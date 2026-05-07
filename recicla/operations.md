# Operações — `recicla`

Contratos detalhados de cada subcomando: argumentos, pré-condições, fluxo, pós-condições, fluxos de erro.

Convenção: `<workspace>` refere-se ao diretório passado em `--workspace` (ou `.` se omitido). `<library>` ao diretório em `--library` (ou `$RECICLA_LIBRARY`).

---

## 1. `scan` — Listar candidatos a extração

### Sintaxe

```bash
python recicla.py scan \
  --workspace <path> \
  --library <path> \
  [--max-size <bytes>] \
  [--json]
```

### Argumentos

| Argumento | Default | Descrição |
|---|---|---|
| `--workspace` | `.` | Raiz do projeto a varrer. |
| `--library` | `$RECICLA_LIBRARY` | Library global. |
| `--max-size` | `51200` (50 KB) | Tamanho máximo de candidato. |
| `--json` | `false` | Saída JSON estruturada em vez de tabela legível. |

### Pré-condições

1. `<workspace>` existe e é diretório.
2. `<library>` existe (criado se ausente).

Se `<library>` não existe, é inicializado: cria diretório, subdiretório `components/` com subpastas vazias para cada categoria, `index.json` com `components: []`, `INDEX.md` com header e marca de Library vazia.

### Fluxo

1. Carregar `index.json` da Library (ou `[]` se Library nova).
2. Carregar `manifest.json` do workspace (ou `[]` se ausente).
3. Walk recursivo no `<workspace>`. Para cada arquivo, aplicar pipeline de elegibilidade (ver `eligibility_criteria.md`).
4. Para candidatos, computar SHA-256 e parsear header.
5. Para skipped, registrar `skip_reason`.
6. Ordenar `candidates` e `skipped` por `path` ascendente.
7. Emitir saída.

### Pós-condições

- **Nenhuma escrita**. Operação read-only sobre `<workspace>` e `<library>`.
- Bootstrap de Library, se ocorreu, é a **única** modificação aceitável (criação de estrutura mínima vazia).

### Saída legível (sem `--json`)

```
Library: /home/iago/recicla-library  (4 components indexed)
Workspace: /home/iago/projects/medicina-leal
Scanned: 142 files

Candidates (3):
  [1] src/utils/jwt-validator.py            2.1 KB   function   marker: yes
  [2] prompts/anamnese-clinica.md           4.3 KB   prompt     marker: no
  [3] schemas/patient.schema.json           1.2 KB   schema     marker: yes

Skipped (2):
  - src/utils/old_jwt.py                    duplicate_hash_in_library (c-a3f9b2e1)
  - src/handlers/billing.py                 not_eligible

Use 'recicla extract --component <path>' to extract specific candidates.
```

### Códigos de saída

- `0` sempre (mesmo sem candidatos, mesmo se Library acabou de ser criada).
- `1` se `<workspace>` não existe ou não é diretório.

---

## 2. `extract` — Mover componente para a Library

### Sintaxe

```bash
python recicla.py extract \
  --component <path> [--component <path>...] \
  --workspace <path> \
  --library <path> \
  [--json]
```

### Argumentos

| Argumento | Default | Descrição |
|---|---|---|
| `--component` | (obrigatório) | Caminho do componente. Relativo ao workspace ou absoluto. Repetível. |
| `--workspace` | `.` | Raiz do projeto. |
| `--library` | `$RECICLA_LIBRARY` | Library. |
| `--json` | `false` | Saída JSON. |

### Pré-condições por componente

1. Arquivo existe.
2. Arquivo passa pelo pipeline de elegibilidade do `scan` (não há sentido em extrair excluído).
3. Arquivo não é binário.
4. Hash não está em `index.json` (não duplicar Library).
5. Hash não está em `manifest.json` com `direction: extracted` (idempotência).

Componentes que falham qualquer pré-condição vão para `skipped[]` com `reason`. A operação **continua** com os demais.

### Fluxo por componente

1. Calcular `sha256` e derivar `component_id`.
2. Parsear header de metadados. Aplicar defaults para campos ausentes.
3. Determinar `library_relpath`: `components/<category>s/<name>.<ext>`. Se já existe arquivo nesse caminho com hash diferente, sufixar `name`: `<name>-<sha256[:8]>.<ext>`.
4. Copiar bytes do arquivo do workspace para `<library>/<library_relpath>`.
5. Verificar pós-cópia: hash do arquivo na Library == `sha256` calculado. Se não bate, abortar com `error_io`, remover cópia parcial.
6. Adicionar entrada em `index.json`. Reordenar componentes por `added_at` ascendente. Atualizar `updated_at`.
7. Adicionar entrada em `manifest.json` com `direction: extracted`. Criar `manifest.json` se ausente.
8. Após todos os componentes processados, regenerar `INDEX.md`.

### Pós-condições

- `<library>/components/<category>s/<name>.<ext>` existe com bytes idênticos ao original.
- `index.json` da Library contém entrada para cada componente extraído.
- `manifest.json` do workspace contém entrada para cada componente, `direction: extracted`.
- `INDEX.md` regenerado refletindo estado atualizado.

### Saída legível

```
Extracted 2 components, skipped 1.

Extracted:
  ✓ c-a3f9b2e1  jwt-validator      ← src/utils/jwt-validator.py
  ✓ c-7b2e1f4d  anamnese-clinica   ← prompts/anamnese-clinica.md

Skipped:
  ✗ src/utils/jwt-validator.py.bak   reason: not_eligible (size_exceeded)

INDEX.md regenerated.
```

### Códigos de saída

- `0` se ao menos um componente extraído com sucesso.
- `1` se nenhum extraído (todos skipped ou todos falharam).
- `3` em erro de I/O (permissão, disco cheio).

---

## 3. `suggest` — Listar componentes da Library com afinidade

### Sintaxe

```bash
python recicla.py suggest \
  --library <path> \
  [--workspace <path>] \
  (--tags <csv> | --auto) \
  [--language <lang>] \
  [--category <cat>] \
  [--top <N>] \
  [--json]
```

### Argumentos

| Argumento | Default | Descrição |
|---|---|---|
| `--library` | `$RECICLA_LIBRARY` | Library. |
| `--workspace` | `.` | Necessário para `--auto` ou para marcar `already_in_workspace`. |
| `--tags` | (alternativo a `--auto`) | CSV de tags. Ex: `auth,jwt`. |
| `--auto` | `false` | Inferir tags do workspace (ver §3.3 abaixo). |
| `--language` | `null` | Filtro adicional por linguagem. |
| `--category` | `null` | Filtro adicional por categoria. |
| `--top` | `10` | Máximo de matches. |
| `--json` | `false` | Saída JSON. |

Pelo menos um de `--tags` ou `--auto` é obrigatório.

### Fluxo

1. Carregar `index.json`.
2. Determinar `query_tags`: vindas de `--tags` ou da inferência automática (§3.3).
3. Para cada componente em `index.json`:
   a. Aplicar filtros `--language` e `--category` se especificados.
   b. Calcular score Jaccard: `|c.tags ∩ query_tags| / |c.tags ∪ query_tags|`.
   c. Edge cases: se ambos vazios, score = 0. Se apenas component.tags vazio mas filtros de language/category passam, score = 0.01 (presença mínima > exclusão).
4. Marcar `already_in_workspace` se `component_id` em `manifest.json` do workspace (qualquer direction).
5. Ordenar por `score` desc, desempate por `added_at` desc.
6. Truncar a `--top`.
7. Emitir.

### §3.3 — Inferência automática de tags (`--auto`)

Sequência de fontes (cumulativa):

1. **`package.json`** (se existe na raiz do workspace):
   - Extrai chaves de `dependencies` e `devDependencies`. Filtra a top-50 mais relevantes (lista hardcoded — ver `recicla.py`).
2. **`pyproject.toml`**:
   - Parsing simples (não usa `tomllib` para compat com Python 3.9 — usa regex pra extrair strings de `[tool.poetry.dependencies]` ou `[project] dependencies = [...]`).
3. **`Cargo.toml`**:
   - Extrai chaves de `[dependencies]`.
4. **`go.mod`**:
   - Extrai linhas `require <pkg>`. Pega último segmento do path.
5. **`README.md`** e **`ARCHITECTURE.md`** se existem:
   - Tokeniza primeiros 500 chars (após header). Filtra stopwords (lista pequena: `the, and, or, but, this, that, a, an, is, are, was, were, in, on, at, of, for, to, with, by` etc.). Mantém tokens com 3-20 chars, lowercase.
6. **Linguagens detectadas**:
   - Walk leve no workspace contando extensões. Adiciona top-3 linguagens como tags.

União de todos os conjuntos. Limita a 30 tags inferidas.

### Saída legível

```
Library: /home/iago/recicla-library
Query: tags=[auth, jwt], language=python (auto-inferred: false)

Top 5 matches:
  [1] c-a3f9b2e1  jwt-validator        score: 0.67  ← function, py
       Tags: auth, jwt, security
       Valida JWT contra issuer e audience configuráveis.
       components/functions/jwt-validator.py

  [2] c-1d4e7c2b  oauth-handler        score: 0.33  ← function, py
       Tags: auth, oauth
       Handler genérico de OAuth 2.0 callback.
       components/functions/oauth-handler.py

  ...

Use 'recicla inject --id <ID> --target <path>' to import.
```

### Códigos de saída

- `0` sempre.

---

## 4. `inject` — Copiar componente da Library para o workspace

### Sintaxe

```bash
python recicla.py inject \
  (--id <component_id> | --library-relpath <path>) \
  --library <path> \
  --workspace <path> \
  --target <relpath> \
  [--force] \
  [--json]
```

### Argumentos

| Argumento | Default | Descrição |
|---|---|---|
| `--id` | (alternativo) | `component_id` na Library. |
| `--library-relpath` | (alternativo) | Caminho relativo na Library. Útil pra desambiguação manual. |
| `--library` | `$RECICLA_LIBRARY` | Library. |
| `--workspace` | `.` | Workspace destino. |
| `--target` | (obrigatório) | Caminho destino, relativo ao workspace. |
| `--force` | `false` | Sobrescrever destino se existir e tiver hash diferente. |
| `--json` | `false` | Saída JSON. |

### Pré-condições

1. Componente existe na Library (resolvido por `--id` ou `--library-relpath`).
2. Hash na Library bate com `sha256` em `index.json`.
3. `<target>` é caminho relativo ao workspace (não absoluto).
4. Diretório pai de `<target>` existe ou pode ser criado.

### Fluxo

1. Resolver componente: lookup em `index.json` por `--id` ou `--library-relpath`. Se ambíguo: erro.
2. Carregar `manifest.json` do workspace.
3. Verificar idempotência:
   - Se `component_id` já em manifesto com `direction: injected` e `workspace_relpath == target` → status `already_injected`. Não faz nada.
4. Verificar destino:
   - Se `<target>` existe:
     - Hash bate com componente da Library → status `identical_file_at_destination`. Apenas registra no manifesto se ainda não estava.
     - Hash não bate e `--force` ausente → status `conflict`. Exit code 2.
     - Hash não bate e `--force` presente → sobrescrever.
   - Se `<target>` não existe → criar diretórios pai, copiar.
5. Verificar pós-cópia: hash do destino == hash do componente.
6. Registrar em `manifest.json` com `direction: injected`, `sha256_at_op`, `timestamp`.

### Pós-condições

- `<workspace>/<target>` existe com bytes idênticos ao componente da Library.
- `manifest.json` registra a operação.
- `index.json` e `INDEX.md` **inalterados**.

### Saída legível

```
Injected c-a3f9b2e1 (jwt-validator) → src/lib/jwt.py
Status: ok
Manifest updated.
```

Variantes:
```
Status: already_injected. No changes.

Status: identical_file_at_destination. Manifest updated.

Status: conflict. File exists with different content. Use --force to overwrite.
  Existing hash:  4d8a91...
  Component hash: 8f3cab...
```

### Códigos de saída

- `0` ok ou `already_injected` ou `identical_file_at_destination`.
- `1` componente não encontrado, target absoluto, ambiguidade.
- `2` conflito sem `--force`.
- `3` erro de I/O.

---

## 5. `audit` — Verificar integridade

### Sintaxe

```bash
python recicla.py audit \
  --workspace <path> \
  --library <path> \
  [--json]
```

### Argumentos

| Argumento | Default | Descrição |
|---|---|---|
| `--workspace` | `.` | Workspace. Pode ser omitido para audit só da Library. |
| `--library` | `$RECICLA_LIBRARY` | Library. |
| `--json` | `false` | Saída JSON. |

### Fluxo

**Library checks:**

1. Para cada componente em `index.json`:
   a. Verifica que arquivo existe em `<library>/<library_relpath>`. Senão: `library_file_missing` (error).
   b. Calcula SHA-256 do arquivo. Se ≠ `sha256` no índice: `library_hash_drift` (error).
2. Verifica unicidade de `sha256` em `index.json`. Duplicatas: `library_duplicate_hash` (error).
3. Verifica que `INDEX.md` existe e é mais recente que `index.json`. Senão: `index_md_stale` (info).

**Workspace checks (se `--workspace` fornecido e `manifest.json` existe):**

4. Para cada entrada em `manifest.json`:
   a. Verifica que `<workspace>/<workspace_relpath>` existe. Senão: `manifest_orphan` (warn).
   b. Calcula SHA-256 atual. Se ≠ `sha256_at_op`: `workspace_hash_drift` (warn).
5. Para entradas com `direction: injected`:
   a. Verifica que `component_id` ainda existe em `index.json`. Senão: `injected_component_removed_from_library` (warn).

### Pós-condições

- Nenhuma escrita. Operação read-only.

### Saída legível

```
Audit summary:
  Library:    /home/iago/recicla-library
  Workspace:  /home/iago/projects/medicina-leal

  ℹ INFO:  0
  ⚠ WARN:  1
  ✗ ERROR: 1

Findings:

[ERROR] library_hash_drift
  Component: c-a3f9b2e1 (jwt-validator)
  Index claims: sha256:8f3cab47...
  Actual:       sha256:9e2ab815...
  → File on disk diverges from index. Library corrupted; investigate.

[WARN]  manifest_orphan
  Component: c-7b2e1f4d (anamnese-clinica)
  Workspace path: prompts/anamnese-clinica.md (file missing)
  → Component injected/extracted but file removed. Manifest stale.
```

### Códigos de saída

- `0` sem findings de severity ≥ warn.
- `1` com findings `warn` mas nenhum `error`.
- `2` com findings `error`.

---

## 6. `render-index` — Regenerar INDEX.md

### Sintaxe

```bash
python recicla.py render-index --library <path>
```

### Argumentos

| Argumento | Default | Descrição |
|---|---|---|
| `--library` | `$RECICLA_LIBRARY` | Library. |

### Fluxo

1. Carregar `index.json`.
2. Renderizar `INDEX.md` segundo regras em `schemas.md` §3.
3. Sobrescrever `<library>/INDEX.md`.

### Pós-condições

- `INDEX.md` reflete `index.json` atual.
- Idempotente: rodar duas vezes seguidas produz mesmo arquivo (com `Updated:` divergindo apenas no timestamp).

### Saída

```
INDEX.md regenerated. 23 components rendered across 4 categories.
```

### Códigos de saída

- `0` sucesso.
- `1` `index.json` ausente ou inválido.

---

## 7. `bundle-init` — Criar declaração local de bundle

### Sintaxe

```
recicla bundle-init
  --name <slug>
  --members <path1,path2,...>
  [--workspace <path>]
  [--description "<texto>"]
  [--tags <t1,t2,...>]
  [--force]
  [--json]
```

### Argumentos

| Flag | Obrigatório | Descrição |
|---|---|---|
| `--name` | sim | Slug do bundle. Regex: `^[a-z0-9][a-z0-9-]{0,63}$`. |
| `--members` | sim | CSV de paths workspace-relativos. Cada path deve existir e ser arquivo. |
| `--workspace` | não | Workspace path. Default: `.`. |
| `--description` | não | Texto livre. |
| `--tags` | não | CSV de tags. |
| `--force` | não | Sobrescrever declaração existente. |
| `--json` | não | Saída JSON em stdout. |

### Pré-condições

- Workspace existe.
- `name` casa o regex.
- Pelo menos um membro.
- Cada `--members` é relativo (não absoluto), aponta para arquivo existente, e não escapa do workspace via `..`.
- Não há membros duplicados na lista.
- Se `.recicla/bundles/<name>.json` já existe e `--force` não foi passado → exit 2.

### Fluxo

1. Validar argumentos.
2. Para cada membro: inferir `bundle_relpath` como o `basename` do path. Se houver colisão de basenames entre membros, prefixar com o nome do diretório-pai (`<parent>/<basename>`); se ainda colidir, sufixar (`<parent>2/<basename>`).
3. Montar declaração com `version: 1.0`, `entrypoint: null`, `role: ""` em todos os membros.
4. Criar `.recicla/bundles/` se ausente.
5. Escrever JSON com `sort_keys=True, indent=2`.

### Pós-condições

- Arquivo `.recicla/bundles/<name>.json` existe e validado por `validate_bundle_decl`.
- Nada na Library é tocado.

### Saída legível

```
Created .recicla/bundles/rag-pipeline.json
Bundle 'rag-pipeline' template with 5 members.
Edit bundle_relpath/role/entrypoint as needed, then run 'recicla bundle-extract --name rag-pipeline'.
```

### Códigos de saída

| Code | Significado |
|---|---|
| 0 | Declaração criada. |
| 1 | Argumento inválido (membro inexistente, name inválido, path absoluto). |
| 2 | Conflito (declaração existe, sem `--force`). |

---

## 8. `bundle-extract` — Registrar bundle na Library

### Sintaxe

```
recicla bundle-extract
  --name <slug>
  [--workspace <path>]
  [--library <path>]
  [--extract-members]
  [--max-size <bytes>]
  [--json]
```

### Argumentos

| Flag | Obrigatório | Descrição |
|---|---|---|
| `--name` | sim | Nome do bundle (slug). Espera `.recicla/bundles/<name>.json` no workspace. |
| `--workspace` | não | Default: `.`. |
| `--library` | não | Default: `$RECICLA_LIBRARY`. |
| `--extract-members` | não | Side-effect: extrai membros não-extraídos antes de registrar. |
| `--max-size` | não | Para o auto-extract eventual. |
| `--json` | não | Saída JSON. |

### Pré-condições

- `.recicla/bundles/<name>.json` existe e passa em `validate_bundle_decl`.
- Cada membro `workspace_relpath` aponta para arquivo existente.
- Para cada membro, `sha256(workspace_file)` resolve para um `component_id` na Library — OU `--extract-members` está presente.
- Sem `--extract-members`, qualquer membro não-resolvido é erro.

### Fluxo

1. Ler e validar declaração local.
2. Para cada membro, calcular `sha256(workspace_relpath)`.
3. Procurar componente na Library com mesmo hash.
4. Se algum membro não tem match e `--extract-members` está presente: invocar `cmd_extract` para os faltantes (mesmo workspace, mesma library, `--json` para suprimir output humano).
5. Re-resolver após extract para obter `component_id`s definitivos.
6. Calcular `bundle_id` = `compute_bundle_id(name, members_for_id)` (ver SPEC §6.4).
7. Se `bundle_id` já está em `index.json.bundles[]` → idempotente, `status: already_registered`, `registered: false`.
8. Caso contrário: se já existe bundle com mesmo `name` e `superseded_by: null`, marcá-lo com `superseded_by = <novo_bundle_id>`.
9. Adicionar novo bundle a `index.json.bundles[]`.
10. Reescrever `index.json` e regenerar `INDEX.md`.

### Pós-condições

- Library tem o bundle registrado.
- Bundles superseded permanecem no index com `superseded_by` apontando para o novo (histórico imutável).
- `INDEX.md` regenerado.

### Saída legível

```
Auto-extracted 5 members:
  - src/processing/transcriber.py
  ...

Bundle b-678bc190 (rag-pipeline) registered with 5 members.
Previous bundle b-aaaa1111 marked as superseded.
INDEX.md regenerated.
```

### Códigos de saída

| Code | Significado |
|---|---|
| 0 | Bundle registrado ou já registrado (idempotente). |
| 1 | Pré-condição falhou (declaração inválida, membro ausente, member não-extraído sem flag). |

---

## 9. `bundle-inject` — Materializar bundle no workspace

### Sintaxe

```
recicla bundle-inject
  (--id <bundle_id> | --name <slug>)
  [--library <path>]
  [--workspace <path>]
  [--target-root <relpath>]
  [--remap <orig=new>]...
  [--force]
  [--allow-superseded]
  [--json]
```

### Argumentos

| Flag | Obrigatório | Descrição |
|---|---|---|
| `--id` ou `--name` | sim | Identifica o bundle. Mutuamente exclusivos. |
| `--library` | não | Default: `$RECICLA_LIBRARY`. |
| `--workspace` | não | Default: `.`. |
| `--target-root` | não | Prefixo workspace-relativo para todos os destinos. Default: vazio (raiz). |
| `--remap` | não | Repetível: `--remap <bundle_relpath>=<override_relpath>`. |
| `--force` | não | Sobrescrever destino com hash divergente. |
| `--allow-superseded` | não | Permitir injetar bundle marcado como `superseded_by`. |
| `--json` | não | Saída JSON. |

### Pré-condições

- Bundle existe no `index.json.bundles[]`.
- Bundle não tem `superseded_by`, OU `--allow-superseded` foi passado.
- Para cada membro: `component_id` está no index e o arquivo na Library tem hash que bate.
- `--target-root` é relativo e não escapa do workspace.
- Cada `--remap target` é relativo, sem `..`, não absoluto.
- Nenhum par de membros mapeia para o mesmo destino final (path collision detectada antes da escrita).

### Fluxo

1. Resolver bundle por `--id` ou `--name`.
2. Validar que não está superseded (ou flag explícita).
3. Construir plano: para cada membro, `dest_rel = target_root / remap.get(bundle_relpath, bundle_relpath)`.
4. Detectar path collision dentro do plano. Se houver → erro, exit 2.
5. Verificar idempotência: se o manifesto local já tem entrada de bundle com mesmo `bundle_id`, mesmo `target_root`, mesmo `remap` (normalizado por sort) → `status: already_injected`, exit 0 sem escrita.
6. Pré-checar conflitos: para cada destino existente, comparar hash. Se diverge e sem `--force` → `status: conflict`, exit 2.
7. **Cópia atômica:** antes de cada escrita, salvar bytes anteriores se arquivo existia. Em caso de falha em qualquer membro, reverter todos os anteriores (restaurar bytes ou apagar arquivo criado).
8. Após sucesso, registrar no manifesto:
   - Cada membro como entrada granular em `manifest.components[]` com `direction: injected` e `via_bundle: <bundle_id>`.
   - Uma entrada agregada em `manifest.bundles[]` com `target_root`, `remap` normalizado, `members_count`.

### Pós-condições

- Workspace tem N arquivos materializados em destinos calculados.
- Manifesto registra cada membro + entrada agregada de bundle.
- Library inalterada.

### Saída legível

```
Injecting bundle b-678bc190 (rag-pipeline) into /tmp/another_app...
  → lib/audio/pipeline/transcriber.py  (from c-a9e3ffaa)
  → lib/audio/pipeline/chunker.py      (from c-1e98127f)
  ...

5 members injected. Manifest updated.
```

### Códigos de saída

| Code | Significado |
|---|---|
| 0 | Bundle injetado, ou já injetado (idempotente). |
| 1 | Pré-condição falhou (bundle não existe, library_hash_drift, --remap inválido). |
| 2 | Conflito: destino existe com hash divergente sem `--force`, ou path collision no plano. |
| 3 | Falha de I/O durante cópia (após revert). |

---

## 10. Tratamento de erros — princípios gerais

1. **Erros não-fatais por item.** Em comandos com múltiplos itens (`extract`, `audit`), erro em um item não interrompe os demais. Item vai para `skipped[]` ou `findings[]`.

2. **Erros fatais abortam o comando.** Library ausente sem permissão de criação, JSON do `index` corrompido, falha de I/O em região crítica → exit ≠ 0 e mensagem clara em stderr.

3. **Sem rollback parcial.** Se `extract` falha no meio de N componentes, os já extraídos permanecem extraídos. `index.json` e `manifest.json` são atualizados incrementalmente após cada cópia bem-sucedida. Re-execução é segura (idempotência cobre os já feitos).

4. **`--json` nunca quebra o formato.** Mesmo em erro, saída com `--json` é JSON válido com `ok: false` e `errors: [...]`.

5. **Stderr vs stdout.** `--json` vai para stdout. Mensagens de erro humanas vão para stderr. Tabelas legíveis vão para stdout.

---

## 11. Variáveis de ambiente

| Variável | Uso |
|---|---|
| `RECICLA_LIBRARY` | Default para `--library`. |
| `RECICLA_MAX_SIZE` | Default para `--max-size` em `scan`. Override por `--max-size`. |
| `RECICLA_CONFIG` | Caminho para `config.json` alternativo. Default: `$XDG_CONFIG_HOME/recicla/config.json` ou `~/.config/recicla/config.json`. |

Precedência: argumento CLI > variável de ambiente > arquivo de config > default.
