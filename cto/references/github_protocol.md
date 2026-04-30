# Protocolo de operação no GitHub

> Carregue ao ativar `/cto`. Define convenções e templates obrigatórios.

## 1. Pré-condições

Toda operação que toca GitHub exige:

```bash
gh auth status   # exit code 0
```

Se falhar: emitir mensagem `Erro: gh CLI não autenticado. Rode \`gh auth login\`.` e exit code 4. Sem fallback silencioso.

## 2. Labels canônicas

Criar uma vez por repo (idempotente — checar antes de criar):

| Label | Cor (hex) | Descrição |
|---|---|---|
| `feat` | `0e8a16` | Funcionalidade nova |
| `bug` | `d73a4a` | Defeito reportado |
| `chore` | `fef2c0` | Manutenção sem mudança funcional |
| `spike` | `1d76db` | Investigação time-boxed |
| `incident` | `b60205` | Incidente de produção |
| `tech-debt` | `5319e7` | Dívida técnica |
| `adr` | `bfdadc` | Discussão de ADR (raro) |
| `postmortem` | `000000` | Pós-morto |
| `blocked` | `e99695` | Bloqueada por dependência |
| `in-progress` | `fbca04` | Em execução ativa |

Comando para criar (executar uma vez):

```bash
gh label create feat --color 0e8a16 --description "Funcionalidade nova" --force
gh label create bug --color d73a4a --description "Defeito reportado" --force
gh label create chore --color fef2c0 --description "Manutenção sem mudança funcional" --force
gh label create spike --color 1d76db --description "Investigação time-boxed" --force
gh label create incident --color b60205 --description "Incidente de produção" --force
gh label create tech-debt --color 5319e7 --description "Dívida técnica" --force
gh label create adr --color bfdadc --description "Discussão de ADR" --force
gh label create postmortem --color 000000 --description "Pós-morto" --force
gh label create blocked --color e99695 --description "Bloqueada por dependência" --force
gh label create in-progress --color fbca04 --description "Em execução ativa" --force
```

## 3. Template literal — corpo de issue (`feat`/`bug`/`chore`/`spike`/`tech-debt`)

Toda issue criada por `scripts/issue.py open` tem este corpo, com placeholders preenchidos:

```markdown
## Hipótese
{HYPOTHESIS}

## Critério de Aceite
{ACCEPTANCE_LIST}

## Definição de Pronto
{DOD_LIST}

## Dependências
{DEPENDENCIES_LIST_OR_NONE}

## Complexidade
{COMPLEXITY: S | M | L | XL}

## Archetype sugerido
{ARCHETYPE_OR_NONE}

---
Aberta via `/cto` em {ISO_DATE}.
```

## 4. Template literal — corpo de issue (`incident`)

```markdown
## Sumário
{ONE_LINE_SUMMARY}

## Detecção
- Quando: {ISO_DATE}
- Como: {DETECTION_SOURCE}

## Impacto inicial estimado
{IMPACT}

## Status atual
{STATUS}

## Próximas ações
- [ ] {NEXT_ACTION_1}

## Após contenção
- [ ] Gerar pós-morto via `python scripts/postmortem.py --incident {NUMBER}`

---
Aberto como incidente via `/cto` em {ISO_DATE}.
```

## 5. Template literal — descrição de milestone

```markdown
## Escopo
{SCOPE}

## Critério de Release
{RELEASE_CRITERION}

## RACI (Responsible Accountable Consulted Informed)
- **Responsible**: {R}
- **Accountable**: {A}
- **Consulted**: {C_LIST_OR_NONE}
- **Informed**: {I_LIST_OR_NONE}

---
Criado via `/cto` em {ISO_DATE}.
```

## 6. Template literal — pós-morto

Conteúdo gerado por `scripts/postmortem.py --incident N`:

```markdown
# Pós-morto — {ORIGINAL_TITLE}

Linkado ao incidente original #{INCIDENT_NUMBER}.

## Timeline
{AUTO_EXTRACTED_TIMELINE}

## Impacto
- Usuários afetados: {TBD}
- Duração: {DURATION_FROM_TIMELINE}
- Receita / dados / SLA impactados: {TBD}

## Causa Raiz
{TBD — preencher após análise}

## Ação Corretiva (Tomada)
- {TBD — o que estancou o incidente}

## Ação Preventiva (Proposta)
- [ ] ADR-NNNN: {decisão arquitetural para evitar recorrência}
- [ ] Issue chore #NNNN: {ação operacional}

## ADRs Gerados
{LIST_OR_NONE}

---
Gerado via `python scripts/postmortem.py --incident {INCIDENT_NUMBER}` em {ISO_DATE}.
```

## 7. Disciplina de CRUD

| Estado | Ação | Responsabilidade |
|---|---|---|
| Aberta | corpo completo (template §3 ou §4) | `issue.py open` enforça |
| Em andamento | `update` com `--finding` (não edita corpo) | preserva auditoria |
| Bloqueada | aplicar label `blocked`; finding com `Bloqueada por #N: <razão>` | rever em cada session opener |
| Pronta para fechar | exige `--pr <url> --commit <sha>` | `issue.py close` enforça |
| Pós-incidente | gerar `postmortem` via script | rodar antes de arquivar incidente |

## 8. Projects (v2) — board de fluxo

WIP (Work In Progress) limit por desenvolvedor: **2** issues simultâneas. Mais que isso, o briefing do CTO sinaliza warning: `WIP_excedido: <user> com N issues abertas`.

Colunas mínimas:
- `Backlog` (open + sem assignee)
- `Próximo` (open + assignado, sem `in-progress`)
- `Em andamento` (label `in-progress`)
- `Bloqueada` (label `blocked`)
- `Em revisão` (PR aberto linkado)
- `Done` (closed)

## 9. Template de PR

Repo deve ter `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Issue
Closes #{ISSUE_NUMBER}

## Mudança
{ONE_PARAGRAPH}

## Reprodução / Demonstração
{COMANDO ou SCREENSHOT ou TESTE}

## Checklist de revisão
- [ ] Testes passando localmente
- [ ] ADR(s) referenciados estão accepted (ou criados neste PR)
- [ ] Mudança documentada no CHANGELOG (se aplicável)
- [ ] Sem novos `TODO` sem issue `tech-debt` aberta
- [ ] Eval offline rodou e passou (se mexeu em prompt/contrato de LLM)
```

CTO **não** revisa PR profundamente — exige que o checklist esteja completo antes de aprovar.

## 10. Comandos `gh` mais usados (cheat sheet)

```bash
# Detectar repo atual
gh repo view --json nameWithOwner -q .nameWithOwner

# Listar milestones abertos
gh api repos/OWNER/NAME/milestones?state=open --jq '.[] | {number,title,due_on,open_issues,closed_issues}'

# Listar issues em andamento
gh issue list --label in-progress --state open --json number,title,labels,assignees,milestone,updatedAt

# Criar milestone
gh api repos/OWNER/NAME/milestones -f title="..." -f description="..." -f due_on="2026-05-15T00:00:00Z"

# Criar issue
gh issue create --title "..." --body "..." --label feat --milestone N

# Comentar em issue
gh issue comment N --body "..."

# Fechar issue
gh issue close N

# Visualizar issue completa (corpo + comments)
gh issue view N --json body,comments
```
