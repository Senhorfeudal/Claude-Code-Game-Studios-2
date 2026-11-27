---
name: brainstorm
description: "Decides game vs app/tool first, then guides the user to a written concept and the right agents/skills. Use for game ideas, app/tool ideas, new concepts, or exploring other directions."
argument-hint: "[idea, 'open', or 'app/tool'] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, WebSearch, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/brainstorm/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,docs.density,workflow`

Resolved above; use as-is. No block → the defaults in `.claude/docs/config-resolution.md`
(`workflow: minimal`, `review_mode: solo`, `automation: collaborative`, `docs.density: terse`), and
say that the settings were not read.

## 0. Project-kind gate — always first

Before any concept question, ask with the question tool:

> What are we creating?
> 1. **Jogo** — a game with rules, player goals and playtesting.
> 2. **Aplicativo ou ferramenta** — software, a web/mobile app, CLI, internal tool or library.

The question is the last thing in the reply; wait for the answer. A skipped or
dismissed question is not an answer.

- **Jogo:** continue with the game flow below. Never read the software reference.
  Run the mandatory external scan below before any concept question.
- **Aplicativo ou ferramenta:** read `.claude/skills/brainstorm/references/software-concept.md`
  and follow it. It writes `design/software-brief.md`, chooses one `sw-*` agent and
  routes to generic software skills. Do **not** load `references/full-concept.md`,
  game director gates or the game brief template in this branch. Say the chosen
  agent and skills in the reply so the user can override them. Run the mandatory
  external scan below before the shape question.

The 38 `sw-*` agents and the routing table live in `docs/software-agents.md`.

# Brainstorm

Turns no idea, or a rough one, into a written design the next step builds from. The project-kind
gate above decides which branch you are in. How much it writes depends on `workflow`:

- **`minimal`, game:** the Lean Brief flow below: a one-page `design/game-brief.md`, then stop. No
  discovery questions, pillars, director gates or `game-concept.md`, and do not load
  `references/full-concept.md`.
- **`standard` or `full`, game:** read `references/full-concept.md` and follow it. It writes
  `design/gdd/game-concept.md` from `.claude/docs/templates/game-concept.md`. Its gates follow
  `.claude/docs/director-gates.md`; each director agent is given its own gate file,
  `.claude/docs/director-gates/<gate-id in lower case>.md` (`cd-pillars.md`,
  `ad-concept-visual.md`, `td-feasibility.md`, `pr-scope.md`), and you do not read those files
  yourself.
- **app/tool:** use `references/software-concept.md` instead; it writes
  `design/software-brief.md` and selects one `sw-*` agent plus generic software skills.

`--review` in the text typed after the skill name overrides `review_mode` for this run.
`docs.density` sets each section's depth: `terse` = bullets; `balanced` = with brief rationale;
`thorough` = rationale and alternatives. Questions follow `.claude/docs/automation-modes.md`
(collaborative asks, guided asks only for major decisions, autonomous logs and proceeds; the
always-ask categories always ask).

Ask with the question tool. Without one, list the options numbered and end your turn to wait. The
question is the last thing in the reply: no advice or lean after it. A skipped or dismissed
question is not an answer: ask again in plain text.

### External scan (`@gamer`) — mandatory, both branches

After the project-kind gate and **before any concept question**, run one sector
scan. Follow `.claude/docs/external-scan.md`. Spawn `gamer` once with a narrow
brief: project kind, engine/platform/stage from `project.yaml`, the sector (game
genre/theme or app category and shape), and the decision this scan must inform.
The game branch never reads the software reference; the app/tool branch never
reads game director gates. Reuse `design/external-scan.md` from this session
when its sector still matches — never spawn a second gamer for the same sector.

Return contract: "Return only (1) the sourced research brief, (2) 3-6 bullets of
local comparison, (3) typed suggestions with owner skills/agents and a concrete
reapplication proposal, and (4) one question with 2-4 options and a
recommendation for the user. Write no files." Use its question as the next
question to the user, widget-first, with the trade-offs in the option
descriptions. Feed the proposals into the concept questions as evidence; never
paste the whole research table before the question. If it returns
`NOT ASSESSED — NO DATA`, continue from the user's words without inventing
references and record that verdict in the scan.

Offer the scan for writing with the brief's write approval: name both paths in
that question and write `design/external-scan.md` only on explicit yes. Applying
any proposal to the brief or GDD needs that document's own approval.

## Lean Brief flow (`workflow: minimal`, game branch)

A few exchanges, not fifteen: capture the thinking that carries the game on one page, then get to
a playable game. Write from the template `.claude/docs/templates/game-brief.md` (six required
fields, the rest one line each). If `design/game-brief.md` exists, read it and refine it instead
of starting over; its In your words section is never rewritten, only added to.

1. **Concept.** From the hint typed after the skill name (or one quick open question if there is
   none), propose **2 or 3 one-line concepts** (verb-first or a mashup of genre and theme), not
   full concept cards. Ask the user to pick or combine them. This is the one creative question
   every run asks.

   **No engine set, at this tier:** the pick is the only question. (`engine.name` in
   `project.yaml` absent, empty or `web`.) On the pick, write nothing and say, with the picked
   concept and their hint in the brackets:
   "Type `/prototype <the picked concept, in their words>` to build it: it asks one round of
   questions, writes the one-page brief from the genre's sheet and builds a playable browser
   game." End with `Verdict: COMPLETE — concept picked; /prototype writes
   the brief.` Go on to step 2 only when they ask to write the brief here first ("write it
   down", "formalize it", or `/start`'s `Formalize it first`).
2. **Fill the brief** in conversation, several fields per exchange:
   - **In your words:** everything the user writes about the game, word for word: the hint, their
     descriptions, their changes. Never your concept lines; when they only picked one, it holds
     their hint and which concept they picked.
   - **Working title:** the brief's title line. Offer one from the chosen concept and let the user
     change it; `/create-stories` names the epic folder after it.
   - **Pitch:** the excited one-liner.
   - **Genre**, **Controls** (how you play) and **Look** (how it looks and sounds, in their
     words, under Look and references): one line each.
   - **Question** (what a first playable build must answer) and **Hooks** (what makes it this
     game and not its genre): propose them from the concept; the user changes them.
   - **Core loop:** the 2 to 4 steps the player repeats.
   - **Goal & fail state**: what the player tries to do, and how they lose. `/create-stories` turns
     it into acceptance criteria.
   - **Features:** the short list that makes it the game, each `[ ]` (not built yet); each becomes
     a story. **More than 7 items: push back.** Say it is too long for an MVP, propose which items
     to cut (the ones the core loop works without), and keep the brief to 7 or fewer.
   - **Out of scope:** what they are deliberately not building (the cut items go here).
   - **Avoid:** every removal in their words ("no combat", "no waiting"), and anything they reject.
   - **Build order:** the riskiest or least proven part first.
   - **Intent:** only from their words or a game they name ("no game over", "a toy, no goal");
     usually empty.
   - **Kill condition** (when to drop it), **Who it's for / what they feel**, **Games you love /
     don't** (any number, a word on why each): one line each; offer, don't force.

   Mark each field the user did not give *(guessed)*, or *(provisional)* when they said "you
   pick". **Keep** stays empty: it fills after they play.
3. **Show the filled brief in full.** Then ask, as its own question: "Brief is ready. May I write it
   to `design/game-brief.md`? The external scan goes to `design/external-scan.md` in the same
   approval." `Yes — write both` / `Revise a field first`. Write only on an explicit
   yes to this question; agreeing to a cut or saying "go on" is not a yes to the write. On a
   revision, change the named field, show it before and after, and ask again. Then write
   `design/game-brief.md` and the approved `design/external-scan.md`, creating folders as
   needed. Never write `design/gdd/game-concept.md` at this tier.
4. **Next steps.** Read `engine.name` in `project.yaml`:
   - **Absent, empty or `web`:** one step, `/prototype`: it builds the brief as a playable
     browser game, after a card of what it will build. Say "Type `/prototype` to build
     it." and do not start it yourself: a typed `/brainstorm` runs its turn on this skill's model,
     and the build must run on the session's.
   - **An engine set:**
     1. `/create-stories`: turn the Features list into stories. At `minimal` there is no separate
        `/create-epics` or `/sprint-plan`; the build order is the plan.
     2. `/dev-story`: the first line of game code.

     Then one line: "`/prototype --path html` makes a browser sketch first; not recommended, since
     the game is rebuilt in [engine]."

   Then one summary line: the pitch, the number of Features, and `design/game-brief.md`. End with
   the line `Verdict: COMPLETE — game brief written; next stop is code.`

If the user stops before the write, say the brief was not written, so it lives only in this
conversation.
