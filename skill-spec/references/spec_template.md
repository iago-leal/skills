# Template Determinístico de SPEC.md

Este é o template canônico que toda SPEC de skill gerada pela `skill-spec` DEVE seguir. É uma adaptação generalizada do padrão `medical-rag/SPEC.md`.

**Regras de preenchimento:**
- Nenhum campo fica em branco. Use `N/A` explicitamente quando a seção não se aplica.
- Valores de configuração, versões de dependência e caminhos DEVEM ser literais (não placeholders).
- Inferências sem confirmação do usuário DEVEM ser marcadas `[INFERIDO — confirmar]`.
- Tabelas são preferidas a prosa quando há múltiplos campos estruturados.

---

## Estrutura canônica (copie e preencha)

```markdown
# Spec: Skill `<nome>`

## Propósito

Esta é a especificação determinística e reproduzível da skill `<nome>`.
Qualquer agente que receba este documento e execute o Skill Creator DEVE produzir
a mesma skill, sem ambiguidade.

---

## 1. Identidade da Skill

| Campo | Valor |
|-------|-------|
| **Nome** | `<nome>` |
| **Diretório** | `<nome>/` (relativo ao diretório de skills do agente) |
| **Propósito** | <1–2 frases declarativas> |
| **Domínio** | <área de aplicação — ex: medicina, devops, escrita> |
| **Privacidade** | <local/cloud/híbrido + justificativa> |
| **Versão** | `1.0.0` |

---

## 2. Estrutura de Arquivos (Obrigatória)

```
<nome>/
├── SKILL.md
├── SPEC.md
├── scripts/          # omitir se N/A
│   └── <script>.py
├── references/       # omitir se N/A
│   └── <ref>.md
└── assets/           # omitir se N/A
    └── <asset>
```

---

## 3. SKILL.md — Conteúdo Obrigatório

### 3.1 Frontmatter YAML (literal)

```yaml
---
name: <nome>
description: >
  <descrição longa com gatilhos explícitos, palavras-chave, exemplos de quando
  ATIVAR e quando NÃO ATIVAR. Inclua delimitação vs skills vizinhas.>
---
```

### 3.2 Corpo do SKILL.md (seções obrigatórias na ordem)

Liste aqui as seções que o SKILL.md DEVE conter, em ordem. Para cada seção,
especifique conteúdo mínimo obrigatório. Exemplo:

#### Seção: Visão Geral
- <conteúdo obrigatório 1>
- <conteúdo obrigatório 2>

#### Seção: <outra>
- ...

---

## 4. Scripts — Especificação Detalhada

> Use `N/A` se a skill for conversacional sem scripts.

### 4.1 `scripts/<script>.py`

#### Responsabilidades
1. <responsabilidade 1>
2. <responsabilidade 2>

#### Padrão de Implementação
- <padrão obrigatório — ex: self-bootstrap estilo X>

#### CLI
```
python scripts/<script>.py [--flag <valor>] [--json]
```

#### Output JSON (`--json`)
```json
{
  "<campo>": "<tipo/exemplo>"
}
```

<repetir para cada script>

---

## 5. Dependências (Versões Fixas)

### 5.1 Dependências Python

| Pacote | Versão | Propósito |
|--------|--------|-----------|
| `<pacote>` | `==X.Y.Z` | <por que precisa> |

### 5.2 Dependências de Sistema

| Pacote | Instalação | Propósito |
|--------|------------|-----------|
| `<pacote>` | `<comando>` | <por que precisa> |

> Use `N/A` em subseções que não se aplicam.

---

## 6. Armazenamento de Dados

> Use `N/A` se a skill não persiste dados.

### 6.1 Diretório Base

```
~/.<skill>/
├── config.json
└── <outros>
```

### 6.2 `config.json` — Schema

```json
{
  "<campo>": "<tipo/exemplo>"
}
```

---

## 7. Padrões de Implementação Obrigatórios

### 7.1 Self-Bootstrap

<especifique o padrão exato — referencie skill existente ou inclua código>

### 7.2 Saída JSON

- Scripts com `--json` imprimem APENAS JSON válido em stdout
- Mensagens de progresso em stderr
- Usar `json.dumps(data, ensure_ascii=False, indent=2)`

### 7.3 Tratamento de Erros

| Condição | Exit code | Comportamento |
|----------|-----------|---------------|
| <condição> | <N> | <mensagem em stderr> |

---

## 8. Fluxo Interativo

> Use `N/A` se a skill não tem fluxo interativo.

Mock exato da primeira execução, com prompts literais e defaults.

```
============================================================
  <skill> — Configuração Inicial
============================================================

[1/N] <pergunta>:
  [1] <opção> (default)
  [2] <opção>

  Escolha [1]: _
```

---

## 9. Critérios de Aceite

A skill está PRONTA quando:

- [ ] `python scripts/<script>.py <args>` executa sem erro
- [ ] Output JSON valida contra schema da Seção 4.X
- [ ] <critério verificável 3>
- [ ] <critério verificável 4>

Cada critério DEVE ser executável e ter resultado binário (passa/falha).

---

## 10. O que esta Skill NÃO faz

- NÃO <atividade 1 fora de escopo>
- NÃO <atividade 2 fora de escopo>
- NÃO <atividade 3 — delegação para outra skill, ex: "use `outra-skill` para X">

Mínimo: 3 itens específicos. Genéricos ("NÃO faz nada ilegal") não contam.

---

## 11. Changelog

> Obrigatório a partir do primeiro UPGRADE.

| Versão | Data | Mudança |
|--------|------|---------|
| 1.0.0 | <ISO 8601> | Versão inicial |
```

---

## Guia de preenchimento por modo

### Modo CRIAR
Preencha na ordem 1→11. Se descobrir que não tem informação para uma seção, volte à entrevista — não invente.

### Modo EXTRAIR
Preencha na ordem 2→4→5→1→7→6→8→9→10→11. Começa pelo observável (estrutura, scripts, deps), termina pela intenção (propósito, privacidade, delimitação) que exige confirmação do usuário.

### Modo UPGRADE
Edite apenas as seções afetadas + obrigatoriamente a Seção 11 (Changelog). Bump de versão na Seção 1.

### Modo AVALIAR
Não edita. Apenas aponta seção por seção o que está faltando, usando o scorer.
