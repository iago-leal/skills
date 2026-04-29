# SOAP 2026-04-28 — RSOP sync com GitHub Issues (design F2/Plano)
- Problemas: #8, #9

## S
**Demandas**
- adicionar sincronização bidirecional opt-in entre RSOP e GitHub Issues (#8)
- substituir códigos de severidade opacos `[M]/[B]` por taxonomia auto-explicativa (#9)

**Queixas**
- RSOP atual é offline-first puro — sem mecanismo de visibilidade ou colaboração externa
- mapeamento RSOP↔Issues é quase 1:1 (problema↔issue, SOAP↔comentário, fase MDCU↔milestone) e nunca foi explorado
- códigos `[M]/[B]` não são auto-explicativos; autor admitiu não recordar significado

**Notas**
- usuário não tinha visto a possibilidade do mapeamento até esta sessão
- preferência forte por `markdown como fonte da verdade` — GitHub é espelho, não destino
- F1 dispensada (problema já formulado pelo usuário); sessão começou direto em F2/Plano

## O
- estrutura RSOP atual: `dados_base.md`, `lista_problemas.md` (4 ativos pré-sessão: #2, #5, #6, #7), `passivos.md`, `soap/` (5 SOAPs em 2026-04-27)
- schema vigente de ATIVOS: `# | Problema | Tipo | Revisitar | Desde | Últ. SOAP`; coluna Tipo distingue consciente×acidental-default; severidade prefixada `[M]/[B]` no campo Problema
- `commit-soap` já lê SOAP da sessão e formata commit A+P; integração com Issues (`Refs #N` / `Closes #N`) é aditiva, não-quebrante
- `gh` CLI disponível no ambiente — sem dependência adicional
- regra global: nunca incluir trailer Co-Authored-By em commits

## A
1. #8 design fechado: sync bidirecional opt-in via `.rsop/config.yml`, markdown autoritativo, conflito = abort+diff (nunca merge automático), bootstrap reverso permitido
2. #9 taxonomia `[CRT]` crítico / `[ALT]` alto / `[MED]` médio / `[BAI]` baixo substitui `[M]/[B]` com critério explícito por código

## P
1. #8 implementação RSOP sync GitHub (target: rsop v1.5.0):
   - `.rsop/config.yml` (versionado): `sync.enabled`, `provider`, `repo`, `labels_prefix`, `milestone_strategy`, `redact_patterns`
   - `.rsop/.sync-ledger.json` (gitignored, regenerável): mapping `RSOP-N → {issue_number, last_synced_hash, last_synced_at}`
   - subcomandos: `--sync-init`, `--sync-status` (dry-run), `--sync-pull`, `--sync-push`, `--sync` (bidirecional pull→push)
   - mapeamento canônico:
     - problema #N ↔ issue com título `[RSOP-N] slug-do-problema`
     - severidade ↔ label `rsop:sev-{crt|alt|med|bai}`
     - dívida consciente ↔ label `rsop:divida-consciente`
     - SOAP inteiro ↔ um comentário com header `## SOAP YYYY-MM-DD`
     - fase MDCU corrente ↔ milestone `MDCU-F{1..6}`
     - `passivos.md` ↔ issues fechadas (espelho exato)
   - bootstrap reverso: `--sync-init` em repo com issues `[RSOP-*]` e markdown vazio reconstrói `lista_problemas.md` + `soap/` a partir das issues
   - integração `commit-soap`: parse de IDs em P; `Refs #N` para problemas tocados, `Closes #N` quando o problema migra para `passivos.md` na mesma sessão; sem Co-Authored-By
   - segurança: `redact_patterns` regex aplicado a SOAPs antes de upload (tripwire para chaves API/AWS, não defesa-em-profundidade)
   - aguarda implementação
2. #9 reforma de severidade (target: rsop v1.5.0, casado com #8):
   - novo schema: `[CRT]` bloqueia uso ou expõe segredo; `[ALT]` degrada experiência ou correção; `[MED]` melhoria significativa; `[BAI]` nice-to-have
   - critério explícito documentado em `rsop/SKILL.md`
   - migração automática: `[M]→[MED]`, `[B]→[BAI]`
   - ortogonal à coluna Tipo (consciente×acidental) — severidade e tipo são dois eixos independentes
   - aguarda implementação

## R
- `markdown como fonte da verdade + GitHub como espelho` preserva o princípio do RSOP (prontuário no próprio repositório) sem renunciar à colaboração; resiliência: se um lado é perdido, o outro reconstrói
- bootstrap reverso é o que torna o sync verdadeiramente bidirecional — sem ele, markdown seria mestre rígido e GitHub mero replica
- F2/Plano dogfoodada: design discutido nesta sessão foi documentado *antes* da implementação, conforme o próprio MDCU prega — coerência epistêmica entre framework e seu próprio uso
