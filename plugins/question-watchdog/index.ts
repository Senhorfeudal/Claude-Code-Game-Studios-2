// question-watchdog — OpenCode server plugin.
// Keeps a runtime question deliverable when the mobile question widget fails.
// The question itself is created by OpenCode's built-in `question` tool; this
// plugin only guarantees that a failed delivery becomes visible text.

type Pending = {
  sessionID: string
  text: string
  timer: ReturnType<typeof setTimeout>
}

export default {
  id: 'question-watchdog',

  async setup(ctx: any) {
    const waitMs = Number(ctx.options?.waitMs ?? 4000)
    const prefix = String(ctx.options?.prefix ?? 'Pergunta (widget não exibido)')
    const pending = new Map<string, Pending>()
    const lastPublished = new Map<string, { text: string; at: number }>()
    const seenErrors = new Set<string>()

    const clear = (key: string) => {
      const entry = pending.get(key)
      if (entry) clearTimeout(entry.timer)
      pending.delete(key)
    }

    const clearSession = (sessionID: string) => {
      for (const [key, entry] of pending) {
        if (entry.sessionID === sessionID) clear(key)
      }
    }

    const publish = async (key: string) => {
      const entry = pending.get(key)
      if (!entry) return
      clear(key)
      const previous = lastPublished.get(entry.sessionID)
      if (previous && previous.text === entry.text && Date.now() - previous.at < 60_000) return
      lastPublished.set(entry.sessionID, { text: entry.text, at: Date.now() })
      try {
        await ctx.session.synthetic({ sessionID: entry.sessionID, text: entry.text })
      } catch (error) {
        console.warn('[question-watchdog] could not publish fallback', error)
      }
    }

    const format = (input: any): string => {
      const questions = Array.isArray(input?.questions) ? input.questions : []
      const blocks = questions.map((question: any, index: number) => {
        const lines = [`${index + 1}. ${question.question ?? question.header ?? 'Pergunta'}`]
        const options = Array.isArray(question.options) ? question.options : []
        options.forEach((option: any, optionIndex: number) => {
          const label = String(option.label ?? '').trim()
          const description = String(option.description ?? '').trim()
          lines.push(`   ${optionIndex + 1}) ${label}${description ? ` — ${description}` : ''}`)
        })
        lines.push('   Responda com o número da opção ou escreva sua resposta.')
        return lines.join('\n')
      })
      return [prefix, '', ...blocks].join('\n').trim()
    }

    // A question aborted before execution never reaches execute.before/after,
    // so also recover it from the persisted transcript at a step boundary.
    const scanSession = async (sessionID: string) => {
      try {
        const messages = await ctx.session.context({ sessionID })
        const list = Array.isArray(messages) ? messages : []
        for (const message of list.slice(-3)) {
          const parts = (message as any)?.content ?? (message as any)?.parts ?? []
          for (const part of parts) {
            if (part?.type !== 'tool' || part?.name !== 'question') continue
            const state = part.state ?? {}
            if (state.status !== 'error') continue
            const error = state.error ?? {}
            const aborted = error.type === 'aborted' || /interrupt/i.test(String(error.message ?? ''))
            if (!aborted) continue
            const callID = part.id ?? part.callID ?? state.callID ?? 'question'
            const key = `${sessionID}:${callID}`
            if (seenErrors.has(key)) continue
            seenErrors.add(key)
            pending.set(key, {
              sessionID,
              text: format(state.input),
              timer: setTimeout(() => void publish(key), 0),
            })
            void publish(key)
          }
        }
      } catch (error) {
        console.warn('[question-watchdog] could not scan session transcript', error)
      }
    }

    const sessionIDOf = (event: any): string | undefined =>
      event?.sessionID ?? event?.context?.sessionID ?? event?.metadata?.sessionID ??
      event?.properties?.sessionID

    // A form created by the built-in question tool means the widget was delivered.
    const controller = new AbortController()
    void (async () => {
      try {
        for await (const event of ctx.event.subscribe({
          types: ['form.created', 'session.idle'],
          signal: controller.signal,
        })) {
          const typed = event as any
          if (typed.type === 'form.created') {
            const sessionID = typed?.data?.form?.sessionID
            if (sessionID) clearSession(sessionID)
            continue
          }
          const sessionID = sessionIDOf(typed)
          if (sessionID) void scanSession(sessionID)
        }
      } catch (error) {
        if (!controller.signal.aborted) console.warn('[question-watchdog] event stream ended', error)
      }
    })()

    // Enforce the protocol in every model call, independent of loaded docs.
    await ctx.session.hook('context', (event: any) => {
      event.system.push({
        type: 'text',
        text: 'Question delivery: call the question tool directly, with no reasoning before the call. If that call errors, is interrupted, or no widget is visible to the user, immediately restate the same question as short numbered text in your visible reply, keep a free-text answer option, and wait for the answer before writing or committing anything. Never leave the question only in reasoning.',
      })
    })

    await ctx.tool.hook('execute.before', (event: any) => {
      if (event?.tool !== 'question') return
      const sessionID = sessionIDOf(event)
      if (!sessionID) {
        console.warn('[question-watchdog] question call without a sessionID; no fallback armed')
        return
      }
      const callID = event.id ?? event.messageID ?? Date.now()
      const key = `${sessionID}:${callID}`
      const text = format(event.input)
      clear(key)
      pending.set(key, {
        sessionID,
        text,
        timer: setTimeout(() => void publish(key), waitMs),
      })
    })

    await ctx.tool.hook('execute.after', (event: any) => {
      const sessionID = sessionIDOf(event)
      if (!sessionID) return
      if (event.status === 'completed') clearSession(sessionID)
      if (event.status === 'error') {
        for (const [key, entry] of pending) {
          if (entry.sessionID === sessionID) void publish(key)
        }
      }
    })

    // Agent rules are appended after global rules, so the last matching rule
    // wins. Add the deny at runtime: the generated opencode.jsonc is rebuilt
    // from the repo agents and drops frontmatter it does not map.
    const agentRegistration = await ctx.agent.transform((editor: any) => {
      for (const agent of editor.list()) {
        const info = agent as any
        const systemValue = info.system
        const system = Array.isArray(systemValue)
          ? systemValue.map((part: any) => (typeof part === 'string' ? part : part?.text ?? '')).join('\n')
          : String(systemValue ?? '')
        if (!system.includes('### Question Delivery (all runtimes)')) continue
        const rules = Array.isArray(info.permissions) ? [...info.permissions] : []
        if (rules.some((rule: any) => rule?.action === 'question' && rule?.effect === 'deny')) continue
        editor.update(String(info.id), (target: any) => {
          target.permissions = [
            ...(Array.isArray(target.permissions) ? target.permissions : []),
            { action: 'question', resource: '*', effect: 'deny' },
          ]
        })
      }
    })

    return () => {
      controller.abort()
      void agentRegistration.dispose()
      for (const key of [...pending.keys()]) clear(key)
    }
  },
}
