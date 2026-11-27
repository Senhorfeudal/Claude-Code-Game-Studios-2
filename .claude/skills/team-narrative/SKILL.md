---
name: team-narrative
description: "Orchestrate the narrative team — narrative-director, writer, world-builder, level-designer — for story, world lore, narrative-driven levels."
argument-hint: "[narrative content description] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-narrative/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
# Team Narrative

If no argument is provided, output usage guidance and exit without starting any pass:
> Usage: `/team-narrative [narrative content description] [--review full|lean|solo]` — describe the story content, scene, or narrative area to work on (e.g., `boss encounter cutscene`, `faction intro dialogue`, `tutorial narrative`). Do not use `AskUserQuestion` here; output the guidance directly.

When this skill is invoked with an argument, orchestrate the narrative team through a structured pipeline.

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

Phase 4's ND-CONSISTENCY is the exception in every mode: it is this pipeline's own
review, not an optional director gate, so `review_mode` never skips it (`team.size`
still decides who runs it — see Phase 4).

`automation` drives the Decision Points note above. See the Decision Points note above and
`.claude/docs/automation-modes.md` for how each mode changes pipeline behavior.

**`team.size`**: which specialist roles are active (orthogonal to review_mode gate-depth and workflow docs).
- **`individual`** (default): `writer` only; `narrative-director` invoked only on an explicit pillar conflict. Other roles folded into the writer, not performed separately.
- **`small`**: `narrative-director` + `writer`, plus `localization-lead` and `world-builder` when `review_mode` is `full` (at `lean` and `solo` they are consulted through the writer).
- **`studio`**: all six Team Composition roles, whatever the `review_mode` (the full pipeline as documented).
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
- **narrative-director** — Story arcs, character design, dialogue strategy, narrative vision
- **writer** — Dialogue writing, lore entries, item descriptions, in-game text
- **world-builder** — World rules, faction design, history, geography, environmental storytelling
- **art-director** — Character visual design, environmental visual storytelling, cutscene/cinematic tone
- **level-designer** — Level layouts that serve the narrative, pacing, environmental storytelling beats
- **localization-lead** — Localization readiness — flags non-localizable strings, cultural assumptions, and i18n gaps

## How to Run Inline

Run each specialist pass inline in this chat. Read the role's
`.claude/agents/<id>.md` for its domain rules, then perform the work here. Never
call `Agent` / `subagent` for a team or for a specialist:
- **narrative-director** — Story arcs, character design, narrative vision
- **writer** — Dialogue writing, lore entries, in-game text
- **world-builder** — World rules, faction design, history, geography
- **art-director** — Character visual profiles, environmental visual storytelling, cinematic tone
- **level-designer** — Level layouts that serve the narrative, pacing
- **localization-lead** — Localization readiness — flags non-localizable strings, cultural assumptions, and i18n gaps

**Read the canon first.** Before Phase 1, read the shared inputs that exist — the narrative bible or tone guide, the character and faction files under `design/narrative/`, and the world rules. Never invent canon: if none exists, say so and ask the user before any drafting.

**Use context once — do not re-read.** Read the shared inputs **once** in this
chat and keep only the sections each pass actually needs. Never re-open a whole
document you already hold; a role performed inline has the same context you do.

**Present each pass compactly.** In the chat, give the artifact path, ≤5
bullets of decisions, and any BLOCKED/CONCERNS items, one line each. Do not
restate the documents you read. Every write still follows the ask-first protocol
in this same chat (File Write Protocol below).

**Substitute a real path for `[path]`.** You write drafts under
`production/narrative/[content-slug]/` — after an ask in this chat. The
finished documents belong in `design/narrative/`, which the exception does **not**
cover, so **you** write those after one approval (see "Write the finals"):

| Role | Drafts to (`[path]`) | Final document (you write it) |
|---|---|---|
| narrative-director | `production/narrative/[content-slug]/brief.md` | `design/narrative/[content-slug]-brief.md` |
| world-builder | `production/narrative/[content-slug]/lore-[topic].md` | `design/narrative/lore/[topic].md` |
| writer | `production/narrative/[content-slug]/dialogue-[scene-slug].md` | `design/narrative/dialogue/[scene-slug].md` |
| art-director | `production/narrative/[content-slug]/visual-direction.md` | `design/narrative/[content-slug]-visual-direction.md` |
| level-designer | `production/narrative/[content-slug]/level-integration.md` | `design/narrative/[content-slug]-level-integration.md` |
| localization-lead | `production/narrative/[content-slug]/i18n-review.md` | stays in `production/` — a review, not a design document |

> **The final destination is not a free choice.** `design/narrative/` is read by
> `/asset-spec`, `/design-review`, `/localize`, `/onboard`,
> `/project-stage-detect`, `/team-level` and the `cd-narrative` director gate.
> An artifact written anywhere else is invisible to all seven.
>
> The `[path]` contract above has a precondition: the path is one *you* named. A
> skill that states the contract but names no concrete destination leaves every
> run to invent one, which defeats it. `/team-qa` Phase 4 carries the same
> requirement for the same reason.

> **Why no bounded exception is needed.** `CLAUDE.md` requires "May I write this
> to [filepath]?" before Write/Edit. Because the orchestrator performs every pass
> itself in the user's chat, that normal rule applies to every artifact: show the
> draft or file set, ask, wait for yes, then write. There is no per-pass write
> authority to hand out and no question for a parent to answer.

Run independent passes in sequence in this chat where the pipeline allows it (the Phase 2 passes run in sequence here).

## Pipeline

### Phase 1: Narrative Direction
Run the **narrative-director** pass inline:
- Define the narrative purpose of this content: what story beat does it serve?
- Identify characters involved, their motivations, and how this fits the overall arc
- Set the emotional tone and pacing targets
- Specify any lore dependencies or new lore this introduces
- Output: narrative brief with story requirements

### Phase 2: World Foundation (parallel)
Run these passes inline, one after another, in this chat:
- **world-builder**: Create or update lore entries for factions, locations, and history relevant to this content. Cross-reference against existing lore for contradictions. Set canon level for new entries.
- **writer**: Draft character dialogue using voice profiles. Ensure all lines are under 120 characters, use named placeholders for variables, and are localization-ready.
- **art-director**: Define character visual design direction for key characters appearing in this content (silhouette, visual archetype, distinguishing features). Specify environmental visual storytelling elements for each key space (prop composition, lighting notes, spatial arrangement). Define tone palette and cinematic direction for any cutscenes or scripted sequences.

**Phase gate:** collect all three Phase 2 outputs, then apply the Decision Points
rule before starting Phase 3 — present the lore, dialogue, and visual direction
summaries and capture approval via `AskUserQuestion` in `collaborative` mode
(auto-advance in `guided` unless a result is BLOCKED; `log_decision` in
`autonomous`).

### Phase 3: Level Narrative Integration
Run the **level-designer** pass inline:
- Review the narrative brief and lore foundation
- Design environmental storytelling elements in the level
- Place narrative triggers, dialogue zones, and discovery points
- Ensure pacing serves both gameplay and story

### Phase 4: Review and Consistency
Run the `narrative-director` pass inline using gate **ND-CONSISTENCY**
(`.claude/docs/director-gates/nd-consistency.md`). This phase runs in every review
mode — it is this pipeline's own review, not an optional director gate. Pass the
context that gate lists (the Phase 2–3 draft paths, the narrative bible or tone
guide, the world rules, the affected character and faction profiles) — named
here, so do not read the gate file in this session — and add:
- Confirm narrative pacing aligns with level design
- Check that all mysteries have documented "true answers"

Act on the verdict: **APPROVE** → Phase 5. **CONCERNS** → show the listed
inconsistencies and ask via `AskUserQuestion` whether to revise them (re-run
the pass for the role that owns each) or accept them. **REJECT** → do not start Phase 5; the
contradictions are fixed first. **NOT ASSESSED [missing input]** → name the
missing input, then supply it and re-run the gate, or carry
`ND-CONSISTENCY: NOT ASSESSED — [input]` into the report's consistency review
results; it is never read as APPROVE (`.claude/docs/director-gates.md`).

**At `team.size: individual`** narrative-director is not in the active set, so the
gate is not performed. The writer checks the drafts against the same criteria, and
the output says so by name: "ND-CONSISTENCY not run — narrative-director is not
active at `team.size: individual`; consistency self-checked by writer." A
self-check is not the gate's verdict, and the report must not present it as one.

### Phase 5: Polish (parallel)
Run these passes inline, one after another, in this chat:
- **writer**: Final self-review — verify no line exceeds dialogue box constraints, all text uses string keys (not raw strings), placeholder variable names are consistent
- **localization-lead**: Validate i18n compliance — check string key naming conventions, flag any strings with hardcoded formatting that won't survive translation, verify character limit headroom for languages that expand (German/Finnish typically +30%), confirm no cultural assumptions in text that would need locale-specific variants
- **world-builder**: Finalize canon levels for all new lore entries

### Write the finals
You hold every draft. List the final documents from the table above, then ask once
via `AskUserQuestion` — "May I write these [N] narrative documents to
`design/narrative/`?" — and write them on approval. The drafts under
`production/narrative/[content-slug]/` stay as the working record.

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

A summary report covering: narrative brief status, lore entries created/updated, dialogue lines written, level narrative integration points, consistency review results, and any unresolved contradictions — including any localization issue the user chose to leave unfixed, by string key.

Verdict: **COMPLETE** — narrative content delivered.

If ND-CONSISTENCY answered NOT ASSESSED and that was carried into the report
(Phase 4), the verdict says so — never a plain COMPLETE:

Verdict: **COMPLETE — consistency NOT ASSESSED ([input])** — narrative content delivered; the consistency review could not run for want of [input].

If the pipeline stops because a dependency is unresolved (e.g., lore contradiction or missing prerequisite not resolved by the user):

Verdict: **BLOCKED** — [reason]

## Next Steps

- Run `/design-review` on the narrative documents for consistency validation.
- Run `/localize extract` to extract new strings for translation after dialogue is finalized.
- Run `/dev-story` to implement dialogue triggers and narrative events in-engine.
