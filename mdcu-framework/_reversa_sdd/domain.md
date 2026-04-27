# Domínio — Glossário e regras de negócio

> Gerado pelo **Reversa Detective** em 2026-04-27
> Extraído por leitura cruzada de SKILL.md, MANIFEST.md, histórico Git e contexto do Scout/Archaeologist.

---

## Glossário canônico (CONFIRMADO 🟢)

### Atores
| Termo | Definição | Onde aparece |
|---|---|---|
| **Usuário** | Engenheiro/desenvolvedor que adota o framework. Coautor das decisões em F5, autoridade única após disjuntor 2/2. | mdcu/SKILL.md:36, 281, 304-339 |
| **Agente** | IA hospedeira (Claude Code / Codex / Cursor / Gemini CLI) que carrega as skills e executa as fases. | inferido + frontmatter |
| **Stakeholder** | Pessoa afetada pelo sistema, mesmo que não interaja diretamente. Mapeado em `dados_base.md` e `ARCHITECTURE.md`. | rsop/SKILL.md:51, project-init/SKILL.md:46, 196 |
| **DPO / responsável** | Owner formal do tratamento de dados (LGPD/HIPAA). | mdcu-seg/SKILL.md:189 |
| **Time** | Coletivo de engenharia com acesso a métricas internas. | mdcu-seg/SKILL.md:170 |
| **Atacante** | Modelo de ameaça implícito do STRIDE (não-ator do sistema, mas referenciado nos vetores). | mdcu-seg/SKILL.md:35-44 |

### Conceitos centrais
| Termo | Definição |
|---|---|
| **Demanda** | O que o usuário **espera resolver** (intenção declarada). Insumo principal do plano. |
| **Queixa** | O que o usuário **reporta sem expectativa de solução**. Dado diagnóstico — pode revelar a demanda real. |
| **Demanda oculta** | Demanda real sob a aparente. Frequentemente surge no final da escuta. |
| **SIFE** | Sentimentos / Ideias sobre a causa / Funcionalidade afetada / Expectativas — instrumento de F2 para revelar demanda oculta. |
| **Padrão de demanda aparente** | Taxonomia: cartão de visita / exploratória / shopping / cure-me. |
| **Reenquadramento** | Reconhecer que o problema sendo resolvido ≠ problema descrito; voltar a F2 ou F3. **Propriedade do sistema, não falha.** |
| **Disjuntor (Circuit Breaker)** | Mecanismo de loop-breaker. Após 2 reenquadramentos em F6, aborta e exige decisão humana. |
| **Gatilho de conformidade** | Verificação não-negociável (ex: `ARCHITECTURE.md` em F1) que pode interromper o fluxo. |
| **Guardrail / invariante** | Decisão arquitetural irreversível registrada em `ARCHITECTURE.md`. Violação exige `--refresh`. |
| **Lock file determinístico** | Arquivo que congela versões exatas de dependências. Sempre commitado, **nunca** em `.gitignore`. |
| **Micro-commit** | Commit técnico atômico durante F6 (`git commit` padrão). Não exige SOAP. |
| **Selo longitudinal** | Commit de fechamento de sessão MDCU gerado por `commit-soap` a partir do A+P do SOAP. |
| **Rastreio (de segurança)** | Checklist binário de 5 itens. Aplicado em F1, F3, F5, F6. Faz analogia com **rastreio populacional Wilson-Jungner**. |
| **F0 (Protocolo de incidente)** | Contenção de incidente. **Suspende** o ciclo MDCU em curso; preserva `_mdcu.md`. |
| **Postmortem blameless** | Análise pós-incidente que ataca causas estruturais, nunca pessoais. |

> **Nota — termos canônicos do framework além deste glossário:** ver `framework/glossary.md` (Satisfação do usuário em sentido clínico, Decisão informada, Composição do orquestrador, Anamnese do projeto/stakeholder, Engine downstream desacoplável, Precisa-resolver × não-precisa-resolver). Este documento é saída do **Reversa** (gitignored em `.gitignore`); o canônico distribuído vive em `framework/`.

### Inspirações declaradas (CONFIRMADO 🟢)
| Inspiração | Origem | Onde no framework |
|---|---|---|
| MCCP (Método Clínico Centrado na Pessoa) | Medicina de Família e Comunidade | MDCU (mdcu/SKILL.md:1) |
| RMOP (Lawrence Weed, 1968) | Registro Médico Orientado por Problemas | RSOP (rsop/SKILL.md:1, 8-10) |
| RCOP / e-SUS PEC | Adaptação brasileira do RMOP | RSOP (rsop/SKILL.md:9) |
| Wilson-Jungner | Critérios de rastreio populacional em saúde | rastreio de segurança (mdcu/SKILL.md:230, mdcu-seg/SKILL.md:10) |
| STRIDE (Microsoft) | Threat modeling categórico | mdcu-seg/SKILL.md:35 |
| IRP (Incident Response Plan) | Cybersecurity clássica | F0 do mdcu-seg (mdcu-seg/SKILL.md:79) |
| Conventional Commits | Convenção de mensagens | commit-soap opcional (commit-soap/SKILL.md:62) |

---

## Regras de negócio implícitas — domínio "metodologia"

> Não são "regras de validação de campo" como num CRUD. São **prescrições normativas** que o framework aplica ao **fluxo de trabalho** do usuário e do agente. A lista a seguir extrai apenas as que NÃO foram ainda capturadas pelo Archaeologist em `code-analysis.md` (anti-duplicação).

### RN-D-001 — Co-autoria, não validação 🟢
"Usuário é coautor. Se apenas aprovou, não houve decisão compartilhada." (mdcu/SKILL.md:281)
**Implicação:** o framework inverte a heurística clássica de "humano-no-loop como aprovador". O humano é coautor; o agente é um instrumento.

### RN-D-002 — Telegráfico por princípio, não por economia 🟢
"A forma como a informação é organizada determina a forma como se pensa." (rsop/SKILL.md:10)
**Implicação:** prosa longa não é cosmética — é falha epistemológica. Validar specs futuras contra disciplina de palavras (A ≤ 5, R = 1 linha).

### RN-D-003 — "Na dúvida, inclua" 🟢
Aplicado a problemas no RSOP (rsop/SKILL.md:78). Reclassificar é barato; reconstruir contexto perdido não.
**Implicação:** trade-off explícito a favor do registro abundante. Revisão posterior limpa.

### RN-D-004 — "S e O bem feitos são a fundação" 🟢
"De escuta confusa sai plano confuso. A e P são consequência — não lugar de compensar S e O ruins." (rsop/SKILL.md:134)
**Implicação:** anti-padrão a vigiar — tentar produzir A/P bons sem investir em S/O.

### RN-D-005 — Pré-condição "anamnese antes do exame físico" 🟢
"Sem contrato técnico definido (stack, estrutura, convenções, lock file), não há terreno estável para escutar demanda sobre código." (mdcu/SKILL.md:98)
**Implicação:** ordem invertida do MVP típico (escuta → arquitetura). Aqui é arquitetura → escuta.

### RN-D-006 — Reflexão é uma linha ou nada 🟢
"R é uma linha. Síntese ou omissão — nunca parágrafo. Se não há o que dizer, o R é omitido." (rsop/SKILL.md:268, 222)
**Implicação:** ciclos coerentes podem (devem) terminar sem R. Forçar R artificial é violação.

### RN-D-007 — `_mdcu.md` é substrato, conversa é volátil 🟢
"A conversa no chat é volátil; o arquivo é o substrato." (mdcu/SKILL.md:81, 283)
**Implicação:** defesa contra Lost in the Middle. O agente não pode confiar na memória de chat para anamnese — sempre relê o arquivo.

### RN-D-008 — Reset do disjuntor só com novo `/mdcu` 🟢
"Decisão do usuário após 2/2 pode liberar novo ciclo — não apaga o contador do ciclo atual." (mdcu/SKILL.md:339)
**Implicação:** o disjuntor é estado por sessão, não por interação. Burlar dá nova sessão, não nova tentativa.

### RN-D-009 — Postmortem ataca estrutura, não pessoa 🟢
"Falhas estruturais, nunca pessoais. Aprendizado vale mais que culpa." (mdcu-seg/SKILL.md:225)
**Implicação:** vetada a redação de postmortem com nome próprio. Ações de remediação devem ser sistêmicas.

### RN-D-010 — LGPD não é opcional 🟢
"LGPD não é item de compliance opcional em software brasileiro. Tratamento de dado pessoal sem base legal documentada é `#[A]`." (mdcu-seg/SKILL.md:228)
**Implicação:** vetor regulatório explícito; PII sem base legal vira problema de severidade alta automática.

### RN-D-011 — Segredo nunca em código/log/repo/issue 🟢
"Se entrou, F0 imediato." (mdcu-seg/SKILL.md:227)
**Implicação:** detecção de segredo vazado escala diretamente para protocolo de incidente, sem triagem prévia.

### RN-D-012 — Skill exclusiva para fechamento 🟢
"Se a sessão gerou SOAP, ela merece `commit-soap`. Se não gerou, não merece — é só `git commit`." (commit-soap/SKILL.md:32)
**Implicação:** divisão clara entre **marcos cognitivos** (commit-soap) e **ruído operacional** (micro-commits). Auditável via `git log --grep` e `--invert-grep`.

### RN-D-013 — Co-Authored-By globalmente proibido 🟡
"NUNCA incluir trailer `Co-Authored-By: Claude ...`" (CLAUDE.md global do usuário, ver decisions.md). Reforçado por commit `6ed9d39`: "commit-msg filtra Co-Authored-By globalmente".
**Implicação:** o framework é registrado como autoria de Iago Leal exclusivamente. Selo de autoria visível em commits dos próprios skills (ex: `commit-soap` declara `author: Iago Leal` no frontmatter).

> **Nota — regras canônicas do framework além de RN-D-001 a RN-D-013:** ver `framework/glossary.md` (RN-D-014 dever de alerta do orquestrador, RN-D-015 triagem precisa-resolver). Este documento é saída do **Reversa** (gitignored em `.gitignore`); o canônico distribuído vive em `framework/`.

---

## Lacunas 🔴 levantadas pelo Detective

### LAC-D-001 — Naming convention de `<contexto>` em SOAP
SOAPs no repo usam ambos `kebab-case` e prosa livre (ver exemplos `2026-04-15_rate-limit-login` vs `2026-04-15_credencial-aws-exposta-em-commit`). **Decisão pendente:** definir convenção canônica.

### LAC-D-002 — Idioma dos artefatos
Framework é em pt-BR; nada veta uso em outros idiomas. **Decisão pendente:** declarar pt-BR como canônico ou marcar i18n como `out of scope`.

### LAC-D-003 — Versionamento individual de skill (gap D-001 já confirmado)
SKILL.md sem campo `version` no frontmatter. **Decisão registrada (Iago):** gap a corrigir. Implementação fica para Writer/sprint futuro.

### LAC-D-004 — Hooks programáticos vs. prosa
Commit `6ed9d39` (2026-04-17) registra hooks programáticos:
- `UserPromptSubmit` injeta `_mdcu.md` a cada turno
- `commit-msg` filtra `Co-Authored-By` globalmente
- "hook anti-deriva de persona"

**MAS** as 5 SKILL.md neste repo não documentam estes hooks. Eles vivem em `~/.claude/` (config local do usuário). **Decisão pendente:** o framework deve documentar (em `ARCHITECTURE.md` futuro do próprio mdcu-framework, ou em README) o hook stack recomendado para deployment? Hoje há uma assimetria: o framework prescreve disciplina mas o enforcement real está fora do repo.
