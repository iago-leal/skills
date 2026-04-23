"""
query.py — Busca hibrida (semantica + BM25) no indice ChromaDB.

SELF-BOOTSTRAP: mesmo padrao de auto-inicializacao.

Modos:
    python query.py --query "tratamento hipotireoidismo" --collection endocrinologia [--json]
    python query.py --query "diabetes tipo 2" --all [--json]
"""

import argparse
import json as json_mod
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
VENV_DIR = SKILL_DIR / ".venv"
SETUP_SCRIPT = SKILL_DIR / "scripts" / "setup.py"
DATA_DIR = Path.home() / ".medical-rag"
CONFIG_PATH = DATA_DIR / "config.json"


# -- Self-bootstrap ------------------------------------------------------------

def resolve_venv_python() -> Path:
    win = VENV_DIR / "Scripts" / "python.exe"
    if win.exists() or sys.platform == "win32":
        return win
    return VENV_DIR / "bin" / "python"


def ensure_initialized():
    venv_python = resolve_venv_python()
    if not VENV_DIR.exists() or not venv_python.exists():
        print("Primeira execução detectada. Configurando...", file=sys.stderr)
        if not SETUP_SCRIPT.exists():
            print(f"ERRO: setup.py não encontrado em {SETUP_SCRIPT}", file=sys.stderr)
            sys.exit(1)
        result = subprocess.run([sys.executable, str(SETUP_SCRIPT)])
        if result.returncode != 0:
            sys.exit(result.returncode)

    # Verificar se estamos rodando dentro do venv via sys.prefix
    venv_prefix = str(VENV_DIR.resolve())
    if not sys.prefix.startswith(venv_prefix):
        target = resolve_venv_python()
        result = subprocess.run([str(target), str(Path(__file__).resolve())] + sys.argv[1:])
        sys.exit(result.returncode)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print("ERRO: config.json não encontrada. Execute setup.py primeiro.", file=sys.stderr)
        sys.exit(4)
    return json_mod.loads(CONFIG_PATH.read_text(encoding="utf-8"))


# -- ChromaDB ------------------------------------------------------------------

def get_chromadb_client():
    import chromadb
    return chromadb.PersistentClient(path=str(DATA_DIR / "chromadb"))


def get_collection(client, name: str, embedding_model: str):
    from chromadb.utils import embedding_functions
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model
    )
    try:
        return client.get_collection(name=name, embedding_function=ef)
    except Exception:
        print(f"ERRO: coleção '{name}' não encontrada.", file=sys.stderr)
        sys.exit(3)


# -- Busca híbrida -------------------------------------------------------------

def hybrid_search(collection, query: str, n_results: int = 5,
                  semantic_weight: float = 0.7) -> list[dict]:
    """Busca semântica no ChromaDB + reranking BM25."""
    # 1. Busca semântica: pegar mais resultados para reranking
    fetch_n = min(n_results * 4, 50)
    results = collection.query(
        query_texts=[query],
        n_results=fetch_n,
        include=["documents", "metadatas", "distances"],
    )

    if not results["documents"] or not results["documents"][0]:
        return []

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    # Converter distância coseno para score (ChromaDB retorna distância, não similaridade)
    semantic_scores = [max(0, 1 - d) for d in distances]

    # 2. Reranking BM25
    from rank_bm25 import BM25Okapi

    tokenized_docs = [doc.lower().split() for doc in docs]
    tokenized_query = query.lower().split()

    bm25 = BM25Okapi(tokenized_docs)
    bm25_scores_raw = bm25.get_scores(tokenized_query)

    # Normalizar BM25 scores para [0, 1]
    max_bm25 = max(bm25_scores_raw) if max(bm25_scores_raw) > 0 else 1
    bm25_scores = [s / max_bm25 for s in bm25_scores_raw]

    # 3. Score combinado
    bm25_weight = 1 - semantic_weight
    combined = []
    for i in range(len(docs)):
        score = (semantic_weight * semantic_scores[i]) + (bm25_weight * bm25_scores[i])

        # Resolver imagens
        image_paths_str = metas[i].get("image_paths", "")
        images = []
        if image_paths_str:
            for img_path in image_paths_str.split("|"):
                if img_path and Path(img_path).exists():
                    images.append({
                        "path": img_path,
                        "page": metas[i].get("page_start", 0),
                    })

        combined.append({
            "text": docs[i],
            "source_file": metas[i].get("source_file", ""),
            "book_title": metas[i].get("book_title", ""),
            "page_start": metas[i].get("page_start", 0),
            "page_end": metas[i].get("page_end", 0),
            "chapter": metas[i].get("chapter", ""),
            "semantic_score": round(semantic_scores[i], 4),
            "bm25_score": round(bm25_scores[i], 4),
            "combined_score": round(score, 4),
            "images": images,
        })

    # Ordenar por score combinado (desc) e retornar top N
    combined.sort(key=lambda x: x["combined_score"], reverse=True)
    for rank, item in enumerate(combined[:n_results], 1):
        item["rank"] = rank

    return combined[:n_results]


# -- CLI -----------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Busca no índice RAG médico")
    p.add_argument("--query", "-q", required=True, help="Texto da consulta")

    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--collection", "-c", help="Nome da coleção")
    group.add_argument("--all", action="store_true", help="Buscar em todas as coleções")

    p.add_argument("--n-results", "-n", type=int, default=5, help="Número de resultados (default: 5)")
    p.add_argument("--with-images", action="store_true", default=True,
                   help="Incluir imagens no resultado (default: true)")
    p.add_argument("--json", action="store_true", help="Saída em JSON")
    return p.parse_args()


def main():
    ensure_initialized()
    args = parse_args()
    config = load_config()

    client = get_chromadb_client()
    embedding_model = config.get("embedding_model", "FremyCompany/BioLORD-2023-M")

    collections_to_search = []
    if args.all:
        all_cols = client.list_collections()
        if not all_cols:
            print("ERRO: nenhuma coleção encontrada.", file=sys.stderr)
            sys.exit(3)
        collections_to_search = [(c.name, c) for c in all_cols]
        # Re-obter com embedding function
        collections_to_search = [
            (name, get_collection(client, name, embedding_model))
            for name, _ in collections_to_search
        ]
    else:
        col = get_collection(client, args.collection, embedding_model)
        collections_to_search = [(args.collection, col)]

    all_results = []
    for col_name, col in collections_to_search:
        print(f"  Buscando em '{col_name}'...", file=sys.stderr)
        results = hybrid_search(col, args.query, n_results=args.n_results)
        for r in results:
            r["collection"] = col_name
        all_results.extend(results)

    # Re-ordenar por score se buscou em múltiplas coleções
    if args.all and len(collections_to_search) > 1:
        all_results.sort(key=lambda x: x["combined_score"], reverse=True)
        all_results = all_results[:args.n_results]
        for rank, item in enumerate(all_results, 1):
            item["rank"] = rank

    # Remover imagens se não solicitado
    if not args.with_images:
        for r in all_results:
            r.pop("images", None)

    if args.json:
        output = {
            "query": args.query,
            "collection": args.collection if not args.all else "ALL",
            "n_results": len(all_results),
            "results": all_results,
        }
        print(json_mod.dumps(output, ensure_ascii=False, indent=2))
    else:
        if not all_results:
            print("\nNenhum resultado encontrado.")
            return

        print(f"\n{'='*60}")
        print(f"  Query: {args.query}")
        print(f"  Resultados: {len(all_results)}")
        print(f"{'='*60}")

        for r in all_results:
            print(f"\n--- #{r['rank']} (score: {r['combined_score']}) ---")
            print(f"  Livro: {r['book_title']}")
            print(f"  Arquivo: {r['source_file']}")
            print(f"  Páginas: {r['page_start']}–{r['page_end']}")
            if r.get("chapter"):
                print(f"  Capítulo: {r['chapter']}")
            print(f"  Scores: semântico={r['semantic_score']}, BM25={r['bm25_score']}")
            if r.get("images"):
                print(f"  Imagens: {len(r['images'])} encontrada(s)")
                for img in r["images"]:
                    print(f"    → {img['path']}")
            print(f"\n  {r['text'][:500]}...")


if __name__ == "__main__":
    main()
