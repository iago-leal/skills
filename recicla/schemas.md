# Schemas — `recicla`

Schemas JSON de todas as estruturas persistidas e de todas as saídas de comando.

---

## 1. `index.json` (Library) — schema v1.1

Localização: `$RECICLA_LIBRARY/index.json`. **Fonte de verdade** dos componentes e bundles catalogados.

### Estrutura

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
      "sha256": "8f3cab47e2d1c9a0b1f4e3d2c7a8b9e0d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a9",
      "size_bytes": 2148,
      "added_at": "2026-04-10T09:15:00Z",
      "added_from_workspace": "/abs/path/to/origin"
    }
  ],
  "bundles": [
    {
      "bundle_id": "b-a1b2c3d4",
      "name": "rag-pipeline",
      "added_at": "2026-05-07T16:30:00Z",
      "added_from_workspace": "/abs/path/to/rag-app",
      "description": "Pipeline RAG canônico.",
      "tags": ["rag", "llm", "pipeline"],
      "entrypoint": "pipeline/retriever.py",
      "members": [
        {"component_id": "c-a1a1a1a1", "bundle_relpath": "pipeline/transcriber.py", "role": "transcribe"},
        {"component_id": "c-b2b2b2b2", "bundle_relpath": "pipeline/chunker.py",     "role": "chunk"}
      ],
      "superseded_by": null
    }
  ]
}
```

### Campos `components[]`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `version` | string | sim | Versão do schema. Atual: `"1.1"`. |
| `library_path` | string | sim | Caminho absoluto da Library. |
| `updated_at` | string ISO 8601 UTC | sim | Última modificação do `index.json`. |
| `components[]` | array | sim | Lista de componentes. Vazia se Library nova. |
| `components[].component_id` | string | sim | `"c-" + sha256[:8]` no momento da primeira extração. |
| `components[].name` | string | sim | Nome canônico (slug). Único na Library — conflito resolvido por sufixo `-<short_hash>`. |
| `components[].category` | string | sim | ∈ `{prompt, template, function, schema, snippet, config}`. |
| `components[].tags` | array&lt;string&gt; | sim | Pode ser vazia. Tags ordenadas alfabeticamente. |
| `components[].description` | string | sim | Texto livre, max 500 chars. `"(sem descrição)"` se ausente. |
| `components[].language` | string | sim | Detectada pela extensão. Ex: `python`, `typescript`, `markdown`, `yaml`, `unknown`. |
| `components[].library_relpath` | string | sim | Caminho relativo a `library_path`. Sempre forward slashes. |
| `components[].sha256` | string | sim | SHA-256 hex completo do arquivo no momento da extração. |
| `components[].size_bytes` | int | sim | Bytes do arquivo. |
| `components[].added_at` | string ISO 8601 UTC | sim | Timestamp da extração. |
| `components[].added_from_workspace` | string | sim | Caminho absoluto do workspace de origem. |

### Campos `bundles[]`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `bundles[].bundle_id` | string | sim | `"b-" + sha256(name + "|" + sorted("cid:relpath"))[:8]`. |
| `bundles[].name` | string | sim | Slug `^[a-z0-9][a-z0-9-]{0,63}$`. Único entre bundles ativos. |
| `bundles[].added_at` | string ISO 8601 UTC | sim | Quando registrado. |
| `bundles[].added_from_workspace` | string | sim | Workspace de origem. |
| `bundles[].description` | string | sim | Texto livre. Pode ser vazio. |
| `bundles[].tags` | array&lt;string&gt; | sim | Pode ser vazia. |
| `bundles[].entrypoint` | string \| null | sim | `bundle_relpath` do entrypoint, ou `null`. |
| `bundles[].members[]` | array | sim | Não-vazia. |
| `bundles[].members[].component_id` | string | sim | Pin determinístico no `component_id`. |
| `bundles[].members[].bundle_relpath` | string | sim | Layout interno canônico. Sem `..`, sem absoluto. |
| `bundles[].members[].role` | string | sim | Pode ser `""`. Metadado consultivo, não afeta `bundle_id`. |
| `bundles[].superseded_by` | string \| null | sim | `bundle_id` do bundle que substitui este, ou `null` se ativo. |

### Invariantes

- `components[]` ordenado por `added_at` ascendente.
- `component_id` único na Library.
- `name` de componente único na Library (após resolução de conflito).
- `sha256` único na Library (não é permitido catalogar duas vezes o mesmo conteúdo).
- `library_relpath` aponta para arquivo existente.
- `bundles[]` ordenado por `added_at` ascendente.
- `bundle_id` único na Library.
- No máximo um bundle ativo (`superseded_by: null`) por `name`.
- Todo `bundles[].members[].component_id` referencia um `component_id` existente em `components[]` (auditável; falha vira `bundle_member_missing`).

---

## 2. `manifest.json` (Workspace local) — schema v1.1

Localização: `<workspace>/.recicla/manifest.json`. Registra **operações** (extrações e injeções de componentes, e injeções de bundles) realizadas neste workspace.

### Estrutura

```json
{
  "version": "1.1",
  "workspace_path": "/abs/path/to/workspace",
  "created_at": "2026-05-07T14:00:00Z",
  "updated_at": "2026-05-07T16:35:00Z",
  "components": [
    {
      "component_id": "c-a3f9b2e1",
      "library_relpath": "components/functions/jwt-validator.py",
      "workspace_relpath": "src/auth/jwt-validator.py",
      "direction": "extracted",
      "sha256_at_op": "8f3cab47e2d1...",
      "timestamp": "2026-05-07T14:05:23Z",
      "via_bundle": null
    },
    {
      "component_id": "c-a1a1a1a1",
      "library_relpath": "components/snippets/transcriber.py",
      "workspace_relpath": "lib/audio/pipeline/transcriber.py",
      "direction": "injected",
      "sha256_at_op": "a1a1a1a1...",
      "timestamp": "2026-05-07T16:35:00Z",
      "via_bundle": "b-a1b2c3d4"
    }
  ],
  "bundles": [
    {
      "bundle_id": "b-a1b2c3d4",
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

### Campos `components[]`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `version` | string | sim | Versão do schema. Atual: `"1.1"`. |
| `workspace_path` | string | sim | Caminho absoluto do workspace. |
| `created_at` | string ISO 8601 UTC | sim | Criação do manifesto. |
| `updated_at` | string ISO 8601 UTC | sim | Última modificação. |
| `components[]` | array | sim | Operações granulares registradas. |
| `components[].component_id` | string | sim | ID na Library. |
| `components[].library_relpath` | string | sim | Caminho relativo na Library. |
| `components[].workspace_relpath` | string | sim | Caminho relativo no workspace. Forward slashes. |
| `components[].direction` | string | sim | ∈ `{extracted, injected}`. |
| `components[].sha256_at_op` | string | sim | Hash do arquivo no momento da operação. |
| `components[].timestamp` | string ISO 8601 UTC | sim | Quando a operação ocorreu. |
| `components[].via_bundle` | string \| null | sim | `bundle_id` se entrou via `bundle-inject`, ou `null` em `extract`/`inject` granulares. |

### Campos `bundles[]`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `bundles[].bundle_id` | string | sim | ID do bundle injetado. |
| `bundles[].name` | string | sim | Nome do bundle (cópia do registro na Library no momento da operação). |
| `bundles[].direction` | string | sim | Sempre `"injected"` em v1.1. |
| `bundles[].members_count` | int | sim | Quantidade de membros materializados. |
| `bundles[].target_root` | string | sim | Prefixo passado em `--target-root`. Pode ser `""`. |
| `bundles[].remap` | object | sim | Map `bundle_relpath → override_relpath`. `{}` se nenhum. |
| `bundles[].timestamp` | string ISO 8601 UTC | sim | Quando ocorreu. |

### Invariantes

- `components[]` ordenado por `timestamp` ascendente.
- A mesma `(component_id, direction, workspace_relpath)` pode aparecer no máximo uma vez (idempotência).
- `bundles[]` ordenado por `timestamp` ascendente.
- A mesma `(bundle_id, target_root, remap)` pode aparecer no máximo uma vez (idempotência de `bundle-inject`).
- Para todo `components[]` com `via_bundle != null`, existe entrada em `bundles[]` com mesmo `bundle_id`.

### Migração v1.0 → v1.1

Manifestos v1.0 são migrados read-time silenciosamente:
- Campo `bundles: []` adicionado.
- Cada `components[]` ganha `via_bundle: null`.
- `version` bumpado.

A primeira escrita após leitura persiste a migração no disco.

---

## 3. Declaração local de bundle — `.recicla/bundles/<name>.json` (schema v1.0)

Localização: `<workspace>/.recicla/bundles/<name>.json`. Declarado pelo usuário (manual ou via `bundle-init`). Lido por `bundle-extract`.

### Estrutura

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

### Campos

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `version` | string | sim | Versão do schema da declaração. Atual: `"1.0"`. |
| `name` | string | sim | Slug `^[a-z0-9][a-z0-9-]{0,63}$`. |
| `description` | string | sim | Texto livre. Pode ser `""`. |
| `tags` | array&lt;string&gt; | sim | Pode ser `[]`. |
| `entrypoint` | string \| null | sim | Deve casar um dos `members[].bundle_relpath`, ou ser `null`. |
| `members[]` | array | sim | Não-vazia. |
| `members[].workspace_relpath` | string | sim | Path do membro no workspace de origem. |
| `members[].bundle_relpath` | string | sim | Layout interno do bundle. Sem `..`, sem absoluto. |
| `members[].role` | string | sim | Pode ser `""`. Metadado consultivo. |

### Invariantes (validadas por `validate_bundle_decl`)

- `name` casa o regex.
- `members[]` não-vazia.
- Sem `workspace_relpath` duplicado.
- Sem `bundle_relpath` duplicado.
- Nenhum `bundle_relpath` é absoluto ou contém `..`.
- Se `entrypoint != null`, deve casar exatamente um `members[].bundle_relpath`.
- Falha em qualquer invariante → `bundle-extract` retorna exit 1 com lista de erros.

---

## 4. `INDEX.md` (Library)

Localização: `$RECICLA_LIBRARY/INDEX.md`. **View** regenerada a partir de `index.json`.

### Estrutura

````markdown
# Component Library Index

> Generated by `recicla` — do not edit manually. Source of truth: `index.json`.
> Updated: <ISO 8601 UTC>
> Components: <N>

## Quick lookup

| ID | Name | Category | Tags | Path |
|---|---|---|---|---|
| `c-a3f9b2e1` | jwt-validator | function | auth, jwt, security | `components/functions/jwt-validator.py` |
| `c-b7d2f1a4` | anamnese | prompt | medicina, mfc | `components/prompts/anamnese.md` |

## Components by category

### Functions (1)

#### `c-a3f9b2e1` — jwt-validator
- **Path:** `components/functions/jwt-validator.py`
- **Tags:** auth, jwt, security
- **Description:** Valida JWT contra issuer e audience configuráveis.
- **Language:** python
- **Hash:** `sha256:8f3cab47e2d1...`
- **Size:** 2.1 KB
- **Added:** 2026-04-10

### Prompts (1)

#### `c-b7d2f1a4` — anamnese
- **Path:** `components/prompts/anamnese.md`
- **Tags:** medicina, mfc
- **Description:** Roteiro de anamnese clínica baseado em MCCP.
- **Language:** markdown
- **Hash:** `sha256:4d8a91b3c7e2...`
- **Size:** 4.3 KB
- **Added:** 2026-04-12

## Consultation protocol (for agents)

To find a component matching a need:
1. Filter the Quick lookup table by `category` and/or `tags` matching the user's intent.
2. Read the matched components' descriptions in the section above.
3. To import: invoke `python <path-to-recicla>/scripts/recicla.py inject --id <ID> --library $RECICLA_LIBRARY --workspace . --target <relative-destination>`.
4. Never copy file contents from this index — always use `inject` to preserve manifest tracking and avoid drift.
````

### Regras de geração

- Categorias listadas em ordem fixa: `prompt, template, function, schema, snippet, config`.
- Componentes dentro de cada categoria: ordenados alfabeticamente por `name`.
- Tags listadas comma-separated, sem espaços extras.
- Tamanho formatado: `< 1024 → "<N> B"`, `< 1024² → "<N.N> KB"`, senão `"<N.N> MB"`.
- `Hash` exibe apenas os primeiros 12 caracteres do hex, prefixado por `sha256:` e seguido de `...`.
- Categorias vazias são omitidas.
- Se Library vazia: ainda assim emitir o header e a seção "Consultation protocol", com aviso `> Library is empty.` no lugar da tabela.

---

## 5. Saídas JSON de comandos

Todas as saídas de comando com flag `--json` seguem um envelope:

```json
{
  "command": "scan | extract | suggest | inject | audit | render-index | bundle-init | bundle-extract | bundle-inject",
  "version": "1.1.0",
  "ok": true,
  "data": { ... },
  "errors": []
}
```

### 5.1 `scan` — campo `data`

```json
{
  "workspace_path": "/abs/path",
  "library_path": "/abs/path",
  "scanned_files": 142,
  "candidates": [
    {
      "path": "src/utils/jwt.py",
      "absolute_path": "/abs/.../src/utils/jwt.py",
      "size_bytes": 2148,
      "category_inferred": "function",
      "language_inferred": "python",
      "has_marker": true,
      "in_canonical_dir": true,
      "metadata_from_header": {
        "name": "jwt-validator",
        "category": "function",
        "tags": ["auth", "jwt"],
        "description": "Valida JWT..."
      },
      "sha256": "..."
    }
  ],
  "skipped": [
    {
      "path": "src/utils/old_jwt.py",
      "skip_reason": "duplicate_hash_in_library",
      "existing_component_id": "c-a3f9b2e1"
    }
  ],
  "bundle_candidates": [
    {
      "path": ".recicla/bundles/rag-pipeline.json",
      "name": "rag-pipeline",
      "valid": true,
      "errors": [],
      "members_count": 5
    }
  ]
}
```

`bundle_candidates[].valid` é `false` se a declaração falha em `validate_bundle_decl`. Nesse caso, `errors[]` lista as falhas.

### 5.2 `extract` — campo `data`

```json
{
  "extracted": [
    {
      "component_id": "c-a3f9b2e1",
      "name": "jwt-validator",
      "library_relpath": "components/functions/jwt-validator.py",
      "workspace_relpath": "src/utils/jwt.py"
    }
  ],
  "skipped": [
    {
      "path": "src/utils/jwt.py",
      "reason": "duplicate_hash_in_library | already_processed_in_workspace | not_eligible",
      "existing_component_id": "c-..."
    }
  ],
  "index_updated": true,
  "manifest_updated": true,
  "index_md_regenerated": true
}
```

### 5.3 `suggest` — campo `data`

```json
{
  "library_path": "/abs/path",
  "query": {
    "tags": ["auth", "jwt"],
    "language": "python",
    "category": null,
    "type": "all",
    "auto_inferred": false
  },
  "matches": [
    {
      "type": "component",
      "component_id": "c-a3f9b2e1",
      "name": "jwt-validator",
      "category": "function",
      "tags": ["auth", "jwt", "security"],
      "language": "python",
      "description": "...",
      "library_relpath": "components/functions/jwt-validator.py",
      "score": 0.667,
      "already_in_workspace": false
    },
    {
      "type": "bundle",
      "bundle_id": "b-a1b2c3d4",
      "name": "rag-pipeline",
      "tags": ["rag", "llm", "pipeline"],
      "description": "Pipeline RAG canônico.",
      "members_count": 5,
      "category": null,
      "language": null,
      "score": 0.143,
      "already_in_workspace": false
    }
  ]
}
```

`matches[].type` ∈ `{component, bundle}`. Componentes têm `component_id`, `category`, `language`, `library_relpath`. Bundles têm `bundle_id`, `members_count`. Ambos têm `score`, `tags`, `description`, `already_in_workspace`.

`query.type` ∈ `{all, component, bundle}` reflete o filtro `--type`.

Quando `--category` ou `--language` é passado, bundles são excluídos da busca a menos que `--type bundle` seja explícito (categoria e linguagem não se aplicam a bundles).

### 5.4 `inject` — campo `data`

```json
{
  "component_id": "c-a3f9b2e1",
  "name": "jwt-validator",
  "source_library_path": "/abs/.../components/functions/jwt-validator.py",
  "destination_workspace_path": "/abs/workspace/src/lib/jwt.py",
  "status": "ok | conflict | already_injected | identical_file_at_destination",
  "manifest_updated": true
}
```

### 5.5 `audit` — campo `data`

```json
{
  "workspace_path": "/abs/path",
  "library_path": "/abs/path",
  "summary": {
    "info": 0,
    "warn": 1,
    "error": 1
  },
  "findings": [
    {
      "severity": "warn",
      "kind": "manifest_orphan",
      "component_id": "c-a3f9b2e1",
      "details": "..."
    },
    {
      "severity": "error",
      "kind": "bundle_member_missing",
      "component_id": "c-deadbeef",
      "bundle_id": "b-a1b2c3d4",
      "details": "bundle 'rag-pipeline' references component c-deadbeef which is missing from index"
    }
  ]
}
```

Tipos de finding:

| `kind` | `severity` | Descrição |
|---|---|---|
| `manifest_orphan` | warn | Manifesto local referencia arquivo que não existe mais no workspace. |
| `workspace_hash_drift` | warn | Hash atual do arquivo no workspace difere de `sha256_at_op`. Componente foi modificado pós-operação. |
| `library_hash_drift` | error | Hash do arquivo na Library difere de `sha256` no `index.json`. Library corrompida. |
| `library_file_missing` | error | `index.json` referencia arquivo que não existe na Library. |
| `library_duplicate_hash` | error | Dois componentes diferentes em `index.json` com mesmo `sha256`. Patológico. |
| `index_md_stale` | info | `INDEX.md` mais antigo que `index.json` — basta rodar `render-index`. |
| `injected_component_removed_from_library` | warn | Componente injetado neste workspace não existe mais no Index. |
| `bundle_member_missing` | error | Bundle ativo referencia `component_id` ausente do Index. Carrega `bundle_id` adicional no finding. |
| `bundle_definition_drift` | warn | Declaração local (`.recicla/bundles/<name>.json`) calcularia um `bundle_id` que não está registrado. Carrega o `bundle_id` computado no finding. |
| `injected_bundle_removed_from_library` | warn | Bundle injetado neste workspace não existe mais no Index. Carrega `bundle_id` no finding. |

### 5.6 `render-index` — campo `data`

```json
{
  "library_path": "/abs/path",
  "index_md_path": "/abs/path/INDEX.md",
  "components_rendered": 23,
  "categories_with_components": ["prompt", "function", "schema"]
}
```

### 5.7 `bundle-init` — campo `data`

```json
{
  "declaration_path": "/abs/.../.recicla/bundles/rag-pipeline.json",
  "declaration_relpath": ".recicla/bundles/rag-pipeline.json",
  "decl": {
    "version": "1.0",
    "name": "rag-pipeline",
    "description": "...",
    "tags": ["rag"],
    "entrypoint": null,
    "members": [...]
  }
}
```

`decl` é o conteúdo escrito no arquivo, eco fiel para conferência.

### 5.8 `bundle-extract` — campo `data`

```json
{
  "bundle_id": "b-a1b2c3d4",
  "name": "rag-pipeline",
  "auto_extracted": ["src/processing/transcriber.py", "..."],
  "members_count": 5,
  "registered": true,
  "status": "registered | already_registered",
  "superseded_id": null
}
```

- `status: registered` — bundle novo registrado.
- `status: already_registered` — `bundle_id` já existe no Index, idempotência. `registered: false`.
- `superseded_id` é o `bundle_id` anterior (mesmo `name`) que foi marcado com `superseded_by`. `null` se nenhum.
- `auto_extracted[]` lista membros extraídos durante esta operação por `--extract-members`. Vazio se não usado.

### 5.9 `bundle-inject` — campo `data`

```json
{
  "bundle_id": "b-a1b2c3d4",
  "name": "rag-pipeline",
  "target_root": "lib/audio",
  "members_count": 5,
  "status": "ok | ok_overwritten | already_injected | conflict",
  "injected": [
    {
      "component_id": "c-a1a1a1a1",
      "bundle_relpath": "pipeline/transcriber.py",
      "destination_workspace_relpath": "lib/audio/pipeline/transcriber.py"
    }
  ],
  "skipped": null,
  "conflicts": null
}
```

- `status: ok` — todos os membros materializados em destinos limpos.
- `status: ok_overwritten` — algum destino foi sobrescrito com `--force`.
- `status: already_injected` — manifesto já tem entrada com mesmo `(bundle_id, target_root, remap)`. `injected: []`, `skipped` lista todos os `bundle_relpath`s.
- `status: conflict` — pelo menos um destino tem hash divergente sem `--force`. `conflicts[]` lista cada caso. Nenhum byte foi escrito (operação atômica).

---

## 6. Códigos de saída (exit codes)

| Code | Significado |
|---|---|
| 0 | Sucesso. |
| 1 | Erro de pré-condição (configuração ausente, arquivo não existe, JSON inválido, declaração inválida). |
| 2 | Conflito que exige `--force` ou ação explícita do usuário. |
| 3 | Erro de I/O (permissão negada, disco cheio). Para `bundle-inject`, copy revertida automaticamente antes de retornar. |
| 99 | Erro inesperado (bug). Stack trace impresso em stderr. |
