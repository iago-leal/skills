"""
manage.py — Gerenciamento de colecoes e livros indexados no RAG.

SELF-BOOTSTRAP: mesmo padrao de auto-inicializacao.

Modos:
    python manage.py --list [--json]
    python manage.py --info endocrinologia [--json]
    python manage.py --delete endocrinologia
    python manage.py --delete-book endocrinologia "Harrison.pdf"
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


# -- ChromaDB ------------------------------------------------------------------

def get_chromadb_client():
    import chromadb
    return chromadb.PersistentClient(path=str(DATA_DIR / "chromadb"))


def get_disk_size(path: Path) -> float:
    """Retorna tamanho em MB de um diretório."""
    total = 0
    if path.is_dir():
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
    return round(total / (1024 * 1024), 1)


# -- Comandos ------------------------------------------------------------------

def cmd_list(client, as_json: bool):
    """Lista todas as coleções."""
    collections = client.list_collections()

    if not collections:
        if as_json:
            print(json_mod.dumps({"collections": []}, indent=2))
        else:
            print("\nNenhuma coleção encontrada.")
        return

    results = []
    for col in collections:
        col_obj = client.get_collection(name=col.name)
        count = col_obj.count()

        # Contar livros únicos e imagens
        books = set()
        if count > 0:
            # Pegar todos os metadados (pode ser lento para coleções grandes)
            data = col_obj.get(limit=count, include=["metadatas"])
            for m in data["metadatas"]:
                if m and m.get("source_file"):
                    books.add(m["source_file"])

        # Tamanho das imagens em disco
        images_dir = DATA_DIR / "images" / col.name
        images_size = get_disk_size(images_dir)
        n_images = sum(1 for _ in images_dir.rglob("*") if _.is_file()) if images_dir.exists() else 0

        results.append({
            "name": col.name,
            "books": len(books),
            "chunks": count,
            "images": n_images,
            "disk_size_mb": images_size,
        })

    if as_json:
        print(json_mod.dumps({"collections": results}, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  Coleções indexadas: {len(results)}")
        print(f"{'='*60}")
        for r in results:
            print(f"\n  {r['name']}:")
            print(f"    Livros: {r['books']}")
            print(f"    Chunks: {r['chunks']}")
            print(f"    Imagens: {r['images']} ({r['disk_size_mb']} MB)")


def cmd_info(client, collection_name: str, as_json: bool):
    """Detalhes de uma coleção específica."""
    try:
        col = client.get_collection(name=collection_name)
    except Exception:
        print(f"ERRO: coleção '{collection_name}' não encontrada.", file=sys.stderr)
        sys.exit(3)

    count = col.count()
    data = col.get(limit=count, include=["metadatas"]) if count > 0 else {"metadatas": []}

    books = {}
    for m in data["metadatas"]:
        if not m:
            continue
        src = m.get("source_file", "desconhecido")
        if src not in books:
            books[src] = {
                "title": m.get("book_title", src),
                "chunks": 0,
                "total_chunks": m.get("total_chunks", 0),
                "ingested_at": m.get("ingested_at", ""),
            }
        books[src]["chunks"] += 1

    images_dir = DATA_DIR / "images" / collection_name
    n_images = sum(1 for _ in images_dir.rglob("*") if _.is_file()) if images_dir.exists() else 0
    images_size = get_disk_size(images_dir)

    result = {
        "collection": collection_name,
        "total_chunks": count,
        "total_images": n_images,
        "images_disk_mb": images_size,
        "books": [
            {
                "source_file": src,
                "title": info["title"],
                "chunks": info["chunks"],
                "ingested_at": info["ingested_at"],
            }
            for src, info in books.items()
        ],
    }

    if as_json:
        print(json_mod.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  Coleção: {collection_name}")
        print(f"{'='*60}")
        print(f"  Total chunks: {count}")
        print(f"  Total imagens: {n_images} ({images_size} MB)")
        print(f"\n  Livros indexados:")
        for b in result["books"]:
            print(f"    • {b['title']} ({b['source_file']})")
            print(f"      Chunks: {b['chunks']} | Ingestão: {b['ingested_at']}")


def cmd_delete(client, collection_name: str):
    """Remove uma coleção inteira."""
    try:
        client.delete_collection(name=collection_name)
        print(f"Coleção '{collection_name}' removida do ChromaDB.", file=sys.stderr)
    except Exception as e:
        print(f"ERRO ao remover coleção: {e}", file=sys.stderr)
        sys.exit(3)

    # Remover imagens
    images_dir = DATA_DIR / "images" / collection_name
    if images_dir.exists():
        import shutil
        shutil.rmtree(images_dir)
        print(f"Imagens removidas de {images_dir}", file=sys.stderr)

    print(f"OK: coleção '{collection_name}' removida completamente.")


def cmd_delete_book(client, collection_name: str, source_file: str):
    """Remove um livro específico de uma coleção."""
    try:
        col = client.get_collection(name=collection_name)
    except Exception:
        print(f"ERRO: coleção '{collection_name}' não encontrada.", file=sys.stderr)
        sys.exit(3)

    # Buscar IDs dos chunks desse livro
    count = col.count()
    if count == 0:
        print(f"Coleção '{collection_name}' está vazia.", file=sys.stderr)
        return

    data = col.get(limit=count, include=["metadatas"])
    ids_to_delete = []
    book_hash = None
    for i, m in enumerate(data["metadatas"]):
        if m and m.get("source_file") == source_file:
            ids_to_delete.append(data["ids"][i])
            # Extrair hash do ID (formato: hash_index)
            if book_hash is None and "_" in data["ids"][i]:
                book_hash = data["ids"][i].split("_")[0]

    if not ids_to_delete:
        print(f"ERRO: livro '{source_file}' não encontrado na coleção.", file=sys.stderr)
        sys.exit(1)

    # Deletar em lotes
    batch_size = 100
    for start in range(0, len(ids_to_delete), batch_size):
        end = start + batch_size
        col.delete(ids=ids_to_delete[start:end])

    print(f"{len(ids_to_delete)} chunks de '{source_file}' removidos.", file=sys.stderr)

    # Remover imagens se temos o hash
    if book_hash:
        images_dir = DATA_DIR / "images" / collection_name / book_hash
        if images_dir.exists():
            import shutil
            shutil.rmtree(images_dir)
            print(f"Imagens removidas de {images_dir}", file=sys.stderr)

    print(f"OK: livro '{source_file}' removido de '{collection_name}'.")


# -- CLI -----------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Gerencia coleções do RAG médico")

    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="Listar todas as coleções")
    group.add_argument("--info", metavar="COLLECTION", help="Detalhes de uma coleção")
    group.add_argument("--delete", metavar="COLLECTION", help="Remover uma coleção")
    group.add_argument("--delete-book", nargs=2, metavar=("COLLECTION", "SOURCE_FILE"),
                       help="Remover um livro de uma coleção")

    p.add_argument("--json", action="store_true", help="Saída em JSON")
    return p.parse_args()


def main():
    ensure_initialized()
    args = parse_args()

    client = get_chromadb_client()

    if args.list:
        cmd_list(client, args.json)
    elif args.info:
        cmd_info(client, args.info, args.json)
    elif args.delete:
        cmd_delete(client, args.delete)
    elif args.delete_book:
        cmd_delete_book(client, args.delete_book[0], args.delete_book[1])


if __name__ == "__main__":
    main()
