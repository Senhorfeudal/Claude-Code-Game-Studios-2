---
name: team-qa
description: "Orchestrate the QA team through a full testing cycle — qa-lead strategy and test plan, qa-tester case writing, execution, sign-off."
argument-hint: "[sprint | feature: system-name] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(bash "*/.claude/skills/team-qa/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

# Team QA

When this skill is invoked, orchestrate the QA team through a structured testing cycle.

**Decision Points:** At each phase transition, use `AskUserQuestion` to present
the user with the specialist pass's proposals as selectable options. Write the pass's
full analysis in conversation, then capture the decision with concise labels.
In `collaborative` mode, the user must approve before moving to the next phase.
In `guided` mode the pipeline advances automatically unless a phase is BLOCKED;
in `autonomous` mode it runs end to end, recording each phase outcome via
`log_decision`. Decisions in `automation_always_ask` categories
(`is_always_ask_category` helper) always prompt regardless of mode. See
`.claude/docs/automation-modes.md`.

**In-chat orchestration:** this team runs in the conversation the user opened —
never as a subagent and never inside a subagent conversation. Each specialist
pass is performed inline by this orchestrator, reading that specialist's
`.claude/agents/<id>.md` for its domain rules. Every decision and write approval
is asked here with `AskUserQuestion`; nothing is forwarded to a parent. If this
skill is somehow invoked inside a subagent, stop and tell the caller to load the
team skill in the main chat. See `.claude/docs/in-chat-teams.md`.

## Phase 0: Resolve Config

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,team.size,qa.level`

Resolved above — use as-is; `--review` overrides `review_mode`. No block →
defaults in `.claude/docs/config-resolution.md`.

`qa.level` decides what a Logic, Integration or Config/Data story's evidence is:
its automated test at `standard` and `full`; at `minimal`, where tests are waived
(`.claude/docs/coding-standards.md`), the acceptance-criteria walk in Phase 5 —
a story without a test is then WAIVED, not missing its evidence. The UI and
Visual/Feel screenshots are required at every level.

`review_mode` sets director-gate depth, and this pipeline has no director gate:
no phase below runs CD-, TD-, PR- or AD-PHASE-GATE, at any `review_mode`. Its
phase gates are the pipeline's own decision points (defined under `team.size`
below), and the roles that work at them are team members, not director gates.

`automation` drives the Decision Points note above. See the Decision Points note above and
`.claude/docs/automation-modes.md` for how each mode changes pipeline behavior.

**`team.size`**: which specialist roles are active (orthogonal to review_mode gate-depth and workflow docs).
- **`individual`** (default): `qa-tester` only; `qa-lead` invoked at phase gates only.
- **`small`**: `qa-lead` + `qa-tester` pipeline (as documented).
- **`studio`**: `qa-lead` + per-story `qa-tester` pass + sign-off.
A non-core role needed at `individual` is folded into the nearest active core role with an informational note. **"Phase gate" means any phase that ends in an `AskUserQuestion` decision point this pipeline itself lists** — a transition under Decision Points above, or a **Gate** step written into the pipeline below — **whatever the `automation` mode**: in `guided` or `autonomous`, where that question is skipped or logged, the phase is still a gate. Not every phase is one. Apply the test literally: if the phase below lists no decision point, it is not a gate, and a role restricted to "phase gates only" is not performed for it. This active-set scoping applies throughout the pipeline below: any phase that names a role outside the active set is folded into the nearest core role rather than performed as a separate pass.

**Announce the active set before Phase 1 — never let the collapse be silent.**
Before starting Phase 1, state in one line which specialist roles this run will
perform inline, and which the pipeline below names but will **not** perform at
the resolved `team.size`. For example:

> `Active roles (team.size: <resolved>): <the roles listed for that size above>.`
> `Not performed this run: <every other role this pipeline names> — folded into`
> `the nearest active core role. Raise team.size (or modes.rigor) to widen.`

Fill it from the `team.size` list directly above and the roles this file's own
pipeline names — not from an example. Both sets differ per orchestrator.
A role the resolved size performs only at phase gates (`qa-lead` at
`individual`) goes in the active set with that qualifier — it is performed, not
folded into another role.

The pipeline below reads as a multi-role sequence and at the shipped default it
is one or two roles — `team-release` names ten and performs one, `team-narrative`
names six across five phases and performs `writer` alone. **The collapse is correct**:
`team.size` is rigor-fronted and the narrow default is the token lever.
Without saying so, a reader cannot
distinguish a correctly-collapsed run from a broken pipeline, and the per-role
"folded into the nearest core role with an informational note" rule above
fires at routing time and never states the shape of the run as a whole.

This is the same rule as the skipped-check reporting elsewhere in this file: **a constraint that is enforced but never surfaced is
indistinguishable, to the person reading the output, from one that was never
enforced.**

## Team Composition

- **qa-lead** — QA strategy, test plan generation, story classification, sign-off report
- **qa-tester** — Test case writing, bug report writing, manual QA documentation

## How to Run Inline

Run each specialist pass inline in this chat. Read the role's
`.claude/agents/<id>.md` for its domain rules, then perform the work here. Never
call `Agent` / `subagent` for a team or for a specialist:
- **qa-lead** — Strategy, planning, classification, sign-off
- **qa-tester** — Test case writing and bug report writing

**Use context once — do not re-read.** Read the shared inputs **once** in this
chat and keep only the sections each pass actually needs. Never re-open a whole
document you already hold; a role performed inline has the same context you do.

**Present each pass compactly.** In the chat, give the artifact path, ≤5
bullets of decisions, and any BLOCKED/CONCERNS items, one line each. Do not
restate the documents you read. Every write still follows the ask-first protocol
in this same chat (File Write Protocol below).

> **Why no bounded exception is needed.** `CLAUDE.md` requires "May I write this
> to [filepath]?" before Write/Edit. Because the orchestrator performs every pass
> itself in the user's chat, that normal rule applies to every artifact: show the
> draft or file set, ask, wait for yes, then write. There is no per-pass write
> authority to hand out and no question for a parent to answer.

At `team.size: studio`, Phase 4 runs one qa-tester pass per story; below that, one pass covers the whole group.

## Pipeline

### Phase 1: Load Context

Before doing anything else, gather the full scope:

1. Detect the current sprint or feature scope from the argument:
   - If argument is a sprint identifier (e.g., `sprint-03`): Glob `production/sprints/sprint-*.md` and match by sprint number — `sprint-3`, `sprint-03` and `sprint-003` all name sprint 3 (`/sprint-plan` writes `sprint-NNN.md`). Read the matched file. If multiple match, use the most recently modified.
   - If argument is `feature: [system-name]`: glob story files tagged for that system
   - If no argument: read `production/session-state/active.md` and `production/sprint-status.yaml` (if present) to infer the active sprint. If there is no sprint — at `rigor: minimal` there are none — ask which epic to cover and use `feature: [epic-slug]`; do not invent a sprint

2. Read `project.stage` from `project.yaml` (fallback `production/stage.txt`) to confirm the current project phase.

3. **Read the open bugs in scope** — the bugs already on file, before QA finds new ones: grep the `**Severity**`, `**Status**` and `**System**` lines of `production/qa/bugs/*.md`, as `/bug-triage` does. A bug is open unless its Status is `Closed` or `Verified Fixed`; it is in scope when its System is one the in-scope stories belong to, or it names an in-scope story — when unsure, list it. These go into the Phase 2 and Phase 6 briefs as **Open bugs in scope**: an open S1 or S2 here already makes the sign-off NOT APPROVED (Phase 6), whatever QA finds. No bug files → "Open bugs in scope: none on file".

4. Count stories found and report to the user:
   > "QA cycle starting for [sprint/feature]. Found [N] stories. Open bugs in scope: [N — S1: n, S2: n, or none on file]. Current stage: [stage]. Ready to begin QA strategy?"

### Phase 2: QA Strategy (qa-lead)

Run the `qa-lead` pass inline to review all in-scope stories and produce a QA strategy.

Pass the qa-lead the **Open bugs in scope** from Phase 1 (ID, severity, story or system), then prompt it to:
- Read each story file
- Classify each story by type: **Logic** / **Integration** / **Visual/Feel** / **UI** / **Config/Data**
- Identify which stories require automated test evidence vs. manual QA — at `qa.level: minimal` none requires a test: a Logic, Integration or Config/Data story without one reads `WAIVED` under Automated Required and gets its acceptance criteria walked in manual QA
- Flag any stories with missing acceptance criteria or missing test evidence that would block QA
- Estimate manual QA effort (number of test sessions needed)
- **Before assessing smoke status, check for an existing smoke check report**: Glob `production/qa/smoke-*.md` and read the most recently modified file (if found). If a report exists, use its verdict and findings directly — do not re-interview the user. If no report exists, note: "No prior smoke check report found — run `/smoke-check sprint` before proceeding." and set smoke check status to UNKNOWN (treat as PASS WITH WARNINGS for the purpose of continuing). Produce a smoke check verdict: **PASS** / **PASS WITH WARNINGS [list]** / **NOT ASSESSED [what did not run]** / **FAIL [list of failures]** / **UNKNOWN (no report found)**
- Produce a strategy summary table and smoke check result:

  | Story | Type | Automated Required | Manual Required | Blocker? |
  |-------|------|--------------------|-----------------|----------|

  **Smoke Check**: [PASS / PASS WITH WARNINGS / NOT ASSESSED / FAIL / UNKNOWN] — [source: `production/qa/smoke-[date].md` or "no report found"] — [details if not PASS]

  **Open bugs in scope**: [BUG-ID — S[n] — story or system, one per line; or "none on file"] — an open S1 or S2 is named here as a known failure

If the smoke check result is **FAIL**, the qa-lead must list the failures prominently. QA cannot proceed past the strategy phase with a failed smoke check.

Present the qa-lead's full strategy to the user, then use `AskUserQuestion`:

```
question: "QA Strategy Review"
options:
  - "Looks good — proceed to test plan"
  - "Adjust story types before proceeding"
  - "Skip blocked stories and proceed with the rest"
  - "Smoke check failed — fix issues and re-run /team-qa"
  - "Cancel — resolve blockers first"
```

If smoke check **FAIL**: do not proceed to Phase 3. Surface the failures from the smoke check report and stop. The user must fix them, re-run `/smoke-check sprint`, and then re-run `/team-qa`.
If smoke check **UNKNOWN**: surface a warning — "No smoke check report found. Recommend running `/smoke-check sprint` before QA. Proceeding with caution."
If smoke check **NOT ASSESSED**: surface what the report says did not run — "The last smoke check could not assess [what did not run]. Recommend re-running `/smoke-check sprint` once it can. Proceeding with caution." — and continue as for UNKNOWN; the sign-off cannot be APPROVED on it (Phase 6).
If smoke check **PASS WITH WARNINGS**: note the warnings for the sign-off report and continue.
If blockers are present: list them explicitly. The user may choose to skip blocked stories or cancel the cycle.

### Phase 3: Test Plan Generation

Using the strategy from Phase 2, produce a structured test plan document.

The test plan should cover:
- **Scope**: sprint/feature name, story count, dates
- **Story Classification Table**: from Phase 2 strategy
- **Automated Test Requirements**: which stories need test files, expected paths in `tests/` (none at `qa.level: minimal`: list the waived stories under Manual QA Scope instead)
- **Manual QA Scope**: which stories need manual walkthrough and what to validate
- **Out of Scope**: what is explicitly not being tested this cycle and why
- **Entry Criteria**: what must be true before QA can begin. Always include: (1) Smoke check PASS or PASS WITH WARNINGS report exists at `production/qa/smoke-*.md`, (2) build is stable (no crashes on launch), (3) at sprint scope, all Must Have stories are `in-progress`, `review` or `done` in `production/sprint-status.yaml`; at `feature:` scope, every in-scope story file's Status is In Progress, In Review or Complete. Add any sprint-specific criteria beyond these.
- **Exit Criteria**: what constitutes a completed QA cycle (all stories PASS or FAIL with bugs filed)

Ask: "May I write the QA plan to `production/qa/qa-plan-[sprint]-[date].md`?"

Write only after receiving approval.

### Phase 4: Test Case Writing (qa-tester)

> **Smoke check** is performed as part of Phase 2 (QA Strategy). If the smoke check returned FAIL in Phase 2, the cycle was stopped there. This phase only runs when the Phase 2 smoke check was PASS, PASS WITH WARNINGS, NOT ASSESSED, or UNKNOWN.

For each story requiring manual QA (Visual/Feel, UI, Integration without automated tests — and, at `qa.level: minimal`, where tests are waived, every Logic, Integration and Config/Data story without a test: its cases walk its acceptance criteria):

Run the `qa-tester` pass inline — one pass per story at `team.size: studio`; one pass covering the whole group at `small` and `individual` — providing, for each story:
- The story file path
- The relevant section of the QA plan for that story
- The GDD acceptance criteria for the system being tested (if available)
- Instructions to write detailed test cases covering all acceptance criteria
- **The output path: `production/qa/test-cases/[story-slug]-cases.md`.** Name it
  explicitly in the prompt, one per story.

> **Why the path is stated here rather than left to the orchestrator.** Every
> write in this chat needs an approval naming its destination, so naming the path
> in this phase is what makes the ask concrete. This is the phase that runs passes
> in sequence, so an unnamed destination does the most damage: each pass would
> improvise its own, and two runs file the same artifact in two places.

Each test case set should include:
- **Preconditions**: game state required before testing begins
- **Steps**: numbered, unambiguous actions
- **Expected Result**: what should happen
- **Actual Result**: field left blank for the tester to fill in
- **Pass/Fail**: field left blank

Present the test cases to the user for review before execution. Group by story.

Use `AskUserQuestion` per story group (batched 3-4 at a time):

```
question: "Test cases ready for [Story Group]. Review before manual QA begins?"
options:
  - "Approved — begin manual QA for these stories"
  - "Revise test cases for [story name]"
  - "Skip manual QA for [story name] — not ready"
```

### Phase 5: Manual QA Execution

Walk through each story in the approved manual QA list.

Batch stories into groups of 3-4 and use `AskUserQuestion` for each. **Wait for
the tester's answer** and record only what they said: a result the tester did not
give is never filled in for them. A story nobody answered for stays unexecuted,
which makes the sign-off NOT ASSESSED — it is not BLOCKED unless they say so.

```
question: "Manual QA — [Story Title]\n[brief description of what to test]"
options:
  - "PASS — all acceptance criteria verified"
  - "PASS WITH NOTES — minor issues found (describe after)"
  - "FAIL — criteria not met (describe after)"
  - "BLOCKED — cannot test yet (reason)"
```

After each FAIL result: use `AskUserQuestion` to collect the failure description, then run the `qa-tester` pass inline to write a formal bug report in `production/qa/bugs/`, in `/bug-report`'s format — its Severity and Priority labels exactly as that template lists them (`S2-High`, `P1-Fix this sprint`, …), because `/bug-triage` parses them.

**After each PASS or PASS WITH NOTES on a Visual/Feel or UI story, record its
evidence in `production/qa/evidence/`.** The retained screenshot is the
evidence: ask the tester to save one of each screen or effect the story touched
under `production/qa/evidence/[story-slug]/`, and confirm it is on disk —
`/story-done` checks for a retained image, not just the write-up. A UI story is
closed by those screenshots; a Visual/Feel story also needs the lead sign-off.
Then ask "May I write the evidence for [story titles] to
`production/qa/evidence/`?", once per story group, and write the evidence
artifact `production/qa/evidence/[story-slug]-evidence.md` from
`.claude/docs/templates/test-evidence.md`, carrying the sign-off table intact and
referencing the screenshots. If no screenshot was saved, name that story in the
Phase 5 summary as missing its retained evidence rather than writing a doc that
implies one.

> **This is not optional bookkeeping — it is the artifact the next skill gates
> on.** `/story-done` globs `production/qa/evidence/` for Visual/Feel and UI
> stories and reads the sign-off table; `/story-readiness`,
> `/test-evidence-review` and `gate-release` read the same directory. Write
> anywhere else and a story can pass a full manual QA cycle here, then be told by
> `/story-done` that no visual evidence exists. Visual/Feel and UI gates are
> **BLOCKING by default**, so that is a deadlock — QA passed, story cannot
> close. It is a merely confusing flag only where `testing.strict.ui` or
> `.visual` has been explicitly set to `false`.
>
> Leave the sign-off rows **unchecked** unless the sign-off actually happened in
> this session. An evidence file with pre-ticked approvals is worse than none: it
> converts a missing signature into a recorded one.

Bug report naming: `BUG-[NNNN].md`, numbered the way `/bug-report` numbers them — the
highest ID in `production/qa/bugs/` plus one, zero-padded to four digits — so
`/bug-report verify` and `close` can find it by its ID.

After collecting all results, summarize:
- Stories PASS: [count]
- Stories PASS WITH NOTES: [count]
- Stories FAIL: [count] — bugs filed: [IDs]
- Stories BLOCKED: [count]

### Phase 6: QA Sign-Off Report

Run the `qa-lead` pass inline to draft the sign-off report using all results from Phases 2–5. **Here the result is the report text in this chat, not a file:** you write the sign-off after the ask at the end of this phase, so the pass writes nothing.

**Brief the qa-lead with the evidence and the verdict rules below — never a verdict.** Pass the strategy table, the smoke check verdict and its source, each story's result, the bugs filed in Phase 5 and the **Open bugs in scope** from Phase 1, and the verdict rules below, verbatim. Do not name a verdict, pre-fill the `### Verdict:` line, or say which fact decides it: the qa-lead applies the rules to the evidence. Then check its verdict against the same rules before asking to write; if they disagree, show both and ask — never silently substitute your own.

The sign-off report format:

```markdown
## QA Sign-Off Report: [Sprint/Feature]
**Date**: [date]

### Test Coverage Summary
| Story | Type | Auto Test | Manual QA | Result |
|-------|------|-----------|-----------|--------|
| [title] | Logic | PASS | — | PASS |
| [title] | Logic | WAIVED (qa.level: minimal) | PASS — criteria walked | PASS |
| [title] | Visual | — | PASS | PASS |
| [title] | Integration | — | BLOCKED | BLOCKED — [reason]; no executed evidence |

### Bugs Found
| ID | Story | Severity | Status |
|----|-------|----------|--------|
| BUG-0001 | [story] | S2 | Open |

[every open bug in scope — those Phase 1 found on file and those filed in Phase 5]

### Verdict: NOT ASSESSED / APPROVED / APPROVED WITH CONDITIONS / NOT APPROVED

**Conditions** (if any): [list what must be fixed before the build advances]

### Next Step
[guidance based on verdict]
```

**Every story in scope gets a Test Coverage Summary row** — BLOCKED and
unexecuted stories included, with the reason in Result — so a story that never
ran cannot drop out of the report.

Verdict rules:

**Order.** Check **NOT APPROVED first**: any open S1/S2 bug in scope — one already on file (Phase 1) as much as one filed in Phase 5 — or a story that
FAILs without a documented workaround, makes the verdict NOT APPROVED whatever
else went unexecuted — a known failure outranks an unknown, and demoting it to
NOT ASSESSED would bury it (`.claude/rules/skill-authoring.md`, obligation 1).

**Then the precondition.** APPROVED and APPROVED WITH CONDITIONS both require
that **every story in scope produced executed evidence** — a test that ran, or a
manual case that was walked. At `qa.level: minimal` a Logic, Integration or
Config/Data story's acceptance-criteria walk is its executed evidence: its tests
are WAIVED, not missing. If any story is BLOCKED, unexecuted, or has no
evidence, the verdict is **NOT ASSESSED**, not either kind of APPROVED. A smoke
check that was UNKNOWN (no report found) or NOT ASSESSED in Phase 2 also makes it
NOT ASSESSED: the build's health was never checked.

- **NOT ASSESSED — NO EVIDENCE**: One or more stories produced no executed
  evidence (BLOCKED, tests not written at `qa.level` standard/full, cases not
  walked, or smoke check FAIL / UNKNOWN / NOT ASSESSED). This is **not** a pass
  and **not** a fail; it means QA did not happen. Say which stories and why.
- **APPROVED**: All stories PASS or PASS WITH NOTES; no S1/S2 bugs open
- **APPROVED WITH CONDITIONS**: S3/S4 bugs open, or PASS WITH NOTES issues documented; no S1/S2 bugs
- **NOT APPROVED**: Any S1/S2 bugs open; or stories FAIL without documented workaround

> **Why the precondition exists.** The three rules below it assume
> every story resolves to PASS or FAIL. A sprint where nothing was executed
> trips none of the NOT APPROVED conditions and **vacuously satisfies "no S1/S2
> bugs open"** — because zero executed tests means zero observed failures. Read
> literally, and without this precondition, the rules let a completely untested
> build reach APPROVED — a `qa-lead` reaching NOT APPROVED on intent would find
> the letter of the rules did not support it. A
> sign-off asserts verified quality; without this precondition the rules cannot
> tell "verified good" from "never looked".

Next step guidance by verdict:
- NOT ASSESSED: "QA did not run to completion. Produce the missing evidence — write the Logic tests (at `qa.level` standard/full) or walk the waived stories' acceptance criteria (at `minimal`), walk the manual cases, run `/smoke-check` — then re-run `/team-qa`. Do not advance the build on this verdict."
- APPROVED: "Build is ready for the next phase. Run `/gate-check` to validate advancement."
- APPROVED WITH CONDITIONS: "Resolve conditions before advancing. S3/S4 bugs may be deferred to polish."
- NOT APPROVED: "Resolve S1/S2 bugs and re-run `/team-qa` or targeted manual QA before advancing."

Ask: "May I write this QA sign-off report to `production/qa/qa-signoff-[sprint]-[date].md`?"

Write only after receiving approval.

## File Write Protocol

All artifacts in this cycle are written by this orchestrator in the current chat.
Before each write — QA plan, test cases, bug reports, evidence or sign-off
report — show the draft or file set and ask "May I write this
to [path]?"; wait for approval. There is no subagent exception — no `Agent` /
`subagent` writes anything.

## Error Recovery Protocol

**First, verify the artifact.** If the pass named a path, check the
path exists before treating the phase as done — **a named artifact that is not
on disk is a failed phase, however fluent the response reads.** A pass can
burn a full phase and produce a plausible preamble having written nothing, which
is neither BLOCKED nor an error nor "cannot complete", so the trigger below
never fires. Resume the pass naming the unmet contract; the context is
usually still there.

If any pass returns BLOCKED, errors, or cannot complete: **surface it
immediately, don't proceed past a dependency it blocks, and always produce a
partial report.** Full procedure: `.claude/docs/error-recovery-protocol.md`.

Common blockers:
- Input file missing (story not found, GDD absent) → redirect to the skill that creates it
- ADR status is Proposed → do not implement; once it is decided, accept it with `/architecture-decision accept ADR-NNNN`
- Scope too large → split into two stories via `/create-stories`
- Conflicting instructions between ADR and story → surface the conflict, do not guess

## Output

A summary covering: stories in scope, smoke check result, manual QA results, bugs filed (with IDs and severities), and the final APPROVED / APPROVED WITH CONDITIONS / NOT APPROVED / NOT ASSESSED verdict.

Verdict: **COMPLETE** — QA cycle finished.
Verdict: **BLOCKED** — smoke check failed or critical blocker prevented cycle completion; partial report produced.

## Session State Update

After the final phase completes (sign-off report written or BLOCKED verdict reached), silently append to `production/session-state/active.md`:

```
<!-- QA RUN: [date] | Sprint: [sprint identifier or "ad-hoc"] | Verdict: [APPROVED/APPROVED WITH CONDITIONS/NOT APPROVED/NOT ASSESSED/BLOCKED] | Report: production/qa/qa-signoff-[sprint]-[date].md -->
```
