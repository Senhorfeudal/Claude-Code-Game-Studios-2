---
name: "team-release"
description: "Orchestrate the release team — release-manager, qa-lead, devops-engineer, producer — to execute a release from candidate to deployment."
metadata:
  opencode/autoinvoke: true
---

# OpenCode port — `team-release`

Load the complete upstream skill at `.claude/skills/team-release/SKILL.md` with the `read` tool and follow it in full. Read any `references/` or scripts it names from that same directory, not from this wrapper.

Expected arguments: [version number or 'next'] [--review full|lean|solo]

## Tool-name mapping (Claude Code → OpenCode)

- `AskUserQuestion` → OpenCode `question` tool. Call it **before** explaining or
  drafting; a failed or invisible widget must immediately become numbered text.
- `Agent` / `Task` → OpenCode `subagent` tool. Agent IDs are the file names in
  `.opencode/agents/` (same names as the original studio agents). Team skills
  are the exception: they stay in this chat and never use it.
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

## In-chat orchestration (mandatory for teams)

This is an in-chat orchestrator: perform every phase inline in the conversation the user opened and never use the `subagent` tool for the team or for any specialist role. Read the role's rules from `.claude/agents/<id>.md` instead. Ask every decision and write approval with the `question` tool in this chat; if the widget is invisible, immediately use numbered text and wait. See `.claude/docs/in-chat-teams.md`.
