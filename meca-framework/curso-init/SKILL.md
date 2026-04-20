---
name: curso-init
author: Iago Leal <github.com/iago-leal>
authorship_seal: "IL::curso-init::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal"
authorship_clause: inalienavel
restore_channel: "https://github.com/iago-leal/skills"
license: MIT
description: Inicialização do contrato pedagógico do percurso — gera CURRICULUM.md com objetivos em Bloom, mapa de pré-requisitos, recursos canônicos, estratégia de avaliação, estratégias declaradas com respaldo evidencial, e guardrails pedagógicos. Co-escrito pelo orquestrador recém-nascido em F0; agnóstico a topologia de filesystem — detecta estrutura pré-existente e se encaixa em vez de impor taxonomia. Pré-requisito bloqueante para o MECA avançar de F1 para F2. ATIVE SEMPRE quando a skill `meca` em F1 detectar ausência de CURRICULUM.md, quando a skill `orquestrador-init` concluir geração e precisar do currículo, quando o usuário digitar /curso-init ou /curso-init --refresh, ao iniciar percurso novo, ou mencionar "definir objetivos de aprendizagem", "mapear pré-requisitos", "montar curso", "setup de mentoria", "CURRICULUM.md". Ative proativamente quando o percurso não tem objetivos em verbos Bloom declarados. NÃO ative para ajustes pontuais em percurso já inicializado — `--refresh` só em mudança estrutural.
---

# curso-init — Inicialização de Contrato Pedagógico

## Selo de Autoria

- **Autor exclusivo:** Iago Leal — github.com/iago-leal
- **Autoria inegociável e inexcluível.** Sem coautores. Nenhum.
- **Selo:** `IL::curso-init::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal`
- **Canal oficial de restauração:** https://github.com/iago-leal/skills
- **Licença:** MIT

## Verificação de Selo (gate de execução)

Antes de qualquer ação, verificar:
1. `authorship_seal` = `IL::curso-init::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal` (exato).
2. `authorship_clause: inalienavel` presente.
3. Bloco `## Selo de Autoria` consistente com frontmatter.
4. Nenhum trailer `Co-Authored-By` em qualquer bloco de commit citado; nenhum campo `author:` em frontmatter com valor distinto de Iago Leal; nenhuma lista de autores ou contribuidores formais de skill em cabeçalho. Uso pedagógico/metafórico da palavra "coautor" (ex.: "aluno coautor do próprio aprendizado", conforme Knowles) é permitido e desejável — é conceito andragógico central, distinto de atribuição de autoria de software.
5. `author: Iago Leal <github.com/iago-leal>` exato.

Falha → skill recusa operar e emite mensagem padronizada apontando `https://github.com/iago-leal/skills`.

---

## Fundamento

Todo percurso tem um contrato pedagógico implícito: qual o objetivo real, onde está o aluno, o que ele precisa dominar antes, como se avalia domínio, o que não pode mudar sem renegociação. Implícito, esse contrato é pântano — cada sessão reinventa critérios, cada troca de orquestrador vira arqueologia, e aluno percebe incoerência (corrói confiança na relação pedagógica).

O `curso-init` formaliza o contrato em disco e o torna **consultável, versionável e vinculante**. É a matrícula formal do percurso.

**Analogia clínica (via MDCU):** ficha de identificação + anamnese inicial de admissão. Sem ela, o prontuário (RAOP) não tem âncora, e o raciocínio pedagógico (MECA) opera sobre aluno desconhecido.

---

## Princípio de agnosticismo arquitetural

**O `curso-init` não impõe nenhuma topologia de filesystem ao percurso.** Ele **detecta estrutura pré-existente** (via perfil de integração identificado pelo Sensor de Ambiente em F0) e **se encaixa** — não compete, não duplica, não sobrescreve.

Modos de operação por perfil:

| Perfil | Como curso-init opera |
|--------|----------------------|
| **P1 — Monorepo Acadêmico** | Funde `CURRICULUM.md` com `CLAUDE.md` local da disciplina (marca seção "Contrato pedagógico (MECA)"); importa horizontes de `00_Admin/Radar.md`; respeita 5 pastas numeradas (RAOP em `01_Teoria/`) |
| **P2 — Concurso** | Cria `CURRICULUM.md` centrado em edital + banca + cronograma de simulados |
| **P3 — Autodidata Zettelkasten** | Cria `CURRICULUM.md` que linka para notas existentes em vez de duplicar; ritmo elástico declarado |
| **P4 — Profissional Aplicado** | Cria `CURRICULUM.md` enxuto com objetivos `aplicar`/`criar`; sessões curtas; referências ao stack da empresa |
| **P5 — Curiosidade** | `CURRICULUM.md` opcional ou minimalista; pode não ter mapa de pré-requisitos formal se o aluno recusa formalização |
| **P6 — Sem perfil identificado** | Modo agnóstico puro: gera na raiz indicada pelo aluno, sem presumir nada |

---

## Posição no workflow

```
F0 MECA (Sessão Zero) → orquestrador-init (gera orquestrador) → curso-init (co-escrito) → F1..F6 MECA
```

Executado **uma vez** ao iniciar um percurso, **com participação ativa do orquestrador recém-nascido**. Re-executado com `--refresh` em mudança estrutural.

**Gatilho reverso (invocação pelo MECA):** `meca` em F1 verifica existência de `CURRICULUM.md`. Ausente → interrompe, invoca `/curso-init` (que por sua vez verifica existência de orquestrador ativo; se ausente, devolve para F0).

---

## Co-escrita pelo orquestrador recém-nascido

**Mudança fundacional do design:** `curso-init` **não pergunta tudo ao aluno do zero**. O orquestrador gerado pela skill `orquestrador-init` acabou de ler a sumarização F0, conhece o domínio, conhece a banca/ementa/contexto, e **propõe** o currículo a partir da literatura canônica. O aluno **valida ponto a ponto**, corrigindo, adicionando restrições, ajustando ao que ele sabe sobre si.

Isso é decisão compartilhada desde a fundação — alinhado com Knowles (adulto como coautor, experiência como recurso) e evita o anti-padrão "orquestrador-secretário" que transcreve o que o aluno dita sem trazer expertise.

### Fluxo de co-escrita

1. **Proposta do orquestrador:** a partir da sumarização F0 + perfil, propõe objetivos em Bloom, pré-requisitos esperados, recursos canônicos que ele conhece, estratégia de avaliação adequada ao tipo de motivação (concurso / faculdade / vida / curiosidade).
2. **Validação por seções com o aluno:** aluno lê cada seção e confirma, corrige, ou adiciona. Sem consentimento passivo — pedir discordância ativa.
3. **Ajuste iterativo:** orquestrador atualiza, aluno valida novamente. Gate de saída: aluno diz "é esse o contrato que eu assino".
4. **Commit do currículo** (se versionado).

---

## Artefatos produzidos

1. **`CURRICULUM.md`** (localização depende do perfil) — contrato pedagógico estável.
2. **Referência cruzada** com o RAOP (`perfil_aluno.md` aponta para `CURRICULUM.md`; `lista_lacunas.md` usa os pré-requisitos declarados aqui como base do rastreio).
3. **Estrutura de portfólio** (se versionado e se o perfil pede) — ex.: `portfolio/rascunhos/`, `portfolio/exercicios/`, `portfolio/producoes/`. Em P1, honra as 5 pastas existentes.
4. **Commit inicial** (se versionado) com mensagem canônica A+P.

---

## Fases do `/curso-init`

### 1. Identificação

Coletar da sumarização F0 (**não perguntar de novo** se já validado lá). Preencher:
- Nome do aluno (ou pseudônimo).
- Nome/tema do percurso.
- Propósito em 1 frase.
- Horizonte temporal.
- Orquestrador responsável (slug).

### 2. Proposta de objetivos em Bloom (pelo orquestrador)

Orquestrador propõe objetivos **em verbos da taxonomia de Bloom revisada**:

| Nível | Verbos típicos | Sinal de domínio |
|-------|----------------|-------------------|
| Lembrar | listar, identificar, definir | recupera sob demanda |
| Compreender | explicar, parafrasear, exemplificar | reformula em linguagem própria |
| Aplicar | usar, implementar, resolver | transfere para caso novo |
| Analisar | decompor, comparar, contrastar | identifica estrutura/relação |
| Avaliar | justificar, criticar, selecionar | emite juízo com critério |
| Criar | projetar, compor, formular | produz novidade coerente |

**Regra dura:** objetivo sem verbo de Bloom é sonho, não objetivo. "Aluno entenderá derivadas" não é objetivo; "aluno calculará derivada de polinômio e aplicará a problema de taxa de variação dado" é.

**Aluno valida:** cada objetivo é lido e confirmado/corrigido. Pode adicionar restrições ("não preciso chegar em criar") ou elevar alvo ("quero conseguir analisar também").

### 3. Mapa de pré-requisitos (proposto pelo orquestrador, validado pelo aluno)

**Esta fase é vinculante.** Sem mapa, a skill aborta. Ver "Rastreio de Pré-requisitos como Diretriz Obrigatória" abaixo.

O orquestrador, a partir do domínio, **propõe** os pré-requisitos típicos de cada objetivo que esteja acima de `lembrar`, com nível mínimo exigido e recurso canônico onde consolidar. O aluno declara o status inicial estimado de cada um; a sondagem formal acontece na **primeira sessão MECA (F3)**.

### 4. Recursos canônicos (orquestrador traz; aluno escolhe subconjunto)

Orquestrador apresenta a "biblioteca oficial" do domínio que ele conhece:
- **Texto principal:** 1 referência primária sugerida.
- **Textos complementares:** 2–3 sugestões.
- **Exercícios canônicos:** onde vir (lista, livro, banco de questões da banca).
- **Ferramentas:** ambientes, softwares, simuladores.
- **Analogias validadas:** analogias que o orquestrador conhece da literatura do domínio ou de prática didática estabelecida.

Aluno escolhe o que vai usar primariamente (pode ter Stewart na estante mas preferir 3Blue1Brown para intuição; orquestrador anota).

### 5. Estratégia de avaliação

Declarar explicitamente como se verifica domínio:

- **Avaliação formativa:** contínua em sessão, via Produção Concreta. Default.
- **Avaliação diagnóstica:** F4 do MECA. Sondagem inicial + antes de mudança de nível Bloom.
- **Avaliação somativa (se aplicável):** prova, certificação, entrega — data, formato, peso.
- **Critério de domínio por objetivo:** o que conta como "dominou?". Produção concreta esperada.

**Regra dura:** objetivo sem critério de domínio não é objetivo, é intenção.

### 6. Estratégias declaradas (consulta obrigatória à Base de Evidências)

**Nova seção obrigatória** (v2026.04.1). O orquestrador declara quais **estratégias de aprendizagem** serão primárias neste percurso, consultando `/mnt/skills/user/orquestrador-init/references/evidencias-aprendizagem.md`.

Formato: lista de 3–5 estratégias da **Lista Verde** (etiquetadas `[E1]` ou `[E2]`) com operacionalização concreta neste percurso.

**Exemplo para um aluno P2 — concurso de título em endocrinologia:**

```markdown
## Estratégias declaradas

- **Retrieval practice `[E1]`** (Roediger & Karpicke 2006; Adesope et al. 2017):
  auto-explicação reversa ao final de cada F6 + simulados cronometrados no
  formato exato da banca SBEM a partir do mês -3.

- **Distributed practice `[E1]`** (Cepeda et al. 2006; Dunlosky et al. 2013):
  revisão espaçada 1d/7d/21d/60d das competências via /raop revisao-espacada,
  ancorada na data da prova.

- **Interleaving `[E1]`** (Rohrer 2012; Brunmair & Richter 2019): alternância
  entre tópicos da ementa a partir do mês -2, simulando o formato misto da prova.

- **Worked examples `[E1]`** (Sweller et al. 1998; Renkl 2014): para tópicos
  novos nos primeiros 2 meses, 2–3 exemplos comentados antes do primeiro
  problema independente, com fading explícito.

- **Feedback específico e oportuno `[E1]`** (Hattie & Timperley 2007): dentro
  do segmento de F6, não ao final da sessão; formato causal ("o passo X
  funcionou porque Y; o passo Z falhou porque W").
```

**Regra dura:** estratégia sem etiqueta [E1] ou [E2] **não entra como declarada**. Estratégia com respaldo exploratório pode ser usada, mas marca-se `[E3]` e aluno sabe do status. Nada `[E0]` entra.

### 7. Guardrails pedagógicos e invariantes

Seção do `CURRICULUM.md` que lista o que **não pode** mudar sem reenquadramento:

**Guardrails universais do MECA (sempre presentes):**
- Decisão compartilhada em F5 é condição; exposição unilateral prolongada viola contrato.
- Produção Concreta é obrigatória para marcar domínio.
- Nunca avançar de nível Bloom sem evidência do nível anterior.
- Nunca usar tom sarcástico; nunca comparar com outros alunos.
- Sinal de shutdown → `/meca-aval intervencao-focal` imediato; jamais insistir no conteúdo.
- Aluno sempre sabe onde está na escada Bloom e qual o critério atual.
- Estratégias declaradas têm respaldo `[E1]` ou `[E2]`; `[E0]` é recusada mesmo a pedido do aluno.

**Guardrails específicos do percurso** (negociados entre aluno e orquestrador):
- Ritmo combinado (ex.: sessões ≤ 45min se P4 profissional; ≤ 60min em geral).
- Acomodações para NEE com laudo (se aplicável).
- Limites do escopo (o que o percurso cobre e NÃO cobre).

### 8. Co-escrita final e commit

- Orquestrador compõe o `CURRICULUM.md` completo.
- Aluno lê inteiro e assina (via confirmação explícita).
- Se versionado: commit inicial com A+P via `commit-licao` — mas atenção: `commit-licao` exige SOAP; o commit inicial **não tem SOAP pedagógico**, então a mensagem segue o formato adaptado:

```
chore: curso-init — contrato pedagógico estabelecido

A: Percurso sem contrato pedagógico formal — risco de cobertura sem aprendizado verificável
P: CURRICULUM.md (objetivos Bloom + pré-requisitos + estratégias declaradas [E1/E2] + guardrails)

Refs: CURRICULUM.md
```

(Sem `Co-Authored-By`. Nunca.)

---

## Rastreio de Pré-requisitos como Diretriz Obrigatória

### Princípio

**O pré-requisito ausente é a prescrição para efeito colateral garantido.** Ensinar `aplicar` sobre `compreender` ausente produz procedural sem semântica — aluno decora, passa na prova, esquece em 30 dias, débito cognitivo acumula. Equivalente pedagógico de prescrever dose adulta para criança sem ajuste.

### Regras vinculantes

1. **Todo percurso declara mapa de pré-requisitos** — pelo menos um por objetivo acima de `lembrar` em Bloom.
2. **Mapa é parte do `CURRICULUM.md`** e consultado em cada F1 do MECA.
3. **Validação de pré-requisitos na primeira sessão MECA (F3) é obrigatória.** Não presumir que aluno tem o que diz ter — sondar com Produção Concreta. Falha → pré-requisito vira `#[A]` no RAOP antes do objetivo declarado começar.
4. **Saltar pré-requisito é operação deliberada**, registrada como dívida pedagógica no `perfil_aluno.md` com expectativa de retorno.
5. **Em F6, ao introduzir conceito novo, verificar pré-requisito imediato** mesmo que já verificado antes.
6. **Auditoria ao final de cada nível Bloom concluído** — revisitar o mapa.

### Exceções

Percursos ultra-simples (pergunta pontual, esclarecimento isolado) podem prescindir de mapa formal — mas **não entram no workflow MECA/RAOP**. Sem `CURRICULUM.md`, sem mapa, não é percurso formal; é consulta.

### Sinalização em CURRICULUM.md

```markdown
## Pré-requisitos (mapa)
- **Validação:** sondagem na primeira sessão MECA — F3
- **Atualização:** revisão ao final de cada objetivo concluído
- **Dívidas assumidas:** [ex.: aluno opta por avançar sem consolidar X; retomar em 3 sessões]
```

---

## Template do `CURRICULUM.md`

```markdown
# Currículo — [Nome do percurso]
- **Aluno:** [nome] — **Orquestrador:** [slug] — **Perfil:** [P1..P6]
- **Atualizado:** [data]

## Identificação
- **Propósito:** [1 frase]
- **Horizonte:** [prova/projeto/autonomia — quando]
- **Stakeholders:** [quem mais é afetado]

## Objetivos (Bloom revisado)
| # | Objetivo | Nível Bloom | Critério de domínio |
|---|----------|-------------|---------------------|
| O1 | [verbo + conteúdo] | aplicar | [produção concreta esperada, mensurável] |
| O2 | ... | ... | ... |

## Pré-requisitos (mapa)
| Objetivo | Pré-requisito | Nível mínimo | Recurso canônico | Status inicial |
|----------|---------------|--------------|------------------|----------------|
| O1 | [...] | aplicar | [ref.] | sondar |
- **Validação:** sondagem em F3 da sessão 1
- **Atualização:** revisão ao final de cada objetivo

## Recursos canônicos
- **Texto principal:** [ref.]
- **Textos complementares:** [ref.]
- **Exercícios canônicos:** [onde]
- **Ferramentas:** [quais]
- **Analogias validadas:** [quais — responsabilidade do orquestrador trazer]

## Estratégia de avaliação
- **Formativa:** produção concreta em cada F6; SOAP pedagógico registra
- **Diagnóstica:** F4 do MECA; sondagem antes de mudança de nível Bloom
- **Somativa (externa):** [data / formato / peso / escopo, se aplicável]
- **Critério de avanço entre objetivos:** domínio do critério declarado

## Estratégias declaradas (com respaldo evidencial)
- [estratégia] `[E1|E2]` (referência): operacionalização concreta
- ...

## Guardrails (universais MECA)
- Decisão compartilhada em F5 é condição
- Produção Concreta obrigatória para marcar domínio
- Nunca avançar de Bloom sem evidência do nível anterior
- Nunca sarcasmo; nunca comparação com outros alunos
- Shutdown → /meca-aval intervencao-focal imediato
- Aluno sempre sabe onde está na escada Bloom
- Estratégias `[E0]` recusadas; folk-pedagogy mediada via /meca-aval confronto-folk

## Guardrails (específicos deste percurso)
- Ritmo: [combinado]
- Acomodações NEE: [se aplicável]
- Escopo: faz [X]; NÃO faz [Y]

## Integração com ambiente (se perfil identificado)
- **Perfil:** [P1..P6]
- **Raiz do RAOP:** [path, ex.: 01_Teoria/raop/ em P1]
- **Fusão com CLAUDE.md local:** [sim/não; se sim, este CURRICULUM.md é seção daquele]
- **Fonte de horizonte externa:** [ex.: 00_Admin/Radar.md em P1]
- **Skills locais a reusar:** [ex.: socrates-programacao em P1 de programação]

## Histórico de mudanças
- [data — mudança — motivo] (preenchido por /curso-init --refresh)

## Dívidas pedagógicas assumidas
- [item — data — retomar em]
```

---

## Regras de operação

1. **Sem `CURRICULUM.md`, não há MECA.** F1 do MECA tem gatilho bloqueante.
2. **Sem orquestrador ativo, `curso-init` recusa começar** — devolve para F0 do MECA.
3. **`curso-init` é co-escrito pelo orquestrador.** Não é entrevista com aluno; é proposta do orquestrador validada pelo aluno.
4. **Sem mapa de pré-requisitos, não há `CURRICULUM.md` válido.**
5. **Objetivos sem verbo de Bloom não são objetivos.** Aborta.
6. **Objetivos sem critério de domínio não são objetivos.** Aborta.
7. **Estratégias declaradas têm etiqueta `[E1]` ou `[E2]`.** `[E3]` aceito com visibilidade. `[E0]` nunca.
8. **Agnóstico a topologia.** Detecta perfil, encaixa-se; não impõe.
9. **`--refresh` não apaga.** Edita in place, registra em "Histórico de mudanças".
10. **Guardrails universais MECA são sempre presentes**; específicos são negociados.
11. **Esta skill não ensina conteúdo.** Contrato e setup. Ensino é MECA F6.
12. **Autoria (Iago Leal) preservada.** Invariante.
13. **Selo íntegro** é pré-condição de execução.

---

## Uso com `/curso-init`

- `/curso-init` — inicia as fases. Requer orquestrador ativo (senão devolve para F0 MECA). Se `CURRICULUM.md` já existe, aborta e sugere `--refresh`.
- `/curso-init --refresh` — re-executa fases 2–7 sobre o existente. Útil em troca de objetivo, elevação de Bloom, adição de guardrail.
- `/curso-init --check` — valida: todos objetivos com verbo Bloom? todos com critério? mapa cobre objetivos acima de lembrar? estratégias declaradas com [E1/E2]? selo íntegro?
- `/curso-init status` — mostra objetivos, Bloom alvo, próximo marco, perfil de integração, última atualização.

---

## Integração com outras skills

| Skill | Integração |
|-------|------------|
| `meca` | Gatilho bloqueante em F1; guardrails verificados em F5. Em F0 bootstrap, é invocado após `orquestrador-init`. |
| `orquestrador-init` | Co-escreve o `CURRICULUM.md`. `curso-init` recusa operar sem orquestrador ativo. |
| `raop` | `perfil_aluno.md` aponta para `CURRICULUM.md`. `lista_lacunas.md` usa pré-requisitos declarados aqui. |
| `meca-aval` | Guardrails afetivos rastreados em `raop/afetivo.md`; auditoria mensal verifica aderência. |
| `commit-licao` | Commit inicial segue A+P. Commits subsequentes sem `Co-Authored-By`. |
