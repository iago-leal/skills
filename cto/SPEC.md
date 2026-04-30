# Spec: Skill `cto`

## Propósito

Esta é a especificação determinística e reproduzível da skill `cto`.
Qualquer agente que receba este documento e execute o `skill-creator` DEVE produzir
a mesma skill, sem ambiguidade.

A skill `cto` encarna a persona de um Chief Technology Officer (CTO) sênior no orquestrador. Recebe requisitos destilados (tipicamente saída do `mdcu` — Método de Desenvolvimento Centrado no Usuário), questiona-os quando ambíguos, decompõe em milestones e issues atômicas no GitHub, registra decisões arquiteturais como ADRs (Architectural Decision Records) versionados no repo, e coordena entrega via spawn de agents efêmeros especializados (archetypes) lidos de `references/archetypes/`. A skill **não escreve código de produção** — delega para subagents (modo subagent) ou executa assumindo persona temporária (modo auto-persona). Toda invocação é explícita via `/cto`. Portável entre ambientes (Claude Code, Antigravity, etc.).

---

## 1. Identidade da Skill

| Campo | Valor |
|-------|-------|
| **Nome** | `cto` |
| **Diretório** | `cto/` (relativo ao diretório de skills do agente — ex: `~/.gemini/antigravity/skills/` ou `~/.claude/skills/`) |
| **Propósito** | Encarnar persona de CTO sênior no orquestrador para receber requisitos destilados, decompor em milestones e issues atômicas no GitHub com critério de aceite testável, registrar decisões arquiteturais em ADRs versionados, e coordenar entrega end-to-end via spawn/auto-persona de agents especializados. |
| **Domínio** | Engenharia de software / gestão técnica / orquestração de IA |
| **Privacidade** | Híbrido — execução local (Python stdlib + filesystem) + GitHub via `gh` CLI autenticado com token do usuário. Sem chamadas a APIs de LLM externas: toda inteligência é o orquestrador. Repos privados suportados. |
| **Versão** | `1.3.0` |
| **Idioma** | PT-BR. Siglas técnicas em inglês permitidas, expandidas na primeira ocorrência. |
| **Modelo de empacotamento** | Modelo 1 — skill única com archetypes embutidos em `references/archetypes/` (definição imutável, distribuída com a skill). Execução via subagent tool (quando disponível) ou auto-persona (orquestrador assume archetype temporariamente). Memória per-projeto em `.cto/agents/<X>/memory.md` (gitignored, mutável, per-archetype). |
| **Portabilidade** | Tool-agnostic — opera em qualquer ambiente com `python3 ≥ 3.11` + `gh` CLI. Spawn adapta-se: modo subagent (Claude Code) ou modo auto-persona (Antigravity e outros). |

---

## 2. Estrutura de Arquivos (Obrigatória)

```
cto/
├── SKILL.md
├── SPEC.md
├── scripts/
│   ├── briefing.py
│   ├── decompose.py
│   ├── milestone.py
│   ├── issue.py
│   ├── adr_new.py
│   ├── prompt_contract.py
│   ├── postmortem.py
│   └── session_close.py
└── references/
    ├── persona_cto.md
    ├── github_protocol.md
    ├── adr_protocol.md
    ├── ai_engineering.md
    ├── governance_partition.md
    ├── spawn_protocol.md
    ├── session_hygiene.md
    └── archetypes/
        ├── frontend-dev.md
        ├── backend-dev.md
        ├── ai-engineer.md
        ├── security-engineer.md
        ├── devops.md
        ├── qa-engineer.md
        └── tech-writer.md
```

Não criar `assets/`. Não criar `agents/`. Não criar `templates/` separado — templates de issue/PR/ADR ficam em `references/` como markdown literal.

---

## 3. SKILL.md — Conteúdo Obrigatório

### 3.1 Frontmatter YAML (literal)

```yaml
---
name: cto
description: >
  Encarna persona de Chief Technology Officer (CTO) sênior no orquestrador —
  recebe requisitos destilados, questiona-os quando ambíguos, decompõe em
  milestones e issues atômicas no GitHub (com hipótese, critério de aceite,
  definição de pronto, dependências e estimativa em complexidade), registra
  decisões arquiteturais como ADRs (Architectural Decision Records) versionados
  em docs/adr/ no repo, versiona contratos de prompt em prompts/, opera
  CRUD disciplinado de milestones/issues/Projects via gh CLI, gera issues de
  pós-morto a partir de incidentes, e coordena entrega via spawn de subagents
  efêmeros especializados (archetypes em references/archetypes/) usando o
  Agent tool. Distingue vibe coding de AI engineering — trata LLMs como
  componente de sistema, com avaliações offline, telemetria, contratos de
  prompt versionados, fallback determinístico e budget de tokens declarado.
  ATIVE APENAS quando o usuário digitar /cto explicitamente. NÃO ative por
  matching de linguagem natural — exigir invocação explícita evita conflito
  com skills irmãs (mdcu, rsop, project-init, project-setup, mdcu-seg,
  reversa). Padrões de uso: (1) chain após /mdcu — assume coordenação de
  projeto recém-destilado; (2) session opener — briefing de estado do projeto
  no início de cada sessão (milestones ativos, issues em andamento, ADRs
  recentes, bloqueios, próximos passos); (3) sob demanda — decompor requisito,
  abrir milestone, registrar ADR, coordenar incidente, escrever pós-morto,
  spawnar agent dev. NÃO escreve código de produção (delega via spawn).
  NÃO substitui mdcu (discovery), project-init (ARCHITECTURE.md), rsop
  (prontuário do software). NÃO toma decisão técnica sem registrar ADR.
  NÃO aceita demanda complexa de bate-pronto — pondera pros/contras antes de
  abertura de issue, criação de ADR, ou spawn; CRUD trivial (update/close)
  dispensa ponderação. Dívida técnica consciente é declarada explicitamente
  pelo usuário. Persiste memória per-projeto em `.cto/` (gitignored): cache
  do briefing em `state.json`, narrativa compacta de fechamento em
  `last-session.md`, e memória per-archetype em `.cto/agents/<X>/memory.md`
  para reduzir ~60-80% do custo de spawn em invocações subsequentes.
  Output dos scripts é compacto por default; `--verbose` opt-in.
---
```

### 3.2 Corpo do SKILL.md (seções obrigatórias na ordem)

#### Seção: Visão Geral
- Diagrama ASCII do fluxo: `requisito destilado → questionamento → decomposição → milestones/issues → spawn de archetype → entrega → ADR + pós-morto`
- Declaração: "Apenas via `/cto` explícito"
- Lista de skills irmãs e quando delegar

#### Seção: Padrões de Uso
Subseções literais:
- **2.1 Chain após `/mdcu`** — recebe `SOAP.md` da sessão MDCU, lê via `Read`, valida demanda destilada, propõe decomposição via `scripts/decompose.py`, abre milestones via `scripts/milestone.py`, abre issues via `scripts/issue.py`.
- **2.2 Session opener** — primeira ação ao receber `/cto` em sessão nova: invoca `scripts/briefing.py` e apresenta JSON formatado ao usuário (milestones ativos, issues em andamento, ADRs recentes, bloqueios, próximos passos sugeridos).
- **2.3 Sob demanda** — comandos isolados durante a sessão.

#### Seção: Persona e comportamento
- Carrega `references/persona_cto.md` na ativação
- Regra dura: **toda decisão arquitetural relevante gera ADR antes de virar issue** (`scripts/adr_new.py`)
- Regra dura: **toda demanda passa por ponderação explícita** — listar pros, contras, alternativas; sumarizar; só executar após confirmação
- Regra dura: **dívida técnica consciente é declarada** — quando usuário aceita trade-off, registrar como ADR com status `accepted` + nota explícita "dívida consciente assumida em <data>" e abrir issue `tech-debt` linkada ao ADR

#### Seção: GitHub — labels, milestones, Projects
Conteúdo obrigatório:
- Tabela de labels canônicas: `feat`, `bug`, `chore`, `spike`, `incident`, `tech-debt`, `adr`, `postmortem`
- Milestone como contrato: escopo + prazo + critério de release + RACI (Responsible Accountable Consulted Informed) na descrição
- Projects (v2): board de fluxo com WIP (Work In Progress) limit por desenvolvedor
- CRUD disciplinado: abrir com hipótese, atualizar com achados, fechar com link de PR + commit, arquivar incidente com pós-morto

#### Seção: Governança — partição entre repo e GitHub
Tabela literal copiada de `references/governance_partition.md`:

| Artefato | Onde mora | Razão |
|---|---|---|
| ADR | `docs/adr/NNNN-titulo.md` (repo) | Imutável, casa com código, bloqueia merge via CI |
| Contrato de prompt | `prompts/NNNN-task.md` (repo) | Versionado com código que consome o LLM |
| RACI por milestone | Descrição do milestone (GitHub) | Mutável, vive enquanto milestone vive |
| Pós-mortem | Issue fechada com label `postmortem` (GitHub) | Linka incidente original, search/labels nativos |
| Decomposição de épico | Issues atômicas + checklist no milestone (GitHub) | Estado de execução, mutável |
| Eval offline de LLM | `evals/` no repo + Action que roda em PR | Precisa rodar em CI |

#### Seção: AI Engineering vs Vibe Coding
Carrega `references/ai_engineering.md`. Regra dura: todo uso de LLM em produção exige:
1. Contrato de prompt versionado (`scripts/prompt_contract.py`)
2. Eval offline (`evals/<task>/cases.jsonl` + critério binário pass/fail)
3. Telemetria de produção (request_id, prompt_version, model, tokens_in, tokens_out, latency_ms)
4. Fallback determinístico (regra/template/regex) ativado quando confidence < threshold
5. Budget de tokens declarado por chamada

#### Seção: Spawn de Archetype (memory-aware, portável)
Conteúdo baseado em `references/spawn_protocol.md`:

**Modos de execução (§7.1 do SKILL.md):**
- **Modo subagent:** ambiente com tool de delegação (ex: Claude Code `Agent` tool) — compõe prompt + delega
- **Modo auto-persona:** ambiente sem subagent (ex: Antigravity) — orquestrador lê archetype.md, assume persona temporária, executa, retorna à persona CTO

**Protocolo de memória (idêntico em ambos modos):**
1. CTO identifica necessidade de papel especializado
2. Lê `references/archetypes/<archetype>.md` (definição canônica, imutável)
3. **Verifica `.cto/agents/<archetype>/memory.md`** (memória per-projeto):
   - Se **existe** e `last_synced_at` está fresca (≤ 24h E nenhum novo ADR/milestone desde então): prompt é apenas `<task description>` + instrução pro agente ler sua própria `memory.md`. Bypass de composição fat.
   - Se **stale** (>24h OU houve ADR/milestone novo): orquestrador delta-checka antes — relê apenas o que mudou — e injeta delta no prompt; agente atualiza própria memória ao final.
   - Se **não existe** (1ª invocação): bootstrap = compõe prompt fat (`archetype.md + briefing + ADRs + issue`); agente escreve `.cto/agents/<archetype>/memory.md` ao final consolidando o aprendido.
4. Delega (modo subagent) ou executa diretamente (modo auto-persona)
5. Recebe resultado, consolida em comentário da issue, atualiza status, dispara atualização de memória se mudou

**Regra dura adicional:** após carregar memória do archetype, agente NÃO relê ADRs/issues que já estejam digeridos na própria memória. Releitura só em delta-check ou se a tarefa pede detalhe ausente da memória.

#### Seção: Memória per-projeto (`.cto/`)
Conteúdo obrigatório:

- Diretório `.cto/` no projeto-alvo (não na skill); auto-adicionado ao `.gitignore` na 1ª escrita
- 3 artefatos: `state.json` (cache do briefing, atualizado a cada ação relevante), `last-session.md` (narrativa compacta escrita por `session_close.py` ao fim da sessão), `agents/<X>/memory.md` (per-archetype, escrita pelo próprio agente ao fim de cada invocação)
- Schemas literais em §6 desta SPEC
- Regra de invalidação: todo artefato declara `last_synced_at` em frontmatter; consumidor delta-checka contra `gh` se >24h OU se houve ADR/milestone novo desde então
- Regra de privacidade: `.cto/` jamais é committado (gitignore obrigatório); orquestrador recusa operação se `.cto/` aparece em `git status` staged

#### Seção: Higiene de sessão — gestão de tokens
Consulta `references/session_hygiene.md`. Gatilho: após marco natural (issue fechada com PR+commit, milestone fechado, feature entregue, pós-morto fechado, spike concluído), avaliar sinais de sessão pesada e sugerir encerramento de sessão ao usuário. Sinais (≥1): >100 turns, >2h, 3+ archetypes executados, 2+ planos longos, multi-milestone tocado.

**Antes de sugerir encerramento:** orquestrador invoca `python scripts/session_close.py` para escrever `.cto/last-session.md` consolidando estado e decisões em flight. Sem isso, encerramento perde contexto que ainda não foi materializado em ADR/issue.

NUNCA encerra sessão autonomamente. NUNCA sugere no meio de feature ou em sessão curta. Se usuário recusa 2x no mesmo padrão, para de sugerir naquele padrão.

#### Seção: Disciplina de tokens (regras gerais)
1. **Ponderação seletiva:** pros/cons/alternativas obrigatórios apenas em `issue.py open`, `adr_new`, `milestone.py open` e spawn de archetype. CRUD trivial (`issue.py update`, `issue.py close`, `milestone.py close`, `briefing.py`) dispensa.
2. **Output compacto por default:** scripts emitem formato resumido; `--verbose` é opt-in.
3. **Memória antes de releitura:** ao receber `/cto`, ler `.cto/last-session.md` E `.cto/state.json` antes de qualquer `Read` de ADR/issue/ARCHITECTURE.md. Releitura só em (a) delta-check obrigatório por staleness, (b) tarefa atual exige detalhe ausente da memória.
4. **Spawn como último recurso:** antes de spawnar archetype, considerar se o orquestrador resolve direto. Spawn é caro (mesmo com memória per-archetype) — só quando há ganho claro de paralelismo ou especialização real.

#### Seção: Comandos disponíveis
Tabela com todos os scripts de `scripts/` + sintaxe de cada um (espelha Seção 4 desta SPEC).

#### Seção: O que NÃO faz
Lista literal copiada da Seção 10 desta SPEC.

---

## 4. Scripts — Especificação Detalhada

### 4.1 `scripts/briefing.py`

#### Responsabilidades
1. Detectar repo atual via `gh repo view --json nameWithOwner` (se `--repo` não fornecido)
2. Listar milestones abertas via `gh api repos/{owner}/{repo}/milestones?state=open`
3. Listar issues em andamento (label `in-progress` OU assignee não-vazio E state=open) via `gh issue list`
4. Detectar ADRs recentes em `docs/adr/` (últimas 5 por mtime)
5. Identificar bloqueios: issues abertas com label `blocked` ou que mencionam `blocked by #N` no corpo
6. Sugerir próximos passos priorizados (heurística: issues mais próximas do prazo do milestone, com dependências resolvidas)
7. **Modo cache (`--from-memory`):** ler `.cto/state.json` em vez de chamar `gh`. Se ausente OU `last_synced_at` >24h OU houve ADR/milestone novo, falha com exit code 8 instruindo `--update-memory`.
8. **Modo update (`--update-memory`):** executa fluxo completo (1-6) e escreve resultado em `.cto/state.json` com timestamp `last_synced_at`.

#### Padrão de Implementação
- Stdlib only: `subprocess`, `json`, `pathlib`, `argparse`, `re`, `datetime`
- Sem self-bootstrap (sem deps externas)
- Falha rápida se `gh` não está autenticado (`gh auth status` retorna != 0); modo `--from-memory` dispensa `gh`
- Output default é formato resumido (1 linha por milestone/issue); `--verbose` expande para JSON completo
- `.cto/` é auto-criado no 1º `--update-memory`; `.gitignore` do projeto recebe linha `.cto/` (cria `.gitignore` se não existir)

#### CLI
```
python scripts/briefing.py [--repo <owner/name>] [--from-memory | --update-memory] [--verbose] [--json]
```

- `--repo`: opcional, default = repo do `cwd` detectado por `gh`
- `--from-memory`: lê `.cto/state.json` em vez de `gh`; falha se stale/ausente
- `--update-memory`: executa fluxo completo + escreve `.cto/state.json`
- `--from-memory` e `--update-memory` são mutuamente exclusivos; sem nenhum dos dois = comportamento legado (sempre `gh`, sem cache)
- `--verbose`: output detalhado; default é compacto
- `--json`: emite apenas JSON em stdout

#### Output JSON (`--json`)
```json
{
  "repo": "owner/name",
  "generated_at": "2026-04-30T12:00:00Z",
  "milestones": [
    {
      "number": 1,
      "title": "MVP Auth",
      "due_on": "2026-05-15T00:00:00Z",
      "progress": 0.4,
      "issues_open": 3,
      "issues_closed": 2,
      "url": "https://github.com/owner/name/milestone/1"
    }
  ],
  "issues_in_progress": [
    {
      "number": 42,
      "title": "Implementar middleware OIDC",
      "labels": ["feat", "in-progress"],
      "assignee": "iagoleal",
      "milestone": 1,
      "last_update": "2026-04-29T10:00:00Z",
      "url": "https://github.com/owner/name/issues/42"
    }
  ],
  "blockers": [
    {"issue": 42, "blocked_by": [37], "reason": "Aguardando ADR-0008"}
  ],
  "recent_adrs": [
    {
      "path": "docs/adr/0008-escolha-de-fila.md",
      "title": "Escolha de fila de tarefas",
      "status": "accepted",
      "date": "2026-04-28"
    }
  ],
  "next_steps": [
    {
      "priority": 1,
      "description": "Resolver ADR-0008 para destravar issue #42",
      "rationale": "Bloqueia 1 issue do milestone com prazo em 15 dias"
    }
  ]
}
```

---

### 4.2 `scripts/decompose.py`

#### Responsabilidades
1. Ler input: caminho de SOAP do `mdcu` (`--input <path>`) OU texto livre (`--text "..."`)
2. Parsear estrutura: extrair demanda destilada, restrições, critérios de sucesso
3. Propor decomposição em milestones (cada um com escopo, critério de release, RACI)
4. Para cada milestone, propor issues atômicas com: hipótese, critério de aceite testável, definição de pronto, dependências entre issues, estimativa em complexidade (S/M/L/XL — não em horas), archetype sugerido para spawn
5. Identificar perguntas em aberto e trade-offs explícitos
6. **Não abre nada no GitHub** — apenas propõe (output JSON consumido por humano ou por `milestone.py`/`issue.py` em pipeline)

#### Padrão de Implementação
- Stdlib only
- Heurística de decomposição: regras textuais em `references/decomposition_heuristics.md` lidas pelo orquestrador (não pelo script — script só estrutura input/output)
- Script delega lógica de decomposição ao orquestrador via prompt; recebe JSON estruturado de volta. **Alternativa determinística:** script aceita JSON pré-estruturado e apenas valida schema. Implementação default: validação de schema; geração de proposta é responsabilidade do orquestrador.

#### CLI
```
python scripts/decompose.py {--input <path> | --text <string>} [--validate-only] [--json]
```

- `--input`: caminho para arquivo `.md` (tipicamente SOAP do `mdcu`)
- `--text`: texto livre como alternativa ao `--input`
- `--validate-only`: valida schema de proposta passada via stdin (sem gerar)
- `--json`: força output JSON em stdout

#### Output JSON
```json
{
  "input_summary": "Adicionar autenticação OIDC ao app, mantendo compatibilidade com sessões existentes",
  "milestones_proposed": [
    {
      "title": "MVP Auth",
      "scope": "Login OIDC + sessão híbrida",
      "release_criterion": "100% dos novos logins via OIDC; sessões legadas funcionam até expiração",
      "raci": {
        "responsible": "ai-engineer",
        "accountable": "user",
        "consulted": ["security-engineer"],
        "informed": []
      },
      "complexity_estimate": "M",
      "issues": [
        {
          "title": "Implementar middleware OIDC",
          "type": "feat",
          "hypothesis": "Middleware OIDC entre nginx e app permite migração gradual",
          "acceptance_criteria": [
            "Login OIDC retorna sessão válida",
            "Sessão legada continua válida até expiração natural",
            "Telemetria distingue origem (oidc/legacy)"
          ],
          "definition_of_done": [
            "Testes unitários passando",
            "ADR-NNNN documentando escolha do provider",
            "Eval offline com 50 casos"
          ],
          "dependencies": [],
          "complexity": "M",
          "spawn_archetype": "backend-dev"
        }
      ]
    }
  ],
  "open_questions": [
    "Qual provider OIDC? (Auth0/Keycloak/Clerk)"
  ],
  "tradeoffs": [
    {
      "decision": "Sessão híbrida vs migração big-bang",
      "pros": ["Sem downtime", "Rollback fácil"],
      "cons": ["Código duplicado por 90 dias", "Telemetria mais complexa"]
    }
  ]
}
```

---

### 4.3 `scripts/milestone.py`

#### Responsabilidades
1. Subcomando `open`: cria milestone via `gh api repos/{}/{}/milestones -f title=... -f description=... -f due_on=...`
2. Subcomando `update`: atualiza campos via PATCH
3. Subcomando `close`: fecha milestone (state=closed) e gera resumo de release notes em stdout

#### Padrão de Implementação
- Stdlib only
- Descrição do milestone DEVE conter seções literais: `## Escopo`, `## Critério de Release`, `## RACI` (Responsible Accountable Consulted Informed)

#### CLI
```
python scripts/milestone.py open --title <str> --scope <str> --release-criterion <str> --raci-responsible <str> --raci-accountable <str> [--raci-consulted <csv>] [--raci-informed <csv>] [--due <ISO8601>] [--repo <owner/name>] [--json]
python scripts/milestone.py update --number <int> [--title <str>] [--scope <str>] [--release-criterion <str>] [--due <ISO8601>] [--repo <owner/name>] [--json]
python scripts/milestone.py close --number <int> [--repo <owner/name>] [--json]
```

#### Output JSON
```json
{
  "action": "open|update|close",
  "milestone": {
    "number": 1,
    "title": "MVP Auth",
    "url": "https://github.com/owner/name/milestone/1",
    "state": "open",
    "due_on": "2026-05-15T00:00:00Z"
  }
}
```

---

### 4.4 `scripts/issue.py`

#### Responsabilidades
1. Subcomando `open`: cria issue com label tipada obrigatória (`feat|bug|chore|spike|incident|tech-debt`), milestone opcional, corpo seguindo template literal de `references/issue_template.md`
2. Subcomando `update`: append de comentário (achado/atualização) via `gh issue comment`
3. Subcomando `close`: fecha issue exigindo `--pr <url>` E `--commit <sha>` (zero exceções: rastreabilidade obrigatória)

#### Padrão de Implementação
- Stdlib only
- Validar label `--type` contra enum hardcoded `{feat, bug, chore, spike, incident, tech-debt}`. Exit code 2 se inválido
- Body de `open` DEVE conter seções: `## Hipótese`, `## Critério de Aceite`, `## Definição de Pronto`, `## Dependências`, `## Complexidade` (S/M/L/XL)

#### CLI
```
python scripts/issue.py open --title <str> --type <feat|bug|chore|spike|incident|tech-debt> --hypothesis <str> --acceptance <csv> --dod <csv> --complexity <S|M|L|XL> [--milestone <int>] [--depends-on <csv-of-issue-numbers>] [--archetype <str>] [--repo <owner/name>] [--json]
python scripts/issue.py update --number <int> --finding <str> [--repo <owner/name>] [--json]
python scripts/issue.py close --number <int> --pr <url> --commit <sha> [--repo <owner/name>] [--json]
```

#### Output JSON
```json
{
  "action": "open|update|close",
  "issue": {
    "number": 42,
    "title": "Implementar middleware OIDC",
    "url": "https://github.com/owner/name/issues/42",
    "state": "open",
    "labels": ["feat"],
    "milestone": 1
  }
}
```

---

### 4.5 `scripts/adr_new.py`

#### Responsabilidades
1. Detectar próximo número via `ls docs/adr/` + parse de prefixo `NNNN-`
2. Criar `docs/adr/NNNN-<slug>.md` com seções literais: `# ADR-NNNN: <título>`, `## Status`, `## Contexto`, `## Decisão`, `## Consequências`, `## Alternativas Consideradas`, `## Referências`
3. Suportar status: `proposed | accepted | deprecated | superseded`
4. Se `--supersedes <NNNN>`, atualizar ADR antigo para `superseded by ADR-<novo>`
5. Slug do título: lowercase, hífens, sem acentos, max 50 chars

#### Padrão de Implementação
- Stdlib only
- Cria diretório `docs/adr/` se não existe
- Numeração sequencial: `0001`, `0002`, ... (4 dígitos)
- Falha se já existe arquivo com o mesmo número (race condition); exit code 3

#### CLI
```
python scripts/adr_new.py --title <str> --status <proposed|accepted|deprecated|superseded> --context <str> --decision <str> --consequences <str> [--alternatives <csv>] [--supersedes <int>] [--debt-conscious] [--json]
```

- `--debt-conscious`: marca ADR como "dívida técnica consciente"; adiciona seção `## Dívida Consciente Assumida` com timestamp e justificativa em `--decision`

#### Output JSON
```json
{
  "adr": {
    "number": 8,
    "path": "docs/adr/0008-escolha-de-fila.md",
    "title": "Escolha de fila de tarefas",
    "status": "accepted",
    "date": "2026-04-30",
    "supersedes": null,
    "debt_conscious": false
  }
}
```

---

### 4.6 `scripts/prompt_contract.py`

#### Responsabilidades
1. Detectar próximo número em `prompts/` (mesma lógica de `adr_new.py`)
2. Criar `prompts/NNNN-<slug>.md` com seções literais: `# Prompt-NNNN: <task>`, `## Versão`, `## Modelo Alvo`, `## Input Schema`, `## Output Schema`, `## Eval Offline`, `## Fallback Determinístico`, `## Budget de Tokens`, `## Telemetria`
3. Versão SemVer: bump minor por mudança aditiva, major por breaking

#### Padrão de Implementação
- Stdlib only
- Cria diretório `prompts/` se não existe
- Falha se não fornecer `--fallback` e `--budget-tokens` (esses são obrigatórios — regra da persona "AI engineering, não vibe coding")

#### CLI
```
python scripts/prompt_contract.py --task <str> --model <str> --input-schema <json-or-path> --output-schema <json-or-path> --fallback <str> --budget-tokens <int> [--eval-cases <path>] [--json]
```

#### Output JSON
```json
{
  "prompt_contract": {
    "number": 3,
    "path": "prompts/0003-classificar-incidente.md",
    "task": "Classificar incidente por severidade",
    "version": "1.0.0",
    "model": "claude-haiku-4-5-20251001",
    "budget_tokens": 800,
    "has_fallback": true,
    "has_eval": true
  }
}
```

---

### 4.7 `scripts/postmortem.py`

#### Responsabilidades
1. Receber número de issue `incident` fechada via `--incident <N>`
2. Validar que issue tem label `incident` E state=closed
3. Coletar contexto: corpo da issue, comentários, PRs/commits linkados
4. Gerar nova issue `postmortem` com seções literais: `# Pós-morto — <título original>`, `## Timeline`, `## Impacto`, `## Causa Raiz`, `## Ação Corretiva (Tomada)`, `## Ação Preventiva (Proposta)`, `## ADRs Gerados`, `## Linkado ao incidente original #N`
5. Aplicar labels `postmortem` + `incident`

#### Padrão de Implementação
- Stdlib only
- Conteúdo das seções é placeholder estruturado para ser preenchido por humano (CTO + envolvidos); script gera o esqueleto com timeline auto-extraída de eventos da issue original (created, comments timestamps, closed)

#### CLI
```
python scripts/postmortem.py --incident <int> [--repo <owner/name>] [--json]
```

#### Output JSON
```json
{
  "postmortem": {
    "number": 88,
    "url": "https://github.com/owner/name/issues/88",
    "linked_incident": 75,
    "timeline_events": 12
  }
}
```

---

### 4.8 `scripts/session_close.py`

#### Responsabilidades
1. Atualizar `.cto/state.json` (chama internamente `briefing.py --update-memory`)
2. Ler input: narrativa estruturada via `--narrative <path>` (markdown) OU stdin (`--narrative -`); contém A+P da sessão, decisões em flight, threads abertas
3. Compor `.cto/last-session.md` com seções literais: frontmatter YAML (`closed_at`, `repo`, `state_snapshot_at`, `turns_estimate`, `archetypes_spawned`), `## Marcos da sessão`, `## Decisões em flight`, `## Threads abertas`, `## TL;DRs de ADRs tocados`, `## TL;DRs de issues tocadas`, `## Próximos passos sugeridos`
4. Para cada archetype spawnado na sessão (passado via `--archetypes <csv>`), disparar atualização de `.cto/agents/<X>/memory.md` se ainda não atualizado pelo próprio agente
5. Validar que `.cto/` está em `.gitignore`; abortar com exit code 9 se não estiver (segurança contra leak)

#### Padrão de Implementação
- Stdlib only
- Cria `.cto/` se não existe; cria/atualiza `.gitignore` adicionando linha `.cto/` se ausente
- Falha (exit code 9) se `.cto/` aparece em `git status --porcelain` como tracked (rastreabilidade da regra de privacidade)
- TL;DRs de ADRs/issues são extraídos do `state.json`; script não lê arquivos completos — apenas estrutura

#### CLI
```
python scripts/session_close.py --narrative <path|-> [--archetypes <csv>] [--repo <owner/name>] [--json]
```

- `--narrative`: caminho para arquivo `.md` com narrativa estruturada da sessão, OU `-` para stdin
- `--archetypes`: CSV de archetypes spawnados (ex: `backend-dev,security-engineer`); para cada archetype listado, dispara refresh de `.cto/agents/<X>/memory.md` quando `last_synced_at` >24h OU houve ADR/milestone novo desde então
- `--repo`: default = detectado por `gh`
- `--json`: emite apenas JSON em stdout

#### Output JSON
```json
{
  "session_closed_at": "2026-04-30T18:00:00Z",
  "artifacts_written": [
    ".cto/state.json",
    ".cto/last-session.md",
    ".cto/agents/backend-dev/memory.md"
  ],
  "gitignore_validated": true,
  "estimated_tokens_saved_next_session": 45000
}
```

---

## 5. Dependências (Versões Fixas)

### 5.1 Dependências Python

| Pacote | Versão | Propósito |
|--------|--------|-----------|
| (nenhuma) | — | Skill usa apenas Python stdlib (`subprocess`, `json`, `pathlib`, `argparse`, `re`, `datetime`, `string`, `sys`, `os`). Justificativa: skill orquestradora fina; templates como markdown com `string.Template`; YAML não é necessário (frontmatter é literal e parseado por regex stdlib quando preciso). Determinismo via stdlib é mais seguro do que dependências externas. |

### 5.2 Dependências de Sistema

| Pacote | Instalação (macOS) | Instalação (Linux) | Versão mínima | Propósito |
|--------|---------------------|---------------------|----------------|-----------|
| `gh` | `brew install gh` | `apt install gh` (Ubuntu 22.04+) ou via [cli.github.com](https://cli.github.com) | `2.40.0` | CLI oficial GitHub; auth via token do usuário; usado em todos os scripts que tocam GitHub |
| `git` | preinstalado / `brew install git` | preinstalado / `apt install git` | `2.40.0` | Detecção de repo, blame, log de ADRs |
| `python` | preinstalado (`/usr/bin/python3`) ou `brew install python@3.11` | `apt install python3.11` | `3.11.0` | Runtime dos scripts (stdlib only) |

Pré-condição: `gh auth status` retorna 0 antes de qualquer script que use GitHub. Se falhar, scripts emitem erro pedindo `gh auth login` (exit code 4).

---

## 6. Armazenamento de Dados

A skill `cto` **não persiste estado em `$HOME`**. Não cria `~/.cto/` nem qualquer diretório em `$HOME` do usuário.

Artefatos gerados pela skill ficam em duas categorias dentro do projeto-alvo:

**Versionados (entram no repo, parte do contrato técnico):**
```
<projeto>/
├── docs/
│   └── adr/
│       ├── 0001-titulo-slug.md
│       └── ...
├── prompts/
│   ├── 0001-task-slug.md
│   └── ...
└── evals/
    └── <task>/
        └── cases.jsonl
```

**Gitignored (memória per-projeto, não vai pro repo):**
```
<projeto>/
└── .cto/
    ├── state.json                  # cache do briefing, schema 6.3
    ├── last-session.md             # narrativa de fechamento, schema 6.4
    └── agents/
        ├── backend-dev/
        │   └── memory.md           # memória per-archetype, schema 6.5
        ├── frontend-dev/
        │   └── memory.md
        └── ...
```

`.cto/` é auto-adicionado ao `.gitignore` do projeto na 1ª escrita por qualquer script. Regra dura: orquestrador recusa operação se `.cto/` aparece staged em `git status` (proteção contra leak em repo público).

### 6.1 Schema de ADR (`docs/adr/NNNN-slug.md`)

Cabeçalho YAML obrigatório (representação JSON literal do schema):

```json
{
  "adr": 8,
  "title": "Escolha de fila de tarefas",
  "status": "accepted",
  "date": "2026-04-30",
  "supersedes": null,
  "superseded_by": null,
  "debt_conscious": false
}
```

Equivalente em frontmatter YAML do arquivo:

```yaml
---
adr: 8
title: Escolha de fila de tarefas
status: accepted
date: 2026-04-30
supersedes: null
superseded_by: null
debt_conscious: false
---
```

Tipos: `adr: int`, `title: str`, `status: enum[proposed,accepted,deprecated,superseded]`, `date: ISO8601-date`, `supersedes: int|null`, `superseded_by: int|null`, `debt_conscious: bool`.

Corpo: seções `## Contexto`, `## Decisão`, `## Consequências`, `## Alternativas Consideradas`, `## Referências`. Se `debt_conscious: true`, seção adicional `## Dívida Consciente Assumida`.

### 6.2 Schema de Prompt Contract (`prompts/NNNN-slug.md`)

Cabeçalho YAML obrigatório (representação JSON literal do schema):

```json
{
  "prompt": 3,
  "task": "Classificar incidente por severidade",
  "version": "1.0.0",
  "model": "claude-haiku-4-5-20251001",
  "budget_tokens": 800,
  "has_fallback": true,
  "has_eval": true
}
```

Equivalente em frontmatter YAML do arquivo:

```yaml
---
prompt: 3
task: Classificar incidente por severidade
version: 1.0.0
model: claude-haiku-4-5-20251001
budget_tokens: 800
has_fallback: true
has_eval: true
---
```

Tipos: `prompt: int`, `task: str`, `version: SemVer-string`, `model: str` (ID literal de modelo Claude), `budget_tokens: int`, `has_fallback: bool`, `has_eval: bool`.

Corpo: seções `## Input Schema` (JSON Schema), `## Output Schema` (JSON Schema), `## Eval Offline` (caminho para `evals/<task>/cases.jsonl` + critério pass/fail), `## Fallback Determinístico` (regra/template/regex acionada quando `confidence < threshold`), `## Telemetria` (lista literal de campos: `request_id`, `prompt_version`, `model`, `tokens_in`, `tokens_out`, `latency_ms`, `confidence`, `fallback_used`).

### 6.3 Schema de `.cto/state.json` (cache do briefing)

```json
{
  "last_synced_at": "2026-04-30T18:00:00Z",
  "repo": "owner/name",
  "synced_against": {
    "latest_adr_number": 8,
    "latest_milestone_number": 3,
    "latest_issue_event_at": "2026-04-30T17:42:00Z"
  },
  "milestones": [ /* mesmo schema de briefing.py output */ ],
  "issues_in_progress": [ /* mesmo schema */ ],
  "blockers": [ /* mesmo schema */ ],
  "recent_adrs": [ /* mesmo schema */ ],
  "next_steps": [ /* mesmo schema */ ]
}
```

Regra de invalidação: `briefing.py --from-memory` falha se (a) `last_synced_at` >24h, OU (b) `gh api` rápido detecta `latest_adr_number` ou `latest_milestone_number` maiores do que o registrado em `synced_against`. Em ambos os casos, sugere `--update-memory`.

### 6.4 Schema de `.cto/last-session.md` (narrativa de fechamento)

Frontmatter YAML obrigatório:

```yaml
---
closed_at: 2026-04-30T18:00:00Z
repo: owner/name
state_snapshot_at: 2026-04-30T18:00:00Z
turns_estimate: 87
archetypes_spawned: [backend-dev, security-engineer]
duration_minutes_estimate: 95
---
```

Corpo com seções literais (na ordem):
- `## Marcos da sessão` — bullets do que foi entregue (issue fechada com PR, milestone fechado, ADR aceito, etc.)
- `## Decisões em flight` — decisões discutidas mas não materializadas em ADR/issue ainda; cada uma com TL;DR + ponteiro para próximo passo
- `## Threads abertas` — questões ainda sem resolução; cada uma com estado e bloqueio se houver
- `## TL;DRs de ADRs tocados` — para cada ADR lido na sessão: número, título, status, 1 frase de decisão, 1 frase de consequência principal
- `## TL;DRs de issues tocadas` — para cada issue tocada: número, título, label tipada, hipótese atual em 1 frase, último achado em 1 frase
- `## Próximos passos sugeridos` — até 5 itens priorizados

### 6.5 Schema de `.cto/agents/<archetype>/memory.md` (memória per-archetype)

Frontmatter YAML obrigatório:

```yaml
---
archetype: backend-dev
last_synced_at: 2026-04-30T17:30:00Z
synced_against:
  latest_adr_number: 8
  latest_milestone_number: 3
invocation_count: 4
last_invoked_at: 2026-04-30T17:25:00Z
---
```

Corpo com seções literais:
- `## Especialização local` — o que o agente aprendeu sobre o projeto que NÃO mora em ADR/issue (ex: convenções tácitas, gotchas descobertos em invocação anterior)
- `## ADRs internalizados` — TL;DR de cada ADR relevante para o domínio do archetype; agente pula releitura do arquivo completo se TL;DR cobre
- `## Issues correntes no domínio` — issues abertas relevantes, com estado e dependências
- `## Heurísticas calibradas` — ajustes de heurística de execução do archetype para este projeto específico (ex: "neste repo, sempre usar pytest -x antes de pytest -k")
- `## Histórico de invocações` — log compacto cronológico (1 linha por invocação anterior: data + tarefa + resultado)

Regra de invalidação: agente delta-checka `synced_against` ao iniciar; se `latest_adr_number` ou `latest_milestone_number` cresceram, agente lê apenas os novos artefatos e atualiza memória. Se `last_synced_at` >7 dias, recomendar refresh completo via `session_close.py --archetypes <X>`.

---

## 7. Padrões de Implementação Obrigatórios

### 7.1 Self-Bootstrap

**N/A.** Skill não usa deps externas Python; nenhum venv próprio é necessário. Scripts rodam diretamente com `python3` do sistema (≥3.11). Pré-condição é apenas `gh` autenticado, validado no início de cada script que usa GitHub.

Padrão de pré-condição (copiar literal em todos os scripts que tocam GitHub):

```python
def ensure_gh_auth() -> None:
    r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write("Erro: gh CLI não autenticado. Rode `gh auth login`.\n")
        sys.exit(4)
```

### 7.2 Saída JSON

- Scripts com `--json` imprimem **apenas JSON válido** em stdout
- Mensagens de progresso, log e erro vão para stderr
- Encoding: `json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)`
- Datas em ISO 8601 UTC com `Z` (`datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`)

### 7.3 Tratamento de Erros

| Condição | Exit code | Mensagem em stderr |
|----------|-----------|---------------------|
| Sucesso | 0 | (nenhuma obrigatória) |
| Argumento inválido (CLI) | 2 | `Erro: argumento inválido — <detalhe>` |
| ADR/Prompt com número duplicado (race) | 3 | `Erro: NNNN já existe em <path>` |
| `gh` não autenticado | 4 | `Erro: gh CLI não autenticado. Rode \`gh auth login\`.` |
| Repo não detectado | 5 | `Erro: repo GitHub não detectado. Use --repo <owner/name>.` |
| Issue/milestone não encontrado | 6 | `Erro: <tipo> #N não existe no repo <repo>.` |
| Validação de schema (decompose) | 7 | `Erro: input não conforma ao schema esperado em <campo>.` |
| Memória `.cto/state.json` stale ou ausente | 8 | `Erro: memória stale (last_synced_at <ISO>) ou ausente. Rode com --update-memory.` |
| `.cto/` rastreado em git (privacy leak) | 9 | `Erro: .cto/ aparece staged em git. Adicione .cto/ ao .gitignore antes de prosseguir.` |
| Erro inesperado | 1 | `Erro: <mensagem>` (com traceback em stderr se `--debug`) |

### 7.4 Padrão de spawn de archetype (memory-aware, portável)

Quando o orquestrador decide delegar a um archetype, opera em **modo subagent** (se tool disponível) ou **modo auto-persona** (orquestrador assume persona temporária do archetype). O protocolo de memória é idêntico.

**Caso A — memória existente e fresca** (`.cto/agents/<archetype>/memory.md` existe E `last_synced_at` ≤24h E nenhum ADR/milestone novo):

1. Ler `references/archetypes/<archetype>.md` — definição canônica
2. Compor prompt: `<archetype.md> + "\n\n## Tarefa\n" + <task description> + "\n\n## Instrução\nLeia .cto/agents/<archetype>/memory.md ANTES de qualquer outro arquivo. A memória contém briefing + TL;DRs de ADRs/issues relevantes. Releia ADR/issue completo APENAS se a tarefa exige detalhe ausente da memória."`
3. Delegar (subagent) ou executar diretamente (auto-persona — ver SKILL.md §7.1)
4. Agente atualiza `.cto/agents/<archetype>/memory.md` ao final (escreve seção "Histórico de invocações" + atualiza TL;DRs se houver mudança)
5. Orquestrador recebe resultado, posta via `issue.py update`

**Caso B — memória stale** (>24h OU houve ADR/milestone novo):

1. Orquestrador delta-checka: lê apenas ADRs/milestones com número > `synced_against`
2. Compor prompt como Caso A + seção `## Delta desde última sincronização\n<delta>`
3. Resto idêntico a Caso A

**Caso C — bootstrap (1ª invocação, memória ausente):**

1. Ler `references/archetypes/<archetype>.md`
2. Executar `python scripts/briefing.py --from-memory --json` (ou `--update-memory` se cache stale)
3. Ler `docs/adr/<adrs-relevantes>.md` + executar `gh issue view --json body,comments`
4. Compor prompt fat: `<archetype.md> + briefing + ADRs + issue + task + instrução de criar memória ao final`
5. Delegar ou executar diretamente (§7.1)
6. Agente cria `.cto/agents/<archetype>/memory.md` consolidando o aprendido (seções 6.5)
7. Orquestrador recebe resultado, posta via `issue.py update`

**Princípio:** Caso A é o caminho default em projetos com uso recorrente do `/cto`; Casos B e C são exceção (delta-check ou onboarding).

---

## 8. Fluxo Interativo

**N/A para fluxo de onboarding.** A skill não tem configuração inicial — basta clonar/criar o diretório e os scripts funcionam imediatamente (pré-condição: `gh auth login` já feito pelo usuário).

**Fluxo de uso (não-interativo, comando-orientado):**

Toda invocação `/cto` em sessão nova executa **session opener** automaticamente como primeira ação:

```
============================================================
  /cto — Briefing de Estado
============================================================

Repo: iagoleal/projeto-x
Gerado em: 2026-04-30T12:00:00Z

Milestones ativos:
  [#1] MVP Auth — 40% (3 abertas, 2 fechadas) — vence em 15 dias

Issues em andamento:
  #42 [feat] Implementar middleware OIDC — @iagoleal — atualizada há 1 dia

Bloqueios:
  #42 → bloqueada por ADR-0008 pendente

ADRs recentes:
  0008 [proposed] Escolha de fila de tarefas — 2026-04-28

Próximos passos sugeridos:
  1. Resolver ADR-0008 (destrava #42)
  2. Abrir spike sobre observabilidade do middleware

Como posso coordenar a partir daqui?
```

Após o briefing, o orquestrador entra em modo de espera para comando explícito do usuário. Não há fluxo interativo de perguntas-de-onboarding.

---

## 9. Critérios de Aceite

A skill está PRONTA quando:

- [ ] `python scripts/briefing.py --repo <owner/name> --json` executa sem erro em repo com 1+ milestone aberto e retorna JSON válido conforme schema da Seção 4.1
- [ ] `python scripts/decompose.py --text "exemplo de demanda" --json` retorna JSON válido com pelo menos 1 milestone proposto e issues conformes ao schema 4.2
- [ ] `python scripts/milestone.py open --title T --scope S --release-criterion R --raci-responsible X --raci-accountable Y --json` cria milestone real no GitHub e retorna JSON conforme 4.3
- [ ] `python scripts/issue.py open --title T --type feat --hypothesis H --acceptance "a,b" --dod "c,d" --complexity M --json` cria issue real com todas as seções obrigatórias no body e retorna JSON conforme 4.4
- [ ] `python scripts/issue.py close --number N --pr URL --commit SHA --json` falha (exit 2) se `--pr` ou `--commit` ausentes
- [ ] `python scripts/adr_new.py --title T --status proposed --context C --decision D --consequences X --json` cria `docs/adr/0001-t.md` com frontmatter YAML conforme 6.1 e seções obrigatórias
- [ ] `python scripts/adr_new.py --debt-conscious ...` adiciona seção `## Dívida Consciente Assumida` no arquivo gerado
- [ ] `python scripts/prompt_contract.py --task T --model M --input-schema '{}' --output-schema '{}' --fallback F --budget-tokens 500 --json` cria `prompts/0001-t.md` conforme 6.2
- [ ] `python scripts/prompt_contract.py` sem `--fallback` ou sem `--budget-tokens` falha com exit code 2
- [ ] `python scripts/postmortem.py --incident <N> --json` cria issue `postmortem` linkada e retorna JSON conforme 4.7
- [ ] `gh auth status` retornando != 0 faz qualquer script tocar GitHub falhar com exit code 4 e mensagem padrão
- [ ] `references/archetypes/` contém os 7 archetypes especificados (`frontend-dev`, `backend-dev`, `ai-engineer`, `security-engineer`, `devops`, `qa-engineer`, `tech-writer`), cada um com as 5 seções literais (`## Identidade`, `## Quando o CTO me chama`, `## Contrato`, `## O que NÃO faço`, `## Heurísticas de execução`)
- [ ] `references/persona_cto.md`, `references/github_protocol.md`, `references/adr_protocol.md`, `references/ai_engineering.md`, `references/governance_partition.md`, `references/spawn_protocol.md` existem
- [ ] Frontmatter de `SKILL.md` contém literalmente "ATIVE APENAS quando o usuário digitar /cto"
- [ ] Spawn de archetype produz prompt composto corretamente (verificável por inspeção de log de Agent tool em sessão de teste)
- [ ] `python scripts/briefing.py --update-memory` cria `.cto/state.json` conforme schema 6.3 e adiciona `.cto/` ao `.gitignore` se ausente
- [ ] `python scripts/briefing.py --from-memory --json` lê `.cto/state.json` quando fresco; falha com exit code 8 quando stale (`last_synced_at` >24h OU latest_adr_number remoto > registrado)
- [ ] `python scripts/session_close.py --narrative <path> --archetypes backend-dev,security-engineer --json` cria `.cto/last-session.md` conforme schema 6.4 e dispara refresh de memória per-archetype quando necessário
- [ ] `python scripts/session_close.py` falha com exit code 9 se `.cto/` aparece staged em `git status --porcelain`
- [ ] Spawn em Caso A (memória fresca) compõe prompt sem incluir conteúdo de ADRs/issues, apenas `<archetype.md> + <task> + instrução de leitura de memória`
- [ ] Spawn em Caso C (bootstrap) cria `.cto/agents/<archetype>/memory.md` conforme schema 6.5 ao final
- [ ] Frontmatter de `SKILL.md` v1.2.0 menciona literalmente "memória per-projeto em `.cto/`" e "ponderação seletiva"
- [ ] Scripts emitem output compacto por default; `--verbose` expande

Cada critério é executável e tem resultado binário (passa/falha).

---

## 10. O que esta Skill NÃO faz

- NÃO escreve código de produção — implementação é delegada via spawn de archetype (`backend-dev`, `frontend-dev`, `ai-engineer`, etc.) usando o Agent tool. CTO consolida resultado em comentário de issue + ADR (Architectural Decision Record).
- NÃO substitui `mdcu` — discovery centrada no usuário (anamnese, demanda aparente vs. demanda verdadeira) é responsabilidade do `mdcu`. CTO recebe a sumarização SOAP destilada como input.
- NÃO substitui `project-init` — extração de contrato técnico (`ARCHITECTURE.md`) é do `project-init`. CTO consulta o `ARCHITECTURE.md` mas não o cria.
- NÃO substitui `rsop` — prontuário do software (lista de problemas, SOAPs do projeto) é do `rsop`. CTO consulta e referencia, não duplica.
- NÃO faz deploy — abre issue `chore` com checklist de release e delega via archetype `devops`.
- NÃO toma decisão técnica sem registrar ADR — toda decisão arquitetural relevante exige `scripts/adr_new.py` antes de virar issue de implementação.
- NÃO aceita demanda complexa de bate-pronto — pondera pros/contras antes de **abertura de issue, criação de ADR, abertura de milestone, ou spawn de archetype**. CRUD trivial (`issue.py update`, `issue.py close`, `milestone.py close`) DISPENSA ponderação por economia de tokens. Dívida técnica consciente é declarada explicitamente pelo usuário e registrada como ADR `--debt-conscious`.
- NÃO ativa sem `/cto` explícito — sem matching de linguagem natural; invocação explícita evita conflito com skills irmãs (`mdcu`, `rsop`, `project-init`, `project-setup`, `mdcu-seg`, `reversa`).
- NÃO usa LLM (Large Language Model) como mágica — todo uso de LLM em produção exige contrato de prompt versionado (`scripts/prompt_contract.py`) com eval offline, fallback determinístico e budget de tokens declarado. Recusa "vibe coding"; distingue rigorosamente de AI engineering.
- NÃO persiste estado em `$HOME` do usuário — proibido criar `~/.cto/` ou qualquer diretório fora do repo do projeto-alvo.
- NÃO commita `.cto/` no repo — diretório é estritamente gitignored; orquestrador recusa operação se aparece staged. Memória per-projeto vive no filesystem local apenas (segurança em repos públicos).
- NÃO relê ADR/issue/ARCHITECTURE.md depois de carregar `.cto/last-session.md` ou `.cto/agents/<X>/memory.md` — releitura só em delta-check obrigatório (memória stale) ou se a tarefa exige detalhe ausente da memória. Releitura redundante anula a economia de token da v1.2.0.
- NÃO faz code review — PRs (Pull Requests) são revisados pelo orquestrador diretamente ou por skill especializada quando existir; CTO apenas exige checklist no template de PR.
- NÃO opera em projeto sem `gh` autenticado — falha rápida (exit code 4) em vez de degradar silenciosamente.

---

## 11. Changelog

| Versão | Data | Mudança |
|--------|------|---------|
| 1.0.0 | 2026-04-30 | Versão inicial. Modelo 1 (skill única com archetypes embutidos), governança D-leve (ADRs em `docs/adr/`, contratos de prompt em `prompts/`, RACI/pós-mortem no GitHub), 7 scripts (briefing, decompose, milestone, issue, adr_new, prompt_contract, postmortem), 7 archetypes (`frontend-dev`, `backend-dev`, `ai-engineer`, `security-engineer`, `devops`, `qa-engineer`, `tech-writer`), zero deps Python externas (stdlib only), `gh` CLI ≥ 2.40.0 + Python ≥ 3.11 como deps de sistema. Ativação apenas via `/cto` explícito. |
| 1.1.0 | 2026-04-30 | Adicionada Seção 8 do SKILL.md "Higiene de sessão — gestão de tokens" e novo reference `references/session_hygiene.md`. CTO agora sugere encerramento de sessão ao usuário após marco natural quando há sinais de sessão pesada. Nunca encerra autonomamente. Não sugere no meio de feature ou em sessão curta. |
| 1.2.0 | 2026-04-30 | **Disciplina de tokens — economia ~40-100k tokens/sessão.** (a) **Memória per-projeto em `.cto/`** (gitignored, auto-`.gitignore`): `state.json` cacheado do briefing, `last-session.md` narrativa de fechamento, `agents/<X>/memory.md` per-archetype. Schemas 6.3, 6.4, 6.5. (b) **Spawn memory-aware** (Casos A/B/C em §7.4): com memória fresca, prompt do spawn é `<archetype.md> + <task>` em vez de fat-prompt — economia ~9-22k tokens/spawn. (c) Novo script `session_close.py` (§4.8). (d) `briefing.py` ganha `--from-memory` e `--update-memory`. (e) **Ponderação seletiva**. (f) Output compacto por default. (g) Novos exit codes: 8 (memória stale), 9 (`.cto/` rastreado em git). |
| 1.3.0 | 2026-04-30 | **Portabilidade multi-ambiente.** (a) **Modo auto-persona** (SKILL.md §7.1): para ambientes sem tool de subagent (ex: Antigravity), orquestrador lê `references/archetypes/<X>.md`, assume persona temporária, executa tarefa, retorna à persona CTO. Protocolo de memória (Casos A/B/C) idêntico em ambos os modos. (b) **Tool-agnostic**: referências a `Read()`, `Bash()`, `Agent` tool substituídas por linguagem imperativa genérica ("Ler", "Executar", "Delegar ou executar diretamente"). (c) **`/clear` → encerramento de sessão**: substituídas todas as referências a `/clear` (comando específico do Claude Code) por linguagem genérica de encerramento de sessão. (d) **Diretório portável**: SPEC §1 agora declara caminho relativo ao diretório de skills do agente (não mais hardcoded a `~/.claude/skills/`). (e) Nova linha na tabela de Identidade: `Portabilidade`. (f) SPEC §3.2 "Spawn de Agent Efêmero" renomeada para "Spawn de Archetype (memory-aware, portável)" com documentação dos 2 modos. (g) §7.4 atualizado com linguagem tool-agnostic. (h) §11 "NÃO faz" ganha item sobre independência de tool. |
