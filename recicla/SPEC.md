# SPEC.md — `recicla`

> **Propósito deste documento.** Esta especificação é suficiente para reconstruir a skill `recicla` em qualquer ambiente, por qualquer agente capaz de operar a skill `skill-creator`. Entregue este SPEC.md ao agente junto com o comando `/skill-creator`. O resultado deve ser uma skill funcionalmente equivalente à descrita aqui — não necessariamente byte-a-byte idêntica, mas **operacionalmente intercambiável**: mesmos comandos, mesmos schemas, mesmas invariantes, mesma saída para mesmo input.

---

## 1. Identidade

| Campo | Valor |
|---|---|
| **Nome** | `recicla` |
| **Versão da spec** | `1.1.0` |
| **Schemas** | `index.json` v1.1, `manifest.json` v1.1, declaração de bundle v1.0 |
| **Tipo** | Skill agnóstica de modelo, determinística |
| **Dependências de runtime** | Python ≥ 3.9, stdlib apenas |
| **Dependências de tooling** | Nenhuma. Sem libs externas, sem chamadas de rede, sem LLM. |
| **Plataformas testadas** | Linux, macOS. Windows funciona mas não é alvo primário. |

---

## 2. Propósito declarado

Permitir que um usuário identifique e migre componentes reutilizáveis (funções, prompts, templates, schemas, configurações, snippets) entre projetos, mediada por uma biblioteca global de componentes (Library) com índice consultável por agentes de IA. Operação bidirecional (workspace ↔ library) com proteção determinística contra duplicatas.

**Não-objetivos** (escopo explicitamente recusado):
- Refatoração intra-projeto.
- Análise semântica do conteúdo dos componentes.
- Recomendação baseada em embeddings ou LLM.
- Versionamento semântico tipo SemVer dos componentes.
- Resolução de dependências entre componentes.

---

## 3. Modelo conceitual

### 3.1 Entidades

| Entidade | Descrição |
|---|---|
| **Workspace** | Diretório de trabalho do projeto atual. Tem `.recicla/manifest.json` se já interagiu com a skill. |
| **Library** | Diretório global de componentes apontado por `$RECICLA_LIBRARY`. Único por usuário. |
| **Componente** | Arquivo único no filesystem, com identidade dada pelo SHA-256 do conteúdo. |
| **Bundle** | Composição nomeada de N componentes (N ≥ 1) com layout interno declarado. Identidade derivada de nome + composição (§3.5). |
| **Manifesto local** | `.recicla/manifest.json` na raiz do workspace. Registra todo componente extraído ou injetado, e todo bundle injetado. |
| **Declaração de bundle** | `.recicla/bundles/<name>.json` na raiz do workspace. Fonte declarativa de um bundle candidato; consumida por `bundle-extract`. |
| **Index** | `index.json` na raiz da Library. Fonte de verdade dos componentes E dos bundles catalogados. |
| **INDEX.md** | View do `index.json` legível por humanos e agentes. Regenerada, nunca editada. |

### 3.2 Identidade de componente

```
component_id := "c-" + sha256(content)[:8]
```

Identidade derivada do conteúdo, não do nome ou caminho. Dois arquivos com mesmo conteúdo têm mesmo `component_id`. Modificação no arquivo invalida o ID — passa a ser componente novo (esse é o critério de drift).

### 3.3 Relações

```
Workspace --(extract)--> Library                     (granular, 1 arquivo)
Library --(inject)--> Workspace                      (granular, 1 arquivo)
Workspace.bundle_decl --(bundle-extract)--> Library  (composição, N membros)
Library --(bundle-inject)--> Workspace               (composição, N membros)
Workspace.manifest registers ALL directions
Library.index aggregates ALL components AND ALL bundles (active + superseded)
```

### 3.4 Categorias de componente

Conjunto fechado:

```
prompt | template | function | schema | snippet | config
```

Mapeamento default por diretório de origem:

| Diretório | Categoria |
|---|---|
| `prompts/` | `prompt` |
| `templates/` | `template` |
| `lib/`, `utils/`, `helpers/`, `functions/` | `function` |
| `schemas/`, `types/` | `schema` |
| `configs/`, `config/` | `config` |
| `components/`, `shared/`, qualquer outro | `snippet` |

Usuário pode sobrescrever via header `@recicla:category`.

Bundles **não têm categoria** — a categoria é propriedade dos componentes individuais. Bundles agrupam por intenção/topologia, não por tipo.

### 3.5 Identidade de bundle

```
bundle_id := "b-" + sha256(canonical)[:8]
canonical := name + "|" + ",".join(sorted([
    f"{member.component_id}:{member.bundle_relpath}"
    for member in members
]))
```

Três consequências:

1. **Mudou nome** → outro bundle. Nome é semântica.
2. **Mudou conjunto de membros** (`component_id` muda ou membro removido/adicionado) → outro bundle.
3. **Mudou layout interno** (`bundle_relpath` de algum membro) → outro bundle. Layout faz parte do ativo (imports relativos dependem dele).
4. **Não mudou** se algum membro foi atualizado na Library com novo `component_id` — o bundle pina nos IDs antigos. Atualizar é operação explícita: re-`bundle-extract` com composição diferente registra novo `bundle_id` e marca o anterior como `superseded_by: <novo_id>`.

Bundles são **imutáveis na Library**. Histórico preservado via `superseded_by`.

### 3.6 Relação bundle ↔ componente

- Bundle **referencia** componentes pelo `component_id`. Não os duplica nem os contém.
- Bundle **não invalida** a injeção/extração granular dos seus membros: cada membro continua sendo um componente normal e pode ser injetado isoladamente via `inject`.
- Membro de bundle **deve existir** como componente na Library no momento do `bundle-extract` (o comando exige pré-extração; flag `--extract-members` automatiza).

---

## 4. Estrutura de arquivos

### 4.1 Skill (entregável)

```
recicla/
├── SKILL.md
├── SPEC.md                     # este arquivo
├── README.md                   # instalação e configuração
├── reference/
│   ├── schemas.md
│   ├── eligibility_criteria.md
│   └── operations.md
└── scripts/
    └── recicla.py
```

### 4.2 Library (gerada em runtime)

```
$RECICLA_LIBRARY/
├── index.json                  # fonte de verdade (componentes + bundles)
├── INDEX.md                    # view regenerada (componentes + bundles)
└── components/
    ├── prompts/
    ├── templates/
    ├── functions/
    ├── schemas/
    ├── snippets/
    └── configs/
```

Bundles **não** têm diretório dedicado: vivem apenas no `index.json` (campo `bundles[]`) e no `INDEX.md` (seção Bundles). Os arquivos referenciados continuam em `components/<plural>/` como qualquer outro componente.

### 4.3 Workspace (gerado em runtime)

```
<workspace>/
└── .recicla/
    ├── manifest.json           # registro local de operações
    └── bundles/
        ├── rag-pipeline.json   # declarações de bundle (autoria do usuário)
        └── ...
```

Declarações de bundle (`.recicla/bundles/*.json`) são **artefatos de autoria** — versionáveis em git, editáveis manualmente. São consumidas por `bundle-extract` e permanecem no workspace após o registro (servem como fonte para re-extração e como sinal para `audit`).

---

## 5. Schemas formais

### 5.1 `index.json` (schema v1.1)

```json
{
  "version": "1.1",
  "library_path": "/home/user/recicla-library",
  "updated_at": "2026-05-07T14:30:00Z",
  "components": [
    {
      "component_id": "c-a3f9b2e1",
      "name": "jwt-validator",
      "category": "function",
      "tags": ["auth", "jwt", "security"],
      "description": "Valida JWT contra issuer e audience configuráveis.",
      "language": "python",
      "library_relpath": "components/functions/jwt-validator.py",
      "sha256": "8f3cab...full_hash",
      "size_bytes": 2148,
      "added_at": "2026-04-10T09:15:00Z",
      "added_from_workspace": "/abs/path/to/origin"
    }
  ],
  "bundles": [
    {
      "bundle_id": "b-678bc190",
      "name": "rag-pipeline",
      "added_at": "2026-05-07T16:30:00Z",
      "added_from_workspace": "/abs/path/to/origin",
      "description": "Pipeline RAG canônico: transcribe → chunk → index → query → generate.",
      "tags": ["rag", "llm", "pipeline"],
      "entrypoint": "pipeline/retriever.py",
      "members": [
        {"component_id": "c-a9e3ffaa", "bundle_relpath": "pipeline/transcriber.py", "role": "transcribe"},
        {"component_id": "c-1e98127f", "bundle_relpath": "pipeline/chunker.py",     "role": "chunk"},
        {"component_id": "c-2c6c310f", "bundle_relpath": "pipeline/vector_db.py",   "role": "index"},
        {"component_id": "c-f281aea8", "bundle_relpath": "pipeline/retriever.py",   "role": "query"},
        {"component_id": "c-6eaeaf9d", "bundle_relpath": "pipeline/generator.py",   "role": "generate"}
      ],
      "superseded_by": null
    }
  ]
}
```

**Invariantes (componentes):**
- `component_id == "c-" + sha256[:8]`
- `category ∈ {prompt, template, function, schema, snippet, config}`
- `library_relpath` é relativo ao `library_path`
- Dois componentes não compartilham `component_id`
- `sha256` calculado sobre o arquivo bruto, sem normalização

**Invariantes (bundles):**
- `bundle_id == "b-" + sha256(canonical)[:8]` (§3.5 e §6.4)
- `name` casa `^[a-z0-9][a-z0-9-]{0,63}$`
- `members[].component_id` deve existir em `components[]` no momento do registro (`audit` reporta `bundle_member_missing` se quebrado)
- `members[].bundle_relpath` é único dentro do bundle, relativo, sem `..`
- `entrypoint`, se presente, casa exatamente um `members[].bundle_relpath`
- `superseded_by` aponta para outro `bundle_id` do mesmo `name` ou é `null`
- Para qualquer `name`, no máximo um bundle ativo (`superseded_by: null`); demais ficam como histórico imutável.

### 5.2 `manifest.json` (workspace local, schema v1.1)

```json
{
  "version": "1.1",
  "workspace_path": "/abs/path/to/workspace",
  "created_at": "2026-05-07T14:00:00Z",
  "updated_at": "2026-05-07T14:05:23Z",
  "components": [
    {
      "component_id": "c-a3f9b2e1",
      "library_relpath": "components/functions/jwt-validator.py",
      "workspace_relpath": "src/auth/jwt-validator.py",
      "direction": "extracted",
      "sha256_at_op": "8f3cab...",
      "timestamp": "2026-05-07T14:05:23Z",
      "via_bundle": null
    },
    {
      "component_id": "c-a9e3ffaa",
      "library_relpath": "components/functions/transcriber.py",
      "workspace_relpath": "lib/audio/pipeline/transcriber.py",
      "direction": "injected",
      "sha256_at_op": "a9e3ffaa...",
      "timestamp": "2026-05-07T16:35:00Z",
      "via_bundle": "b-678bc190"
    }
  ],
  "bundles": [
    {
      "bundle_id": "b-678bc190",
      "name": "rag-pipeline",
      "direction": "injected",
      "members_count": 5,
      "target_root": "lib/audio",
      "remap": {},
      "timestamp": "2026-05-07T16:35:00Z"
    }
  ]
}
```

**Invariantes (componentes):**
- `direction ∈ {extracted, injected}`
- `sha256_at_op` é o hash no momento da operação — pode divergir do estado atual (drift detectável por `audit`)
- `via_bundle` é `null` para operações granulares (`extract`/`inject`) e `<bundle_id>` para membros materializados via `bundle-inject`

**Invariantes (bundles):**
- `direction == "injected"` (não há `bundle-extract` rastreado no manifest local — extração é registrada apenas no Index global)
- A combinação `(bundle_id, target_root, normalized(remap))` é única no manifest — base da idempotência (I3 estendida).

### 5.3 Declaração de bundle (`.recicla/bundles/<name>.json`, schema v1.0)

Artefato de autoria. Editável manualmente. Versionável em git. Consumido por `bundle-extract`.

```json
{
  "version": "1.0",
  "name": "rag-pipeline",
  "description": "Pipeline RAG canônico: transcribe → chunk → index → query → generate.",
  "tags": ["rag", "llm", "pipeline"],
  "entrypoint": "pipeline/retriever.py",
  "members": [
    {
      "workspace_relpath": "src/processing/transcriber.py",
      "bundle_relpath": "pipeline/transcriber.py",
      "role": "transcribe"
    },
    {
      "workspace_relpath": "src/processing/chunker.py",
      "bundle_relpath": "pipeline/chunker.py",
      "role": "chunk"
    }
  ]
}
```

**Validação (`validate_bundle_decl`):**
- `name`: string casa `^[a-z0-9][a-z0-9-]{0,63}$`
- `description`: string (opcional, default `""`)
- `tags`: lista de strings
- `entrypoint`: string ou `null`. Se string, casa um `members[].bundle_relpath`
- `members`: lista não-vazia. Sem duplicatas em `workspace_relpath` nem `bundle_relpath`
- `members[].bundle_relpath`: relativo, sem `..`, sem prefixo absoluto
- `members[].role`: string (opcional)

### 5.4 Header de metadados em arquivo de componente

Sintaxe livre de comentário (cada linha pode ter qualquer prefixo de comentário antes do `@recicla:`):

```
@recicla:reusable
@recicla:name <nome-canônico>            # opcional
@recicla:category <categoria>            # opcional, ∈ categorias fechadas
@recicla:tags <tag1>,<tag2>,<tag3>       # opcional, comma-separated
@recicla:description <texto livre>       # opcional, mesma linha
```

Regex de parsing (referência implementada):
```
^\s*[^\w\n]*\s*@recicla:(\w+)\s*(.*?)\s*$
```

(Permissivo: aceita `@recicla:reusable` sem valor; chave sem espaço também casa.)

### 5.5 Saídas JSON dos comandos

Todo subcomando aceita `--json` e produz envelope:

```json
{
  "command": "<command>",
  "version": "1.1.0",
  "ok": true,
  "data": { ... },
  "errors": []
}
```

Schemas resumidos abaixo. Para detalhes, ver `reference/operations.md` e `reference/schemas.md`.

**`scan` data:**
```json
{
  "workspace_path": "/abs",
  "library_path": "/abs",
  "scanned_files": 142,
  "candidates": [
    {
      "path": "src/utils/jwt.py",
      "size_bytes": 2148,
      "category_inferred": "function",
      "has_marker": true,
      "in_canonical_dir": true,
      "language_inferred": "python",
      "metadata_from_header": {"name": "...", "tags": [...], "description": "...", "category": "function"},
      "sha256": "..."
    }
  ],
  "skipped": [
    {"path": "...", "skip_reason": "duplicate_hash_in_library", "existing_component_id": "c-..."}
  ],
  "bundle_candidates": [
    {"path": ".recicla/bundles/rag-pipeline.json", "name": "rag-pipeline", "valid": true, "errors": [], "members_count": 5}
  ]
}
```

**`extract` data:**
```json
{
  "extracted": [
    {"component_id": "c-...", "library_relpath": "components/functions/jwt.py", "workspace_relpath": "src/utils/jwt.py", "name": "jwt"}
  ],
  "skipped": [{"path": "...", "reason": "duplicate_hash_in_library", "existing_component_id": "c-..."}],
  "index_updated": true,
  "manifest_updated": true,
  "index_md_regenerated": true
}
```

**`suggest` data:**
```json
{
  "library_path": "/abs",
  "query": {"tags": ["auth"], "language": "python", "category": null, "type": "all", "auto_inferred": false},
  "matches": [
    {"type": "component", "component_id": "c-...", "name": "...", "score": 0.66, "tags": [...], "category": "function", "language": "python", "description": "...", "library_relpath": "...", "already_in_workspace": false},
    {"type": "bundle", "bundle_id": "b-...", "name": "rag-pipeline", "score": 0.14, "tags": [...], "members_count": 5, "description": "...", "category": null, "language": null, "already_in_workspace": false}
  ]
}
```

**`inject` data:**
```json
{
  "component_id": "c-...",
  "name": "...",
  "source_library_path": "...",
  "destination_workspace_path": "...",
  "status": "ok | already_injected | identical_file_at_destination | conflict",
  "manifest_updated": true
}
```

**`audit` data:**
```json
{
  "library_path": "/abs",
  "workspace_path": "/abs|null",
  "summary": {"info": 0, "warn": 0, "error": 0},
  "findings": [
    {"severity": "warn|error|info", "kind": "<finding_kind>", "component_id": "c-...|null", "bundle_id": "b-...|null", "details": "..."}
  ]
}
```

Finding kinds (exhaustivo):
- `library_file_missing` (error) — `index.json` referencia arquivo ausente.
- `library_hash_drift` (error) — sha256 do arquivo na Library diverge do registrado.
- `library_duplicate_hash` (error) — dois componentes com mesmo sha256.
- `index_md_stale` (info) — `INDEX.md` mais antigo que `index.json` (mtime).
- `manifest_orphan` (warn) — manifest registra `workspace_relpath` que não existe.
- `workspace_hash_drift` (warn) — arquivo no workspace foi modificado desde a operação.
- `injected_component_removed_from_library` (warn) — componente injetado sumiu do Index.
- `bundle_member_missing` (error) — bundle ativo referencia `component_id` ausente do Index.
- `bundle_definition_drift` (warn) — `.recicla/bundles/<name>.json` resolveria para `bundle_id` não-registrado.
- `injected_bundle_removed_from_library` (warn) — bundle injetado sumiu do Index.

**`render-index` data:**
```json
{
  "library_path": "/abs",
  "index_md_path": "/abs/INDEX.md",
  "components_rendered": 12,
  "categories_with_components": ["function", "prompt"]
}
```

**`bundle-init` data:**
```json
{
  "declaration_path": "/abs/.recicla/bundles/rag-pipeline.json",
  "declaration_relpath": ".recicla/bundles/rag-pipeline.json",
  "decl": { ... full declaration JSON ... }
}
```

**`bundle-extract` data:**
```json
{
  "bundle_id": "b-...",
  "name": "rag-pipeline",
  "members_count": 5,
  "registered": true,
  "status": "registered | already_registered",
  "auto_extracted": ["src/processing/foo.py"],
  "superseded_id": "b-... | null"
}
```

**`bundle-inject` data:**
```json
{
  "bundle_id": "b-...",
  "name": "rag-pipeline",
  "target_root": "lib/audio",
  "members_count": 5,
  "status": "ok | ok_overwritten | already_injected | conflict",
  "injected": [
    {"component_id": "c-...", "bundle_relpath": "pipeline/x.py", "destination_workspace_relpath": "lib/audio/pipeline/x.py"}
  ]
}
```

(Em conflito sem `--force`, retorna `ok: false` e `data.conflicts: [{dest_rel, existing_hash, component_hash}]`.)

---

## 6. Heurísticas determinísticas

### 6.1 Elegibilidade para extração (operação `scan`)

```
file_is_candidate(f, workspace, library) :=
  not is_excluded_path(f)            # .git, node_modules, etc.
  AND size(f) <= max_size            # default 50KB
  AND not is_binary(f)               # null byte nos primeiros 8KB
  AND (has_marker(f) OR is_in_canonical_dir(f))
  AND sha256(f) not in workspace.manifest.components[].sha256_at_op
  AND sha256(f) not in library.index.components[].sha256
```

`is_excluded_path` (lista fixa, ordenada):
```
.git/, .svn/, .hg/, node_modules/, __pycache__/, .pytest_cache/, .mypy_cache/,
dist/, build/, target/, .next/, .nuxt/, .cache/, .venv/, venv/, env/,
.recicla/, .DS_Store, *.lock
```

(Note que `.recicla/` está na lista de exclusões — declarações de bundle são detectadas por varredura explícita de `.recicla/bundles/`, não pelo walk geral.)

`is_in_canonical_dir` (qualquer ancestral do path):
```
lib/, utils/, shared/, components/, helpers/, templates/, prompts/,
schemas/, snippets/, configs/, config/, functions/, types/
```

### 6.2 Sugestão (operação `suggest`)

Modo explícito: `--tags a,b,c [--language X] [--category Y] [--type all|component|bundle]`. Filtra `index.json` por interseção exata.

Modo automático: `--auto`. Infere tags do workspace:
1. Lê `package.json` → `dependencies` + `devDependencies` keys (filtra a top-15 mais comuns).
2. Lê `pyproject.toml` → `[tool.poetry.dependencies]` ou `[project.dependencies]`.
3. Lê `Cargo.toml` → `[dependencies]`.
4. Lê `README.md` → tokeniza primeiros 200 caracteres, filtra stopwords.
5. Lê `ARCHITECTURE.md` se presente → tokeniza, filtra stopwords.

Resultado: conjunto de tags inferidas. Score de afinidade Jaccard:

```
score(item, query_tags) = |item.searchable ∩ query_tags| / |item.searchable ∪ query_tags|
```

onde `item.searchable` para componentes é `tags`; para bundles é `tags ∪ {role for each member if role}`.

Empate desempata por `added_at` mais recente.

`--language` e `--category` são filtros que se aplicam apenas a componentes; quando passados sem `--type bundle`, removem bundles do conjunto de candidatos (categoria/linguagem não fazem sentido para bundles).

### 6.3 Detecção de duplicatas

Em **extração**:
1. Calcular hash do arquivo candidato.
2. Se hash em `index.json.components[].sha256` → skip com `reason: duplicate_hash_in_library`.
3. Se hash em `manifest.json.components[].sha256_at_op` → skip com `reason: already_processed_in_workspace`.

Em **injeção (granular)**:
1. Se `(component_id, workspace_relpath)` já em `manifest.json.components[]` com `direction: injected` → `status: already_injected`.
2. Se arquivo destino existe e hash bate com componente da Library → `status: identical_file_at_destination`.
3. Se arquivo destino existe e hash NÃO bate → `status: conflict`, exigir `--force`.

Em **bundle-extract**:
1. Calcula `bundle_id` determinístico a partir da declaração resolvida.
2. Se `bundle_id` já em `index.json.bundles[].bundle_id` → `status: already_registered`.
3. Se `name` já tem bundle ativo (`superseded_by: null`) com `bundle_id` diferente → marca o anterior `superseded_by: <new_id>` e registra o novo.

Em **bundle-injeção**:
1. Se `(bundle_id, target_root, normalized(remap))` já em `manifest.json.bundles[]` com `direction: injected` → `status: already_injected`.
2. Pré-checa colisão entre destinos do plano (dois `bundle_relpath` distintos mapeando para mesmo destino após `target_root`/`remap`). Erro: exit 2.
3. Pré-checa cada destino contra arquivo existente: se hash diverge, `status: conflict`, exigir `--force`.
4. Cópia atômica: se qualquer membro falhar pós-cópia (hash mismatch ou I/O), reverte todos os anteriores (restaura conteúdo prévio salvo em memória ou remove arquivos novos).

### 6.4 Cálculo de `bundle_id`

```
canonical(name, members) :=
    name + "|" + ",".join(sorted([
        f"{m.component_id}:{m.bundle_relpath}" for m in members
    ]))

bundle_id := "b-" + sha256(canonical.encode("utf-8"))[:8]
```

Pseudocódigo:
```python
def compute_bundle_id(name: str, members: list[dict]) -> str:
    parts = sorted(
        f"{m['component_id']}:{m['bundle_relpath']}" for m in members
    )
    canonical = name + "|" + ",".join(parts)
    return "b-" + sha256(canonical.encode("utf-8")).hexdigest()[:8]
```

Implicações:
- Função pura. Mesmo `(name, members)` → mesmo `bundle_id` em qualquer máquina, qualquer linguagem.
- `members` é serializado **ordenado** pelo par `f"{component_id}:{bundle_relpath}"` para que a ordem da declaração local não afete o ID.
- `role` **não** entra no cálculo — é metadado consultivo, mudar role não muda identidade.
- `description`, `tags`, `entrypoint` **não** entram no cálculo — também metadados.
- Se o usuário corrige um typo em `description`, o `bundle_id` não muda. Se ele troca um `bundle_relpath`, muda.

---

## 7. Operações — contratos formais

### 7.1 `scan`

```
recicla.py scan --workspace <path> --library <path> [--json] [--max-size <bytes>]
```

- Pré-condição: `--library` existe (ou cria estrutura mínima).
- Pré-condição: `--workspace` existe.
- Pós-condição: nenhum arquivo modificado. Operação read-only.
- Exit code: 0 mesmo sem candidatos.

### 7.2 `extract`

```
recicla.py extract --component <path> [--component <path>...] --workspace <path> --library <path> [--json]
```

- Pré-condição: cada `--component` é caminho absoluto ou relativo ao workspace, e existe.
- Pré-condição: hash de cada componente passa pelos filtros de duplicata.
- Pós-condição: arquivo copiado para `<library>/components/<category>/<name>.<ext>`. Conflito de nome resolvido com sufixo `-<short_hash>`.
- Pós-condição: entrada adicionada em `index.json`.
- Pós-condição: entrada adicionada em `manifest.json` (criando se ausente).
- Pós-condição: `INDEX.md` regenerado.
- Exit code: 0 se ao menos um extraído com sucesso, 1 se todos falharam.

### 7.3 `suggest`

```
recicla.py suggest --library <path> [--workspace <path>] (--tags <csv> | --auto) [--language <lang>] [--category <cat>] [--top <N>] [--json]
```

- Pré-condição: `--library` existe e tem `index.json` válido.
- Default `--top`: 10.
- Operação read-only.
- Exit code: 0 sempre, mesmo com zero matches.

### 7.4 `inject`

```
recicla.py inject (--id <component_id> | --library-relpath <path>) --library <path> --workspace <path> --target <relpath> [--force] [--json]
```

- Pré-condição: componente existe na Library.
- Pré-condição: `--target` é relativo à raiz do workspace.
- Pós-condição: arquivo copiado de Library para `<workspace>/<target>`.
- Pós-condição: entrada adicionada em `manifest.json` com `direction: injected`.
- Sem efeito sobre `index.json` ou `INDEX.md`.
- Exit code: 0 ok, 2 conflito sem `--force`.

### 7.5 `audit`

```
recicla.py audit --workspace <path> --library <path> [--json]
```

- Operação read-only.
- Exit code: 0 sem findings, 1 com `warn`, 2 com `error`.

### 7.6 `render-index`

```
recicla.py render-index --library <path>
```

- Pré-condição: `index.json` válido.
- Pós-condição: `INDEX.md` reescrito a partir de `index.json` (componentes + bundles ativos).
- Idempotente (módulo timestamp do header).
- Exit code: 0.

### 7.7 `bundle-init`

```
recicla.py bundle-init --name <slug> --members <csv> [--workspace <path>]
                       [--description <text>] [--tags <csv>] [--force] [--json]
```

- Pré-condição: `--workspace` é diretório válido.
- Pré-condição: `--name` casa `^[a-z0-9][a-z0-9-]{0,63}$`.
- Pré-condição: cada path em `--members` é relativo, dentro do workspace, e existe como arquivo.
- Pré-condição: `--workspace/.recicla/bundles/<name>.json` não existe (a menos que `--force`).
- Pós-condição: cria `.recicla/bundles/<name>.json` com template:
  - `bundle_relpath` inferido como `basename` do membro; conflitos desempatam com `<parent>/<basename>`.
  - `role` vazio. Usuário edita.
  - `entrypoint: null`. Usuário edita.
- **Não toca a Library.** Comando offline; pode rodar sem `RECICLA_LIBRARY` configurado.
- Exit code: 0 ok, 1 input inválido, 2 conflito (já existe sem `--force`).

### 7.8 `bundle-extract`

```
recicla.py bundle-extract --name <slug> [--workspace <path>] [--library <path>]
                          [--extract-members] [--max-size <bytes>] [--json]
```

- Pré-condição: `.recicla/bundles/<name>.json` existe e passa em `validate_bundle_decl`.
- Pré-condição: cada `members[].workspace_relpath` existe no workspace.
- Pré-condição: cada membro tem componente correspondente na Library (resolvido por `sha256(workspace_file)` no Index).
  - Sem `--extract-members`: se algum membro não está na Library, erro com lista de pendências.
  - Com `--extract-members`: extrai membros pendentes via `cmd_extract` interna antes de registrar.
- Operação:
  1. Resolve cada membro para `component_id` via hash.
  2. Calcula `bundle_id` determinístico (§6.4).
  3. Idempotência: se `bundle_id` já no Index → `status: already_registered`, retorna 0 sem mudanças.
  4. Se `name` já tem bundle ativo com outro `bundle_id` → marca o anterior `superseded_by: <new_id>`.
  5. Adiciona novo bundle ao `index.json.bundles[]`.
  6. Regenera `INDEX.md`.
- Pós-condição: `index.json` atualizado, `INDEX.md` regenerado. **Não modifica `manifest.json` local.**
- Exit code: 0 ok, 1 input ou pré-condição inválida.

### 7.9 `bundle-inject`

```
recicla.py bundle-inject (--id <bundle_id> | --name <slug>) [--library <path>]
                         [--workspace <path>] [--target-root <relpath>]
                         [--remap <orig=new>]... [--force] [--allow-superseded] [--json]
```

- Pré-condição: bundle existe no Index (busca por `--id` ou `--name`).
- Pré-condição: bundle não está com `superseded_by` (a menos que `--allow-superseded`).
- Pré-condição: todos os `members[].component_id` existem no Index e seus arquivos na Library batem com sha256 (sem drift).
- Pré-condição: `--target-root`, se passado, é relativo ao workspace.
- Pré-condição: `--remap` no formato `orig=new`, repetível. `new` é relativo, sem `..`.
- Pré-condição: nenhum par de membros mapeia para mesmo destino após aplicar `target_root` e `remap` (path collision detectada antes de qualquer cópia).
- Idempotência: se manifest já tem entrada de bundle com mesmo `(bundle_id, target_root, normalized(remap))` e `direction: injected` → `status: already_injected`.
- Operação atômica:
  1. Computa plano completo (component_id → destino) sem efeitos colaterais.
  2. Pré-checa conflitos de hash em destinos existentes. Sem `--force`, retorna `status: conflict` (exit 2).
  3. Para cada membro, cria diretório destino, copia, verifica hash pós-cópia.
  4. Falha em qualquer membro → reverte todos os anteriores (restaura conteúdo prévio salvo em memória; remove arquivos criados que não existiam antes).
- Pós-condição: cada membro materializado em `<workspace>/<target_root>/<bundle_relpath>` (ou `<remap>`).
- Pós-condição: cada membro adicionado a `manifest.json.components[]` com `direction: injected, via_bundle: <bundle_id>`.
- Pós-condição: entrada agregada adicionada a `manifest.json.bundles[]`.
- Exit code: 0 ok, 1 erro pré-condição, 2 conflito (use `--force`), 3 I/O.

---

## 8. Invariantes globais (testes de aceitação)

Toda implementação válida deve satisfazer:

1. **I1 — Determinismo de ID.** Para qualquer arquivo `f` com conteúdo `c`, `extract(f)` produz `component_id == "c-" + sha256(c)[:8]`, em qualquer ambiente.

2. **I2 — Idempotência de extração.** `extract` do mesmo arquivo duas vezes seguidas resulta em uma única entrada em `index.json` e uma única entrada em `manifest.json`. A segunda execução produz `skipped: [{reason: ...}]`.

3. **I3 — Idempotência de injeção.** `inject` do mesmo componente para o mesmo target duas vezes seguidas: a segunda retorna `status: already_injected` ou `status: identical_file_at_destination`. Para `bundle-inject`, idempotência é por `(bundle_id, target_root, normalized(remap))`.

4. **I4 — `INDEX.md` é função pura de `index.json`.** Para o mesmo `index.json`, qualquer execução de `render-index` produz o mesmo `INDEX.md` byte-a-byte (módulo timestamp atual no header).

5. **I5 — Manifesto rastreia tudo.** Toda `extract` ou `inject` (granular ou via bundle) bem-sucedida adiciona entrada em `manifest.json`. Auditoria com `audit` em workspace recém-tocado nunca retorna `manifest_orphan`.

6. **I6 — Sem dependências externas.** O script `recicla.py` importa apenas da stdlib do Python. Verificável com `python -c "import ast; tree = ast.parse(open('recicla.py').read()); ..."`.

7. **I7 — Saída JSON estável.** Para mesmo estado de Library e workspace, mesmo comando com `--json` produz saída JSON com mesmas chaves, em mesma ordem (chaves ordenadas alfabeticamente nos dicts).

8. **I8 — Bundle imutável na Library.** Bundle nunca é modificado após registro. Nova composição com mesmo `name` produz novo `bundle_id` e marca o anterior com `superseded_by: <new_id>`. Implementação: `bundle-extract` nunca faz `update`; sempre `append + supersede`.

9. **I9 — Bundle pina membros por `component_id`, não por path.** Atualização de um componente na Library (criando novo `component_id` via novo conteúdo) **não** afeta bundles existentes que referenciem o ID antigo. O bundle continua válido enquanto o `component_id` antigo permanecer no Index. Remoção explícita do componente antigo dispara `bundle_member_missing` em `audit`.

---

## 9. Casos de teste mínimos

Para validar uma reimplementação:

### T1 — Extração simples
- Workspace: arquivo `src/utils/hash.py` com header `@recicla:reusable`.
- Library: vazia.
- Ação: `scan` lista 1 candidato; `extract` move para `library/components/functions/hash.py`.
- Verificação: `index.json` tem 1 entrada; `manifest.json` tem 1 entrada com `direction: extracted`; `INDEX.md` contém o componente.

### T2 — Idempotência de extract
- Estado pós-T1.
- Ação: rodar `extract` do mesmo arquivo de novo.
- Verificação: `skipped: [{reason: "already_processed_in_workspace"}]`. Nada muda em `index.json`.

### T3 — Detecção de duplicata por hash entre workspaces
- Workspace A: extraiu `hash.py`.
- Workspace B: tem cópia byte-a-byte de `hash.py` em `lib/`.
- Ação em B: `scan`.
- Verificação: arquivo aparece em `skipped` com `reason: duplicate_hash_in_library`.

### T4 — Injeção
- Library com 1 componente extraído de A.
- Workspace C novo.
- Ação em C: `inject --id c-... --target src/lib/hash.py`.
- Verificação: arquivo presente em C; `manifest.json` de C tem entrada com `direction: injected`.

### T5 — Audit detecta drift
- Estado pós-T4. Modificar `src/lib/hash.py` em C (adicionar comentário).
- Ação: `audit` em C.
- Verificação: finding `severity: warn, kind: workspace_hash_drift`.

### T6 — Render-index idempotente
- Estado qualquer com componentes na Library.
- Ação: `render-index` duas vezes seguidas.
- Verificação: `INDEX.md` igual nas duas execuções (excluindo o campo `Updated:`).

### T7 — Sugestão por tags
- Library com 3 componentes, tags `[auth,jwt]`, `[auth,oauth]`, `[ui,react]`.
- Ação: `suggest --tags auth,jwt --top 5`.
- Verificação: ordem por Jaccard descendente, primeiro deve ser o `[auth,jwt]` com score 1.0.

### T8 — Bootstrap de Library vazia
- `RECICLA_LIBRARY` aponta para diretório inexistente.
- Ação: qualquer comando.
- Verificação: estrutura mínima criada (`components/{prompt,template,function,schema,snippet,config}`, `index.json` com arrays `components` e `bundles` vazios, `INDEX.md` com header e contadores zerados).

### T9 — `bundle-init` cria template válido
- Workspace com 3 arquivos marcados como `@recicla:reusable` em `lib/`.
- Ação: `bundle-init --name foo --members lib/a.py,lib/b.py,lib/c.py --tags x,y`.
- Verificação:
  - `.recicla/bundles/foo.json` criado.
  - `validate_bundle_decl` retorna `[]` (lista vazia de erros).
  - `members[].bundle_relpath` deduplicado.
  - `entrypoint: null`, `role: ""` em cada membro.

### T10 — `bundle-extract` idempotente
- Estado: bundle declarado e extraído uma vez.
- Ação: `bundle-extract --name foo` sem mudar a declaração.
- Verificação: `status: already_registered`, `registered: false`, nada adicionado ao `index.json.bundles[]`.

### T11 — `bundle-inject` materializa N membros
- Library com bundle de 5 membros. Workspace destino vazio.
- Ação: `bundle-inject --id b-XXXXXXXX --target-root lib/x`.
- Verificação:
  - 5 arquivos materializados em `lib/x/<bundle_relpath>` no destino.
  - `manifest.json.components` ganhou 5 entradas com `direction: injected, via_bundle: b-XXXXXXXX`.
  - `manifest.json.bundles` ganhou 1 entrada agregada.
  - Hash de cada arquivo materializado bate com o componente da Library.

### T12 — Re-`bundle-extract` com composição diferente gera supersede
- Estado: bundle `foo` com 3 membros registrado (bundle_id `b-AAA`).
- Ação: editar `.recicla/bundles/foo.json` removendo um membro; `bundle-extract --name foo`.
- Verificação:
  - `status: registered`, `superseded_id: b-AAA`.
  - Novo `bundle_id` (`b-BBB`) registrado, `superseded_by: null`.
  - Bundle anterior (`b-AAA`) ainda no Index com `superseded_by: b-BBB`.
  - `INDEX.md` mostra apenas `b-BBB` na seção Bundles (superseded omitido).

### T13 — `audit` detecta `bundle_member_missing`
- Estado: bundle ativo referencia `c-XYZ`. Manualmente removo `c-XYZ` do `index.json.components[]`.
- Ação: `audit`.
- Verificação: finding `severity: error, kind: bundle_member_missing, bundle_id: <id>, component_id: c-XYZ`.

### T14 — `bundle-inject` detecta `bundle_path_collision` na declaração
- Bundle declarado com dois membros distintos com mesmo `bundle_relpath`.
- Ação: `bundle-extract --name <name>`.
- Verificação: `validate_bundle_decl` retorna erro `duplicate bundle_relpath`. Comando falha com exit 1, sem tocar Library.

(Variante runtime: dois `--remap` distintos em `bundle-inject` mapeando para mesmo destino → exit 2 com mensagem `bundle_path_collision`.)

---

## 10. Instruções para o `skill-creator` reconstruir esta skill

Quando este SPEC.md for entregue ao `skill-creator`:

1. **Capturar intent** lendo este arquivo. Pular interview — está aqui completo.
2. **Gerar SKILL.md** seguindo:
   - Frontmatter `name: recicla` e descrição "pushy" cobrindo gatilhos `/recicla scan|extract|suggest|inject|audit|render-index|bundle-init|bundle-extract|bundle-inject`. Manter ≤ 1024 caracteres no campo `description`.
   - Seções: Fundamento, Configuração obrigatória, Operações sobre componentes, Operações sobre bundles, Critérios de elegibilidade, Marcação de metadados, Declaração de bundle, Manifesto local, INDEX.md, Workflows (extração granular, reciclar pipeline composto, injeção), Auditoria, Heurística "bundle vs componente", Invariantes, Referências.
   - Tom técnico, imperativo, sem preâmbulos motivacionais.
3. **Gerar `scripts/recicla.py`** implementando os 9 subcomandos com os contratos da seção 7. Stdlib apenas. Saída JSON com `--json`. Hash SHA-256. IDs determinísticos (componente §3.2, bundle §3.5/§6.4). Bootstrap automático de Library. Migração silenciosa de schemas v1.0 → v1.1 em read-time. Cópia atômica em `bundle-inject` com revert em falha.
4. **Gerar `reference/schemas.md`** com os schemas da seção 5 expandidos com exemplos.
5. **Gerar `reference/eligibility_criteria.md`** com a seção 6.1 expandida e exemplos de matches/não-matches.
6. **Gerar `reference/operations.md`** com a seção 7 expandida (todos os 9 subcomandos), fluxos de erro detalhados, exemplos de chamada e saída.
7. **Gerar `README.md`** curto com: instalação (clone/copy), configuração (`RECICLA_LIBRARY`), comandos básicos para componentes e bundles.
8. **Validar** os casos de teste da seção 9 (T1–T14) antes de empacotar. Cada teste deve passar.

Não gerar testes automatizados (`evals/evals.json` etc.) a menos que o usuário solicite — esses 14 casos são suficientes como sanity check manual.

---

## 11. Versionamento desta spec

Esta spec é versionada em `version: 1.1.0` no frontmatter conceitual. Histórico:

| Versão | Mudança |
|---|---|
| `1.0.0` | Versão inicial. Componentes únicos, 6 subcomandos, schemas `index.json` e `manifest.json` v1.0. |
| `1.1.0` | Bundles adicionados como 2ª entidade de 1ª classe. 3 subcomandos novos (`bundle-init`, `bundle-extract`, `bundle-inject`). Schemas `index.json` e `manifest.json` bumped para v1.1 (campo `bundles[]` e `via_bundle`). Schema novo: declaração de bundle v1.0. Invariantes I1–I7 preservadas; I8 e I9 adicionadas. Migração read-time silenciosa de v1.0 → v1.1. |

**Compatibilidade:**
- `index.json` v1.0 lido por implementação 1.1 → tratado como `bundles: []`. Próxima escrita atualiza para v1.1.
- `manifest.json` v1.0 lido por 1.1 → tratado como `bundles: []` e cada `components[]` ganha `via_bundle: null`. Próxima escrita atualiza para v1.1.
- Implementação 1.0 lendo `index.json` v1.1 ignora o campo `bundles[]` (read defensivo). Não há perda de dados — apenas perda de funcionalidade até atualizar.

Mudanças que quebram contratos de subcomando ou identidade (ex: alterar serialização canônica de `bundle_id`) exigem incremento de major (`2.0.0`) e migração explícita.
