# Lista de problemas — Ativos
- **Projeto:** mdcu-framework — **Última revisão:** 2026-04-27

| # | Problema | Desde | Últ. SOAP |
|---|----------|-------|-----------|
| 1 | [A] tese-formalizacao — F-1 a F-5 não codificadas em artefatos canônicos do framework | 2026-04-27 | 2026-04-27 |
| 2 | [M] arquitetura-md-ausente — framework não tem ARCHITECTURE.md próprio; contrato vive em `framework/` + `MANIFEST.md` (exceção justificada, dívida consciente) | 2026-04-27 | 2026-04-27 |
| 3 | [M] divida-consciente-schema — `lista_problemas.md` não distingue dívida consciente × acidental, sem prazo de revisitar (PLANEJAMENTO §5.1) | 2026-04-27 | 2026-04-27 |
| 4 | [M] glossario-canonico-promocao — termos canônicos promovidos para `framework/glossary.md` (versionado); `_reversa_sdd/domain.md` mantém termos extraídos por Reversa (gitignored) — resolvido nesta sessão | 2026-04-27 | 2026-04-27 |
| 5 | [B] dogfooding-suite-executavel — dogfooding atual é estático (Reversa); falta suite que rode em CI (PLANEJAMENTO §6.2) | 2026-04-27 | 2026-04-27 |
| 6 | [B] protocolo-sign-out — protocolo de transferência de caso entre orquestradores não documentado (PLANEJAMENTO §6.3) | 2026-04-27 | 2026-04-27 |
| 7 | [B] rubrica-scorer-distillate — análogo skill-spec rubric pro distillate canônico (PLANEJAMENTO §6.4); teto art-craft declarado em F-4 | 2026-04-27 | 2026-04-27 |
| 8 | [A] f6-reformulacao — F6 reformulada em 3 sub-blocos (F6.a delegação ao engine + modo monolítico declarado / F6.b acompanhamento com Disjuntor / F6.c tradução de retorno + fechamento). Lock file rule migrou para #9. Aguarda /rsop revisar para ir a passivos | 2026-04-27 | 2026-04-27 |
| 9 | [M] project-init-tradutor — split em duas skills: project-init (interface + extração de contrato → ARCHITECTURE.md) e project-setup nova (materialização técnica em modo desacoplado/monolítico declarado). Aguarda /rsop revisar | 2026-04-27 | 2026-04-27 |
| 10 | [M] precisa-resolver-codificacao — eixo precisa-resolver × não-precisa-resolver hoje só em prosa (RN-D-015); enriquecer schema da `lista_problemas.md` com coluna Status | 2026-04-27 | 2026-04-27 |
| 11 | [M] commit-soap-desacoplamento — commit-soap v2.0.0 desacoplado: aceita SOAP (default), --from <path> ou --inline; selo de qualquer marco longitudinal (sessão MDCU, project-setup, refresh, release). Aguarda /rsop revisar | 2026-04-27 | 2026-04-27 |
