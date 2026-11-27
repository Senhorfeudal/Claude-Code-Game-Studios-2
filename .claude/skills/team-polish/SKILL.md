---
name: team-polish
description: "Orchestrate the polish team — performance-analyst, technical-artist, sound-designer, qa-tester — to optimize and harden a feature or area."
argument-hint: "[feature or area to polish] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-polish/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
# Team Polish

If no argument is provided, output usage guidance and exit without starting any pass:
> Usage: `/team-polish [feature or area to polish] [--review full|lean|solo]` — specify the feature or area to polish (e.g., `combat`, `main menu`, `inventory system`, `level-1`). Do not use `AskUserQuestion` here; output the guidance directly.

When this skill is invoked with an argument, orchestrate the polish team through a structured pipeline.

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

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,team.size,workflow`

Resolved above — use as-is; `--review` overrides `review_mode`. No block →
defaults in `.claude/docs/config-resolution.md`.

`review_mode` sets director-gate depth, and this pipeline has no director gate:
no phase below runs CD-, TD-, PR- or AD-PHASE-GATE, at any `review_mode`. Its
phase gates are the pipeline's own decision points (defined under `team.size`
below), and the roles that work at them are team members, not director gates.

`automation` drives the Decision Points note above. See the Decision Points note above and
`.claude/docs/automation-modes.md` for how each mode changes pipeline behavior.

**`team.size`**: which specialist roles are active (orthogonal to review_mode gate-depth and workflow docs).
- **`individual`** (default): `performance-analyst` + `technical-artist`. Other roles folded into these two, not performed separately. No programmer is active, so the optimisation list's programmer items are not implemented in this run — the report names the list as handed to `/dev-story` (Phase 2).
- **`small`**: + `sound-designer` + `qa-tester` + `engine-programmer`, and `tools-programmer` when Phase 1 traces a cause to a content authoring tool (the full pipeline as documented).
- **`studio`**: the `small` set, `engine-programmer` included, + an adversarial review pass: Phase 5's qa-tester is told "your job is not to confirm this holds — find how it breaks", and the report says the pass ran. This pipeline has no engine specialist to widen; engine-level work stays with `engine-programmer`.
A non-core role needed at `individual` is folded into the nearest active core role with an informational note. **"Phase gate" means any phase that ends in an `AskUserQuestion` decision point this pipeline itself lists** — a transition under Decision Points above, or a **Gate** step written into the pipeline below — **whatever the `automation` mode.** `guided` and `autonomous` change how a gate is passed (it auto-advances, or is recorded with `log_decision`), not whether it is one, so the gate stays a gate in every mode. A role restricted to "phase gates only" is performed at those points and no others. This active-set scoping applies throughout the pipeline below: any phase that names a role outside the active set is folded into the nearest core role rather than performed as a separate pass.

**Announce the active set before Phase 1 — never let the collapse be silent.**
Before starting Phase 1, state in one line which specialist roles this run will
perform inline, and which the pipeline below names but will **not** perform at
the resolved `team.size`. For example:

> `Active roles (team.size: <resolved>): <the roles listed for that size above>.`
> `Not performed this run: <every other role this pipeline names> — folded into`
> `the nearest active core role. Raise team.size (or modes.rigor) to widen.`

Fill it from the `team.size` list directly above and the roles this file's own
pipeline names — not from an example. Both sets differ per orchestrator.

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
- **performance-analyst** — Profiling, memory analysis, frame budget, and the optimisation list — it writes no game code
- **engine-programmer** — Implements the optimisation list's engine-level items: rendering pipeline, memory, resource loading, hot paths (invoke when performance-analyst identifies low-level root causes)
- **technical-artist** — VFX polish, shader optimization, visual quality
- **sound-designer** — Audio polish, mixing, ambient layers, feedback sounds
- **tools-programmer** — Content pipeline tool verification, editor tool stability, automation fixes (Phase 2, when Phase 1 traces a cause to a content authoring tool)
- **qa-tester** — Edge case testing, regression testing, soak testing

## How to Run Inline

Run each specialist pass inline in this chat. Read the role's
`.claude/agents/<id>.md` for its domain rules, then perform the work here. Never
call `Agent` / `subagent` for a team or for a specialist:
- **performance-analyst** — Profiling, memory analysis, the optimisation list
- **engine-programmer** — Engine-level fixes from the optimisation list: rendering, memory, resource loading
- **technical-artist** — VFX polish, shader optimization, visual quality
- **sound-designer** — Audio polish, mixing, ambient layers
- **tools-programmer** — Content pipeline and editor tool fixes from the optimisation list
- **qa-tester** — Edge case testing, regression testing, soak testing

**Use context once — do not re-read.** Read the shared inputs **once** in this
chat and keep only the sections each pass actually needs. Never re-open a whole
document you already hold; a role performed inline has the same context you do.

**Present each pass compactly.** In the chat, give the artifact path, ≤5
bullets of decisions, and any BLOCKED/CONCERNS items, one line each. Do not
restate the documents you read. Every write still follows the ask-first protocol
in this same chat (File Write Protocol below).

**Substitute a real path for `[path]` — this skill's destination is
`production/polish/`.** Name it per role, one file each:

| Role | Writes to |
|---|---|
| performance-analyst | `production/polish/[area]-report-[date].md` |
| technical-artist | `production/polish/[area]-render-notes-[date].md` |
| engine-programmer | `production/polish/[area]-engine-fixes-[date].md` |
| tools-programmer | `production/polish/[area]-tool-fixes-[date].md` |
| sound-designer | `production/polish/[area]-audio-notes-[date].md` |
| qa-tester | `production/polish/[area]-verification-[date].md` |

> **Why `production/` and not `docs/`.** These are date-stamped measurements of
> one run, the same shape as `production/qa/smoke-[date].md` — not durable
> specifications like `docs/architecture/`. Keeping them beside the other
> point-in-time process artifacts is what makes a later comparison possible.
>
> The `[path]` contract above has a precondition: the path is one *you* named, so
> a concrete destination must be stated here or every run invents one. Unlike
> `/team-qa` and `/team-narrative`, whose destinations are fixed by their
> consumers, this location has no reader in the repo and was chosen deliberately.
> **Nothing reads `production/polish/` yet** — say so when reporting, so the user
> knows the report is a record rather than an input to a later gate.

> **Why no bounded exception is needed.** `CLAUDE.md` requires "May I write this
> to [filepath]?" before Write/Edit. Because the orchestrator performs every pass
> itself in the user's chat, that normal rule applies to every artifact: show the
> draft or file set, ask, wait for yes, then write. There is no per-pass write
> authority to hand out and no question for a parent to answer.

Run independent passes in sequence in this chat where the pipeline allows it (e.g., Phases 3 and 4 can run simultaneously).

## Pipeline

### Phase 1: Assessment
Run the **performance-analyst** pass inline:
- Profile the target feature/area using `/perf-profile`
- Identify performance bottlenecks and frame budget violations
- Measure memory usage and check for leaks
- Benchmark against target hardware specs
- Output: performance report with the prioritized **optimisation list** — for each item, the change, its expected gain against the budget, and its owner (technical-artist for rendering-side changes, engine-programmer for engine systems and hot paths, tools-programmer for a content authoring tool, otherwise the programmer who owns the system)

### Phase 2: Optimization
performance-analyst writes no game code ("recommend and assign", its role file),
so Phase 2 implements its Phase 1 list through the owners in the active set:
- **engine-programmer** — performed only when Phase 1 identified engine-level root causes (rendering pipeline, resource loading, memory allocator, hot paths in core loops): implement those items, fix allocation pressure, verify gameplay behavior is unchanged. Output: engine-level fixes with before/after metrics and profiler validation
- **tools-programmer** — only when Phase 1 traced a cause to a content authoring tool: fix the tool. Output: tool fixes with before/after metrics
- **technical-artist** — rendering-side items (draw calls, overdraw, particles, shaders, LOD) join its Phase 3 brief

Every implementation pass in Phases 2–4 first lists the files it will create or
change, and you ask once for the whole Phase 2–4 set before any is edited (File
Write Protocol).

**An item whose owner is not in the active set is not implemented in this run.**
At `team.size: individual` that is every programmer item, since no programmer is
active; at any size it includes an item owned by a programmer this pipeline does
not name (e.g. gameplay-programmer for a gameplay-script hot spot). The report
lists those items with their owners under
"Optimisation list handed to `/dev-story`: `production/polish/[area]-report-[date].md`".
A metric they target that is over budget stays a known problem at Phase 6.

### Phase 3: Visual Polish (parallel with Phase 2)
Run the **technical-artist** pass inline:
- Review VFX for quality and consistency with art bible
- Optimize particle systems and shader effects
- Add screen shake, camera effects, and visual juice where appropriate
- Ensure effects degrade gracefully on lower settings
- Output: polished visual effects

### Phase 4: Audio Polish (parallel with Phase 2)
Run the **sound-designer** pass inline:
- Review audio events for completeness (are any actions missing sound feedback?)
- Check audio mix levels — nothing too loud or too quiet relative to the mix
- Add ambient audio layers for atmosphere
- Verify audio plays correctly with spatial positioning
- Output: audio polish list and mixing notes

### Phase 5: Hardening
Run the **qa-tester** pass inline:
- Test all edge cases: boundary conditions, rapid inputs, unusual sequences
- Soak test: run the feature for extended periods checking for degradation
- Stress test: maximum entities, worst-case scenarios
- Regression test: verify polish changes haven't broken existing functionality — each Phase 2–4 change by name, engine-level fixes included
- Test on minimum spec hardware (if available)
- Output: test results with any remaining issues

### Phase 6: Sign-off
- Collect results from all team members
- Compare performance metrics against budgets
- Report: READY FOR RELEASE / NOT ASSESSED / NEEDS MORE WORK
- List every remaining issue with its severity (S1–S4), the measured gap where there is one (e.g. "9 ms against a 6 ms budget — 3 ms over"), and a recommendation; a regression also names the broken behavior and the polish change that caused it

**NOT ASSESSED ranks above READY FOR RELEASE and below NEEDS MORE WORK.** A known
problem — a metric over budget, an unresolved regression — makes it NEEDS MORE
WORK whatever else went unchecked. Otherwise, if any part of the scope could not
be checked, the result is NOT ASSESSED, never READY FOR RELEASE, and the report
names each gap:
- A metric with no committed budget. `performance.target_framerate`,
  `performance.frame_budget_ms`, `performance.draw_call_limit` and
  `performance.memory_ceiling_mb` have no default, and `/perf-profile` reports an
  unset one as NOT ASSESSED — nothing was compared, so no budget was met.
- A phase that did not run: BLOCKED, skipped, or its role outside the active set.
  At `team.size: individual`, sound-designer's audio polish and qa-tester's
  hardening are only folded into the active roles, not run, and Phase 2's
  programmer items are handed to `/dev-story` rather than implemented.

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
partial report.** A skipped role's section stays a named gap — never fill it with content of your own. Full procedure: `.claude/docs/error-recovery-protocol.md`.

Common blockers:
- Input file missing (story not found, GDD absent) → redirect to the skill that creates it
- ADR status is Proposed → do not implement; once it is decided, accept it with `/architecture-decision accept ADR-NNNN`
- Scope too large → split into two stories via `/create-stories`
- Conflicting instructions between ADR and story → surface the conflict, do not guess

## File Write Protocol

Every write in this pipeline is made by this orchestrator in the current chat.
Before each write, show the draft or the exact file set and ask "May I write this
to [path]?"; wait for approval. There is no subagent exception — no role writes
on its own, and no write happens while a question is still open.

Implementation files (code, shaders, audio and assets) are named as one set
before the write: list every file you will create or change with a one-line
summary, ask once for the whole set, and write only after a yes. An edit to an
existing file is always on that list.

Working drafts go to the paths named in "How to Run Inline" above. Final
documents under `design/` are compiled here from those drafts and written only
after their own "May I write …?" prompt.

## Output

A summary report covering: performance before/after metrics, visual polish changes, audio polish changes, test results, any optimisation list handed to `/dev-story`, and release readiness assessment.

## Next Steps

- If READY FOR RELEASE: run `/release-checklist` for the final pre-release validation.
- If NEEDS MORE WORK: schedule remaining issues in `/sprint-plan update` (at `workflow: minimal`, which has no sprints, add them to the brief's build order) and re-run `/team-polish` after fixes.
- If NOT ASSESSED: supply what was missing — commit the unset `performance.*` budgets in `project.yaml` (`/project-settings`), or run the phases that did not run (raise `team.size`) — then re-run `/team-polish`. Do not treat the area as release-ready.
- If the report handed an optimisation list to `/dev-story`: implement those items there, then re-run `/team-polish` to measure the gain.
- Run `/gate-check` for a formal phase gate verdict before handing off to release.
