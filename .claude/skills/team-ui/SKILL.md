---
name: team-ui
description: "Orchestrate the UI team through the UX pipeline — authoring, visual design, implementation, review, polish. Uses /ux-design, /ux-review, studio templates."
argument-hint: "[UI feature description] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-ui/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
# Team UI

If no argument is provided, output usage guidance and exit without starting any pass or reading any design files:
> Usage: `/team-ui [UI feature description] [--review full|lean|solo]` — describe the screen or UI feature to build (e.g., `inventory screen`, `main menu`, `combat HUD`). Do not use `AskUserQuestion` here; output the guidance directly.

When this skill is invoked, orchestrate the UI team through a structured pipeline.

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

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,team.size`

Resolved above — use as-is; `--review` overrides `review_mode`. No block →
defaults in `.claude/docs/config-resolution.md`.

`review_mode` sets director-gate depth, and this pipeline has no director gate:
no phase below runs CD-, TD-, PR- or AD-PHASE-GATE, at any `review_mode`. Its
phase gates are the pipeline's own decision points (defined under `team.size`
below), and the roles that work at them are team members, not director gates.

`automation` drives the Decision Points note above. See the Decision Points note above and
`.claude/docs/automation-modes.md` for how each mode changes pipeline behavior.

**`team.size`**: which specialist roles are active (orthogonal to review_mode gate-depth and workflow docs).
- **`individual`** (default): `ui-programmer` + `ux-designer`. Other roles folded into these two, not performed separately.
- **`small`**: + `accessibility-specialist` + `art-director`.
- **`studio`**: + engine UI specialist + an adversarial review pass: Phase 4's reviewers are told "your job is not to confirm this matches the spec — find where it fails it", and the report says the pass ran.
A non-core role needed at `individual` is folded into the nearest active core role with an informational note. **"Phase gate" means any phase that ends in an `AskUserQuestion` decision point this pipeline itself lists** — a transition under Decision Points above, or a **Gate** step written into the pipeline below — **whatever the `automation` mode.** `guided` and `autonomous` change how a gate is passed (it auto-advances, or is recorded with `log_decision`), not whether it is one, so the gate stays a gate in every mode. A role restricted to "phase gates only" is performed at those points and no others. This active-set scoping applies throughout the pipeline below: any phase that names a role outside the active set is folded into the nearest core role rather than performed as a separate pass.

**Announce the active set before Step 1 — never let the collapse be silent.**
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
- **ux-designer** — User flows, wireframes, accessibility, input handling
- **ui-programmer** — UI framework, screens, widgets, data binding, implementation
- **art-director** — Visual style, layout polish, consistency with art bible
- **engine UI specialist** — Validates UI implementation patterns against engine-specific best practices (`specialists.ui` from `project.yaml`; if absent, the UI Specialist line of `## Engine Specialists` in `.claude/docs/technical-preferences.md`)
- **accessibility-specialist** — Audits accessibility compliance at Phase 4

> **`specialists.ui: null` means UNSET.** Treat it as absent and skip the engine
> UI specialist; never name `null` as a specialist. The v1.0 migration writes
> the whole `specialists` block whenever any one member is set, so `null` here is
> ordinary — and the config reader returns it as the non-empty string `"null"`.

**Templates used by this pipeline:**
- `ux-spec.md` — Standard screen/flow UX specification
- `hud-design.md` — HUD-specific UX specification
- `interaction-pattern-library.md` — Reusable interaction patterns
- `accessibility-requirements.md` — Committed accessibility tier and requirements

## How to Run Inline

Run each specialist pass inline in this chat. Read the role's
`.claude/agents/<id>.md` for its domain rules, then perform the work here. Never
call `Agent` / `subagent` for a team or for a specialist:
- **ux-designer** — User flows, wireframes, accessibility, input handling
- **ui-programmer** — UI framework, screens, widgets, data binding
- **art-director** — Visual style, layout polish, art bible consistency
- **[UI engine specialist]** — Engine-specific UI pattern validation (e.g., unity-ui-specialist, ue-umg-specialist, godot-specialist)
- **accessibility-specialist** — Accessibility compliance audit

**Use context once — do not re-read.** Read the shared inputs **once** in this
chat and keep only the sections each pass actually needs. Never re-open a whole
document you already hold; a role performed inline has the same context you do.

**Present each pass compactly.** In the chat, give the artifact path, ≤5
bullets of decisions, and any BLOCKED/CONCERNS items, one line each. Do not
restate the documents you read. Every write still follows the ask-first protocol
in this same chat (File Write Protocol below).

**Substitute a real path for `[path]`.** Working artifacts go under
`production/ui/[feature-name]/`, the slug Phase 1b's `design/ux/[feature-name].md`
uses. One file per role, so the inline Phase 4 reviews never share one:

| Phase / role | Writes to |
|---|---|
| 2 art-director | `production/ui/[feature-name]/visual-design.md` |
| 3 engine UI specialist | `production/ui/[feature-name]/engine-notes.md` |
| 3 ui-programmer | the code root — the files the one implementation ask lists (File Write Protocol), after an ask in this chat |
| 4 ux-designer, art-director, accessibility-specialist | `production/ui/[feature-name]/review-[role].md`, one each |

The UX spec itself (Phase 1b) and any pattern-library update are under `design/`,
after an ask in this chat: `/ux-design` or you ask before writing them.

> **Why no bounded exception is needed.** `CLAUDE.md` requires "May I write this
> to [filepath]?" before Write/Edit. Because the orchestrator performs every pass
> itself in the user's chat, that normal rule applies to every artifact: show the
> draft or file set, ask, wait for yes, then write. There is no per-pass write
> authority to hand out and no question for a parent to answer.

Run independent passes in sequence in this chat where the pipeline allows it (the Phase 4 review passes run in sequence here).

## Pipeline

### Phase 1a: Context Gathering

Before designing anything, read and synthesize. Read each GDD by section: find the
headings you need with the Grep tool (pattern `^#`, content mode) and Read those
ranges with offset and limit.
- `design/gdd/game-concept.md` — platform targets and intended audience (or
  `design/game-brief.md`, the one-page brief that replaces it at `rigor: minimal` —
  its "Who it's for" line gives the audience; it names no platform)
- `design/player-journey.md` — player's state and context when they reach this screen
- All GDD UI Requirements sections relevant to this feature
- `design/ux/interaction-patterns.md` — existing patterns to reuse (not reinvent)
- `design/accessibility-requirements.md` — committed accessibility tier (Basic, Standard, Comprehensive or Exemplary)

**Report the status of every document above before designing anything.** Phase 1a
reads five inputs, and any of them can be absent. List each as
present or ABSENT.

**`design/accessibility-requirements.md` is the one that must not pass silently.**
It carries the committed accessibility tier, which **Phase 3 implements against**
and **Phase 4 gates on** ("verify compliance against the committed accessibility
tier … flag any violations as blockers"). If the file is missing there is no tier,
so that gate has no criterion and would pass while checking nothing — a gate made
of an absent standard, the same shape as an assertion that can never fail. When it
is absent:
- Say so here, and carry it forward: **Phase 4 must report
  `Accessibility: NOT ASSESSED — no committed tier (design/accessibility-requirements.md absent)`
  and must NOT report the accessibility gate as passed.**
- The ux-designer states which tier they designed against as an explicit
  assumption, so a later reader can see it was assumed rather than committed.
- Recommend `/ux-design accessibility` to establish the tier.

Absence of a concept doc (neither `design/gdd/game-concept.md` nor
`design/game-brief.md`), `design/player-journey.md` or `design/ux/hud.md` is not
blocking, but name each missing one in the brief you
pass to the ux-designer so they design knowing what context they lack, rather
than inferring it.

**If `design/ux/interaction-patterns.md` does not exist**, surface the gap immediately:
> "interaction-patterns.md does not exist — no existing patterns to reuse."

Then use `AskUserQuestion` with options:
- (a) Run `/ux-design patterns` first to establish the pattern library, then continue
- (b) Proceed without the pattern library — ui-programmer will treat all patterns created as new and add each to a new `design/ux/interaction-patterns.md` at completion

Do NOT invent or assume patterns from the feature name or GDD alone. If the user chooses (b), explicitly instruct ui-programmer in Phase 3 to treat all patterns as new and document them in `design/ux/interaction-patterns.md` when implementation is complete. Note the pattern library status (created / absent / updated) in the final summary report.

Summarize the context in a brief for the ux-designer: what the player is doing, what they need, what constraints apply, and which existing patterns are relevant.

### Phase 1b: UX Spec Authoring

Invoke `/ux-design [feature name]` in this chat, or run the `ux-designer` pass inline to produce `design/ux/[feature-name].md` following the `ux-spec.md` template.

If designing the HUD, use the `hud-design.md` template instead of `ux-spec.md`.

> **Notes on special cases:**
> - For HUD design specifically, invoke `/ux-design` with `argument: hud` (e.g., `/ux-design hud`).
> - For the interaction pattern library, run `/ux-design patterns` once at project start and update it whenever new patterns are introduced during later phases.

Output: `design/ux/[feature-name].md` with all required spec sections filled.

### Phase 1c: UX Review

After the spec is complete, invoke `/ux-review design/ux/[feature-name].md`.

**Gate**: Do not proceed to Phase 2 until the verdict is APPROVED. If the verdict is NEEDS REVISION, the ux-designer must address the flagged issues in the same spec — it is kept and revised, never discarded — and re-run the review. The user may explicitly accept a NEEDS REVISION risk and proceed, but this must be a conscious decision — present the specific concerns via `AskUserQuestion` before asking whether to proceed.

A **NOT ASSESSED** verdict blocks the same way, and the user may override it the same way. Its fix is an input, not a revision: present the dimensions `/ux-review` could not assess and the missing input for each (e.g. `/ux-design accessibility` for an uncommitted tier). Re-running the review without that input returns the same verdict, so offer to produce the input first.

When the user proceeds past NEEDS REVISION or NOT ASSESSED, the final report records the override: the verdict, the concerns or unassessed dimensions left open, and that the user chose to proceed.

### Phase 2: Visual Design

Run the **art-director** pass inline:
- Review the full UX spec (flows, wireframes, interaction patterns, accessibility notes) — not just the wireframe images
- Apply visual treatment from the art bible: colors, typography, spacing, animation style
- Check that visual design preserves accessibility compliance: verify color contrast ratios, and confirm color is never the only indicator of state (shape, text, or icon must reinforce it)
- Specify all asset requirements needed from the art pipeline: icons at specified sizes, background textures, fonts, decorative elements — with precise dimensions and format requirements
- Ensure consistency with existing implemented UI screens
- Output: visual design spec with style notes and asset manifest

### Phase 3: Implementation

Before implementation begins, run the **engine UI specialist** pass inline (`specialists.ui` from `project.yaml`; if absent, the UI Specialist line of `## Engine Specialists` in `.claude/docs/technical-preferences.md`) to review the UX spec and visual design spec for engine-specific implementation guidance:
- Which engine UI framework should be used for this screen? (e.g., UI Toolkit vs UGUI in Unity, Control nodes vs CanvasLayer in Godot, UMG vs CommonUI in Unreal)
- Any engine-specific gotchas for the proposed layout or interaction patterns?
- Recommended widget/node structure for the engine?
- Output: engine UI implementation notes to hand off to ui-programmer before they begin

If no engine is configured, skip this step. **Record ``Engine validation: NOT ASSESSED — no engine configured (`engine.name` unset in `project.yaml`)`` in this run's output.** A skipped check that says nothing is indistinguishable from a check that passed; the reader cannot tell engine guidance was never sought.

Run the **ui-programmer** pass inline:
- Implement the UI following the UX spec and visual design spec
- **Use patterns from `design/ux/interaction-patterns.md`** — do not reinvent patterns that are already specified. If a pattern almost fits but needs modification, note the deviation and flag it for ux-designer review.
- **UI NEVER owns or modifies game state** — display only; emit events for all player actions
- All text through the localization system — no hardcoded player-facing strings
- Support both input methods (keyboard/mouse AND gamepad)
- Implement accessibility features per the committed tier in `design/accessibility-requirements.md`
- Wire up data binding to game state
- **If any new interaction pattern is created during implementation** (i.e., something not already in the pattern library), add it to `design/ux/interaction-patterns.md` before marking implementation complete
- Output: implemented UI feature

### Phase 4: Review (parallel)

Run these passes inline, in order:
- **ux-designer**: Verify implementation matches wireframes and interaction spec. Test keyboard-only and gamepad-only navigation. Check accessibility features function correctly.
- **art-director**: Verify visual consistency with art bible. Check at minimum and maximum supported resolutions.
- **accessibility-specialist**: Verify compliance against the committed accessibility tier documented in `design/accessibility-requirements.md`. Flag any violations as blockers. **If that file is absent there is no committed tier, so this gate has no criterion: report `Accessibility: NOT ASSESSED — no committed tier (design/accessibility-requirements.md absent)` and do NOT report the gate as passed**. Carry forward whatever tier Phase 1a recorded as assumed, and say plainly that it was assumed.

All three review streams must report before proceeding to Phase 5.

### Phase 5: Polish

- Address all review feedback
- Verify animations are skippable and respect the player's motion reduction preferences
- Confirm UI sounds trigger through the audio event system (no direct audio calls)
- Test at all supported resolutions and aspect ratios
- **Verify `design/ux/interaction-patterns.md` is up to date** — if any new patterns were introduced during this feature's implementation, confirm they have been added to the library
- **Confirm all HUD elements respect the visual budget** defined in `design/ux/hud.md` (element count, screen region allocations, maximum opacity values)

## Quick Reference — When to Use Which Skill

- `/ux-design` — Author a new UX spec for a screen, flow, or HUD from scratch
- `/ux-review` — Validate a completed UX spec before implementation
- `/team-ui [feature]` — Full pipeline from concept through polish (calls `/ux-design` and `/ux-review` internally)
- `/quick-design` — Small UI changes that don't need a full new UX spec

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

A summary report covering: UX spec status, UX review verdict, visual design status, implementation status, accessibility compliance, input method support, interaction pattern library update status, and any outstanding issues.

Verdict: **COMPLETE** — UI feature delivered through full pipeline (UX spec → visual → implementation → review → polish).

If the accessibility gate (no committed tier) or the engine validation (no engine
configured) was NOT ASSESSED, the verdict names each one — never a plain COMPLETE:

Verdict: **COMPLETE — [accessibility | engine validation] NOT ASSESSED ([reason])** — UI feature delivered; the named check could not run.

Verdict: **BLOCKED** — pipeline halted; surface the blocker and its phase before stopping.

## Next Steps

- Run `/ux-review` on the final spec if not yet approved.
- Run `/code-review` on the UI implementation before closing stories.
- Run `/team-polish` if visual or audio polish pass is needed.
