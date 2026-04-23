---
name: skill-spec
description: >
  Cria, extrai, avalia e atualiza specs DETERMINÍSTICAS de skills — documentos
  reprodutíveis onde qualquer agente que execute a SPEC produz a mesma skill,
  sem ambiguidade. Funde o fluxo de entrevista do `sdd-spec`, os modos
  CRIAR/EXTRAIR/AVALIAR/UPGRADE do `software-architecture`, e a anatomia
  obrigatória de SKILL.md do `skill-creator`. Artefato único: `SPEC.md` no
  padrão do `medical-rag` (identidade → estrutura de arquivos → SKILL.md
  obrigatório → scripts com CLI/JSON → deps pinadas → padrões de implementação
  → critérios de aceite → o que NÃO faz). Use esta skill SEMPRE que o usuário
  quiser gerar uma spec determinística de skill, documentar uma skill existente
  em formato reprodutível, fazer engenharia reversa de skill, avaliar se uma
  spec é ambígua/incompleta, versionar atualização de skill, ou mencionar
  "spec de skill", "SPEC.md", "spec determinística", "reproduzir skill",
  "blueprint de skill". NÃO ative para specs de features de produto (use
  `sdd-spec`), nem para design de sistema (use `software-architecture`), nem
  para construir a skill em si a partir da SPEC (use `skill-creator` depois).
---

# skill-spec — Orquestrador de specs determinísticas de skills

## Visão Geral

```
Intenção do usuário
       │
       ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   CRIAR      │    │   EXTRAIR    │    │   AVALIAR    │    │   UPGRADE    │
│  entrevista  │    │  skill → SPEC│    │  SPEC → score│    │  SPEC v1→v2  │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │                   │
       └───────────────────┼───────────────────┼───────────────────┘
                           ▼
                    ┌─────────────┐
                    │  SPEC.md    │  (determinística, reprodutível)
                    └──────┬──────┘
                           │
                           ▼
                   scripts/spec_scorer.py
                   (Determinismo 30 / Reprodutibilidade 25 /
                    Completude 20 / Testabilidade 15 / Delimitação 10)
```

O artefato único entregue é `SPEC.md` no padrão `medical-rag/SPEC.md` (ver `references/spec_template.md`). Opcionalmente, um agente pode depois passar a SPEC para o `skill-creator` construir a skill concreta, ou para o `software-architecture` gerar `architecture.md` com Mermaid.

---

## 4 Modos

| Modo | Quando usar | Input | Output |
|------|-------------|-------|--------|
| **CRIAR** | Nova skill, partindo de intenção verbalizada | Entrevista 1-a-1 (ver `references/interview_protocol.md`) | `SPEC.md` |
| **EXTRAIR** | Documentar skill existente em formato reprodutível (engenharia reversa) | Diretório de skill (`SKILL.md` + scripts + refs) | `SPEC.md` |
| **AVALIAR** | Auditar SPEC pronta antes de delegar para `skill-creator` | `SPEC.md` existente | Score 0–100 + gaps |
| **UPGRADE** | Versionar mudança (nova deps, novo script, novo modo) | `SPEC.md` + descrição da mudança | `SPEC.md` atualizado com diff documentado |

Pergunte ao usuário em qual modo entrar se não estiver claro. Nunca assuma.

---

## Delegação para skills-irmãs

Esta skill é **orquestradora fina**. Delegue quando fizer sentido:

| Situação | Delegue para |
|----------|-------------|
| Usuário quer spec de **feature de produto** (não skill) | `sdd-spec` |
| Usuário quer **arquitetura de sistema** (não skill) | `software-architecture` |
| Usuário quer **diagrama Mermaid** do pipeline da skill | `software-architecture` modo EXTRAIR sobre a SPEC gerada |
| Usuário quer **construir a skill** a partir da SPEC | `skill-creator` |
| Usuário quer **benchmark de trigger rate** da skill pronta | `skill-creator` (scripts/run_eval.py) |

Nunca duplique o trabalho dessas skills. A `skill-spec` gera o blueprint; as outras consomem.

---

## Fluxo: Modo CRIAR

### Passo 1 — Entrevista (obrigatória, 1 pergunta por turno)

Execute o protocolo em `references/interview_protocol.md`. 7 perguntas, uma de cada vez. Não avance sem resposta. Se o usuário já passou contexto, pule perguntas cobertas mas confirme antes.

### Passo 2 — Preencher o template

Abra `references/spec_template.md` e preencha cada seção com as respostas da entrevista. Nunca deixe campo em branco — marque `N/A` explicitamente quando a seção não se aplica (ex: skill conversacional sem scripts).

### Passo 3 — Rodar scorer

```bash
python scripts/spec_scorer.py <caminho/SPEC.md> [--json]
```

Retorna score 0–100 + breakdown por dimensão + lista de gaps críticos.

### Passo 4 — Iterar até score ≥ 80

- Score **≥ 80** → pronta para entregar
- Score **60–79** → corrija gaps e re-avalie (sem nova entrevista)
- Score **< 60** → entrevista incompleta: volte ao Passo 1 nas perguntas em aberto

### Passo 5 — Entrega

Apresente ao usuário:
1. `SPEC.md` final
2. Relatório do scorer (score + breakdown)
3. Próximo passo sugerido: "Quer delegar para `skill-creator` construir a skill agora?"

---

## Fluxo: Modo EXTRAIR

Engenharia reversa de skill existente → SPEC.md determinística.

### Passo 1 — Inventário

Leia o diretório da skill inteira:
- `SKILL.md` (frontmatter + corpo)
- Todos os scripts (`scripts/*.py`, `*.sh`, etc.)
- Todas as referências (`references/*.md`)
- Assets, agents, templates

### Passo 2 — Preencher template

Preencha `references/spec_template.md` a partir do código observado. Para campos não observáveis (ex: "por que essa escolha de chunking?"), **pergunte ao usuário** antes de inferir. Inferências sem confirmação DEVEM ser marcadas `[INFERIDO — confirmar]`.

### Passo 3 — Detectar lacunas de determinismo

Execute o scorer. Gaps comuns em extração:
- Deps sem versão → perguntar se pinar
- Valores mágicos no código não documentados → elevar para seção "Configuração"
- Scripts sem CLI documentada → derivar `argparse` do código

### Passo 4 — Entrega

`SPEC.md` + lista de `[INFERIDO]` para o usuário confirmar ou corrigir.

---

## Fluxo: Modo AVALIAR

### Passo 1 — Rodar scorer

```bash
python scripts/spec_scorer.py <caminho/SPEC.md> --json
```

### Passo 2 — Interpretar

| Dimensão | Pontuação indica |
|----------|------------------|
| Determinismo (30) | Valores fixos, deps pinadas, zero ambiguidade |
| Reprodutibilidade (25) | Outro agente produziria a mesma skill |
| Completude (20) | Todas as 11 seções presentes e preenchidas |
| Testabilidade (15) | Critérios de aceite verificáveis (CLI + output) |
| Delimitação (10) | Seção "NÃO faz" explícita e útil |

### Passo 3 — Reportar

Para cada gap crítico, cite linha/seção da SPEC e sugira correção concreta. Não reescreva a SPEC no modo AVALIAR — só aponte.

---

## Fluxo: Modo UPGRADE

### Passo 1 — Carregar SPEC existente

### Passo 2 — Entrevistar sobre a mudança

- O que mudou? (novo script / nova deps / novo modo / correção)
- Por quê?
- Quebra compatibilidade com versão anterior?

### Passo 3 — Aplicar diff na SPEC

- Incrementar versão no frontmatter do SKILL.md que a SPEC prescreve
- Atualizar seção afetada
- **Adicionar entrada ao "Changelog" da SPEC** (seção 12, ver template)

### Passo 4 — Re-avaliar

Rodar scorer. Se quebrou algo (deps não pinada, CLI ambígua) → corrigir antes de entregar.

---

## Anatomia do SPEC.md

Ver `references/spec_template.md` para o template canônico. Resumo das 11 seções obrigatórias:

1. **Propósito** — 1 parágrafo, declaração de determinismo
2. **Identidade** — tabela (nome, diretório, propósito, domínio, privacidade)
3. **Estrutura de Arquivos** — árvore ASCII obrigatória
4. **SKILL.md — Conteúdo Obrigatório** — frontmatter literal + corpo obrigatório
5. **Scripts — Especificação Detalhada** — responsabilidades + CLI + output JSON (ou `N/A`)
6. **Dependências** — versões pinadas (ou `N/A`)
7. **Armazenamento de Dados** — diretórios + schemas de config (ou `N/A`)
8. **Padrões de Implementação** — self-bootstrap, JSON output, erros
9. **Fluxo Interativo** — perguntas + defaults (ou `N/A`)
10. **Critérios de Aceite** — checklist verificável
11. **O que NÃO faz** — delimitação explícita

Opcional:
12. **Changelog** — obrigatório a partir do primeiro UPGRADE

---

## Rubrica de Determinismo

Ver `references/determinism_rubric.md` para a rubrica completa com pesos, sinais de qualidade por dimensão, e red flags.

---

## Critério de "Pronta"

A SPEC está pronta para delegar ao `skill-creator` quando:

- [ ] Score do scorer ≥ 80
- [ ] Seção "O que NÃO faz" tem ao menos 3 itens específicos
- [ ] Todos os scripts (se houver) têm CLI documentada + exemplo de output JSON
- [ ] Todas as dependências têm versão fixa (`==`) ou explicitamente `latest` justificado
- [ ] Critérios de aceite têm pelo menos um checkbox por script
- [ ] Não há `[INFERIDO]` pendente sem confirmação do usuário

---

## O que esta skill NÃO faz

- NÃO constrói a skill (delega para `skill-creator`)
- NÃO gera specs de features de produto (delega para `sdd-spec`)
- NÃO desenha arquitetura de sistema (delega para `software-architecture`)
- NÃO executa os scripts prescritos — só os especifica
- NÃO valida compatibilidade semântica com skills existentes (responsabilidade do `skill-creator`)
