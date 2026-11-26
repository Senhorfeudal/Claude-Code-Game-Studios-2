---
name: "prototype"
description: "Asks a few questions, writes a one-page brief, builds a playable browser game as one HTML folder it plays and screenshots; with an engine set, a throwaway engine or paper prototype. Ends on proceed, pivot or kill. Use when the user says make me a game, wants to try a game idea or mechanic, needs a quick spike, asks to change a game it made, or says they love or hate it."
metadata:
  opencode/autoinvoke: true
---

# OpenCode port — `prototype`

Load the complete upstream skill at `.claude/skills/prototype/SKILL.md` with the `read` tool and follow it in full. Read any `references/` or scripts it names from that same directory, not from this wrapper.

Expected arguments: [what to make] [--from <your game>] [--path html|engine|paper] [--review full|lean|solo] [--spike]

## Tool-name mapping (Claude Code → OpenCode)

- `AskUserQuestion` → OpenCode `question` tool. Call it **before** explaining or
  drafting; a failed or invisible widget must immediately become numbered text.
- `Agent` / `Task` → OpenCode `subagent` tool. Agent IDs are the file names in
  `.opencode/agents/` (same names as the original studio agents).
- `Bash` → `shell` tool. `Write` / `Edit` → `write` / `edit`.
- `WebSearch` / `WebFetch` → `websearch` / `webfetch`.
- `TaskCreate` / `TaskUpdate` → `todowrite` when available, otherwise plain text.
- `${CLAUDE_SKILL_DIR}` → `.claude/skills/<id>`; `${CLAUDE_PROJECT_DIR}` → the
  workspace root (the directory holding `project.yaml`).
- Inline `!`…`` preloads in the original skill are Claude Code prompt expansions.
  OpenCode does not execute them: run the enclosed command with `shell` and use
  its output (most are `bash .claude/hooks/yaml-helper.sh resolve_config ...`).
- `$ARGUMENTS` in the original skill means the user's current request.
- `model: opus|sonnet|haiku` frontmatter in the original files is ignored by
  OpenCode; agents inherit the session model unless explicitly configured.

## Rules that stay in force

- Keep the ask-first protocol: show options, get a decision, draft, then ask “May I write this to [path]?” before writing.
- The framework never runs a skill for you: after loading it, carry out its phases in this session and report the verdicts it specifies.
