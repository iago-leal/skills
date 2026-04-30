# Partição de Governança — repo vs. GitHub

> Carregue para entender por que cada artefato vive onde vive.

## 1. Princípio-guia

**Vai pro filesystem do repo só o que precisa ser:**
1. Versionado com o código que o implementa, ou
2. Capaz de bloquear merge via CI.

**Vai pro GitHub o que é:**
1. Estado de execução mutável, ou
2. Comunicação entre humanos (comments, threads), ou
3. Cobertura nativa de search/labels/notifications.

Aplicar isso evita dois anti-padrões:
- **Tudo no GitHub (B-puro)**: ADR descolado do código; muda código sem mudar decisão; vendor lock-in
- **Tudo no filesystem (D-pesado)**: RACI vira documento morto; pós-mortem ninguém lê; status report fora da plataforma

## 2. Tabela canônica

| Artefato | Onde mora | Razão |
|---|---|---|
| **ADR** | `docs/adr/NNNN-titulo.md` (repo) | Imutável por design; casa com código; bloqueia merge via CI |
| **Contrato de prompt** | `prompts/NNNN-task.md` (repo) | Versionado com código que consome o LLM; eval roda em PR |
| **Eval offline (cases)** | `evals/<task>/cases.jsonl` (repo) | Roda em CI; bloqueia regressão |
| **Schema de API/dado** | `schemas/*.json` ou `proto/*` (repo) | Idem ADR — código depende disso |
| **Runbook operacional** | `docs/runbook/<sistema>.md` (repo) | Versionado com código que ele opera |
| **Política de retry/timeout** | `config/<sistema>.yaml` (repo) | Lida pelo código em runtime |
| **RACI por milestone** | Descrição do milestone (GitHub) | Mutável; vive enquanto milestone vive; expira no fechamento |
| **Pós-mortem** | Issue `incident`+`postmortem` fechada (GitHub) | Linka incidente original; search/labels nativos |
| **Decomposição de épico** | Issues atômicas + checklist no milestone (GitHub) | Estado de execução; mutável |
| **Status de release** | Milestone progress + issues fechadas (GitHub) | Visualização nativa |
| **Discussão de proposta** | Issue (preferencial) ou GitHub Discussions | Threading e participação |
| **Roadmap** | Projects v2 (GitHub) | Board nativo; integra issues/milestones |
| **Status report semanal** | NÃO criar (anti-padrão) | Briefing do `/cto` substitui — gerado dinâmico |
| **Wiki de conhecimento** | NÃO criar (anti-padrão) | Vira documentação morta. Use `docs/` no repo + ADRs |

## 3. Por que ADR no repo (e não em issue)

Um ADR em issue parece eficiente:
- Time inteiro vê
- Comentários inline na discussão
- Search nativo

Mas falha em 3 dimensões críticas:

### 3.1 Não bloqueia merge
Lint de CI não consegue ler issue eficientemente em PR. Resultado: PR que altera `src/auth/` consegue mergear sem atualizar ADR de auth — porque ninguém checa.

Com ADR em arquivo:

```yaml
# .github/workflows/adr-lint.yml
- name: Block PR if auth changed without ADR update
  run: |
    if git diff --name-only origin/main..HEAD | grep -q '^src/auth/' &&
       ! git diff --name-only origin/main..HEAD | grep -q '^docs/adr/.*auth.*'; then
      echo "PR altera src/auth/ sem atualizar ADR. Atualize docs/adr/ correspondente."
      exit 1
    fi
```

Esse hook é impossível em B-puro.

### 3.2 Issue editável != documento versionado
Issue body pode ser editado por qualquer mantenedor. Sem `git log` confiável de quem mudou o quê quando. ADR em arquivo tem `git blame` linha-a-linha.

### 3.3 Vendor lock-in
Sair do GitHub = perder histórico de decisão. ADR em arquivo viaja com o código para qualquer plataforma (GitLab, Forgejo, Bitbucket, mirror local).

## 4. Por que pós-morto em issue (e não em arquivo)

Inverso do anterior:

- Pós-morto referencia incidente original (issue) — link nativo, sem broken refs
- Discussão pós-incidente é parte do pós-morto — comments fazem sentido
- Pós-morto não bloqueia merge (já é histórico)
- Search por label `postmortem` é nativo
- Pós-morto não é versionado conforme código evolui — congela no momento

Forçar pós-morto em arquivo seria ritual sem ganho.

## 5. Exceção: pós-morto que vira ADR

Frequente: durante pós-morto, descobre-se decisão arquitetural que precisa virar guardrail. Nesse caso:

1. Pós-morto fica como issue (estado: o que aconteceu)
2. ADR novo é criado em `docs/adr/NNNN.md` (decisão preventiva)
3. Pós-morto referencia ADR: `## Ação Preventiva ─ ADR-NNNN`
4. ADR referencia pós-morto na seção `## Referências`

Não duplique conteúdo entre os dois — link.

## 6. Quando criar wiki?

Resposta curta: **não crie**.

Resposta longa: o anti-padrão clássico de wiki é virar dump de tudo que "alguém deveria saber" e ninguém ler. Em vez disso:

| Necessidade | Onde mora |
|---|---|
| "Como o sistema X funciona" | `docs/architecture/X.md` (repo) |
| "Como rodar testes" | `README.md` (repo) |
| "Como debugar problema Y" | `docs/runbook/Y.md` (repo) |
| "Por que escolhemos Z" | `docs/adr/NNNN-Z.md` (repo) |
| "Quem é responsável por W" | RACI de milestone (GitHub) ou `CODEOWNERS` (repo) |

Tudo versionado com código. Tudo grep-ável. Tudo com `git log`.

## 7. Cheat sheet de decisão

```
A informação muda com o código?
  └─ SIM → repo (ADR, prompt, schema, runbook)
  └─ NÃO → continua perguntando ↓

A informação é estado de execução?
  └─ SIM → GitHub (issue, milestone, project)
  └─ NÃO → continua ↓

A informação precisa ser discutida com humanos antes de virar verdade?
  └─ SIM → issue ou Discussion (GitHub)
  └─ NÃO → continua ↓

A informação é histórico fechado de evento passado?
  └─ SIM → issue fechada (GitHub) com label apropriada
  └─ NÃO → re-pergunte se precisa existir
```
