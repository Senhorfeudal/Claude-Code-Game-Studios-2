# Relatório do port para OpenCode V2

**Data:** 2026-11-26  
**Repositório:** `Senhorfeudal/Claude-Code-Game-Studios-2`  
**Workspace:** `/root/projects/Home`  
**Base upstream preservada:** `43e1952` (`fix(agents): return questions to the orchestrator across all roles`)

## 1. Objetivo

Tornar o template Senhorfeudal Game Studios operacional no OpenCode V2 sem
modificar a fonte de verdade Claude Code (`.claude/`), e testar as 80 skills de
forma headless para encontrar falhas reais de portabilidade.

A estratégia foi adicionar uma camada adaptadora em `.opencode/`: wrappers de
skills, slash commands, subagents, configuração de permissões e um plugin que
faz a ponte dos validators bash existentes. O `CLAUDE.md` original foi mantido;
`AGENTS.md` é a versão das instruções para OpenCode.

## 2. O que foi implementado

| Área | Arquivos | Finalidade |
| --- | --- | --- |
| Instruções | `AGENTS.md`, `.opencode/OPENCODE-PORT.md` | Regras do projeto no formato OpenCode e documentação completa do mapeamento. |
| Configuração | `.opencode/opencode.jsonc` | `instructions`, plugins, watcher e permissões traduzidas de `.claude/settings.json` (bloqueios de `rm -rf`, force push, `.env`, assets binários etc.). |
| Skills | `.opencode/skills/<id>/SKILL.md` (80) | Wrappers que preservam `name`/`description`/`autoinvoke` e instruem o modelo a ler o `SKILL.md` original e seus `references/`. |
| Comandos | `.opencode/commands/<id>.md` (80) | `/prototype`, `/start`, `/skill-test`, … — cada comando carrega a skill correspondente e repassa `$ARGUMENTS`. |
| Agents | `.opencode/agents/<id>.md` (90: 52 jogo + 38 software, incluindo `web-android-specialist`) | `mode: subagent`, `steps` a partir de `maxTurns`, permissões derivadas de `tools`/`disallowedTools` e nota sobre o tier original. |
| Hooks | `.opencode/plugins/ccgs-bridge/index.js` | Encaminha `validate-commit.sh`, `validate-push.sh`, `validate-write.sh`, `validate-registry.sh`, `validate-assets.sh` e `validate-skill-change.sh` para os hooks de ferramenta do OpenCode, com fail-open. |
| Question fallback | `plugins/question-watchdog/index.ts` | Plugin já existente no upstream, agora ativado pela config do projeto. |
| Ferramentas | `.opencode/scripts/generate-opencode-layer.py`, `.opencode/scripts/verify-port.py` | Regeneração determinística da camada e verificação de arquivos + API + ativação de skill. |
| Documentação | `README.md`, `CHANGELOG.md`, este relatório | README apresenta o repositório como port para OpenCode V2 (com Claude Code como compatibilidade) e linka os detalhes. |

Os 80 `SKILL.md` upstream não foram alterados: o wrapper apenas delega para
eles. Assim, correções no template Claude Code continuam valendo para os dois
runtimes após rodar o gerador.

## 3. Traduções de runtime

| Construto do Claude Code | Equivalente no OpenCode V2 |
| --- | --- |
| `AskUserQuestion` | ferramenta `question` (com fallback imediato para texto numerado se o widget falhar) |
| `Agent` / `Task` | ferramenta `subagent`, com os IDs de `.opencode/agents/` |
| `Bash` | `shell` |
| `Write` / `Edit` | `write` / `edit` |
| `WebFetch` / `WebSearch` | `webfetch` / `websearch` |
| `TaskCreate` / `TaskUpdate` | `todowrite` quando disponível, senão texto |
| `!`…`` em frontmatter | instrução para executar o comando com `shell` (o OpenCode não expande) |
| `${CLAUDE_SKILL_DIR}` / `${CLAUDE_PROJECT_DIR}` | `.claude/skills/<id>` / raiz do workspace |
| `$ARGUMENTS` | argumentos do slash command |
| `allowed-tools`, `user-invocable`, `model`, `maxTurns` | `permissions`, `metadata.opencode/autoinvoke`, modelo da sessão, `steps` |
| `disable-model-invocation: true` | `opencode/autoinvoke: false` (8 skills continuam acessíveis só por comando) |

## 4. Falhas encontradas e corrigidas

1. **`disable-model-invocation` não era convertido.** O gerador comparava o valor
   com `True` do Python, mas o frontmatter traz a string `true`. Resultado: 8
   skills (`changelog`, `day-one-patch`, `dev-story`, `help`, `hotfix`,
   `launch-checklist`, `settings`, `story-done`) ficavam com
   `autoinvoke: true`. Corrigido pela comparação textual; `verify-port.py`
   agora confirma as 8 flags.
2. **Caminhos de plugin resolvidos a partir da pasta errada.** O OpenCode resolve
   paths relativos em relação a `.opencode/`, não à raiz. `./plugins/...`
   apontava para `.opencode/.opencode/plugins/...` e os plugins falhavam ao
   carregar (`ENOENT` no log). Corrigido para `../plugins/question-watchdog` e
   `./plugins/ccgs-bridge`; ambos aparecem como `active` em `/api/plugin`.
3. **Formato errado na API de comandos.** O verificador esperava `id`, mas
   `/api/command` retorna `name`. Isso causava um `KeyError` e abortava a
   verificação. Corrigido para aceitar `name` ou `id`.

## 5. Verificação

| Verificação | Comando | Resultado |
| --- | --- | --- |
| Port end-to-end | `python3 .opencode/scripts/verify-port.py` | **10/10 PASS** |
| Descoberta via API | incluído no verificador | 80/80 skills, 80/80 commands, 90/90 agents |
| Wrapper prevalece sobre o fallback `.claude/skills` | incluído no verificador | `PASS` para `skill-test` |
| Plugins carregados | `/api/plugin` | `ccgs-bridge` e `question-watchdog` `active` |
| Ativação de skill em sessão | `/api/experimental/session/{id}/skill` | HTTP `204`, incluindo aliases ocultos (`changelog`, `story-done`) |
| Linter estático das skills | `bash .claude/scripts/skill-lint.sh all --root .` | 80 skills × 7 checks processados, sem falha dura |
| Suíte original Python | `python3 -m unittest discover -s tests -p 'test_*.py'` (venv com `tests/requirements.txt`) | **109 testes OK** |
| Sintaxe dos hooks | `find .claude -name '*.sh' -print0 \| xargs -0 -n 1 bash -n` | OK |
| Smoke dos validators | payloads de exemplo para `validate-commit.sh` e `validate-write.sh` | exit `0` |
| Verificação de agents | `bash .claude/scripts/agent-check.sh .` | concluído sem erro |
| Invocação real de `skill-test` | `opencode2 run ...` | Skill carregada; geração final **NOT ASSESSED** — cota do modelo gratuito esgotada |

### Sobre as 17 observações estruturais do linter

O linter sinalizou 17 skills com combinações incomuns, todas esperadas pelo
desenho do framework e nenhuma com falha nos checks automáticos:

- `phases<2` / `no-verdict`: aliases de uma linha (`help`, `settings`, `changelog`,
  `next-step`, `project-stage-detect`, `project-settings`) e os 9 orquestradores
  `team-*`, que executam papéis em fases inline em vez de terem fases próprias
  (ver § 5b).
- `write-without-ask`: `balance-check` e `consistency-check` pedem confirmação
  com `AskUserQuestion` em linguagem diferente do literal `May I write`.

Elas estão registradas aqui para não serem confundidas com regressões do port.

### 5b. Teams no mesmo chat

Os nove skills `team-*` deixaram de encaminhar especialistas para conversas de
subagentes e passaram a ser orquestradores executados na conversa do usuário.
Isso corrige o loop observado no mobile: um team dentro de um subagent não tem
widget de pergunta e só consegue devolver a decisão pendente ao pai, que precisa
reabrir a conversa — o usuário vê a sessão "em execução" sem nenhuma pergunta.

Regras aplicadas (`.claude/docs/in-chat-teams.md`):

- `Agent` / `subagent` removido de `allowed-tools` dos 9 teams; nenhum time ou
  papel é spawnado.
- Cada fase lê `.claude/agents/<id>.md` e é executada inline; fases marcadas como
  paralelas viram passes consecutivos com saídas distintas.
- Toda decisão e toda autorização de escrita usam `AskUserQuestion` no chat
  atual; se o skill rodar dentro de um subagent, ele para e pede para ser
  carregado no chat principal.
- Não há mais "bounded exception" de escrita para subagentes: o orquestrador
  mostra o rascunho/conjunto de arquivos, pergunta "May I write this to [path]?"
  e só escreve após o sim.

`/next-step` recebeu um branch explícito para ações `/team-*`: pergunta "Run
`/team-X` here, in this chat?", carrega o skill no chat atual com `skill` e só
usa crews para ações não-team. O gerador emite essa regra nos 9 wrappers.

Evidências: `tests/test_in_chat_teams.py` (novo), atualizações em
`tests/test_next_step_routing.py`, specs em `studio-tests/skills/team/` e
`studio-tests/skills/utility/next-step.md`; suíte Python 109 testes OK.

### 5c. Branch software no `/brainstorm`

O commit `96d0252` separou o fluxo em dois caminhos. `/brainstorm` pergunta
primeiro se a ideia é um **jogo** ou um **aplicativo/ferramenta**. No ramo
software, ele carrega `.claude/skills/brainstorm/references/software-concept.md`,
escreve `design/software-brief.md`, escolhe um dos 38 papéis `sw-*` listados em
`docs/software-agents.md` e usa skills genéricas de software — sem gates de
diretor de jogo nem `game-concept.md`. Os 38 papéis foram portados como os
demais agents, elevando o total para 90. Evidências: 38 specs em
`studio-tests/agents/software/`, `studio-tests/skills/utility/brainstorm.md` e
`docs/software-agents.md`/`.json`; `verify-port.py` conta os agents de forma
dinâmica.

### 5d. Scan externo compartilhado

`@spy` passou a espião de setor (jogos e software). `/brainstorm` roda um scan
obrigatório nos dois ramos e grava `design/external-scan.md` na mesma aprovação
do brief; `/prototype`, `/start`, `/next-step`, `/map-systems` e `/design-system`
leem o arquivo e só pedem um novo scan quando ele está ausente/desatualizado ou
quando uma decisão precisa de evidência nova. Cada proposta de reaplicação passa
pelo "May I write" do documento dono; o agente permanece read-only e sem
ferramenta de pergunta. Protocolo em `.claude/docs/external-scan.md`; guardrails
em `tests/test_spy_agent.py` e nos specs de spy/brainstorm/downstream.

## 6. Lacunas conhecidas

1. Hooks de ciclo de vida do Claude Code (`session-start`, `detect-gaps`,
   `session-stop`, `pre-compact`, auditoria de agent) e `statusLine` não têm
   equivalente neste port.
2. Blocos `!`…`` são instruções para o modelo, não injeção automática de prompt;
   se uma skill assume config pré-carregada, o modelo precisa executar o comando.
3. Tiers `opus`/`sonnet`/`haiku` viram herança do modelo da sessão (nesta
   instalação só o provider `opencode` está disponível). `memory: project`,
   `isolation: worktree` e `skills:` pré-carregados dos agents são notas, não
   recursos enforcementados pelo runtime.
4. Dois testes Python do upstream leem
   `/root/.oc-opencode2/config/opencode/opencode.jsonc` (config global do app
   mobile), não o `.opencode/opencode.jsonc` deste projeto; foram tratados
   separadamente na interpretação dos resultados.
5. Um build completo de jogo (`/prototype`) ainda depende de uma sessão com
   cota de modelo disponível; apenas o carregamento da skill foi confirmado.

## 7. Como validar novamente

```bash
cd /root/projects/Home

# Regenerar a camada depois de editar .claude/skills ou .claude/agents
python3 .opencode/scripts/generate-opencode-layer.py

# Verificação principal (arquivos + API + ativação)
python3 .opencode/scripts/verify-port.py

# Checagens upstream
bash .claude/scripts/skill-lint.sh all --root .
bash .claude/scripts/agent-check.sh .
bash .claude/scripts/compat-inventory.sh .

# Suíte Python (usa o venv criado em /tmp/opencode/venv)
/tmp/opencode/venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

No app, `/skill-test static all` executa o modo estático das 80 skills e
`/prototype` inicia o fluxo de criação de jogo já com os nomes de ferramentas
traduzidos.

## 8. Histórico e publicação

O histórico Git upstream foi preservado a partir de `43e1952`; o remote
`origin` aponta para `https://github.com/Senhorfeudal/Claude-Code-Game-Studios-2.git`.
As mudanças deste port foram adicionadas em commits sobre esse histórico,
mantendo `CLAUDE.md`, `.claude/` e os testes originais intactos. O commit
`1528ac7` converteu os nove teams para execução no chat do usuário e o
`96d0252` uniu os 38 agentes de software (89 no total).
A descrição e os topics do GitHub também foram atualizados para destacar o port
(`opencode`, `opencode-v2`), mantendo `claude-code` como compatibilidade.

A camada também foi instalada de forma global em `$OPENCODE_CONFIG_DIR`
(`/root/.oc-opencode2/config/opencode/`): 80 skills completas (com `references/`),
80 commands, 90 agents, plugins, instruções e permissões, todos copiados do
repositório (sem symlink). A verificação em `/tmp/opencode/global-check`
confirmou 80/80 skills, 80/80 commands, 90/90 agents, 2/2 plugins ativos e
ativação de `skill-test` com HTTP 204. Dentro deste repositório, a camada local
`.opencode/` continua tendo precedência sobre a cópia global.
