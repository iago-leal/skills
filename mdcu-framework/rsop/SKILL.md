---
name: rsop
description: Registro de Software Orientado por Problemas — prontuário longitudinal do software, inspirado no RMOP de Lawrence Weed (1968) e no modelo RCOP do e-SUS PEC. Formato enxuto, telegráfico, orientado por problema. ATIVE SEMPRE que o usuário digitar /rsop, pedir para documentar estado de um sistema, registrar um incidente ou interação significativa com um projeto, criar ou atualizar lista de problemas de um software, registrar SOAP de um projeto, ou mencionar "prontuário do software". Também ative quando a skill `mdcu` referenciar o RSOP como dependência. Ative proativamente quando o contexto indicar que o usuário está trabalhando em um projeto sem documentação longitudinal estruturada. NÃO ative para documentação pontual de código (docstrings, README simples) ou para registro de decisões isoladas (use ADRs diretamente).
---

# RSOP — Registro de Software Orientado por Problemas

## Fundamento

Prontuário do software. Formato telegráfico por princípio, não por economia. Prosa longa é ruído.

## Posição no workflow

```
MDCU (fases 1–6, notas na conversa)  →  Execução  →  _soap.md (temp)  →  commit-soap  →  deletar _soap.md
```

O git é o registro longitudinal. O CLAUDE.md carrega o estado vivo.

---

## Estrutura

O RSOP não cria diretório próprio. Dois artefatos apenas:

| Artefato | Onde | Ciclo de vida |
|----------|------|---------------|
| `## Lista de Problemas` | CLAUDE.md do projeto | Permanente — atualizada a cada sessão |
| `_soap.md` | raiz do projeto | Temporário — deletado após commit |

Nada mais é criado em disco.

---

## Lista de Problemas

### O que é

Índice vivo do projeto. Componente mais importante do RSOP. Fica numa seção dedicada do CLAUDE.md do projeto, sempre em contexto, sem necessidade de leitura explícita de arquivo.

### Regras

- **Problema:** tudo que preocupa engenheiro, usuário ou ambos. Bug, dívida, limitação, risco, conflito.
- **Nível de resolução:** descrição evolui (sintoma → hipótese → diagnóstico). O nome do problema carrega a precisão atual.
- **Severidade:** prefixo `[A]` alta, `[M]` média, `[B]` baixa.
- **Status:** `ativo` ou `passivo`. Passivo pode reativar.
- **Na dúvida, inclua.** Reclassificar é barato; reconstruir contexto perdido não.
- **Não entram:** bugs pontuais resolvidos no mesmo dia, ajustes cosméticos. Ficam só no SOAP.
- **Exceção — segurança:** vulnerabilidades **sempre** entram, mesmo se corrigidas no mesmo dia. Ao resolver, viram passivo com `reativável? sim`. Severidade mínima `[M]`; `[A]` se explorável em produção.

### Formato no CLAUDE.md

```markdown
## Lista de Problemas
**Projeto:** [nome] — **Revisão:** [data]

### Ativos
| # | Problema | Desde | Últ. SOAP |
|---|----------|-------|-----------|
| 1 | [A] N+1 queries listagem pedidos | 2026-03-10 | 2026-04-12 |
| 2 | [M] sem alerta em saturação redis | 2026-04-01 | 2026-04-15 |

### Passivos
| # | Problema | Ativo em | Fechado por | Reativável? |
|---|----------|----------|-------------|-------------|
| 1 | [B] timeout em webhook legacy | 2025-11 → 2026-02 | refactor webhook v2 | não |
```

Sem coluna "Notas". Evolução mora no commit referenciado.

---

## SOAP

### O que é

Destilado da sessão. Criado no fechamento do ciclo MDCU. Temporário: existe só até o commit ser gerado.

### Princípio

**S e O bem feitos são a fundação.** De escuta confusa sai plano confuso. A e P são consequência — não compensam S e O ruins.

### Regras de escrita

- Ordem direta: sujeito-verbo-complemento.
- Sem artigos e conectivos desnecessários.
- Um tópico = uma informação.
- Se retirar a linha e nada se perder, a linha não existia.
- Não inventar: só o que foi observado, relatado ou medido.

### S — Subjetivo

O que o usuário/stakeholder relata. **Três sub-slots telegráficos:**

- **Demandas:** o que espera resolver.
- **Queixas:** o que reporta sem expectativa de solução.
- **Notas:** opcional. SIFE quando relevante, demanda oculta suspeita. Omita se vazia.

### O — Objetivo

Tópicos telegráficos. O que foi observado, medido, verificado. Só o que foi efetivamente examinado.

### A — Avaliação

Lista numerada. **Máximo 5 palavras por item.** Cada item referencia um `#` da lista de problemas.

### P — Plano

Lista numerada. **1:1 com A.** Um plano por avaliação. Uma linha cada.

### R — Reflexão

**Uma linha.** Síntese do ciclo ou omissão — nunca parágrafo.

### Formato do `_soap.md`

```markdown
# SOAP [data] — [contexto]
- Problemas: #1, #2

## S
**Demandas**
- [demanda principal]

**Queixas**
- [queixa se houver]

**Notas**
- [SIFE ou demanda oculta, se relevante]

## O
- [observação 1]
- [observação 2]

## A
1. #1 [≤5 palavras]
2. #2 [≤5 palavras]

## P
1. [plano para #1]
2. [plano para #2]

## R
- [síntese em 1 linha, ou omitir]
```

O `_soap.md` deve estar no `.gitignore` do projeto (ou ser deletado antes do commit). O commit-soap lê A+P antes da deleção.

---

## Regras de operação

1. Toda sessão MDCU gera `_soap.md`.
2. `_soap.md` é deletado após o commit.
3. A lista de problemas é o índice — mantenha atualizada em F4 do MDCU.
4. S separa Demandas de Queixas. Sem isso, o plano vai na direção errada.
5. A e P são 1:1, por problema. Nunca prosa livre.
6. A ≤ 5 palavras. Se estourar, o problema está mal nomeado — refine o `#`.
7. R é uma linha. Síntese ou omissão.
8. Na dúvida, inclua na lista. Reclassificar é barato.

---

## Uso com `/rsop`

- `/rsop init` — adiciona seção `## Lista de Problemas` vazia ao CLAUDE.md do projeto.
- `/rsop lista` — exibe e/ou atualiza a lista de problemas no CLAUDE.md.
- `/rsop soap` — cria `_soap.md` na raiz do projeto com template preenchido.
- `/rsop revisar` — reclassifica, atualiza descrição, move ativo↔passivo na lista.
- `/rsop status` — resumo: data da última revisão, #ativos/#passivos, último commit-soap.
