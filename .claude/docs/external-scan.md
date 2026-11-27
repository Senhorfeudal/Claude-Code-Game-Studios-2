# External scan — shared protocol

Used by `/spy`, `/brainstorm` and every skill that consumes a concept or brief.
`@spy` is the read-only sector scout. The orchestrating skill owns the question
widget, every file write, and the decision to apply a learning.

## Artifact

`design/external-scan.md` — one scan per project, created by `/brainstorm` on
every run, in both the game and the app/tool branch. Downstream skills read it
instead of re-researching. They spawn `@spy` again only when the file is
missing, the sector changed, or a pending decision needs fresh evidence.

```markdown
# External scan — [sector]

- Project kind: game | app/tool
- Sector: [genre/theme or app category and shape]
- Scanned: [date] — engine/platform/stage: [from project.yaml]
- Decision informed: [what the scan had to inform]

## Sources
| Source | URL | What it shows | Recency | Licence | Evidence strength |
| --- | --- | --- | --- | --- | --- |

## What is different out there
3-6 bullets. Each names the source id and the concrete difference — mechanic,
scope cut, architecture, workflow, pricing, onboarding — not a generic trend.

## Reapplication proposals
| Type | Proposal | Evidence | Confidence | Owner skill/agent | Status | Applied to |
| --- | --- | --- | --- | --- | --- | --- |
```

`Type` is `IMPROVEMENT`, `IMPLEMENTATION` or `FIX`. `Confidence` is `High`,
`Medium` or `Low`. `Status` is `proposed`, `applied` or `declined`; a declined
row keeps its reason in `Applied to`. Never present copied code or assets as a
drop-in: describe the pattern and name where it lives.

## When to scan

- **`/brainstorm`** — mandatory, both branches, after the project-kind gate and
  before any concept question. Brief: engine/platform/stage, sector, and the
  decision to inform. The game branch reads no software reference; the app/tool
  branch reads no game director gate.
- **`/spy`** — direct invocation uses the same protocol and writes nothing.
- **Downstream skills** (`/prototype`, `/start`, `/next-step`, `/map-systems`,
  `/design-system`, `/create-architecture`, `/quick-design`) — read
  `design/external-scan.md` before deciding; use `proposed` rows as inputs. A
  new scan happens only if the file is missing or stale, the sector changed, or
  a decision needs evidence the file does not have. Offer it as an option, never
  as an unasked detour.

## Sector scope

- **Game:** genre, mechanic or theme, platform. Shipped games, prototypes,
  post-mortems, engine samples, repositories and genre pages. Market numbers
  need a source; otherwise say "not researched".
- **App/tool:** category, shape (CLI, app builder, data/internal tool, framework),
  platform. Repositories and their source tree, official docs, changelogs,
  developer write-ups, product sites and app-store listings.
- Prefer the last 12 months and name the recency of each source. Cross-engine
  or cross-platform findings are context, not recommendations. Licence is
  required whenever code or assets would be reused.

## Approval boundary

1. `@spy` returns four parts only: sourced brief, local comparison, typed
   reapplication proposals, and one question with 2-4 options for the
   orchestrator. It writes no file and calls no question tool.
2. The orchestrator asks that question through the widget. Only then does it
   offer the scan for writing: "May I write this to `design/external-scan.md`?"
   This may be the same approval as the brief write, as long as both paths are
   named in the question.
3. Applying a proposal to a brief, GDD, ADR or code follows that document's own
   write approval. Mark the proposal `applied` in that approved write or in a
   separate approved scan update, naming the file changed.
4. `declined` records the reason. No proposal disappears silently.
5. `NOT ASSESSED — NO DATA` is written as the scan verdict with no invented
   sources; the downstream skill proceeds from the user's words and says no
   external reference was found.

## Handoff

`@spy` output → `design/external-scan.md` → concept/brief questions →
downstream skills read proposals → user approves each application → status is
recorded. The scan is evidence, never a decision made on the user's behalf.
