# SDD — `project-setup`

> Spec executável da skill `project-setup` (v0.1.0).
> Gerado pelo Reversa Writer em 2026-04-27 (refresh cirúrgico — skill nova).

## Visão Geral

Engine de **materialização do contrato técnico** extraído por `project-init`. Recebe `ARCHITECTURE.md` como input e executa setup técnico em disco: manifesto de dependências, lock file determinístico, `.gitignore` apropriado para a stack, estrutura mínima de diretórios, commit inicial via `commit-soap` desacoplado. 🟢

Skill **nova** introduzida pelo split estrutural de `project-init` (commit `1378d5e`) sob princípio P-8 (`framework/principles.md`) — delegação a engines downstream desacopláveis. 🟢

## Responsabilidades

- Receber `ARCHITECTURE.md` da raiz como input (gerado por `/project-init`). 🟢
- Selecionar **modo de operação**: desacoplado (engine de scaffolding) ou monolítico (declarado, com critério de saída). 🟢
- Materializar manifesto + lock file + `.gitignore` + estrutura mínima conforme stack declarada. 🟢
- **Enforcement efetivo** das regras canônicas de Gestão Determinística de Dependências (declaradas em `project-init/SKILL.md`). 🟢
- Invocar `commit-soap --inline` ao final para selo do commit inicial (P-9 — acompanhamento longitudinal transversal). 🟢
- NÃO produz contrato em prosa (responsabilidade de `project-init`). 🟢
- NÃO executa código de produção (responsabilidade de engines downstream em F6.a do MDCU). 🟢

## Interface

### Comandos públicos (`/`)

| Comando | Parâmetros | Saída |
|---|---|---|
| `/project-setup` | — | Materializa setup baseado em `ARCHITECTURE.md` da raiz 🟢 |
| `/project-setup --refresh` | — | Reaplica setup após `/project-init --refresh` que mudou stack/gerenciador 🟢 |
| `/project-setup --check` | — | Valida conformidade: lock file presente, bate com manifesto, `.gitignore` apropriado 🟢 |
| `/project-setup --mode <desacoplado\|monolitico>` | mode | Força modo específico (default: detecta baseado em disponibilidade de engine) 🟢 |
| `/project-setup --mode desacoplado --engine <nome>` | engine | Força engine específico (cookiecutter, yeoman, plop, copier, ...) 🟢 |

### Artefatos produzidos

| Artefato | Lifecycle | Origem |
|---|---|---|
| `<manifesto>` (`package.json` / `pyproject.toml` / `Cargo.toml` / etc) | structural | declarado em `ARCHITECTURE.md` § Dependências |
| `<lock_file>` (`package-lock.json` / `poetry.lock` / `Cargo.lock` / etc) | structural | regras canônicas de Gestão Determinística |
| `.gitignore` | structural | apropriado para a stack (nunca inclui lock file) |
| Estrutura mínima de diretórios (`src/`, `tests/`, `rsop/`, `docs/`) | structural | conforme convenções de `ARCHITECTURE.md` |
| Commit inicial (via `commit-soap --inline`) | git_history | A+P pré-formatado com Refs: ARCHITECTURE.md |

### Artefatos consumidos

- `ARCHITECTURE.md` (raiz) — input obrigatório. Aborta se ausente, orienta usuário a invocar `/project-init` primeiro. 🟢

## Modos de operação 🟢

### Modo desacoplado (preferido quando engine plugado existe)

**Engines candidatos por stack:**

| Stack | Engines candidatos |
|---|---|
| Python | cookiecutter (templates), copier (templates evolutivos) |
| JavaScript/TypeScript | create-next-app, create-vite, plop (custom), yeoman |
| Rust | cargo-generate |
| Go | (sem cookiecutter idiomático maduro; usar templates customizados) |
| Multi-stack | yeoman, plop, copier |

**Operação:**
1. Identificar engine apropriado para a stack declarada
2. Invocar engine com input mínimo (stack + nome + caminho)
3. Verificar que engine produziu manifesto + lock file conforme `ARCHITECTURE.md`
4. Validar `.gitignore` (engine pode ter gerado; senão adicionar)
5. Verificar correspondência manifesto ↔ lock declarado
6. Invocar `/commit-soap --inline` para selar

**Por que preferir:** engines maduros encarnam boas práticas comunitárias; reduzem custo de manutenção; cumprem P-8 estruturalmente.

### Modo monolítico declarado (exceção com critério de saída)

Quando **nenhum engine de scaffolding maduro** está disponível para a stack, ou quando custo de plugar engine externo > custo de execução direta.

**Critérios de aceitação:**
- Stack incomum sem engine de scaffolding maduro
- Projeto pequeno ou em fase exploratória onde cookiecutter/yeoman seria over-engineering
- Adopter explicitamente prefere monolítico (decisão informada — F-3, RN-D-014)

**Critério de saída (quando migrar para desacoplado):**
- Stack ganha engine maduro
- Projeto cresce e múltiplos colaboradores precisam reproduzir setup deterministicamente
- Manutenção do "monolítico ad-hoc" vira gargalo cognitivo

**Operação:**
1. Executar `npm init` / `poetry init` / `cargo init` / `go mod init` / etc.
2. Instalar dependências iniciais → **gera lock file**
3. Verificar lock file efetivo bate com declaração do `ARCHITECTURE.md`
4. Inicializar git se ainda não inicializado
5. Gerar `.gitignore` adequado (nunca incluir lock file)
6. Criar estrutura mínima de diretórios
7. Invocar `/commit-soap --inline` para selar

## Regras de Negócio 🟢

### RN — Pré-condição: `ARCHITECTURE.md` deve existir

> Sem `ARCHITECTURE.md` válido, `project-setup` aborta. Não improvisar contrato — orientar usuário a invocar `/project-init` primeiro.

### RN — Modo monolítico é exceção declarada

> NÃO silencioso. Adopter precisa saber em qual modo está, com critério de saída visível. Modo silencioso transformaria P-8 em mito-aspiracional.

### RN — Gestão Determinística de Dependências (vinculante)

> Regras canônicas declaradas em `project-init/SKILL.md` § "Gestão Determinística de Dependências" são **enforcement efetivo** aqui. Lock file commitado, sempre. Lock file nunca em `.gitignore`. Manifesto + lock no mesmo commit.

### RN — Selo via `commit-soap --inline`

> Commit inicial NÃO usa `git commit` direto. Usa `/commit-soap --inline` com A+P estruturado — mesmo selo de qualquer marco longitudinal (P-9). Garante que `git log --grep="A:"` capture o setup inicial como marco cognitivo.

### RN — `--refresh` é cirúrgico

> Não recria o que já existe. Detecta divergência entre `ARCHITECTURE.md` e estado em disco; ajusta apenas as diferenças. Reusa lock file existente sempre que compatível com novo manifesto.

## Critérios de Aceitação 🟢

```gherkin
Cenário: Modo desacoplado quando engine maduro disponível
  Dado que ARCHITECTURE.md declara stack "Python 3.12 + Poetry"
  E que cookiecutter está disponível no PATH
  Quando /project-setup é invocado sem --mode
  Então o engine cookiecutter é selecionado e invocado
  E o manifesto pyproject.toml é gerado
  E o poetry.lock é gerado e commitado junto ao pyproject.toml
  E .gitignore inclui __pycache__/ mas NÃO inclui poetry.lock
  E o commit inicial usa /commit-soap --inline com Refs: ARCHITECTURE.md

Cenário: Modo monolítico declarado quando engine ausente
  Dado que ARCHITECTURE.md declara stack incomum sem engine de scaffolding maduro
  Quando /project-setup é invocado
  Então modo monolítico é declarado explicitamente em mensagem ao usuário
  E os critérios de aceitação E saída são listados (não silenciosos)
  E npm init / poetry init / cargo init / etc é executado pelo orquestrador-instância
  E manifesto + lock são commitados no mesmo commit (RN Gestão Determinística)
  E commit inicial usa /commit-soap --inline

Cenário: --check valida conformidade
  Dado que projeto já passou por /project-setup
  Quando /project-setup --check é invocado
  Então o relatório telegráfico inclui:
    - Lock file presente: sim/não
    - Lock file bate com manifesto: sim/não
    - .gitignore apropriado para stack: sim/não
    - Estrutura mínima presente: sim/não
  E qualquer "não" gera item para correção (ou /project-setup --refresh)

Cenário: --refresh ajusta divergência sem recriar tudo
  Dado que /project-init --refresh modificou ARCHITECTURE.md (mudança de gerenciador)
  Quando /project-setup --refresh é invocado
  Então a divergência é detectada (manifesto antigo vs. novo gerenciador declarado)
  E o ajuste é cirúrgico (migração de package.json para pyproject.toml conforme novo gerenciador)
  E o commit usa /commit-soap --inline com A+P descrevendo a refresh
```

## Priorização MoSCoW

### Must (v0.1.0)

- ✅ Receber `ARCHITECTURE.md` como input e abortar se ausente
- ✅ Modo desacoplado com lista de engines candidatos por stack
- ✅ Modo monolítico declarado com critérios de aceitação + saída
- ✅ Enforcement das regras de Gestão Determinística (lock commitado, manifesto+lock juntos)
- ✅ Invocação de `/commit-soap --inline` para selo inicial

### Should (v0.2.0+)

- 🔵 `--check` operacional com relatório telegráfico estruturado
- 🔵 `--refresh` cirúrgico (detectar divergência ARCHITECTURE.md vs. disco)
- 🔵 Lista de engines de scaffolding por stack expandida (mais opções para Go, Elixir, etc.)

### Could (futuro)

- 🟡 Auto-detecção de engine apropriado baseada em disponibilidade no PATH
- 🟡 Fallback gracioso (engine X não disponível → tentar Y → último recurso monolítico)

### Won't (out of scope)

- 🔴 Implementar engine de scaffolding próprio (anti-padrão de P-8 — delegar a engines maduros existentes)
- 🔴 Resolver dependências entre projetos (escopo de gerenciador, não desta skill)

## Padrões transversais aplicados

### "Modo monolítico declarado com critério de saída" (padrão #7)

Paralelo direto à F6.a do MDCU. Mesmo padrão: nomear o atalho operacional, declarar critérios de aceitação + saída, evitar transformar exceção em regra silenciosa.

### "Regras canônicas vigem em ambos os modos" (padrão #8)

Regras de Gestão Determinística (declaradas em `project-init`) vigoram em desacoplado E monolítico. Engine externo respeita; orquestrador-instância em monolítico respeita. Princípio é da regra, não do enforcer.

### "Skill desacoplada de sessão MDCU" (padrão #9)

Selo via `commit-soap --inline` cumpre P-9: commit inicial é marco longitudinal arbitrário, não fechamento de sessão MDCU. Reuso da skill `commit-soap` em contexto não-MDCU.

## Code-Spec Matrix

| Arquivo | Componente lógico | Cobertura |
|---|---|---|
| `project-setup/SKILL.md:1-3` | Frontmatter (version 0.1.0, author, description) | 🟢 |
| `project-setup/SKILL.md:6-15` | Fundamento + analogia clínica | 🟢 |
| `project-setup/SKILL.md:18-30` | Posição no workflow (project-init → project-setup → MDCU) | 🟢 |
| `project-setup/SKILL.md:32-37` | Input obrigatório (ARCHITECTURE.md) | 🟢 |
| `project-setup/SKILL.md:40-48` | Artefatos materializados | 🟢 |
| `project-setup/SKILL.md:50-101` | Modos de operação (desacoplado / monolítico declarado) | 🟢 |
| `project-setup/SKILL.md:103-117` | Regras canônicas de Gestão Determinística (herdadas) | 🟢 |
| `project-setup/SKILL.md:119-134` | Selo via commit-soap desacoplado | 🟢 |
| `project-setup/SKILL.md:136-145` | Comandos `/project-setup` | 🟢 |
| `project-setup/SKILL.md:147-156` | Regras de operação | 🟢 |
| `project-setup/SKILL.md:158-163` | Integração com outras skills | 🟢 |

## Lacunas 🔴

- **Engines de scaffolding ainda não-implementados como integração concreta:** v0.1.0 documenta candidatos mas não tem auto-invocação via subprocess (P-1: framework é markdown puro, sem JS) — cabe ao orquestrador-instância invocar manualmente
- **Versionamento de `ARCHITECTURE.md`:** mudanças via `--refresh` não são versionadas semver; fica para v2026.06+

## Status de release

- **v0.1.0** entregue em commit `1378d5e` (2026-04-27)
- **v1.0.0** prevista quando `--check` e `--refresh` forem operacionais com testes em projetos-cliente reais (release-train v2026.06+)
