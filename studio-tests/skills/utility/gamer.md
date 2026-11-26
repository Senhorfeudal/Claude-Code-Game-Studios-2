# Skill Test Spec: /gamer

## Skill Summary

`/gamer` is a read-only utility skill that exposes the existing `gamer` agent
through the slash-command list. It builds a narrow research brief from the
invocation and local project context, asks for the brief through the runtime
question widget when it is missing, and delegates to exactly one `gamer`
subagent. The agent performs the web/forum/GitHub research and returns a
question with 2-4 options; the skill asks that question verbatim through its
own widget and reports only the chosen decision with the necessary sources.
The skill never writes files, never asks from the subagent and never presents
a raw research dump as the final answer. Verdicts: `COMPLETE — research
delivered`, `COMPLETE — research declined` and `NOT ASSESSED — <reason>`. No
director gates apply.

---

## Static Assertions (Structural)

Checked against the SKILL.md by `/skill-test spec` — no fixture needed.

- [ ] Frontmatter has all required fields (`name`, `description`, `argument-hint`, `user-invocable`, `allowed-tools`)
- [ ] `allowed-tools` has `Agent` and `AskUserQuestion`, and no `Write` or `Edit`
- [ ] Contains verdict keywords: COMPLETE, NOT ASSESSED
- [ ] Delegates to the `gamer` agent with one `Agent` call
- [ ] Says the subagent has no question widget and must not ask the user
- [ ] Says the agent's question is used verbatim in one widget call
- [ ] Has a next-step handoff (`/next-step`)

---

## Director Gate Checks

None. This is a research-and-decision utility; no director gate is invoked at
any `review_mode`.

---

## Fixture Defaults

Every case starts from `modes.rigor: minimal` and `modes.automation:
collaborative`, with no `project.local.yaml`, per `studio-tests/CLAUDE.md` §
Fixture defaults. Each case has a project with `project.yaml` and a question
widget in the runtime.

---

## Test Cases

### Case 1: Invocation carries a narrow brief

**Fixture:**
- `project.yaml` declares Web / TypeScript
- Input: "gamer research parry timing for a Web melee prototype; decide whether to copy the window or the telegraph"
- The `gamer` agent returns 3 options with trade-offs

**Expected behavior:**
1. The skill reads the local context, makes no write, and does not ask for another brief
2. It spawns one `gamer` agent with engine, platform, feature, decision and local file names
3. The agent's question is passed verbatim to the widget with its 3 options
4. The user's answer is reported with the sources that justify it
5. Verdict is `COMPLETE — research delivered`

**Assertions:**
- [ ] No `Write` or `Edit` call
- [ ] Exactly one subagent
- [ ] No reasoning or draft text precedes the question call
- [ ] No raw research table is shown before the question

### Case 2: Missing brief is asked through the widget

**Fixture:**
- Input: `/gamer` with no argument

**Expected behavior:**
1. The skill calls the question tool with the four brief options and a free-text affordance
2. A skipped or dismissed question is re-asked once, then falls back to plain text
3. Only a real choice is delegated; "Decide without external research" ends with `COMPLETE — research declined`

**Assertions:**
- [ ] The question tool is called before the agent
- [ ] No delegation follows a skipped question
- [ ] Declining research causes no agent call

### Case 3: Agent has no data

**Fixture:**
- The `gamer` agent returns `NOT ASSESSED — NO DATA` with the fallback question

**Expected behavior:**
1. The skill keeps the agent's verdict instead of inventing sources
2. The fallback question is asked through the widget
3. Verdict remains `NOT ASSESSED — NO DATA`

**Assertions:**
- [ ] No fabricated URL or source appears
- [ ] The agent's verdict is not upgraded to COMPLETE

### Case 4: Runtime without an agent tool

**Fixture:**
- The runtime exposes no `Agent` tool

**Expected behavior:**
1. The skill answers `NOT ASSESSED — NO AGENT TOOL`
2. It names the `gamer` agent for direct invocation
3. It makes no research claim

**Assertions:**
- [ ] No delegation is attempted
- [ ] The verdict is NOT ASSESSED

### Case 5: Follow-up needs separate confirmation

**Fixture:**
- The user answered the research question and the skill offered `prototype`

**Expected behavior:**
1. The follow-up is offered through the widget after the answer
2. No skill or agent is started until the user confirms it

**Assertions:**
- [ ] Research delivery and follow-up are distinct questions
- [ ] The verdict is reported before any follow-up work

---

## Protocol Compliance

- [ ] Questions go through the runtime widget, with no raw reasoning before the call
- [ ] A skipped or dismissed question is not an answer
- [ ] Plain text is only a fallback when no question tool exists
- [ ] The subagent returns its question to the orchestrator; it never asks directly
- [ ] The skill writes no files
- [ ] Exactly one subagent is delegated at a time
