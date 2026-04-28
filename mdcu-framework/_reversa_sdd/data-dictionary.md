# Dicionário de dados — mdcu-framework

> Gerado pelo **Reversa Archaeologist** em 2026-04-27
> Os "dados" deste framework são **artefatos em disco** que as skills produzem/consomem. Cada artefato funciona como uma "tabela" com schema prescrito em prosa.

---

## Inventário de artefatos

| # | Artefato | Owner | Lifecycle | Local típico |
|---|---|---|---|---|
| 1 | `_mdcu.md` | mdcu | transitório (sessão) | raiz do projeto-cliente |
| 2 | `rsop/dados_base.md` | rsop | estrutural | `rsop/` |
| 3 | `rsop/lista_problemas.md` | rsop | longitudinal (ativo) | `rsop/` (injetado em CLAUDE.md) |
| 4 | `rsop/passivos.md` | rsop | longitudinal (morto) | `rsop/` (sob demanda) |
| 5 | `rsop/seguranca.md` | mdcu-seg | trimestral | `rsop/` |
| 6 | `rsop/soap/YYYY-MM-DD_<contexto>.md` | rsop | permanente | `rsop/soap/` |
| 7 | `rsop/soap/YYYY-MM-DD_incidente-<ref>.md` | mdcu-seg (formato estendido) | permanente | `rsop/soap/` |
| 8 | `ARCHITECTURE.md` | project-init | estrutural | raiz do projeto-cliente |
| 9 | mensagem de commit (commit-soap) | commit-soap | permanente | git history |

---

## Artefato 1 — `_mdcu.md` (transitório)

**Owner:** mdcu | **Lifecycle:** criado em `/mdcu`, deletado pós-SOAP em F6 fechamento.

**Schema (mdcu/SKILL.md:58-77):**

| Campo | Tipo | Obrigatório | Descrição | Constraints |
|---|---|---|---|---|
| `# Sessão [data] — [projeto/tema]` | header L1 | sim | identificação da sessão | data ISO YYYY-MM-DD |
| `Tentativas de Reenquadramento` | counter | sim | controle do disjuntor F6 | inicializa `0/2`; incrementa em F6 reenquadramento; max `2/2` |
| `## F1 Preparação` | seção | sim | notas livres + check de `ARCHITECTURE.md` | — |
| `## F2 Escuta → S:` | seção+campo | sim | bullets telegráficos | sub-slots: Demandas / Queixas / Notas (SIFE) |
| `## F3 Exploração → O:` | seção+campo | sim | bullets de fatos observados | fonte explícita quando útil |
| `## F4 Avaliação` | seção | sim | hipótese + pró/contra | hipótese 1 linha |
| `## F5 Plano` | seção | sim | alternativas + decisão | mín 2 alternativas |
| `## F6 Execução` | seção | sim | divergências + reflexão rascunho | reflexão final = 1 linha → R do SOAP |

**Regras de escrita:**
- F2/F3 escrevem **durante a fase**, não retroativamente.
- F6 **relê o arquivo inteiro** antes de executar e antes de fechar.

---

## Artefato 2 — `rsop/dados_base.md` (estrutural)

**Owner:** rsop | **Lifecycle:** atualizado em mudança estrutural; não é diário.

**Schema (rsop/SKILL.md:42-62):**

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `Projeto` | string | sim | nome do projeto |
| `Atualizado` | date | sim | última revisão |
| `## Identificação` | seção | sim | Propósito (1 frase), Responsáveis, Stakeholders |
| `## Stack` | seção | sim | Linguagens/frameworks, Infra, Repositório |
| `## Dívidas conhecidas` | lista | opcional | itens — omitir se vazia |

**Regra:** "se um campo não tem conteúdo relevante, omita. Template é teto, não piso." (rsop/SKILL.md:64)

---

## Artefato 3 — `rsop/lista_problemas.md` (ATIVOS)

**Owner:** rsop | **Lifecycle:** vivo; injetado em `CLAUDE.md` do projeto.

**Schema (rsop/SKILL.md:84-92):**

| Coluna | Tipo | Obrigatório | Constraints |
|---|---|---|---|
| `#` | int | sim | identificador estável; nunca reciclado entre ativos e passivos |
| `Problema` | string | sim | **prefixo de severidade obrigatório**: `[A]`, `[M]`, ou `[B]` |
| `Desde` | date | sim | data de abertura |
| `Últ. SOAP` | date | sim | data do último SOAP que tocou o problema |

**Constraints especiais:**
- **Sem coluna `Notas`** (a evolução vive nos SOAPs referenciados).
- **Sem seção `## Passivos`** (passivos vivem em `passivos.md`).
- **Apenas problemas ATIVOS** entram aqui.
- **Exceção segurança:** vulnerabilidade entra mesmo se corrigida no mesmo dia (severidade mínima `[M]`).

**Enum de severidade:**
| Código | Significado |
|---|---|
| `[A]` | Alta — crítico, impacto amplo, ou explorável em produção (segurança) |
| `[M]` | Média — impacto significativo, contornável |
| `[B]` | Baixa — incômodo, baixo impacto |

---

## Artefato 4 — `rsop/passivos.md` (ARQUIVO MORTO)

**Owner:** rsop | **Lifecycle:** estático; **não injetado no system prompt por padrão**.

**Schema (rsop/SKILL.md:111-120):**

| Coluna | Tipo | Obrigatório | Constraints |
|---|---|---|---|
| `#` | int | sim | mesmo `#` que tinha em `lista_problemas.md` |
| `Problema` | string | sim | prefixo `[A]/[M]/[B]` mantido |
| `Ativo em` | date range | sim | formato `YYYY-MM → YYYY-MM` |
| `Fechado por` | string | sim | descrição da resolução (ex: "refactor webhook v2") |
| `Fechado em` | date | sim | YYYY-MM-DD |
| `Reativável?` | enum | sim | `não` / `sim — vigiar recorrência` / `sim — [motivo]` |

**Constraint de regressão:**
Se reaberto, recebe nota `reaberto em [data] — ver SOAP [ref]` E o `#` vai de volta para `lista_problemas.md`.

**Constraint de consulta:**
A IA só lê `passivos.md` em DOIS casos: (a) suspeita de regressão; (b) pedido explícito do usuário.

---

## Artefato 5 — `rsop/seguranca.md` (auditoria)

**Owner:** mdcu-seg | **Lifecycle:** revisão obrigatória a cada **90 dias**.

**Schema (mdcu-seg/SKILL.md:160-200):**

### Cabeçalho
| Campo | Tipo | Obrigatório |
|---|---|---|
| `Projeto` | string | sim |
| `Última revisão` | date | sim |
| `Próxima revisão` | date | sim |

### `## Classificação de dados`
| Coluna | Tipo |
|---|---|
| Categoria | enum: `Restrito` / `Confidencial` / `Interno` / `Público` |
| O que é | string |
| Onde mora | string |
| Quem acessa | string |

### `## Regime de auditoria` — campos fixos
- `SAST`, `DAST`, `Dependency scan`, `Secret scan`, `Pentest`, `Code review de segurança`

### `## Gestão de segredos`
- `Onde moram`, `Rotação` (por tipo), `Acesso`

### `## Conformidade`
- `Regulações aplicáveis` (LGPD, HIPAA, PCI-DSS, ISO 27001, ...)
- `DPO/responsável`, `Base legal de tratamento`, `Política de retenção`

### `## Histórico de incidentes (últimos 12 meses)`
| Coluna | Tipo |
|---|---|
| Data | YYYY-MM-DD |
| Severidade | enum L1/L2/L3/L4 |
| Resumo | string |
| Postmortem | ref SOAP |

### `## Vulnerabilidades ativas` — espelho da `lista_problemas.md` filtrada por segurança.

---

## Artefato 6 — `rsop/soap/YYYY-MM-DD_<contexto>.md` (SOAP padrão)

**Owner:** rsop | **Lifecycle:** permanente. Único registro autorizado da sessão.

**Naming:** `YYYY-MM-DD_<contexto>.md` (kebab-case ou snake_case no contexto — exemplos no repo usam ambos).

**Schema (rsop/SKILL.md:177-208):**

| Campo | Tipo | Obrigatório | Constraints |
|---|---|---|---|
| `# SOAP YYYY-MM-DD — [contexto]` | header L1 | sim | data ISO + contexto curto |
| `Problemas: #N, #M` | metadata | sim | refs a `#` em lista_problemas |
| `## S` | seção | sim | três sub-slots |
| `### Demandas` (markdown bold) | bullets | sim | 1 tópico = 1 demanda |
| `### Queixas` | bullets | sim | dado diagnóstico, mesmo sem expectativa |
| `### Notas` | bullets | opcional | SIFE / padrão de demanda / demanda oculta — omitir se vazia |
| `## O` | bullets | sim | telegráfico, sem sub-slots, fonte explícita quando útil |
| `## A` | numbered list | sim | **MAX 5 PALAVRAS POR ITEM**; cada item refs um `#` |
| `## P` | numbered list | sim | **1:1 com A**; uma linha cada |
| `## R` | string | opcional | **UMA LINHA** ou omitir |

**Regras de escrita (rsop/SKILL.md:136-145):**
- Ordem direta: sujeito-verbo-complemento.
- Sem artigos/conectivos desnecessários quando o sentido se preserva.
- Um tópico = uma informação.
- Se retirar a linha e nada se perder, a linha não existia.
- Não inventar — só observado/relatado/medido.
- Distinguir fonte (usuário/log/terceiro) quando relevante.

---

## Artefato 7 — `rsop/soap/YYYY-MM-DD_incidente-<ref>.md` (SOAP de incidente)

**Owner:** mdcu-seg | **Lifecycle:** permanente. Estende o schema do SOAP padrão.

**Schema adicional (mdcu-seg/SKILL.md:102-145):**

| Campo extra | Tipo | Obrigatório |
|---|---|---|
| `Tipo: incidente (F0)` | metadata | sim |
| `Severidade: L1\|L2\|L3\|L4` | enum | sim |
| `## Etapas F0` | numbered list 1–6 | sim |

**Etapas F0 com timestamps:**
1. **Identificação** (HH:MM): alerta/origem
2. **Contenção curta** (HH:MM): ação imediata
3. **Contenção média** (HH:MM): patch temporário, rotação
4. **Erradicação** (HH:MM): patch definitivo
5. **Recuperação** (HH:MM): serviço restaurado + monitoramento
6. **Postmortem** (data seguinte): blameless, ações estruturais

**Enum de severidade de incidente:**
| Código | Significado |
|---|---|
| `L1` | Baixa — contida, sem exposição confirmada |
| `L2` | Média — exposição parcial |
| `L3` | Alta — exposição confirmada |
| `L4` | Crítica — ativa em produção |

**⚠️ Não confundir** com severidade de problema RSOP (`[A]/[M]/[B]`). Escalas distintas, domínios distintos.

---

## Artefato 8 — `ARCHITECTURE.md` (contrato técnico)

**Owner:** project-init | **Lifecycle:** estrutural; alterado apenas via `/project-init --refresh`.

**Schema (project-init/SKILL.md:189-245):**

### Cabeçalho
- `# Architecture — [Nome]`
- `Atualizado: YYYY-MM-DD`

### `## Identificação`
- `Propósito` (1 frase) | `Responsáveis` | `Stakeholders`

### `## Stack`
- `Linguagem` | `Runtime` | `Framework` | `Banco de dados` | `Infra`

### `## Dependências`
| Campo | Constraint |
|---|---|
| `Gerenciador` | enum: npm/yarn/pnpm/Poetry/uv/Cargo/Go modules/Bundler/Composer/Mix/NuGet |
| `Manifesto` | path do manifesto |
| `Lock file` | path do lock — **rótulo `COMMITADO` obrigatório** |
| `Política de versão` | string (ex: "^ no manifesto, exata no lock") |
| `Auditoria` | ferramenta + frequência |
| `Upgrades` | manual / Dependabot/Renovate com review humano |

### `## Estrutura de diretórios`
- `src/` | `tests/` | `rsop/` | `docs/` (e quaisquer adicionais idiomáticas)

### `## Convenções`
- `Lint` | `Format` | `Naming` | `Branches` | `Commits`

### `## Comandos principais`
- `install` | `dev` | `test` | `build` | `lint` | `format` | (`migrate` | `seed` se DB)

### `## Guardrails (invariantes)`
- Lista de invariantes não-negociáveis (sem mudar sem `--refresh`).

### `## Escopo`
- `Faz:` / `NÃO faz:`

### `## ADRs relacionados`
- Links.

---

## Artefato 9 — Mensagem de commit (commit-soap)

**Owner:** commit-soap | **Lifecycle:** permanente em git history.

**Formato canônico (commit-soap/SKILL.md:42-50):**
```
A: [síntese da Avaliação — 1ª linha máx 72 chars]
P: [síntese do Plano]

Refs: rsop/soap/YYYY-MM-DD_contexto.md
```

**Constraints:**
- 1ª linha (A): **≤ 72 caracteres** (compatibilidade `git log --oneline`).
- A: 1–3 frases. P: 1–3 frases.
- Sem tipo técnico obrigatório (Conventional Commits opcional).
- Múltiplos problemas → repetir `A:` e `P:` por `#`.
- **Trailer `Refs:`** apontando para path relativo do SOAP completo.
- ⚠️ **NUNCA incluir trailer `Co-Authored-By` ou atribuição de coautoria** — regra global do usuário (CLAUDE.md global, ver decisions.md).

---

## Enums consolidados

### Severidade de problema RSOP
| Valor | Domínio |
|---|---|
| `[A]` | Alta |
| `[M]` | Média |
| `[B]` | Baixa |

### Severidade de incidente (mdcu-seg)
| Valor | Domínio |
|---|---|
| `L1` | Baixa, contida |
| `L2` | Média, parcial |
| `L3` | Alta, confirmada |
| `L4` | Crítica, ativa em produção |

### Categoria de dado (mdcu-seg)
| Valor | Domínio |
|---|---|
| `Restrito` | PHI/PII identificada |
| `Confidencial` | Credenciais, tokens, chaves |
| `Interno` | Métricas, logs |
| `Público` | Docs, landing |

### STRIDE (mdcu-seg)
`S` Spoofing | `T` Tampering | `R` Repudiation | `I` Information disclosure | `D` Denial of service | `E` Elevation of privilege

### Demanda (mdcu)
| Tipo | Descrição |
|---|---|
| `Demanda` | O que o usuário espera resolver |
| `Queixa` | O que reporta sem expectativa de solução |

### Padrão de demanda aparente (mdcu, F2)
`cartão de visita` | `exploratória` | `shopping` | `cure-me`

### SIFE (mdcu, F2)
`Sentimentos` | `Ideias sobre a causa` | `Funcionalidade afetada` | `Expectativas`

### Reversibilidade de passivo (rsop)
`não` | `sim — vigiar recorrência` (segurança) | `sim — [motivo específico]`

---

## Relacionamentos entre artefatos (≈ "ERD")

```
ARCHITECTURE.md ─── lido por ──→ _mdcu.md (F1, F5, F6)
                                       │
dados_base.md ─── lido por ────→ _mdcu.md (F1)
                                       │
lista_problemas.md ←── escrito por ── _mdcu.md (F4) e rsop (/rsop revisar)
                                       │
                                       │ (no fechamento F6)
                                       ↓
                              soap/YYYY-MM-DD_*.md ← lê _mdcu.md (S, O, A, P)
                                       │                  e referencia # de
                                       │                  lista_problemas.md
                                       ↓
                              commit-soap (mensagem)
                                       │
                              referencia caminho do SOAP em "Refs:"

passivos.md ←── /rsop revisar move # resolvidos de lista_problemas.md
                /rsop regressao consulta e reabre

seguranca.md ←── /mdcu-seg auditoria (trimestral)
              espelha vulnerabilidades ativas de lista_problemas.md
              indexa incidentes (refs SOAPs de incidente)

soap/YYYY-MM-DD_incidente-*.md ←── /mdcu-seg incidente (F0)
                                  estende schema do SOAP padrão
```

---

## Lacunas 🔴

1. Não há schema validável (JSON Schema, etc.) para nenhum dos artefatos. Validação é por inspeção humana ou pela aderência do agente às prescrições em prosa. **Sugestão para Writer/Architect:** propor schemas formais (ex: JSON Schema embutido em SKILL.md) como evolução futura.
2. Naming convention de `<contexto>` em `soap/YYYY-MM-DD_<contexto>.md`: **livre** — kebab-case, snake_case ou prosa, desde que sem espaços (constraint implícito de filesystem). 🟢 (Iago, 2026-04-27 — questions.md P5: "sem opinião") — scripts de busca devem usar `ls rsop/soap/ | grep -i <termo>` agnóstico a convenção.
3. Não há contrato sobre **idioma** dos artefatos. Os exemplos estão em pt-BR; o framework é descrito em pt-BR; mas nada impede uso em outro idioma. **Sugestão Writer:** declarar pt-BR como canônico ou marcar i18n como `out of scope`.
