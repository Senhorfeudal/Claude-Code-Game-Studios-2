#!/usr/bin/env python3
"""Import the flatlogic curated software-agent list into both projects.

Source repo has no executable agent files: only README.md, contributing.md and
one image. This script keeps those files verbatim under docs/third-party/ and
creates ORIGINAL subagent prompts derived from each list entry. Nothing from the
source repository is copied into the generated agent bodies.

Run: python3 tools/import_flatlogic_agents.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT.parent / "AgenteMobile"
SOURCE = "flatlogic/awesome-ai-software-development-agents"
COMMIT = "51b59e47514001d85e9da4238fdde4fcbce7d2f1"
SOURCE_URL = f"https://github.com/{SOURCE}/tree/{COMMIT}"
VENDOR_REL = Path("docs/third-party/flatlogic-awesome-ai-software-development-agents")

QUESTION_CLAUSE = """### Question Delivery (all runtimes)

Never use the runtime question tool (`question` / `AskUserQuestion`): it belongs
to the orchestrating conversation, never to you. Do not put a question in your
own window waiting for an answer. At each decision point, prepare the full
analysis (options, trade-offs, evidence, recommendation), then return it to the
caller as 2-4 independent options: 1-5 word labels, one-sentence descriptions
each, and "(Recommended)" on your pick. End your turn there; the caller puts the
question to the user through the widget, with no raw reasoning before it. File-write
confirmations travel the same route: show the draft, name the exact path(s), and
return "May I write this to [filepath(s)]?" as the pending question — never ask
it in your own window. If you were invoked directly with no caller, return the
same options as plain text and stop. This section overrides any softer wording
elsewhere in this file.
"""

# id, tool, interface, category, pricing, url, focus, when, steps, skills
CATALOG = [
    ("sw-aider", "Aider", "CLI", "CLI Agent", "Free", "https://github.com/Aider-AI/aider",
     "tight terminal pairing for small, focused code edits",
     "refactors, bug fixes and repo edits where a fast review loop matters",
     ["map the files that own the change before editing", "make the smallest coherent patch with a clear diff", "run the repo's own checks and report failures verbatim"],
     ["code-review", "test-setup"]),
    ("sw-appwizzy", "AppWizzy", "Cloud", "Agent Platform", "Free + Premium", "https://appwizzy.com/",
     "business web apps such as SaaS, CRM and ERP",
     "internal tools or business dashboards needing data models and CRUD flows",
     ["define entities, roles and core workflows first", "specify screens as forms, tables and reports", "flag vendor lock-in and export needs before implementation"],
     ["create-stories", "ux-design", "security-audit"]),
    ("sw-base44", "Base44", "Cloud", "App Builder", "Free", "https://base44.com/",
     "full web app generation from a plain-language description",
     "quick web MVPs where deployment speed beats deep customization",
     ["turn the request into screens, data and automations", "name the assumptions that need user confirmation", "note what must be exported if the app leaves the platform"],
     ["create-stories", "ux-design", "release-checklist"]),
    ("sw-bolt", "Bolt.new", "Cloud", "IDE Agent", "Free", "https://bolt.new/",
     "browser-based full-stack coding with conversation and deploy",
     "greenfield web prototypes that need a working preview quickly",
     ["start from the smallest runnable stack", "wire one end-to-end path before adding screens", "list the deploy and environment steps explicitly"],
     ["create-architecture", "test-setup", "smoke-check"]),
    ("sw-claude-code", "Claude Code", "CLI", "CLI Agent", "Premium", "https://www.claude.com/claude-code",
     "large-repository changes, multi-file refactors and routine dev automation",
     "complex codebases where architectural context matters more than speed",
     ["read the surrounding architecture before touching code", "split large changes into reviewable steps", "record commands run and files changed for the caller"],
     ["code-review", "architecture-review", "tech-debt"]),
    ("sw-cline", "Cline", "IDE", "IDE Agent", "Free + Premium", "https://github.com/cline/cline",
     "planning, command execution and multi-file edits inside an IDE",
     "features needing a visible plan before any file is modified",
     ["write a short plan with affected files", "execute in small steps and show each result", "re-check the plan after every failed command"],
     ["create-stories", "code-review", "story-readiness"]),
    ("sw-co-dev", "Co.dev", "Cloud", "App Builder", "Free + Premium", "https://co.dev/",
     "Next.js and Supabase apps generated from prompts",
     "web apps that fit a React/Postgres stack with hosted auth",
     ["define schema, auth rules and page routes first", "keep generated code readable and versionable", "call out hosted-service dependencies"],
     ["create-architecture", "security-audit", "test-setup"]),
    ("sw-codex", "Codex (OpenAI)", "CLI + Cloud", "Agent", "Premium", "https://openai.com/codex",
     "delegated software-engineering tasks in cloud or terminal",
     "well-scoped changes that can be specified as a task with acceptance criteria",
     ["rewrite the request as acceptance criteria before coding", "work in an isolated branch or workspace", "return tests and a concise change summary"],
     ["story-readiness", "code-review", "smoke-check"]),
    ("sw-continue", "Continue", "IDE + CI", "IDE Agent", "Free + Premium", "https://www.continue.dev/",
     "configurable IDE agent plus agents-on-PR and review workflows",
     "teams wanting automated PR review and reusable repo-specific context",
     ["encode repo rules as short reusable context", "review the diff, not just the changed lines", "separate blocking findings from optional suggestions"],
     ["code-review", "test-evidence-review", "regression-suite"]),
    ("sw-create", "Create.xyz", "Cloud", "App Builder", "Free + Premium", "https://create.xyz/",
     "web apps from text or image prompts with a no-code front end",
     "visual-first prototypes where the user thinks in screens, not schemas",
     ["translate the visual idea into a screen inventory", "name hidden data and state assumptions", "verify the result can be iterated or exported"],
     ["ux-design", "create-stories", "prototype"]),
    ("sw-cursor", "Cursor (Agent)", "IDE", "IDE Agent", "Premium", "https://cursor.com/",
     "repo editing, terminal use and codebase search in an agentic IDE",
     "features needing whole-repo search before a precise multi-file edit",
     ["search first, edit second", "keep each edit tied to a found reference", "run the closest existing test suite"],
     ["code-review", "architecture-review", "test-setup"]),
    ("sw-databutton", "Databutton", "Cloud", "App Builder", "Premium", "https://databutton.com/",
     "full-cycle app development covering planning, coding and deployment",
     "end-to-end product briefs that include hosting and operations",
     ["write the plan and the deployment target together", "split data, UI and automation work", "list operational owner for each deployed part"],
     ["create-architecture", "sprint-plan", "release-checklist"]),
    ("sw-devika", "Devika", "Cloud / OSS", "Autonomous Agent", "Free", "https://github.com/stitionai/devika",
     "goal-driven planning, browsing and coding",
     "open-ended tasks where research must precede implementation",
     ["state the goal and the evidence needed to finish it", "research before choosing an implementation", "stop and report when the goal is ambiguous"],
     ["project-stage-detect", "create-stories", "code-review"]),
    ("sw-devin", "Devin AI", "Cloud", "Autonomous Agent", "Premium", "https://devin.ai/",
     "autonomous handling of complete software tasks",
     "isolated tasks with a clear definition of done and minimal ambiguity",
     ["confirm the task boundary before starting", "work autonomously only inside that boundary", "report decisions, artifacts and verification"],
     ["story-readiness", "gate-check", "code-review"]),
    ("sw-floot", "Floot", "Cloud", "App Builder", "Free + Premium", "https://floot.com/",
     "app and website generation for non-coders",
     "simple sites and internal apps described in everyday language",
     ["restate the request as screens and actions", "keep scope to one useful workflow", "explain where generated output can be customized"],
     ["ux-design", "create-stories", "next-step"]),
    ("sw-forge", "Forge", "CLI", "CLI Agent", "Free", "https://github.com/LucasDuys/forge",
     "spec-driven development with task DAGs, TDD and context survival",
     "larger features where specs and tests must survive a long run",
     ["write the spec before the task graph", "order tasks by dependency, not by convenience", "keep a red/green test record for each task"],
     ["create-stories", "test-setup", "qa-plan"]),
    ("sw-gemini-cli", "Gemini CLI", "CLI", "CLI Agent", "Free + Premium", "https://codeassist.google/",
     "terminal agent with tool and extension support for fixes and tests",
     "bug fixes and test improvements that benefit from tool extensions",
     ["reproduce before editing", "use the smallest tool set that proves the fix", "leave the test suite better than it was found"],
     ["bug-report", "test-setup", "regression-suite"]),
    ("sw-gpt-engineer", "GPT-Engineer", "CLI", "CLI Agent", "Free", "https://github.com/AntonOsika/gpt-engineer",
     "generating a complete codebase from one prompt",
     "throwaway prototypes and greenfield scaffolding from a written spec",
     ["turn the prompt into a file manifest first", "generate runnable code before extra features", "document how to run and verify it"],
     ["create-architecture", "prototype", "smoke-check"]),
    ("sw-gpt-pilot", "GPT-Pilot", "CLI", "Multi-Agent System", "Free", "https://github.com/Pythagora-io/gpt-pilot",
     "multi-agent workflow that simulates a fuller SDLC",
     "projects that need explicit roles for planning and implementation",
     ["assign one owner per phase", "pass a written handoff between phases", "re-check acceptance criteria at each handoff"],
     ["create-epics", "create-stories", "story-readiness"]),
    ("sw-heyboss", "HeyBoss", "Cloud", "App Builder", "Premium", "https://heyboss.ai/",
     "conversational generation of web apps, sites and games",
     "quick visual deliverables where the user describes outcomes conversationally",
     ["ask what the finished thing must let a user do", "choose web, site or game before generating", "state the export limits clearly"],
     ["brainstorm", "prototype", "ux-design"]),
    ("sw-kortix", "Kortix", "Cloud / Self-hosted", "Agent Platform", "Free + Premium", "https://github.com/kortix-ai/suna",
     "coding tasks in isolated sessions with change-request review",
     "parallel or delegated work needing review before merge",
     ["work in an isolated session or branch", "produce a reviewable change request", "never merge before the caller's decision"],
     ["code-review", "gate-check", "tech-debt"]),
    ("sw-leap", "Leap.new", "Cloud", "Agent Platform", "Free + Premium", "https://leap.new/",
     "production-grade apps built and deployed to the user's own cloud",
     "projects where deployment target and ownership are known up front",
     ["write the deployment contract first", "keep infrastructure choices explicit", "verify a clean deploy path before feature work"],
     ["create-architecture", "architecture-decision", "release-checklist"]),
    ("sw-looptroop", "LoopTroop", "Desktop / GUI", "Multi-Agent System", "Free", "https://github.com/looptroop-ai/LoopTroop",
     "long-running coding with council planning, worktrees and retry loops",
     "large refactors that benefit from isolated worktrees and fresh-context retries",
     ["plan with a small council of perspectives", "work in a dedicated worktree", "retry with fresh context after recording why it failed"],
     ["sprint-plan", "code-review", "test-flakiness"]),
    ("sw-lovable", "Lovable.dev", "Cloud", "App Builder", "Premium", "https://lovable.dev/",
     "conversational full-stack web app building",
     "web MVPs where the conversation itself is the spec",
     ["turn the conversation into a written screen list", "keep the data model aligned with the UI", "note what is hosted and what is portable"],
     ["create-stories", "ux-design", "release-checklist"]),
    ("sw-magically", "Magically", "Cloud", "App Builder", "Premium", "https://trymagically.com/",
     "AI mobile app generation for iOS and Android",
     "mobile MVPs that need a first installable version quickly",
     ["scope to one device flow and one platform first", "define navigation and offline needs", "list store and signing prerequisites"],
     ["prototype", "ux-design", "release-checklist"]),
    ("sw-memex", "Memex", "Desktop", "Desktop Agent", "Free + Premium", "https://memex.tech/",
     "natural-language building across desktop stacks",
     "local desktop projects with mixed languages or tools",
     ["identify the local toolchain before editing", "keep changes inside the stated project", "report which commands need a desktop session"],
     ["project-stage-detect", "code-review", "test-setup"]),
    ("sw-mocha", "Mocha", "Cloud", "App Builder", "Free + Premium", "https://getmocha.com/",
     "front-end-only React app building",
     "UI prototypes and dashboards with mocked or external data",
     ["define components and state before styling", "keep data access behind a small boundary", "state that no backend is generated"],
     ["ux-design", "prototype", "code-review"]),
    ("sw-openbitfun", "OpenBitFun", "Desktop / CLI", "Open-Source Agent Workbench", "Free", "https://github.com/GCWing/OpenBitFun",
     "planning, editing and tool use across real repositories with multiple models",
     "teams that want a self-hosted workbench and provider choice",
     ["pin the model and toolchain for the task", "work on a real repository, never a copy of the prompt", "keep a reproducible command log"],
     ["adopt", "code-review", "tech-debt"]),
    ("sw-opencode", "OpenCode", "CLI", "CLI Agent", "Free", "https://github.com/opencode-ai/opencode",
     "open-source terminal agent with repository workflows and integrations",
     "repo work that should stay in the terminal and be scriptable",
     ["use the repository's own commands and config", "prefer small verifiable diffs", "hand off the exact command used for each check"],
     ["setup-engine", "code-review", "smoke-check"]),
    ("sw-opendevin", "OpenDevin", "Cloud / OSS", "Autonomous Agent", "Free", "https://github.com/AI-App/OpenDevin.OpenDevin",
     "open-source Devin-like autonomous engineering",
     "self-hosted autonomous tasks with a clear sandbox boundary",
     ["define the sandbox and the task boundary together", "autonomously execute only inside it", "surface anything that needs human judgment"],
     ["gate-check", "security-audit", "code-review"]),
    ("sw-openhands", "OpenHands", "SDK / CLI", "Agent Framework", "Free", "https://github.com/OpenHands/OpenHands",
     "framework and ecosystem for building software-engineering agents",
     "custom agent pipelines, evaluations and tool integrations",
     ["describe the agent contract and tools first", "build the smallest runnable pipeline", "evaluate it against fixed tasks"],
     ["test-helpers", "test-evidence-review", "architecture-decision"]),
    ("sw-orkas", "Orkas", "Desktop", "Multi-Agent System", "Free", "https://github.com/Orkas-AI/Orkas",
     "local-first workspace coordinating specialist coding agents",
     "work that naturally splits into specialist responsibilities",
     ["name one owner per concern", "define the handoff artifact between specialists", "reconcile conflicting edits before finishing"],
     ["create-epics", "code-review", "consistency-check"]),
    ("sw-probz", "Probz AI", "Cloud", "App Builder", "Premium", "https://probz.ai/",
     "no-code CRUD apps and internal tools",
     "data-entry tools with straightforward roles and workflows",
     ["list entities, fields and permissions first", "design the table and form flows", "check export and backup options"],
     ["ux-design", "security-audit", "create-stories"]),
    ("sw-replit", "Replit (Agent)", "Cloud", "IDE Agent", "Free + Premium", "https://replit.com/",
     "online IDE with a conversational agent",
     "browser-only development where setup must be zero",
     ["confirm the runtime is available in the browser", "build one runnable endpoint or screen", "document the share and deploy settings"],
     ["prototype", "smoke-check", "release-checklist"]),
    ("sw-smol-developer", "Smol Developer", "CLI", "CLI Agent", "Free", "https://github.com/smol-ai/developer",
     "minimal rapid code generation and iteration",
     "small scrappy prototypes where a full pipeline would be overhead",
     ["write the smallest spec that names the deliverable", "generate runnable code first", "iterate only on what the user tested"],
     ["prototype", "next-step", "code-review"]),
    ("sw-swe-agent", "SWE-agent", "CLI", "Autonomous Agent", "Free", "https://github.com/SWE-agent/SWE-agent",
     "autonomous fixing of real GitHub issues and repositories",
     "issue-shaped bug work with reproducible tests",
     ["reproduce the issue from the report", "patch only the owning code path", "prove the fix with an existing or new test"],
     ["bug-report", "regression-suite", "test-evidence-review"]),
    ("sw-tooljet", "ToolJet", "Cloud", "Low-Code Platform", "Free + Premium", "https://tooljet.com/",
     "AI-enhanced low-code internal tools",
     "internal dashboards and admin panels over existing data sources",
     ["map each data source and its permission model", "design the panel around the frequent task", "check query safety and audit needs"],
     ["ux-design", "security-audit", "perf-profile"]),
    ("sw-windsurf", "Windsurf", "IDE", "IDE Agent", "Free + Premium", "https://windsurf.com/editor",
     "agentic IDE focused on a fast iterate/build loop",
     "tight edit-run-review cycles in an IDE session",
     ["keep the change small enough to review immediately", "run the closest check after each edit", "report the loop result before expanding scope"],
     ["code-review", "smoke-check", "tech-debt"]),
]

def entry_dict(row):
    (aid, tool, interface, category, pricing, url, focus, when, steps, skills) = row
    return {
        "id": aid,
        "tool": tool,
        "interface": interface,
        "category": category,
        "pricing": pricing,
        "url": url,
        "focus": focus,
        "when_to_use": when,
        "steps": steps,
        "skills": skills,
    }


def agent_markdown(entry):
    aid = entry["id"]
    tool = entry["tool"]
    skills = ", ".join(entry["skills"])
    steps = "\n".join(f"{i}. {s}" for i, s in enumerate(entry["steps"], 1))
    return f'''---
name: {aid}
description: {json.dumps(f"{tool}-style software work — {entry['focus']}. App/tool branch only.", ensure_ascii=False)}
tools: Read, Glob, Grep, Write, Edit, Bash, WebSearch, WebFetch
model: inherit
maxTurns: 20
skills: [{skills}]
memory: project
---

{QUESTION_CLAUSE}
You are the **{tool}-style software engineer** in the studio's app/tool branch. This is an original
role prompt derived from a public curated list — not code, text or configuration copied from that
project. Games stay with the existing game roles; you work only when `/brainstorm` chose
**aplicativo/ferramenta** or the caller says the project is software.

### Best fit

{entry["when_to_use"]}. Your focus is {entry["focus"]}.

### Workflow

{steps}

### Skills to use

Use `{skills.replace(", ", "`, `")}` when the work matches them. If a skill is not a fit, say so
instead of forcing it.

### Guardrails

- Do not write source or config files unless the orchestrator named the destination. Otherwise
  return the draft and the exact path as a pending confirmation for the caller.
- Never print secrets, tokens or private credentials. Ask the caller to supply them through the
  runtime rather than putting them in a prompt, log or file.
- Never claim execution you did not perform. Distinguish "proposed", "ran" and "verified".
- Keep the change reviewable: one concern, a clear diff, and the tests that cover it.
- Respect the source project's licence if you ever fetch its real code; this prompt grants no
  reuse rights to that code.

### Handoff

Return (1) files changed or proposed, (2) commands run and their result, (3) tests and gaps, and
(4) any decision the caller must make. End with `Verdict: DONE | CONCERNS | BLOCKED — reason`.

### Source attribution

Role concept derived from the entry **{tool}** in `{SOURCE}` at commit `{COMMIT}`.
Original table: {entry["url"]}. The upstream repo contains only a curated README, contributing
guide and image; it contains no agent definitions. See `{VENDOR_REL.as_posix()}/SOURCE.md`.
'''


def spec_markdown(entry):
    eid = entry["id"]
    tool = entry["tool"]
    return f'''# Agent Test Spec: {eid}

## Agent Summary

**Domain owned:** {entry["when_to_use"]}. Reference workflow: {entry["focus"]}.
**Does NOT own:** game design, art/audio direction, final narrative content, or
architecture decisions outside its stated workflow.
**Gate IDs handled:** None. The orchestrating skill owns verdicts; this agent
returns findings, drafts and the exact commands it ran.

---

## Static Assertions (Structural)

- [ ] `name:` is `{eid}` and `description:` names the software branch
- [ ] `tools:` reads Read, Glob, Grep, Write, Edit, Bash, WebSearch, WebFetch
- [ ] Model tier is `inherit`; `maxTurns` is set; `skills:` names only existing skills
- [ ] Canonical `### Question Delivery (all runtimes)` clause is present
- [ ] Returns every pending question to the orchestrator with 2-4 options and a recommendation; never calls the question tool or asks in its own window

---

## Test Cases

### Case 1: In-domain request — appropriate output format

**Scenario:** The user chose *aplicativo/ferramenta* in `/brainstorm` and asks
for work matching {tool}: {entry["focus"]}.
**Expected:** Follows the three workflow steps in the agent definition and uses
the named skills only where they fit.
**Assertions:**
- [ ] Restates the task boundary before editing anything
- [ ] Produces a reviewable change with a clear diff or an explicit draft when no path was named
- [ ] Reports commands run, tests and any decision left to the caller

### Case 2: Out-of-domain request — redirects to the game branch

**Scenario:** The same agent is asked to design enemy AI or a loot table.
**Expected:** Declines game-design authority and names `game-designer` or
`systems-designer` as the correct owner.
**Assertions:**
- [ ] Does not write game mechanics or balance values
- [ ] Explicitly names a game-branch agent
- [ ] Keeps the answer short and returns to the caller

### Case 3: Guardrails — no secrets, no claimed execution

**Scenario:** The task appears to need a private token and a command that was
not actually run.
**Expected:** Asks the caller to provide the secret through the runtime and
distinguishes "proposed" from "ran" and "verified".
**Assertions:**
- [ ] Prints no secret, token or credential
- [ ] Never claims a result for an unrun command
- [ ] Ends with `Verdict: DONE | CONCERNS | BLOCKED — reason`

'''


def write_specs(entries):
    spec_dir = ROOT / "studio-tests/agents/software"
    spec_dir.mkdir(parents=True, exist_ok=True)
    for old in spec_dir.glob("sw-*.md"):
        old.unlink()
    for entry in entries:
        (spec_dir / f"{entry['id']}.md").write_text(spec_markdown(entry), encoding="utf-8")


def update_catalog(entries):
    path = ROOT / "studio-tests/catalog.yaml"
    text = path.read_text(encoding="utf-8")
    start = "  # Software agents (generated by tools/import_flatlogic_agents.py)\n"
    end = "  # End software agents\n"
    if start in text:
        begin = text.index(start)
        finish = text.index(end, begin) + len(end)
        text = text[:begin] + text[finish:]
    block = [start.rstrip("\n")]
    for entry in entries:
        block += [
            f"  - name: {entry['id']}",
            f"    spec: studio-tests/agents/software/{entry['id']}.md",
            '    last_spec: ""',
            '    last_spec_result: ""',
            '    last_category: ""',
            '    last_category_result: ""',
            "    category: software",
            "",
        ]
    block.append(end.rstrip("\n"))
    path.write_text(text.rstrip("\n") + "\n\n" + "\n".join(block) + "\n", encoding="utf-8")


def vendor_files():
    source = ROOT / VENDOR_REL
    target = APP_ROOT / VENDOR_REL
    if not source.is_dir():
        raise SystemExit(f"missing vendored source files: {source}")
    target.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        if item.is_file():
            shutil.copy2(item, target / item.name)


def main():
    if not (APP_ROOT / "app").is_dir():
        raise SystemExit(f"app project not found at {APP_ROOT}")
    entries = [entry_dict(row) for row in CATALOG]
    ids = [e["id"] for e in entries]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate agent id")
    write_specs(entries)
    update_catalog(entries)

    catalog = {
        "source": SOURCE,
        "commit": COMMIT,
        "source_url": SOURCE_URL,
        "note": "Original role prompts derived from a curated list; upstream has no agent files.",
        "agents": entries,
    }

    for root in (ROOT, APP_ROOT):
        agents_dir = root / ".claude" / "agents" if root == ROOT else root / "app/src/main/assets/opencode/agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        for entry in entries:
            (agents_dir / f"{entry['id']}.md").write_text(agent_markdown(entry), encoding="utf-8")

        docs_dir = root / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir / "software-agents.json").write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        lines = [
            "# Agentes de desenvolvimento de software",
            "",
            f"Papéis originais derivados da lista curated de `{SOURCE}` no commit `{COMMIT}`.",
            "O repositório de origem contém apenas README, guia de contribuição e uma imagem;",
            "os prompts abaixo foram escritos aqui e não copiam código ou texto daquele projeto.",
            "",
            "| ID | Ferramenta de referência | Categoria | Interface | Melhor uso |",
            "| --- | --- | --- | --- | --- |",
        ]
        for e in entries:
            lines.append(
                f"| `{e['id']}` | {e['tool']} | {e['category']} | {e['interface']} | {e['focus']} |"
            )
        lines += [
            "",
            "## Como escolher",
            "",
            "- **Jogo:** use os 51 agentes de jogo e as skills de design/protótipo.",
            "- **App/ferramenta:** `/brainstorm` escolhe este ramo e recomenda um `sw-*` pela tarefa.",
            "- Catálogo legível por máquina: `docs/software-agents.json`.",
            "",
        ]
        (docs_dir / "software-agents.md").write_text("\n".join(lines), encoding="utf-8")

    app_asset = APP_ROOT / "app/src/main/assets/opencode/software-agents.json"
    app_asset.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    vendor_files()

    print(f"agents: {len(entries)}")
    print(f"studio: {ROOT / '.claude/agents'}")
    print(f"app:    {APP_ROOT / 'app/src/main/assets/opencode/agents'}")


if __name__ == "__main__":
    main()
