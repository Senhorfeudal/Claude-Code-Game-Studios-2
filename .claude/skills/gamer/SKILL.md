---
name: gamer
description: "External scout — finds similar games and repositories on the web, forums and GitHub, studies their structure, and returns sourced suggestion options to the orchestrator. Use when research outside the repo would change a decision."
argument-hint: "[research brief: engine, platform, feature and decision]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Agent, AskUserQuestion
model: sonnet
---

# Gamer — external scout

This skill makes the `gamer` agent reachable from the skill list. It is
read-only: it writes no files and changes no code. The agent researches the
web, forums and GitHub; this skill owns the question widget and puts the
agent's recommendation to the user.

## Phase 1 — Build a narrow brief

Read `project.yaml` for engine, platform and stage. Read the concept or GDD in
scope and name the local files that matter. If the invocation already names a
feature and a decision, use that brief. Otherwise call the question tool
immediately, with no reasoning or draft text before it:

- Question: "What should the external scout research, and what decision must it inform?"
- Options: "Similar games for this mechanic", "Open-source implementations",
  "Engine docs and reusable tooling", "Decide without external research"
- The runtime's free-text affordance covers a custom brief; say so in the question
- Mark one option as recommended with the trade-off in its description

A skipped or dismissed question is not an answer: re-ask once through the
widget, then use the plain-text fallback in `.claude/docs/automation-modes.md`.
Only a real choice proceeds. **Decide without external research** ends with
`COMPLETE — research declined`.

## Phase 2 — Delegate to the agent

If the runtime has no `Agent` tool, answer
`NOT ASSESSED — NO AGENT TOOL` and name the `gamer` agent for direct invocation.
Otherwise spawn **one** `gamer` subagent with a brief containing:

- the engine, platform and stage from `project.yaml`
- the feature or mechanic and the decision the research must inform
- the local files read in Phase 1, with no pasted document contents
- the agent's output contract: research brief table, local comparison,
  suggestions with owner, and one question with 2-4 options

Never ask a question from the subagent: it has no question widget. Never accept
a raw research dump as the final answer. If the agent reports
`NOT ASSESSED — NO DATA`, keep that verdict and surface it in Phase 3.

## Phase 3 — Deliver the decision

Use the agent's **Question for the orchestrator** verbatim in a single question
tool call. Keep the agent's 2-4 short options, recommendation and trade-offs;
do not rewrite them into a longer essay or put the research table before the
call. The user's answer is the decision; report only the chosen option and the
sources needed to justify it.

After the answer, offer one follow-up through the same widget: `prototype`,
`design-system`, `create-architecture`, `code-review`, or "research another
target". Do not start that work without a separate confirmation.

**Verdict:** `COMPLETE — research delivered` after the user answers,
`COMPLETE — research declined` when they skip external research, or
`NOT ASSESSED — <reason>` when the agent or widget could not run.

---

## Next step

After the verdict, offer `/next-step` for what to do in the project now.
