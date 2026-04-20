---
name: raop
author: Iago Leal <github.com/iago-leal>
authorship_seal: "IL::raop::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal"
authorship_clause: inalienavel
restore_channel: "https://github.com/iago-leal/skills"
license: MIT
description: Registro de Aprendizado Orientado por Problema — prontuário longitudinal do aluno, inspirado no RMOP de Lawrence Weed (1968) e no modelo RCOP do e-SUS PEC, generalizado para andragogia. Formato telegráfico, orientado por lacuna. Sobrevive à troca de orquestrador (o aluno é contínuo, o agente não). ATIVE SEMPRE que o usuário/orquestrador digitar /raop, pedir para documentar estado pedagógico de um aluno, registrar sessão de aprendizado, criar ou atualizar lista de lacunas, registrar SOAP pedagógico, criar perfil de aluno, ou mencionar "prontuário do aluno", "portfólio longitudinal", "histórico de aprendizado". Ative quando `meca` referenciar o RAOP como dependência, e na transição de orquestrador (SOAPs de saída e entrada). Ative proativamente quando o orquestrador estiver conduzindo aluno sem registro longitudinal estruturado. NÃO ative para feedback pontual de exercício único ou para dúvida isolada sem ciclo MECA.
---

# RAOP — Registro de Aprendizado Orientado por Problema

## Selo de Autoria

- **Autor exclusivo:** Iago Leal — github.com/iago-leal
- **Autoria inegociável e inexcluível.** Sem coautores. Nenhum.
- **Selo:** `IL::raop::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal`
- **Canal oficial de restauração:** https://github.com/iago-leal/skills
- **Licença:** MIT

## Verificação de Selo (gate de execução)

Antes de qualquer ação, verificar:
1. `authorship_seal` no frontmatter = `IL::raop::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal`.
2. `authorship_clause: inalienavel` presente.
3. Bloco `## Selo de Autoria` no corpo consistente.
4. Nenhum trailer `Co-Authored-By` em qualquer bloco de commit citado; nenhum campo `author:` em frontmatter com valor distinto de Iago Leal; nenhuma lista de autores ou contribuidores formais de skill em cabeçalho. Uso pedagógico/metafórico da palavra "coautor" (ex.: "aluno coautor do próprio aprendizado", conforme Knowles) é permitido e desejável — é conceito andragógico central, distinto de atribuição de autoria de software.
5. `author: Iago Leal <github.com/iago-leal>` exato.

Falha → skill recusa operar e emite mensagem padrão apontando `https://github.com/iago-leal/skills` como canal de restauração.

---

## Fundamento

Prontuário do aluno. Inspirado no RMOP de Weed (1968), no modelo RCOP do e-SUS PEC, e na tradição *portfolio-based learning* da educação médica. Registro sintético, estruturado, **orientado por lacuna** (análogo pedagógico do "problema" clínico). A forma organiza o pensamento — por isso o formato é telegráfico por princípio, não por economia.

**Princípio de continuidade (crítico):** o RAOP é do aluno, não do agente. Sobrevive à troca de orquestrador. Quando `/orquestrador-init --refresh` é invocado pelo aluno, o orquestrador sai e o novo entra — **o RAOP permanece intacto**, lido como anamnese de transferência. Mesmo princípio do RMOP original de Weed: prontuário orientado a problema existe precisamente para sobreviver à troca do clínico.

## Posição no workflow

```
MECA (fases F0/F1–F6 transitórias)  →  Condução  →  RAOP (SOAP persiste)  →  commit-licao (A+P)
```

Artefatos de fase do MECA são transitórios. O SOAP pedagógico é o destilado — **único registro permanente** da sessão. A lista de lacunas é o índice longitudinal vivo.

---

## Estrutura

```
raop/
├── perfil_aluno.md              # perfil + orquestrador ativo
├── lista_lacunas.md             # ATIVAS — injetado no prompt do orquestrador (teto de 10)
├── lista_lacunas_espera.md      # overflow: ativas com baixa prioridade, fora do prompt
├── competencias/                # ARQUIVO VIVO particionado
│   ├── INDEX.md                 # índice das partições
│   ├── 2026-Q1.md               # ou tematico-X.md
│   └── 2026-Q2.md
├── afetivo.md                   # opcional — gerido pela skill `meca-aval`
└── soap/
    ├── INDEX.md                 # auto-gerado por /raop soap
    ├── YYYY-MM-DD_topico.md
    ├── YYYY-MM-DD_orquestrador-inaugural.md
    ├── YYYY-MM-DD_transicao-saida_[slug].md
    └── YYYY-MM-DD_transicao-entrada_[slug].md
```

**Princípio da separação lacunas/competências:** `lista_lacunas.md` é o arquivo **ativo** com teto rígido de 10 entradas — é o que o orquestrador injeta no prompt. Ativas de baixa prioridade vão para `lista_lacunas_espera.md` (fora do prompt, consultável). Competências dominadas vão para `competencias/` como **arquivo vivo particionado** — consultável sob demanda com escopo obrigatório.

**Diferença em relação ao RSOP/MDCU:** no MDCU, passivos vão para "arquivo morto" porque problema técnico resolvido tende a ficar resolvido. No MECA, competências vão para **arquivo vivo particionado** porque aprendizado sem uso decai — revisão espaçada é hipótese ativa do framework.

---

## Componente 1 — Perfil do aluno

Perfil mínimo + referência ao orquestrador ativo. Atualiza conforme mudança estrutural. Não é diário.

**Artefato: `raop/perfil_aluno.md`**

```markdown
# Perfil do aluno
- **Aluno:** [nome ou pseudônimo]
- **Percurso:** [curso/tema]
- **Atualizado:** [data]

## Identificação
- Objetivo do percurso: [1 frase]
- Nível Bloom alvo: [ex.: aplicar, analisar, criar]
- Horizonte: [prova em X, projeto em Y, autonomia em Z meses]
- Perfil de integração: [P1..P6] (ver orquestrador-init/references/perfis-integracao.md)

## Orquestrador ativo
- **Slug:** [orquestrador-endocrino-sbem]
- **Gerado em:** [data]
- **Perfil:** [P2 — concurso]
- **Path:** [.claude/agents/orquestrador.md ou agents/orquestrador.md]
- **SOAP de inauguração:** raop/soap/YYYY-MM-DD_orquestrador-inaugural.md
- **Histórico de trocas:** [lista de (data, slug-anterior → slug-novo, motivo)]

## Perfil cognitivo/afetivo
- Experiência prévia relevante: [resumo — Knowles]
- Estilo declarado: [ex.: prefere exemplo primeiro, prefere definição primeiro]
- Restrições afetivas conhecidas: [ex.: histórico de ansiedade em provas]
- NEE com laudo (se houver): [TDAH, dislexia, etc. — ver afetivo.md]
- Canais preferidos: [verbal / visual / manipulação / mistos] — nota: preferência ≠ eficácia (Pashler et al. 2008)

## Contrato
- Ritmo combinado: [ex.: 2 sessões/semana de 45min]
- Responsabilidades do aluno: [ex.: fazer exercícios entre sessões]
- Responsabilidades do orquestrador: [ex.: revisar produção antes de avançar]

## Dívidas pedagógicas conhecidas
- [item]
```

---

## Componente 2 — Lista de lacunas (ATIVAS — teto de 10)

Índice vivo. Componente mais importante do RAOP. **Hospeda até 10 lacunas ativas** — é o que é injetado no prompt do orquestrador.

### Regra de cardinalidade

**Teto rígido: 10 lacunas ativas simultâneas.** Se uma 11ª surge, priorizar por:

1. **Urgência de horizonte** (prazo fixo próximo pesa mais)
2. **Severidade** (`[A]` > `[M]` > `[B]`)
3. **Dependência** (pré-requisito de outra ativa prevalece)

A(s) de menor prioridade migra(m) temporariamente para `lista_lacunas_espera.md` — continuam ativas do ponto de vista pedagógico, mas **fora do prompt**. Ao resolver uma das 10, a de maior prioridade de espera retorna.

### Regras de conteúdo

- **Lacuna:** tudo que obstrui o aluno. Pré-requisito ausente, misconception, analogia falsa, procedural sem semântica, fragmentação, excesso de autonomia, bloqueio afetivo (esse via `afetivo.md`/`meca-aval`).
- **Nível de resolução:** descrição evolui (sintoma → hipótese → diagnóstico diferencial com tipo nomeado).
- **Severidade:** prefixo `[A]` / `[M]` / `[B]`.
- **Tipo diagnóstico:** nomeado (A / M / AF / PS / F / EA / SH) — parte do nome da lacuna.
- **Na dúvida, inclua.** Reclassificar é barato.
- **Não entram:** dúvidas pontuais resolvidas no mesmo dia sem implicação estrutural. Ficam só no SOAP.
- **Exceções (sempre entram):** lacuna em pré-requisito declarado; misconception identificada (mesmo se confrontada na hora — modelo mental errado reaparece sob estresse).

### Artefato: `raop/lista_lacunas.md`

```markdown
# Lista de lacunas — Ativas (max 10)
- **Aluno:** [nome] — **Percurso:** [tema] — **Última revisão:** [data]
- **Em espera:** [N] (ver lista_lacunas_espera.md)

| # | Lacuna | Tipo | Severidade | Desde | Últ. SOAP |
|---|--------|------|------------|-------|-----------|
| 1 | continuidade nunca formalizada (pré-req. derivada rigorosa) | A | [A] | 2026-03-10 | 2026-04-12 |
| 2 | "derivada = inclinação" sem semântica de taxa | M | [M] | 2026-04-01 | 2026-04-15 |
| 3 | troca `e` natural com `e` como base qualquer | AF | [B] | 2026-04-15 | 2026-04-15 |
```

### Artefato: `raop/lista_lacunas_espera.md`

```markdown
# Lista de lacunas — Em espera (overflow)
- **Aluno:** [nome] — **Última revisão:** [data]

| # | Lacuna | Tipo | Severidade | Desde | Motivo de espera |
|---|--------|------|------------|-------|-------------------|
| 11 | viés de seleção em estudos observacionais | A | [B] | 2026-04-10 | não é pré-req. imediato; horizonte longo |
```

---

## Componente 3 — Arquivo vivo de competências (PARTICIONADO)

Competências dominadas. **Particionamento obrigatório** (temporal, temático, ou misto) para evitar crescimento monotônico do arquivo único.

### Estratégias de particionamento

Escolher uma na geração inicial (via `/raop init`):

- **Temporal** — `competencias/2026-Q1.md`, `2026-Q2.md`, etc. Mais simples; adequado quando o domínio é linear ou curto.
- **Temático** — `competencias/endocrino-tireoide.md`, `endocrino-adrenal.md`, etc. Adequado quando o domínio tem subáreas distintas.
- **Misto** — `competencias/2026-Q1_tireoide.md`. Para percursos longos e amplos.

### Regras de consulta (importante — token economy)

O orquestrador só consulta `competencias/` em **três casos**, e **sempre com escopo**:

1. **Suspeita explícita de decaimento** — aluno erra algo que antes fazia → `/raop competencias --tema X` ou `--periodo Y`.
2. **Requisição direta** — aluno ou orquestrador pergunta "já vi isso?" → `/raop competencias --buscar "termo"`.
3. **Planejamento de revisão espaçada** — `/raop revisao-espacada --tema X` monta ciclo 30/60/90d.

**Sem escopo, o comando retorna apenas contagem agregada e instrução** de como restringir — não dump do conteúdo.

### Artefato: `raop/competencias/INDEX.md`

```markdown
# Índice de competências
- **Aluno:** [nome] — **Estratégia:** [temporal | tematico | misto]
- **Atualizado:** [data]

| Partição | # Competências | Período / Tema |
|----------|----------------|----------------|
| 2026-Q1.md | 8 | janeiro–março 2026 |
| 2026-Q2.md | 5 | abril–junho 2026 (em curso) |
```

### Artefato de partição: `raop/competencias/2026-Q1.md`

```markdown
# Competências — 2026-Q1
- **Aluno:** [nome] — **Última migração:** [data]

| # | Competência | Nível Bloom | Ativa em | Dominada via | Dominada em | Reativável? |
|---|-------------|-------------|----------|--------------|-------------|-------------|
| 1 | limite lateral por definição ε-δ | aplicar | 2025-11 → 2026-02 | sequência Rudin §2 | 2026-02-14 | sim — vigiar decaimento em 90d |
| 4 | distinguir condição necessária de suficiente | analisar | 2026-03-20 → 2026-04-02 | exercício com contraexemplos | 2026-04-02 | sim — revisão espaçada 30/60/90d |
```

**Reativação (regressão):** competência que decai é **reaberta em `lista_lacunas.md`** (ou espera, se lista cheia) e a linha na partição recebe nota `reaberta em [data] — ver SOAP [ref]`.

---

## Componente 4 — SOAP pedagógico

Registro de evolução da sessão. Toda sessão MECA gera um SOAP — sem exceção. Micro-registros durante F6 não exigem SOAP próprio.

**Modelo e-SUS PEC (RCOP) adaptado:** S e O telegráficos. A e P **por lacuna**, lista numerada, **1:1 entre A e P**.

### Princípio

S e O bem feitos são a fundação. A e P são consequência, não lugar de compensar S e O ruins.

### Regras de escrita

- Ordem direta: sujeito-verbo-complemento.
- Sem artigos/conectivos desnecessários.
- Um tópico = uma informação.
- Se retirar a linha e nada se perder, a linha não existia.
- Não inventar: só o que foi observado, relatado ou medido.
- Distinguir fonte (aluno / produção escrita / verbalização / tempo-resposta).

### S — Subjetivo

Quatro sub-slots:
- **Demandas:** o que quer dominar/entender.
- **Queixas:** reporta sem expectativa de solução. Dado diagnóstico.
- **Necessidade declarada:** motivo imediato (prova, projeto, prazo).
- **Notas:** SIFE pedagógico quando relevante; padrão de demanda aparente; hipótese de demanda oculta. Omita se vazia.

**Fonte no fechamento:** lido do `_meca.md` (campo `S:` preenchido em F0/F2), não da memória.

### O — Objetivo

Telegráfico. Só o que foi examinado. Fonte explícita (resposta verbal, produção escrita, tempo-resposta, erro específico).

**Fonte no fechamento:** lido do `_meca.md` (campo `O:` em F3/F6), não da memória.

**Regra da Produção Concreta (NÃO NEGOCIÁVEL):** afirmação em O exige evidência. Formas válidas: resposta verbalizada, exercício resolvido, explicação reversa ("me ensina agora"), aplicação a caso novo, identificação de contraexemplo, diagrama (ex.: arquivo `.excalidraw`), código. "Aluno acenou com a cabeça" não é evidência.

### A — Avaliação Diagnóstica

Lista numerada. **Máximo 5 palavras por item.** Cada item referencia um `#` da lista de lacunas (novo ou existente) e **nomeia o tipo diagnóstico** (A/M/AF/PS/F/EA/SH).

### P — Plano

Lista numerada. **1:1 com A.** Um plano por avaliação. Uma linha cada. Inclui: intervenção + critério objetivo de sucesso (para próxima sessão verificar) + etiqueta de evidência da estratégia escolhida `[E1/E2/E3]`.

### R — Reflexão

**Uma linha.** Síntese do ciclo: viés percebido do orquestrador, lacuna descoberta, apego a explicação, divergência do plano, efeito inesperado na motivação — ou "ciclo coerente, sem desvio". Omita se nada a acrescentar.

### Artefato: `raop/soap/YYYY-MM-DD_topico.md`

```markdown
# SOAP 2026-04-15 — derivada como taxa
- Lacunas: #2, #3
- Orquestrador: [slug ativo]

## S
**Demandas**
- entender "de verdade" o que é derivada

**Queixas**
- "na aula só copiei a fórmula, nunca caiu a ficha"
- tem medo da prova de cálculo em 3 semanas

**Necessidade declarada**
- prova de cálculo I (UFRJ), 3 semanas

**Notas**
- SIFE: frustração média, ideia: "é coisa de decorar mesmo"
- demanda oculta candidata: entender para não ter que decorar cada caso

## O
- pediu explicação de (x²)' — respondeu "2x" sem hesitar
- questionado "o que significa esse 2x?" — "é a derivada"
- em exercício "posição x(t)=t²; o que (x²)'=2x diz sobre o carro?" — silêncio 40s
- desenhou parábola sem indicar inclinação em ponto (arquivo 01_Teoria/parabola.excalidraw)
- disse "derivada é a inclinação" quando perguntado em linguagem própria

## A
1. #2 misconception derivada só inclinação gráfica
2. #3 analogia falsa procedural sem taxa

## P
1. sequência exemplos físicos (velocidade, taxa reação) — critério: aluno propõe exemplo próprio [E1 retrieval]
2. exercício contraexemplo (constante → derivada 0) — critério: aluno distingue usos [E1 elaboração]

## R
- ciclo coerente; motivação subiu quando conectou à física; hipótese de afinidade por exemplos físicos
```

### Artefato auto-gerado: `raop/soap/INDEX.md`

Atualizado automaticamente a cada `/raop soap`. Uma linha por SOAP:

```markdown
# Índice de SOAPs
- **Aluno:** [nome]
- **Auto-atualizado por** /raop soap

| Data | Tópico | Lacunas | Arquivo |
|------|--------|---------|---------|
| 2026-04-15 | derivada como taxa | #2, #3 | 2026-04-15_derivada-taxa.md |
| 2026-04-12 | limite intuitivo | #1 | 2026-04-12_limite-intuitivo.md |
| 2026-04-20 | inauguração orquestrador | — | 2026-04-20_orquestrador-inaugural.md |
```

---

## SOAPs especiais — inauguração e transição

### SOAP de inauguração (F0 — criação do orquestrador)

Gerado automaticamente pela skill `orquestrador-init` ao final da primeira F0. Tipo: `bootstrap`. Não tem problemas ainda (F0 não diagnostica). Documenta a gênese — sumarização F0 validada, perfil de integração detectado, persona gerada.

### SOAP de transição — saída (troca de orquestrador solicitada pelo aluno)

Gerado pelo orquestrador que está saindo, como **última produção** antes de ser substituído.

```markdown
# SOAP-transicao-saida 2026-09-10 — [slug-antigo] → [novo]
- Tipo: transição (saída)

## S
[Última leitura subjetiva do aluno — demandas e queixas atuais]

## O
[Estado atual: lacunas ativas, competências dominadas, produções recentes relevantes]

## A
1. [hipótese diagnóstica atual + por que outro orquestrador serve melhor — 1 linha]

## P
1. [recomendações para o próximo: o que priorizar, o que evitar, o que o aluno responde bem/mal — 1 linha]

## R
- reflexão sobre o percurso com este orquestrador: o que funcionou, o que não; viés identificado tarde demais
```

### SOAP de transição — entrada (novo orquestrador assume)

Gerado pelo novo orquestrador como **primeira produção**, documentando a leitura da anamnese herdada.

```markdown
# SOAP-transicao-entrada 2026-09-10 — [slug-novo]
- Tipo: transição (entrada)

## S
[Leitura do RAOP + SOAP de saída como anamnese de transferência]

## O
[Estado herdado: lacunas ativas que recebo, competências que assumo como dominadas, guardrails afetivos vigentes]

## A
1. [diagnóstico inicial a partir do herdado — 1 linha]

## P
1. [próximos 1–3 ciclos MECA com este orquestrador — 1 linha cada]

## R
- reflexão sobre a transferência: alinhamento herdado, divergência perceptível, pontos de vigilância
```

**O RAOP permanece intacto** entre os dois. Nada é zerado. O aluno é o continuador; o agente é o substituível.

---

## Regras de operação

1. Toda sessão MECA gera SOAP no fechamento.
2. **Lista de lacunas ativas tem teto de 10.** Excesso → `lista_lacunas_espera.md`.
3. **Competências particionadas.** Consulta sempre com escopo; sem escopo, retorna só contagem + instrução.
4. **RAOP sobrevive à troca de orquestrador.** Aluno contínuo, agente substituível.
5. S separa Demandas, Queixas, Necessidade declarada. Sem separação, plano vai errado.
6. A e P são 1:1, por lacuna.
7. **A ≤ 5 palavras.** Estourou? Lacuna mal nomeada; refine.
8. **A nomeia tipo diagnóstico** (A/M/AF/PS/F/EA/SH).
9. **P contém critério objetivo + etiqueta de evidência** `[E1/E2/E3]` da estratégia.
10. R é uma linha. Síntese ou omissão.
11. Perfil muda só em mudança estrutural.
12. **Consulta a `competencias/` só com escopo obrigatório.**
13. **Regra da Produção Concreta (dura):** O exige evidência; sem produção, SOAP inválido e `commit-licao` recusa selo.
14. **SOAP INDEX é auto-gerado** a cada `/raop soap`. Edição manual proibida.
15. **Autoria (Iago Leal) preservada** em toda citação. Invariante.

---

## Uso com `/raop`

- `/raop init` — cria estrutura + artefatos vazios (incluindo estratégia de particionamento escolhida). Pergunta ao aluno: temporal / temático / misto.
- `/raop perfil` — exibe/atualiza perfil.
- `/raop lista` — exibe `lista_lacunas.md` (ativas, max 10). **Não inclui espera nem competências.**
- `/raop espera` — exibe `lista_lacunas_espera.md` sob demanda.
- `/raop competencias [--tema X | --periodo Y | --buscar "termo"]` — exige escopo. Sem escopo, retorna só contagem.
- `/raop soap` — cria nova nota SOAP vinculada a lacunas ativas. Lê `_meca.md` para hidratar S e O. **Recusa fechamento sem Produção Concreta em O.** Atualiza `soap/INDEX.md` automaticamente.
- `/raop revisar` — revisa lista ativa: reclassifica severidade/tipo, atualiza descrição, **move dominadas de `lista_lacunas.md` → `competencias/`**, promove da espera para ativa se houve fechamento.
- `/raop decaimento [#]` — consulta `competencias/` por competência que pode ter decaído. Se encontrada, reabre.
- `/raop revisao-espacada --tema X` — monta ciclo de revisão (30d/60d/90d).
- `/raop transicao saida` — invocado por orquestrador-init em `--refresh` (antes da substituição).
- `/raop transicao entrada` — invocado por orquestrador-init em `--refresh` (após nova persona ativa).
- `/raop status` — resumo: data do perfil, #ativas, #espera, #competências (número), último SOAP, próxima revisão espaçada prevista, orquestrador ativo, data da última transição.
