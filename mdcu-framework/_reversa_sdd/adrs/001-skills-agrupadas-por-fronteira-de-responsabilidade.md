# ADR-001 — Skills agrupadas em `mdcu-framework/` por fronteira de responsabilidade

- **Status:** Aceito
- **Data:** 2026-04-15
- **Commit-fonte:** `ad125f9` 🟢
- **Confiança:** 🟢 CONFIRMADO (extraído da própria mensagem A+P)

## Contexto

Inicialmente o MDCU era uma única skill monolítica (`60a9d1c`, `0420ad8`). Cresceu para abranger raciocínio (fases), registro longitudinal e geração de commit. Manter tudo em uma SKILL.md violaria a regra do agent-skills-format de que cada skill tem responsabilidade única e descrição ≤ 1024 chars.

## Decisão

Quebrar em **3 skills com fronteira clara**, agrupadas em `mdcu-framework/`:
- `mdcu` — raciocínio (fases F1–F6)
- `rsop` — registro longitudinal (SOAP + lista de problemas)
- `commit-soap` — selo de fechamento (commit derivado de SOAP)

## Consequências
- ✅ Cada skill cabe em uma janela de descrição e em um propósito.
- ✅ `commit-soap` e `rsop` ficam reutilizáveis fora do MDCU (se alguém quiser).
- ✅ Manutenção independente.
- ⚠️ Custo de coordenação entre skills passa a ser explícito (necessário documentar dependências) — endereçado por ADR-003.
