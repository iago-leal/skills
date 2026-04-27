# Lacunas remanescentes — mdcu-framework

> Gerado pelo Reversa Reviewer em 2026-04-27
> Última atualização: rodada 2 de respostas (todas as 10 perguntas respondidas).

---

## Lacunas pendentes (0)

🟢 **Nenhuma lacuna pendente.** Todas as 10 perguntas geradas pela Reviewer foram respondidas e processadas em duas rodadas.

---

## Histórico de resoluções

### Rodada 0 (decisões prévias à Reviewer)

| ID | Lacuna | Resolução | Origem |
|---|---|---|---|
| ✅ D-001 | Frontmatter sem `version` | **Gap** confirmado em 2026-04-27; convenção definida em P10 | decisions.md |
| ✅ D-002 | Reversa scaffolding no repo | **`.gitignore`** criado em 2026-04-27 | decisions.md |

### Rodada 1 (questions.md, 5 respostas)

| Pergunta | Lacuna | Resolução | Spec atualizada |
|---|---|---|---|
| ✅ P3 | `/commit-soap` com SOAP A vazio | **ABORTA com aviso** | sdd/commit-soap.md (Fluxos + Gherkin) |
| ✅ P4 | `/commit-soap --amend` em commit não-soap | **AVISA antes** | sdd/commit-soap.md (Fluxos + Gherkin) |
| ✅ P5 | Naming `<contexto>` em SOAP | **Livre** (sem convenção forçada) | data-dictionary.md |
| ✅ P6 | Idioma canônico | **pt-BR canônico, robusto operacional em EN; i18n NÃO neste release** | architecture.md (seção 6) |
| ✅ P7 | Multi-humano | **`_mdcu.md` compartilhado**, `Co-authored-by:` PADRÃO Git para humanos, LLMs proibidos | sdd/mdcu.md, permissions.md |

### Rodada 2 (questions.md, 5 respostas finais)

| Pergunta | Lacuna | Resolução | Spec atualizada |
|---|---|---|---|
| ✅ P1 | `/rsop soap` sem `_mdcu.md` | **Pergunta cenário** (A: SOAP em branco / B: guiado curto / C: aborta com recuperação) | sdd/rsop.md (Fluxos + Gherkin) |
| ✅ P2 | `/rsop init` em diretório existente | **ABORTA com aviso**, sugere `/rsop reset` e `/rsop repair` (roadmap) | sdd/rsop.md (Fluxos + Interface roadmap + Gherkin) |
| ✅ P8 | Hooks programáticos fora do repo | **Nova skill `mdcu-hooks`** versionada com JSON-spec; `/mdcu-hooks install` aplica no engine ativo | architecture.md (D-004 resolvida + versão 0.1.0), c4-containers.md (diagrama futuro), sdd/mdcu.md |
| ✅ P9 | Gate de integração removido | **Nova regra ao MDCU F6** vinculando `test`/`build` antes de `/mdcu fechar` | sdd/mdcu.md (regra + Gherkin + Prioridade), adrs/005 atualizado |
| ✅ P10 | Convenção de versionamento | **Semver puro por skill**; próximo release `v2026.05`; bundle continua via `MANIFEST.md` | architecture.md (seção 7 + tabela de versões iniciais) |

---

## Resumo numérico

- **Lacunas iniciais identificadas:** 10 (em `domain.md`, `permissions.md`, `architecture.md`, SDDs).
- **Resolvidas pelo usuário antes da revisão:** 2 (D-001, D-002).
- **Resolvidas na rodada 1:** 5 (P3, P4, P5, P6, P7).
- **Resolvidas na rodada 2:** 5 (P1, P2, P8, P9, P10).
- **Pendentes:** **0**. ✅

---

## Roadmap derivado da rodada 2 (próximo release `v2026.05`)

| Item | Tipo | Skill afetada | Decisão |
|---|---|---|---|
| Adicionar `version` ao frontmatter de todas as 5 skills | semver puro | todas | P10 |
| Implementar Gate de Integração em F6 (vincular `test`/`build`) | nova regra | `mdcu` 3.0.0 | P9 |
| Especificar comportamentos `/rsop soap` sem `_mdcu.md` (3 cenários) | UX | `rsop` 1.2.0 | P1 |
| Especificar comportamento `/rsop init` em diretório existente | UX | `rsop` 1.2.0 | P2 |
| Implementar comandos `/rsop reset` e `/rsop repair` (roadmap) | nova superfície | `rsop` 1.3.0 ou skill nova | P2 |
| Especificar `/commit-soap` com SOAP A vazio (ABORTA) | UX | `commit-soap` 1.1.0 | P3 |
| Especificar `/commit-soap --amend` (AVISA antes) | UX | `commit-soap` 1.1.0 | P4 |
| Promover multi-humano de Won't para Should em `mdcu/SKILL.md` | nova seção | `mdcu` 3.0.0 | P7 |
| Adicionar seção "Idioma" canônico ao `mdcu/SKILL.md` ou ao README | meta | todas | P6 |
| **Criar skill nova `mdcu-hooks`** com `hooks-spec.json` e comandos `install/check/uninstall` | nova skill | `mdcu-hooks` 0.1.0 | P8 |

---

## Item ainda em aberto (sem severidade — sugestão futura)

- **D-CHANGELOG** (severidade `[B]`): sem changelog automatizado entre release-trains. Sugestão: extrair de `git log --grep="A:"` no diretório do framework. Não é lacuna do framework em si; é melhoria de tooling. Pode entrar em release futuro.
