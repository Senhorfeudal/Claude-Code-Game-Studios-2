---
name: team-release
description: "Orchestrate the release team — release-manager, qa-lead, devops-engineer, producer — to execute a release from candidate to deployment."
argument-hint: "[version number or 'next'] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-release/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
# Team Release

**Argument check:** If no version number is provided:
1. Read `production/session-state/active.md` and the most recent file in `production/milestones/` (if they exist) to infer the target version.
2. If a version is found: report "No version argument provided — inferred [version] from milestone data. Proceeding." Then confirm with `AskUserQuestion`: "Releasing [version]. Is this correct?"
3. If no version is discoverable: use `AskUserQuestion` to ask "What version number should be released? (e.g., v1.0.0)" and wait for user input before proceeding. Do not default to a hardcoded version string.

When this skill is invoked, orchestrate the release team through a structured pipeline.

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

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,team.size,workflow,project.stage`

Resolved above — use as-is; `--review` overrides `review_mode`. No block →
defaults in `.claude/docs/config-resolution.md`.

**Stage check — before any pass runs.** This skill ships a release, and
`/gate-check release` is the readiness gate that must pass first; only its PASS
sets `project.stage` to `Release`. If the resolved `project.stage` is anything
else — `Polish`, an earlier stage, or not set — stop before Phase 1 and run
nothing:

> "The release readiness gate has not passed (project.stage: [stage]) — run
> `/gate-check release` first."

Then ask with `AskUserQuestion`, in every `automation` mode — an override is never
taken on the user's behalf: `[A] Stop — I'll run /gate-check release (recommended)`
/ `[B] Proceed anyway — override the stage check`. On `[A]`, end the run: Verdict
**BLOCKED** — release gate not passed. On `[B]`, ask why with the question widget (free-text answer; plain text only if no widget tool exists), then record
the override as `Stage override: project.stage was [stage] — release gate not
passed; the user chose to proceed: [reason]` in the Phase 1 brief, in the go/no-go
record (`go-no-go-[version].md`) and in the final report. An override never
changes the stage itself.

`review_mode` sets director-gate depth, and this pipeline has no director gate:
no phase below runs CD-, TD-, PR- or AD-PHASE-GATE, at any `review_mode`. Its
phase gates are the pipeline's own decision points (defined under `team.size`
below), and the roles that work at them are team members, not director gates.

`automation` drives the Decision Points note above. See the Decision Points note above and
`.claude/docs/automation-modes.md` for how each mode changes pipeline behavior.

**`team.size`**: which specialist roles are active (orthogonal to review_mode gate-depth and workflow docs).
- **`individual`** (default): `release-manager` only. Other roles folded into the release-manager, not performed separately.
- **`small`**: + `producer` + `devops-engineer` + `qa-lead` + `community-manager`.
- **`studio`**: + `security-engineer` + `analytics-engineer` + `localization-lead` + `performance-analyst`, and `network-programmer` when the game is multiplayer (the full pipeline as documented).
A non-core role needed at `individual` is folded into the nearest active core role with an informational note. **"Phase gate" means any phase that ends in an `AskUserQuestion` decision point this pipeline itself lists** — a transition under Decision Points above, the stage check, or the Phase 6 deploy question — **whatever the `automation` mode.** `guided` and `autonomous` change how a gate is passed (it auto-advances, or is recorded with `log_decision`), not whether it is one, so the gate stays a gate in every mode. A role restricted to "phase gates only" is performed at those points and no others. This active-set scoping applies throughout the pipeline below: any phase that names a role outside the active set is folded into the nearest core role rather than performed as a separate pass.

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
- **release-manager** — Release tag, versioning, changelog, patch notes, deployment
- **qa-lead** — Test sign-off, regression suite, release quality gate
- **devops-engineer** — Build pipeline, artifacts, deployment automation
- **security-engineer** — Pre-release security audit (invoke if game has online/multiplayer features or player data)
- **network-programmer** — Netcode stability sign-off (invoke if game has multiplayer)
- **analytics-engineer** — Verify telemetry events fire correctly and dashboards are live
- **localization-lead** — Verify every shipped string is translated
- **performance-analyst** — Benchmark the release build against its performance targets
- **community-manager** — Launch announcement and player-facing messaging, written from the patch notes
- **producer** — Go/no-go decision, stakeholder communication, scheduling

## How to Run Inline

Run each specialist pass inline in this chat. Read the role's
`.claude/agents/<id>.md` for its domain rules, then perform the work here. Never
call `Agent` / `subagent` for a team or for a specialist:
- **release-manager** — Release tag, versioning, changelog, patch notes, deployment
- **qa-lead** — Test sign-off, regression suite, release quality gate
- **devops-engineer** — Build pipeline, artifacts, deployment automation
- **security-engineer** — Security audit for online/multiplayer/data features
- **analytics-engineer** — Telemetry event verification and dashboard readiness
- **community-manager** — Launch communication, written from the patch notes
- **producer** — Go/no-go decision, stakeholder communication
- **network-programmer** — Netcode stability sign-off (invoke if game has multiplayer)
- **localization-lead** — Translation completeness sign-off (Phase 4)
- **performance-analyst** — Performance benchmarks against targets (Phase 4)

**Use context once — do not re-read.** Read the shared inputs **once** in this
chat and keep only the sections each pass actually needs. Never re-open a whole
document you already hold; a role performed inline has the same context you do.

**Present each pass compactly.** In the chat, give the artifact path, ≤5
bullets of decisions, and any BLOCKED/CONCERNS items, one line each. Do not
restate the documents you read. Every write still follows the ask-first protocol
in this same chat (File Write Protocol below).

**Substitute a real path for `[path]`.** One file per role under
`production/releases/`, except the two whose homes are fixed elsewhere. An active
role standing in for one outside the active set writes that role's file:

| Phase / role | Writes to | Destination fixed by |
|---|---|---|
| 1 producer | `production/releases/release-plan-[version].md` | this skill |
| 2 release-manager | `production/releases/release-checklist-[version].md` | `/release-checklist` |
| 3 qa-lead | `production/releases/qa-gate-[version].md` | this skill |
| 3 devops-engineer | `production/releases/build-[version].md` | this skill |
| 3 security-engineer | `production/releases/security-signoff-[version].md` | this skill |
| 3 network-programmer | `production/releases/netcode-signoff-[version].md` | this skill |
| 4 localization-lead | `production/releases/localization-signoff-[version].md` | this skill |
| 4 performance-analyst | `production/releases/performance-signoff-[version].md` | this skill |
| 4 analytics-engineer | `production/releases/analytics-signoff-[version].md` | this skill |
| 5 go/no-go | `production/releases/go-no-go-[version].md` | this skill |
| 6 release-manager | `docs/patch-notes/[version].md` | `/patch-notes` |
| 6 community-manager | `production/releases/announcement-[version].md` | this skill |
| 7 release-manager | `production/releases/release-report-[version].md` | this skill |

> **Every one of those thirteen outputs needs a stated destination.**
> `production/releases/` is where `/release-checklist` already writes, and
> `docs/patch-notes/[version].md` is where `/patch-notes` already writes, so the
> release record lands in one place regardless of which skill produced it.
>
> **A separate file per role, not one appended record.** Phase 3 and Phase 4
> run consecutive passes; two passes appending to one file overwrite each other,
> and the earlier section vanishes silently.

> **Why no bounded exception is needed.** `CLAUDE.md` requires "May I write this
> to [filepath]?" before Write/Edit. Because the orchestrator performs every pass
> itself in the user's chat, that normal rule applies to every artifact: show the
> draft or file set, ask, wait for yes, then write. There is no per-pass write
> authority to hand out and no question for a parent to answer.

Run independent passes in sequence in this chat where the pipeline allows it (the Phase 3 passes run in sequence here).

## Pipeline

### Phase 1: Release Planning
Run the **producer** pass inline:
- Confirm all milestone acceptance criteria are met
- Identify any scope items deferred from this release
- Set the target release date and communicate to team
- Output: release authorization with scope confirmation

### Phase 2: Release Candidate
Run the **release-manager** pass inline:
- Bump version numbers in all relevant files on `main`; the commit carrying the bump is the release candidate. Development is trunk-based — a release is a tag on `main` (applied in Phase 6), not a branch
- Confirm the release checklist from Polish (`/release-checklist`, run before `/gate-check release`) is complete for this candidate; run it now only if none exists
- Cut a `release/[version]` branch from the candidate only if this release needs stabilising (a freeze, platform certification) — bug fixes only there, and every fix lands on `main` as well
- Output: release candidate commit (plus the `release/*` branch, if one was cut) and checklist

### Phase 3: Quality Gate (parallel)
Run these passes inline, in order:
- **qa-lead**: Execute full regression test suite. Test all critical paths. Verify no open bugs at the severities `/gate-check release` blocks for this `workflow`: S1 at every tier, S2 and S3 too at `full`. Sign off on quality.
- **devops-engineer**: Build release artifacts for all target platforms. Verify builds are clean and reproducible. Run automated tests in CI.
- **security-engineer** *(if game has online features, multiplayer, or player data)*: Conduct pre-release security audit. Review authentication, anti-cheat, data privacy compliance. Sign off on security posture.
- **network-programmer** *(if game has multiplayer)*: Sign off on netcode stability. Verify lag compensation, reconnect handling, and bandwidth usage under load.

When either role is in the active set, decide its condition from `platform.online` and `platform.multiplayer` in `project.yaml`, plus whether the game stores player data. A key that is absent is not a `false`: ask the user rather than assume an offline game. A role skipped on these grounds says so by name in the Phase 3 output — e.g. `security-engineer: not performed — platform.online: false, platform.multiplayer: false, no player data`.

### Phase 4: Localization, Performance, and Analytics
Run these passes inline, one after another (folded in where the role is not active):
- Verify all strings are translated (fold in **localization-lead** if active)
- Run performance benchmarks against targets (fold in **performance-analyst** if active)
- **analytics-engineer**: Verify all telemetry events fire correctly on release build. Confirm dashboards are receiving data. Check that critical funnels (onboarding, progression, monetization if applicable) are instrumented.
- Output: localization, performance, and analytics sign-off — one file per role (table above)

### Phase 5: Go/No-Go
Before the go/no-go pass, get the **technical-director** release sign-off. The
producer role stays in this chat, so this orchestrator performs the
`technical-director` pass at
`review_mode: full` only — this is a director review, not a PHASE-GATE, so `lean`
and `solo` skip it. Ask for GO, CONCERNS or NO-GO on the release candidate's
technical state, or NOT ASSESSED naming what it could not read. When it is not
performed, the go/no-go record says `technical-director sign-off: not run
(review_mode: <mode>)` instead of listing it as given; a NOT ASSESSED answer is
recorded as such and never counted as a sign-off.

Run the **producer** pass inline, passing every sign-off collected so far:
- Collect sign-off from: qa-lead, release-manager, devops-engineer, security-engineer (if performed in Phase 3), network-programmer (if performed in Phase 3), and technical-director (if performed above)
- Carry a stage-check override, if there was one, into the go/no-go record as its `Stage override:` line
- Evaluate any open issues — are they blocking or can they ship?
- Make the go/no-go call
- Output: release decision with rationale

**If producer declares NO-GO:**
- Surface the decision immediately: "PRODUCER: NO-GO — [rationale, e.g., S1 bug found in Phase 3]."
- Use `AskUserQuestion` with options:
  - Fix the blocker and re-run the affected phase
  - Defer the release to a later date
  - Override NO-GO with documented rationale (user must provide written justification)
- **Skip Phase 6 entirely** — do not tag, deploy to staging, deploy to production, or perform the community-manager pass.
- Produce a partial report summarizing Phases 1–5 and what was skipped (Phase 6) and why.
- Verdict: **BLOCKED** — release not deployed.

After the user selects "Override NO-GO with documented rationale":
- Ask with the question widget (free-text answer; plain text only if no widget tool exists): "Please describe the justification for overriding the NO-GO verdict. This will be embedded in the release record."
- Wait for the user's written justification.
- Embed the justification text in the partial approval record before Phase 6: append a "⚠️ Override Justification: [user's text]" field.
- Only then proceed to Phase 6.

### Phase 6: Deployment (if GO)

**This phase always requires explicit user approval regardless of
`modes.automation` — including `autonomous` mode.** Production deployment is
irreversible and high-stakes; it is NOT covered by the configurable
`automation_always_ask` categories, so this skill guards it unconditionally.
Before tagging or deploying, use `AskUserQuestion`:
- Prompt: "Producer verdict is GO. Execute Phase 6 — tag, deploy to staging,
  deploy to production?"
- Options: `[A] Yes, deploy` / `[B] Staging only — hold production` / `[C] Stop here`

Only after explicit approval, run the **release-manager** and **devops-engineer** passes inline:
- Tag the release in version control
- Finalize the changelog drafted in Polish (`/write-changelog`), adding what changed since the gate
- Deploy to staging for final smoke test
- Deploy to production (only if the user approved production above)
- Human team action: Monitor dashboards and error rates for 48 hours post-release. Schedule a follow-up retrospective using `/retrospective` at the 48-hour mark.

After deployment, run the **release-manager** pass inline:
- Finalize the patch notes drafted in Polish using `/patch-notes [version]` — release-manager carries that skill and the Bash access its `git log` step needs; `community-manager` has neither

Then hand those patch notes to **community-manager**:
- Prepare launch announcement (store page updates, social media, community post)
- Draft known issues post if any S3+ issues shipped
- Output: all player-facing release communication, ready to publish on deploy confirmation

### Phase 7: Post-Release
- **release-manager**: Generate release report (what shipped, what was deferred, metrics)
- **producer**: Update milestone tracking, communicate to stakeholders
- **qa-lead**: Monitor incoming bug reports for regressions
- **community-manager**: Publish all player-facing communication, monitor community sentiment
- **analytics-engineer**: Confirm live dashboards are healthy; alert if any critical events are missing
- Keep the 48-hour monitoring window from Phase 6: bugs, dashboards and community sentiment are watched for 48 hours after release (release-manager's own watch runs to its 72h report)
- Schedule post-release retrospective if issues occurred

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
- ADR status is Proposed → do not implement; accept it with `/architecture-decision accept ADR-NNNN` once decided
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

A summary report covering: release version, scope, quality gate results, go/no-go decision, deployment status, and monitoring plan.

Verdict: **COMPLETE** — release executed and deployed.
Verdict: **BLOCKED** — release halted; the stage check stopped it, go/no-go was NO, or a hard blocker is unresolved.

## Next Steps

- Monitor post-release dashboards for 48 hours.
- Run `/retrospective` if significant issues occurred during the release.
- `project.stage` reads `Release` unless the stage check was overridden: `/gate-check release` is the Polish → Release readiness gate, run before this skill. After an override the stage still reads what it did. Only `/gate-check` changes `project.stage` (on a PASS, or a CONCERNS whose risks the user accepted), so this skill never writes it or `production/stage.txt`. `Release` is the terminal stage in the `project.stage` enum — there is no post-launch stage value. Record live/post-launch status in the release report, not in `project.stage`.
