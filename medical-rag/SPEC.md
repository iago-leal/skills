# Spec: Skill `medical-rag`

## Propósito

Esta é a especificação determinística e reproduzível da skill `medical-rag`.
Qualquer agente que receba este documento e execute o Skill Creator DEVE produzir
a mesma skill, sem ambiguidade.

---

## 1. Identidade da Skill

| Campo | Valor |
|-------|-------|
| **Nome** | `medical-rag` |
| **Diretório** | `medical-rag/` (relativo ao diretório de skills do agente) |
| **Propósito** | Pipeline RAG multimodal local para processar, indexar e consultar livros médicos (PDF digital ou escaneado), com extração de texto via OCR e associação de imagens ao contexto textual |
| **Domínio** | Medicina (endocrinologia, clínica médica, qualquer especialidade) |
| **Privacidade** | 100% local e offline após instalação inicial das dependências. Nenhum dado é enviado para nuvem |

---

## 2. Estrutura de Arquivos (Obrigatória)

```
medical-rag/
├── SKILL.md                         # Instruções do agente (ver Seção 3)
├── SPEC.md                          # Este documento (referência imutável)
├── scripts/
│   ├── setup.py                     # Auto-bootstrap: cria venv + instala deps
│   ├── ingest.py                    # Pipeline: PDF → OCR → Chunks → ChromaDB + Imagens
│   ├── query.py                     # Busca híbrida (semântica + BM25) com imagens
│   └── manage.py                    # CRUD de coleções e livros indexados
└── references/
    └── chunking_strategies.md       # Estratégias de chunking para texto médico
```

---

## 3. SKILL.md — Conteúdo Obrigatório

### 3.1 Frontmatter YAML

```yaml
---
name: medical-rag
description: >
  Pipeline RAG multimodal local para processar, indexar e consultar livros
  médicos em PDF (digitais ou escaneados com OCR). Extrai texto E imagens,
  indexa em ChromaDB com embeddings biomédicos (BioLORD), e permite buscas
  semânticas com citação de fonte e imagens contextuais. Use esta skill SEMPRE
  que o usuário quiser indexar livros médicos, processar PDFs de medicina,
  pesquisar em livros de endocrinologia ou outras especialidades, fazer OCR
  em livros escaneados, criar uma base de conhecimento médica local, consultar
  textos médicos, ou mencionar "RAG", "indexar livro", "pesquisar no livro",
  "base de conhecimento", "OCR médico", "processar PDF escaneado", "buscar
  em livro", "endocrinologia", "livro de medicina". Também ative quando o
  usuário mencionar que quer "perguntar ao livro", "consultar referência
  médica", ou "extrair conteúdo de livro". NÃO ative para leitura simples
  de PDF (use a skill pdf), nem para anonimização de dados (use
  data-anonymizer).
---
```

### 3.2 Corpo do SKILL.md

O corpo DEVE conter as seguintes seções, nesta ordem:

#### Seção: Visão Geral
- Diagrama ASCII do pipeline: `PDF → OCR → Markdown → Chunks → Embeddings → ChromaDB ← Query`
- Nota: imagens são extraídas e associadas aos chunks por proximidade de página

#### Seção: Auto-configuração
- A skill se auto-instala na primeira execução de qualquer script
- Exige: Python 3.10+, Tesseract instalado no sistema (`brew install tesseract tesseract-lang`)
- Cria `.venv` isolado dentro do diretório da skill
- Diretório de dados: `~/.medical-rag/` (ChromaDB + imagens extraídas)

#### Seção: Configuração Inicial (Perguntas Obrigatórias)
Na PRIMEIRA execução do `ingest.py`, o script DEVE perguntar interativamente:

1. **Modelo de embeddings** (escolha obrigatória):
   - `[1] FremyCompany/BioLORD-2023-M` (RECOMENDADO — otimizado para terminologia biomédica, ~400MB)
   - `[2] all-MiniLM-L6-v2` (genérico, leve, ~80MB — menos preciso para medicina)
   - `[3] pritamdeka/S-PubMedBert-MS-MARCO` (PubMed, ~400MB — alternativa biomédica)
   - `[4] Outro` (o usuário digita o nome do modelo HuggingFace)

2. **Idiomas para OCR** (seleção múltipla):
   - `[1] Português (por)` ← pré-selecionado
   - `[2] Inglês (eng)` ← pré-selecionado
   - `[3] Espanhol (spa)`
   - `[4] Francês (fra)`
   - `[5] Alemão (deu)`
   - `[6] Outro` (o usuário digita o código ISO do Tesseract)

3. **Tamanho do chunk** (com default):
   - Default: `1000 tokens` com overlap de `200 tokens`
   - O usuário pode alterar ambos os valores
   - Nota explicativa: "Para livros de 1000+ páginas, 1000 tokens por chunk com 200 de overlap oferece bom equilíbrio entre contexto e precisão de busca"

As respostas são salvas em `~/.medical-rag/config.json` e reutilizadas em execuções futuras.
O usuário pode reconfigurar a qualquer momento com `python scripts/setup.py --reconfigure`.

#### Seção: Como Ingerir Livros
```bash
# Arquivo único
python scripts/ingest.py --file livro.pdf --collection endocrinologia [--json]

# Diretório com vários PDFs
python scripts/ingest.py --dir /pasta/pdfs/ --collection endocrinologia [--json]

# Forçar OCR em todas as páginas (mesmo as digitais)
python scripts/ingest.py --file livro.pdf --collection endo --force-ocr [--json]
```

#### Seção: Como Consultar
```bash
# Busca em uma coleção
python scripts/query.py --query "tratamento hipotireoidismo" --collection endocrinologia [--json]

# Busca em todas as coleções
python scripts/query.py --query "diabetes mellitus tipo 2" --all [--json]

# Controlar número de resultados
python scripts/query.py --query "fisiopatologia" --collection endo --n-results 10 [--json]

# Incluir imagens no resultado (default: true)
python scripts/query.py --query "histologia tireoide" --collection endo --with-images [--json]
```

#### Seção: Como Gerenciar
```bash
python scripts/manage.py --list [--json]
python scripts/manage.py --info endocrinologia [--json]
python scripts/manage.py --delete endocrinologia
python scripts/manage.py --delete-book endocrinologia "Harrison.pdf"
```

---

## 4. Scripts — Especificação Detalhada

### 4.1 `scripts/setup.py`

#### Responsabilidades
1. Criar `.venv` dentro do diretório da skill (se não existir)
2. Instalar dependências Python (ver Seção 5)
3. Verificar Tesseract instalado (`tesseract --version`)
4. Criar diretório `~/.medical-rag/` com subdiretórios:
   - `~/.medical-rag/chromadb/` — banco vetorial persistente
   - `~/.medical-rag/images/` — imagens extraídas dos PDFs
   - `~/.medical-rag/config.json` — configurações do usuário
5. Opção `--reconfigure`: re-executa as perguntas da Seção 3.2

#### Padrão de Implementação
- Seguir EXATAMENTE o padrão de `data-anonymizer-ollama/scripts/setup.py`:
  - Função `venv_python()` para resolver caminho do Python no venv
  - Função `run()` para executar subprocessos com log
  - Saída numerada `[1/N]`, `[2/N]`... para cada etapa
  - Print final com resumo e caminhos

#### CLI
```
python scripts/setup.py [--reconfigure]
```

---

### 4.2 `scripts/ingest.py`

#### Responsabilidades
1. **Self-bootstrap**: detectar ausência de `.venv` e rodar `setup.py` automaticamente, depois re-executar com o Python do venv (padrão `anonymize.py`)
2. **Carregar config**: ler `~/.medical-rag/config.json` (se não existir, perguntar interativamente — Seção 3.2)
3. **Extração de texto**: usar `pymupdf4llm.to_markdown()` com OCR automático
4. **Extração de imagens**: usar `pymupdf` para extrair imagens de cada página com posição (bounding box)
5. **Chunking**: dividir texto em chunks conforme config (default: 1000 tokens, 200 overlap)
6. **Associação imagem-chunk**: vincular imagens ao chunk cuja página de origem coincide
7. **Indexação**: inserir chunks no ChromaDB com metadados e referência a imagens
8. **Relatório**: imprimir/retornar estatísticas de ingestão

#### Lógica de Extração de Texto (Detalhe)
```python
import pymupdf4llm

md_text = pymupdf4llm.to_markdown(
    str(pdf_path),
    show_progress=True,
    # OCR é ativado automaticamente pelo pymupdf4llm em páginas sem texto
)
```
Se `--force-ocr` for passado, usar `pages` parameter para forçar OCR em todas.

#### Lógica de Extração de Imagens (Detalhe)
```python
import pymupdf

doc = pymupdf.open(str(pdf_path))
for page_num in range(len(doc)):
    page = doc[page_num]
    image_list = page.get_images(full=True)
    for img_info in image_list:
        xref = img_info[0]
        rects = page.get_image_rects(xref)
        img_data = doc.extract_image(xref)
        # Filtrar imagens muito pequenas (< 50x50 px) — são ícones/artefatos
        width = img_data["width"]
        height = img_data["height"]
        if width < 50 or height < 50:
            continue
        # Salvar em ~/.medical-rag/images/<collection>/<book_hash>/page_<N>_img_<xref>.<ext>
        ext = img_data["ext"]  # png, jpeg, etc.
        img_bytes = img_data["image"]
        # ... salvar no disco
```

#### Lógica de Chunking (Detalhe)
```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[dict]:
    """
    Divide texto em chunks com overlap.
    Tenta quebrar em limites de parágrafo (\n\n) quando possível.
    Cada chunk retorna: {"text": str, "start_char": int, "end_char": int}
    """
    # 1. Dividir por parágrafos primeiro
    # 2. Agrupar parágrafos até atingir chunk_size tokens
    # 3. Ao atingir, fechar chunk e iniciar próximo com overlap
    # 4. Manter marcadores de capítulo/seção (## Heading) no início do chunk
```

#### Metadados por Chunk no ChromaDB
Cada chunk DEVE ter estes metadados:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `source_file` | `str` | Nome do arquivo PDF original |
| `source_path` | `str` | Caminho absoluto do PDF |
| `book_title` | `str` | Título extraído do metadata do PDF, ou nome do arquivo |
| `page_start` | `int` | Primeira página coberta pelo chunk |
| `page_end` | `int` | Última página coberta pelo chunk |
| `chapter` | `str` | Capítulo detectado (header mais recente antes do chunk), ou "" |
| `chunk_index` | `int` | Índice sequencial do chunk no livro (0-based) |
| `total_chunks` | `int` | Total de chunks do livro |
| `image_paths` | `str` | Lista de caminhos de imagens associadas, separados por `|` |
| `collection` | `str` | Nome da coleção |
| `ingested_at` | `str` | Timestamp ISO 8601 da ingestão |

#### ID do Documento no ChromaDB
Formato: `{book_hash}_{chunk_index}` onde `book_hash` = primeiros 12 chars do SHA-256 do arquivo PDF.

#### CLI
```
python scripts/ingest.py --file <caminho.pdf> --collection <nome> [--force-ocr] [--json]
python scripts/ingest.py --dir <diretório/> --collection <nome> [--force-ocr] [--json]
```

#### Output JSON (`--json`)
```json
{
  "ingest": {
    "source": "Endocrinologia_Clinica.pdf",
    "collection": "endocrinologia",
    "pages_total": 1042,
    "pages_ocr": 1042,
    "pages_digital": 0,
    "chunks_created": 1580,
    "images_extracted": 342,
    "embedding_model": "FremyCompany/BioLORD-2023-M",
    "chunk_size_tokens": 1000,
    "overlap_tokens": 200,
    "duration_seconds": 847.3,
    "book_hash": "a1b2c3d4e5f6"
  }
}
```

---

### 4.3 `scripts/query.py`

#### Responsabilidades
1. **Self-bootstrap** (mesmo padrão)
2. **Busca semântica**: consultar ChromaDB com a query
3. **Reranking BM25**: re-ordenar top-K resultados usando BM25 para priorizar terminologia médica exata
4. **Associação de imagens**: para cada chunk retornado, incluir caminhos de imagens associadas
5. **Output**: resultados formatados com citação completa

#### Lógica de Busca Híbrida (Detalhe)
```python
# 1. Busca semântica: top 20 do ChromaDB
semantic_results = collection.query(
    query_texts=[query],
    n_results=20,
    include=["documents", "metadatas", "distances"]
)

# 2. Reranking BM25 sobre os 20 resultados semânticos
from rank_bm25 import BM25Okapi
tokenized_docs = [doc.split() for doc in semantic_results["documents"][0]]
bm25 = BM25Okapi(tokenized_docs)
bm25_scores = bm25.get_scores(query.split())

# 3. Score combinado: 0.7 * semantic_score + 0.3 * bm25_score (normalizado)
# 4. Retornar top N pelo score combinado
```

#### CLI
```
python scripts/query.py --query <texto> --collection <nome> [--n-results 5] [--with-images] [--json]
python scripts/query.py --query <texto> --all [--n-results 5] [--with-images] [--json]
```

#### Output JSON (`--json`)
```json
{
  "query": "fisiopatologia do hipotireoidismo",
  "collection": "endocrinologia",
  "n_results": 3,
  "results": [
    {
      "rank": 1,
      "text": "O hipotireoidismo primário resulta da falência da glândula tireoide...",
      "source_file": "Endocrinologia_Clinica.pdf",
      "book_title": "Endocrinologia Clínica — Vilar",
      "page_start": 142,
      "page_end": 143,
      "chapter": "Cap. 7 — Doenças da Tireoide",
      "semantic_score": 0.92,
      "bm25_score": 0.78,
      "combined_score": 0.878,
      "images": [
        {
          "path": "~/.medical-rag/images/endocrinologia/a1b2c3d4e5f6/page_142_img_47.png",
          "page": 142
        }
      ]
    }
  ]
}
```

---

### 4.4 `scripts/manage.py`

#### Responsabilidades
1. **Self-bootstrap** (mesmo padrão)
2. Listar coleções com contagem de documentos e livros
3. Detalhar coleção específica (livros, chunks, imagens, tamanho em disco)
4. Remover coleção inteira
5. Remover livro específico de uma coleção (por nome do arquivo)

#### CLI
```
python scripts/manage.py --list [--json]
python scripts/manage.py --info <collection> [--json]
python scripts/manage.py --delete <collection>
python scripts/manage.py --delete-book <collection> <source_file>
```

#### Output JSON (`--list --json`)
```json
{
  "collections": [
    {
      "name": "endocrinologia",
      "books": 3,
      "chunks": 4200,
      "images": 890,
      "disk_size_mb": 124.5
    }
  ]
}
```

---

## 5. Dependências (Versões Fixas)

### 5.1 Dependências Python (instaladas no `.venv`)

| Pacote | Propósito |
|--------|-----------|
| `pymupdf4llm` | Extração de texto/markdown de PDFs com OCR automático |
| `pymupdf` | Extração de imagens com bounding box e metadados |
| `chromadb` | Banco vetorial local persistente |
| `sentence-transformers` | Geração de embeddings (carrega modelo HuggingFace) |
| `rank-bm25` | Algoritmo BM25 para reranking por keywords |
| `tiktoken` | Contagem precisa de tokens para chunking |

### 5.2 Dependências de Sistema

| Pacote | Instalação (macOS) | Propósito |
|--------|---------------------|-----------|
| `tesseract` | `brew install tesseract` | Engine de OCR |
| `tesseract-lang` | `brew install tesseract-lang` | Pacotes de idioma (por, eng, spa, fra, deu...) |

---

## 6. Armazenamento de Dados

### 6.1 Diretório Base
```
~/.medical-rag/
├── config.json              # Configurações do usuário
├── chromadb/                # Banco vetorial persistente
└── images/                  # Imagens extraídas
    └── <collection>/
        └── <book_hash>/
            ├── page_1_img_42.png
            ├── page_1_img_55.jpeg
            └── ...
```

### 6.2 `config.json` — Schema
```json
{
  "embedding_model": "FremyCompany/BioLORD-2023-M",
  "ocr_languages": ["por", "eng", "spa"],
  "chunk_size_tokens": 1000,
  "chunk_overlap_tokens": 200,
  "min_image_dimension": 50,
  "data_dir": "~/.medical-rag",
  "configured_at": "2026-04-23T16:50:00-03:00"
}
```

---

## 7. Padrões de Implementação Obrigatórios

### 7.1 Self-Bootstrap
TODOS os scripts (`ingest.py`, `query.py`, `manage.py`) DEVEM implementar o padrão
de self-bootstrap idêntico ao `data-anonymizer-ollama/scripts/anonymize.py`:

```python
SKILL_DIR = Path(__file__).parent.parent
VENV_DIR = SKILL_DIR / ".venv"
SETUP_SCRIPT = SKILL_DIR / "scripts" / "setup.py"

def resolve_venv_python() -> Path:
    win = VENV_DIR / "Scripts" / "python.exe"
    if win.exists() or sys.platform == "win32":
        return win
    return VENV_DIR / "bin" / "python"

def ensure_initialized():
    venv_python = resolve_venv_python()
    if not VENV_DIR.exists() or not venv_python.exists():
        # Rodar setup.py
        result = subprocess.run([sys.executable, str(SETUP_SCRIPT)])
        if result.returncode != 0:
            sys.exit(result.returncode)
    # Verificar se estamos rodando dentro do venv via sys.prefix
    # (em macOS, symlinks do venv resolvem para o mesmo binário do sistema,
    #  então comparar caminhos resolvidos não funciona — sys.prefix é confiável)
    venv_prefix = str(VENV_DIR.resolve())
    if not sys.prefix.startswith(venv_prefix):
        target = resolve_venv_python()
        result = subprocess.run([str(target), str(Path(__file__).resolve())] + sys.argv[1:])
        sys.exit(result.returncode)
```

### 7.2 Saída JSON
Todo script que aceita `--json` DEVE:
- Imprimir APENAS o JSON válido em stdout
- Imprimir mensagens de progresso em stderr
- Usar `json.dumps(data, ensure_ascii=False, indent=2)`

### 7.3 Tratamento de Erros
- Arquivo não encontrado: exit code 1, mensagem clara em stderr
- Tesseract não instalado: exit code 2, instrução de instalação em stderr
- Coleção não encontrada: exit code 3
- Config não encontrada sem `--json` (modo interativo): perguntar e salvar
- Config não encontrada com `--json` (modo programático): exit code 4 com mensagem

---

## 8. Fluxo de Configuração Interativa

Quando `config.json` não existe e o script é executado sem `--json`:

```
============================================================
  medical-rag — Configuração Inicial
============================================================

  Bem-vindo! Vou configurar o RAG para seus livros médicos.

[1/3] Modelo de embeddings para busca semântica:
  [1] FremyCompany/BioLORD-2023-M (RECOMENDADO — biomédico, ~400MB)
  [2] all-MiniLM-L6-v2 (genérico, ~80MB)
  [3] pritamdeka/S-PubMedBert-MS-MARCO (PubMed, ~400MB)
  [4] Outro (digitar nome do HuggingFace)

  Escolha [1]: _

[2/3] Idiomas para OCR (separados por vírgula):
  Opções: por, eng, spa, fra, deu
  Ou digite outro código Tesseract.

  Idiomas [por,eng]: _

[3/3] Tamanho do chunk (em tokens):
  Para livros de 1000+ páginas, recomendamos 1000 tokens com 200 de overlap.

  Chunk size [1000]: _
  Overlap [200]: _

============================================================
  Configuração salva em ~/.medical-rag/config.json
============================================================
```

---

## 9. Critérios de Aceite

A skill está PRONTA quando:

- [ ] `python scripts/setup.py` cria o venv e instala todas as deps sem erro
- [ ] `python scripts/ingest.py --file <pdf> --collection teste --json` processa um PDF e retorna JSON válido
- [ ] Páginas escaneadas (imagem) são processadas via OCR automaticamente
- [ ] Imagens são extraídas e salvas em `~/.medical-rag/images/`
- [ ] `python scripts/query.py --query "teste" --collection teste --json` retorna resultados com citação e imagens
- [ ] `python scripts/manage.py --list --json` lista coleções corretamente
- [ ] `python scripts/manage.py --delete teste` remove a coleção
- [ ] Config interativa funciona na primeira execução
- [ ] Todos os scripts fazem self-bootstrap corretamente
- [ ] Saída `--json` é JSON válido, mensagens de progresso vão para stderr

---

## 10. O que esta Skill NÃO faz

- NÃO gera respostas com LLM (apenas recupera chunks relevantes — o agente orquestrador usa o texto recuperado como contexto)
- NÃO envia dados para nuvem (tudo local)
- NÃO faz anonimização de dados (use `data-anonymizer` para isso)
- NÃO lê PDFs simples sem indexação (use a skill `pdf` para isso)
- NÃO faz embeddings de imagens (imagens são associadas por proximidade de página, não por conteúdo visual)
