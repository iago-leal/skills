# ADR-008 — Release-train `v2026.04` com 6 patches consolidados

- **Status:** Aceito
- **Data:** 2026-04-20 (data do MANIFEST)
- **Fonte:** `MANIFEST.md` 🟢
- **Confiança:** 🟢 CONFIRMADO

## Contexto

Após uma série de mudanças incrementais (ADRs 001–007), surgiu a necessidade de **consolidar uma versão coerente** das 5 skills. Sem release-train, cada skill teria seu próprio versionamento e os usuários teriam dificuldade em saber "qual conjunto consistente instalar".

## Decisão

Adotar **release-train com naming `vAAAA.MM`**: `v2026.04`. O `MANIFEST.md` declara a versão e enumera os 6 patches aplicados:

| # | Patch | Skill alvo |
|---|---|---|
| 1 | Prontuário de rascunho (`_mdcu.md` com S:/O:, leitura em F6) | mdcu |
| 2a | Micro-commits permitidos em F6 | mdcu |
| 2b | `commit-soap` exclusivo para fechamento (não WIP) | commit-soap |
| 3 | `passivos.md` como arquivo morto; `lista_problemas.md` só com ativos | rsop |
| 4 | Disjuntor 2/2 em F6 + exit protocol | mdcu |
| 5 | Gatilho de conformidade `ARCHITECTURE.md` em F1 | mdcu |
| 6 | Gestão Determinística de Dependências | project-init (nova) |

Validações de release:
- Todas as 5 skills com `description` ≤ 1024 caracteres (limite Claude).
- Nome `_mdcu.md` padronizado entre skills que o referenciam.

## Consequências
- ✅ Conjunto coerente de skills entregável de uma vez.
- ✅ Rastreabilidade de mudanças por patch (mapeada à skill alvo).
- ✅ Disciplina de validação (limite de chars do `description`).
- ⚠️ **Versionamento do conjunto, não das skills individuais** — daí o gap D-001 (skills sem `version` no frontmatter). O usuário só sabe qual versão tem se o `MANIFEST.md` veio junto, o que não acontece quando se instala via `cp -R` em `~/.claude/skills/`.
- ⚠️ Sem changelog automatizado — patches ficam apenas no `MANIFEST.md` desta release. Próximo release-train precisa reconstituir a lista.
