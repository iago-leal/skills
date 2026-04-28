# Code/Spec Matrix — mdcu-framework

> Gerado pelo Reversa Writer em 2026-04-27.
> Matriz de rastreabilidade entre **arquivos do projeto** e **specs SDD geradas**.

---

## Matriz: arquivo do projeto → spec correspondente

| Arquivo | Spec correspondente | Cobertura |
|---|---|---|
| `mdcu/SKILL.md` | `_reversa_sdd/sdd/mdcu.md` | 🟢 |
| `rsop/SKILL.md` | `_reversa_sdd/sdd/rsop.md` | 🟢 |
| `commit-soap/SKILL.md` | `_reversa_sdd/sdd/commit-soap.md` | 🟢 |
| `project-init/SKILL.md` | `_reversa_sdd/sdd/project-init.md` | 🟢 |
| `mdcu-seg/SKILL.md` | `_reversa_sdd/sdd/mdcu-seg.md` | 🟢 |
| `MANIFEST.md` | `_reversa_sdd/adrs/008-release-train-v2026-04-com-6-patches.md` | 🟢 |
| `framework-diagrama.html` | — (documentação visual editorial — fora do escopo de spec executável) | — |
| `CLAUDE.md` (raiz) | `_reversa_sdd/c4-context.md` (citado como entry-point ambiental) | 🟡 (não é parte do framework — instalado pelo Reversa) |
| `AGENTS.md` (raiz) | idem | 🟡 (não é parte do framework — instalado pelo Reversa) |

---

## Matriz inversa: spec → arquivo(s) consultado(s)

| Spec gerada | Arquivos do projeto |
|---|---|
| `inventory.md` (Scout) | todos (visão de superfície) |
| `dependencies.md` (Scout) | todos os SKILL.md (extração de dependências entre skills) |
| `code-analysis.md` (Archaeologist) | 5 SKILL.md (mdcu, rsop, commit-soap, project-init, mdcu-seg) |
| `data-dictionary.md` (Archaeologist) | 5 SKILL.md (extração de schemas de artefatos) |
| `flowcharts/{mdcu,rsop,commit-soap,project-init,mdcu-seg}.md` | SKILL.md correspondente |
| `domain.md` (Detective) | 5 SKILL.md + git log + MANIFEST.md |
| `state-machines.md` (Detective) | 5 SKILL.md (extração de estados) |
| `permissions.md` (Detective) | 5 SKILL.md + CLAUDE.md global |
| `adrs/001-008-*.md` (Detective) | git log (mensagens de commit) + MANIFEST.md |
| `architecture.md` (Architect) | todos os artefatos do Scout/Archaeologist/Detective |
| `c4-context.md` (Architect) | 5 SKILL.md + AGENTS.md + CLAUDE.md |
| `c4-containers.md` (Architect) | 5 SKILL.md |
| `c4-components.md` (Architect) | mdcu/SKILL.md (foco) + outros para visão simplificada |
| `erd-complete.md` (Architect) | data-dictionary.md → 5 SKILL.md (origem) |
| `traceability/spec-impact-matrix.md` (Architect) | todos os SDD planejados |
| `sdd/mdcu.md` (Writer) | mdcu/SKILL.md |
| `sdd/rsop.md` (Writer) | rsop/SKILL.md |
| `sdd/commit-soap.md` (Writer) | commit-soap/SKILL.md |
| `sdd/project-init.md` (Writer) | project-init/SKILL.md |
| `sdd/mdcu-seg.md` (Writer) | mdcu-seg/SKILL.md |
| `user-stories/comandos-de-invocacao.md` (Writer) | 5 SKILL.md (extração de gatilhos `/`) |

---

## Cobertura por arquivo

| Arquivo | Linhas no projeto | Coberto por SDD | Coberto por flowchart | Coberto por ADR retroativo | Cobertura final |
|---|---:|---|---|---|---|
| `mdcu/SKILL.md` | 351 | sdd/mdcu.md | flowcharts/mdcu.md | ADR-001, 003, 004, 006 | 🟢 |
| `rsop/SKILL.md` | 238 | sdd/rsop.md | flowcharts/rsop.md | ADR-001, 002, 003, 008 | 🟢 |
| `commit-soap/SKILL.md` | 114 | sdd/commit-soap.md | flowcharts/commit-soap.md | ADR-001, 003, 008 | 🟢 |
| `project-init/SKILL.md` | 278 | sdd/project-init.md | flowcharts/project-init.md | ADR-007, 008 | 🟢 |
| `mdcu-seg/SKILL.md` | 238 | sdd/mdcu-seg.md | flowcharts/mdcu-seg.md | ADR-004, 005, 008 | 🟢 |
| `MANIFEST.md` | 67 | — (citado em vários SDDs) | — | ADR-008 | 🟢 |
| `framework-diagrama.html` | 1553 | — | — | — | — (editorial; fora de escopo) |
| `CLAUDE.md` (raiz, criado pelo Reversa) | 20 | c4-context.md | — | — | 🟡 (artefato externo) |
| `AGENTS.md` (raiz, criado pelo Reversa) | 19 | c4-context.md | — | — | 🟡 (artefato externo) |

---

## Cobertura por spec gerada

| Categoria | Quantidade | Detalhe |
|---|---:|---|
| Inventários (Scout) | 2 | inventory.md, dependencies.md |
| Contexto JSON (Scout) | 1 | surface.json |
| Análise técnica (Archaeologist) | 2 | code-analysis.md, data-dictionary.md |
| Flowcharts Mermaid (Archaeologist) | 5 | um por skill |
| Contexto JSON (Archaeologist) | 1 | modules.json |
| Domínio + estado + permissões (Detective) | 3 | domain.md, state-machines.md, permissions.md |
| ADRs retroativos (Detective) | 8 | adrs/001..008-*.md |
| Visão arquitetural (Architect) | 6 | architecture.md, c4-context, c4-containers, c4-components, erd-complete, spec-impact-matrix |
| Specs SDD por componente (Writer) | 5 | sdd/{mdcu,rsop,commit-soap,project-init,mdcu-seg}.md |
| User Stories (Writer) | 1 | user-stories/comandos-de-invocacao.md |
| Code/Spec Matrix (Writer) | 1 | este arquivo |
| Decisões do usuário (Reversa) | 1 | .reversa/context/decisions.md |
| **TOTAL** | **36 arquivos** | (mais 8 ADRs e 5 flowcharts em subdiretórios) |

---

## Arquivos sem spec correspondente ("—")

- **`framework-diagrama.html`** — documentação visual editorial. Não é spec executável. Decisão: fora do escopo do Reversa. Pode ser referenciada nos `c4-*.md` como anexo visual.

---

## Cobertura estimada do framework

**~95%** 🟢

Justificativa:
- 5/5 skills têm SDD completa com Critérios de Aceitação em Gherkin.
- 9/9 artefatos em disco têm schema documentado (data-dictionary.md).
- 8 ADRs retroativos cobrem a evolução até v2026.04.
- 7 máquinas de estado cobrem fluxos com transições não-triviais.
- 16 proibições absolutas + autoridades explícitas mapeadas.
- ~5% restante são lacunas declaradas (i18n, naming SOAP, multi-humano, version frontmatter, hooks fora do repo) — todas registradas como `decisions.md` D-001/D-002 (resolvidas) ou `LAC-D-*` no domain.md (pendentes para Iago decidir).

---

## Lacunas 🔴 metodológicas

- **OpenAPI ausente:** descartado por ausência de REST/GraphQL. **Não é lacuna — é não-aplicabilidade.**
- **User stories tradicionais (com personas múltiplas e jornadas longas):** o framework tem **uma persona principal** (engenheiro adotando metodologia) — stories são curtas e de invocação. Adequado ao domínio.
- **Code coverage de testes:** **inaplicável** — framework não tem código executável; "validação" é por uso real e iteração via SOAPs.
