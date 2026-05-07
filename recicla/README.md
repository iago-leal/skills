# recicla

Skill agnóstica de modelo/harness para gestão determinística de **componentes** e **bundles** reutilizáveis entre projetos. Identifica candidatos no workspace, extrai para uma Library global, mantém `INDEX.md` consultável por agentes, e injeta de volta em novos workspaces — tudo via um único CLI Python (stdlib only).

A partir da v1.1.0, além de componentes individuais (1 arquivo = 1 ativo), `recicla` cataloga **bundles**: composições nomeadas de N arquivos onde o ativo reutilizável vive na **composição** (pipelines, esqueletos arquiteturais, scaffolds multi-arquivo).

## Instalação

### Claude.ai (web)

Coloque o diretório `recicla/` em `/mnt/skills/user/recicla/`. A skill é detectada automaticamente.

### Claude Code (local)

```bash
mkdir -p ~/.claude/skills
cp -r recicla ~/.claude/skills/
```

### Outras integrações

A skill é agnóstica de harness. Para usar fora dos clientes Anthropic, basta executar o script diretamente:

```bash
python3 recicla/scripts/recicla.py --help
```

## Configuração

A skill exige uma variável de ambiente apontando para o diretório global:

```bash
export RECICLA_LIBRARY="$HOME/recicla-library"
```

Adicione ao seu `~/.bashrc` / `~/.zshrc`. O diretório é criado automaticamente na primeira invocação.

Variáveis adicionais opcionais:

- `RECICLA_MAX_SIZE` — limite em bytes para arquivos elegíveis (default: `51200`, i.e. 50KB)
- `RECICLA_CONFIG` — caminho para arquivo de configuração JSON

## Uso rápido

### Componentes (arquivo único)

```bash
# Identifica candidatos no workspace
python3 recicla/scripts/recicla.py scan

# Extrai um componente para a Library
python3 recicla/scripts/recicla.py extract --component lib/jwt-validator.py

# Sugere componentes da Library
python3 recicla/scripts/recicla.py suggest --tags auth,jwt

# Filtrar só componentes (excluir bundles)
python3 recicla/scripts/recicla.py suggest --tags auth --type component

# Injeta um componente
python3 recicla/scripts/recicla.py inject --id c-490a4774 --target lib/jwt.py
```

### Bundles (composições nomeadas)

```bash
# 1. Criar declaração local de bundle
python3 recicla/scripts/recicla.py bundle-init \
  --name rag-pipeline \
  --members src/transcribe.py,src/chunk.py,src/retrieve.py,src/generate.py \
  --description "Pipeline RAG canônico" \
  --tags rag,llm,pipeline

# 2. (Opcional) Editar .recicla/bundles/rag-pipeline.json:
#    - ajustar bundle_relpath para topologia desejada
#    - preencher role e entrypoint

# 3. Registrar bundle na Library (auto-extrai membros se necessário)
python3 recicla/scripts/recicla.py bundle-extract --name rag-pipeline --extract-members

# 4. Em outro projeto, injetar bundle inteiro
python3 recicla/scripts/recicla.py bundle-inject --name rag-pipeline --target-root lib/audio
```

### Manutenção

```bash
# Audita Library + workspace (drift, member missing, definition drift)
python3 recicla/scripts/recicla.py audit --workspace .

# Regenera INDEX.md a partir de index.json (função pura)
python3 recicla/scripts/recicla.py render-index
```

Todos os comandos aceitam `--json` para saída programática (envelope `{command, version, ok, data, errors}`).

## Quando usar bundle vs componente

- **Componente** — 1 arquivo é o ativo. Função, prompt, schema, snippet auto-suficiente.
- **Bundle** — composição entre 2+ arquivos é o ativo. Pipeline com N estágios; scaffold de feature; padrão arquitetural cuja topologia interna importa.

Heurística operacional: se cada arquivo isoladamente seria reescrito do zero em outro projeto mas o **padrão** entre eles é replicável → bundle.

## Estrutura entregue

```
recicla/
├── SKILL.md                          # Frontmatter + manual operacional
├── SPEC.md                           # Especificação formal v1.1.0 — reconstruível por skill-creator
├── README.md                         # Este arquivo
├── reference/
│   ├── schemas.md                    # Schemas JSON (index, manifest, declaração de bundle, saídas)
│   ├── eligibility_criteria.md       # Pipeline de filtros para componentes
│   └── operations.md                 # Contratos formais dos 9 subcomandos
└── scripts/
    └── recicla.py                    # CLI completa (~2700 linhas, stdlib only)
```

## Reconstrução

A `SPEC.md` é projetada para ser auto-suficiente: passe ao `skill-creator` e qualquer modelo competente reconstrói a skill com aderência idêntica aos contratos formais e às invariantes I1–I9.

## Versão

`recicla` v1.1.0 — schemas `index.json` v1.1, `manifest.json` v1.1, declaração de bundle v1.0.

Migração v1.0 → v1.1 é silenciosa (read-time) e backward-compatible: libraries antigas ganham `bundles: []` automaticamente; manifestos antigos ganham `bundles: []` e `via_bundle: null` em cada entry de componente.
