# Lista de problemas — Ativos
- **Projeto:** mdcu-framework — **Última revisão:** 2026-04-28

| # | Problema | Tipo | Revisitar | Desde | Últ. SOAP |
|---|----------|------|-----------|-------|-----------|
| 2 | [M] arquitetura-md-ausente — framework não tem ARCHITECTURE.md próprio; contrato vive em framework/ + MANIFEST.md | consciente | ao distribuir framework para projeto-cliente externo | 2026-04-27 | 2026-04-27 |
| 5 | [B] dogfooding-suite-executavel — dogfooding atual é estático (Reversa); falta suite que rode em CI | | release-train v2026.06+ | 2026-04-27 | 2026-04-27 |
| 6 | [B] protocolo-sign-out — protocolo de transferência de caso entre orquestradores não documentado | | | 2026-04-27 | 2026-04-27 |
| 7 | [B] rubrica-scorer-distillate — reformulado: scorer numérico rejeitado por incompatibilidade com F-4 + P-5; checklist binário de 10 itens em rsop/SKILL.md (v1.4.0) auto-aplicado em F6.c. Aguarda /rsop revisar | | | 2026-04-27 | 2026-04-27 |
| 8 | [M] rsop-sync-github-ausente — RSOP é offline-first puro; falta sync bidirecional opt-in com GitHub Issues como espelho (problema↔issue, SOAP↔comentário, fase MDCU↔milestone, passivos↔fechadas). Design fechado em SOAP 2026-04-28; aguarda implementação | | rsop v1.5.0 | 2026-04-28 | 2026-04-28 |
| 9 | [M] severidade-codigo-opaco — códigos `[M]/[B]` em schema lista_problemas não são auto-explicativos; autor não recorda significado após semanas. Reforma para `[CRT]/[ALT]/[MED]/[BAI]` com critério explícito por código; migração automática `[M]→[MED]`, `[B]→[BAI]` | | rsop v1.5.0 (casado com #8) | 2026-04-28 | 2026-04-28 |
