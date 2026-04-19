---
name: project-init
description: Inicialização de contrato técnico de projeto — estabelece `ARCHITECTURE.md` (stack, estrutura, convenções, guardrails), gerenciador de pacotes, lock file determinístico e commit inicial. Pré-requisito bloqueante para o MDCU avançar de F1 para F2. ATIVE SEMPRE que o usuário digitar /project-init ou /project-init --refresh, quando a skill `mdcu` em F1 detectar ausência de `ARCHITECTURE.md` na raiz do projeto, quando iniciar um projeto do zero, pedir para "definir arquitetura", "configurar gerenciador de pacotes", "setup inicial", ou mencionar `ARCHITECTURE.md`. Ative proativamente quando o projeto não tiver manifesto de dependências pinadas (risco de build quebrado por upgrade silencioso) ou documento arquitetural. NÃO ative para ajustes pontuais em projetos já inicializados — `--refresh` só em mudança estrutural (troca de stack, troca de gerenciador, novo guardrail).
---

# project-init — Inicialização de Contrato Técnico

## Fundamento

Todo projeto tem um contrato técnico implícito: qual a stack, onde as coisas moram, como se instala dependência, como se roda teste, o que não pode mudar sem discussão. Implícito, esse contrato é pântano — cada sessão de IA reinventa regras, cada colaborador vira arqueólogo, e upgrades silenciosos de dependência quebram o sistema sem aviso.

O `project-init` formaliza o contrato em disco e o torna **consultável, versionável e vinculante**. É a certidão de nascimento do projeto.

**Analogia clínica:** equivalente à ficha de identificação e anamnese inicial de admissão. Sem ela, o prontuário (RSOP) não tem âncora, e o raciocínio clínico (MDCU) opera sobre paciente desconhecido. Stack, convenções e lock file são dados demográficos e antropométricos do sistema — mudam raramente, mas condicionam todo o resto.

---

## Posição no workflow

```
project-init (1× ou --refresh)  →  MDCU F1  →  F2 Escuta  →  ...  →  RSOP SOAP  →  commit-soap
```

Executado **uma vez** ao iniciar um projeto. Re-executado com `--refresh` em mudança estrutural (troca de stack, troca de gerenciador de pacotes, adição de guardrail arquitetural relevante).

**Gatilho reverso (invocação pelo MDCU):** a skill `mdcu`, ao entrar em F1, verifica se `ARCHITECTURE.md` existe na raiz do projeto. Se não existe, interrompe o fluxo e invoca `/project-init`. F2 só inicia após `project-init` concluído.

---

## Artefatos produzidos

1. **`ARCHITECTURE.md`** (raiz do projeto) — contrato técnico estável.
2. **Manifesto de dependências** (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `composer.json`, etc.) — dependências declaradas.
3. **Lock file determinístico** (ver Gestão Determinística de Dependências) — versões pinadas e reprodutíveis.
4. **Commit inicial** com os três artefatos acima + estrutura mínima de diretórios.

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

Estes comandos viram contrato: a IA em F6 usa estes — não inventa variantes.

### 6. Guardrails e invariantes

Seção explícita do `ARCHITECTURE.md` que lista o que **não pode** mudar sem reenquadramento explícito:
- Decisões arquiteturais irreversíveis (ex. "tudo é type-safe end-to-end", "migrations são forward-only", "nenhum serviço fala direto com o DB de outro").
- Limites de escopo (o que o projeto faz e, principalmente, o que NÃO faz).
- Regras de segurança estruturais (ex. "segredos só via secret manager", "PII só em tabelas marcadas `restricted`").

**Regra:** se durante o MDCU F5/F6 uma decisão violar um guardrail, a execução **não prossegue** — exige `/project-init --refresh` para reformalizar o contrato, ou reenquadramento do problema.

### 7. Geração e commit inicial

- Criar `ARCHITECTURE.md` com tudo acima preenchido.
- Inicializar o gerenciador de pacotes (`npm init`, `poetry init`, `cargo init`, `go mod init`, etc.).
- Instalar dependências iniciais (se definidas) — **gerando o lock file**.
- Inicializar git (se ainda não inicializado).
- `.gitignore` adequado para a stack.
- **Commit inicial** com todos os artefatos, mensagem canônica:
  ```
  chore: project-init — contrato técnico estabelecido

  A: Projeto sem contrato técnico formal — risco de decisões ad hoc e builds não reprodutíveis
  P: ARCHITECTURE.md + [manifesto] + [lock file] gerados e commitados

  Refs: ARCHITECTURE.md
  ```

---

## Gestão Determinística de Dependências (DIRETRIZ OBRIGATÓRIA)

### Princípio

**O lock file é a receita médica exata do sistema.** Uma prescrição sem dose, via, frequência e fabricante não é prescrição — é sugestão. Da mesma forma, `"express": "^4.0.0"` em um manifesto sem lock é sugestão; `"express": "4.19.2"` com hash SHA no lock é prescrição executável.

Um projeto sem lock file rigoroso sofre das mesmas patologias de um sistema de saúde sem padronização de prescrição: efeitos colaterais imprevistos (build quebrado por patch silencioso em dep transitiva), incompatibilidade entre ambientes (dev e prod com versões diferentes de uma lib), impossibilidade de reprodução retrospectiva (não se consegue auditar o que rodou em produção no mês passado).

### Regras vinculantes

1. **Todo projeto gerado/configurado por este skill deve definir um gerenciador de pacotes que produza um arquivo de lock** (ex: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `uv.lock`, `Cargo.lock`, `go.sum`, `Gemfile.lock`, `composer.lock`, `mix.lock`).

2. **O lock file é commitado no repositório. Sempre.** Nunca `.gitignore`-ado. O `.gitignore` padrão gerado por esta skill inclui `node_modules/`, `__pycache__/`, `target/`, `dist/`, etc. — **nunca** o lock file.

3. **A instalação, atualização ou remoção de dependências na Fase 6 (Execução) do MDCU sem a geração/atualização rigorosa do respectivo arquivo de lock é ESTRITAMENTE PROIBIDA.** Qualquer alteração em dependência é operação de duas partes: (a) altera manifesto, (b) regenera lock. Commit deve incluir ambos.

4. **Versões flutuantes (`^`, `~`, `*`, `latest`, `>=`) no manifesto são aceitáveis** — são expressão de intenção — **desde que o lock file congele a versão exata resolvida**. O manifesto é política, o lock é o fato.

5. **Upgrades de dependência são operações deliberadas**, não automáticas. Ferramentas como Dependabot/Renovate podem sugerir — o merge de PR de upgrade é decisão humana, com regeneração do lock file na ponta.

6. **Em F6, ao instalar/atualizar dependência, a IA deve:**
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
- **Commits:** ver skill `commit-soap` para selos de sessão; `git commit` padrão para WIPs

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
2. **Sem lock file, não há `ARCHITECTURE.md` válido.** A fase 3 aborta se a stack escolhida não admite gerenciador com lock.
3. **Lock file é sempre commitado.** Nunca `.gitignore`-ado. Nunca.
4. **Alteração de dependência em F6 = manifesto + lock no mesmo commit.** Separar é quebrar reprodutibilidade.
5. **`--refresh` não apaga o `ARCHITECTURE.md`.** Edita in place, registra a alteração em seção de changelog (ou em ADR), e re-commita.
6. **Guardrails são vinculantes.** Violação em F5/F6 → exige `--refresh` ou reenquadramento do plano.
7. **Esta skill não implementa código do projeto.** Só contrato e setup inicial. Código vai no MDCU F6.

---

## Uso com `/project-init`

- `/project-init` — inicia as 7 fases para um projeto novo. Se `ARCHITECTURE.md` já existe, aborta e sugere `--refresh`.
- `/project-init --refresh` — re-executa as fases 2–6 sobre o `ARCHITECTURE.md` existente. Útil em troca de stack, troca de gerenciador, adição de guardrail.
- `/project-init --check` — valida se o projeto atual está conforme: existe `ARCHITECTURE.md`? existe lock file? o lock bate com o manifesto? guardrails estão coerentes com código atual? Retorna relatório telegráfico.
- `/project-init status` — mostra stack declarada, gerenciador, lock file presente (sim/não), última atualização.

---

## Integração com outras skills

| Skill | Integração |
|-------|------------|
| `mdcu` | Gatilho bloqueante em F1; `ARCHITECTURE.md` é lido no início de toda sessão. |
| `rsop` | `dados_base.md` do RSOP pode se sobrepor a partes do `ARCHITECTURE.md` (identificação, stack) — fonte única de verdade é o `ARCHITECTURE.md`; o `dados_base.md` pode referenciá-lo. |
| `mdcu-seg` | Guardrails de segurança do `ARCHITECTURE.md` são rastreados pelo regime de auditoria em `rsop/seguranca.md`. |
| `commit-soap` | O commit inicial gerado por `project-init` segue o formato A+P, mesmo não vindo de SOAP — é o marco zero. |
| `alfred` | Alfred lista projetos inicializados (com `ARCHITECTURE.md`) separadamente de projetos em rascunho (sem). |
