# Software branch of `/brainstorm`

Use this file **only** after the project-kind gate returns *aplicativo/ferramenta*.
Never load `full-concept.md`, the game director gates, or the game brief template
in this branch. The deliverable is `design/software-brief.md`.

## 1. Pick the software shape

Ask one question with 2-4 options. Recommend from the user's words; never guess:

1. **CLI / code agent** — terminal work, SDK, library, repo tooling, automation.
2. **App builder** — web or mobile product with screens and user accounts.
3. **Data or internal tool** — dashboards, CRUD, admin panels, reports.
4. **Framework / autonomous** — a pipeline, multi-agent system or evaluation harness.

Use the answer to select one primary `sw-*` role. Name it in the next reply so
the user can override it.

## 2. Role routing

| Shape | Primary roles | Notes |
| --- | --- | --- |
| CLI / code agent | `sw-aider`, `sw-cline`, `sw-cursor`, `sw-windsurf`, `sw-gemini-cli`, `sw-claude-code`, `sw-codex`, `sw-opencode`, `sw-openbitfun`, `sw-continue`, `sw-forge`, `sw-gpt-engineer`, `sw-gpt-pilot`, `sw-smol-developer`, `sw-swe-agent`, `sw-devika`, `sw-devin`, `sw-opendevin`, `sw-openhands`, `sw-kortix`, `sw-orkas`, `sw-looptroop`, `sw-memex` | Match by workflow, not by brand preference. |
| App builder | `sw-appwizzy`, `sw-base44`, `sw-bolt`, `sw-co-dev`, `sw-create`, `sw-databutton`, `sw-floot`, `sw-heyboss`, `sw-lovable`, `sw-magically`, `sw-leap`, `sw-replit`, `sw-mocha` | Mobile goes to `sw-magically`; front-end-only goes to `sw-mocha`. |
| Data or internal tool | `sw-tooljet`, `sw-probz`, `sw-appwizzy`, `sw-co-dev` | Always ask about data sources and permissions. |
| Framework / autonomous | `sw-openhands`, `sw-looptroop`, `sw-gpt-pilot`, `sw-orkas`, `sw-devika` | Ask what must be reproducible and how success is evaluated. |

The full catalog with focus, pricing and upstream link is in
`docs/software-agents.md` and `docs/software-agents.json`.

## 3. Skill routing

Use these generic studio skills by need, not all at once:

- **Definition:** `/create-stories`, `/story-readiness`, `/quick-design`.
- **Architecture:** `/create-architecture`, `/architecture-decision`,
  `/architecture-review` (these work for software too; ignore engine-only text).
- **UX:** `/ux-design`, `/ux-review`, `/localize`.
- **Quality:** `/test-setup`, `/qa-plan`, `/code-review`, `/security-audit`,
  `/perf-profile`, `/smoke-check`, `/regression-suite`.
- **Delivery:** `/sprint-plan`, `/gate-check`, `/release-checklist`,
  `/write-changelog`.

Do not use game-only skills (`art-bible`, `balance-check`, `playtest-report`,
`prototype`) unless the user explicitly wants a game-like toy.

## 4. Brief flow

`workflow: minimal`: capture the fields in one exchange, show the filled brief,
then ask once: "Brief is ready. May I write it to `design/software-brief.md`?"
Write only on an explicit yes. Do not add architecture docs at this tier.

`standard` or `full`: use `.claude/docs/templates/software-brief.md`, fill every
field, mark guesses *(guessed)*, show the whole brief, and ask the same write
question. After the write, recommend the primary `sw-*` role and the first two
skills from section 3. At `full`, also offer `/story-readiness` before code.

Cap `Features` at 7. If there are more, push back and move the cut items to
`Out of scope`. Never invent acceptance criteria the user did not imply: offer
them and let the user change them.

## 5. Next step

End with:

- one line: title, primary `sw-*` agent, first generic skill;
- `Type /next-step to continue.`;
- `Verdict: COMPLETE — software brief written; next stop is code.`

If the user stops before the write, say the brief was not written and lives only
in the conversation.
