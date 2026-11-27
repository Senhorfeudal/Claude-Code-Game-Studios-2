#!/usr/bin/env python3
"""Generate the OpenCode V2 layer from the Claude Code studio template.

Run from anywhere: python3 .opencode/scripts/generate-opencode-layer.py
Source of truth stays in .claude/skills and .claude/agents. Generated files are
plain Markdown under .opencode/ and can be edited, but a rerun overwrites them.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".claude" / "skills"
AGENTS = ROOT / ".claude" / "agents"
OUT_SKILLS = ROOT / ".opencode" / "skills"
OUT_COMMANDS = ROOT / ".opencode" / "commands"
OUT_AGENTS = ROOT / ".opencode" / "agents"


def frontmatter(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"missing frontmatter: {path}")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"unterminated frontmatter: {path}")
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, object] = {}
    current = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            current = match.group(1)
            value = match.group(2).strip()
            if value.startswith('"') and value.endswith('"'):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            elif value.startswith("[") and value.endswith("]"):
                value = [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
            data[current] = value
        elif current and line.startswith((" ", "\t")) and isinstance(data.get(current), list):
            data[current].append(line.strip().strip("'\""))
    return data, body


def scalar(value: object) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


TOOL_MAPPING = """## Tool-name mapping (Claude Code → OpenCode)

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
"""


def generate_skills() -> list[str]:
    OUT_COMMANDS.mkdir(parents=True, exist_ok=True)
    ids: list[str] = []
    for source in sorted(SKILLS.glob("*/SKILL.md")):
        skill_id = source.parent.name
        meta, _ = frontmatter(source)
        description = str(meta.get("description", f"Studio skill: {skill_id}"))
        autoinvoke = "false" if str(meta.get("disable-model-invocation", "")).lower() == "true" else "true"
        hint = meta.get("argument-hint")
        lines = [
            "---",
            f"name: {scalar(skill_id)}",
            f"description: {scalar(description)}",
            "metadata:",
            f"  opencode/autoinvoke: {autoinvoke}",
            "---",
            "",
            f"# OpenCode port — `{skill_id}`",
            "",
            f"Load the complete upstream skill at `.claude/skills/{skill_id}/SKILL.md` "
            "with the `read` tool and follow it in full. Read any `references/` or "
            "scripts it names from that same directory, not from this wrapper.",
            "",
        ]
        if hint:
            lines += [f"Expected arguments: {hint}", ""]
        lines += [TOOL_MAPPING]
        lines += [
            "## Rules that stay in force",
            "",
            "- Keep the ask-first protocol: show options, get a decision, draft, then ask "
            '“May I write this to [path]?” before writing.',
            "- The framework never runs a skill for you: after loading it, carry out its "
            "phases in this session and report the verdicts it specifies.",
            "",
        ]
        if skill_id.startswith("team-"):
            lines += [
                "## In-chat orchestration (mandatory for teams)",
                "",
                f"This is an in-chat orchestrator: perform every phase inline in the "
                "conversation the user opened and never use the `subagent` tool for the "
                "team or for any specialist role. Read the role's rules from "
                "`.claude/agents/<id>.md` instead. Ask every decision and write approval "
                "with the `question` tool in this chat; if the widget is invisible, "
                "immediately use numbered text and wait. See "
                "`.claude/docs/in-chat-teams.md`.",
                "",
            ]
        target = OUT_SKILLS / skill_id / "SKILL.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(lines), encoding="utf-8")

        cmd = [
            "---",
            f"description: {scalar(description)}",
            "---",
            "",
            f"Load the `{skill_id}` skill with the `skill` tool, read "
            f"`.claude/skills/{skill_id}/SKILL.md` in full, and execute it to completion.",
            "",
            "User request / arguments: $ARGUMENTS",
            "",
        ]
        (OUT_COMMANDS / f"{skill_id}.md").write_text("\n".join(cmd), encoding="utf-8")
        ids.append(skill_id)
    return ids


def generate_agents() -> list[str]:
    OUT_AGENTS.mkdir(parents=True, exist_ok=True)
    ids: list[str] = []
    for source in sorted(AGENTS.glob("*.md")):
        agent_id = source.stem
        meta, body = frontmatter(source)
        description = str(meta.get("description", f"Studio agent: {agent_id}"))
        tools = meta.get("tools", "")
        tool_names = {part.strip() for part in str(tools).split(",") if part.strip()}
        disallowed = {part.strip() for part in str(meta.get("disallowedTools", "")).split(",") if part.strip()}

        rules: list[dict[str, str]] = []
        if "Bash" in disallowed or "Bash" not in tool_names:
            rules.append({"action": "shell", "resource": "*", "effect": "deny"})
        if "Write" not in tool_names and "Edit" not in tool_names:
            rules.append({"action": "edit", "resource": "*", "effect": "deny"})
        if "Agent" not in tool_names:
            rules.append({"action": "subagent", "resource": "*", "effect": "deny"})
        if "### Question Delivery (all runtimes)" in body:
            rules.append({"action": "question", "resource": "*", "effect": "deny"})

        header = [
            "---",
            f"description: {scalar(description)}",
            "mode: subagent",
        ]
        try:
            steps = int(str(meta.get("maxTurns", "20")).strip())
            if steps > 0:
                header.append(f"steps: {steps}")
        except ValueError:
            pass
        if rules:
            header.append("permissions:")
            for rule in rules:
                header += [
                    f"  - action: {rule['action']}",
                    f"    resource: {scalar(rule['resource'])}",
                    f"    effect: {rule['effect']}",
                ]
        header.append("---")

        notes = ["", "## OpenCode port notes", ""]
        original_model = str(meta.get("model", "inherit"))
        notes.append(
            f"- Original tier/model: `{original_model}`. OpenCode subagents inherit "
            "the session model; treat this as seniority, not a billing tier."
        )
        if meta.get("skills"):
            preloaded = ", ".join(str(meta["skills"])) if not isinstance(meta["skills"], list) else ", ".join(meta["skills"])
            notes.append(
                f"- Preloaded skills: {preloaded}. Load each with the `skill` tool when needed."
            )
        if meta.get("memory") == "project":
            notes.append(
                "- Original `memory: project` has no direct V2 equivalent; keep durable "
                "state in `production/session-state/active.md`."
            )
        if meta.get("isolation") == "worktree":
            notes.append("- Original `isolation: worktree` is not enforced by OpenCode; use a worktree when asked.")
        notes.append(
            "- Delegation uses the `subagent` tool with agent IDs from `.opencode/agents/`."
        )
        notes.append("")

        target = OUT_AGENTS / f"{agent_id}.md"
        target.write_text("\n".join(header) + "\n" + body.rstrip() + "\n" + "\n".join(notes), encoding="utf-8")
        ids.append(agent_id)
    return ids


def main() -> None:
    skill_ids = generate_skills()
    agent_ids = generate_agents()
    print(f"generated {len(skill_ids)} skills, {len(skill_ids)} commands, {len(agent_ids)} agents")


if __name__ == "__main__":
    main()
