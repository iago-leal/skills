# Diagrama arquitetural canônico — mdcu-framework

> Fonte canônica da arquitetura visual do framework.
> Diagrama compartilhado pelo stakeholder em 2026-04-27 (versão 2, com seta corrigida).
> Em caso de tensão entre este documento e qualquer outro artefato visual ou prosa, **este prevalece**.
> Note: `framework-diagrama.html` no root do repositório é documentação **editorial** (visualização pública), não fonte canônica — divergências entre os dois resolvem-se a favor deste arquivo.

---

## Visão geral

O framework opera em **4 camadas**, organizadas em torno do ciclo iterativo de desenvolvimento de software (Requisitos → Análise → Especificações → Código → Teste → Manutenção). MDCU é a **interface humana bidirecional** entre o usuário e a pipeline técnica; engines downstream desacopláveis fazem a execução técnica; `rsop` + `commit-soap` formam camada longitudinal transversal que abraça todas as fases.

```
                                  ┌─────────────────────────────────┐
                                  │   Acompanhamento longitudinal   │
                                  │   • rsop                        │
                                  │   • commit-soap                 │
                                  └──────────────┬──────────────────┘
                                                 │ (transversal — abraça todas)
                ┌────────────────────────────────┼────────────────────────────────┐
                │                                ↓                                │
                │                                                                 │
   Requisitos ──→ Análise ──→ Especificações ──→ ┌── Código ──→ Teste ──┐ ──→ Manutenção
       │                                          │     [zona IA]        │
       │                                          └──────────────────────┘
       │                            ↑                       │
       │                            │                       │
       │                            │              ┌────────┴──────────┐
       │                            │              │  Engines externos │
       │                            └──────────────┤  • spec-kit       │
       │                                           │  • superpowers    │
       │                                           │  • bmad           │
       │                                           │  • ...            │
       │                                           │  (DESACOPLÁVEIS   │
       │                                           │   do framework)   │
       │                                           └─────────┬─────────┘
       │                                                     │
       ↓ (técnica MCCP                                       │ (devolvem complexidade
       │  alimenta                                           │  técnica via vocabulário
       │  Requisitos)                                        │  MCCP)
       │                                                     │
       ↓                                                     ↓
   ┌────────┐  ←── (MCCP é técnica-fonte;                 ┌────────┐
   │  MCCP  │      MDCU operacionaliza MCCP em SE)        │  MCCP  │
   └───┬────┘                                             └────┬───┘
       │                                                       │
       │ (MCCP alimenta MDCU)                                  │
       ↓                                                       ↓
   ┌──────────────────────────────────────────────────────────────┐
   │                          MDCU                                │
   │   (interface humana bidirecional Usuário ↔ pipeline técnica) │
   └──────────────────────────────┬───────────────────────────────┘
                                  │ (bidirecional)
                                  ↓
                              ┌────────┐
                              │Usuário │
                              └────────┘
```

---

## Anatomia em 4 camadas

| Camada | Componentes | Papel | Skills/artefatos |
|---|---|---|---|
| **1. Interface humana** | MDCU (operacionalização do MCCP em SE) | Canal bidirecional Usuário ↔ pipeline técnica. Faz **extração de requisitos** (ida) e **tradução de complexidade técnica** (volta). | `mdcu/SKILL.md` |
| **2. Delegação técnica** | Engines downstream desacopláveis: spec-kit, superpowers, bmad, libs maduras, Reversa (quando "stakeholder" é sistema legado) | Análise, Especificação, Código (zona "IA"), Teste, Manutenção | Externos ao framework — invocados por convenção, não embutidos |
| **3. Acompanhamento longitudinal** | `rsop` (prontuário) + `commit-soap` (selo) | Transversal a TODAS as fases. Registro permanente do projeto. | `rsop/SKILL.md`, `commit-soap/SKILL.md` |
| **4. Fundação** | `project-init` (contrato técnico) + `mdcu-seg` (vigilância de segurança) | Estabelece terreno (1× ou em refresh) e vigia continuamente | `project-init/SKILL.md`, `mdcu-seg/SKILL.md` |

---

## Direcionalidade das setas (canônica)

| Origem → destino | Significado |
|---|---|
| `MCCP → MDCU` | MCCP é técnica-fonte; MDCU operacionaliza MCCP em SE (ver F-1 em `principles.md`) |
| `Usuário ↔ MDCU` | Bidirecional. Ida: usuário traz queixa/demanda; MDCU extrai. Volta: MDCU traduz complexidade técnica para opção decidível pelo usuário. |
| `MDCU → MCCP → Requisitos` | MDCU usa técnica MCCP para alimentar a fase Requisitos da pipeline |
| `Engines externos → MCCP` | Complexidade técnica gerada pelos engines é traduzida via vocabulário MCCP antes de chegar ao MDCU para devolução ao usuário |
| `Especificações → Engines externos` | Engines recebem requisitos e produzem Análise/Spec/Código/Teste |
| `Acompanhamento longitudinal ⇕ todas as fases` | Bidirecional implícito — rsop registra e é consultado em qualquer fase |

---

## O que o diagrama torna explícito

1. **MDCU NÃO faz Análise, Especificação, Código, Teste ou Manutenção.** Esses ficam todos na pipeline técnica, executados por engines externos. (Ver P-8 em `principles.md`.)
2. **MDCU é canal bidirecional.** Não é só "front-end de extração" — também é "back-end de tradução" da complexidade técnica de volta para o usuário, fundamental para a decisão informada (F-3 em `principles.md`).
3. **Engines externos são desacopláveis.** O framework prescreve disciplina mas não obriga engine específico. spec-kit, superpowers, bmad são exemplos atuais; outros podem ser adotados sem quebrar o framework.
4. **MCCP é entidade arquitetural separada do MDCU.** MCCP é a técnica-fonte, MDCU é a aplicação SE. (Ver F-1 em `principles.md`.)
5. **`rsop` + `commit-soap` são transversais.** Não são "fechamento de sessão MDCU" como hoje codificado — abraçam todas as fases. (Implementação efetiva fica em `rsop/lista_problemas.md` `#11`.)

---

## Implicações para skills atuais

Estas implicações estão registradas como problemas ativos na `lista_problemas.md` do framework, com refatoração efetiva deferida:

| Implicação | `#` | Ação |
|---|---|---|
| MDCU F6 atual contém execução técnica direta (micro-commits, lock file, "incrementos pequenos") — viola P-8 | `#8 [A]` | Reformular F6 como "tradução de retorno" ou removê-la |
| `project-init` executa npm/poetry/git diretamente — pode ser orquestrador de setup-engine externo | `#9 [M]` | Tornar tradutor de invocação ao engine apropriado |
| `commit-soap` está acoplado à sessão MDCU — P-9 prevê selo de qualquer marco longitudinal | `#11 [M]` | Desacoplar de sessão MDCU |

---

## Versão e histórico

| Versão | Data | Mudança |
|---|---|---|
| v1 | 2026-04-27 | Compartilhamento inicial pelo stakeholder em sessão MDCU sobre o próprio framework. Anatomia em 4 camadas explicitada. |
| v2 | 2026-04-27 | Seta corrigida: `MCCP → MDCU` (antes apontava `MDCU → MCCP`). Refina F-1 — MCCP é fonte, MDCU é operacionalização. |

**Diagrama-fonte original:** capturado em sessão de planejamento 2026-04-27, preservado em `_mdcu.md` da sessão (efêmero — destilado em SOAP da mesma data).
