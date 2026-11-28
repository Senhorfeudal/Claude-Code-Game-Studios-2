# Senhorfeudal Game Studios — OpenCode edition

Indie game and software development managed through 90 specialist subagents (52 game + 38 software) and 80 skills.
Each agent owns a domain, enforcing separation of concerns and quality. This
folder is the OpenCode port of the Claude Code template; `CLAUDE.md` is kept as
the upstream source for Claude Code sessions.

## Technology stack

- **Engine**: [CHOOSE: Web / Godot 4 / Unity / Unreal Engine 5]
- **Language**: [CHOOSE: TypeScript / GDScript / C# / C++ / Blueprint]
- **Version control**: Git with trunk-based development
- **Build system / asset pipeline**: [SPECIFY after choosing engine]

Engine-specialist agents exist for Godot, Unity, Unreal and `web-android-specialist`
for browser/Android runtimes; use the matching set
or the general programmers for a Web project.

## OpenCode runtime mapping

- **Skills** live in `.claude/skills/<id>/SKILL.md`. OpenCode-native wrappers in
  `.opencode/skills/<id>/SKILL.md` take precedence and tell the model to read the
  upstream file and its `references/`. Load one with the `skill` tool (exact ID,
  e.g. `skill-test`), or mention `@skill-id` in a prompt.
- **Slash commands** are mirrored in `.opencode/commands/<id>.md`, so `/prototype`,
  `/start`, `/skill-test` etc. work. A command loads the corresponding skill.
- **Agents** are in `.opencode/agents/<id>.md` as OpenCode subagents (same names
  as the original Claude Code agents). Delegate with the `subagent` tool.
- **Question tool**: use `question` for every user decision — no reasoning before
  the call, context and options in the tool input. If the widget fails or is not
  visible, immediately restate the question as numbered text and wait.
- **Inline `!`shell`` blocks** in upstream skills are Claude Code prompt
  expansions. OpenCode does not run them: execute the enclosed command with the
  `shell` tool. `${CLAUDE_SKILL_DIR}` means `.claude/skills/<id>` and
  `${CLAUDE_PROJECT_DIR}` means this workspace root.
- **`@path` imports** in upstream docs are Claude Code syntax. In OpenCode, read
  the named file with the `read` tool when a skill asks for it.
- `allowed-tools`, `user-invocable`, `argument-hint`, `model: opus|sonnet|haiku`
  and `maxTurns` in upstream frontmatter are Claude Code metadata. OpenCode uses
  `permissions`, skill `metadata.opencode/autoinvoke`, and `steps` instead.
- Hooks are not native to OpenCode. `.opencode/plugins/ccgs-bridge/index.js`
  forwards commit/push and asset/write validation to the existing bash hooks;
  `plugins/question-watchdog` keeps questions deliverable on mobile.

See `.opencode/OPENCODE-PORT.md` for the full mapping, verification commands and
known gaps.

## Project structure

Read `.claude/docs/directory-structure.md` on demand for the full tree.
`project.yaml` at the root is the single source of truth for engine, modes and
naming; skills resolve it through `.claude/hooks/yaml-helper.sh resolve_config`.
`.claude/docs/technical-preferences.md` is a legacy fallback.

## Configuration

`project.yaml` holds engine, specialists, naming, platform, performance and
`modes.rigor` (`minimal` by default). Skills resolve it with `resolve_config`
(see `.claude/docs/config-resolution.md`). OpenCode runtime settings live in
`.opencode/opencode.jsonc`; the two files serve different purposes.

## Collaboration protocol

**User-driven, not autonomous.** Every task follows:
**Question → Options → Decision → Draft → Approval**.

- Ask “May I write this to [path]?” before using `write`/`edit`. Exempt:
  `active.md` appends, agent memory, and a subagent's new file at the path its
  orchestrating skill named (see `.claude/rules/agent-memory.md`).
- Show drafts or summaries before requesting approval; require explicit approval
  for multi-file changes.
- No commits without user instruction.
- A skipped or dismissed question is not an answer: re-ask through the widget
  and wait. Plain text is a fallback only when no widget exists or the call
  fails, is interrupted, or never renders.
- If started outside this folder, warn first: the local config, rules and hooks
  only load from this project root.

Full protocol: `docs/COLLABORATIVE-DESIGN-PRINCIPLE.md`,
`.claude/docs/automation-modes.md` § Question delivery.

First session? Say “make me a game” (`/prototype`), or run `/start`.

## Coding standards

Read `.claude/rules/` and `.claude/docs/coding-standards.md` on demand. Values
are data-driven; tests come before implementation; anything the player sees must
be observed in a running game before it is called done.

## Context management

- `production/session-state/active.md` is the session checkpoint. Read it first
  after compaction, a crash or `/clear`.
- Helpers in `.claude/scripts/` emit observations, never verdicts.
- `.claude/docs/context-management.md` is a reference, read on demand.
