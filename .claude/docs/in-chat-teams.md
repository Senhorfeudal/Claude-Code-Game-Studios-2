# In-chat team orchestration

**Status:** normative for all `/team-*` skills. Supersedes the subagent fan-out
described in `coordination-rules.md` for team pipelines only.

A team is an **orchestrator that runs in the conversation the user opened**. It
is a skill, never an agent. No team skill may be spawned with `Agent` /
`subagent`, and no team skill may spawn its specialists with `Agent` /
`subagent` either. Every phase is performed inline, in the same chat, with the
same question widget and the same write-approval protocol the user is already
using.

## Why

A team forwarded into a subagent conversation loses the question widget. Its
only remaining move is to return a pending decision to a parent, which must
then re-spawn the team and re-ask — a loop where the user sees no question and
the session stays "running". Running the orchestrator in the user's chat keeps
decisions and approvals where the user can actually answer them.

## Rules

1. **Load, don't delegate.** Invoke a team with its slash command or by loading
   the skill in the current chat. `/next-step` loads a chosen team the same way.
   Never put a `/team-*` id in an `Agent` / `subagent` call.
2. **Specialists are roles, not sessions.** For each phase, read the named
   specialist's `.claude/agents/<id>.md` for its domain rules, then perform the
   work inline. Announce which roles are active at the resolved `team.size` and
   which are folded into a nearest active role. A role outside the active set is
   not performed as a separate pass; its input is summarised into the role that
   covers it.
3. **Sequential, not parallel.** Phases marked "parallel" become consecutive
   inline passes. Keep each pass's output distinct — path, ≤5 decision bullets,
   BLOCKED/CONCERNS — so no reader has to guess which role produced which line.
4. **Ask in this chat.** Every `AskUserQuestion` / `question` call happens in the
   orchestrating conversation. Nothing is forwarded to a parent for an answer.
   If a team skill somehow finds itself inside a subagent, stop and tell the
   caller to load the team skill in the main chat; never draft a question in
   reasoning there.
5. **Ask before every write.** The orchestrator writes all artifacts itself in
   the current chat. Before each write, show the draft or the file set and ask
   “May I write this to [path]?”; wait for approval. There is no subagent
   bounded-exception for team writes.
6. **Same verdicts.** Engine validation, skipped roles and blocked phases are
   still reported with the skill's existing verdict wording. A role performed
   inline counts as performed; a role folded into another counts as not
   separately assessed.

## `team.size` after the change

| Size | Active roles |
| --- | --- |
| `individual` (default) | the core role named by each skill; others folded in |
| `small` | the full role list in that skill's Team Composition |
| `studio` | full role list + engine sub-specialist validation + adversarial review pass |

The size still controls rigor and token spend; it no longer controls how many
agent sessions are created (that number is always zero).
