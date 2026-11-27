---
name: spy
description: "External sector scout — scans the web, forums, app stores and GitHub for what is new and different in a game or software sector, and returns sourced learnings reapplyable to this project. Use when research outside the repo would change a decision."
argument-hint: "[research brief: engine, platform, feature and decision]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Agent, AskUserQuestion
model: sonnet
---

# Spy — external sector scout

This skill makes the `spy` agent reachable from the skill list. It is
read-only: it writes no files and changes no code. The agent researches what
is different out there in a game or software sector; this skill owns the
question widget and puts the agent's recommendation to the user. The shared
protocol is `.claude/docs/external-scan.md`; the artifact is
`design/external-scan.md`.

## Phase 1 — Build a narrow brief

Read `project.yaml` for project kind, engine, platform and stage. Read the
concept or GDD in scope and `design/external-scan.md` if it exists. If the
invocation already names the sector, feature and decision, use that brief.
Otherwise call the question tool immediately, with no reasoning or draft text
before it:

- Question: "What sector should the external scout research, and what decision must it inform?"
- Options: "Similar games for this mechanic", "Open-source implementations",
  "Software category and competitors", "Decide without external research"
- The runtime's free-text affordance covers a custom brief; say so in the question
- Mark one option as recommended with the trade-off in its description

A skipped or dismissed question is not an answer: re-ask once through the
widget, then use the plain-text fallback in `.claude/docs/automation-modes.md`.
Only a real choice proceeds. **Decide without external research** ends with
`COMPLETE — research declined`.

## Phase 2 — Delegate to the agent

If the runtime has no `Agent` tool, answer
`NOT ASSESSED — NO AGENT TOOL` and name the `spy` agent for direct invocation.
Otherwise spawn **one** `spy` subagent with a brief containing:

- the project kind (game or app/tool), engine, platform and stage from `project.yaml`
- the sector (game genre/theme or software category and shape), the feature or
  mechanic, and the decision the research must inform
- the local files read in Phase 1, with no pasted document contents
- the agent's output contract: research brief table, local comparison, typed
  suggestions with a reapplication and owner, and one question with 2-4 options
- whether an existing `design/external-scan.md` should be updated or reused

Never ask a question from the subagent: it has no question widget. Never accept
a raw research dump as the final answer. If the agent reports
`NOT ASSESSED — NO DATA`, keep that verdict and surface it in Phase 3.

## Phase 3 — Deliver the decision

Use the agent's **Question for the orchestrator** verbatim in a single question
tool call. Keep the agent's 2-4 short options, recommendation and trade-offs;
do not rewrite them into a longer essay or put the research table before the
call. The user's answer is the decision; report only the chosen option and the
sources needed to justify it.

After the answer, offer the scan for writing through the same widget: "May I
write this to `design/external-scan.md`?" Write the file in the format from
`.claude/docs/external-scan.md` only on explicit approval; mark proposals
`proposed`. Then offer one follow-up through the same widget: `prototype`,
`design-system`, `create-architecture`, `code-review`, or "research another
target". Do not start that work or apply a proposal without a separate
confirmation.

**Verdict:** `COMPLETE — research delivered` after the user answers,
`COMPLETE — research declined` when they skip external research, or
`NOT ASSESSED — <reason>` when the agent or widget could not run.

---

## Next step

After the verdict, offer `/next-step` for what to do in the project now.
