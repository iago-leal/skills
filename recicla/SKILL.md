---
name: recicla
description: Gestão determinística de componentes e bundles reutilizáveis entre projetos. Identifica componentes extraíveis no workspace, copia para biblioteca global, mantém INDEX.md consultável por agentes de IA, e executa o caminho inverso. Bundles capturam composições nomeadas de N arquivos (pipelines, esqueletos arquiteturais). Manifesto local previne duplicatas. ATIVE SEMPRE que o usuário digitar /recicla, /recicla scan, /recicla extract, /recicla suggest, /recicla inject, /recicla audit, /recicla bundle-init, /recicla bundle-extract ou /recicla bundle-inject. Ative ao pedir "extrair componente reutilizável", "salvar pipeline reusável", "extrair conjunto de arquivos relacionados", "molde de arquitetura", "reaproveitar código entre projetos", ou mencionar `RECICLA_LIBRARY` ou `INDEX.md`. Ative proativamente ao terminar sessão produzindo utilitário, prompt, schema, template, função genérica ou padrão de pipeline que serviria noutro projeto. NÃO ative para refatoração interna ao próprio repo.
---

# recicla — Reciclagem Determinística de Componentes e Bundles

## Fundamento

Componente reutilizável produzido num projeto e nunca mais visto é desperdício de capital cognitivo. A maioria das soluções para isso falha por dois motivos: (1) são heurísticas baseadas em "intuição do modelo" — irreprodutíveis entre sessões e modelos —, ou (2) dependem de um harness específico (Cursor, Copilot, plugin proprietário) que prende o usuário num ecossistema.

`recicla` resolve isso operando em três invariantes:

1. **Determinismo total.** Critérios de elegibilidade explícitos, hashes SHA-256 como identidade de componente, schemas JSON fixos, scripts em Python stdlib. Mesmo input → mesmo output em qualquer ambiente que tenha Python 3.9+.
2. **Agnosticismo de modelo e harness.** A skill não depende de capacidade específica de nenhum LLM. O modelo apenas invoca scripts e apresenta resultados. Pode ser executada por Claude, GPT, Gemini, Llama local ou um humano via CLI.
3. **Bidirecionalidade com proteção contra duplicatas.** Workspace → Library (extração) e Library → Workspace (injeção) compartilham o mesmo manifesto local, que registra todo componente já tocado. Hash batendo → operação idempotente.

Quando o ativo reusável vive na **composição entre N arquivos** (pipeline RAG, esqueleto de microserviço, padrão de plugin), não num arquivo isolado, use **bundles** (§Bundles abaixo). Bundle é uma camada acima de componente: referencia componentes existentes pelo `component_id` e fixa o layout interno em que devem ser materializados juntos.

A skill **não toma decisões inteligentes**. Apenas executa um pipeline com saída JSON estruturada, e delega ao usuário (ou ao modelo, sob supervisão) a confirmação das ações destrutivas (cópia, sobrescrita, atualização de versão).

---

## Configuração obrigatória

A skill requer uma variável de ambiente `RECICLA_LIBRARY` apontando para o diretório global de componentes do usuário.

```bash
export RECICLA_LIBRARY="$HOME/recicla-library"
```

Sugerir ao usuário adicionar à shell de inicialização (`~/.bashrc`, `~/.zshrc`) na primeira execução. Caminho alternativo: arquivo `~/.config/recicla/config.json` com `{"library_path": "..."}`.

Na primeira execução em uma library nova, a skill cria a estrutura mínima:

```
$RECICLA_LIBRARY/
├── index.json          # fonte de verdade (components + bundles) — NÃO editar à mão
├── INDEX.md            # view legível — regenerado a partir de index.json
└── components/         # arquivos de componentes, organizados por categoria
    ├── prompts/
    ├── templates/
    ├── functions/
    ├── schemas/
    ├── snippets/
    └── configs/
```

`bundle-init` é a única operação que **não** requer `RECICLA_LIBRARY` — cria apenas o template local da declaração.

---

## Operações (subcomandos)

A skill expõe nove operações, todas via `python scripts/recicla.py <subcomando> [args]`. Cada uma tem contrato JSON definido em `reference/operations.md`.

### Operações sobre componentes

| Operação | Direção | O que faz |
|---|---|---|
| `scan` | Workspace → (proposta) | Lista candidatos a extração + bundles declarados localmente. |
| `extract` | Workspace → Library | Copia componente confirmado para a Library, atualiza `index.json`, registra no manifesto local. |
| `suggest` | Library → (proposta) | Lista componentes **e bundles** da Library com afinidade ao workspace atual. Filtro `--type component\|bundle\|all`. |
| `inject` | Library → Workspace | Copia componente individual da Library para o workspace, registra no manifesto local. |
| `audit` | Library + Workspace | Verifica integridade — manifestos órfãos, hashes divergentes, drift de bundles, membros faltando. |
| `render-index` | Library | Regenera `INDEX.md` a partir de `index.json`. |

### Operações sobre bundles

| Operação | Direção | O que faz |
|---|---|---|
| `bundle-init` | Workspace (offline) | Cria template `.recicla/bundles/<name>.json` a partir de uma lista de membros. Não toca a Library. |
| `bundle-extract` | Workspace → Library | Lê declaração local, valida pré-condições, registra bundle no `index.json`. Opcional `--extract-members` extrai os membros faltantes antes de registrar. |
| `bundle-inject` | Library → Workspace | Materializa todos os membros do bundle no workspace, sob `--target-root`, com `--remap` opcional. Operação atômica com revert em falha. |

Detalhes de cada operação, contratos de saída e fluxos de erro: `reference/operations.md`.

---

## Critérios de elegibilidade (componentes)

A operação `scan` aplica um pipeline determinístico de filtros. Detalhamento completo em `reference/eligibility_criteria.md`. Resumo:

**Inclusão (basta um critério):**
1. Header de marcação explícita: arquivo contém em qualquer linha `@recicla:reusable`.
2. Localização canônica: arquivo em `lib/`, `utils/`, `shared/`, `components/`, `helpers/`, `templates/`, `prompts/`, `schemas/`, `snippets/`.

**Exclusão (qualquer um descarta):**
1. Sob `.git/`, `node_modules/`, `__pycache__/`, `dist/`, `build/`, `.venv/`, `venv/`, `target/`, `.next/`, `.cache/`, `.recicla/`.
2. Tamanho > 50 KB (configurável via `--max-size`).
3. Arquivo binário (heurística: byte nulo nos primeiros 8 KB).
4. Hash já presente em `.recicla/manifest.json` do workspace atual (já processado).
5. Hash já presente em `index.json` da Library (já catalogado a partir de outro workspace).

A skill **nunca** extrai sem confirmação explícita — o `scan` apenas lista.

Bundles **não** têm critérios de elegibilidade automáticos: são sempre declarados explicitamente pelo usuário em `.recicla/bundles/*.json`. `bundle-extract` recusa registrar se algum membro falha em `is_candidate` da extração de componentes (sem rebaixamento de critérios via bundle).

---

## Marcação de metadados em componentes

Para extração com metadados precisos (e portanto INDEX.md útil), o usuário pode anotar o componente com um header. Formato deterministicamente parseável:

```python
# @recicla:reusable
# @recicla:name jwt-validator
# @recicla:category function
# @recicla:tags auth,jwt,security
# @recicla:description Valida JWT contra issuer e audience configuráveis.
```

Sintaxe de comentário varia por linguagem (`#`, `//`, `<!-- ... -->`, `;;`, `--`). O parser tolera qualquer prefixo de comentário e pesca apenas as linhas que começam com `@recicla:` (após o prefixo).

Se o header estiver ausente, a skill preenche com defaults:
- `name`: nome do arquivo sem extensão.
- `category`: derivada do diretório canônico (`prompts/` → `prompt`, etc.) ou `snippet` por fallback.
- `tags`: vazio.
- `description`: primeira linha não vazia do arquivo, truncada a 80 caracteres, ou `"(sem descrição)"`.

---

## Bundles — composições nomeadas de componentes

### Quando usar bundle vs componente

Heurística (julgamento humano, não regra do código):

- **Componente único:** o arquivo, sozinho, é o ativo. Outro projeto pode injetar e usar isolado.
- **Bundle:** ≥3 arquivos compartilham um propósito que se perde se separados. Imports relativos, contratos entre módulos, ordem de pipeline. Ativo é a topologia.
- **Caso de fronteira (2 arquivos, coesão fraca):** prefira componentes individuais.

### Declaração local

Bundle é declarado em `.recicla/bundles/<name>.json` no workspace de origem. Schema completo em `reference/schemas.md`. Exemplo:

```json
{
  "version": "1.0",
  "name": "rag-pipeline",
  "description": "Pipeline RAG canônico: transcribe → chunk → index → query → generate.",
  "tags": ["rag", "llm", "pipeline"],
  "entrypoint": "pipeline/retriever.py",
  "members": [
    {"workspace_relpath": "src/processing/transcriber.py", "bundle_relpath": "pipeline/transcriber.py", "role": "transcribe"},
    {"workspace_relpath": "src/processing/chunker.py",     "bundle_relpath": "pipeline/chunker.py",     "role": "chunk"},
    {"workspace_relpath": "src/processing/vector_db.py",   "bundle_relpath": "pipeline/vector_db.py",   "role": "index"},
    {"workspace_relpath": "src/processing/retriever.py",   "bundle_relpath": "pipeline/retriever.py",   "role": "query"},
    {"workspace_relpath": "src/processing/generator.py",   "bundle_relpath": "pipeline/generator.py",   "role": "generate"}
  ]
}
```

Campos:
- `name`: slug `^[a-z0-9][a-z0-9-]{0,63}$`, único entre bundles ativos.
- `members[].workspace_relpath`: onde o membro está no workspace de origem.
- `members[].bundle_relpath`: layout interno canônico do bundle (preserva imports relativos). Não pode ser absoluto nem conter `..`.
- `members[].role`: string livre, metadado consultivo. Não afeta `bundle_id`.
- `entrypoint`: opcional, deve casar um dos `bundle_relpath`. Marca ponto de entrada para leitura/uso.
- `tags`, `description`: metadados.

### Identidade de bundle

```
bundle_id = "b-" + sha256(name + "|" + sorted("c-XXXX:bundle/path.py" for each member))[:8]
```

Implicação: **mudou nome, conjunto de membros ou layout interno → outro `bundle_id`**. `role`, `description`, `tags`, `entrypoint` **não** entram no cálculo.

Bundles são **imutáveis** na Library. Re-`bundle-extract` com mesma composição é idempotente. Re-extract com composição diferente cria novo `bundle_id` e marca o anterior com `superseded_by: <new_id>`. Histórico preservado.

---

## Manifesto local — `.recicla/manifest.json` (schema v1.1)

Cada workspace que tocou na Library tem um `.recicla/manifest.json` na raiz. Schema completo em `reference/schemas.md`. Estrutura:

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
      "sha256_at_op": "8f3c...",
      "timestamp": "2026-05-07T14:05:23Z",
      "via_bundle": null
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

`direction` em `components[]` é `"extracted"` ou `"injected"`. `via_bundle` é o `bundle_id` se o componente entrou via `bundle-inject`, ou `null` em operações granulares. `bundles[]` registra entrada agregada por `bundle-inject` para idempotência por `(bundle_id, target_root, remap)`.

Manifestos v1.0 são migrados em read-time silenciosamente: campos `bundles: []` e `via_bundle: null` são adicionados na primeira escrita.

---

## INDEX.md — formato consultável por agente

`INDEX.md` é regenerado pela skill a partir de `index.json`. Nunca editar à mão. O formato é otimizado para que um agente de IA, ao receber o arquivo no contexto, consiga em uma passagem responder "tenho componente que serve para X?" ou "tenho um bundle desse padrão?". Estrutura:

```markdown
# Component Library Index

> Generated by `recicla` — do not edit manually. Source of truth: `index.json`.
> Updated: 2026-05-07T16:30:00Z
> Components: 23
> Bundles: 4

## Quick lookup
| ID | Name | Category | Tags | Path |
| `c-a3f9b2e1` | jwt-validator | function | auth, jwt, security | `components/functions/jwt-validator.py` |
...

## Components by category
### Functions (8)
#### `c-a3f9b2e1` — jwt-validator
...

## Bundles
| ID | Name | Members | Tags | Entrypoint |
| `b-a1b2c3d4` | rag-pipeline | 5 | rag, llm, pipeline | `pipeline/retriever.py` |

### `b-a1b2c3d4` — rag-pipeline
- **Description:** Pipeline RAG canônico: transcribe → chunk → index → query → generate.
- **Tags:** rag, llm, pipeline
- **Entrypoint:** `pipeline/retriever.py`
- **Members (5):**
  | Component | Bundle path | Role |
  | `c-a1a1a1a1` | `pipeline/transcriber.py` | transcribe |
  ...
- **Inject:** `python recicla.py bundle-inject --id b-a1b2c3d4 --target-root <path>`

## Consultation protocol (for agents)
1. Filter Quick lookup by category/tags.
2. Read matched components' descriptions.
3. To import a component: `inject --id <ID> --target <path>`.
4. Never copy file contents from this index — always use `inject`/`bundle-inject`.
5. For composed patterns (pipelines, multi-file architectures), filter the Bundles table. Import via `bundle-inject` with `--target-root`.
```

A última seção é instrução para o próprio agente de IA — `recicla` espera ser usado por agentes, e o INDEX.md inclui o protocolo de consulta para reduzir ambiguidade.

---

## Workflow padrão (extração de componentes)

Quando o usuário pede `/recicla scan` ou similar:

1. Verificar `RECICLA_LIBRARY` setada. Se não, instruir configuração e parar.
2. Inicializar Library se não existir (criar estrutura mínima).
3. Inicializar manifesto local se não existir (`.recicla/manifest.json`).
4. Executar `python scripts/recicla.py scan --workspace . --library $RECICLA_LIBRARY --json`.
5. Apresentar tabela enxuta dos candidatos: `path | category | size | reason`. Se houver `bundle_candidates`, listá-los separados.
6. Perguntar ao usuário quais extrair (números, lista, ou `all`).
7. Para cada confirmado: `python scripts/recicla.py extract --component <path> [...]` (script lida com metadados, hash, gravação).
8. Após extração, `INDEX.md` é regenerado automaticamente.
9. Confirmar ao usuário: "Extraídos N componentes. INDEX.md atualizado."

Não fazer iteração de "reescrever para ficar mais reutilizável" — `recicla` move o que já existe. Refatoração é responsabilidade externa.

---

## Workflow padrão (extração de bundle)

Quando o usuário identifica que um conjunto de N arquivos é um padrão reusável:

1. Marcar cada arquivo individual com `@recicla:reusable` e tags relevantes (necessário — sem isso o membro falha em `is_candidate`).
2. `python scripts/recicla.py bundle-init --name <slug> --members <csv> [--description "..."] [--tags ...]` para criar o template em `.recicla/bundles/<slug>.json`.
3. Editar o template:
   - Ajustar `bundle_relpath` para refletir layout interno desejado (mantém imports relativos coerentes).
   - Anotar `role` em cada membro.
   - Definir `entrypoint` (opcional, mas recomendado).
4. `python scripts/recicla.py bundle-extract --name <slug> --extract-members` para registrar (com auto-extract dos membros faltantes em uma só chamada).
5. Confirmar ao usuário: `bundle_id` retornado, contagem de membros, supersede de versão anterior se houver.

---

## Workflow padrão (injeção)

Para componente individual:
1. `suggest --tags ...` ou `--auto` para listar candidatos. Saída diferencia `type: component | bundle`.
2. `inject --id <ID> --target <path>` materializa o arquivo.

Para bundle:
1. `suggest` filtrado por `--type bundle` se quiser só padrões compostos.
2. `bundle-inject --id <bundle_id> --target-root <path>` materializa todos os membros sob o prefixo. Layout interno do bundle é preservado.
3. `--remap orig=new` para renomear membros específicos sem afetar os demais.
4. `--force` para sobrescrever destinos existentes; sem isso, conflito pré-checado retorna `status: conflict` (exit 2) sem tocar nenhum byte.
5. `--allow-superseded` para injetar versão antiga (uso raro, debug histórico).

---

## Auditoria

`/recicla audit` ou `python scripts/recicla.py audit --workspace . --library $RECICLA_LIBRARY`:

Checks de **componentes**:
- `manifest_orphan`: arquivo registrado no manifest sumiu do workspace.
- `workspace_hash_drift`: arquivo no workspace foi modificado após extract/inject.
- `library_hash_drift`: arquivo na Library tem hash diferente do registrado em `index.json`.
- `library_file_missing`: `index.json` referencia arquivo que não existe.
- `library_duplicate_hash`: dois `component_id`s diferentes com mesmo `sha256` (caso patológico).
- `index_md_stale`: `INDEX.md` mais antigo que `index.json` (rodar `render-index`).
- `injected_component_removed_from_library`: componente injetado num workspace não existe mais no Index.

Checks de **bundles**:
- `bundle_member_missing`: bundle ativo referencia `component_id` ausente do Index.
- `bundle_definition_drift`: declaração local em `.recicla/bundles/<name>.json` calcularia um `bundle_id` que não está registrado (rodar `bundle-extract`).
- `injected_bundle_removed_from_library`: bundle injetado num workspace não existe mais no Index.

Saída JSON com classificação por severidade: `info | warn | error`. Exit code: 0 limpo, 1 warns, 2 errors.

Não corrige automaticamente — o usuário decide o que fazer com cada divergência.

---

## Invariantes (o que SEMPRE deve ser verdade)

1. `INDEX.md` é função pura de `index.json`. Reescrevê-lo manualmente é violação — qualquer execução posterior sobrescreve.
2. Todo componente na Library tem entrada em `index.json` com hash que bate com o conteúdo atual do arquivo.
3. Toda extração ou injeção (granular ou via bundle) produz uma entrada nova no manifesto local correspondente.
4. Hashes são SHA-256 do conteúdo binário do arquivo, sem normalização de whitespace.
5. IDs de componente são derivados deterministicamente: `c-` + primeiros 8 caracteres do SHA-256 do conteúdo no momento da primeira extração.
6. A skill nunca executa o conteúdo de componentes. Apenas copia bytes.
7. **Bundle imutável.** Bundle nunca é modificado após registro. Nova composição com mesmo nome → novo `bundle_id` + supersede do anterior.
8. **Bundle pina membros por `component_id`, não por path.** Atualização de um componente na Library cria um novo `component_id`; bundles existentes continuam apontando para o ID antigo (válido enquanto o ID antigo permanecer no Index).

---

## Referências

- `SPEC.md` — especificação formal completa, suficiente para reconstruir esta skill com qualquer modelo + skill-creator.
- `reference/schemas.md` — schemas JSON de `index.json`, `manifest.json`, declaração de bundle e saídas dos comandos.
- `reference/eligibility_criteria.md` — pipeline de filtros do `scan`, com exemplos.
- `reference/operations.md` — contratos de cada subcomando (entrada, saída, erros).
- `scripts/recicla.py` — implementação CLI única, Python stdlib, ~1900 linhas.

---

## Posição no ecossistema (opcional)

`recicla` opera ortogonalmente ao MDCU/RSOP — não substitui, não invoca, não é invocado. A diferença conceitual:

- **MDCU/RSOP:** prontuário e raciocínio **dentro** de um projeto.
- **`recicla`:** transferência de componentes e bundles **entre** projetos.

Pode ser invocado em qualquer fase de um projeto, em qualquer momento. O caso típico é após `commit-soap` numa sessão que produziu utilitário genérico (extract individual) ou um pipeline canônico (bundle) — antes de fechar o terminal, vale extrair.
