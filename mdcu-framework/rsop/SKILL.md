---
name: rsop
author: Iago Leal <github.com/iago-leal>
description: Registro de Software Orientado por Problemas — sistema de documentação longitudinal de software inspirado no Registro Médico Orientado por Problemas (RMOP) de Lawrence Weed. ATIVE SEMPRE que o usuário digitar /rsop, pedir para documentar estado de um sistema, registrar um incidente ou interação significativa com um projeto, criar ou atualizar lista de problemas de um software, registrar SOAP de um projeto, criar dados base de um sistema, ou mencionar "prontuário do software". Também ative quando a skill `mdcu` referenciar o RSOP como dependência. Ative proativamente quando o contexto indicar que o usuário está trabalhando em um projeto sem documentação longitudinal estruturada. NÃO ative para documentação pontual de código (docstrings, README simples) ou para registro de decisões isoladas (use ADRs diretamente).
---

# RSOP — Registro de Software Orientado por Problemas

## Fundamento

Inspirado no Registro Médico Orientado por Problemas (RMOP) de Lawrence Weed (1968), o RSOP é o prontuário do software. A premissa de Weed: *a forma como lidamos com a informação determina a forma como pensamos*. Se a documentação do software é organizada por sprint, pensamos em sprints. Se é organizada por problemas, pensamos em problemas. A estrutura do registro molda o raciocínio.

O RSOP é um sistema de resolução de problemas, não um log de atividades. Ele organiza a informação de modo a facilitar o conhecimento do sistema, a reflexão sobre seus problemas e a tomada de decisão.

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

Registro de cada interação significativa com o sistema. O SOAP não é autônomo — é subordinado à lista de problemas. Cada nota referencia quais problemas da lista foram abordados.

### S — Subjetivo

O que o usuário/stakeholder relata. A experiência do problema na voz de quem o vive.

Inclui: motivo do contato (expresso e real), contexto (iniciativa de quem, programada ou não), fonte da informação, workarounds já tentados, frustrações, expectativas, perspectiva da pessoa sobre o problema e avaliação que faz dos recursos de que dispõe. Registar não só o que a pessoa diz explicitamente, mas também o que fica implícito ou que surge apenas no final da interação.

### O — Objetivo

O que o engenheiro observa e mede. Dados factuais e objetiváveis.

Inclui: logs, métricas, reprodução do comportamento, análise de código, resultados de testes, output de ferramentas de diagnóstico, resultados de aplicação de instrumentos de avaliação (benchmarks, load tests, auditorias), informação de outros times ou sistemas (notas de incidentes de dependências, relatórios de outros prestadores). O conceito de exame objetivo é *dirigido* à natureza do problema — não é um checklist genérico.

### A — Avaliação

Raciocínio técnico sobre os problemas identificados nesta interação.

Para cada problema abordado: hipótese de causa raiz, diagnósticos diferenciais (pode ser X, mas também pode ser Y), severidade, grau de controlo, evolução desde a última interação. Registar ao mais alto nível de resolução possível no momento. É a partir do A que se atualiza a lista de problemas — mas nem todo problema do A transita para a lista (problemas menores e autolimitados ficam apenas aqui).

### P — Plano

O que será feito, por quem, em que prazo. Acordado entre engenheiro e usuário.

Para cada problema: plano de investigação diagnóstica (se a causa ainda não é clara), plano de intervenção (correção, refatoração, mitigação — farmacológico ou não), plano preventivo (o que fazer para que não reincida), plano educacional (documentação, treinamento), recursos a mobilizar (pessoas, infra, orçamento), referenciações (escalar para outro time, consultar especialista), próxima reavaliação. Inclui também reflexões do engenheiro sobre a interação e falhas a corrigir na próxima.

Comunicações não presenciais (mensagens, e-mails, feedback assíncrono) entre engenheiro e usuário sobre o sistema devem também ser registadas no P quando relevantes.

**Artefato: `rsop/soap/[data]_[contexto].md`**

```markdown
# SOAP — [data] — [contexto/problema principal]
- **Problemas da lista abordados:** [#1, #3, ...]
- **Quem participou:** [pessoas/papéis]

## S — Subjetivo
- **Motivo do contato:** [expresso]
- **Motivo real (se diferente):** [implícito]
- **Contexto:** [iniciativa de quem, programado ou não]
- **Relato:** [o que o usuário/stakeholder trouxe]
- **Expectativas:** [o que espera como resultado]
- **Já tentou:** [workarounds, tentativas anteriores]
- **Perspectiva sobre o problema:** [como a pessoa vê a situação]
- **Recursos identificados pela pessoa:** [o que ela acha que pode contribuir]

## O — Objetivo
- **Observações factuais:** [logs, métricas, reprodução, análise de código]
- **Resultados de diagnóstico:** [testes, ferramentas, instrumentação]
- **Informação de outros times/sistemas:** [se aplicável]
- **Instrumentos aplicados:** [benchmarks, auditorias, load tests — se aplicável]

## A — Avaliação
Para cada problema abordado:
- **Problema #[N]:** [descrição no nível de resolução atual]
  - Hipótese: [causa provável]
  - Diferenciais: [outras causas possíveis]
  - Severidade: [alta/média/baixa]
  - Controle: [controlado/parcialmente/não controlado]
  - Evolução: [melhorou/estável/piorou desde última interação]
  - Atualizar lista de problemas? [sim/não — o quê]

## P — Plano
Para cada problema abordado:
- **Problema #[N]:**
  - Investigação: [o que ainda precisa ser investigado]
  - Intervenção: [o que será feito — correção, refatoração, mitigação]
  - Prevenção: [o que fazer para que não reincida]
  - Educacional: [documentação, treinamento necessário]
  - Recursos: [o que precisa ser mobilizado]
  - Referenciação: [escalar? para quem?]
  - Reavaliação: [quando e como]
- **Reflexões do engenheiro:** [notas pessoais, vieses percebidos, falhas a corrigir]
- **Comunicações registradas:** [feedback assíncrono relevante, se houver]
```

---

## Regras de operação do RSOP

1. **A lista de problemas é o componente mais importante.** É o índice do sistema. Sem ela, o SOAP são notas soltas sem fio condutor.
2. **O SOAP é subordinado à lista.** Cada nota referencia problemas da lista. Problemas novos identificados no A devem ser avaliados para inclusão na lista.
3. **Dados base devem estar atualizados.** Mudanças de stack, equipe, infra, contexto organizacional — tudo atualiza os dados base. Não é seção estática.
4. **Nível de resolução evolui.** Um problema começa como sintoma e deve progredir para diagnóstico conforme a investigação avança. Atualize a lista quando o nível de resolução mudar.
5. **Classificação ativo/passivo é dinâmica.** Revise periodicamente. Um problema passivo pode reativar.
6. **Na dúvida, inclua.** É mais barato reclassificar do que reconstruir contexto perdido.
7. **O RSOP não substitui o código.** Ele documenta o raciocínio sobre o sistema, não a implementação. Complementa, não duplica.

---

## Uso com `/rsop`

- `/rsop init` — Cria a estrutura de diretórios e os artefatos iniciais (dados base + lista de problemas vazia).
- `/rsop dados` — Exibe e permite atualizar os dados base do sistema.
- `/rsop lista` — Exibe a lista de problemas atual (ativos e passivos).
- `/rsop soap` — Cria uma nova nota SOAP vinculada aos problemas da lista.
- `/rsop revisar` — Inicia revisão da lista de problemas (reclassificar, atualizar nível de resolução, mover entre ativo/passivo).
- `/rsop status` — Exibe resumo: dados base (última atualização), quantidade de problemas ativos/passivos, último SOAP registrado.
