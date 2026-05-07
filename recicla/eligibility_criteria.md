# Critérios de Elegibilidade — `recicla scan`

Este documento define **com precisão** o pipeline de filtros que determina se um arquivo do workspace é candidato a extração. Toda heurística aqui é **determinística e checável** — não há "pareceu reutilizável".

---

## 1. Pipeline de avaliação

Para cada arquivo `f` encontrado durante o walk recursivo do workspace:

```
def is_candidate(f, workspace_path, max_size_bytes, manifest, index):
    # Filtros de exclusão (fail-fast)
    if is_excluded_path(f, workspace_path):
        return (False, "excluded_path")
    if size(f) > max_size_bytes:
        return (False, "size_exceeded")
    if is_binary(f):
        return (False, "binary_file")

    # Filtros de inclusão (basta um)
    has_marker = file_has_marker(f)
    in_canonical = is_in_canonical_dir(f, workspace_path)
    if not (has_marker or in_canonical):
        return (False, "not_eligible")

    # Filtros de duplicata (read-only checks)
    h = sha256(f)
    if h in {c.sha256_at_op for c in manifest.components}:
        return (False, "already_processed_in_workspace")
    if h in {c.sha256 for c in index.components}:
        return (False, "duplicate_hash_in_library")

    return (True, None)
```

A operação `scan` retorna ambos:
- `candidates[]` — arquivos com `is_candidate == True`
- `skipped[]` — arquivos com `is_candidate == False`, junto com `skip_reason`

A presença na lista `skipped` é informativa, não erro.

---

## 2. Filtros de exclusão

### 2.1 Caminhos excluídos

Lista fixa, exata, ordenada (qualquer match em qualquer ancestral do path descarta o arquivo):

```
.git/
.svn/
.hg/
.bzr/
node_modules/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.tox/
dist/
build/
target/
out/
.next/
.nuxt/
.cache/
.parcel-cache/
.venv/
venv/
env/
.env/
.DS_Store
.recicla/
```

Padrões adicionais por nome de arquivo:

```
*.lock
*.min.js
*.min.css
*.map
*.pyc
*.pyo
*.class
*.o
*.so
*.dll
*.exe
```

### 2.2 Tamanho máximo

Default: **50 KB** (51200 bytes).

Configurável via `--max-size <bytes>`. Justificativa: componentes reutilizáveis tendem a ser pequenos e auto-contidos. Arquivos grandes são quase sempre módulos de aplicação específicos, dados ou builds.

Não confundir com **arquivos vazios** — arquivos com 0 bytes são automaticamente descartados como `not_eligible` (não há nada para reciclar).

### 2.3 Detecção de binário

Heurística: ler primeiros 8192 bytes do arquivo. Se contiver byte `0x00` → binário.

Não usar inspeção de extensão para isso (uma `.py` pode ter sido salva como binário corrompido; um `.bin` pode ser texto). O byte nulo é o único critério.

---

## 3. Filtros de inclusão

### 3.1 Marcador explícito (`@recicla:reusable`)

Arquivo é candidato se **alguma linha** do arquivo (excluindo o conteúdo binário, mas todo arquivo aqui já passou no filtro de binário) contém a substring literal `@recicla:reusable`.

Detalhes:
- Case-sensitive.
- A substring pode estar precedida por qualquer prefixo de comentário (`#`, `//`, `/*`, `<!--`, `;;`, `--`, etc.).
- Basta uma ocorrência. A linha pode ter mais conteúdo após.

### 3.2 Diretório canônico

Arquivo é candidato se algum dos diretórios ancestrais (relativos ao workspace) é um destes nomes:

```
lib/
libs/
utils/
util/
shared/
common/
components/
helpers/
helper/
templates/
template/
prompts/
prompt/
schemas/
schema/
snippets/
snippet/
configs/
config/
functions/
function/
types/
```

Match é por nome de diretório, não por padrão glob. `src/lib/auth.ts` qualifica (ancestral `lib/`); `src/library_management/db.py` não qualifica (não há ancestral exato `lib/`).

### 3.3 Combinação

Se ambos os critérios falharem, o arquivo é descartado com `skip_reason: "not_eligible"`.

Se ambos passarem, o arquivo é candidato — não há prioridade (a presença do marcador apenas garante override de metadados via header).

---

## 4. Filtros de duplicata

### 4.1 Manifesto local

Cada arquivo do workspace é hasheado (SHA-256). Se o hash bate com algum `sha256_at_op` no `manifest.json` do workspace:

```
skip_reason: "already_processed_in_workspace"
existing_component_id: <component_id da entrada do manifesto>
```

Isso suprime tanto:
- Componentes já extraídos deste workspace para a Library.
- Componentes injetados da Library neste workspace (que poderiam ser "re-extraídos" sem essa proteção).

### 4.2 Index da Library

Se o hash bate com algum `sha256` em `index.json`:

```
skip_reason: "duplicate_hash_in_library"
existing_component_id: <component_id na Library>
```

Cobre o caso em que dois workspaces têm cópias idênticas do mesmo arquivo (ex: copy-paste manual antes da skill existir). A Library mantém o componente uma única vez.

### 4.3 Hash não bate, mas nome existe

**Não** é caso de duplicata. Dois arquivos com mesmo nome mas conteúdo diferente são componentes diferentes. A operação `extract` resolve conflito de nome no destino com sufixo `-<short_hash>` (ver `operations.md`).

---

## 5. Inferência de metadados

Quando o arquivo qualifica como candidato, a skill pré-extrai metadados (mesmo antes da extração efetiva, para apresentar ao usuário no resultado de `scan`).

### 5.1 Header `@recicla:*`

Se o arquivo contém linhas no formato:

```
[<comment_prefix>] @recicla:<key> <value>
```

A skill extrai `key → value` para `key ∈ {name, category, tags, description}`. Demais chaves são ignoradas (forward-compatible com extensões futuras).

Regex utilizada:

```
^\s*[^\w\n]*\s*@recicla:(\w+)\s+(.+?)\s*$
```

`tags` é parseada como CSV: `auth, jwt, security` → `["auth", "jwt", "security"]`. Trim em cada elemento; descarta vazios.

### 5.2 Defaults se header ausente

| Campo | Default |
|---|---|
| `name` | `slugify(filename_without_extension)` — kebab-case ASCII. |
| `category` | Mapeada do diretório canônico ancestral (ver tabela abaixo). Fallback: `snippet`. |
| `tags` | `[]`. |
| `description` | Primeira linha não vazia e não puramente um comentário decorativo (`####`, `///`, etc.), truncada a 200 chars. Se nada serve: `"(sem descrição)"`. |

### 5.3 Mapeamento diretório → categoria

| Diretório ancestral (mais próximo) | Categoria |
|---|---|
| `prompts/`, `prompt/` | `prompt` |
| `templates/`, `template/` | `template` |
| `lib/`, `libs/`, `utils/`, `util/`, `helpers/`, `helper/`, `functions/`, `function/` | `function` |
| `schemas/`, `schema/`, `types/` | `schema` |
| `configs/`, `config/` | `config` |
| `snippets/`, `snippet/`, `shared/`, `common/`, `components/` | `snippet` |

Se múltiplos ancestrais qualificam, vence o **mais próximo** do arquivo. Ex: `src/utils/templates/foo.txt` → `template` (mais próximo) e não `function`.

### 5.4 Mapeamento extensão → linguagem

| Extensão | `language` |
|---|---|
| `.py` | `python` |
| `.js`, `.mjs`, `.cjs` | `javascript` |
| `.ts`, `.tsx` | `typescript` |
| `.jsx` | `javascript` |
| `.rb` | `ruby` |
| `.go` | `go` |
| `.rs` | `rust` |
| `.java` | `java` |
| `.kt` | `kotlin` |
| `.swift` | `swift` |
| `.c`, `.h` | `c` |
| `.cpp`, `.cc`, `.hpp` | `cpp` |
| `.cs` | `csharp` |
| `.php` | `php` |
| `.sh`, `.bash`, `.zsh` | `shell` |
| `.sql` | `sql` |
| `.md`, `.markdown` | `markdown` |
| `.txt` | `text` |
| `.json` | `json` |
| `.yaml`, `.yml` | `yaml` |
| `.toml` | `toml` |
| `.html`, `.htm` | `html` |
| `.css`, `.scss`, `.sass` | `css` |
| `.xml` | `xml` |
| (outras) | `unknown` |

---

## 6. Casos de exemplo

### 6.1 Match — marcador explícito em diretório arbitrário

`src/business_logic/billing.py`:
```python
# @recicla:reusable
# @recicla:name calc-prorated-charge
# @recicla:category function
# @recicla:tags billing,proration
# @recicla:description Calcula cobrança rateada por dias do mês.

def calc_prorated_charge(amount, day_in, day_out, days_in_month=30):
    ...
```

→ **candidato**. `has_marker: true`, `in_canonical_dir: false`. Metadados do header.

### 6.2 Match — diretório canônico, sem marcador

`packages/lib/format-date.ts`:
```typescript
export function formatDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}
```

→ **candidato**. `has_marker: false`, `in_canonical_dir: true` (`lib/`). Metadados inferidos: `name: format-date`, `category: function`, `language: typescript`, `tags: []`, `description: "export function formatDate(d: Date): string {"`.

### 6.3 Não-match — diretório não canônico, sem marcador

`src/pages/dashboard/index.tsx`:
```typescript
export default function Dashboard() { ... }
```

→ **descartado**. `not_eligible`.

### 6.4 Não-match — sob `node_modules/`

`node_modules/lodash/lodash.js` — descartado por `excluded_path` antes de qualquer outro filtro.

### 6.5 Não-match — duplicata

`src/utils/hash.py` com mesmo conteúdo de `c-a3f9b2e1` já na Library:

→ `skipped`, `reason: duplicate_hash_in_library`, `existing_component_id: c-a3f9b2e1`.

### 6.6 Não-match — arquivo grande

`templates/dashboard.html` com 80KB → descartado por `size_exceeded`.

### 6.7 Match parcial — header sem todos os metadados

`utils/slugify.py`:
```python
# @recicla:reusable
# @recicla:tags string,utility

def slugify(text): ...
```

→ **candidato**. Metadados parciais do header (`tags`), demais via default:
- `name: slugify` (do filename)
- `category: function` (do dir `utils/`)
- `description: "def slugify(text): ..."` (primeira linha não-comentário)

---

## 7. Conformidade

Uma reimplementação do `scan` é considerada conforme se:

1. Para o mesmo input (workspace + library + manifesto + max-size), produz o mesmo conjunto de candidatos e skipped (módulo ordenação — ver abaixo).
2. Ordenação dentro de `candidates[]` e `skipped[]`: por `path` ascendente, lexicográfico bytewise.
3. Saída JSON com `--json` é estável (chaves ordenadas alfabeticamente nos dicts internos).

---

## 8. Bundles e elegibilidade

Bundles **não** têm critérios de elegibilidade automáticos. Diferentemente de componentes, que são identificados via heurística (header `@recicla:reusable` ou diretório canônico), bundles são sempre **declarados explicitamente** pelo usuário em `.recicla/bundles/<name>.json`.

`scan` lista declarações de bundle encontradas no workspace em `bundle_candidates[]`, marcando cada uma como `valid: true | false` conforme `validate_bundle_decl`. Não há "inferência" de bundle a partir do filesystem.

`bundle-extract` impõe uma restrição adicional: cada `members[].workspace_relpath` deve passar nos critérios de elegibilidade da extração de componentes (`is_candidate`). Isso significa que membros de bundle precisam estar em diretório canônico OU ter header `@recicla:reusable`. **Não há rebaixamento de critérios via bundle**: declarar um arquivo como membro não o torna automaticamente extraível se ele não passaria no `scan`.

Razão: bundle pina componentes pelo `component_id` (sha256 do conteúdo). Para o pin existir, o membro precisa estar registrado no `index.json` da Library — o que só acontece via `extract`, que aplica os critérios.
