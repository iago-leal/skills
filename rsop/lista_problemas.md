# Lista de problemas
- **Projeto:** skills
- **Última revisão:** 2026-04-16

## Problemas ativos

| # | Problema | Desde | Nível de resolução | Severidade | Notas |
|---|----------|-------|--------------------|------------|-------|
| 1 | Projetos MDCU v1 em andamento não têm os campos novos dos artefatos 03/04/05 (Superfície de ataque, Ameaças e LGPD, Estratégia de testes, Gate de Integração). Migração opcional mas não automatizada. | 2026-04-16 | diagnóstico | baixa | Decisão em aberto: forçar backfill ou aceitar convivência v1/v2. |
| 2 | Skills do framework MDCU não têm suíte automática de validação. Validação é observacional — mudança pode regredir comportamento sem detecção. Dissonante com o próprio Gate de Integração que o framework agora exige de projetos que o adotam. | 2026-04-16 | hipótese | média | Candidato a dogfooding: aplicar `teste-integrado` ao próprio repo skills. Requer definir o que é "teste integrado" de uma skill (cenário de invocação + verificação de artefato). |

## Problemas passivos

| # | Problema | Período ativo | Motivo de inativação | Pode reativar? | Notas |
|---|----------|---------------|----------------------|----------------|-------|
| 3 | MDCU v1 não tinha gates obrigatórios para segurança (LGPD, prompt injection, chaves, BD, logs) nem para integração pré-deploy. Permitia omissão silenciosa de ambas as dimensões em plano e execução. | antes de 2026-04-16 | MDCU v2 introduz Gate de Segurança (Fase 4→5) e Gate de Integração (dentro da Fase 6) como regras 10 e 11, com skills `seguranca-dados` e `teste-integrado` materializando a operação. | Sim, se alguém editar o MDCU removendo os gates ou se os gates forem contornados na prática. | Ver `soap/2026-04-16_mdcu-v2-gates.md`. |
| 4 | CLAUDE.md do repo desatualizado com estrutura antiga (`MDCU/` em caixa alta, sem `mdcu-framework/`, sem menção a commit-soap, teste-integrado, seguranca-dados, sem política de symlinks). | antes de 2026-04-16 | Reescrito em 2026-04-16 com estrutura real, as 5 skills do `mdcu-framework/`, convenção kebab-case lowercase e seção **Distribuição** com política de symlinks. | Sim, se novas skills forem adicionadas sem atualizar o CLAUDE.md. | Ver `soap/2026-04-16_mdcu-v2-gates.md`. |
| 5 | Skills sendo editadas diretamente em `~/.claude/skills/` (espelho de execução) em vez do repo versionado — quebra rastreabilidade e perde mudanças em próxima sincronização. | sessão de 2026-04-16 (antes da correção) | Estabelecida política unidirecional repo → global com symlinks. As 5 skills em `~/.claude/skills/` agora apontam para `mdcu-framework/`. | Sim, se alguém destruir os symlinks e recriar diretórios reais no global. | Memória pessoal registrada em `~/.claude/projects/-Users-iagoleal-Desktop-github-repos/memory/skills_sync_policy.md`. |
