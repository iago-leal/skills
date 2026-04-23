# Estratégias de Chunking para Texto Médico

## Visão Geral

Texto médico é particularmente denso e rico em terminologia especializada.
Uma estratégia de chunking inadequada pode separar um diagnóstico de seu
tratamento, ou cortar uma lista de sintomas ao meio.

## Estratégia Primária: Chunking por Parágrafo com Limites de Seção

1. **Detectar marcadores de seção**: linhas que começam com `#`, `##`, `###`
   (gerados pelo pymupdf4llm a partir dos headings do PDF)
2. **Respeitar limites**: nunca quebrar no meio de um parágrafo
3. **Agregar parágrafos**: acumular parágrafos consecutivos até atingir
   o `chunk_size` configurado (default: 1000 tokens)
4. **Overlap**: ao fechar um chunk, o próximo começa com os últimos
   `overlap` tokens do chunk anterior (default: 200 tokens)
5. **Prefixo de contexto**: se o chunk não começa com um heading,
   prefixar com o heading mais recente anterior (ex: "## Cap. 7 — Tireoide\n\n")

## Estratégia de Fallback

Se o texto não tem marcadores de seção (comum em PDFs escaneados sem
estrutura), usar chunking recursivo:

1. Tentar quebrar por `\n\n` (parágrafos)
2. Se um parágrafo excede `chunk_size`, quebrar por `\n` (linhas)
3. Se uma linha excede `chunk_size`, quebrar por `. ` (sentenças)
4. Último recurso: quebrar por espaço (palavras)

## Valores Recomendados por Tipo de Livro

| Tipo | Chunk Size | Overlap | Rationale |
|------|-----------|---------|-----------|
| Textbook (ex: Harrison, Vilar) | 1000 tokens | 200 | Capítulos longos, seções densas |
| Artigo científico | 500 tokens | 100 | Mais curto, seções bem definidas |
| Guidelines / Protocolos | 800 tokens | 150 | Listas e tabelas frequentes |
| Atlas de imagens | 300 tokens | 50 | Pouco texto por página, muitas imagens |

## Tratamento Especial

### Tabelas
- Tabelas em markdown (detectadas por linhas com `|`) devem ser mantidas
  inteiras em um único chunk, mesmo que excedam o `chunk_size`
- Se a tabela for maior que 2x o `chunk_size`, dividir por linhas

### Listas
- Listas enumeradas ou com bullets devem ser mantidas inteiras quando possível
- Contexto: manter o parágrafo introdutório junto com a lista

### Referências Bibliográficas
- Seções de referências bibliográficas no final dos capítulos podem ser
  indexadas com metadado `is_reference: true` para filtragem
