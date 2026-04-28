---
name: rsop
version: "1.4.0"
author: Iago Leal <github.com/iago-leal>
description: Registro de Software Orientado por Problemas — prontuário longitudinal do software, inspirado no RMOP de Lawrence Weed (1968) e no modelo RCOP do e-SUS PEC. Formato enxuto, telegráfico, orientado por problema. Schema da `lista_problemas.md` distingue dívida consciente × acidental (coluna Tipo) e codifica prazo de revisitar (coluna Revisitar). ATIVE SEMPRE que o usuário digitar /rsop, pedir para documentar estado de um sistema, registrar um incidente ou interação significativa com um projeto, criar ou atualizar lista de problemas de um software, registrar SOAP de um projeto, criar dados base de um sistema, ou mencionar "prontuário do software". Também ative quando a skill `mdcu` referenciar o RSOP como dependência. Ative proativamente quando o contexto indicar que o usuário está trabalhando em um projeto sem documentação longitudinal estruturada. NÃO ative para documentação pontual de código (docstrings, README simples) ou para registro de decisões isoladas (use ADRs diretamente).
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
├── lista_problemas.md      # ATIVOS — injetado no CLAUDE.md do projeto
├── passivos.md             # ARQUIVO MORTO — não injetado no system prompt
├── seguranca.md            # opcional — gerido pela skill `mdcu-seg`
└── soap/
    └── YYYY-MM-DD_contexto.md
```

**Princípio da separação ativos/passivos:** o `lista_problemas.md` é o arquivo **ativo**, referenciado e injetado no `CLAUDE.md` do projeto (ou equivalente) — cada token ali consome janela de contexto e atenção do agente. Problemas fechados não têm direito permanente a esse espaço. Passivos vão para arquivo estático em disco (`passivos.md`) — consultáveis sob demanda, fora do contexto injetado por padrão.

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

## Componente 2 — Lista de problemas (ATIVOS)

Índice vivo. Componente mais importante do RSOP. **Hospeda apenas problemas ativos** — é o que é referenciado/injetado no `CLAUDE.md` do projeto.

### Regras

- **Problema:** tudo que preocupa engenheiro, usuário ou ambos. Bug, dívida, limitação, risco, conflito.
- **Nível de resolução:** descrição evolui (sintoma → hipótese → diagnóstico). O próprio nome do problema carrega a precisão atual.
- **Severidade:** prefixo `[A]` alta, `[M]` média, `[B]` baixa. Sem coluna separada.
- **Status neste arquivo:** apenas `ativo`. Passivos vivem em `passivos.md`. Queixa-triada-aceita usa prefixo `[aceito-arquivado]` na coluna `#` (ver "Triagem precisa-resolver" abaixo + `framework/glossary.md` RN-D-015).
- **Tipo:** distingue **dívida consciente** (escolha informada com prazo de revisitar) de **acidental** (default, omitido). Ver "Dívida consciente × acidental" abaixo + `framework/glossary.md`.
- **Revisitar:** prazo de revisitação para dívidas conscientes — data ISO (`2026-Q3`, `2026-09-15`) OU condição (`pós migração v2`, `quando >100 usuários`) OU `—` (não aplicável). Livre, telegráfico.
- **Na dúvida, inclua.** Reclassificar é barato; reconstruir contexto perdido não.
- **Não entram:** bugs pontuais resolvidos no mesmo dia, ajustes cosméticos. Ficam só no SOAP.
- **Exceção — segurança:** vulnerabilidades **sempre** entram como ativos, mesmo se corrigidas no mesmo dia. Ao resolver, migram para `passivos.md` com `reativável? sim — vigiar recorrência`. Severidade mínima `[M]`; `[A]` se explorável em produção.

### Dívida consciente × acidental

**Dívida consciente:** escolha informada de adiar resolução com motivo declarado e prazo de revisitar (urgência operacional, validação de hipótese, custo > benefício no momento). É legítima quando documentada — ver `framework/principles.md` F-3 (decisão informada).

**Dívida acidental:** dívida que existe sem ter sido escolhida — bug que persiste, limitação descoberta tarde, risco não previsto. Default da coluna `Tipo` (omitido).

**Regra de operação:**
- Dívida consciente exige **`Tipo: consciente` + `Revisitar` preenchidos**. Sem prazo, vira acidental travestida.
- Dívida acidental **omite ambas as colunas** (preserva minimalismo P-5).

### Triagem precisa-resolver

Nem toda queixa vira `#` que precisa resolver — algumas são ouvidas, validadas e arquivadas como aceitas pelo stakeholder (RN-D-015 em `framework/glossary.md`). Para evitar que reapareçam como "novas" em sessão futura:

- Queixa-triada-aceita entra na lista com prefixo `[aceito-arquivado]` na coluna `#`.
- Não conta para métricas de "problemas a resolver".
- Documenta motivo na descrição do problema (ex: `[aceito-arquivado] [B] log verbose em dev — stakeholder aceita ruído pra debug`).

### Artefato: `rsop/lista_problemas.md`

```markdown
# Lista de problemas — Ativos
- **Projeto:** [nome] — **Última revisão:** [data]

| # | Problema | Tipo | Revisitar | Desde | Últ. SOAP |
|---|----------|------|-----------|-------|-----------|
| 1 | [A] N+1 queries listagem pedidos |  |  | 2026-03-10 | 2026-04-12 |
| 2 | [M] sem alerta em saturação redis |  |  | 2026-04-01 | 2026-04-15 |
| 3 | [M] cache em memória single-node | consciente | pós migração k8s | 2026-04-10 | 2026-04-15 |
| [aceito-arquivado] | [B] log verbose em dev — stakeholder aceita ruído | | | 2026-04-05 | 2026-04-15 |
```

**Defaults implícitos:** Tipo omitido = `acidental`; Revisitar omitido = sem prazo (faz sentido para acidentais).

**Sem seção `## Passivos`. Sem coluna "Notas".** Evolução mora no SOAP referenciado.

---

## Componente 3 — Arquivo Morto (PASSIVOS)

Problemas fechados/resolvidos vivem aqui. **Arquivo estático em disco.** Não é injetado no system prompt por padrão — poupa tokens e atenção.

### Regra de consulta (importante)

A IA só deve **consultar** `rsop/passivos.md` em dois casos:
1. **Suspeita explícita de regressão** — comportamento atual tem cheiro de problema antigo já fechado.
2. **Requisição direta do usuário** — "veja se já resolvemos isso antes", "olha os passivos", etc.

Fora desses casos, passivos são invisíveis ao agente. Isso é feature, não bug: ciclo cognitivo rápido precisa de contexto enxuto.

### Artefato: `rsop/passivos.md`

```markdown
# Passivos — Arquivo morto
- **Projeto:** [nome] — **Última migração:** [data]

| # | Problema | Ativo em | Fechado por | Fechado em | Reativável? |
|---|----------|----------|-------------|------------|-------------|
| 1 | [B] timeout em webhook legacy | 2025-11 → 2026-02 | refactor webhook v2 | 2026-02-14 | não |
| 3 | [M] log de auth com senha em claro | 2026-03-20 → 2026-04-02 | redact hook no middleware | 2026-04-02 | sim — vigiar recorrência (segurança) |
```

Reativação: se um passivo volta à vida (regressão), ele é **reaberto no `lista_problemas.md` como ativo** e a linha em `passivos.md` recebe nota `reaberto em [data] — ver SOAP [ref]`.

---

## Componente 4 — SOAP

Registro de evolução da sessão. Toda sessão MDCU gera um SOAP — sem exceção. (Micro-commits técnicos durante F6 não exigem SOAP próprio — são checkpoints dentro da sessão; o SOAP sela o fechamento.)

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

**Fonte do S no fechamento:** lido primariamente do `_mdcu.md` (campo `S:` preenchido durante F2), não reconstruído de memória.

### O — Objetivo

Tópicos telegráficos. O que foi observado, medido, verificado. Sem sub-slots. Só o que foi efetivamente examinado — o exame é dirigido à natureza do problema, não checklist genérico. Fonte explícita quando útil (log, código, terceiro).

**Fonte do O no fechamento:** lido primariamente do `_mdcu.md` (campo `O:` preenchido durante F3), não reconstruído de memória.

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

## Checklist de qualidade do SOAP

> **Cap F-4 declarado** (`framework/principles.md`): este checklist mede o **necessário, não o suficiente**. Satisfação clínica do usuário (F-3) é desfecho longitudinal, não verificável no fechamento. "Parte da arte" da tradução problema↔requisito é incompressível — score binário não captura, só a leitura crítica do orquestrador-instância (F-2 camada 3) e o uso real do software ao longo do tempo.
>
> **Posicionamento:** auto-aplicado pelo orquestrador na F6.c do MDCU (tradução de retorno + fechamento), antes de invocar `commit-soap`. **Não-bloqueante:** falha em item subjetivo (10) é nota mental; falha em item objetivo (1-9) é correção do SOAP antes de selar.

**10 itens binários:**

1. **S separa Demandas de Queixas** (sub-slots presentes, mesmo se um deles vazio com `—`)? — RN-D-004 + Componente 4.S
2. **Padrão de demanda aparente classificado** quando aplicável (cartão de visita / exploratória / shopping / cure-me) ou justificada ausência? — Componente 4.S Notas
3. **A é lista numerada com itens ≤5 palavras**? — Componente 4.A
4. **P é 1:1 com A** (cada A tem um P; nenhum P órfão)? — Componente 4.P
5. **Cada item de A referencia `#` válido** na `lista_problemas.md` (ativo ou prefixado `[aceito-arquivado]`)? — Componente 4.A
6. **R é uma linha OU omitido** (nunca parágrafo)? — RN-D-006 + Componente 4.R
7. **S e O foram lidos de `_mdcu.md` no fechamento**, não reconstruídos da memória? — RN-D-007 + Componente 4 fontes
8. **Dívida consciente (se introduzida) tem `Tipo: consciente` + `Revisitar` preenchidos** na `lista_problemas.md`? — RN-D-016
9. **Aceito-arquivado (se aplicável) usa prefixo `[aceito-arquivado]` na coluna `#`** com motivo na descrição? — RN-D-015
10. **Anamnese atualizada se padrão novo do stakeholder observado** durante a sessão? — F-5 (`framework/principles.md`)

**Como aplicar:** o orquestrador percorre os 10 itens em sequência ao terminar de redigir o SOAP. Cada item retorna `sim` / `não` / `n/a`. Não há score; não há soma; não há gate.

- **Itens 1-9:** se algum retorna `não`, **corrigir o SOAP antes de invocar `commit-soap`**. São pré-condições de qualidade objetivas — falha aqui significa SOAP malformado.
- **Item 10:** subjetivo ("padrão novo"). Se em dúvida, atualizar a anamnese — segue RN-D-003 ("na dúvida, inclua").

**Quando usar `n/a`:**
- Item 2 (`n/a`) se a sessão foi totalmente operacional (não houve escuta de novo problema — ex: `/rsop revisar`)
- Item 8 (`n/a`) se nenhuma dívida consciente foi introduzida nesta sessão
- Item 9 (`n/a`) se nenhuma queixa-triada-aceita foi introduzida

**Anti-padrão a vigiar:** percorrer o checklist mecanicamente como ritual sem leitura crítica. O checklist é gatilho para releitura, não substituto dela. Se 10/10 sim mas o SOAP "soa raso" para o orquestrador, o problema não está nos 10 itens — está em F-4 (a parte da arte que o checklist não mede). Não selar até resolver.

---

## Regras de operação

1. Toda sessão MDCU gera SOAP no fechamento.
2. Lista de problemas (ativos) é o índice — mantenha atualizada e enxuta.
3. **Passivos vão para arquivo morto.** `lista_problemas.md` contém só ativos — é o que vai injetado no CLAUDE.md. Tokens não-ativos são custo sem benefício.
4. S separa Demandas de Queixas. Sem essa separação, o plano vai na direção errada.
5. A e P são 1:1, por problema. Nunca prosa livre.
6. A ≤ 5 palavras. Se estourar, o problema está mal nomeado — refine o `#` na lista.
7. R é uma linha. Síntese ou omissão — nunca parágrafo.
8. Na dúvida, inclua na lista. Reclassificar é barato.
9. Dados base mudam só em mudança estrutural.
10. **Consulta a `passivos.md` só por suspeita de regressão ou pedido explícito.** Fora disso, é ruído.

---

## Uso com `/rsop`

- `/rsop init` — cria estrutura + artefatos vazios (incluindo `passivos.md` vazio).
- `/rsop dados` — exibe/atualiza dados base.
- `/rsop lista` — exibe `lista_problemas.md` (ativos). **Não inclui passivos por default.**
- `/rsop passivos` — exibe `passivos.md` sob demanda. Usar apenas se suspeita de regressão ou se o usuário pediu.
- `/rsop soap` — cria nova nota SOAP vinculada a problemas da lista ativa. **Lê `_mdcu.md` da sessão em curso** para hidratar S e O (não reconstrói de memória).
- `/rsop revisar` — revisa lista ativa: reclassifica severidade, atualiza descrição, e **move problemas resolvidos de `lista_problemas.md` → `passivos.md`** (com data de fechamento e referência ao SOAP que resolveu). Também move passivos reabertos no sentido inverso, se aplicável.
- `/rsop regressao [#]` — consulta o `passivos.md` explicitamente em busca de problema fechado que pode ter retornado. Se encontrado, reabre no arquivo ativo.
- `/rsop status` — resumo: data de dados base, #ativos, #passivos (número, não conteúdo), último SOAP.
