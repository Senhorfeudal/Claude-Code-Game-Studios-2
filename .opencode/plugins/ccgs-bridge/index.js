// ccgs-bridge — OpenCode V2 hook bridge for the studio's Claude Code validators.
// Fail open: a missing bash, timeout, or script error must never block a tool call.
import { spawnSync } from "node:child_process"
import path from "node:path"
import { fileURLToPath } from "node:url"

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..")
const hooks = path.join(root, ".claude", "hooks")
const shellish = /^(bash|shell)$/
const editorish = /^(write|edit|patch)$/
const dangerous = /\b(git\s+commit|git\s+push|git\s+tag|git\s+merge|gh\s+release|butler\s+push|steamcmd)\b/

function run(script, payload) {
  try {
    const result = spawnSync("bash", [path.join(hooks, script)], {
      cwd: root,
      env: { ...process.env, CLAUDE_PROJECT_DIR: root },
      input: JSON.stringify(payload),
      encoding: "utf8",
      timeout: 1500,
      maxBuffer: 256 * 1024,
    })
    if (result.error) return { status: 0, stderr: String(result.error.message) }
    return {
      status: result.status ?? 0,
      stderr: (result.stderr || "").trim(),
      stdout: (result.stdout || "").trim(),
    }
  } catch (error) {
    return { status: 0, stderr: String(error?.message ?? error) }
  }
}

function warn(script, output) {
  const message = output.stderr || output.stdout
  if (message) console.warn(`[ccgs-bridge] ${script}: ${message}`)
}

function toolName(tool) {
  if (tool === "write") return "Write"
  if (tool === "edit" || tool === "patch") return "Edit"
  return "Bash"
}

export default {
  id: "ccgs-bridge",

  async setup(ctx) {
    await ctx.tool.hook("execute.before", (event) => {
      const tool = String(event?.tool ?? "")
      const input = event?.input ?? {}

      if (shellish.test(tool)) {
        const command = String(input.command ?? input.cmd ?? "")
        if (!dangerous.test(command)) return
        for (const script of ["validate-commit.sh", "validate-push.sh"]) {
          const output = run(script, { tool_name: "Bash", tool_input: { command } })
          warn(script, output)
          if (output.status === 2) {
            throw new Error(`[ccgs-bridge] ${script} blocked the command: ${output.stderr || output.stdout || "validation failed"}`)
          }
        }
        return
      }

      if (editorish.test(tool)) {
        const file_path = String(input.file_path ?? input.path ?? "")
        const payload = { tool_name: toolName(tool), tool_input: { ...input, file_path } }
        for (const script of ["validate-write.sh", "validate-registry.sh"]) {
          const output = run(script, payload)
          warn(script, output)
          if (output.status === 2) {
            throw new Error(`[ccgs-bridge] ${script} blocked the write: ${output.stderr || output.stdout || "validation failed"}`)
          }
        }
      }
    })

    await ctx.tool.hook("execute.after", (event) => {
      const tool = String(event?.tool ?? "")
      if (!editorish.test(tool)) return
      const input = event?.input ?? {}
      const file_path = String(input.file_path ?? input.path ?? "")
      const payload = { tool_name: toolName(tool), tool_input: { ...input, file_path } }
      for (const script of ["validate-assets.sh", "validate-skill-change.sh"]) {
        warn(script, run(script, payload))
      }
    })
  },
}
