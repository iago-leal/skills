# SOAP — 2026-04-16 — MDCU v2 com Gate de Segurança e Gate de Integração

- **Problemas da lista abordados:** #3 (MDCU v1 sem gates — agora passivo), #4 (CLAUDE.md desatualizado — agora passivo), #5 (edição no espelho de execução — agora passivo). Problemas #1 e #2 identificados nesta sessão e adicionados como ativos.
- **Participantes:** Iago (usuário/dono), Claude (engenheiro).

## S — Subjetivo
- Motivo do contato (expresso): criar skill(s) para gerar testes e integrações, pois testes isolados podem mascarar bugs de integração; criar skill para segurança cibernética, LGPD, exposição de BD e prompt injection.
- Motivo real (implícito): lacuna estrutural no MDCU — o método permitia omissão silenciosa de segurança e de validação integrada.
- Contexto: iniciativa do usuário, não programada. Gatilho foi projeto `medicina_leal` em produção com dados pessoais sensíveis, chaves de API de LLM, e insegurança declarada do usuário sobre o tema segurança.
- Mapa de demandas: sequência lógica "mudança → teste isolado → teste integrado verde → deploy" + cobertura de segurança na Avaliação e no Plano.
- Mapa de queixas: "muito inseguro com segurança cibernética, LGPD"; "sem isso, todo o resto fica comprometido".
- SIFE: sentimento de insegurança/prevenção; ideia de que gaps de integração geram bugs futuros; impacto na confiança para evoluir o Medicina Leal; expectativa de processo que impeça omissão.
- Já tentou: nada prévio. Preocupação é preventiva, disparada por programador experiente que o usuário ouviu (não ferida em aberto).

## O — Objetivo
- MDCU v1 (antes desta sessão): 7 fases, sem gates obrigatórios, artefatos 03/04/05 sem campos específicos para superfície de ataque ou estratégia de testes.
- Skills existentes na categoria: `engineering:testing-strategy`, `engineering:code-review`, `engineering:deploy-checklist` — genéricas, não cobrem LGPD/dados médicos/chaves de LLM com a especificidade do caso.
- `medicina_leal`: em produção desde 12/04/2026 em `https://portal.medicinaleal.com/`. Usa Gemini + OpenAI (chaves), SQLite para usuários, dados de pacientes em volume no host, service account Google. Tem staging com testes automatizados rodando.
- Estrutura física do repo skills descoberta durante a sessão: fonte da verdade em `~/Desktop/github_repos/skills/mdcu-framework/`, espelho em `~/.claude/skills/`. Edições iniciais foram feitas por engano no espelho e migradas em seguida para o repo.
- Conteúdo do repo antes da sessão: `commit-soap`, `mdcu` (v1), `rsop` em `mdcu-framework/`; `claude_delegate/` na raiz; `rsop/soap/` vazio.
- CLAUDE.md do repo antes da sessão: descrevia estrutura antiga (`MDCU/` em caixa alta), sem menção a `commit-soap`/`teste-integrado`/`seguranca-dados`, sem política de distribuição.

## A — Avaliação
- **Problema #3 (MDCU v1 sem gates — agora passivo):** diagnóstico preciso. Hipótese confirmada: o método permitia plano aprovado sem threat modeling e execução declarada concluída sem teste integrado. Gravidade alta em projetos com dados pessoais (caso `medicina_leal`). Severidade reduzida a zero após MDCU v2.
- **Problema #4 (CLAUDE.md desatualizado — agora passivo):** documentação descrevia um estado que não era mais real. Impacto prático: orientação equivocada para quem (inclusive Claude) ler o repo. Resolvido.
- **Problema #5 (edição no espelho — agora passivo):** violação de política do próprio usuário ("repo é fonte da verdade"). Corrigido com symlinks unidirecionais — modelo mental "editar o repo = atualizar o global" agora é fato mecânico, não disciplina.
- **Problema #1 (migração v1→v2 — novo ativo):** projetos em andamento com artefatos v1 não têm os campos novos. Decisão de compatibilidade pendente: backfill obrigatório, oportunístico, ou coexistência permanente?
- **Problema #2 (skills sem suíte automática — novo ativo):** dissonância dogfooding — o framework agora exige gate de integração de projetos clientes mas o próprio repo de skills não tem. Não há como definir "teste integrado de uma skill" sem desenho dedicado.

## P — Plano
- **Problema #1:** reavaliar em 30 dias (após primeiro uso do MDCU v2 em `medicina_leal`). Se o atrito for baixo, aceitar coexistência permanente. Se alto, adicionar modo `/mdcu migrar-v2` que faça backfill guiado dos campos.
- **Problema #2:** deixar em observação. Só intervir se houver regressão observada em skill. Intervenção possível no futuro: definir "teste integrado de skill" como "cenário de invocação documentado + verificação de artefato produzido".
- **Nada a mudar agora** nos problemas passivos — só monitorar reativação.
- **Reflexões:**
  - Fase 2 (Escuta) foi razoável — capturei demanda, queixa e o "programador experiente" como gatilho não-patológico. Poderia ter perguntado mais cedo sobre o estado do Medicina Leal para ancorar concreto.
  - Fase 5 teve decisão compartilhada de fato — o usuário reverteu minha recomendação educacional para operacional em `seguranca-dados`. Isso é coautoria, não validação passiva. Respeitei a decisão mas mantive o disclaimer de falsa sensação de segurança.
  - Falha operacional: editei inicialmente em `~/.claude/skills/` em vez do repo. O usuário corrigiu explicitamente. Regra agora registrada em memory `skills_sync_policy.md`.
  - Viés de pressa: quase avancei para SOAP sem checar onde o RSOP deveria viver. Corrigi com `list_projects` do MCP, mas gastei ciclos que poderiam ter sido evitados perguntando antes.
