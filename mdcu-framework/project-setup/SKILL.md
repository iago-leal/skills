---
name: project-setup
version: "0.1.0"
author: Iago Leal <github.com/iago-leal>
description: Materialização do contrato técnico extraído por `project-init` — recebe `ARCHITECTURE.md` como input e executa setup técnico em disco (manifesto de dependências, lock file determinístico, `.gitignore` da stack, commit inicial via `commit-soap` desacoplado). Invocada automaticamente ao final do `project-init`. Opera em **modo desacoplado** (delegando a engine de scaffolding maduro — cookiecutter, yeoman, plop, copier — quando disponível para a stack) ou em **modo monolítico declarado** (orquestrador-instância como engine ad-hoc, com critério de saída para modo desacoplado quando engine maduro existir). ATIVE SEMPRE que o usuário digitar /project-setup ou /project-setup --refresh, quando a skill `project-init` concluir geração de `ARCHITECTURE.md` e não houver setup técnico ainda materializado, ou quando mencionar "instalar contrato", "inicializar stack do projeto", "gerar lock file inicial". NÃO ative para reinstalação rotineira de dependências em projeto já existente — para isso use os comandos canônicos do projeto declarados no `ARCHITECTURE.md` (`install`).
---

# project-setup — Materialização do Contrato Técnico

## Fundamento

`project-init` extrai o contrato técnico (ARCHITECTURE.md). `project-setup` o **materializa em disco**: instala dependências declaradas, gera lock file determinístico, configura `.gitignore` adequado para a stack, e sela o setup com commit inicial via `commit-soap` desacoplado.

A separação é canônica (P-7 + P-8 em `framework/principles.md`):
- **`project-init`** = interface humana + extração de contrato. Não executa.
- **`project-setup`** = engine de materialização. Executa, mas em modo desacoplado quando há engine de scaffolding maduro disponível, ou em modo monolítico declarado quando não há.

**Analogia clínica:** `project-init` é a redação da prescrição (anamnese + plano terapêutico documentado). `project-setup` é a equipe de farmácia + enfermagem que executa a prescrição (dispensa medicamento, administra dose, registra). A separação é boa prática — o médico não dispensa o medicamento, o farmacêutico não escreve a prescrição.

---

## Posição no workflow

```
project-init (extrai contrato → ARCHITECTURE.md)
   ↓
project-setup (materializa)
   ├─ modo desacoplado: invoca engine de scaffolding (cookiecutter / yeoman / plop / copier)
   └─ modo monolítico: orquestrador-instância como engine ad-hoc (declarado, com critério de saída)
   ↓
commit-soap desacoplado (sela commit inicial — A+P inline ou de input estruturado)
   ↓
MDCU F1  →  F2 Escuta  →  ...
```

---

## Input

**`ARCHITECTURE.md`** na raiz do projeto, produzido por `/project-init`. Se ausente, aborta e orienta o usuário a invocar `/project-init` primeiro.

---

## Artefatos materializados

1. **Manifesto de dependências** declarado no `ARCHITECTURE.md` (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `composer.json`, etc.).
2. **Lock file determinístico** declarado no `ARCHITECTURE.md` — versões pinadas e reprodutíveis (regras canônicas em `project-init/SKILL.md` seção "Gestão Determinística de Dependências").
3. **`.gitignore`** apropriado para a stack — **nunca** inclui o lock file.
4. **Estrutura mínima de diretórios** (`src/`, `tests/`, `rsop/`, `docs/`) conforme convenções do `ARCHITECTURE.md`.
5. **Commit inicial** via `commit-soap` desacoplado — A+P inline com referência a `ARCHITECTURE.md`.

---

## Modos de operação

### Modo desacoplado (preferido quando engine plugado existe)

Para stacks com engine de scaffolding maduro disponível, `project-setup` **delega**:

| Stack | Engines candidatos |
|---|---|
| Python | cookiecutter (templates), copier (templates evolutivos) |
| JavaScript/TypeScript | create-next-app, create-vite, plop (templates customizados), yeoman |
| Rust | cargo-generate |
| Go | go templates customizados (não há cookiecutter idiomático maduro) |
| Multi-stack | yeoman, plop, copier |

**Operação no modo desacoplado:**
1. Identificar engine apropriado para a stack declarada no `ARCHITECTURE.md`.
2. Invocar engine com input mínimo (stack + nome do projeto + caminho).
3. Verificar que engine produziu manifesto + lock file conforme declarado.
4. Adicionar `.gitignore` se engine não gerou (raro), ou validar se gerou corretamente.
5. Verificar que o lock file declarado em `ARCHITECTURE.md` corresponde ao gerado.
6. Invocar `commit-soap` desacoplado para selar.

**Por que preferir desacoplado:** engines maduros encarnam boas práticas comunitárias; reduzem custo de manutenção do `project-setup`; cumprem P-8 estruturalmente.

### Modo monolítico declarado (exceção com critério de saída)

Quando **nenhum engine de scaffolding maduro está disponível** para a stack escolhida, ou quando custo de plugar engine externo > custo de execução direta, o `project-setup` opera como engine ad-hoc — ele mesmo executa `npm init`, `poetry init`, `cargo init`, etc.

**Critérios de aceitação do modo monolítico:**
- Stack incomum sem engine de scaffolding maduro.
- Projeto pequeno ou em fase exploratória onde cookiecutter/yeoman seria over-engineering.
- Adopter explicitamente prefere modo monolítico (decisão informada — F-3, RN-D-014).

**Critério de saída (quando migrar para modo desacoplado):**
- Stack ganha engine maduro (ex: cookiecutter passa a cobrir o caso).
- Projeto cresce e múltiplos colaboradores precisam reproduzir setup deterministicamente.
- Manutenção do "monolítico ad-hoc" vira gargalo cognitivo.

**Operação no modo monolítico:**
1. Executar `npm init` / `poetry init` / `cargo init` / `go mod init` / `bundle init` / etc. conforme stack.
2. Instalar dependências iniciais (se declaradas em `ARCHITECTURE.md`) — **gerando o lock file**.
3. Verificar que o lock file foi efetivamente criado e bate com a declaração do `ARCHITECTURE.md`.
4. Inicializar git (se ainda não inicializado).
5. Gerar `.gitignore` adequado para a stack (nunca incluir o lock file).
6. Criar estrutura mínima de diretórios.
7. Invocar `commit-soap` desacoplado para selar.

**Por que não esconder o modo monolítico:** F-3 do `framework/principles.md` exige decisão informada — adopter precisa saber que está no atalho, e qual é o caminho de saída. Modo silencioso transforma a tese P-8 em mito-aspiracional; modo declarado preserva-a operacional.

---

## Regras de Gestão Determinística de Dependências (vigoram em ambos os modos)

> Regras canônicas declaradas em `project-init/SKILL.md` seção "Gestão Determinística de Dependências" são vinculantes aqui também. **`project-setup` é o enforcement efetivo dessas regras.**

Sumário operacional:
- Lock file commitado, **sempre**.
- Lock file **nunca** em `.gitignore`.
- Manifesto + lock file no **mesmo commit**.
- Versões flutuantes no manifesto OK desde que lock congele exato.
- CI usa `npm ci` / `poetry install --no-update` / `cargo build --locked` / equivalente.
- Auditoria periódica é responsabilidade do regime longitudinal (`mdcu-seg auditoria`).

---

## Selo via commit-soap desacoplado

Ao final da materialização, `project-setup` invoca `commit-soap` (desacoplado, ver `commit-soap/SKILL.md`) com A+P inline:

```
A: Projeto sem contrato técnico materializado — sem lock file, sem reprodutibilidade
P: ARCHITECTURE.md materializado: [manifesto] + [lock file] + .gitignore + estrutura inicial; modo de execução: [desacoplado via <engine> | monolítico]

Refs: ARCHITECTURE.md
```

**Por que via `commit-soap` desacoplado:** P-9 (acompanhamento longitudinal transversal) — todo marco longitudinal usa o mesmo selo. Inicial commit é marco; SOAP de sessão MDCU é marco; release é marco. Mesma skill, mesma forma.

---

## Uso com `/project-setup`

- `/project-setup` — materializa o setup com base no `ARCHITECTURE.md` da raiz. Aborta se `ARCHITECTURE.md` não existe (orienta `/project-init` primeiro).
- `/project-setup --refresh` — reaplica setup após `/project-init --refresh` que tenha mudado stack/gerenciador. Detecta divergência entre `ARCHITECTURE.md` e estado em disco; ajusta.
- `/project-setup --check` — valida se o projeto atual está em conformidade: lock file presente? bate com manifesto? `.gitignore` apropriado para a stack? Retorna relatório telegráfico.
- `/project-setup --mode desacoplado --engine <nome>` — força modo desacoplado com engine específico (default tenta detectar).
- `/project-setup --mode monolitico` — força modo monolítico (default escolhe baseado em disponibilidade de engine).

---

## Regras de operação

1. **Sem `ARCHITECTURE.md` válido, aborta.** Não improvisar contrato — invocar `/project-init` primeiro.
2. **Modo monolítico é exceção declarada.** Não silencioso. Adopter precisa saber em qual modo está e qual é o critério de saída.
3. **Lock file é vinculante** — regras canônicas de `project-init` "Gestão Determinística de Dependências" são enforcement efetivo aqui.
4. **Commit inicial via `commit-soap` desacoplado** — não usar `git commit` direto. Mesmo selo de qualquer marco longitudinal (P-9).
5. **Esta skill executa.** É o engine de materialização. Diferente de `project-init` (que só extrai contrato).
6. **`--refresh` é cirúrgico.** Não recria o que já existe; ajusta divergências entre `ARCHITECTURE.md` e disco.

---

## Integração com outras skills

| Skill | Integração |
|-------|------------|
| `project-init` | Recebe input do contrato extraído (`ARCHITECTURE.md`). `project-init` invoca `project-setup` ao final da fase 7. |
| `commit-soap` | Invocado pelo `project-setup` para selar commit inicial (modo desacoplado). |
| `mdcu` | F1 do MDCU exige `project-init` **e** `project-setup` concluídos antes de F2. |
| `rsop` | `dados_base.md` referencia `ARCHITECTURE.md`; `project-setup` não toca `rsop/`. |
| `mdcu-seg` | Auditoria periódica de dependências instaladas (regime longitudinal — `mdcu-seg auditoria`). |
