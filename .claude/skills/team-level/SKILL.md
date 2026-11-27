---
name: team-level
description: "Orchestrate the level team — level-designer, narrative-director, world-builder, art-director, systems-designer, qa-tester — for complete area creation."
argument-hint: "[level name or area to design] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-level/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

# Team Level

If no argument is provided, output usage guidance and exit without starting any pass or reading any design files:
> Usage: `/team-level [level name or area to design] [--review full|lean|solo]` — specify the level or area to design (e.g., `forest temple`, `tutorial village`, `final boss arena`). Do not use `AskUserQuestion` here; output the guidance directly.

When this skill is invoked:

**Decision Points:** At each step transition, use `AskUserQuestion` to present
the user with the specialist pass's proposals as selectable options. Write the pass's
full analysis in conversation, then capture the decision with concise labels.
In `collaborative` mode, the user must approve before moving to the next step.
In `guided` mode the pipeline advances automatically unless a step is BLOCKED;
in `autonomous` mode it runs end to end, recording each step outcome via
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
- **`individual`** (default): `level-designer` only. Other roles folded into the level-designer, not performed separately.
- **`small`**: + `systems-designer` + `art-director` + `qa-tester`.
- **`studio`**: + `narrative-director` + `world-builder` + `accessibility-specialist` (the full pipeline as documented).
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

1. **Read the argument** for the target level or area (e.g., `tutorial`,
   `forest dungeon`, `hub town`, `final boss arena`).

2. **Gather context** (read each design doc by section: find the headings you need
   with the Grep tool with pattern `^#` in content mode, and Read those ranges
   with offset and limit):
   - Read the game concept at `design/gdd/game-concept.md` — or `design/game-brief.md`,
     the one-page brief that replaces it at `rigor: minimal` — if either exists
   - Read game pillars at `design/gdd/game-pillars.md`
   - Read existing level docs in `design/levels/`
   - Read relevant narrative docs in `design/narrative/`
   - Read world-building docs for the area's region/faction

## How to Run Inline

Run each specialist pass inline in this chat. Read the role's
`.claude/agents/<id>.md` for its domain rules, then perform the work here. Never
call `Agent` / `subagent` for a team or for a specialist:
- **narrative-director** — Narrative purpose, characters, emotional arc
- **world-builder** — Lore context, environmental storytelling, world rules
- **level-designer** — Spatial layout, pacing, encounters, navigation
- **systems-designer** — Enemy compositions, loot tables, difficulty balance
- **art-director** — Visual theme, color palette, lighting, asset requirements
- **accessibility-specialist** — Navigation clarity, colorblind safety, cognitive load
- **qa-tester** — Test cases, boundary testing, playtest checklist

**Use context once — do not re-read.** Read the shared inputs **once** in this
chat and keep only the sections each pass actually needs. Never re-open a whole
document you already hold; a role performed inline has the same context you do.

**Present each pass compactly.** In the chat, give the artifact path, ≤5
bullets of decisions, and any BLOCKED/CONCERNS items, one line each. Do not
restate the documents you read. Every write still follows the ask-first protocol
in this same chat (File Write Protocol below).

**Substitute a real path for `[path]`.** Working artifacts go under
`production/levels/[level-name]/`, slugged as in the "Save to" step below. One
file per role, so the inline steps never share one:

| Step / role | Writes to |
|---|---|
| 1 narrative-director | `production/levels/[level-name]/narrative.md` |
| 1 world-builder | `production/levels/[level-name]/lore.md` |
| 1 art-director | `production/levels/[level-name]/visual-direction.md` |
| 2 level-designer | `production/levels/[level-name]/layout.md` |
| 3 systems-designer | `production/levels/[level-name]/systems.md` |
| 4 art-director | `production/levels/[level-name]/production-concepts.md` |
| 4 accessibility-specialist | `production/levels/[level-name]/accessibility.md` |
| 5 qa-tester | `production/qa/test-cases/[level-name]-cases.md` — test cases, edge cases, playtest checklist, acceptance criteria |

These are working drafts; the durable record is the level design document you
compile from them (`design/levels/[level-name].md`).

> **Why no bounded exception is needed.** `CLAUDE.md` requires "May I write this
> to [filepath]?" before Write/Edit. Because the orchestrator performs every pass
> itself in the user's chat, that normal rule applies to every artifact: show the
> draft or file set, ask, wait for yes, then write. There is no per-pass write
> authority to hand out and no question for a parent to answer.

3. **Orchestrate the level design team** in sequence:

### Step 1: Narrative + Visual Direction (narrative-director + world-builder + art-director, parallel)

Run the three passes inline, one after another, in this chat.

Run the `narrative-director` pass inline to:
- Define the narrative purpose of this area (what story beats happen here?)
- Identify key characters, dialogue triggers, and lore elements
- Specify emotional arc (how should the player feel entering, during, leaving?)

Run the `world-builder` pass inline to:
- Provide lore context for the area (history, faction presence, ecology)
- Define environmental storytelling opportunities
- Specify any world rules that affect gameplay in this area

Run the `art-director` pass inline to:
- Establish visual theme targets for this area — these are INPUTS to layout, not outputs of it
- Define the color temperature and lighting mood for this area (how does it differ from adjacent areas?)
- Specify shape language direction (angular fortress? organic cave? decayed grandeur?)
- Name the primary visual landmarks that will orient the player
- Read `design/art/art-bible.md` if it exists — anchor all direction in the established art bible. Read it by section: find the headings you need with the Grep tool (pattern `^#`, content mode) and Read those ranges with offset and limit.

**The art-director's visual targets from Step 1 must be passed to the level-designer in Step 2** as explicit constraints. Layout decisions happen within the visual direction, not before it.

**Gate**: Use `AskUserQuestion` to present all three Step 1 outputs (narrative brief, lore foundation, visual direction targets) and confirm before proceeding to Step 2.

### Step 2: Layout and Encounter Design (level-designer)
Run the `level-designer` pass inline with the full Step 1 output as context:
- Narrative brief (from narrative-director)
- Lore foundation (from world-builder)
- **Visual direction targets (from art-director)** — layout must work within these targets, not contradict them

The level-designer should:
- Design the spatial layout (critical path, optional paths, secrets) — ensuring primary routes align with the visual landmark targets from Step 1
- Define pacing curve (tension peaks, rest areas, exploration zones) — coordinated with the emotional arc from narrative-director
- Place encounters with difficulty progression
- Design environmental puzzles or navigation challenges
- Define points of interest and landmarks for wayfinding — these must match the visual landmarks the art-director specified
- Specify entry/exit points and connections to adjacent areas

**Adjacent area dependency check**: After the layout is produced, check `design/levels/` for each adjacent area referenced by the level-designer. If any referenced area's `.md` file does not exist, surface the gap:
> "Level references [area-name] as an adjacent area but `design/levels/[area-name].md` does not exist."

Use `AskUserQuestion` with options:
- (a) Proceed with a placeholder reference — mark the connection as UNRESOLVED in the level doc and list it in the open cross-level dependencies section of the summary report
- (b) Pause and run `/team-level [area-name]` first to establish that area

Do NOT invent content for the missing adjacent area.

**Gate**: Use `AskUserQuestion` to present Step 2 layout (including any unresolved adjacent area dependencies) and confirm before proceeding to Step 3.

### Step 3: Systems Integration (systems-designer)
Run the `systems-designer` pass inline to:
- Specify enemy compositions and encounter formulas
- Define loot tables and reward placement
- Balance difficulty relative to expected player level/gear
- Design any area-specific mechanics or environmental hazards
- Specify resource distribution (health pickups, save points, shops)

**Gate**: Use `AskUserQuestion` to present Step 3 outputs and confirm before proceeding to Step 4.

### Step 4: Production Concepts + Accessibility (art-director + accessibility-specialist, parallel)

**Note**: The art-director's directional pass (visual theme, color targets, mood) happened in Step 1. This pass is location-specific production concepts — given the finalized layout, what does each specific space look like?

Run the `art-director` pass inline with the finalized layout from Step 2:
- Produce location-specific concept specs for key spaces (entrance, key encounter zones, landmarks, exits)
- Specify which art assets are unique to this area vs. shared from the global pool
- Define sight-line and lighting setups per key space (these are now layout-informed, not directional)
- Specify VFX needs that are specific to this area's layout (weather volumes, particles, atmospheric effects)
- Flag any locations where the layout creates visual direction conflicts with the Step 1 targets — surface these as production risks

Run the `accessibility-specialist` pass inline to:
- Review the level layout for navigation clarity (can players orient themselves without relying on color alone?)
- Check that critical path signposting uses shape/icon/sound cues in addition to color
- Review any puzzle mechanics for cognitive load — flag anything that requires holding more than 3 simultaneous states
- Check that key gameplay areas have sufficient contrast for colorblind players
- Output: accessibility concerns list with severity (BLOCKING / RECOMMENDED / NICE TO HAVE)

Complete both passes before proceeding.

**Gate**: Use `AskUserQuestion` to present both Step 4 results. If the accessibility-specialist returned any BLOCKING concerns, highlight them prominently and offer:
- (a) Return to level-designer and art-director to redesign the flagged elements before Step 5
- (b) Document as a known accessibility gap and proceed to Step 5 with the concern explicitly logged in the final report

Do NOT proceed to Step 5 without the user acknowledging any BLOCKING accessibility concerns.

### Step 5: QA Planning (qa-tester)
Run the `qa-tester` pass inline to:
- Write test cases for the critical path
- Identify boundary and edge cases (sequence breaks, softlocks)
- Create a playtest checklist for the area
- Define acceptance criteria for level completion

4. **Compile the level design document** combining all team outputs into the
   level design template format.

The orchestrator already holds every pass's output — **compile the document
itself; do not re-run the `level-designer` pass and re-send all outputs verbatim.** That
second pass pays a fresh overhead plus a full re-transmission of context
the orchestrator already has, to move text it is already holding. After compiling
into the level-design template format, ask the user directly via
`AskUserQuestion`: "May I write the compiled level design to
`design/levels/[level-name].md`?" On approval, write it.

5. **Save to** `design/levels/[level-name].md` after that approval.
   `[level-name]` is the argument as a slug — lowercase, spaces → hyphens
   (`forest dungeon` → `forest-dungeon.md`) — and `[area-name]` in the adjacent
   area check is slugged the same way.

6. **Output a summary** with: area overview, encounter count, estimated asset
   list, narrative beats, any cross-team dependencies or open questions, open
   cross-level dependencies (adjacent areas referenced but not yet designed, each
   marked UNRESOLVED), and accessibility concerns with their resolution status.

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

Verdict: **COMPLETE** — level design document produced and all team outputs compiled.
Verdict: **BLOCKED** — one or more passes blocked, or a role was skipped (`.claude/docs/error-recovery-protocol.md` step 5); partial report produced with unresolved items listed.

## Next Steps

- Run `/design-review design/levels/[level-name].md` to validate the completed level design doc.
- Run `/dev-story` to implement level content once the design is approved.
- Run `/qa-plan` to generate a QA test plan for this level.

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
