# ADR-005 — `mdcu-seg` substitui `seguranca-dados` e `teste-integrado`

- **Status:** Aceito (substitui parcialmente ADR-004)
- **Data:** 2026-04-17
- **Commit-fonte:** `e06fa1a` 🟢
- **Confiança:** 🟢 CONFIRMADO

## Contexto

A versão 2 do MDCU (ADR-004) introduziu duas skills auxiliares: `seguranca-dados` (gate de segurança em F4→F5) e `teste-integrado` (gate de integração em F6 pré-deploy). Em uso real (ver commit anterior `4415d44` que tentou compor essas skills com nativas `engineering:*`), aparentemente:
- A separação entre "segurança de dados" e "teste integrado" criou sobreposição confusa.
- O domínio de incident response (F0) não cabia em nenhuma das duas.
- Auditoria contínua (revisão trimestral) também não tinha lar claro.

## Decisão

Consolidar em **uma única skill `mdcu-seg`** com 3 domínios:
1. **Threat modeling** (STRIDE) — substitui o gate de segurança.
2. **Protocolo F0** (IRP 5 etapas) — novo, contenção de incidente.
3. **Auditoria contínua** (`rsop/seguranca.md`) — vigilância longitudinal.

`teste-integrado` foi removido (não há substituto direto neste commit; aparentemente abolido em favor de testes idiomáticos por stack via `ARCHITECTURE.md`).

## Consequências
- ✅ Domínio de segurança coerente e completo (preventivo + corretivo + vigilância).
- ✅ Aplicação explícita de Wilson-Jungner (rastreio populacional) ao software.
- ✅ Reduz superfície de skills do framework.
- ⚠️ Gate de integração foi **removido** sem substituto formal nesta release. **Resolvido em 2026-04-27 (questions.md P9):** Iago decidiu pela opção (b) — adicionar **regra explícita ao MDCU F6 pré-fechamento** vinculando os comandos `test`/`build` do `ARCHITECTURE.md.Comandos principais` (ver `sdd/mdcu.md` Regras de Negócio + Critérios de Aceitação atualizados). Não revive a skill `teste-integrado`; o gate vive dentro do MDCU.
