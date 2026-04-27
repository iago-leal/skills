# ADR-002 — RSOP desmembrada como skill autônoma invocável pelo MDCU

- **Status:** Aceito
- **Data:** 2026-04-15
- **Commit-fonte:** `c25308b` (refactor) e `d2b3d0c` (feat anterior, RSOP como componente embutido) 🟢
- **Confiança:** 🟢 CONFIRMADO (refactor explícito)

## Contexto

Em `d2b3d0c`, o RSOP era apresentado como **componente embutido** dentro do MDCU. Imediatamente em seguida (`c25308b`, mesma data), foi promovido a **skill autônoma**. A motivação não está documentada na mensagem do refactor, mas é inferível pelo padrão do framework:
- RSOP é um conceito reutilizável (qualquer engenheiro adotando "prontuário do software" se beneficia, mesmo sem usar MDCU).
- Manter embutido acoplaria o ciclo de vida do RSOP ao do MDCU.

## Decisão

`rsop` vira skill independente. MDCU passa a invocá-la como dependência declarada.

## Consequências
- ✅ RSOP utilizável standalone (`/rsop init`, `/rsop dados`, etc.).
- ✅ MDCU pode evoluir sem mexer em RSOP.
- ✅ Habilita ADR-005 (mdcu-seg também usa RSOP).
- ⚠️ Introduziu o risco de versões desencontradas — mitigado parcialmente por release-train (MANIFEST.md), mas o gap D-001 (frontmatter sem `version`) ainda torna isso opaco.
