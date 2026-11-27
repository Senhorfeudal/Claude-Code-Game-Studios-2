# Agent Coordination Rules

1. **Vertical Delegation**: Leadership agents delegate to department leads, who
   delegate to specialists. Never skip a tier for complex decisions.
2. **Horizontal Consultation**: Agents at the same tier may consult each other
   but must not make binding decisions outside their domain.
3. **Conflict Resolution**: When two agents disagree, escalate to the shared
   parent. If no shared parent, escalate to `creative-director` for design
   conflicts or `technical-director` for technical conflicts.
4. **Change Propagation**: When a design change affects multiple domains, the
   `producer` agent coordinates the propagation.
5. **No Unilateral Cross-Domain Changes**: An agent must never modify files
   outside its designated directories without explicit delegation.
6. **Read Design Docs by Section**: A brief names the sections an agent needs
   by heading. Find a heading in a GDD, ADR or the art bible with the Grep
   tool (`^#`, content mode) and Read that range with offset and limit; read a doc
   whole only when the task needs all of it, and say why. `validate-read.sh`
   refuses a whole-file read of a doc over 40 KB.
7. **Nothing Goes Upstream**: Never file, open or comment on an issue or pull
   request in an engine, plugin or vendor repository, even when asked. Write a
   draft (`/bug-report` drafts only) and the user submits it.

## Model Tier Assignment

Read `.claude/docs/model-tiers.md` on demand. It carries the tier table, the
per-skill assignments and the authoring rule.

**Key point:** whether a skill's `model:` is used
depends on how the skill starts. Typed as `/skill-name`: yes, except a `haiku`
pin in auto mode. Started by Claude through the Skill tool: no. Never tell a
user a `haiku` skill saves money; an `opus` skill typed in a Sonnet session
costs more. The agent-side `model:` is a different mechanism, and is applied.

## Subagents vs in-chat teams vs Agent Teams

This project uses three distinct patterns. Pick the right one before planning work:

### In-chat teams (all `/team-*` skills)
A team is an orchestrator running in the conversation the user opened. It loads
each specialist's role rules and performs the phase inline; it never calls
`Agent` / `subagent` for itself or for a specialist. All decisions and write
approvals use the question widget in that same chat. This matters on OpenCode
Mobile: a team forwarded into a subagent conversation loses the widget and can
only return a pending decision to a parent, leaving the user in a running
session with no visible question. Full rule: `.claude/docs/in-chat-teams.md`.
`/next-step` loads a chosen team in the current chat; it never routes a team to
a crew.

### Subagents (non-team orchestration only)
Spawned via the `Agent` tool (OpenCode: `subagent`) within a single session for
non-team orchestration such as `/review-all-gdds`. Subagents share the session's
permission context and return results to the parent. A subagent asked for a
decision must return it to the orchestrating conversation — it must never draft
a question in its own output, where nobody can answer it.

**When to spawn in parallel**: If two subagents' inputs are independent (neither
needs the other's output to begin), spawn both `Agent` calls simultaneously
rather than waiting. Example: `/review-all-gdds` **Phase 2** (consistency) and
**Phase 3** (design theory) are independent — spawn both at the same time.
Phase 1 loads the GDDs and both depend on it, so it is the one phase here that
must NOT be parallelised.

### Agent Teams (experimental — opt-in)
Multiple independent Claude Code *sessions* coordinated via a shared task list.
Opt-in only — read `.claude/docs/agent-teams.md` on demand before proposing one.
Not used by `/team-*` skills.

## Parallel Task Protocol

For non-team orchestration that spawns multiple independent agents:

1. Issue all independent `Agent` calls before waiting for any result
2. Collect all results before proceeding to dependent phases
3. If any agent is BLOCKED, surface it immediately — do not silently skip
4. Always produce a partial report if some agents complete and others block

For teams, the equivalent is a sequence of inline passes in the user's chat:
keep each pass's artifact path, decision bullets and BLOCKED/CONCERNS distinct,
and ask every approval there.
