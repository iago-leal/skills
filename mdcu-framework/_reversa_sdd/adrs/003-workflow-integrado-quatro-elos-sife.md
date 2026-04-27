# ADR-003 — Workflow integrado de 4 elos + SIFE no SOAP

- **Status:** Aceito
- **Data:** 2026-04-15
- **Commit-fonte:** `f1e840c` 🟢
- **Confiança:** 🟢 CONFIRMADO (mensagem A+P explícita)

## Contexto

Após ADR-001/002 separar as 3 skills, a relação entre elas era implícita. SOAPs estavam sendo escritos sem disciplina suficiente — "S e O ruins viravam A e P confusos".

## Decisão

1. Declarar **workflow canônico de 4 elos**: `MDCU → Execução → RSOP → commit-soap`.
2. MDCU declara dependência **explícita** de RSOP e commit-soap.
3. RSOP ganha **disciplina de escrita do SOAP**:
   - S separa Demandas × Queixas
   - SIFE como instrumento de demanda oculta
   - A ≤ 5 palavras por item; P 1:1 com A; R uma linha
4. RSOP ganha "posicionamento no workflow" — explica de onde vem e para onde vai cada artefato.

## Consequências
- ✅ Coerência epistemológica: o SOAP fica auditável contra disciplina (não contra estilo subjetivo).
- ✅ Habilita formato de commit-soap baseado em A+P.
- ✅ Ataca o anti-padrão "compensar S/O ruins com A/P prolixo".
- ⚠️ Aumenta a barreira de entrada do RSOP (mais regras a aprender) — trade-off explícito.
