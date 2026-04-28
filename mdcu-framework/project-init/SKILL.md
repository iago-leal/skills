---
name: project-init
version: "2.0.0"
author: Iago Leal <github.com/iago-leal>
description: Extração de contrato técnico de projeto — conduz a anamnese arquitetural com o usuário e produz `ARCHITECTURE.md` (stack, gerenciador de pacotes, lock file declarado, estrutura, convenções, comandos, guardrails). NÃO executa setup técnico — quem materializa o contrato em disco é a skill `project-setup`. Pré-requisito bloqueante para o MDCU avançar de F1 para F2. ATIVE SEMPRE que o usuário digitar /project-init ou /project-init --refresh, quando a skill `mdcu` em F1 detectar ausência de `ARCHITECTURE.md` na raiz do projeto, quando iniciar um projeto do zero, pedir para "definir arquitetura", "documentar contrato técnico", ou mencionar `ARCHITECTURE.md`. Ative proativamente quando o projeto não tiver documento arquitetural. NÃO ative para ajustes pontuais em projetos já inicializados — `--refresh` só em mudança estrutural (troca de stack, troca de gerenciador, novo guardrail).
---

# project-init — Extração de Contrato Técnico

## Fundamento

Todo projeto tem um contrato técnico implícito: qual a stack, onde as coisas moram, como se instala dependência, como se roda teste, o que não pode mudar sem discussão. Implícito, esse contrato é pântano — cada sessão de IA reinventa regras, cada colaborador vira arqueólogo, e upgrades silenciosos de dependência quebram o sistema sem aviso.

O `project-init` formaliza o contrato em disco e o torna **consultável, versionável e vinculante** — produz `ARCHITECTURE.md` (a certidão de nascimento do projeto). **Não executa o setup técnico** (instalar dependências, criar lock file, fazer commit inicial) — isso é responsabilidade da skill `project-setup`, que recebe `ARCHITECTURE.md` como input e materializa o contrato em disco.

**Analogia clínica:** equivalente à anamnese inicial de admissão + redação do plano terapêutico. Sem ela, o prontuário (RSOP) não tem âncora, e o raciocínio clínico (MDCU) opera sobre paciente desconhecido. A **execução** do plano (medicação, procedimentos) é etapa subsequente, papel da equipe de execução — análogo ao `project-setup`.

---

## Posição no workflow

```
project-init (extrai contrato → ARCHITECTURE.md)
   ↓
project-setup (materializa: npm/poetry/cargo init + lock + .gitignore + commit inicial via commit-soap)
   ↓
MDCU F1  →  F2 Escuta  →  ...  →  RSOP SOAP  →  commit-soap
```

Executado **uma vez** ao iniciar um projeto. Re-executado com `--refresh` em mudança estrutural (troca de stack, troca de gerenciador de pacotes, adição de guardrail arquitetural relevante).

**Gatilho reverso (invocação pelo MDCU):** a skill `mdcu`, ao entrar em F1, verifica se `ARCHITECTURE.md` existe na raiz do projeto. Se não existe, interrompe o fluxo e invoca `/project-init`. F2 só inicia após `project-init` **e** `project-setup` concluídos.

**Composição P-7:** `project-init` faz o **contrato**; `project-setup` faz a **materialização**. Cada skill tem responsabilidade única (ver `framework/principles.md` P-7, P-8).

---

## Artefato produzido

**`ARCHITECTURE.md`** (raiz do projeto) — contrato técnico estável.

**Não produz:** manifesto de dependências, lock file, `.gitignore`, commit inicial. Estes são produzidos por `project-setup` (modo desacoplado) ou por orquestrador-instância em modo monolítico de `project-setup`.

---

## Fases do `/project-init`

### 1. Identificação

Coletar do usuário (ou da conversa corrente do MDCU F1):
- Nome do projeto.
- Propósito em 1 frase.
- Responsáveis e stakeholders principais.
- Raiz do projeto no filesystem.

Se o MDCU já tem esses dados no `rsop/dados_base.md`, reutilizar — não perguntar duas vezes.

### 2. Seleção de stack

Perguntar/validar:
- Linguagem principal.
- Framework (se houver).
- Runtime/versão (node 20, python 3.12, rust 1.80, etc.).
- Infra alvo (onde roda em produção).

**Critério de evidência (herdado do MDCU F5):** precedência de tecnologias consolidadas > experimentais. Escolha exótica exige justificativa registrada em ADR.

### 3. Definição de gerenciador de pacotes + lock file

**Esta fase é vinculante.** Sem gerenciador com lock file determinístico, a skill aborta e exige redefinição. Ver seção "Gestão Determinística de Dependências" abaixo.

Mapeamento canônico por stack:

| Stack | Gerenciador | Manifesto | Lock file |
|-------|-------------|-----------|-----------|
| JavaScript/TypeScript | npm | `package.json` | `package-lock.json` |
| JavaScript/TypeScript | yarn | `package.json` | `yarn.lock` |
| JavaScript/TypeScript | pnpm | `package.json` | `pnpm-lock.yaml` |
| Python | Poetry | `pyproject.toml` | `poetry.lock` |
| Python | uv | `pyproject.toml` | `uv.lock` |
| Python | pip + pip-tools | `requirements.in` | `requirements.txt` (pinado) |
| Rust | Cargo | `Cargo.toml` | `Cargo.lock` |
| Go | Go modules | `go.mod` | `go.sum` |
| Ruby | Bundler | `Gemfile` | `Gemfile.lock` |
| PHP | Composer | `composer.json` | `composer.lock` |
| Elixir | Mix | `mix.exs` | `mix.lock` |
| .NET | NuGet | `*.csproj` | `packages.lock.json` (habilitar) |

Se a stack escolhida não aparece acima, o agente **pesquisa e propõe** o lock file canônico da comunidade — e só prossegue após confirmação do usuário. `requirements.txt` sem pinning estrito (ex. `flask`, sem versão) **não conta como lock file**.

**Importante:** esta fase apenas **declara** gerenciador + lock file no `ARCHITECTURE.md`. A geração efetiva do lock file (instalação de dependências) é responsabilidade do `project-setup`.

### 4. Estrutura de diretórios e convenções

Definir layout mínimo:
- `src/` (ou equivalente idiomático da stack).
- `tests/` (ou `test/` conforme idioma da stack).
- `rsop/` (para a skill `rsop`).
- `docs/` (se aplicável).

Convenções:
- Estilo de código (linter, formatter).
- Naming (snake_case / camelCase / kebab-case / PascalCase — por contexto).
- Estratégia de branch (trunk-based / git flow / GitHub flow).

### 5. Comandos principais

Registrar no `ARCHITECTURE.md` os comandos canônicos do projeto:
- `install` (instalar dependências)
- `dev` (rodar em desenvolvimento)
- `test` (rodar testes)
- `build` (produção)
- `lint` / `format`
- `migrate` / `seed` (se DB)

Estes comandos viram contrato: a IA em F6 do MDCU usa estes — não inventa variantes.

### 6. Guardrails e invariantes

Seção explícita do `ARCHITECTURE.md` que lista o que **não pode** mudar sem reenquadramento explícito:
- Decisões arquiteturais irreversíveis (ex. "tudo é type-safe end-to-end", "migrations são forward-only", "nenhum serviço fala direto com o DB de outro").
- Limites de escopo (o que o projeto faz e, principalmente, o que NÃO faz).
- Regras de segurança estruturais (ex. "segredos só via secret manager", "PII só em tabelas marcadas `restricted`").

**Regra:** se durante o MDCU F5/F6 uma decisão violar um guardrail, a execução **não prossegue** — exige `/project-init --refresh` para reformalizar o contrato, ou reenquadramento do problema.

### 7. Geração do `ARCHITECTURE.md` + handoff para `project-setup`

- Criar `ARCHITECTURE.md` na raiz do projeto com tudo coletado nas fases 1-6.
- **Não criar** manifesto, lock file, `.gitignore` ou commit inicial — esses são responsabilidade de `project-setup`.
- **Handoff:** ao final da fase 7, invocar `/project-setup` automaticamente (ou orientar o usuário a invocar) para materializar o contrato. `project-setup` lê `ARCHITECTURE.md` como input e executa o setup técnico (ver `project-setup/SKILL.md`).

**Mensagem de handoff esperada:**

```
[project-init concluído]

ARCHITECTURE.md criado em: [caminho]
Contrato técnico extraído:
- Stack: [stack]
- Gerenciador: [gerenciador]
- Lock file declarado: [lock]

Próximo passo: /project-setup para materializar o contrato (instalar dependências,
gerar lock file, commit inicial). MDCU só pode iniciar F2 após project-setup.
```

---

## Gestão Determinística de Dependências (DIRETRIZ CANÔNICA)

### Princípio

**O lock file é a receita médica exata do sistema.** Uma prescrição sem dose, via, frequência e fabricante não é prescrição — é sugestão. Da mesma forma, `"express": "^4.0.0"` em um manifesto sem lock é sugestão; `"express": "4.19.2"` com hash SHA no lock é prescrição executável.

Um projeto sem lock file rigoroso sofre das mesmas patologias de um sistema de saúde sem padronização de prescrição: efeitos colaterais imprevistos (build quebrado por patch silencioso em dep transitiva), incompatibilidade entre ambientes (dev e prod com versões diferentes de uma lib), impossibilidade de reprodução retrospectiva (não se consegue auditar o que rodou em produção no mês passado).

### Regras vinculantes (vigoram em ambos os modos — desacoplado e monolítico)

> Estas regras são **canônicas e prescritivas**, independem de quem executa o setup. Em modo desacoplado (engine de scaffolding plugado), o engine respeita. Em modo monolítico (orquestrador-instância como engine ad-hoc), o orquestrador respeita.

1. **Todo projeto deve definir um gerenciador de pacotes que produza um arquivo de lock** (ex: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `uv.lock`, `Cargo.lock`, `go.sum`, `Gemfile.lock`, `composer.lock`, `mix.lock`).

2. **O lock file é commitado no repositório. Sempre.** Nunca `.gitignore`-ado. O `.gitignore` padrão gerado por `project-setup` inclui `node_modules/`, `__pycache__/`, `target/`, `dist/`, etc. — **nunca** o lock file.

3. **A instalação, atualização ou remoção de dependências sem a geração/atualização rigorosa do respectivo arquivo de lock é ESTRITAMENTE PROIBIDA.** Qualquer alteração em dependência é operação de duas partes: (a) altera manifesto, (b) regenera lock. Commit deve incluir ambos.

4. **Versões flutuantes (`^`, `~`, `*`, `latest`, `>=`) no manifesto são aceitáveis** — são expressão de intenção — **desde que o lock file congele a versão exata resolvida**. O manifesto é política, o lock é o fato.

5. **Upgrades de dependência são operações deliberadas**, não automáticas. Ferramentas como Dependabot/Renovate podem sugerir — o merge de PR de upgrade é decisão humana, com regeneração do lock file na ponta.

6. **Em F6 do MDCU (modo monolítico de execução), ao instalar/atualizar dependência, o orquestrador-instância deve:**
   - Executar o comando idiomático do gerenciador (`npm install X`, `poetry add X`, `cargo add X`, etc.).
   - Verificar que o lock file foi modificado.
   - Incluir manifesto **e** lock file no mesmo commit.
   - Se o lock file não foi modificado (ex. porque o comando falhou ou porque a dependência já estava instalada), investigar antes de prosseguir.

7. **Em CI/CD, builds usam o lock file (`npm ci`, `poetry install --no-update`, `cargo build --locked`, etc.).** Nunca `npm install` solto em CI — isso pode regenerar o lock silenciosamente.

8. **Auditoria periódica:** `npm audit`, `poetry check`, `cargo audit`, `pip-audit`, etc. fazem parte do regime de vigilância (ver `mdcu-seg auditoria`). Vulnerabilidade em dep com fix disponível vira `#` no RSOP.

### Exceções

Projetos ultra-simples (script único, experimento descartável, snippet de demonstração) podem prescindir de lock file — **mas então não entram no workflow MDCU/RSOP**. O MDCU exige `ARCHITECTURE.md`, e o `ARCHITECTURE.md` exige lock file. Sem um dos dois, não é projeto formal; é rascunho.

### Sinalização em ARCHITECTURE.md

A seção de dependências do `ARCHITECTURE.md` deve declarar:

```markdown
## Dependências
- **Gerenciador:** [npm | yarn | pnpm | poetry | uv | ...]
- **Manifesto:** [package.json | pyproject.toml | ...]
- **Lock file:** [package-lock.json | poetry.lock | ...] — COMMITADO
- **Política de versão:** [ex. ^x.y.z no manifesto, versão exata no lock]
- **Auditoria:** [ferramenta, frequência — ex. `npm audit` no CI a cada PR]
- **Upgrades:** [manual | Dependabot/Renovate com review humano]
```

---

## Template do `ARCHITECTURE.md`

```markdown
# Architecture — [Nome do projeto]
- **Atualizado:** [data]

## Identificação
- **Propósito:** [1 frase]
- **Responsáveis:** [quem]
- **Stakeholders:** [quem é afetado]

## Stack
- **Linguagem:** [ex. TypeScript 5.4]
- **Runtime:** [ex. Node 20 LTS]
- **Framework:** [ex. Next.js 14 App Router]
- **Banco de dados:** [ex. PostgreSQL 16]
- **Infra:** [ex. Railway + Vercel]

## Dependências
- **Gerenciador:** [ex. pnpm]
- **Manifesto:** [ex. package.json]
- **Lock file:** [ex. pnpm-lock.yaml] — COMMITADO
- **Política de versão:** [ex. ^ no manifesto, exata no lock]
- **Auditoria:** [ex. `pnpm audit` no CI]
- **Upgrades:** [ex. Renovate com review humano]

## Estrutura de diretórios
- `src/` — código fonte
- `tests/` — testes
- `rsop/` — prontuário do projeto (ver skill `rsop`)
- `docs/` — documentação adicional

## Convenções
- **Lint:** [ex. ESLint com preset X]
- **Format:** [ex. Prettier]
- **Naming:** [ex. camelCase para variáveis, PascalCase para tipos]
- **Branches:** [ex. trunk-based, PRs curtos]
- **Commits:** ver skill `commit-soap` para selos de marcos longitudinais; `git commit` padrão para WIPs

## Comandos principais
- `install` — [ex. `pnpm install`]
- `dev` — [ex. `pnpm dev`]
- `test` — [ex. `pnpm test`]
- `build` — [ex. `pnpm build`]
- `lint` — [ex. `pnpm lint`]
- `format` — [ex. `pnpm format`]

## Guardrails (invariantes — não mudar sem /project-init --refresh)
- [ex. "Toda mutação de dados passa por service layer, nunca direto no repository."]
- [ex. "Segredos só via vault X; nunca em env vars de CI."]
- [ex. "PII só em tabelas com prefixo `restricted_`."]

## Escopo
- **Faz:** [o que o projeto resolve]
- **NÃO faz:** [o que o projeto deliberadamente não abraça]

## ADRs relacionados
- [link para ADRs relevantes, se houver]
```

---

## Regras de operação

1. **Sem `ARCHITECTURE.md`, não há MDCU.** A skill `mdcu` em F1 tem gatilho inegociável que invoca esta skill na ausência.
2. **Sem lock file declarado em `ARCHITECTURE.md`, a skill aborta na fase 3.** Stack que não admite gerenciador com lock não passa pela porta.
3. **Esta skill NÃO executa setup técnico.** Não roda `npm init`, `poetry init`, `cargo init`, `git init`, `git commit`, instalação de deps. Tudo isso é responsabilidade do `project-setup` (P-7, P-8 — ver `framework/principles.md`).
4. **Lock file é sempre declarado como commitado.** Nunca `.gitignore`-ado. Esta regra vale como prescrição — o enforcement efetivo cabe ao `project-setup` (modo desacoplado ou monolítico).
5. **`--refresh` não apaga o `ARCHITECTURE.md`.** Edita in place, registra a alteração em seção de changelog (ou em ADR), e re-commita (via `commit-soap` desacoplado).
6. **Guardrails são vinculantes.** Violação em F5/F6 do MDCU → exige `--refresh` ou reenquadramento do plano.
7. **Esta skill produz contrato em prosa, não código nem dependência instalada.** Quem materializa é `project-setup`.

---

## Uso com `/project-init`

- `/project-init` — inicia as 7 fases para um projeto novo. Se `ARCHITECTURE.md` já existe, aborta e sugere `--refresh`. Ao final, invoca `/project-setup` automaticamente (ou orienta o usuário).
- `/project-init --refresh` — re-executa as fases 2–6 sobre o `ARCHITECTURE.md` existente. Útil em troca de stack, troca de gerenciador, adição de guardrail. Mudanças relevantes em stack/gerenciador disparam `/project-setup --refresh` em sequência.
- `/project-init --check` — valida se o projeto atual está conforme: existe `ARCHITECTURE.md`? guardrails estão coerentes com código atual? Retorna relatório telegráfico. (Verificação de lock file efetivo é `/project-setup --check`.)
- `/project-init status` — mostra stack declarada, gerenciador declarado, última atualização do `ARCHITECTURE.md`.

---

## Integração com outras skills

| Skill | Integração |
|-------|------------|
| `project-setup` | Recebe `ARCHITECTURE.md` como input e materializa setup técnico. Invocado no final da fase 7 do `project-init`. |
| `mdcu` | Gatilho bloqueante em F1; `ARCHITECTURE.md` é lido no início de toda sessão. F2 só inicia após `project-init` **e** `project-setup`. |
| `rsop` | `dados_base.md` do RSOP pode se sobrepor a partes do `ARCHITECTURE.md` (identificação, stack) — fonte única de verdade é o `ARCHITECTURE.md`; o `dados_base.md` pode referenciá-lo. |
| `mdcu-seg` | Guardrails de segurança do `ARCHITECTURE.md` são rastreados pelo regime de auditoria em `rsop/seguranca.md`. |
| `commit-soap` | Mudanças em `ARCHITECTURE.md` (via `--refresh`) são seladas via `commit-soap` desacoplado (qualquer marco longitudinal). |
