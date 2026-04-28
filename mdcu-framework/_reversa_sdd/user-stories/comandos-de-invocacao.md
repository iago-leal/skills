# User Stories — Gatilhos de invocação do mdcu-framework

> Gerado pelo Reversa Writer em 2026-04-27.
> Adaptação: o framework não tem UI; suas "user stories" são os **gatilhos de invocação documentados em `description:` de cada SKILL.md** + os comandos `/`. Cada story aqui mapeia uma intenção do usuário a uma skill ativada.

---

## Persona principal

**Engenheiro/desenvolvedor adotando o mdcu-framework como metodologia de trabalho.** Trabalha com um agente de IA (Claude Code / Codex / Cursor / Gemini CLI) carregando as 5 skills do framework. Conhece os comandos `/`. É coautor das decisões — não apenas validador.

Personas secundárias citadas mas não-interativas: Stakeholder do projeto-cliente, DPO/responsável (LGPD), Time.

---

## Stories — Skill `mdcu`

### US-MDCU-001 — Iniciar uma sessão estruturada para um problema novo
> Como **engenheiro**,
> quero **iniciar um ciclo metodológico para um problema técnico que vou enfrentar**,
> para **escutar o problema antes de saltar para solução**.

**Trigger:** `/mdcu` ou frase do usuário "vamos resolver X", "preciso entender Y", "como abordar Z?".
**Skill ativada:** `mdcu` (e cascateia para `project-init` se `ARCHITECTURE.md` ausente).
**Critério de sucesso:** `_mdcu.md` criado, F1 ativa, gatilho de conformidade aplicado.

### US-MDCU-002 — Reenquadrar um problema durante a execução
> Como **engenheiro**,
> quero **voltar à escuta quando percebo que o problema sendo resolvido ≠ problema descrito**,
> para **evitar entregar a coisa certa para o problema errado**.

**Trigger:** `/mdcu reenquadrar` ou frase "espera, isso não é bem o problema", "vou repensar".
**Skill ativada:** `mdcu` (incrementa contador se em F6).
**Critério:** counter atualizado em `_mdcu.md`; retorno a F2 ou F3.

### US-MDCU-003 — Ser interrompido quando estou em loop
> Como **engenheiro**,
> quero **que o agente PARE de tentar quando eu o vejo iterando sem progresso**,
> para **não consumir API e não perder tempo**.

**Trigger:** **automático** quando contador atinge 2/2 em F6.
**Skill ativada:** `mdcu` (Disjuntor).
**Critério:** exit protocol fixo de 5 campos exibido; agente aguarda decisão humana sem sugerir caminho.

### US-MDCU-004 — Salvar e fechar uma sessão MDCU
> Como **engenheiro**,
> quero **destilar a sessão num SOAP e selar com commit-soap**,
> para **deixar contexto cognitivo no `git log` para mim e para o futuro agente**.

**Trigger:** `/mdcu fechar` (após F6 concluída).
**Skill ativada:** `mdcu` → cascata para `rsop` → `commit-soap`. `_mdcu.md` deletado.
**Critério:** SOAP em `rsop/soap/`, commit no git history com formato A:/P:/Refs:.

---

## Stories — Skill `rsop`

### US-RSOP-001 — Inicializar prontuário em projeto novo
> Como **engenheiro**,
> quero **criar a estrutura de prontuário longitudinal**,
> para **ter onde registrar problemas, dados base e SOAPs desde o dia 1**.

**Trigger:** `/rsop init`.
**Skill ativada:** `rsop`.
**Critério:** `rsop/{dados_base.md, lista_problemas.md, passivos.md, soap/}` criados; `passivos.md` vazio.

### US-RSOP-002 — Registrar SOAP da sessão atual
> Como **engenheiro**,
> quero **destilar S/O/A/P/R do `_mdcu.md` em arquivo permanente**,
> para **que a sessão tenha um único registro auditável**.

**Trigger:** `/rsop soap` (geralmente cascateado por `/mdcu fechar`).
**Skill ativada:** `rsop`.
**Critério:** `soap/YYYY-MM-DD_<contexto>.md` com S/O/A/P/R formatados pela disciplina (A≤5 palavras, P 1:1, R=1 linha).

### US-RSOP-003 — Ver lista de problemas ativos
> Como **engenheiro**,
> quero **ver os problemas ativos do projeto sem ruído de problemas fechados**,
> para **decidir o próximo ciclo MDCU com foco**.

**Trigger:** `/rsop lista` (ou injeção automática em `CLAUDE.md` do projeto).
**Skill ativada:** `rsop`.
**Critério:** apenas ativos exibidos; passivos NÃO incluídos.

### US-RSOP-004 — Verificar se um sintoma é regressão de bug antigo
> Como **engenheiro**,
> quero **consultar o arquivo morto de problemas resolvidos**,
> para **detectar se estou vendo regressão antes de tratar como bug novo**.

**Trigger:** `/rsop regressao N` ou frase "isso parece o bug X que resolvemos antes", "olha os passivos".
**Skill ativada:** `rsop`.
**Critério:** se sintoma corresponde, problema é reaberto em `lista_problemas.md` com nota cruzada.

### US-RSOP-005 — Limpar e reclassificar problemas
> Como **engenheiro**,
> quero **revisar a lista de problemas e mover resolvidos para passivos**,
> para **manter o índice ativo enxuto (e o system prompt do agente também)**.

**Trigger:** `/rsop revisar`.
**Skill ativada:** `rsop`.
**Critério:** problemas resolvidos migram para `passivos.md` com colunas `Fechado por`, `Fechado em`, `Reativável?`.

---

## Stories — Skill `commit-soap`

### US-CS-001 — Selar sessão MDCU com commit que preserva contexto
> Como **engenheiro**,
> quero **gerar mensagem de commit a partir do A+P do SOAP**,
> para **que `git log` mostre marcos cognitivos e não apenas "WIP" ou "fix typo"**.

**Trigger:** `/commit-soap` (geralmente cascateado por `/mdcu fechar`).
**Skill ativada:** `commit-soap`.
**Critério:** mensagem com `A:`, `P:`, `Refs:` exibida; após confirmação, commit registrado em git history.

### US-CS-002 — Auditar a história cognitiva do projeto
> Como **engenheiro**,
> quero **filtrar `git log` por avaliações, planos ou problemas específicos**,
> para **reconstituir o raciocínio sem reler todo o histórico**.

**Trigger:** comando shell — `git log --grep="A:"`, `git log --grep="P:"`, `git log --grep="#3"`, `git log --grep="Refs: rsop"`, `git log --invert-grep --grep="A:"`.
**Skill ativada:** nenhuma — é apenas shell. **A skill `commit-soap` HABILITA esse uso** ao impor o formato.
**Critério:** comandos retornam apenas commits que correspondem ao filtro.

### US-CS-003 — Reescrever último commit após SOAP atualizado
> Como **engenheiro**,
> quero **atualizar a mensagem do último commit quando ajustei o SOAP depois**,
> para **manter coerência entre o registro permanente e o git history**.

**Trigger:** `/commit-soap --amend`.
**Skill ativada:** `commit-soap`.
**Critério:** `git commit --amend` executado com nova mensagem.

### US-CS-004 — Revisar mensagem antes de comitar
> Como **engenheiro**,
> quero **ver a mensagem proposta antes de ela entrar no histórico**,
> para **corrigir síntese inadequada antes de commit irreversível**.

**Trigger:** `/commit-soap --dry-run` (ou comportamento padrão de `/commit-soap` que exibe antes de comitar).
**Skill ativada:** `commit-soap`.
**Critério:** mensagem exibida; nada comitado até confirmação.

---

## Stories — Skill `project-init`

### US-PI-001 — Estabelecer contrato técnico em projeto novo
> Como **engenheiro**,
> quero **criar `ARCHITECTURE.md`, manifesto e lock file determinístico**,
> para **que o projeto tenha terreno estável antes de qualquer ciclo MDCU**.

**Trigger:** `/project-init` ou frase "definir arquitetura", "configurar gerenciador de pacotes", "setup inicial".
**Skill ativada:** `project-init`.
**Critério:** `ARCHITECTURE.md` + manifesto + lock + `.gitignore` (com lock FORA) + commit inicial canônico.

### US-PI-002 — Atualizar contrato após mudança estrutural
> Como **engenheiro**,
> quero **registrar mudança de stack/gerenciador/guardrail sem perder histórico**,
> para **que o `ARCHITECTURE.md` continue sendo fonte única de verdade**.

**Trigger:** `/project-init --refresh`.
**Skill ativada:** `project-init`.
**Critério:** `ARCHITECTURE.md` atualizado in place; alteração registrada em changelog/ADR.

### US-PI-003 — Validar conformidade do projeto
> Como **engenheiro**,
> quero **verificar se `ARCHITECTURE.md` está coerente com o código atual**,
> para **detectar drift antes de virar débito de arquitetura**.

**Trigger:** `/project-init --check`.
**Skill ativada:** `project-init`.
**Critério:** relatório telegráfico com 4 pontos (existe? lock? bate? guardrails?).

### US-PI-004 — Ser interrompido quando o MDCU detecta ausência de contrato
> Como **engenheiro impaciente**,
> quero **que o framework PARE meu MDCU se eu esqueci de inicializar o projeto**,
> para **não acumular débito por pular a "anamnese"**.

**Trigger:** **automático** — gate `mdcu` F1 detecta `ARCHITECTURE.md` ausente.
**Skill ativada:** `project-init` (via cascata do `mdcu`).
**Critério:** mensagem "[F1 INTERROMPIDA — AUSÊNCIA DE ARCHITECTURE.md]" + invocação `/project-init`.

---

## Stories — Skill `mdcu-seg`

### US-SEG-001 — Modelar ameaças de uma feature nova
> Como **engenheiro**,
> quero **aplicar STRIDE sobre um componente que mexe com PII/auth**,
> para **identificar ameaças antes que virem incidentes**.

**Trigger:** `/mdcu-seg threat-model [escopo]` — manual ou cascateado pelo MDCU em F3 (rastreio item 1 ou 2 afirmativo) ou F5 (alternativa que falha no rastreio).
**Skill ativada:** `mdcu-seg`.
**Critério:** tabela STRIDE 6-categorias com vetor + mitigação; mitigações não-triviais viram `#` no RSOP; categorias N/A com justificativa.

### US-SEG-002 — Conter incidente em produção
> Como **engenheiro**,
> quero **executar protocolo IRP estruturado quando detecto vazamento ou comprometimento**,
> para **estancar o sangramento e preservar evidência sem improviso**.

**Trigger:** `/mdcu-seg incidente` — manual ou cascateado pelo MDCU em F6 (sinal de incidente) ou frase "vazamento", "breach", "credencial exposta".
**Skill ativada:** `mdcu-seg` (SUSPENDE MDCU ativo).
**Critério:** 5 etapas (Identificação → Contenção curta → Média → Erradicação → Recuperação → Postmortem) com timestamps; SOAP-incidente em `rsop/soap/`; postmortem blameless.

### US-SEG-003 — Manter regime de auditoria trimestral
> Como **engenheiro**,
> quero **revisar `rsop/seguranca.md` a cada 90 dias**,
> para **que o regime de segurança não vire ficção administrativa**.

**Trigger:** `/mdcu-seg auditoria` — manual ou pela própria skill que sinaliza atraso após 90d, ou em eventos estruturais (nova integração, mudança de stack, nova regulação, incidente recente).
**Skill ativada:** `mdcu-seg`.
**Critério:** 6 seções atualizadas (Classificação / Regime / Gestão de segredos / Conformidade / Histórico de incidentes / Vulnerabilidades ativas); `Próxima revisão = +90d`.

### US-SEG-004 — Saber rapidamente o estado de segurança do projeto
> Como **engenheiro** (ou auditor externo),
> quero **um resumo telegráfico do estado de segurança**,
> para **decidir se há ação imediata sem reler o `seguranca.md` inteiro**.

**Trigger:** `/mdcu-seg status` ou `/mdcu-seg`.
**Skill ativada:** `mdcu-seg`.
**Critério:** resumo: `#` segurança ativos, última auditoria, incidentes abertos.

---

## Stories transversais (multi-skill)

### US-X-001 — Adotar o framework do zero em projeto existente
> Como **engenheiro**,
> quero **trazer um projeto que já existe para o workflow MDCU**,
> para **começar a registrar prontuário longitudinal e gerar commits-SOAP**.

**Sequência:** `/project-init --refresh` (sobre projeto existente) → `/rsop init` → `/mdcu` no próximo problema → `/mdcu fechar` → `/rsop soap` + `/commit-soap` (cascata).
**Skills:** `project-init` + `rsop` + `mdcu` + `commit-soap`.

### US-X-002 — Auditar história cognitiva de um problema específico
> Como **engenheiro novo no projeto**,
> quero **entender a história longitudinal do problema #3**,
> para **saber o que foi tentado e por que ainda está aberto**.

**Sequência:** `git log --grep="#3"` (mostra commits-SOAP) → ler SOAPs referenciados em `rsop/soap/` → consultar `rsop/lista_problemas.md` linha do `#3` (ou `passivos.md` se fechado).
**Skills:** `commit-soap` (formato), `rsop` (artefatos).

### US-X-003 — Recuperar do disjuntor e continuar trabalho
> Como **engenheiro**,
> quero **decidir o caminho após o disjuntor 2/2 disparar**,
> para **destravar a sessão sem o agente prosseguir sozinho**.

**Sequência:** ler exit protocol exibido → escolher uma das opções listadas (incluindo abortar a sessão) → se decisão libera novo ciclo, executar `/mdcu` (novo `_mdcu.md` reseta contador). **Importante:** decisão NÃO reseta o contador da sessão atual.
**Skills:** `mdcu`.

### US-X-004 — Fechar uma sessão pós-incidente F0
> Como **engenheiro**,
> quero **retomar o MDCU suspenso após o incidente F0 ser resolvido**,
> para **finalizar a sessão original com SOAP, agora ciente das novas vulnerabilidades**.

**Sequência:** `/mdcu-seg incidente` resolvido → SOAP-incidente registrado → MDCU retoma do `_mdcu.md` preservado → `/mdcu fechar` (cascata `/rsop soap` + `/commit-soap`).
**Skills:** `mdcu-seg` + `mdcu` + `rsop` + `commit-soap`.

---

## Lacunas 🔴

- **US-X-005 — Colaboração multi-humano:** não há story possível porque o framework não documenta autoridade entre múltiplos colaboradores em sessão MDCU compartilhada (ver `permissions.md` LAC). Quando dois engenheiros usam `_mdcu.md`, qual é a sessão? Decisão pendente.
- **US-X-006 — Versionar a versão do framework instalada:** sem campo `version` no frontmatter (gap D-001), não há story para "verificar qual versão das skills tem instalada". Workaround atual: ler `MANIFEST.md` se presente no repo, mas isso não acompanha a cópia em `~/.claude/skills/`.
