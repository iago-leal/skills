# Inventário — mdcu-framework

> Gerado pelo **Reversa Scout** em 2026-04-27 (refresh cirúrgico após 6 sessões MDCU)
> Engenharia reversa do projeto raiz `/Users/iagoleal/Desktop/github_repos/skills/mdcu-framework`

---

## Natureza do projeto (CONFIRMADO 🟢)

`mdcu-framework` **não é uma aplicação de software tradicional.** É um **framework metodológico** distribuído como **Agent Skills** (formato Claude Code / Codex / Cursor / Gemini CLI).

- Sem código-fonte executável (`.ts`, `.py`, `.go`, etc.).
- Sem manifesto de dependências (`package.json`, `pyproject.toml`, etc.).
- Sem lock file, sem CI/CD, sem Dockerfile, sem banco de dados.
- Conteúdo: **Markdown estruturado** — 6 SKILL.md + 4 artefatos canônicos do framework + 1 MANIFEST + 1 HTML editorial + RSOP populado.
- Distribuição prevista: cópia para `~/.claude/skills/` (instalação manual, ver `MANIFEST.md`).

**Implicação para fases seguintes:** Archaeologist, Detective, Architect e Writer trabalharão sobre **conteúdo prescritivo em prosa estruturada** — extrair fluxos, contratos entre skills, regras de operação e gates obrigatórios. Não há AST, não há dependency graph, não há entry-point de runtime.

---

## Mudanças desde inventário anterior (2026-04-27 17:44)

Em 6 sessões MDCU consecutivas (commits `ba76256` → `be71eca`), a estrutura mudou substancialmente:

- **NOVO diretório `framework/`** (4 artefatos canônicos versionados): `principles.md`, `architecture-diagram.md`, `glossary.md`, `README.md`
- **NOVA skill `project-setup/`** (v0.1.0) — materialização técnica do contrato, separada do `project-init`
- **`project-init` v2.0.0** — refatorada para só interface (não executa setup)
- **`mdcu` v3.0.0** — F6 reformulada em 3 sub-blocos (delegação + acompanhamento + tradução-fechamento); modo monolítico declarado; gatilho de conformidade dual
- **`rsop` v1.4.0** — schema enriquecido (Tipo + Revisitar) + checklist de qualidade do SOAP (10 itens binários)
- **`commit-soap` v2.0.0** — desacoplado de sessão MDCU; aceita `--from <path>` e `--inline`
- **RSOP populado** — `rsop/dados_base.md` (com Anamnese), `lista_problemas.md` (4 ativos + 7 passivos), 5 SOAPs em `rsop/soap/`
- **`PLANEJAMENTO.md`** (raiz) — documento exploratório que originou as 6 sessões; untracked (não-canônico)

---

## Estrutura de pastas (CONFIRMADO 🟢)

```
mdcu-framework/
├── AGENTS.md                       # entry-point Codex/Cursor (Reversa)
├── CLAUDE.md                       # entry-point Claude Code (Reversa) — gitignored
├── MANIFEST.md                     # manifesto de release v2026.05 (planejada — 6 skills)
├── PLANEJAMENTO.md                 # documento exploratório (untracked, não-canônico)
├── framework-diagrama.html         # documentação visual editorial (1553 linhas)
│
├── mdcu/SKILL.md                   # skill 1 — orquestrador metodológico (462 linhas, v3.0.0 implícita)
├── rsop/SKILL.md                   # skill 2 — prontuário longitudinal (297 linhas, v1.4.0)
├── commit-soap/SKILL.md            # skill 3 — selo longitudinal universal (185 linhas, v2.0.0)
├── project-init/SKILL.md           # skill 4 — extração de contrato técnico (293 linhas, v2.0.0)
├── project-setup/SKILL.md          # skill 5 — materialização do contrato (163 linhas, v0.1.0) [NOVA]
├── mdcu-seg/SKILL.md               # skill 6 — segurança (238 linhas, v1.0.0)
│
├── framework/                      # artefatos canônicos versionados [NOVO]
│   ├── principles.md               # F-1 a F-5 + P-8, P-9 (192 linhas)
│   ├── architecture-diagram.md     # diagrama canônico das 4 camadas (116 linhas)
│   ├── glossary.md                 # termos canônicos + RN-D-014/015/016 (135 linhas)
│   └── README.md                   # relação framework/ × _reversa_sdd/ (39 linhas)
│
├── rsop/                           # prontuário do próprio framework [POPULADO]
│   ├── SKILL.md
│   ├── dados_base.md               # identificação técnica + Anamnese do projeto/stakeholder
│   ├── lista_problemas.md          # 4 ativos (#2 consciente, #5/#6/#7 [B])
│   ├── passivos.md                 # 7 entries (problemas resolvidos hoje)
│   └── soap/                       # 5 SOAPs registrados em 2026-04-27
│       ├── 2026-04-27_tese-formalizada-rsop-inaugurado.md
│       ├── 2026-04-27_f6-reformulada.md
│       ├── 2026-04-27_split-project-init-commit-soap-desacoplado.md
│       ├── 2026-04-27_schema-enrichment-lista-problemas.md
│       └── 2026-04-27_checklist-qualidade-soap.md
│
├── _reversa_sdd/                   # output do Reversa (gitignored)
├── .reversa/                       # estado do Reversa (gitignored)
├── .claude/skills/reversa-*        # Reversa instalado (NÃO faz parte do projeto)
└── .agents/skills/reversa-*        # idem
```

**Nota de exclusão:** `.claude/skills/reversa-*`, `.agents/skills/reversa-*`, `.reversa/`, `_reversa_sdd/` e `.git/` são excluídos da análise. `_reversa_sdd/` é output do próprio Reversa (auto-referência).

---

## Linguagens e formatos (CONFIRMADO 🟢)

| Formato | Extensão | Contagem | Linhas úteis | Papel |
|---|---|---|---|---|
| Markdown | `.md` | 16 arquivos | ≈2218 | Conteúdo das skills + RSOP + framework canônico + meta |
| HTML+CSS | `.html` | 1 arquivo | 1553 | Documentação visual editorial |

**Linguagem primária:** `Markdown`.

---

## "Módulos" identificados (CONFIRMADO 🟢)

A nomenclatura "módulo" para fins do plano Reversa = **uma SKILL.md raiz** OU **um diretório canônico do framework**.

### Skills (6)

| # | Módulo | Versão | Linhas | Papel no framework |
|---|--------|--------|--------|--------------------|
| 1 | `mdcu` | 3.0.0 (implícita — falta frontmatter) | 462 | Orquestrador metodológico — F1-F6, F6 em 3 sub-blocos, modo monolítico declarado |
| 2 | `rsop` | 1.4.0 | 297 | Prontuário longitudinal + Schema enriquecido + Checklist qualidade SOAP |
| 3 | `commit-soap` | 2.0.0 | 185 | Selo longitudinal universal (qualquer marco — sessão MDCU, project-setup, refresh, release) |
| 4 | `project-init` | 2.0.0 | 293 | Extração de contrato técnico → ARCHITECTURE.md (não executa setup) |
| 5 | `project-setup` | 0.1.0 | 163 | **NOVA** — materialização do contrato (manifesto + lock + estrutura), modo desacoplado/monolítico declarado |
| 6 | `mdcu-seg` | 1.0.0 (implícita) | 238 | Módulo de segurança — STRIDE, F0, auditoria trimestral |

### Camada canônica do framework (1 diretório)

| Diretório | Arquivos | Papel |
|---|---|---|
| `framework/` | 4 (principles, architecture-diagram, glossary, README) | Fonte de verdade epistemológica e arquitetural — versionada e distribuída |

**Lista canônica para Fase 2 (Escavação) refresh:** mudanças em `mdcu`, `rsop`, `commit-soap`, `project-init`; análise nova em `project-setup`; análise canônica em `framework/`.

---

## Frameworks / runtimes / dependências externas

**CONFIRMADO 🟢:** nenhum.

Skills Agent dependem apenas de:
- Engine compatível (Claude Code, Codex, Cursor, Gemini CLI) — runtime de IA, não de software.
- Sistema de arquivos local (instalação em `~/.claude/skills/`).
- `git` (para componentes `commit-soap`, `project-setup` em modo monolítico).

**🟡 INFERIDO:** o `framework-diagrama.html` carrega Google Fonts por CDN — única dependência externa em runtime, e estritamente editorial.

---

## Entry points (CONFIRMADO 🟢)

Não há "entry point" de aplicação. Há **gatilhos de invocação** documentados em `description:` de cada SKILL.md.

| Comando-gatilho | Skill ativada | Origem |
|---|---|---|
| `/mdcu`, `/mdcu fase N`, `/mdcu reenquadrar`, `/mdcu fechar`, `/mdcu status` | `mdcu` | mdcu/SKILL.md fim |
| `/rsop init|dados|lista|passivos|soap|revisar|regressao|status` | `rsop` | rsop/SKILL.md fim |
| `/commit-soap`, `/commit-soap --from <path>`, `/commit-soap --inline`, `/commit-soap --dry-run`, `/commit-soap --amend` | `commit-soap` | commit-soap/SKILL.md (v2.0.0) |
| `/project-init`, `/project-init --refresh`, `/project-init --check`, `/project-init status` | `project-init` | project-init/SKILL.md |
| `/project-setup`, `/project-setup --refresh`, `/project-setup --check`, `/project-setup --mode <desacoplado\|monolitico>` | `project-setup` | project-setup/SKILL.md (NOVA) |
| `/mdcu-seg [threat-model|incidente|auditoria|status]` | `mdcu-seg` | mdcu-seg/SKILL.md |

---

## Configurações

| Arquivo | Propósito |
|---|---|
| `MANIFEST.md` | Manifesto da release v2026.05 (planejada) — 6 skills, mudanças, instalação |
| `framework/README.md` | Explica relação `framework/` × `_reversa_sdd/` |
| `framework/principles.md` | Princípios canônicos (F-1 a F-5 + P-8, P-9) — fonte de verdade |
| `framework/glossary.md` | Termos canônicos + RN-D-014/015/016 |
| `framework/architecture-diagram.md` | Anatomia das 4 camadas |
| Frontmatter de cada SKILL.md | `name`, `version`, `author`, `description` |

---

## CI/CD, Docker, Database

**CONFIRMADO 🟢:** ausentes (sem mudança desde inventário anterior).

---

## Cobertura de testes

**CONFIRMADO 🟢:** não há framework de testes nem arquivos `*.test.*` / `*.spec.*`. Validação ocorre por uso real + SOAPs registrados nos commits do próprio repo.

**Lacuna identificada:** `rsop/lista_problemas.md` `#5` (`dogfooding-suite-executavel`) ainda aberta — falta suite executável de validação para CI.

---

## Anatomia em 4 camadas (NOVO — declarada em `framework/architecture-diagram.md`)

| Camada | Componentes | Papel |
|---|---|---|
| **1. Interface humana** | `mdcu` (operacionaliza MCCP em SE) | Canal bidirecional Usuário ↔ pipeline |
| **2. Delegação técnica** | engines downstream desacopláveis: spec-kit, superpowers, bmad, libs maduras, Reversa | Análise, Especificação, Código, Teste — NÃO embutidas no framework |
| **3. Acompanhamento longitudinal** | `rsop` + `commit-soap` (desacoplado) | Transversal a todas as fases (Requisitos → Manutenção) |
| **4. Fundação** | `project-init` (extrai) + `project-setup` (materializa) + `mdcu-seg` (vigia) | Estabelece terreno + vigia continuamente |

---

## Observações cruzadas para fases seguintes (atualizadas)

1. **Para o Archaeologist (refresh):** análise nova de `project-setup` (modo desacoplado vs. monolítico declarado, regras de Gestão Determinística de Dependências enforcement). Re-análise de `mdcu` (F6 em 3 sub-blocos com Disjuntor preservado em F6.b), `rsop` (schema enriquecido + checklist qualidade), `commit-soap` (desacoplado universal), `project-init` (só interface). Artefatos em disco populados em `rsop/`.

2. **Para o Detective (deferred):** ADRs retroativos para 6 commits de hoje. Atualização de `domain.md` com termos canônicos novos (Satisfação clínica, Decisão informada, Composição do orquestrador, Anamnese, Engine downstream desacoplável, Precisa-resolver, Dívida consciente × acidental) e RN-D-014/015/016. **Detective foi parcialmente feito in-loco** durante as sessões — refresh formal fica para sessão futura.

3. **Para o Architect (refresh):** `architecture.md` precisa P-8 + P-9 sistemáticos (atualmente parcial). C4 diagrams precisam refletir 6 skills + camada `framework/` separada. Dependências de skill mudaram (`mdcu` agora depende de `project-setup` também; `commit-soap` é invocado por `project-setup` E por `mdcu`; etc.).

4. **Para o Writer (refresh):** regenerar 4 SDDs (mdcu, rsop, commit-soap, project-init) + criar 1 novo (project-setup). User stories estão consistentes (gatilhos de invocação são entry points). Code-spec matrix precisa atualização.

---

## Total de arquivos analisados

16 arquivos do projeto Markdown (mdcu/SKILL.md, rsop/SKILL.md + 5 SOAPs + dados_base + lista_problemas + passivos, commit-soap/SKILL.md, project-init/SKILL.md, project-setup/SKILL.md, mdcu-seg/SKILL.md, framework/*, MANIFEST.md) + 1 HTML editorial + AGENTS.md + PLANEJAMENTO.md (untracked, exploratório).
