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

# Medical RAG — Retrieval-Augmented Generation para Livros Médicos

Pipeline local e offline para processar livros médicos (PDF digital ou escaneado),
extrair texto via OCR, indexar em banco vetorial com embeddings biomédicos,
e permitir buscas semânticas com citação de fonte e imagens contextuais.

## Pipeline

```
PDF ──► pymupdf4llm (OCR automático) ──► Markdown
  │                                          │
  ├──► pymupdf (extrai imagens) ──► disco    │
  │                                          ▼
  │                                    Chunking (1000 tok + 200 overlap)
  │                                          │
  │                                          ▼
  │                                    Embeddings (BioLORD-2023-M)
  │                                          │
  │                                          ▼
  └──► associação por página ──────►  ChromaDB (persistente local)
                                             │
                                             ▼
                                     Query híbrida (semântica + BM25)
                                             │
                                             ▼
                                     Resultados + citações + imagens
```

## Auto-configuração

A skill se auto-instala na primeira execução de qualquer script.
Exige que o Tesseract esteja instalado no sistema:

```bash
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-por tesseract-ocr-spa
```

Na primeira execução, o script pergunta interativamente:
1. **Modelo de embeddings** (default: `FremyCompany/BioLORD-2023-M`)
2. **Idiomas para OCR** (default: `por,eng`)
3. **Tamanho do chunk** (default: 1000 tokens, overlap 200)

As configurações ficam em `~/.medical-rag/config.json`.

## Ingerir Livros

```bash
# Arquivo único
python scripts/ingest.py --file livro.pdf --collection endocrinologia [--json]

# Diretório com vários PDFs
python scripts/ingest.py --dir /pasta/pdfs/ --collection endocrinologia [--json]

# Forçar OCR em todas as páginas (mesmo digitais)
python scripts/ingest.py --file livro.pdf --collection endo --force-ocr [--json]
```

O script extrai texto (com OCR automático para páginas escaneadas), divide em chunks,
extrai imagens, e indexa tudo no ChromaDB. Imagens pequenas (< 50x50 px) são ignoradas.

## Consultar

```bash
# Busca em uma coleção
python scripts/query.py --query "tratamento hipotireoidismo" --collection endocrinologia [--json]

# Busca em todas as coleções
python scripts/query.py --query "diabetes mellitus tipo 2" --all [--json]

# Controlar número de resultados (default: 5)
python scripts/query.py --query "fisiopatologia" --collection endo --n-results 10 [--json]
```

A busca é híbrida: combina similaridade semântica (ChromaDB) com reranking BM25
para priorizar terminologia médica exata. Cada resultado inclui citação completa
(livro, página, capítulo) e imagens da mesma página.

## Gerenciar Coleções

```bash
# Listar todas as coleções
python scripts/manage.py --list [--json]

# Detalhes de uma coleção
python scripts/manage.py --info endocrinologia [--json]

# Remover coleção
python scripts/manage.py --delete endocrinologia

# Remover um livro de uma coleção
python scripts/manage.py --delete-book endocrinologia "Harrison.pdf"
```

## Arquivos de Referência

| Arquivo | Quando usar |
|---------|-------------|
| `SPEC.md` | Especificação técnica completa e reproduzível da skill |
| `references/chunking_strategies.md` | Detalhes sobre estratégias de chunking para texto médico |

## Notas Importantes

- **Privacidade**: todo processamento é local. Nenhum dado sai da máquina após a instalação
- **Imagens**: são associadas aos chunks por proximidade de página, não por conteúdo visual
- **LLM**: a skill NÃO gera respostas — apenas recupera chunks relevantes para o agente usar como contexto
- **Livros grandes**: para livros de 1000+ páginas, a ingestão pode levar vários minutos (OCR é intensivo)
