# SDD — `cto`

> Spec executável da skill CTO (Governança Técnica).
> Gerado pelo Reversa Writer em 2026-05-03. Cada afirmação é marcada com 🟢 / 🟡 / 🔴.

## Visão Geral

CTO é um agente voltado à governança técnica, atuando como o C-level do repositório. Ele coordena o processo de desenvolvimento focando em milestones, divisões atômicas (issues) via `gh` CLI, ADRs, contratos de prompts e instanciação (spawn) de archetypes com memória. 🟢

## Responsabilidades

- **Atuar como Engine Downstream do MDCU:** O CTO entra em cena formalmente quando invocado pelo `mdcu` na fase **F6.a** (Delegação), recebendo o briefing/plano da clínica para transformá-lo em engenharia. 🟢
- Decompor macro-demandas em milestones e issues atômicas via `gh` CLI. 🟢
- Exigir e registrar decisões arquiteturais (ADRs), centralizando **toda a infraestrutura e formatação** de ADRs (inclusive para o Vitruvius). 🟢
- Gerir contratos de prompt (versionamento, eval e fallback). 🟢
- Realizar Spawn (invocação de agentes especializados) fornecendo memória apropriada. 🟢
- Gerir memória de longo prazo no diretório `.cto/`. 🟢

## Interface

### Comandos públicos (`scripts/`)

| Script | Propósito | Saída |
|---|---|---|
| `scripts/briefing.py` | Recolhe estado via gh ou state.json | Contexto injetado |
| `scripts/decompose.py` | Proposição local de milestones | Artefatos de breakdown |
| `scripts/milestone.py` | CRUD remoto de milestones via gh | Milestone GH |
| `scripts/issue.py` | CRUD remoto de issues via gh | Issue GH |
| `scripts/adr_new.py` | Templates de ADR | docs/adr/*.md |
| `scripts/prompt_contract.py` | Contratos de prompts | prompts/*.md |
| `scripts/postmortem.py` | Issue blameless após incidente | Issue GH de Postmortem |
| `scripts/session_close.py` | Gera sumário da sessão | .cto/last-session.md |

### Artefato produzido

- `.cto/state.json` (cache mutável). 🟢
- `.cto/last-session.md` (fechamento de sessão). 🟢
- `.cto/agents/<archetype>/memory.md` (memória específica de agente). 🟢
- `docs/adr/NNNN-*.md` (decisões arquiteturais). 🟢
- `prompts/NNNN-*.md` (contratos de engenharia de AI). 🟢

### Artefatos consumidos

- `_mdcu.md` (se ativado logo após o fluxo MDCU). 🟢

## Regras de Negócio

- **Nenhum código sem Issue:** Todo PR deve se vincular a uma issue aberta e tipada. 🟢
- **ADR precedes Issue:** Decisões que geram trade-offs sistêmicos precisam de ADR registrada antes da issue técnica ser criada. O CTO é o **dono exclusivo da infraestrutura de ADRs** (`scripts/adr_new.py`), e skills de ideação como Vitruvius devem delegar a formatação de ADRs ao CTO. 🟢
- **Memória de Spawn (Caso A/B/C):** O CTO decide, ao instanciar um agente subordinado, o tamanho do contexto que irá entregar (fresco, stale ou bootstrap), economizando tokens. 🟢
- **Contratos de Prompt:** Prompts de LLMs exigem controle de versão SemVer, schema explícito, fallback determinístico e métricas. 🟢

## Critérios de Aceitação

```gherkin
Dado que o CTO foi invocado para criar uma issue técnica complexa
E não existe um ADR registrado para a decisão estrutural subjacente
Quando ele analisa os pré-requisitos
Então o CTO GERA primeiro o ADR via `scripts/adr_new.py`
E apenas depois cria a issue referenciando o ADR

Dado que a sessão foi encerrada
Quando a milestone principal é alcançada
Então o CTO roda `scripts/session_close.py`
E atualiza o cache e o arquivo de last-session
```
