---
name: rsop
author: Iago Leal <github.com/iago-leal>
description: Registro de Software Orientado por Problemas — sistema de documentação longitudinal de software inspirado no Registro Médico Orientado por Problemas (RMOP) de Lawrence Weed. ATIVE SEMPRE que o usuário digitar /rsop, pedir para documentar estado de um sistema, registrar um incidente ou interação significativa com um projeto, criar ou atualizar lista de problemas de um software, registrar SOAP de um projeto, criar dados base de um sistema, ou mencionar "prontuário do software". Também ative quando a skill `mdcu` referenciar o RSOP como dependência. Ative proativamente quando o contexto indicar que o usuário está trabalhando em um projeto sem documentação longitudinal estruturada. NÃO ative para documentação pontual de código (docstrings, README simples) ou para registro de decisões isoladas (use ADRs diretamente).
---

# RSOP — Registro de Software Orientado por Problemas

## Fundamento

Inspirado no Registro Médico Orientado por Problemas (RMOP) de Lawrence Weed (1968), o RSOP é o prontuário do software. A premissa de Weed: *a forma como lidamos com a informação determina a forma como pensamos*. Se a documentação do software é organizada por sprint, pensamos em sprints. Se é organizada por problemas, pensamos em problemas. A estrutura do registro molda o raciocínio.

O RSOP é um sistema de resolução de problemas, não um log de atividades. Ele organiza a informação de modo a facilitar o conhecimento do sistema, a reflexão sobre seus problemas e a tomada de decisão.

### Posição no workflow

O RSOP é o terceiro elo do workflow integrado:

```
MDCU (fases 1–5)  →  Execução  →  RSOP (SOAP)  →  commit-soap (A+P)
```

O MDCU delimita o problema e produz o plano. A execução segue o plano. O RSOP registra o SOAP da sessão. O commit-soap sela com A+P. O RSOP também é consultado pelo MDCU no início de cada ciclo (Fase 1) para prover longitudinalidade.

---

## Estrutura

O RSOP tem três componentes. Todos são obrigatórios.

```
rsop/
├── dados_base.md          # Perfil do sistema
├── lista_problemas.md     # Índice vivo — componente mais importante
└── soap/                  # Notas progressivas por interação
    ├── 2026-04-15_setup-inicial.md
    ├── 2026-04-18_incidente-api.md
    └── ...
```

---

## Componente 1 — Dados base do sistema

Perfil abrangente do sistema. Equivalente ao perfil do paciente na medicina: identificação, antecedentes, contexto, recursos. Não é estático — atualiza-se ao longo do ciclo de vida. Deve ser o primeiro artefato criado em qualquer projeto e o primeiro documento consultado por qualquer pessoa nova que entre no projeto.

**Artefato: `rsop/dados_base.md`**

```markdown
# Dados base do sistema
- **Nome do projeto:** [nome]
- **Data de criação:** [data]
- **Última atualização:** [data]

## Identificação
- **Propósito:** [descrição concisa do que o sistema faz e para quem]
- **Responsáveis:** [pessoas/papéis e formas de contato]
- **Stakeholders:** [quem é afetado pelo sistema]

## Contexto e território
- **Organização:** [empresa/equipe/contexto organizacional]
- **Usuários:** [quem usa, em que contexto, com que frequência]
- **Sistemas adjacentes:** [integrações, dependências externas, APIs consumidas/expostas]
- **Restrições regulatórias ou legais:** [se aplicável]

## Antecedentes
- **Stack:** [linguagens, frameworks, infraestrutura]
- **Repositório:** [link]
- **Arquitetura atual:** [descrição ou referência a diagrama]
- **Histórico de decisões relevantes:** [referência a ADRs]
- **Tratamentos anteriores:** [migrações, refatorações, pivôs significativos]
- **Sequelas:** [dívida técnica conhecida, workarounds em produção, limitações herdadas]

## Hábitos e condições crônicas
- **Padrões de deploy:** [frequência, processo, ambientes]
- **Observabilidade:** [logs, métricas, alertas — o que existe e o que falta]
- **Padrões de incidentes:** [tipos recorrentes, frequência, severidade]
- **Dependências críticas:** [o que, se cair, derruba o sistema]

## Recursos e suporte
- **Equipe:** [composição, senioridade, disponibilidade]
- **Orçamento/infra:** [restrições conhecidas]
- **Documentação existente:** [o que existe, onde, grau de atualização]
```

---

## Componente 2 — Lista de problemas

O componente mais importante do RSOP. É o índice vivo do sistema — um resumo de todos os problemas relevantes, classificados como ativos ou passivos, mantido atualizado ao longo de todo o ciclo de vida.

A lista de problemas é o que dá longitudinalidade real ao acompanhamento do sistema. Sem ela, cada interação começa do zero.

### Regras da lista de problemas

**O que é um problema:** tudo que preocupa o engenheiro, o usuário, ou ambos. Pode ser um bug, uma limitação arquitetural, uma dívida técnica, um requisito não atendido, um risco identificado, um conflito entre stakeholders, uma restrição de infraestrutura.

**Nível de resolução:** cada problema é listado no mais alto nível de resolução possível a cada momento. Um sintoma vago ("o sistema está lento") deve evoluir para diagnóstico preciso ("N+1 queries na listagem de pedidos") quando houver informação suficiente. A mera classificação/codificação do problema sem descrição é redutora — documenta a categoria mas não o problema no sistema em particular.

**O que entra na lista:**
- Problemas crônicos ou recorrentes.
- Problemas com impacto significativo em usuários, performance ou operação.
- Decisões que condicionam decisões futuras (arquiteturais, tecnológicas).
- Dívidas técnicas que afetam a saúde do sistema.
- Problemas resolvidos mas que podem reativar ou condicionar decisões futuras.

**O que NÃO entra na lista:**
- Problemas menores, isolados e autolimitados (bug pontual corrigido no mesmo dia, ajuste cosmético). Estes ficam apenas no SOAP da interação em que surgiram.

**Classificação:**
- **Ativo** — afeta o sistema agora.
- **Passivo** — resolvido, mas com potencial de reativar ou de condicionar decisões clínicas futuras.
- A classificação é dinâmica: um problema passivo pode tornar-se ativo e vice-versa.

**Na dúvida:** inclua e revise depois. É preferível incluir e reclassificar do que perder.

**Momentos-chave para revisão da lista:**
- Início de novo ciclo de desenvolvimento.
- Pós-incidente.
- Entrada de pessoa nova no projeto.
- Reenquadramento de problema.
- Elaboração de relatórios ou referenciações (comunicação com outros times/stakeholders).
- Reavaliação periódica da saúde do sistema.

**Artefato: `rsop/lista_problemas.md`**

```markdown
# Lista de problemas
- **Projeto:** [nome]
- **Última revisão:** [data]

## Problemas ativos
| # | Problema | Desde | Nível de resolução | Severidade | Notas |
|---|----------|-------|--------------------|------------|-------|
| 1 | [descrição completa] | [data] | [sintoma/hipótese/diagnóstico] | [alta/média/baixa] | [referência a SOAP] |

## Problemas passivos
| # | Problema | Período ativo | Motivo de inativação | Pode reativar? | Notas |
|---|----------|---------------|----------------------|----------------|-------|
| 1 | [descrição completa] | [de — até] | [resolvido/integrado em outro/mitigado] | [sim/não — condição] | [referência a SOAP] |
```

---

## Componente 3 — Notas progressivas (SOAP)

Registro de evolução de cada sessão de trabalho com o sistema. Toda sessão gera um SOAP, sem exceção — assim como toda consulta médica gera um registro. O SOAP não é opcional nem reservado para interações "significativas". É o registro obrigatório de evolução. Pular é perder contexto.

O SOAP é subordinado à lista de problemas. Cada nota referencia quais problemas da lista foram abordados. Após registrado, o SOAP vai para o prontuário (RSOP). A depender do que foi abordado, o conteúdo do SOAP pode indicar necessidade de atualizar a lista de problemas, os dados base ou outras questões longitudinais — mas essa atualização é consequência, não obrigação automática.

### Disciplina de escrita

A qualidade do SOAP depende da forma como é escrito. Registro não é transcrição. Princípios:

- **Frases em ordem direta.** Sujeito-verbo-complemento. Sem inversões desnecessárias.
- **Conciso sem perder informação relevante.** Cada frase deve carregar informação que mude o entendimento ou a decisão. Se retirar a frase e nada se perder, ela não deveria estar ali.
- **Sem redundância.** Se já foi dito no S, não repetir no A. Se o O já evidencia, não re-descrever.
- **Dispensa informação secundária.** Entra o que é relevante para a avaliação e o plano. O resto é ruído.
- **Não assumir o que não foi verificado.** Se não rodou teste, não registrar "testes ok". Se não houve relato do usuário sobre algo, não inventar. Só entra o que foi efetivamente observado, relatado ou medido.
- **Distinguir fonte da informação.** No S, diferenciar o que o usuário trouxe espontaneamente do que foi perguntado. Se a informação veio de terceiro (outro time, log, dependência), explicitar.
- **Sem repetição de sujeito.** Não iniciar frases consecutivas com o mesmo sujeito. Variar com sujeito oculto ou voz impessoal para dar fluidez.

### S — Subjetivo

Formato: tópicos. O que o usuário/stakeholder relata. A experiência do problema na voz de quem o vive.

Registar: motivo do contato (expresso e real — podem divergir), contexto (iniciativa de quem, programada ou não), fonte da informação. Distinguir **demandas** (o que espera que se resolva) de **queixas** (o que reporta sem expectativa de solução) — mapear ambas, pois o quadro global contribui para o diagnóstico. Capturar o SIFE: Sentimentos (frustração, urgência, confiança), Ideias (o que o usuário acha que é a causa), Funcionalidade (como o problema afeta o uso/operação), Expectativas (o que espera como resultado). Workarounds já tentados. Estar atento a padrões de demanda aparente (cartão de visita, demanda exploratória, shopping) — nem sempre o motivo declarado é o motivo real. Registar não só o que a pessoa diz explicitamente, mas também o que fica implícito ou que surge no final da interação.

### O — Objetivo

Formato: tópicos. O que o engenheiro observa e mede. Dados factuais e objetiváveis.

Registar: logs, métricas, reprodução do comportamento, análise de código, resultados de testes, output de ferramentas de diagnóstico, resultados de instrumentos de avaliação (benchmarks, load tests, auditorias), informação de outros times ou sistemas. O exame objetivo é *dirigido* à natureza do problema — não é um checklist genérico. Só registar o que foi efetivamente examinado.

### A — Avaliação

Formato: tópicos. Raciocínio técnico sobre os problemas identificados nesta sessão.

Para cada problema abordado: hipótese de causa raiz, diagnósticos diferenciais, severidade, grau de controle, evolução desde a última sessão. Registar ao mais alto nível de resolução possível no momento. É a partir do A que se avalia necessidade de atualizar a lista de problemas — mas nem todo problema do A transita para a lista.

### P — Plano

Formato: tópicos. O que será feito, por quem, em que prazo. Acordado entre engenheiro e usuário.

Para cada problema: investigação diagnóstica (se causa não é clara), intervenção (correção, refatoração, mitigação), prevenção (para não reincidir), educacional (documentação, treinamento), recursos a mobilizar, referenciações (escalar para outro time), reavaliação (quando e como). Comunicações assíncronas relevantes. Reflexões do engenheiro e falhas a corrigir na próxima sessão.

**Artefato: `rsop/soap/[data]_[contexto].md`**

```markdown
# SOAP — [data] — [contexto/problema principal]
- **Problemas da lista abordados:** [#1, #3, ...]
- **Participantes:** [pessoas/papéis]

## S — Subjetivo
- Motivo do contato: [expresso]
- Motivo real (se diferente): [implícito — estar atento a padrões de demanda aparente]
- Contexto: [iniciativa de quem, programado ou não]
- Mapa de demandas: [o que espera que se resolva]
- Mapa de queixas: [o que reporta sem expectativa de solução]
- Relato: [o que o usuário/stakeholder trouxe — distinguir espontâneo de perguntado]
- SIFE: [sentimentos, ideias sobre a causa, impacto funcional, expectativas]
- Já tentou: [workarounds, tentativas anteriores]

## O — Objetivo
- [apenas o que foi efetivamente observado, medido ou verificado]
- Logs/métricas: [se coletados]
- Reprodução: [se tentada — resultado]
- Análise de código: [se realizada — achados]
- Informação externa: [de outros times/sistemas, se aplicável]

## A — Avaliação
- Problema #[N]: [nível de resolução atual]
  - Hipótese: [causa provável]
  - Diferenciais: [se aplicável]
  - Severidade/controle/evolução: [em relação à última sessão]
  - Atualizar lista? [sim/não]

## P — Plano
- Problema #[N]:
  - Intervenção: [o quê, quem, prazo]
  - Investigação pendente: [se houver]
  - Prevenção: [se aplicável]
  - Referenciação: [se aplicável]
  - Reavaliação: [quando]
- Reflexões: [vieses, falhas a corrigir, notas pessoais]
```

---

## Regras de operação do RSOP

1. **Toda sessão gera um SOAP.** Sem exceção. É registro de evolução obrigatório. Pular é perder contexto.
2. **A lista de problemas é o componente mais importante.** É o índice do sistema. Sem ela, os SOAPs são notas soltas sem fio condutor.
3. **O SOAP é subordinado à lista.** Cada nota referencia problemas da lista. Problemas novos identificados no A devem ser avaliados para inclusão na lista.
4. **Dados base devem estar atualizados.** Mudanças de stack, equipe, infra, contexto organizacional — tudo atualiza os dados base. Não é seção estática.
5. **Nível de resolução evolui.** Um problema começa como sintoma e deve progredir para diagnóstico conforme a investigação avança. Atualize a lista quando o nível de resolução mudar.
6. **Classificação ativo/passivo é dinâmica.** Revise periodicamente. Um problema passivo pode reativar.
7. **Na dúvida, inclua.** É mais barato reclassificar do que reconstruir contexto perdido.
8. **O RSOP não substitui o código.** Ele documenta o raciocínio sobre o sistema, não a implementação. Complementa, não duplica.

---

## Uso com `/rsop`

- `/rsop init` — Cria a estrutura de diretórios e os artefatos iniciais (dados base + lista de problemas vazia).
- `/rsop dados` — Exibe e permite atualizar os dados base do sistema.
- `/rsop lista` — Exibe a lista de problemas atual (ativos e passivos).
- `/rsop soap` — Cria uma nova nota SOAP vinculada aos problemas da lista.
- `/rsop revisar` — Inicia revisão da lista de problemas (reclassificar, atualizar nível de resolução, mover entre ativo/passivo).
- `/rsop status` — Exibe resumo: dados base (última atualização), quantidade de problemas ativos/passivos, último SOAP registrado.
