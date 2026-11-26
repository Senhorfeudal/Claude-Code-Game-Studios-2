# Agent routing for `/next-step`

Used only **after** the user chooses an action in Step 7b. This maps an action
to a starting crew; it is not a task brief. The orchestrator still writes a
brief with the chosen action, the state report and the crew roles.

## Rules

- At most **three agents** per crew. The first owns the result; the others
  consult. An owner may not delegate the whole task away.
- Read `project.yaml` first. Use `engine.name` and `modes.rigor` from the
  resolved config; do not route on a guess about the project.
- **Engine override:** for Godot, Unity or Unreal, replace `engine-programmer`
  with `godot-specialist`, `unity-specialist` or `unreal-specialist` (or the
  named sub-specialist when the action targets shaders, UI, GAS, replication or
  addressables). For Web, keep `engine-programmer`.
- `gamer` and `question-widget-specialist` are **read-only**. They may research
  or review question wording; they never implement or write files.
- Every agent with `Write`/`Edit` follows the ask-first protocol in `CLAUDE.md`.
  Ask before writing, show the draft, wait for approval.
- If no row matches, say `NOT ASSESSED — NO ROUTE` and ask the user to name the
  agents. Never invent a crew from the repository name.

## Routes

| Step id / action | Command | Crew (owner first) | Why |
|------------------|---------|--------------------|-----|
| `engine-setup` | `/setup-engine` | `technical-director`, `engine-programmer` | Pin the engine version and its project conventions |
| `game-brief` | `/brainstorm` | `creative-director`, `game-designer`, `gamer` | Shape the pitch and scope; `gamer` only when references are wanted |
| `game-concept` | `/brainstorm` | `creative-director`, `game-designer`, `world-builder` | Pillars, mechanics and the world the concept needs |
| `create-stories` | `/create-stories` | `producer`, `game-designer`, `qa-lead` | Break the brief into build order with testable acceptance criteria |
| `dev-story` | `/dev-story` | `gameplay-programmer`, `qa-tester` | Implement the story and cover its acceptance criteria |
| `story-done` | `/story-done` | `qa-lead`, `qa-tester` | Verify evidence before closing the story |
| `prototype` | `/prototype` | `prototyper`, `creative-director` | Build the one-shot and keep it tied to the brief |
| `art-bible` | `/art-bible` | `art-director`, `technical-artist` | Visual identity plus what the engine can actually render |
| `map-systems` | `/map-systems` | `game-designer`, `systems-designer` | Decompose the concept and order the systems |
| `design-system` | `/design-system` | `systems-designer`, `game-designer` | Write one system's GDD against the design pillars |
| `create-architecture` | `/create-architecture` | `lead-programmer`, `technical-director` | Module boundaries and engine-compatible decisions |
| `architecture-decision` | `/architecture-decision` | `technical-director`, `lead-programmer` | Record context, alternatives and consequences |
| `architecture-review` | `/architecture-review` | `technical-director`, `lead-programmer` | Check GDD traceability and cross-ADR conflicts |
| `qa-plan` | `/qa-plan` | `qa-lead`, `qa-tester` | Classify stories and write the sprint test plan |
| `gate-check` | `/gate-check` | `producer`, `qa-lead` | Stage readiness and the required artifacts |
| `balance-check` | `/balance-check` | `economy-designer`, `game-designer` | Find broken progressions and degenerate strategies |
| `bug-report` | `/bug-report` | `qa-tester`, `gameplay-programmer` | Reproduce, severity, then likely owner |
| `security-audit` | `/security-audit` | `security-engineer`, `lead-programmer` | Save tampering, cheats, input and data exposure |
| `perf-profile` | `/perf-profile` | `performance-analyst`, `technical-artist` | Measure against budgets before optimising |
| `localize` | `/localize` | `localization-lead`, `writer` | String tables, cultural review and voice scope |
| `release-checklist` | `/release-checklist` | `release-manager`, `devops-engineer`, `qa-lead` | Build, certification, store metadata and sign-off |
| `cut` | `/cut` | `producer`, `creative-director` | What to cut and the polish list that finishes it |
| external research | `/next-step` | `gamer`, `creative-director` | Research first, then decide what it means for the project |
| stuck / unclear | `/next-step` | `producer`, `creative-director` | Re-orient and reduce to one action |
