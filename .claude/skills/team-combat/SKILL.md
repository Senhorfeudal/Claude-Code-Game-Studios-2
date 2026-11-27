---
name: team-combat
description: "Orchestrate the combat team — game-designer, gameplay-programmer, ai-programmer, technical-artist, sound-designer, qa-tester — design through implement and validate."
argument-hint: "[combat feature description] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-combat/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
# Team Combat

**Argument check:** If no combat feature description is provided, output:
> "Usage: `/team-combat [combat feature description] [--review full|lean|solo]` — Provide a description of the combat feature to design and implement (e.g., `melee parry system`, `ranged weapon spread`)."
Then stop immediately without starting any pass or reading any files.

When this skill is invoked with a valid argument, orchestrate the combat team through a structured pipeline.

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

`workflow` sizes the Phase 1 design document the way `/design-system` does:
`## Summary` plus all 8 sections at `full`; at `standard`, Overview, Detailed
Design, Edge Cases, Dependencies and Acceptance Criteria, plus Formulas whenever
the mechanic defines numeric rules (a combat mechanic almost always does); at
`minimal` the game brief is the design record and the GDD is optional — draft
those five sections and tell the user it is optional at this workflow level.

**`team.size`**: which specialist roles are active (orthogonal to review_mode gate-depth and workflow docs).
- **`individual`** (default): `gameplay-programmer` runs the pipeline; escalate `ai-programmer` only if the feature flags AI work. Other Team Composition roles are folded into the gameplay-programmer, not performed separately.
- **`small`**: the full Team Composition pipeline below, as documented.
- **`studio`**: full pipeline + engine sub-specialists + an adversarial review pass. *Engine sub-specialists*: the primary engine specialist's prompt says it may hand parts of its review to the sub-specialists its `tools:` grant names (for example `ue-gas-specialist` for abilities); below `studio` it answers alone. *Adversarial review pass*: Phase 5's qa-tester is told "your job is not to confirm this works — find how it breaks", and the report says the pass ran.
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
- **game-designer** — Design the mechanic, define formulas and edge cases
- **gameplay-programmer** — Implement the core gameplay code
- **ai-programmer** — Implement NPC/enemy AI behavior for the feature
- **technical-artist** — Create VFX, shader effects, and visual feedback
- **sound-designer** — Define audio events, impact sounds, and ambient combat audio
- **engine specialist** (primary) — Validate architecture and implementation patterns are idiomatic for the engine (the primary specialist is `<engine>-specialist` from `engine.name` — Godot→`godot-specialist`, Unity→`unity-specialist`, Unreal→`unreal-specialist`, Web→`lead-programmer`; fall back to the Primary line of `## Engine Specialists` in `technical-preferences.md`)
- **qa-tester** — Write test cases and validate the implementation

## How to Run Inline

Run each specialist pass inline in this chat. Read the role's
`.claude/agents/<id>.md` for its domain rules, then perform the work here. Never
call `Agent` / `subagent` for a team or for a specialist:
- **game-designer** — Design the mechanic, define formulas and edge cases
- **gameplay-programmer** — Implement the core gameplay code
- **ai-programmer** — Implement NPC/enemy AI behavior
- **technical-artist** — Create VFX, shader effects, visual feedback
- **sound-designer** — Define audio events, impact sounds, ambient audio
- **[primary engine specialist]** — Engine idiom validation for architecture and implementation
- **qa-tester** — Write test cases and validate implementation

**Use context once — do not re-read.** Read the shared inputs **once** in this
chat and keep only the sections each pass actually needs. Never re-open a whole
document you already hold; a role performed inline has the same context you do.

**Present each pass compactly.** In the chat, give the artifact path, ≤5
bullets of decisions, and any BLOCKED/CONCERNS items, one line each. Do not
restate the documents you read. Every write still follows the ask-first protocol
in this same chat (File Write Protocol below).

**Substitute a real path for `[path]`.** Every phase that produces an artifact
names one; most are fixed by the skill that already reads them:

| Phase / role | Writes to | Destination fixed by |
|---|---|---|
| 1 game-designer (draft) | `production/combat/[feature]-gdd-draft.md` | this skill — you write the final `design/gdd/[feature].md` (Phase 1) |
| 2 gameplay-programmer | `docs/architecture/[feature]-sketch.md` | see note below |
| 2 engine specialist | `docs/architecture/[feature]-engine-notes.md` | see note below |
| 3 gameplay-programmer, ai-programmer, technical-artist | the code root and `assets/` — the files the Phase 3 approval lists | after an ask in this chat: asked once for the set (File Write Protocol) |
| 3 sound-designer | `production/combat/[feature]-audio-events.md` | this skill |
| 5 qa-tester (test cases) | `production/qa/test-cases/[feature]-cases.md` | `/team-qa` Phase 4 |
| 5 qa-tester (bugs) | `production/qa/bugs/BUG-[NNNN].md` | `/team-qa` Phase 5 |

Phase 6 is a spoken status report, not an artifact — no path, and none needed.

> **Every phase above names a concrete destination, deliberately.** The Error
> Recovery Protocol below says "a named artifact that is not on disk is a failed
> phase" — a check that cannot run when no path was named.
>
> **The two `docs/architecture/` entries are a judgement call, not a convention.**
> That directory holds ADRs (`adr-NNNN-*.md`); a sketch is a precursor to one, not
> one itself, and **nothing in the repo reads either file**. Say so when
> reporting, so the sketch is understood as a record rather than an input to a
> later gate.

> **Why no bounded exception is needed.** `CLAUDE.md` requires "May I write this
> to [filepath]?" before Write/Edit. Because the orchestrator performs every pass
> itself in the user's chat, that normal rule applies to every artifact: show the
> draft or file set, ask, wait for yes, then write. There is no per-pass write
> authority to hand out and no question for a parent to answer.

Run independent passes in sequence in this chat where the pipeline allows it (the Phase 3 passes run in sequence here).

## Pipeline

### Phase 1: Design
Run the **game-designer** pass inline:
- Create or update the design document for `design/gdd/[feature].md` from `.claude/docs/templates/game-design-document.md`, with `## Summary` and the sections `workflow` requires (Phase 0) — at `full`: mechanic overview, player fantasy, detailed rules, formulas with variable definitions, edge cases, dependencies, tuning knobs with safe ranges, and acceptance criteria
- Output: completed design document, drafted to `production/combat/[feature]-gdd-draft.md`

`design/` is a durable design record, not a working artifact, so the
game-designer pass drafts and **you** write the GDD — the pattern `/team-level` and
`/team-narrative` use. At the Phase 1 decision point, present the draft and ask
via `AskUserQuestion`: "May I write the design document to
`design/gdd/[feature].md`?" Write it on approval; nothing is written under
`design/` before that answer.

### Phase 2: Architecture
Run the **gameplay-programmer** pass inline (with **ai-programmer** if AI is involved):
- Review the design document, reading it by section: find the headings you need with the Grep tool (pattern `^#`, content mode) and Read those ranges with offset and limit
- Design the code architecture: class structure, interfaces, data flow
- Identify integration points with existing systems
- Output: architecture sketch with file list and interface definitions

Then run the **primary engine specialist** pass inline to validate the proposed architecture:
- Is the class/node/component structure idiomatic for the pinned engine? (e.g., Godot node hierarchy, Unity MonoBehaviour vs DOTS, Unreal Actor/Component design)
- Are there engine-native systems that should be used instead of custom implementations?
- Any proposed APIs that are deprecated or changed in the pinned engine version?
- Output: engine architecture notes — incorporate into the architecture before Phase 3 begins

If no engine is configured, skip the specialist pass. **Record ``Engine validation: NOT ASSESSED — no engine configured (`engine.name` unset in `project.yaml`)`` in this run's output.** A skipped check that says nothing is indistinguishable from a check that passed.

Use `AskUserQuestion`:
- Prompt: "Architecture sketch complete. Approve to proceed with parallel implementation."
- Options:
  - `[A] Proceed — run implementation passes (gameplay-programmer, ai-programmer, technical-artist, sound-designer)`
  - `[B] Revise the architecture first — I'll describe what needs to change`
  - `[C] Stop here — I'll continue later`

Only run implementation passes if the user selects [A]. (In `guided`/`autonomous`
mode this architecture gate is a normal phase transition — proceed to
implementation unless the architecture sketch came back BLOCKED, recording the
decision via `log_decision` in autonomous mode. The gate is not a release-
critical or irreversible decision, so it follows the standard pipeline rule.)

### Phase 3: Implementation (parallel where possible)
Run these passes inline, in order:
- **gameplay-programmer**: Implement core combat mechanic code
- **ai-programmer**: Implement AI behaviors (if the feature involves NPC reactions)
- **technical-artist**: Create VFX and shader effects
- **sound-designer**: Define audio event list and mixing notes, drafted to `production/combat/[feature]-audio-events.md`

The code, VFX and shader work needs a write approval: list the files to
create or change, ask once for the whole set, and write only after a yes
(File Write Protocol).

### Phase 4: Integration
- Wire together gameplay code, AI, VFX, and audio
- Ensure all tuning knobs are exposed and data-driven
- Verify the feature works with existing combat systems

**Gate**: Use `AskUserQuestion` to present the integration result and confirm before proceeding to Phase 5.

### Phase 5: Validation
Run the **qa-tester** pass inline:
- Write test cases from the acceptance criteria
- Test all edge cases documented in the design
- Verify performance impact is within budget
- File bug reports for any issues found

### Phase 6: Sign-off
- Collect results from all team members
- Report feature status: COMPLETE / NEEDS WORK / BLOCKED
- List any outstanding issues and their assigned owners

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

A summary report covering: design completion status, implementation status per role, test results, and any open issues.

Verdict: **COMPLETE** — combat feature designed, implemented, and validated.

If the engine validation was skipped (Phase 2, no engine configured), the verdict
says so — never a plain COMPLETE:

Verdict: **COMPLETE — engine validation NOT ASSESSED ([reason])** — combat feature designed, implemented, and validated; the engine specialist never reviewed the architecture.

Verdict: **NEEDS WORK** — every phase ran, but Phase 5 validation left failures or open bugs unresolved; the report lists each with its owner.

Verdict: **BLOCKED** — one or more phases could not complete, or a role was skipped (`.claude/docs/error-recovery-protocol.md` step 5); partial report produced with unresolved items listed.

## Next Steps

- Run `/code-review` on the implemented combat code before closing stories.
- Run `/balance-check` to validate combat formulas and tuning values.
- Run `/team-polish` if VFX, audio, or performance polish is needed.
