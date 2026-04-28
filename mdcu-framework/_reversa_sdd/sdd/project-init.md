# SDD — `project-init`

> Spec executável da skill `project-init` — inicialização de contrato técnico.
> Gerado pelo Reversa Writer em 2026-04-27.

## Visão Geral

Inicializa o **contrato técnico** de um projeto-cliente: produz `ARCHITECTURE.md` + manifesto + lock file determinístico + commit inicial canônico. 🟢 Pré-requisito **bloqueante** do MDCU (gate F1→F2). Re-executável como `--refresh` em mudança estrutural; auditável como `--check`. 🟢

## Responsabilidades

- Conduzir o usuário pelas **7 fases** de inicialização: Identificação, Stack, Gerenciador+Lock, Estrutura, Comandos, Guardrails, Geração+Commit. 🟢
- Aplicar a **tabela canônica stack→gerenciador→lock** (12 stacks) ou pesquisar+propor para stacks novas. 🟢
- Aplicar **8 regras vinculantes** de Gestão Determinística de Dependências (DDD). 🟢
- Gerar `ARCHITECTURE.md` segundo template fixo (9 seções). 🟢
- Validar projeto existente via `--check` (4 pontos: existe? lock? bate? guardrails?). 🟢
- Atualizar contrato existente via `--refresh` (re-executa fases 2–6 in place). 🟢

## Interface

### Comandos públicos

| Comando | Pré-condição | Efeito |
|---|---|---|
| `/project-init` | `ARCHITECTURE.md` ausente | 7 fases sequenciais → cria `ARCHITECTURE.md` + manifesto + lock + commit inicial 🟢 |
| `/project-init --refresh` | `ARCHITECTURE.md` presente; mudança estrutural | re-executa fases 2-6 sobre `ARCHITECTURE.md` existente 🟢 |
| `/project-init --check` | nenhuma | valida 4 pontos; retorna relatório telegráfico 🟢 |
| `/project-init status` | nenhuma | resumo: stack, gerenciador, lock presente, última atualização 🟢 |

### Artefatos produzidos

- `ARCHITECTURE.md` (raiz do projeto-cliente) 🟢
- Manifesto da stack escolhida (ex: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`) 🟢
- Lock file determinístico (ex: `package-lock.json`, `poetry.lock`, `Cargo.lock`, `go.sum`) 🟢
- `.gitignore` adequado à stack (com **lock file EXPLICITAMENTE FORA** dele) 🟢
- Commit inicial canônico no formato A:/P:/Refs: 🟢

## Regras de Negócio

- **Sem `ARCHITECTURE.md`, MDCU não inicia F2.** Gate bloqueante. (project-init/SKILL.md:251) 🟢
- **Sem lock determinístico, fase 3 ABORTA.** Não há contrato válido sem lock. (project-init/SKILL.md:252) 🟢
- **Lock file é commitado, sempre. NUNCA em `.gitignore`.** Regra absoluta. (project-init/SKILL.md:147-149, 253) 🟢
- **Mexer dependência em F6 do MDCU = manifesto + lock no MESMO commit.** Separar é quebrar reprodutibilidade. (project-init/SKILL.md:151, 254) 🟢
- **`requirements.txt` sem pinning estrito NÃO conta como lock.** (project-init/SKILL.md:82) 🟢
- **Versões flutuantes no manifesto OK; lock CONGELA versão exata.** Manifesto é política, lock é fato. (project-init/SKILL.md:153) 🟢
- **Upgrades são deliberados.** Dependabot/Renovate só sugere; merge é decisão humana. (project-init/SKILL.md:155) 🟢
- **CI usa lock** (`npm ci`, `poetry install --no-update`, `cargo build --locked`). Nunca install solto. (project-init/SKILL.md:163) 🟢
- **Stack desconhecida** (fora da tabela canônica de 12) exige pesquisa + proposta + confirmação humana. (project-init/SKILL.md:82) 🟢
- **Violação de guardrail em F5/F6 do MDCU exige `--refresh` ou reenquadramento.** (project-init/SKILL.md:115-116, 256) 🟢
- **`--refresh` não apaga `ARCHITECTURE.md`.** Edita in place; registra alteração em changelog/ADR. (project-init/SKILL.md:255) 🟢
- **Projetos ultra-simples** (script único, snippet) podem prescindir de lock — **mas então não entram no workflow MDCU/RSOP**. (project-init/SKILL.md:168-169) 🟢

## Fluxo Principal — `/project-init` (caminho longo)

1. **Verifica `ARCHITECTURE.md`.** Se já existe, ABORTA e sugere `--refresh`. 🟢
2. **F1 Identificação:** coleta nome, propósito (1 frase), responsáveis, stakeholders, raiz. Se MDCU já tem em `rsop/dados_base.md`, REUTILIZA. 🟢
3. **F2 Stack:** valida linguagem, framework, runtime, infra alvo. Critério: consolidado > experimental (justificar exótico via ADR). 🟢
4. **F3 Gerenciador + Lock (VINCULANTE):** lookup na tabela canônica. Stack desconhecida → pesquisa + propõe + confirma. Se nenhum lock determinístico viável → ABORTA. 🟢
5. **F4 Estrutura + convenções:** define `src/`, `tests/`, `rsop/`, `docs/` (ou idiomático) + lint/format/naming/branches. 🟢
6. **F5 Comandos principais:** registra `install/dev/test/build/lint/format` (e `migrate/seed` se DB) — viram contrato. 🟢
7. **F6 Guardrails:** lista invariantes (decisões irreversíveis, limites de escopo, regras de segurança estrutural). 🟢
8. **F7 Geração + commit inicial:**
   - Cria `ARCHITECTURE.md` (template de 9 seções)
   - Inicializa gerenciador (`npm init`, `poetry init`, `cargo init`, `go mod init`, etc.)
   - Instala deps iniciais → **GERA LOCK FILE**
   - `git init` se necessário + `.gitignore` por stack (com lock EXPLICITAMENTE fora)
   - Commit inicial canônico:
     ```
     chore: project-init — contrato técnico estabelecido

     A: Projeto sem contrato técnico formal — risco de decisões ad hoc...
     P: ARCHITECTURE.md + [manifesto] + [lock file] gerados e commitados

     Refs: ARCHITECTURE.md
     ``` 🟢

## Fluxos Alternativos

- **`/project-init --refresh`:** pula F1 (assume identificação preservada); re-executa F2-F6 in place; registra alteração em changelog interno do `ARCHITECTURE.md` ou ADR separado. NÃO apaga o arquivo. 🟢
- **`/project-init --check`:** verifica 4 pontos:
  1. `ARCHITECTURE.md` existe?
  2. Lock file declarado existe?
  3. Lock bate com manifesto (sem dessincronia)?
  4. Guardrails coerentes com código atual?
  Falha em qualquer ponto retorna instrução específica. 🟢
- **Stack `requirements.txt` sem pinning:** ABORTA fase 3 com mensagem de redefinição. 🟢
- **Projeto ultra-simples** (snippet): pode prescindir, mas perde acesso a MDCU/RSOP. 🟢
- **`/project-init` em projeto SEM git inicializado:** executa `git init` antes do commit inicial. 🟡 (implícito)

## Dependências

- **Autônoma** dentro do framework. 🟢
- É invocada por: `mdcu` (gate bloqueante F1→F2). 🟢
- Integra com (project-init/SKILL.md:272-279):
  - `rsop` — `dados_base.md` pode referenciar `ARCHITECTURE.md` (fonte única de verdade é o `ARCHITECTURE.md`)
  - `mdcu-seg` — guardrails de segurança rastreados em `rsop/seguranca.md`
  - `commit-soap` — commit inicial usa formato A:/P:/Refs:

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência | Confiança |
|---|---|---|---|
| Reprodutibilidade | Lock file determinístico em CI (`npm ci`, etc.); commit conjunto manifesto+lock | project-init/SKILL.md:151, 163 | 🟢 |
| Auditabilidade | `ARCHITECTURE.md` versionado; `--check` revela divergência | project-init/SKILL.md:265 | 🟢 |
| Estabilidade | Guardrails são invariantes; mudança exige `--refresh` deliberado | project-init/SKILL.md:115, 256 | 🟢 |
| Portabilidade | 12 stacks suportadas + extensão por pesquisa | project-init/SKILL.md:67-82 | 🟢 |
| Idempotência | `--refresh` re-executa sem apagar | project-init/SKILL.md:255 | 🟢 |
| Segurança | Guardrails de segurança estrutural ficam no `ARCHITECTURE.md` (segredos via vault, PII em tabelas marcadas, etc.) | project-init/SKILL.md:113-114 | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que um projeto novo TS/Node não tem ARCHITECTURE.md
Quando o usuário digita /project-init
Então project-init conduz as 7 fases
  E gera ARCHITECTURE.md, package.json, package-lock.json (ou pnpm-lock.yaml ou yarn.lock)
  E o lock file está fora do .gitignore
  E faz commit inicial com mensagem canônica chore: project-init

Dado que ARCHITECTURE.md já existe
Quando o usuário digita /project-init
Então project-init ABORTA com sugestão de --refresh

Dado que o usuário escolheu Python e quer usar requirements.txt sem pinning
Quando project-init avança para fase 3
Então project-init ABORTA exigindo redefinição (Poetry / uv / pip-tools com pinning)

Dado que ARCHITECTURE.md existe mas o lock está dessincronizado com o manifesto
Quando o usuário digita /project-init --check
Então project-init retorna FAIL no ponto 3 com instrução de regenerar lock
  (npm install / poetry lock / cargo update --workspace)

Dado que MDCU em F1 verificou e ARCHITECTURE.md está ausente
Quando MDCU INTERROMPE e invoca /project-init
Então project-init é executado, ARCHITECTURE.md é criado, e MDCU retorna a F1
  agora podendo avançar para F2

Dado que F6 do MDCU vai instalar uma nova dependência
Quando o agente executa npm install X (ou poetry add X / cargo add X)
Então o lock file é regenerado
  E manifesto + lock entram no MESMO commit
  E project-init --check posterior passa
```

## Prioridade

| Requisito | MoSCoW | Justificativa |
|---|---|---|
| Lock file obrigatório | Must | Reprodutibilidade não é opcional — citação literal |
| Gate bloqueante MDCU F1→F2 | Must | Sem contrato técnico não há terreno estável |
| 7 fases do `/project-init` | Must | Caminho canônico de inicialização |
| Tabela canônica 12 stacks | Must | Determinismo do mapeamento stack→lock |
| `--refresh` in place | Must | Mudança estrutural sem perder histórico |
| `--check` 4-pontos | Should | Auditoria de conformidade |
| Pesquisa de stack desconhecida | Should | Extensibilidade |
| `--status` | Could | Conveniência |
| Auto-detecção de violação de guardrail | Won't | Detecção fica com MDCU em F5/F6 — esta skill não monitora |

## Rastreabilidade de Código

| Arquivo | Componente lógico | Cobertura |
|---|---|---|
| `project-init/SKILL.md:1-3` | frontmatter | 🟢 |
| `project-init/SKILL.md:6-14` | Fundamento | 🟢 |
| `project-init/SKILL.md:18-26` | Posicionamento + gatilho reverso pelo MDCU | 🟢 |
| `project-init/SKILL.md:30-35` | Artefatos produzidos | 🟢 |
| `project-init/SKILL.md:39-133` | 7 fases | 🟢 |
| `project-init/SKILL.md:137-184` | Gestão Determinística de Dependências (8 regras + exceções + sinalização) | 🟢 |
| `project-init/SKILL.md:189-245` | Template `ARCHITECTURE.md` | 🟢 |
| `project-init/SKILL.md:249-257` | 7 regras de operação | 🟢 |
| `project-init/SKILL.md:262-266` | Comandos `/project-init` | 🟢 |
| `project-init/SKILL.md:272-279` | Integração com outras skills | 🟢 |

---

## Refresh 2026-04-27 — delta v2.0.0

> Acionado pelo commit `1378d5e` — split estrutural project-init/project-setup. Detalhes em `_reversa_sdd/code-analysis.md` apêndice.

### Mudanças estruturais 🟢

- **Frontmatter `version: "2.0.0"` + `author: Iago Leal`** — bump MAJOR (escopo reduzido)
- **Description redefinida** — "extração de contrato técnico" (antes "inicialização")
- **Workflow redesenhado** — `project-init → project-setup → MDCU` (antes `project-init → MDCU`)
- **"Artefato produzido" reduzido** — apenas `ARCHITECTURE.md`. **NÃO produz** mais manifesto, lock file, `.gitignore`, commit inicial
- **Fase 7 reescrita** — gera apenas `ARCHITECTURE.md` + invoca `/project-setup` automaticamente para materialização
- **Nova mensagem de handoff** explícita ao usuário ao final da fase 7
- **Regras de operação atualizadas** — regra 3 nova: "Esta skill NÃO executa setup técnico"

### Diferença essencial vs. v1.x 🟢

**v1.x:** project-init era ato monolítico — extraía contrato + executava `npm/poetry/cargo init` + instalava deps + fazia `git init` + `git commit` inicial.

**v2.0.0:** project-init **só extrai contrato** e gera `ARCHITECTURE.md` em prosa. Materialização técnica (setup em disco) é **delegada à nova skill `project-setup`** sob princípio P-8 (`framework/principles.md`) — delegação a engines downstream desacopláveis.

### Gestão Determinística de Dependências preservada 🟢

A seção integral "Gestão Determinística de Dependências" (8 regras vinculantes + exceções + sinalização em ARCHITECTURE.md) foi **preservada** como prescrição canônica. Mudança: o **enforcement efetivo** das regras agora cabe ao `project-setup` (modo desacoplado via engine de scaffolding OU monolítico declarado). Conceito: regras descrevem **como** o lock file deve funcionar, independente de **quem** executa.

### Critério de Aceitação NOVO (Gherkin)

```gherkin
Cenário: project-init delega materialização para project-setup ao final da fase 7
  Dado que /project-init concluiu fases 1-6 (extração de contrato)
  E que ARCHITECTURE.md foi gerado na raiz do projeto
  Quando a fase 7 termina
  Então /project-setup é invocado automaticamente (ou usuário é orientado a invocar)
  E project-init NÃO executa npm init / poetry init / git init / git commit
  E a mensagem de handoff é exibida ao usuário com próximos passos

Cenário: project-init --refresh notifica project-setup sobre mudança estrutural
  Dado que /project-init --refresh foi executado
  E que ARCHITECTURE.md teve stack ou gerenciador modificado
  Quando o refresh termina
  Então /project-setup --refresh é invocado para reaplicar setup
  E divergência entre ARCHITECTURE.md e estado em disco é detectada e ajustada
```

### Priorização MoSCoW — atualização

- **Must:** split project-init / project-setup operacional (P-7 + P-8)
- **Must:** Gestão Determinística de Dependências preservada como prescrição canônica
- **Should:** invocação automática de `project-setup` ao final da fase 7 (alternativa: orientar usuário)

### Lacuna remanescente

- Versionamento implícito do `ARCHITECTURE.md` (contrato evolui com `--refresh`) ainda não é versionado por semver — fica para release-train v2026.06+
