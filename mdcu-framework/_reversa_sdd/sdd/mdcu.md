# SDD — `mdcu`

> Spec executável da skill MDCU (Método de Desenvolvimento Centrado no Usuário).
> Gerado pelo Reversa Writer em 2026-04-27. Cada afirmação é marcada com 🟢 / 🟡 / 🔴.

## Visão Geral

Orquestrador metodológico inspirado no Método Clínico Centrado na Pessoa (MCCP) da Medicina de Família e Comunidade. 🟢 Conduz uma sessão de desenvolvimento em 6 fases (F1–F6) cujos artefatos são transitórios; única persistência é o SOAP final escrito pela skill `rsop`. 🟢

## Responsabilidades

- Gerenciar o ciclo de vida de uma sessão MDCU: criar `_mdcu.md`, transicionar entre F1–F6, deletar `_mdcu.md` no fechamento. 🟢
- Aplicar o **Gatilho de Conformidade** (verificação de `ARCHITECTURE.md` antes de F2). 🟢
- Aplicar o **Disjuntor 2/2** em F6 (loop-breaker contra reenquadramento infinito). 🟢
- Aplicar o **Rastreio de Segurança 5-itens** em F1, F3, F5, F6. 🟢
- Coordenar invocação de outras skills do framework: `/project-init`, `/rsop soap`, `/commit-soap`, `/mdcu-seg`. 🟢
- Manter a disciplina de escuta/decisão compartilhada (D ≠ Q, ≥2 alternativas em F5). 🟢

## Interface

### Comandos públicos (`/`)

| Comando | Parâmetros | Saída |
|---|---|---|
| `/mdcu` | — | `_mdcu.md` criado + F1 ativada (com gatilho automático) 🟢 |
| `/mdcu fase N` | `N ∈ {1..6}` | salta para fase N (gate aplica para N≥2) 🟢 |
| `/mdcu status` | — | exibe `_mdcu.md`, fase atual, contador, presença de `ARCHITECTURE.md` 🟢 |
| `/mdcu reenquadrar` | — | protocolo de reenquadramento; **incrementa contador se em F6** 🟢 |
| `/mdcu fechar` | — | dispara `/rsop soap` → `/commit-soap` → delete de `_mdcu.md` 🟢 |

### Artefato produzido

`_mdcu.md` (transitório, raiz do projeto-cliente). Schema completo em `_reversa_sdd/data-dictionary.md` Artefato 1. 🟢

### Artefatos consumidos

- `ARCHITECTURE.md` (raiz) — gate F1 + leitura em F5/F6. 🟢
- `rsop/dados_base.md`, `rsop/lista_problemas.md`, último `rsop/soap/*.md` — em F1. 🟢

## Regras de Negócio

- **F1 → F2 exige `ARCHITECTURE.md`.** Se ausente, INTERROMPE e invoca `/project-init`. (mdcu/SKILL.md:91-113) 🟢
- **Disjuntor 2/2 em F6.** Ao 2º reenquadramento, ABORTA execução e exige decisão humana via exit protocol fixo de 5 campos. Reset apenas com novo `/mdcu`. (mdcu/SKILL.md:304-339) 🟢
- **Mexer dependência em F6** exige manifesto + lock no MESMO commit. (mdcu/SKILL.md:218,286) 🟢
- **Alternativa F5 que viola guardrail** do `ARCHITECTURE.md` exige `/project-init --refresh` antes de F6. (mdcu/SKILL.md:200,285) 🟢
- **Precedência de evidência F5:** skills > MCPs > libs mantidas > padrões > original. (mdcu/SKILL.md:186-191) 🟢
- **F2 separa Demanda × Queixa**, com SIFE quando opaco; padrões de demanda aparente: cartão de visita / exploratória / shopping / cure-me. (mdcu/SKILL.md:138-141) 🟢
- **F6 sempre relê `_mdcu.md` por inteiro** antes de executar e antes de fechar. (mdcu/SKILL.md:210,220) 🟢
- **Rastreio de segurança 5 itens binários** em F1, F3, F5, F6 — vulnerabilidade detectada vira `#` no RSOP. (mdcu/SKILL.md:228-251) 🟢
- **Usuário é coautor**, não validador. Apenas-aprovação não conta como decisão compartilhada. (mdcu/SKILL.md:281) 🟢
- **`_mdcu.md` é deletado pós-SOAP+commit**, nunca antes. (mdcu/SKILL.md:222) 🟢
- **Gate de Integração (NOVA — F6 pré-fechamento):** antes de `/mdcu fechar`, o agente DEVE rodar o comando `test` definido em `ARCHITECTURE.md.Comandos principais` (e `build` quando aplicável). **Falha de teste impede fechamento.** O agente deve apresentar o erro e ou (a) corrigir, ou (b) reenquadrar via `/mdcu reenquadrar`, ou (c) acionar disjuntor humano. Nunca pula. 🟢 (Iago, 2026-04-27 — questions.md P9; substitui o gate `teste-integrado` removido em ADR-005 — ver D-ADR-005)
- **Hooks programáticos (UserPromptSubmit, anti-deriva, commit-msg) viram skill versionada `mdcu-hooks` (NOVA, roadmap)** com JSON de spec lido pelo orquestrador e aplicado via `/mdcu-hooks install`. Resolve a assimetria histórica de "hooks só na máquina do Iago". 🟢 (Iago, 2026-04-27 — questions.md P8; D-004 resolvida)

## Fluxo Principal

1. Usuário digita `/mdcu`. Skill cria `_mdcu.md` com template (header + `Tentativas de Reenquadramento: 0/2` + 6 seções vazias). Ativa F1. 🟢
2. **F1 — Gatilho:** verifica `ARCHITECTURE.md` na raiz. Se ausente → invoca `/project-init` → retorna a F1 do início. Se presente, lê stack/guardrails. 🟢
3. **F1 — Demais ações:** lê `rsop/dados_base.md`, `rsop/lista_problemas.md`, último SOAP; identifica vieses; verifica reenquadramento pendente; aplica rastreio de segurança. Anota em `_mdcu.md`. 🟢
4. **F2 — Escuta** (2 minutos de ouro): pergunta aberta única; separa D × Q; usa SIFE se opaco. ESCREVE `S:` em `_mdcu.md` (sub-slots: Demandas/Queixas/Notas). 🟢
5. **F3 — Exploração:** "por que isso é problema?", patobiografia, sistema ao redor; rastreio de segurança. ESCREVE `O:` em `_mdcu.md`. 🟢
6. **F4 — Avaliação:** hipótese ("o provável problema é X devido a Y") + pró/contra + reversibilidade. Atualiza `lista_problemas.md` (novo `#` ou evolui descrição). Anota em `_mdcu.md`. 🟢
7. **F5 — Plano:** ≥2 alternativas com trade-offs (precedência de evidência); rastreio de segurança em cada; verificação de guardrails. Decisão compartilhada. ESCREVE em `_mdcu.md`. 🟢
8. **F6 — Execução:** RELÊ `_mdcu.md` inteiro; executa plano (skills > MCPs > tools); micro-commits permitidos; manifesto+lock no mesmo commit. 🟢
9. **F6 — Fechamento:** RELÊ `_mdcu.md`; invoca `/rsop soap` → `/commit-soap`; DELETA `_mdcu.md`. 🟢

## Fluxos Alternativos

- **Reenquadramento em F6 (1ª vez):** retorna a F2 ou F3, **incrementa contador para 1/2**. Continua. 🟢
- **Reenquadramento em F6 (2ª vez):** **DISJUNTOR DISPARA**. ABORTA execução. Emite exit protocol com 5 campos (tentativas, falhas, próximo enquadramento, gap, opções). Aguarda decisão humana. Não prossegue sozinho. 🟢
- **Suspensão por F0 (incidente):** `mdcu-seg incidente` SUSPENDE o ciclo; `_mdcu.md` PRESERVADO intacto. Retoma após incidente resolvido. 🟢
- **Salto de fase:** `/mdcu fase N` permite avançar/voltar; gate de conformidade ainda aplica para N≥2. 🟢
- **Status:** `/mdcu status` é não-destrutivo; mostra estado atual sem alterar. 🟢

## Dependências

- **`project-init`** — bloqueante. Gate F1→F2 exige `ARCHITECTURE.md`; se ausente, MDCU invoca `/project-init` e suspende. 🟢
- **`rsop`** — lifecycle. Consultada em F1 (lê dados base + lista de problemas + último SOAP); atualizada em F4 (lista_problemas); usada no fechamento via `/rsop soap`. 🟢
- **`commit-soap`** — lifecycle. Invocada no fechamento via `/commit-soap` para gerar selo longitudinal. 🟢
- **`mdcu-seg`** — condicional. Invocada quando rastreio dispara (PII/auth em F3, alternativa que falha em F5, sinal de incidente em F6, `#[A]` ativo em F1). 🟢

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência | Confiança |
|---|---|---|---|
| Confiabilidade | Defesa contra Lost in the Middle via injeção de `_mdcu.md` por hook (`UserPromptSubmit`) e releitura obrigatória em F6 | mdcu/SKILL.md:81,210,283; ADR-006 | 🟡 (hook fora do repo) |
| Auditabilidade | Decisões registradas em `_mdcu.md` durante o ciclo, destiladas em SOAP permanente | mdcu/SKILL.md:50-77 | 🟢 |
| Robustez (anti-loop) | Disjuntor 2/2 em F6 com exit protocol obrigatório | mdcu/SKILL.md:304-339 | 🟢 |
| Reprodutibilidade | Manifesto+lock no mesmo commit em F6 (delegado a project-init regra DDD) | mdcu/SKILL.md:218 | 🟢 |
| Segurança | Rastreio em 4 fases + delegação a `mdcu-seg` quando dispara | mdcu/SKILL.md:228-262 | 🟢 |
| Portabilidade | Markdown + frontmatter Agent Skills — funciona em Claude/Codex/Cursor/Gemini | frontmatter; AGENTS.md | 🟢 |
| Performance | Não aplicável (não há latência de runtime — é prosa interpretada) | — | — |

> Inferido. Validar com adoção em projeto real.

## Critérios de Aceitação

```gherkin
Dado que o projeto NÃO tem ARCHITECTURE.md na raiz
Quando o usuário digita /mdcu
Então MDCU cria _mdcu.md, ativa F1, detecta ausência de ARCHITECTURE.md
  e INTERROMPE invocando /project-init antes de avançar para F2

Dado que o projeto TEM ARCHITECTURE.md
  E rsop/lista_problemas.md tem #[A] de segurança ativo
Quando o usuário digita /mdcu
Então MDCU em F1 invoca /mdcu-seg auditoria para contextualizar
  antes de avançar para F2

Dado que o ciclo está em F6 com contador 1/2
Quando uma nova evidência exige reenquadrar
Então MDCU incrementa contador para 2/2, ABORTA execução,
  emite exit protocol de 5 campos e aguarda decisão humana

Dado que o ciclo está em F6 e a execução foi concluída
Quando o usuário digita /mdcu fechar
Então MDCU relê _mdcu.md, invoca /rsop soap, depois /commit-soap,
  e finalmente DELETA _mdcu.md

Dado que F2 está em curso
Quando o usuário relata "está lento" sem explicar expectativa
Então MDCU registra como Queixa em S: (não Demanda),
  e usa SIFE para revelar demanda oculta antes de F4

Dado que F6 está pronta para fechar e ARCHITECTURE.md define `test` como comando principal
Quando o usuário (ou agente) propõe /mdcu fechar
Então MDCU executa `test` ANTES de invocar /rsop soap
  E se o teste FALHA, MDCU bloqueia o fechamento e informa o erro
  E o agente deve (a) corrigir, (b) /mdcu reenquadrar, ou (c) acionar disjuntor humano
  E /mdcu fechar só prossegue após `test` retornar verde

Dado que ARCHITECTURE.md define `build` além de `test`
Quando F6 vai fechar
Então MDCU executa `test` E `build` antes de /rsop soap
  E falha em qualquer um bloqueia o fechamento
```

## Prioridade

| Requisito | MoSCoW | Justificativa |
|---|---|---|
| Gate de conformidade `ARCHITECTURE.md` em F1 | Must | Sem contrato técnico não há terreno estável (mdcu/SKILL.md:98) |
| Disjuntor 2/2 em F6 | Must | Anti-loop crítico — protege ciclo contra IA tautológica |
| Disciplina F2 (D × Q + SIFE) | Must | "S e O bem feitos são a fundação" — sem isso, A/P são compensação |
| F6 relê `_mdcu.md` | Must | Defesa contra Lost in the Middle |
| Rastreio de segurança 5-itens | Must | Vulnerabilidade detectada cedo é rasreio populacional Wilson-Jungner |
| ≥2 alternativas em F5 | Must | Decisão compartilhada exige opção real |
| Salto de fase `/mdcu fase N` | Should | Útil em retomadas, não no fluxo padrão |
| Status `/mdcu status` | Could | Conveniência |
| Gate de Integração (F6 pré-fechamento) | **Must** | Substitui `teste-integrado` removido em ADR-005; cenário de risco (deploy com testes vermelhos) é real |
| Skill `mdcu-hooks` versionada (NOVA, roadmap) | Must | Resolve assimetria de enforcement (D-004); JSON de spec + comando `/mdcu-hooks install` |
| Co-autoria multi-humano | Should | `_mdcu.md` é **compartilhado** entre engenheiros humanos no mesmo ciclo. Coautoria registrada no SOAP (S: pode ter notas atribuídas; commits-SOAP podem ter múltiplos autores humanos). **LLMs NÃO entram como coautores** (consistência com regra global anti-`Co-Authored-By`). (Iago, 2026-04-27 — questions.md P7) 🟢 |

## Rastreabilidade de Código

| Arquivo | Componente lógico | Cobertura |
|---|---|---|
| `mdcu/SKILL.md:1-3` | frontmatter (description) | 🟢 |
| `mdcu/SKILL.md:6-30` | Workflow integrado | 🟢 |
| `mdcu/SKILL.md:34-46` | Persona + Princípio central | 🟢 |
| `mdcu/SKILL.md:50-83` | Sessão ativa `_mdcu.md` (template) | 🟢 |
| `mdcu/SKILL.md:86-225` | Fases F1–F6 | 🟢 |
| `mdcu/SKILL.md:228-262` | Rastreio de segurança | 🟢 |
| `mdcu/SKILL.md:266-269` | Reflexão | 🟢 |
| `mdcu/SKILL.md:272-287` | 13 regras de operação | 🟢 |
| `mdcu/SKILL.md:290-339` | Reenquadramento + Disjuntor | 🟢 |
| `mdcu/SKILL.md:345-351` | Comandos `/mdcu` | 🟢 |

---

## Refresh 2026-04-27 — delta v3.0.0 implícita

> Acionado pelos commits `ba76256` (tese formalizada) → `599307d` (F6 reformulada) → `1378d5e` (split + commit-soap desacoplado). Detalhes completos em `_reversa_sdd/code-analysis.md` apêndice de refresh.

### Mudanças estruturais 🟢

- **Nova seção "Escopo do MDCU"** no topo da SKILL.md — declara o que MDCU FAZ (extração via MCCP + tradução de complexidade) e NÃO FAZ (execução, código, spec, análise arquitetural — DELEGADOS a engines downstream desacopláveis P-8)
- **Persona reescrita** com 3 camadas (arquiteto SE sênior + comunicador MCCP + tradutor-artista) — F-2 em `framework/principles.md`
- **Workflow integrado** redesenhado: `project-init → project-setup → MDCU → engine downstream OU monolítico → RSOP SOAP → commit-soap`
- **Gatilho de conformidade DUAL** — F1 verifica `ARCHITECTURE.md` E setup materializado (era só `ARCHITECTURE.md`)
- **F6 reformulada em 3 sub-blocos** — F6.a delegação (engine ou monolítico declarado) + F6.b acompanhamento (Disjuntor 2/2 preservado) + F6.c tradução de retorno + fechamento

### Novas dependências 🟢

- **`project-setup`** (NOVA, v0.1.0) — invocada pelo gatilho dual de F1 quando setup não materializado; recebe `ARCHITECTURE.md` como input
- **Engines downstream desacopláveis** (P-8) — referenciados em F6.a; não são skill, são padrão de delegação (spec-kit, superpowers, bmad, libs, Reversa)
- **`commit-soap` desacoplado** (v2.0.0) — F6.c usa modo default (lê SOAP); paradigma "selo longitudinal universal"

### Critério de Aceitação NOVO (Gherkin)

```gherkin
Cenário: Modo monolítico declarado em F6.a
  Dado que F5 produziu plano de execução
  E que NENHUM engine downstream concreto está plugado ao projeto
  Quando F6.a ativa
  Então o orquestrador-instância opera como engine ad-hoc
  E o modo monolítico é declarado explicitamente em _mdcu.md (não silencioso)
  E os critérios de saída (engine maduro disponível, projeto cresceu, manutenção vira gargalo) ficam visíveis ao adopter
```

```gherkin
Cenário: Disjuntor 2/2 preservado em F6.b
  Dado que F6.a delegou execução (modo desacoplado ou monolítico)
  E que F6.b está acompanhando
  E que o orquestrador identificou necessidade de reenquadrar
  Quando o contador atinge 2/2
  Então a execução automática É abortada
  E o exit protocol é acionado
  E o usuário decide o caminho a seguir
```

### Priorização MoSCoW — atualização

- **Promovido para Must:** modo monolítico declarado com critério de saída em F6.a (era implícito)
- **Promovido para Must:** F6 em 3 sub-blocos com Disjuntor preservado em F6.b
- **Should:** referência ao `framework/principles.md` no topo da skill (canônico citável)

### Lacunas remanescentes

- `mdcu/SKILL.md` ainda não tem `version: "3.0.0"` no frontmatter (regra D-001 do release-train original); **aguarda sessão futura** para bump explícito
- F-1 a F-5 são citadas no corpo mas não estão repetidas — adopters precisam ler `framework/principles.md` separadamente
