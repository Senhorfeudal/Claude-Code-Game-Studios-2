> **In-chat orchestration:** this spec describes a team skill, which is an
> orchestrator running in the user's current conversation. Specialist phases are
> run inline by reading `.claude/agents/<id>.md`; no `Agent` / `subagent`
> tool is used for the team or its specialists. Every decision and write approval
> is asked in this chat. See `.claude/docs/in-chat-teams.md`.

# Skill Test Spec: /team-audio

## Skill Summary

Orchestrates the audio team through a four-step pipeline: audio direction
(audio-director) → sound design + accessibility review as consecutive inline passes (sound-designer
+ accessibility-specialist) → technical implementation + engine validation in
inline sequence (technical-artist + primary engine specialist) → code integration
(gameplay-programmer). Phase 0 resolves `review_mode`, `automation` and
`team.size`, and the skill announces the active role set in one line before
Step 1 — at the default `team.size: individual` only sound-designer is run and
every other role is consulted through it. Reads relevant GDDs, the sound bible (if
present), and existing audio asset lists before starting inline passes. The orchestrator writes
their working artifacts to paths the orchestrator names, under the bounded write
exception; the orchestrator compiles the audio design document itself and writes it
to `design/audio/audio-[feature].md` only after asking via `AskUserQuestion`. Uses
`AskUserQuestion` at each step transition. Verdict is COMPLETE when the audio design
document is produced, BLOCKED when an unresolved dependency stops the pipeline.
Skips the engine specialist when no engine is configured and records
`Engine validation: NOT ASSESSED`.

---

## Static Assertions (Structural)

- [ ] Has required frontmatter fields: `name`, `description`, `argument-hint`, `user-invocable`, `allowed-tools`
- [ ] Has ≥2 step/phase headings
- [ ] Contains verdict keywords: COMPLETE, BLOCKED
- [ ] Contains "File Write Protocol" section
- [ ] Every write is made by the orchestrator after a "May I write" ask naming its path; implementation files (code, shaders, audio, assets) are listed as one set and asked for once before any is written
- [ ] Names a destination per role under `production/audio/[feature]/`: `direction.md` (audio-director), `sfx-spec.md` (sound-designer), `accessibility.md` (accessibility-specialist), `integration-plan.md` (technical-artist), `engine-notes.md` (engine specialist)
- [ ] Defines a phase gate as a decision point the pipeline itself lists, whatever the `automation` mode, and claims no director pass at phase gates
- [ ] The compiled audio design document is written by the orchestrator only after it asks via `AskUserQuestion` "May I write the audio design to `design/audio/audio-[feature].md`?" (`design/` is outside the "May I write" ask)
- [ ] Every pass ends with the pass output: path written, ≤5-bullet summary, BLOCKED/CONCERNS items one line each
- [ ] Has a next-step handoff at the end (references `/dev-story`, `/asset-audit`)
- [ ] Error Recovery Protocol section is present: verify a named artifact is on disk before treating a step as done, surface BLOCKED immediately, always produce a partial report, full procedure in `.claude/docs/error-recovery-protocol.md`
- [ ] `AskUserQuestion` is used at step transitions before proceeding (`collaborative` mode)
- [ ] Phase 0 resolves `review_mode`, `automation` and `team.size`, and requires a one-line active roles announcement before Step 1
- [ ] Step 2 explicitly runs sound-designer and accessibility-specialist as consecutive inline passes, and How to Run Inline lists `accessibility-specialist`
- [ ] Step 2 labels a gameplay-critical audio event with no visual cue or subtitle BLOCKING, and Step 3 waits for the user to resolve or accept it
- [ ] Step 3 explicitly runs technical-artist and engine specialist as consecutive inline passes (when engine is configured)
- [ ] Skill reads the sound bible at `design/audio/sound-bible.md` during context gathering if it exists; a sound bible still at `design/gdd/sound-bible.md` (the earlier location) is read, with a recommendation to move it
- [ ] Output document is saved to `design/audio/audio-[feature].md`

---

## Fixture Defaults

Every case's `project.yaml` sets `modes.rigor: minimal` and
`modes.automation: collaborative`, with no `project.local.yaml`, unless its own
Fixture says otherwise. Rules: `studio-tests/CLAUDE.md` §
Fixture defaults.

---

## Test Cases

### Case 1: Happy Path — All steps complete, audio design document saved

**Fixture:**
- Resolved config block: `team.size: studio`, `automation: collaborative`
- `engine.name` in `project.yaml` is Godot
- GDD for the target feature exists at `design/gdd/combat.md`
- Sound bible exists at `design/audio/sound-bible.md`
- Existing audio assets are listed in `assets/audio/`
- No accessibility gaps exist in the planned audio event list

**Input:** `/team-audio combat`

**Expected behavior:**
1. Before any pass, one line announces the active roles for `team.size: studio`
2. Context gathering: orchestrator reads `design/gdd/combat.md`, `design/audio/sound-bible.md`, and `assets/audio/` asset list before starting passes any role
3. Step 1: audio-director is run; defines sonic identity, emotional tone, adaptive music direction, mix targets, and adaptive audio rules for combat
4. `AskUserQuestion` presents audio direction; user approves before Step 2 begins
5. Step 2: sound-designer and accessibility-specialist are run as consecutive inline passes; sound-designer produces SFX specifications, audio event list with trigger conditions, and mixing groups; accessibility-specialist identifies critical gameplay audio events and specifies visual fallback and subtitle requirements
6. `AskUserQuestion` presents SFX spec and accessibility requirements; user approves before Step 3 begins
7. Step 3: technical-artist and `godot-specialist` (derived from `engine.name`) are run as consecutive inline passes; technical-artist designs bus structure, middleware integration, memory budgets, and streaming strategy; engine specialist validates that the integration approach is idiomatic for the pinned engine
8. `AskUserQuestion` presents technical plan; user approves before Step 4 begins
9. Step 4: gameplay-programmer is run; first returns the code and test files it will create or change, the orchestrator asks once for that set, and only after the yes it wires up audio events to gameplay triggers, implements adaptive music, sets up occlusion zones and writes unit tests for audio event triggers
10. For every step, the orchestrator checks that the path named in the pass's pass output exists before treating the step as done
11. Orchestrator compiles all outputs into a single audio design document itself (no inline pass is re-run to write it)
12. Orchestrator asks via `AskUserQuestion`: "May I write the audio design to `design/audio/audio-combat.md`?" and writes it only on approval
13. Summary output lists: audio event count, estimated asset count, implementation tasks, and any open questions
14. Verdict: COMPLETE

**Assertions:**
- [ ] Active roles line naming `team.size: studio` appears before the first pass runs
- [ ] Sound bible is read during context gathering (before Step 1) when it exists
- [ ] audio-director is run before sound-designer or accessibility-specialist
- [ ] `AskUserQuestion` appears after Step 1 output and before Step 2 launch
- [ ] sound-designer and accessibility-specialist inline passes run in order in Step 2
- [ ] technical-artist and `godot-specialist` inline passes run in order in Step 3
- [ ] gameplay-programmer is not launched until Step 3 `AskUserQuestion` is approved
- [ ] gameplay-programmer writes no code or test file before the one ask for its implementation set is answered yes
- [ ] Audio design document is written to `design/audio/audio-combat.md` (not another path), by the orchestrator, only after its `AskUserQuestion` approval
- [ ] Summary includes audio event count and estimated asset count
- [ ] Verdict is COMPLETE after document delivery

---

### Case 2: Accessibility Gap — Critical gameplay audio event has no visual fallback

**Fixture:**
- Resolved config block: `team.size: studio`, `automation: collaborative`
- GDD for the target feature exists
- Step 1 and Step 2 are in progress
- sound-designer's audio event list includes "EnemyNearbyAlert" — a spatial audio cue that warns the player an enemy is approaching from off-screen
- accessibility-specialist reviews the event list and finds "EnemyNearbyAlert" has no visual fallback (no on-screen indicator, no subtitle, no controller rumble specified)

**Input:** `/team-audio stealth` (Step 2 scenario)

**Expected behavior:**
1. Steps 1–2 proceed; accessibility-specialist and sound-designer are run as consecutive inline passes
2. accessibility-specialist returns its review with a BLOCKING concern: "`EnemyNearbyAlert` is a critical gameplay audio event (warns player of off-screen threat) with no visual fallback — hearing-impaired players cannot detect this threat."
3. Orchestrator writes the concern in conversation before presenting `AskUserQuestion`
4. `AskUserQuestion` presents the accessibility concern as a BLOCKING issue with options such as:
   - Add a visual indicator for EnemyNearbyAlert (e.g., directional arrow on HUD) and continue
   - Add controller haptic feedback as the fallback and continue
   - Stop here and resolve all accessibility gaps before proceeding to Step 3
5. Step 3 (technical-artist + engine specialist) is not launched until the user resolves or explicitly accepts the gap
6. If the user stops: a partial report of the Step 1–2 outputs is produced and the verdict is `BLOCKED — [reason]` naming the unresolved EnemyNearbyAlert gap
7. If the user accepts the gap and continues: the gap is listed among the open questions in the final summary

**Assertions:**
- [ ] Accessibility gap is labeled BLOCKING (not advisory) in the report
- [ ] The specific event name ("EnemyNearbyAlert") and the nature of the gap are stated
- [ ] `AskUserQuestion` surfaces the gap before Step 3 is launched
- [ ] At least one resolution option is offered (add visual fallback, add haptic fallback)
- [ ] Step 3 is not launched while the gap is unresolved without explicit user authorization
- [ ] If the user stops, the verdict is `BLOCKED — [reason]` naming the gap and the Step 1–2 outputs are kept in a partial report; if the user carries it forward, the final summary lists it as an open question

---

### Case 3: No Argument — Usage guidance or design doc inference

**Fixture:**
- Any project state

**Input:** `/team-audio` (no argument)

**Expected behavior:**
1. Skill detects no argument is provided
2. Outputs usage guidance: e.g., "Usage: `/team-audio [feature or area to design audio for] [--review full|lean|solo]` — specify the feature or area to design audio for (e.g., `combat`, `main menu`, `forest biome`, `boss encounter`)"
3. Skill exits without starting passes any roles

**Assertions:**
- [ ] Skill does NOT perform any roles when no argument is provided
- [ ] Usage message shows the full argument-hint — `/team-audio [feature or area to design audio for] [--review full|lean|solo]` — and argument examples
- [ ] Skill does NOT attempt to infer a feature from existing design docs without user direction
- [ ] No `AskUserQuestion` is used — output is direct guidance

---

### Case 4: Missing Sound Bible — Skill notes the gap and proceeds without it

**Fixture:**
- Resolved config block: `team.size: small`, `automation: collaborative`
- GDD for the target feature exists at `design/gdd/main-menu.md`
- No sound bible exists at `design/audio/sound-bible.md` or `design/gdd/sound-bible.md`
- Engine is configured; other context files are present

**Input:** `/team-audio main menu`

**Expected behavior:**
1. Context gathering: orchestrator reads `design/gdd/main-menu.md` and checks for `design/audio/sound-bible.md`
2. Sound bible is not found; orchestrator notes the gap in one line: "No sound bible at `design/audio/sound-bible.md`; audio direction starts from the GDDs alone"
3. Pipeline proceeds normally through all four steps without the sound bible as input
4. audio-director in Step 1 is informed that no sound bible exists and must establish sonic identity from the feature GDD alone
5. Next Steps recommends creating the sound bible and says who writes it: the `audio-director` role drafts `design/audio/sound-bible.md` from `.claude/docs/templates/sound-bible.md`, starting from this run's Step 1 direction, and asks before writing

**Assertions:**
- [ ] Orchestrator checks for the sound bible during context gathering (before Step 1)
- [ ] Missing sound bible is noted explicitly in conversation — not silently ignored
- [ ] Pipeline does NOT halt due to the missing sound bible
- [ ] audio-director is notified that no sound bible exists in its prompt context
- [ ] Next Steps recommends creating a sound bible and names its author — the `audio-director`, drafting from `.claude/docs/templates/sound-bible.md`
- [ ] The skill does not write `design/audio/sound-bible.md` itself in this run
- [ ] Verdict is still COMPLETE if all other steps succeed

---

### Case 5: Engine Not Configured — Engine specialist step skipped and recorded

**Fixture:**
- Resolved config block: `team.size: studio`, `automation: collaborative`
- `engine.name` is unset in `project.yaml`, and `.claude/docs/technical-preferences.md` has no Primary engine specialist (shows `[TO BE CONFIGURED]`)
- GDD for the target feature exists
- Sound bible may or may not exist

**Input:** `/team-audio boss encounter`

**Expected behavior:**
1. Steps 1–2 proceed normally (audio-director, sound-designer, accessibility-specialist)
2. Step 3: technical-artist pass runs normally; engine specialist perform is SKIPPED
3. The run output records: `Engine validation: NOT ASSESSED — no engine configured (engine.name unset in project.yaml)`
4. Step 4: gameplay-programmer still runs — the missing engine is not treated as a blocker
5. Verdict: `COMPLETE — engine validation NOT ASSESSED (no engine configured)` — the skip is graceful, not a blocker, and never a plain COMPLETE

**Assertions:**
- [ ] Engine specialist is NOT run when no engine is configured
- [ ] Skill does NOT error out due to the missing engine configuration
- [ ] The run output contains `Engine validation: NOT ASSESSED — no engine configured` with the `engine.name` reason — the skip is not silently omitted
- [ ] Engine integration is never described as validated or passed in this run
- [ ] technical-artist is still run in Step 3 (skip applies only to the engine specialist)
- [ ] gameplay-programmer still runs in Step 4
- [ ] Verdict is `COMPLETE — engine validation NOT ASSESSED (…)`, never a plain COMPLETE (engine not configured is a graceful case, not a blocker)

---

### Case 6: `review_mode` gates nothing — the same request at full, lean and solo

**Fixture:**
- `project.yaml`: `modes.review_mode: lean` (pinned: the runs below override or keep
  it), `team.size: studio` (pinned: so every step and role in the pipeline is active)
- `engine.name` is Godot; `design/gdd/combat.md` and `design/audio/sound-bible.md`
  exist; no accessibility gaps in the event list
- Run A: `/team-audio combat --review full`. Run B: `/team-audio combat` (resolves
  `lean`). Run C: `/team-audio combat --review solo`

**Expected behavior:**
1. All three runs open with the same active roles line for `team.size: studio`
2. All three run the same four steps with the same roles: audio-director, then
   sound-designer + accessibility-specialist, then technical-artist + `godot-specialist`,
   then gameplay-programmer. These are team members working the steps, not director gates
3. No run runs a CD-, TD-, PR- or AD-PHASE-GATE at any step: "no phase below runs
   CD-, TD-, PR- or AD-PHASE-GATE, at any `review_mode`"
4. The `AskUserQuestion` at each step transition, the single ask for the audio design
   document and the verdict are the same in all three

**Assertions:**
- [ ] No director gate (CD-, TD-, PR- or AD-PHASE-GATE) is run in Run A (`full`), Run B (`lean`) or Run C (`solo`)
- [ ] The active roles, the roles run per step and the number of step-transition asks are identical across the three runs
- [ ] `--review full` does not add a review step and `--review solo` does not remove one: only `team.size` changes who is run
- [ ] Each run writes `design/audio/audio-combat.md` only after its own ask and ends COMPLETE

---

## Protocol Compliance

- [ ] At the default `team.size: individual`, the run opens with `Active roles (team.size: individual): sound-designer.` and a `Not run this run:` line naming audio-director, accessibility-specialist, technical-artist, the engine specialist and gameplay-programmer, consulted through sound-designer — before any pass runs
- [ ] Context gathering (GDDs, sound bible, asset list) runs before any pass runs
- [ ] In `collaborative` mode, `AskUserQuestion` is used after every step output before the next step launches
- [ ] Inline sequence starting passes: Step 2 (sound-designer + accessibility-specialist) and Step 3 (technical-artist + engine specialist) issue all inline passes before waiting for results
- [ ] The orchestrator writes only to paths the orchestrator named; each after a "May I write" ask in this chat
- [ ] The orchestrator writes the compiled audio design document only after an explicit `AskUserQuestion` approval
- [ ] A step whose named artifact is missing on disk is treated as failed and the pass is resumed — not reported as done
- [ ] BLOCKED status from any role is surfaced immediately as "[PassName]: BLOCKED — [reason]" — not silently skipped
- [ ] A partial report is always produced when some passes complete and others block
- [ ] Audio design document path follows the pattern `design/audio/audio-[feature].md`
- [ ] Verdict is exactly COMPLETE (qualified `— engine validation NOT ASSESSED ([reason])` when that step was skipped) or BLOCKED — no other verdict values used
- [ ] Next Steps handoff references `/dev-story` and `/asset-audit`

---

## Coverage Notes

- The "Retry with narrower scope" and "Skip this role" resolution paths from the Error
  Recovery Protocol are not separately tested — they follow the same `AskUserQuestion`
  + partial-report pattern validated in Cases 2 and 5.
- Step 4 (gameplay-programmer) happy-path behavior is validated implicitly by Case 1.
  Failure modes for this step follow the standard Error Recovery Protocol.
- The accessibility-specialist's subtitle and caption requirements (beyond visual fallbacks)
  are validated implicitly by Case 1. Case 2 focuses on the more severe case where a
  critical gameplay event has no fallback at all.
- Engine specialist validation logic (idiomatic integration, version-specific changes) is
  tested only for the configured and unconfigured states. The specific content of the
  engine specialist's output is out of scope for this behavioral spec.
- `guided` and `autonomous` automation modes (auto-advance, `log_decision`) are not given
  dedicated cases; the individual-size collapse is covered by the Protocol Compliance
  announcement check rather than a full run.
