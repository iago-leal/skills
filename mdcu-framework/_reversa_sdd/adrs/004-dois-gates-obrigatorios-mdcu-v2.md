# ADR-004 — Dois gates obrigatórios no MDCU v2 (Segurança e Integração)

- **Status:** Substituído por ADR-005 (consolidação em mdcu-seg)
- **Data:** 2026-04-16
- **Commit-fonte:** `2265776` 🟢
- **Confiança:** 🟢 CONFIRMADO (commit longo descreve a decisão completa)

## Contexto

Sem gates explícitos, o MDCU permitia "omissão silenciosa" em segurança e integração — o agente podia passar de F4 para F5 ignorando que havia nova superfície de ataque, ou de F6 para deploy sem validação integrada. O risco crescia com a adoção do framework em projetos com PII / LLM / chaves.

## Decisão

Adicionar **dois gates não-opcionais**:

1. **Gate de Segurança (Fase 4→5)** — aciona skill `seguranca-dados` quando há nova superfície de ataque (LLM, BD, chaves, LGPD).
2. **Gate de Integração (Fase 6 pré-deploy)** — aciona skill `teste-integrado` exigindo:
   - teste isolado verde
   - suíte integrada verde
   - critério objetivo do plano cumprido

Adicionar **regras 10 e 11** ao MDCU tornando os gates não-opcionais.

Como subproduto, **inicializar RSOP do próprio repo** em `rsop/` com `dados_base.md`, `lista_problemas.md` e primeiro SOAP — dogfooding.

Distribuição para `~/.claude/skills/` formalizada como **symlinks unidirecionais**.

## Consequências
- ✅ Eliminada a omissão silenciosa em segurança.
- ✅ Dogfooding melhora a robustez (problemas do framework viram `#` no próprio framework).
- ✅ Symlinks evitam cópias desencontradas.
- ⚠️ Duas skills novas (`seguranca-dados`, `teste-integrado`) — complexidade extra.
- ⚠️ Esta decisão **foi parcialmente revogada** por ADR-005: `seguranca-dados` e `teste-integrado` foram unificadas em `mdcu-seg`.
