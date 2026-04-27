# SDD — `commit-soap`

> Spec executável da skill `commit-soap` — gerador de mensagem de commit derivada do A+P do SOAP.
> Gerado pelo Reversa Writer em 2026-04-27.

## Visão Geral

Gerador de mensagem de commit que preserva o **contexto cognitivo** da sessão MDCU. 🟢 Lê o SOAP mais recente (A e P) e formata uma mensagem que pode ser auditada via `git log --grep`. Selo longitudinal — só usado em fechamento de sessão MDCU ou merge final de feature. 🟢

## Responsabilidades

- Localizar o SOAP mais recente em `rsop/soap/`. 🟢
- Extrair seções A e P. 🟢
- Sintetizar A e P seguindo regras de formatação (1ª linha ≤ 72 chars; 1-3 frases por bloco; `Refs:` no trailer). 🟢
- Múltiplos `#` → repetir `A:` e `P:` por problema. 🟢
- Exibir mensagem ao usuário antes de comitar. 🟢
- Abortar com mensagem fixa se não há SOAP da sessão (não inventar). 🟢
- Suportar `--dry-run` (gera sem comitar) e `--amend` (reescreve último commit). 🟢

## Interface

### Comandos públicos

| Comando | Efeito |
|---|---|
| `/commit-soap` | lê SOAP mais recente; gera mensagem; exibe; comita após confirmação 🟢 |
| `/commit-soap --dry-run` | gera mensagem sem comitar 🟢 |
| `/commit-soap --amend` | `git commit --amend` com nova mensagem do SOAP atualizado 🟢 |

### Saída

Mensagem de commit no formato canônico (não escreve em filesystem; escreve apenas em git history). 🟢

## Regras de Negócio

- **EXCLUSIVO para fechamento.** Sessão MDCU fechada (com SOAP) ou merge final de feature. (commit-soap/SKILL.md:21-32) 🟢
- **PROIBIDO para WIPs**, micro-commits, formatação, typos, merges intermediários — usar `git commit` padrão. (commit-soap/SKILL.md:25-31) 🟢
- **Sem SOAP da sessão → ABORTA com mensagem fixa.** Não inventa. (commit-soap/SKILL.md:112-114) 🟢
- **Linha A: máx 72 caracteres** na 1ª linha (compatibilidade `git log --oneline`). 🟢
- **Trailer `Refs:`** apontando para path relativo do SOAP. 🟢
- **Sem tipo técnico obrigatório** (Conventional Commits opcional como prefixo combinável). 🟢
- **Trailer `Co-Authored-By: Claude` PROIBIDO.** Regra global do usuário (CLAUDE.md global) + filtrado por hook `commit-msg` (ADR-006). 🟢
- Múltiplos problemas: repetir `A:` e `P:` por `#`. 🟢
- Habilita auditoria via `git log --grep="A:|P:|#N|Refs: rsop"` e `--invert-grep` para ruído. 🟢

## Fluxo Principal

1. Localiza SOAP mais recente em `rsop/soap/` (heurística: maior `YYYY-MM-DD` no nome de arquivo). 🟢
2. Verifica existência. Se ausente → emite mensagem fixa de orientação ("Registre /rsop soap antes — ou use git commit padrão se WIP") e ABORTA. Não inventa. 🟢
3. Extrai seções `## A` e `## P` do SOAP. 🟢
4. Identifica se há múltiplos `#` (lista numerada com refs). 🟢
5. Formata mensagem:
   - Caso single-`#`: `A: [síntese]` + `P: [síntese]` + linha em branco + `Refs: rsop/soap/YYYY-MM-DD_*.md`
   - Caso multi-`#`: repete `A: #N — [síntese]` e `P: #N — [síntese]` por problema, + `Refs:` 🟢
6. Garante que 1ª linha (linha A ou linha do tipo Conventional) ≤ 72 chars. 🟢
7. Exibe mensagem ao usuário para revisão. 🟢
8. Modo:
   - sem flag → aguarda confirmação → `git commit -m <mensagem>` 🟢
   - `--dry-run` → exibe mas não comita 🟢
   - `--amend` → `git commit --amend -m <mensagem>` 🟢

## Fluxos Alternativos

- **Usuário rejeita mensagem:** ABORTA sem comitar; oferece reformatação manual. 🟡 (não explícito; comportamento esperado)
- **SOAP existe mas A está vazio:** ABORTA com aviso "SOAP malformado — seção A vazia. Não há SOAP válido sem A." Nunca usa string vazia, nunca pergunta. 🟢 (Iago, 2026-04-27 — questions.md P3)
- **Conflito com pre-commit hook que falha:** comportamento herdado do `git commit` padrão; framework não interfere. 🟢
- **`--amend` em commit que não veio do commit-soap:** AVISA antes — "o último commit não tem formato A:/P:/Refs: — reescrever mesmo assim?" — exige confirmação explícita do usuário antes de prosseguir. 🟢 (Iago, 2026-04-27 — questions.md P4)

## Dependências

- **`rsop`** — lê SOAP mais recente em `rsop/soap/`. Sem RSOP, não há fonte. 🟢
- **`git`** — runtime. Sem git, não há destino. 🟢
- **NÃO escreve** em nenhum artefato do framework — apenas em git history. 🟢

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência | Confiança |
|---|---|---|---|
| Auditabilidade | Formato `A:/P:/#N/Refs:` permite filtros via `git log --grep` | commit-soap/SKILL.md:88-95 | 🟢 |
| Compatibilidade | 1ª linha ≤ 72 chars para `git log --oneline` | commit-soap/SKILL.md:56 | 🟢 |
| Integridade | Aborta sem inventar quando SOAP ausente | commit-soap/SKILL.md:112-114 | 🟢 |
| Conformidade | Sem trailer `Co-Authored-By` (filtrado por hook global e regra do usuário) | CLAUDE.md global + ADR-006 | 🟢 |
| Reversibilidade | Suporte a `--amend` quando SOAP é atualizado pós-commit | commit-soap/SKILL.md:101 | 🟢 |
| Idempotência | Não documentada — re-executar `/commit-soap` cria novo commit (não amenda automaticamente) | inferido | 🟡 |

## Critérios de Aceitação

```gherkin
Dado que existe rsop/soap/2026-04-27_feature-x.md com A: "1. #3 lentidão N+1" e P: "1. eager loading + index"
Quando o usuário digita /commit-soap
Então commit-soap exibe mensagem:
  """
  A: #3 lentidão N+1 confirmada — pioria desde último deploy
  P: #3 eager loading em OrderQuery + índice composto

  Refs: rsop/soap/2026-04-27_feature-x.md
  """
  E após confirmação executa git commit com essa mensagem

Dado que NÃO existe SOAP na sessão atual
Quando o usuário digita /commit-soap
Então commit-soap emite mensagem fixa:
  "Não há SOAP da sessão atual. Registre via /rsop soap antes de commitar
   — ou, se isto é apenas um WIP/checkpoint, use git commit padrão."
  E ABORTA sem inventar mensagem

Dado que existe SOAP que toca #3 e #7
Quando o usuário digita /commit-soap
Então commit-soap gera mensagem com:
  "A: #3 [...] / A: #7 [...] / P: #3 [...] / P: #7 [...] / Refs: ..."

Dado que o SOAP foi atualizado após commit
Quando o usuário digita /commit-soap --amend
Então commit-soap reescreve a mensagem do último commit
  E NÃO inclui trailer Co-Authored-By

Dado que existe SOAP mas a seção ## A está vazia
Quando o usuário digita /commit-soap
Então commit-soap ABORTA com mensagem "SOAP malformado — seção A vazia."
  E NÃO comita
  E orienta a corrigir o SOAP via /rsop soap antes de tentar de novo

Dado que o último commit é um WIP padrão (sem formato A:/P:/Refs:)
Quando o usuário digita /commit-soap --amend
Então commit-soap AVISA "o último commit não tem formato A:/P:/Refs: — reescrever mesmo assim?"
  E aguarda confirmação explícita
  E só prossegue se o usuário confirma
```

## Prioridade

| Requisito | MoSCoW | Justificativa |
|---|---|---|
| Formato A/P/Refs | Must | Define o "selo longitudinal" — diferencia de commit comum |
| Aborto sem SOAP | Must | Anti-invenção — preserva fidedignidade |
| 1ª linha ≤ 72 chars | Must | Compatibilidade `git log --oneline` |
| Sem `Co-Authored-By` | Must | Regra absoluta do usuário |
| `--dry-run` | Should | Conveniência para revisão |
| `--amend` | Should | Útil para SOAP iterado |
| Múltiplos `#` no formato | Should | Casos comuns em sessões de fechamento de feature |
| Exibição antes de comitar | Should | Permite revisão humana |
| Auto-detecção de WIP vs. fechamento | Won't | Decisão é do usuário (escolha de comando) |

## Rastreabilidade de Código

| Arquivo | Componente lógico | Cobertura |
|---|---|---|
| `commit-soap/SKILL.md:1-4` | frontmatter (com `author: Iago Leal`) | 🟢 |
| `commit-soap/SKILL.md:9-13` | Problema que resolve | 🟢 |
| `commit-soap/SKILL.md:15-17` | Dependência (`rsop`) | 🟢 |
| `commit-soap/SKILL.md:19-40` | Quando usar (gates EXCLUSIVO/PROIBIDO) | 🟢 |
| `commit-soap/SKILL.md:42-71` | Formato canônico + regras | 🟢 |
| `commit-soap/SKILL.md:73-84` | Múltiplos problemas | 🟢 |
| `commit-soap/SKILL.md:86-95` | Auditoria via `git log` | 🟢 |
| `commit-soap/SKILL.md:97-101` | Comandos `/commit-soap` | 🟢 |
| `commit-soap/SKILL.md:103-114` | Operação + tratamento de SOAP ausente | 🟢 |

---

## Refresh 2026-04-27 — delta v2.0.0

> Acionado pelo commit `1378d5e` — desacoplamento. Detalhes em `_reversa_sdd/code-analysis.md` apêndice.

### Mudanças estruturais 🟢

- **Frontmatter `version: "2.0.0"`** — bump MAJOR (escopo expandido: era "exclusivo fechamento MDCU", agora "selo longitudinal universal")
- **Description redefinida** — agora declara explicitamente os marcos cobertos: sessão MDCU, project-setup, refresh estrutural, marcos do adopter
- **Nova seção "Mudança em v2.0.0 (desacoplamento)"** — explica MAJOR bump e compatibilidade com v1.x
- **Nova seção "Fontes de A+P aceitas"** — 3 modos: SOAP default, `--from <path>`, `--inline`
- **Nova seção "Fluxo canônico (project-setup)"** — integração com nova skill
- **Nova seção "Fluxo canônico (refresh estrutural)"** — suporte a `--refresh`

### "API pública" expandida 🟢

| Comando | Parâmetros | Efeito | Pré-condição |
|---|---|---|---|
| `/commit-soap` | — | Default — lê último SOAP em `rsop/soap/` | SOAP existe (preservado da v1.x) |
| `/commit-soap --from <path>` | path | NOVO — lê A+P de arquivo arbitrário | path válido com formato A+P |
| `/commit-soap --inline` | A+P estruturado | NOVO — recebe A+P direto (usado por outras skills) | A+P bem formado |
| `/commit-soap --dry-run` | — | Gera mensagem sem commitar | — |
| `/commit-soap --amend` | — | Reescreve último commit-soap | último commit é commit-soap |

### Compatibilidade com v1.x 🟢

Comportamento default (sem argumento) **idêntico à v1.x**. Quebra de versão é semântica — escopo da skill mudou de "fechamento MDCU" para "selo longitudinal universal". Adopters que usam só `/commit-soap` sem argumento continuam funcionando.

### Critério de Aceitação NOVO (Gherkin)

```gherkin
Cenário: project-setup invoca commit-soap inline
  Dado que /project-setup terminou de materializar contrato técnico
  E que A+P inicial foi pré-formatado pelo project-setup
  Quando /commit-soap --inline é invocado com A+P estruturado
  Então a mensagem de commit é gerada no formato A:/P:/Refs:
  E o commit é executado com referência a ARCHITECTURE.md
  E o commit aparece em git log --grep="A:" como marco longitudinal

Cenário: /project-init --refresh sela via commit-soap inline
  Dado que /project-init --refresh modificou ARCHITECTURE.md (mudança de stack)
  E que /project-setup --refresh aplicou as mudanças no manifesto e lock file
  Quando o ciclo de refresh termina
  Então /commit-soap --inline é invocado com A+P descrevendo a mudança
  E o commit aparece em git log --grep="Refs: ARCHITECTURE.md" como marco arquitetural
```

### Padrão P-9 operacionalizado 🟢

A v2.0.0 é a operacionalização efetiva de P-9 (acompanhamento longitudinal transversal — `framework/principles.md`). Antes da v2.0.0, P-9 era princípio canônico mas não tinha ferramenta universal para selar marcos não-MDCU. Agora qualquer skill ou fluxo que produza A+P estruturado pode invocar `--inline` e gerar selo longitudinal coerente.

### Lacuna remanescente

- **Adoption de `--from`/`--inline` por outras skills:** apenas `project-setup` (v0.1.0) usa `--inline` hoje. Outros candidatos (ex: skills futuras de release-tag, feature-merge auditável) ficam para release-train v2026.06+.
