# Protocolo de ADR (Architectural Decision Record)

> Carregue ao trabalhar com decisões arquiteturais. Define formato e ciclo de vida.

## 1. Quando criar ADR

Crie ADR sempre que houver:

- **Escolha de tecnologia** com alternativas viáveis (ex: Postgres vs. SQLite, Redis vs. RabbitMQ)
- **Padrão arquitetural** que afeta múltiplos módulos (ex: event sourcing, CQRS)
- **Trade-off não-trivial** (performance vs. simplicidade, custo vs. latência)
- **Convenção que vai durar** (formato de IDs, esquema de retry, política de logs)
- **Dívida consciente** (escolha sub-ótima assumida com prazo de revisita)

NÃO crie ADR para:
- Mudança trivial reversível em < 1 dia
- Decisão local de função (use comentário no código)
- Bug fix óbvio
- Refactor mecânico

## 2. Localização e numeração

Diretório: `<projeto>/docs/adr/`

Arquivo: `NNNN-slug-titulo-curto.md` (4 dígitos zero-padded, slug em kebab-case lowercase sem acentos, max 50 chars).

Numeração sequencial — `0001`, `0002`, ... `9999`. Nunca reutilizar número.

## 3. Estrutura literal de ADR

```markdown
---
adr: NNNN
title: Título humano
status: proposed | accepted | deprecated | superseded
date: YYYY-MM-DD
supersedes: NNNN | null
superseded_by: NNNN | null
debt_conscious: true | false
---

# ADR-NNNN: {TÍTULO}

## Status
{proposed | accepted | deprecated | superseded}

{IF superseded:} Substituído por ADR-{N}.
{IF supersedes:} Substitui ADR-{N}.

## Contexto
{Descrição do problema, restrições, forças em jogo. 2-5 parágrafos.
Inclua dados concretos: métricas, custos, prazos. Sem prosa motivacional.}

## Decisão
{1-2 parágrafos. Verbo no presente. "Adotamos X.", não "vamos adotar X."}

## Consequências
### Positivas
- {ganho concreto 1}
- {ganho concreto 2}

### Negativas
- {custo concreto 1}
- {custo concreto 2}

### Neutras / a observar
- {item que vira métrica de saúde}

## Alternativas Consideradas
### Alternativa A: {nome}
{Por que foi descartada}

### Alternativa B: {nome}
{Por que foi descartada}

{IF debt_conscious=true:}
## Dívida Consciente Assumida
- **Assumida em**: YYYY-MM-DD
- **Justificativa**: {por que aceitamos a sub-otimalidade agora}
- **Prazo de revisita**: {YYYY-MM-DD ou condição binária — ex: "quando passar de 100 req/s sustentado por 1 semana"}
- **Issue tech-debt linkada**: #{NNN}
{END IF}

## Referências
- Issue/Milestone que originou: #{NNN}
- {links para benchmark, RFC externa, paper, etc.}
```

## 4. Estados (lifecycle)

```
            [ proposed ] ──────────► [ accepted ]
                  │                       │
                  │                       │
                  ▼                       ▼
            [ rejected ]            [ deprecated ]
                                          │
                                          ▼
                                   [ superseded ]
                                   (link para ADR novo)
```

- `proposed`: em discussão. PR aberto. Não bloqueia código ainda.
- `accepted`: decisão final. CI/code review pode bloquear merge que viole.
- `deprecated`: ainda válida historicamente, mas não usar em novo código.
- `superseded`: substituída por ADR-N. Manter arquivo (histórico), apontar para sucessora.

Transições:
- `proposed → accepted`: merge do PR que adiciona o ADR
- `accepted → deprecated`: novo ADR explicitamente deprecia (atualiza este)
- `accepted → superseded`: novo ADR `--supersedes N` (script atualiza este)

## 5. ADR Lint (CI guardrail)

Recomendar adicionar Action que falha PR se:

- ADR `proposed` sem checklist de revisão completo
- Mudança em `src/auth/**` sem ADR `accepted` referente a auth no PR ou citado
- Mudança em `src/billing/**` idem
- ADR criado sem campo `date`

Esse lint converte ADR de teatro em controle. Sem ele, ADR vira wiki morta.

## 6. ADR retroativo? Não.

Tentação comum: descobrir que código X foi escolhido sem ADR; criar ADR retroativo "para registrar". Não faça.

ADR retroativo é dishonest — finge que houve deliberação quando não houve. Em vez disso:
- Abrir ADR `proposed` re-discutindo a escolha **agora** (com contexto atual, não fictício)
- Marcar dívida consciente se decidir manter (`--debt-conscious`)

## 7. Dívida consciente — modelo mental

ADR `--debt-conscious` é a única forma honesta de dizer "sabemos que não é o ideal, escolhemos assim mesmo, e aqui está o gatilho de revisita". Sem isso:

- Junior dev descobre código sub-ótimo daqui a 6 meses
- Junior dev pensa "alguém errou"
- Junior dev refaz "do jeito certo" sem entender a restrição original
- Bug aparece porque a restrição original era real
- Time perde 1 semana entendendo

ADR `--debt-conscious` previne tudo isso com 1 arquivo.
