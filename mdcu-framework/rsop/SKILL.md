---
name: rsop
description: Registro de Software Orientado por Problemas — prontuário longitudinal do software, inspirado no RMOP de Lawrence Weed (1968) e no modelo RCOP do e-SUS PEC. Formato enxuto, telegráfico, orientado por problema. ATIVE SEMPRE que o usuário digitar /rsop, pedir para documentar estado de um sistema, registrar um incidente ou interação significativa com um projeto, criar ou atualizar lista de problemas de um software, registrar SOAP de um projeto, criar dados base de um sistema, ou mencionar "prontuário do software". Também ative quando a skill `mdcu` referenciar o RSOP como dependência. Ative proativamente quando o contexto indicar que o usuário está trabalhando em um projeto sem documentação longitudinal estruturada. NÃO ative para documentação pontual de código (docstrings, README simples) ou para registro de decisões isoladas (use ADRs diretamente).
---

# RSOP — Registro de Software Orientado por Problemas

## Fundamento

Prontuário do software. Inspirado no RMOP de Weed (1968) e no modelo RCOP adotado pelo e-SUS PEC: registro sintético, estruturado, **orientado por problema**. A forma como a informação é organizada determina a forma como se pensa — por isso o formato é telegráfico por princípio, não por economia. Prosa longa é ruído.

## Posição no workflow

```
MDCU (fases 1–7 transitórias)  →  Execução  →  RSOP (SOAP persiste)  →  commit-soap (A+P)
```

Os artefatos de fase do MDCU são transitórios. O SOAP é o destilado — **único registro permanente** da sessão. A lista de problemas é o índice longitudinal.

---

## Estrutura

```
rsop/
├── dados_base.md
├── lista_problemas.md
├── seguranca.md          # opcional — gerido pela skill `mdcu-seg`
└── soap/
    └── YYYY-MM-DD_contexto.md
```

---

## Componente 1 — Dados base

Perfil mínimo do sistema. Atualiza conforme mudança estrutural. Não é diário.

**Artefato: `rsop/dados_base.md`**

```markdown
# Dados base
- **Projeto:** [nome]
- **Atualizado:** [data]

## Identificação
- Propósito: [1 frase]
- Responsáveis: [quem]
- Stakeholders: [quem é afetado]

## Stack
- Linguagens/frameworks: [lista]
- Infra: [onde roda]
- Repositório: [link]

## Dívidas conhecidas
- [item]
- [item]
```

Regra: se um campo não tem conteúdo relevante, omita. Template é teto, não piso.

---

## Componente 2 — Lista de problemas

Índice vivo. Componente mais importante do RSOP.

### Regras

- **Problema:** tudo que preocupa engenheiro, usuário ou ambos. Bug, dívida, limitação, risco, conflito.
- **Nível de resolução:** descrição evolui (sintoma → hipótese → diagnóstico). O próprio nome do problema carrega a precisão atual.
- **Severidade:** prefixo `[A]` alta, `[M]` média, `[B]` baixa. Sem coluna separada.
- **Status:** `ativo` ou `passivo`. Dinâmico — passivo pode reativar.
- **Na dúvida, inclua.** Reclassificar é barato; reconstruir contexto perdido não.
- **Não entram:** bugs pontuais resolvidos no mesmo dia, ajustes cosméticos. Ficam só no SOAP.
- **Exceção — segurança:** vulnerabilidades **sempre** entram na lista, mesmo se corrigidas no mesmo dia. Ao resolver, viram passivo com `reativável? sim — vigiar recorrência`. Severidade mínima `[M]`; `[A]` se explorável em produção.

### Artefato: `rsop/lista_problemas.md`

```markdown
# Lista de problemas
- **Projeto:** [nome] — **Última revisão:** [data]

## Ativos
| # | Problema | Desde | Últ. SOAP |
|---|----------|-------|-----------|
| 1 | [A] N+1 queries listagem pedidos | 2026-03-10 | 2026-04-12 |
| 2 | [M] sem alerta em saturação redis | 2026-04-01 | 2026-04-15 |

## Passivos
| # | Problema | Ativo em | Fechado por | Reativável? |
|---|----------|----------|-------------|-------------|
| 1 | [B] timeout em webhook legacy | 2025-11 → 2026-02 | refactor webhook v2 | não |
```

Sem coluna "Notas". Evolução mora no SOAP referenciado.

---

## Componente 3 — SOAP

Registro de evolução da sessão. Toda sessão gera um SOAP — sem exceção.

**Modelo e-SUS PEC (RCOP):** S e O são tópicos telegráficos. A e P são **por problema**, lista numerada, com correspondência 1:1 entre A e P. Prosa extensa desqualifica o registro.

### Princípio

**S e O bem feitos são a fundação.** De escuta confusa sai plano confuso. Quando as demandas são captadas corretamente, o plano emerge coerente. A e P são consequência — não lugar de compensar S e O ruins.

### Regras de escrita

- Ordem direta: sujeito-verbo-complemento.
- Sem artigos e conectivos desnecessários quando o sentido se preserva.
- Um tópico = uma informação.
- Se retirar a linha e nada se perder, a linha não existia.
- Não inventar: só o que foi observado, relatado ou medido.
- Distinguir fonte quando relevante (usuário / log / terceiro).

### S — Subjetivo

O que o usuário/stakeholder relata. **Três sub-slots telegráficos:**

- **Demandas:** o que espera resolver. 1 tópico por demanda.
- **Queixas:** o que reporta sem expectativa de solução. Ainda assim é dado diagnóstico — pode revelar o problema real.
- **Notas:** opcional. SIFE quando relevante (Sentimentos / Ideias sobre a causa / Funcionalidade afetada / Expectativas), padrão de demanda aparente suspeito (cartão de visita, exploratória, shopping, cure-me), hipótese de demanda oculta. Omita se vazia.

Separar D de Q é condição para não ir na direção errada. SIFE é o instrumento que revela demanda oculta ou mal-elaborada — use-o quando D e Q sozinhos não explicam o quadro. Demanda oculta frequentemente aparece no final da escuta; volte ao S e atualize quando surgir.

### O — Objetivo

Tópicos telegráficos. O que foi observado, medido, verificado. Sem sub-slots. Só o que foi efetivamente examinado — o exame é dirigido à natureza do problema, não checklist genérico. Fonte explícita quando útil (log, código, terceiro).

### A — Avaliação

Lista numerada. **Máximo 5 palavras por item.** Cada item referencia um `#` da lista de problemas (novo ou existente).

### P — Plano

Lista numerada. **1:1 com A.** Um plano para cada avaliação. Uma linha cada.

### R — Reflexão

**Uma linha.** Síntese do ciclo: viés percebido, lacuna descoberta, apego a solução própria, divergência do plano, ou "ciclo coerente, sem desvio". Omita se nada a acrescentar.

### Artefato: `rsop/soap/YYYY-MM-DD_contexto.md`

```markdown
# SOAP 2026-04-15 — rate limit login
- Problemas: #1, #2

## S
**Demandas**
- corrigir rate limit errante no login hoje

**Queixas**
- cliente reclamou de lentidão geral na semana
- equipe acha que redis "não é confiável"

**Notas**
- SIFE: frustração alta, pressão por SLA; ideia do usuário: "culpa do redis"
- possível demanda oculta: confiança no stack de cache, não só o bug

## O
- logs (produção): HTTP 429 a cada ~30 req/s
- redis CLI: counter correto, TTL coerente
- código middleware: janela fixa 10s, não desliza

## A
1. #1 janela rate limit mal configurada
2. #2 falta alerta saturação redis

## P
1. corrigir window → 60s fixo deslizante
2. adicionar prometheus alert + runbook

## R
- ciclo coerente; demanda oculta sobre confiança no redis merece follow-up
```

Notar: A1 = 5 palavras, A2 = 5 palavras; cada A referencia um `#`; P é 1:1 com A; R é 1 linha.

---

## Regras de operação

1. Toda sessão gera SOAP.
2. Lista de problemas é o índice — mantenha atualizada.
3. S separa Demandas de Queixas. Sem essa separação, o plano vai na direção errada.
4. A e P são 1:1, por problema. Nunca prosa livre.
5. A ≤ 5 palavras. Se estourar, o problema está mal nomeado — refine o `#` na lista.
6. R é uma linha. Síntese ou omissão — nunca parágrafo.
7. Na dúvida, inclua na lista. Reclassificar é barato.
8. Dados base mudam só em mudança estrutural.

---

## Uso com `/rsop`

- `/rsop init` — cria estrutura + artefatos vazios.
- `/rsop dados` — exibe/atualiza dados base.
- `/rsop lista` — exibe lista de problemas.
- `/rsop soap` — cria nova nota SOAP vinculada a problemas da lista.
- `/rsop revisar` — revisa lista (reclassifica, atualiza descrição, move ativo↔passivo).
- `/rsop status` — resumo: data de dados base, #ativos/#passivos, último SOAP.
