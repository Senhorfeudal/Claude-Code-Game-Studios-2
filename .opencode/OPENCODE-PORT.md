# OpenCode port notes

This repository is the Senhorfeudal Game Studios template (90 agents — 52 game + 38 software — and 80 skills)
with a native OpenCode V2 layer. The upstream Claude Code files are kept intact
under `.claude/`; the generated layer lives under `.opencode/` and is produced by
`.opencode/scripts/generate-opencode-layer.py`.

## Layout

| Source (Claude Code) | OpenCode V2 |
| --- | --- |
| `CLAUDE.md` | `AGENTS.md` (project instructions) |
| `.claude/skills/<id>/SKILL.md` | `.opencode/skills/<id>/SKILL.md` wrapper (wins by ID) + `.claude/skills` compatibility fallback |
| Skill slash commands | `.opencode/commands/<id>.md` (`/prototype`, `/skill-test`, …) |
| `.claude/agents/<id>.md` | `.opencode/agents/<id>.md` with `mode: subagent` |
| `.claude/settings.json` permissions | `permissions` in `.opencode/opencode.jsonc` |
| `.claude/hooks/*.sh` validators | `.opencode/plugins/ccgs-bridge/index.js` (tool hooks) |
| Optional question watchdog | `plugins/question-watchdog/index.ts` loaded from config |
| `project.yaml` | unchanged — framework behaviour config, not OpenCode config |

Regenerate the layer after editing upstream skills or agents:

```bash
python3 .opencode/scripts/generate-opencode-layer.py
```

## Runtime translations

- **Skill invocation.** OpenCode lists only the skill ID, name and description at
  each model step. The model loads one with the `skill` tool; the wrapper then
  instructs it to read the full upstream `SKILL.md` and its `references/`.
- **`!`…`` preloads.** Claude Code expands inline shell blocks before a skill
  runs. OpenCode does not. The wrapper tells the model to run them with the
  `shell` tool. Most are:
  `bash .claude/hooks/yaml-helper.sh resolve_config --keys …`
- **Tool names.** `AskUserQuestion` → `question`; `Agent`/`Task` → `subagent`;
  `Bash` → `shell`; `Write`/`Edit` → `write`/`edit`; `WebFetch`/`WebSearch` →
  `webfetch`/`websearch`; `TaskCreate`/`TaskUpdate` → `todowrite` if available.
- **Frontmatter.** `allowed-tools`, `user-invocable`, `argument-hint`, `model`
  tiers and `maxTurns` are Claude Code metadata. OpenCode uses `permissions`,
  `metadata.opencode/autoinvoke`, command arguments and `steps`. Eight skills
  that set `disable-model-invocation: true` keep that behaviour through
  `opencode/autoinvoke: false` while remaining available as slash commands.
- **In-chat teams.** All nine `/team-*` skills are orchestrators that run in the
  user's current conversation. They never use `Agent`/`subagent` for themselves
  or for a specialist: each phase is an inline pass reading
  `.claude/agents/<id>.md`, and every decision/write approval uses the `question`
  tool in that same chat. `/next-step` loads a chosen team here; it only routes
  non-team actions to a crew. See `.claude/docs/in-chat-teams.md`. Generated team
  wrappers repeat this rule.
- **Software branch.** `/brainstorm` first asks game vs app/tool. The app/tool
  branch loads `references/software-concept.md`, writes `design/software-brief.md`
  and selects one of the 38 `sw-*` roles from `docs/software-agents.md`; it never
  loads game director gates. Those roles are ported like any other agent.
- **Agents.** All 90 (52 game + 38 software) are subagents with permissions derived from their original
  `tools`/`disallowedTools`. Every agent carries the shared "Error-Prevention Rules"
  contract (`UNVERIFIED`, `NOT ASSESSED`, no silent guesses, no writes before approval). Agents with the “Question Delivery (all runtimes)”
  clause also get a `question` deny rule. `model: opus|sonnet|haiku` becomes an
  inherited session model; the tier is preserved as a note in each agent body.
  `memory: project`, `isolation: worktree` and preloaded `skills:` are notes,
  not enforced runtime features.
- **`@path` imports** in upstream docs are not expanded by OpenCode; read the
  referenced file with `read` when a skill asks for it.

## Hooks bridge

`ccgs-bridge` forwards Claude Code hook payloads to the bash scripts:

| OpenCode hook | Scripts |
| --- | --- |
| `tool.execute.before` on shell commands mentioning git/release | `validate-commit.sh`, `validate-push.sh` (exit 2 blocks) |
| `tool.execute.before` on write/edit | `validate-write.sh`, `validate-registry.sh` (advisory) |
| `tool.execute.after` on write/edit | `validate-assets.sh`, `validate-skill-change.sh` (advisory) |

Advisory output goes to the server log. The bridge fails open: a missing bash,
timeout or script error never blocks work. Hard safety remains in the OpenCode
permission rules.

## Global installation

The same layer is also copied into the OpenCode user config directory, so it is
available in every project, not only in this repository. On this device the
effective directory is `$OPENCODE_CONFIG_DIR`
(`/root/.oc-opencode2/config/opencode/`):

```text
/root/.oc-opencode2/config/opencode/
├── opencode.jsonc          # permissions, instructions, plugins, watcher
├── skills/                 # 80 upstream skills, including references/
├── commands/               # 80 slash commands
├── agents/                 # 51 subagents
├── plugins/                # ccgs-bridge + question-watchdog
├── instructions/           # copies of this note and the full report
└── .claude/                # validators and helper scripts used by the bridge
```

It is a copy, not a symlink: the project layer in `/root/projects/Home` still
wins inside this repo, while other projects use the global copy. Re-copy after
changing upstream skills or agents.

## Known gaps (not silently ignored)

1. Claude Code session lifecycle hooks (`session-start`, `detect-gaps`,
   `session-stop`, `pre-compact`, agent audit trail) and `statusLine` have no
   OpenCode equivalent in this port.
2. `!`…`` expansions are instructions, not automatic prompt injection. If a
   skill assumes the config was preloaded without running the command, the model
   must run it explicitly.
3. Agent model tiers are flattened to the session model on this installation
   (only the `opencode` provider is configured here).
4. Upstream Python tests that hardcode
   `/root/.oc-opencode2/config/opencode/opencode.jsonc` test the mobile app's
   global config, not this project's `.opencode/opencode.jsonc`; treat those
   results separately from the project verification.
5. The port was verified structurally and through the OpenCode API. A full
   end-to-end game build (`/prototype`) still needs a real play session.

## Verification

```bash
# Structural linter shipped with the framework (80 upstream skills)
bash .claude/scripts/skill-lint.sh all --root .

# Other upstream read-only checks
bash .claude/scripts/agent-check.sh .
bash .claude/scripts/compat-inventory.sh .

# OpenCode layer: files, discovery API and a skill-activation smoke test
python3 .opencode/scripts/verify-port.py

# Upstream Python suite (needs PyYAML from tests/requirements.txt)
python3 -m unittest discover -s tests -p 'test_*.py'
```

`verify-port.py` uses the running OpenCode service credentials from the
environment. If the service is unavailable it reports `NOT ASSESSED` for API
checks rather than claiming a pass.
