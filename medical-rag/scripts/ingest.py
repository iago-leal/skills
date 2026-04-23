"""
ingest.py — Pipeline de ingestao: PDF -> OCR -> Chunks -> ChromaDB + Imagens.

SELF-BOOTSTRAP: na primeira execucao detecta .venv ausente, roda setup.py
automaticamente, e re-executa com o Python do venv.

Modos:
    Arquivo:    python ingest.py --file livro.pdf --collection endocrinologia [--json]
    Diretorio:  python ingest.py --dir /pasta/ --collection endocrinologia [--json]
"""

import argparse
import hashlib
import json as json_mod
import subprocess
import sys
import time
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
        print("=" * 60, file=sys.stderr)
        print("  Primeira execução detectada.", file=sys.stderr)
        print("  Configurando a skill automaticamente...", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        if not SETUP_SCRIPT.exists():
            print(f"ERRO: setup.py não encontrado em {SETUP_SCRIPT}", file=sys.stderr)
            sys.exit(1)
        result = subprocess.run([sys.executable, str(SETUP_SCRIPT)])
        if result.returncode != 0:
            sys.exit(result.returncode)
        venv_python = resolve_venv_python()
        if not venv_python.exists():
            print(f"ERRO: Python do venv não encontrado após setup", file=sys.stderr)
            sys.exit(1)

    # Verificar se estamos rodando dentro do venv via sys.prefix
    venv_prefix = str(VENV_DIR.resolve())
    if not sys.prefix.startswith(venv_prefix):
        target = resolve_venv_python()
        result = subprocess.run([str(target), str(Path(__file__).resolve())] + sys.argv[1:])
        sys.exit(result.returncode)


# -- Config --------------------------------------------------------------------

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print("ERRO: config.json não encontrada. Execute setup.py primeiro.", file=sys.stderr)
        print(f"  Esperado em: {CONFIG_PATH}", file=sys.stderr)
        sys.exit(4)
    return json_mod.loads(CONFIG_PATH.read_text(encoding="utf-8"))


# -- Extração de texto ---------------------------------------------------------

def extract_text(pdf_path: Path, force_ocr: bool = False) -> str:
    import pymupdf4llm

    print(f"  Extraindo texto de {pdf_path.name}...", file=sys.stderr)
    kwargs = {"show_progress": True}
    if force_ocr:
        kwargs["force_text"] = False  # força OCR mesmo com texto digital

    md_text = pymupdf4llm.to_markdown(str(pdf_path), **kwargs)
    return md_text


# -- Extração de imagens -------------------------------------------------------

def extract_images(pdf_path: Path, collection: str, book_hash: str,
                   min_dim: int = 50) -> dict[int, list[str]]:
    """Extrai imagens do PDF e retorna {page_num: [caminhos_salvos]}."""
    import pymupdf

    images_dir = DATA_DIR / "images" / collection / book_hash
    images_dir.mkdir(parents=True, exist_ok=True)

    page_images: dict[int, list[str]] = {}
    doc = pymupdf.open(str(pdf_path))

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_info in image_list:
            xref = img_info[0]
            try:
                img_data = doc.extract_image(xref)
            except Exception:
                continue

            w, h = img_data.get("width", 0), img_data.get("height", 0)
            if w < min_dim or h < min_dim:
                continue

            ext = img_data.get("ext", "png")
            img_bytes = img_data.get("image", b"")
            if not img_bytes:
                continue

            fname = f"page_{page_num}_img_{xref}.{ext}"
            fpath = images_dir / fname
            fpath.write_bytes(img_bytes)

            if page_num not in page_images:
                page_images[page_num] = []
            page_images[page_num].append(str(fpath))

    doc.close()
    return page_images


# -- Chunking ------------------------------------------------------------------

def count_tokens(text: str, enc=None) -> int:
    if enc is None:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[dict]:
    """Divide texto em chunks com overlap, respeitando limites de parágrafo."""
    import tiktoken

    enc = tiktoken.get_encoding("cl100k_base")
    paragraphs = text.split("\n\n")
    chunks = []
    current_parts = []
    current_tokens = 0
    current_heading = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Detectar heading
        if para.startswith("#"):
            current_heading = para.split("\n")[0]

        para_tokens = count_tokens(para, enc)

        # Se um parágrafo sozinho excede o chunk_size, dividir por sentenças
        if para_tokens > chunk_size:
            # Fechar chunk atual se houver conteúdo
            if current_parts:
                chunk_text_joined = "\n\n".join(current_parts)
                chunks.append({"text": chunk_text_joined, "heading": current_heading})
                # Overlap: manter últimas partes
                overlap_parts = []
                overlap_tokens = 0
                for p in reversed(current_parts):
                    pt = count_tokens(p, enc)
                    if overlap_tokens + pt > overlap:
                        break
                    overlap_parts.insert(0, p)
                    overlap_tokens += pt
                current_parts = overlap_parts
                current_tokens = overlap_tokens

            # Dividir parágrafo grande por sentenças
            sentences = para.replace(". ", ".\n").split("\n")
            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue
                st = count_tokens(sent, enc)
                if current_tokens + st > chunk_size and current_parts:
                    chunk_text_joined = "\n\n".join(current_parts)
                    chunks.append({"text": chunk_text_joined, "heading": current_heading})
                    overlap_parts = []
                    overlap_tokens = 0
                    for p in reversed(current_parts):
                        pt = count_tokens(p, enc)
                        if overlap_tokens + pt > overlap:
                            break
                        overlap_parts.insert(0, p)
                        overlap_tokens += pt
                    current_parts = overlap_parts
                    current_tokens = overlap_tokens
                current_parts.append(sent)
                current_tokens += st
            continue

        if current_tokens + para_tokens > chunk_size and current_parts:
            chunk_text_joined = "\n\n".join(current_parts)
            chunks.append({"text": chunk_text_joined, "heading": current_heading})
            # Overlap
            overlap_parts = []
            overlap_tokens = 0
            for p in reversed(current_parts):
                pt = count_tokens(p, enc)
                if overlap_tokens + pt > overlap:
                    break
                overlap_parts.insert(0, p)
                overlap_tokens += pt
            current_parts = overlap_parts
            current_tokens = overlap_tokens

        current_parts.append(para)
        current_tokens += para_tokens

    # Último chunk
    if current_parts:
        chunk_text_joined = "\n\n".join(current_parts)
        chunks.append({"text": chunk_text_joined, "heading": current_heading})

    return chunks


# -- Detecção de página por chunk -----------------------------------------------

def detect_page_numbers(text: str) -> list[tuple[int, int]]:
    """Detecta marcadores de página inseridos pelo pymupdf4llm.
    Retorna lista de (char_offset, page_number)."""
    import re
    markers = []
    # pymupdf4llm insere marcadores como -----\nPage X\n-----
    for m in re.finditer(r'(?:^|\n).*?[Pp]age\s+(\d+)', text):
        markers.append((m.start(), int(m.group(1))))
    return markers


def assign_pages_to_chunks(text: str, chunks: list[dict]) -> list[dict]:
    """Atribui números de página a cada chunk baseado na posição no texto."""
    # Abordagem simplificada: dividir proporcionalmente
    total_len = len(text)
    if total_len == 0:
        for c in chunks:
            c["page_start"] = 0
            c["page_end"] = 0
        return chunks

    # Calcular posição de cada chunk no texto original
    pos = 0
    for c in chunks:
        idx = text.find(c["text"][:100], pos)
        if idx == -1:
            idx = pos
        c["_char_pos"] = idx
        pos = idx + len(c["text"]) // 2

    # Estimar páginas proporcionalmente (assume distribuição uniforme)
    # Isso é uma aproximação — pymupdf4llm não insere marcadores confiáveis
    for c in chunks:
        ratio_start = c["_char_pos"] / total_len
        ratio_end = (c["_char_pos"] + len(c["text"])) / total_len
        c["page_start"] = max(1, int(ratio_start * c.get("_total_pages", 1)))
        c["page_end"] = max(1, int(ratio_end * c.get("_total_pages", 1)))
        del c["_char_pos"]

    return chunks


# -- Indexação ChromaDB ---------------------------------------------------------

def get_chromadb_collection(collection_name: str, embedding_model: str):
    import chromadb
    from chromadb.utils import embedding_functions

    client = chromadb.PersistentClient(path=str(DATA_DIR / "chromadb"))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model
    )
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def index_chunks(chunks: list[dict], collection, book_hash: str,
                 source_file: str, book_title: str, collection_name: str,
                 page_images: dict[int, list[str]]):
    """Insere chunks no ChromaDB com metadados e referências de imagens."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    total = len(chunks)
    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        chunk_id = f"{book_hash}_{i}"

        # Associar imagens por página
        images_for_chunk = []
        for pg in range(chunk.get("page_start", 0), chunk.get("page_end", 0) + 1):
            if pg in page_images:
                images_for_chunk.extend(page_images[pg])

        ids.append(chunk_id)
        documents.append(chunk["text"])
        metadatas.append({
            "source_file": source_file,
            "book_title": book_title,
            "page_start": chunk.get("page_start", 0),
            "page_end": chunk.get("page_end", 0),
            "chapter": chunk.get("heading", ""),
            "chunk_index": i,
            "total_chunks": total,
            "image_paths": "|".join(images_for_chunk),
            "collection": collection_name,
            "ingested_at": now,
        })

        if (i + 1) % 50 == 0:
            print(f"  Indexando chunk {i + 1}/{total}...", file=sys.stderr)

    # Inserir em lotes de 100
    batch_size = 100
    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )

    print(f"  {total} chunks indexados em '{collection_name}'.", file=sys.stderr)


# -- Pipeline principal --------------------------------------------------------

def process_pdf(pdf_path: Path, collection_name: str, config: dict,
                force_ocr: bool = False) -> dict:
    """Processa um PDF completo: extração, chunking, imagens, indexação."""
    t0 = time.time()

    # Hash do arquivo
    sha = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:12]

    # Metadata do PDF
    import pymupdf
    doc = pymupdf.open(str(pdf_path))
    total_pages = doc.page_count
    meta = doc.metadata or {}
    book_title = meta.get("title", "") or pdf_path.stem
    doc.close()

    # 1. Extrair texto
    md_text = extract_text(pdf_path, force_ocr=force_ocr)

    # 2. Extrair imagens
    print(f"  Extraindo imagens de {pdf_path.name}...", file=sys.stderr)
    page_images = extract_images(
        pdf_path, collection_name, sha,
        min_dim=config.get("min_image_dimension", 50)
    )
    total_images = sum(len(v) for v in page_images.values())
    print(f"  {total_images} imagens extraídas.", file=sys.stderr)

    # 3. Chunking
    print(f"  Dividindo texto em chunks...", file=sys.stderr)
    chunks = chunk_text(
        md_text,
        chunk_size=config.get("chunk_size_tokens", 1000),
        overlap=config.get("chunk_overlap_tokens", 200),
    )
    # Atribuir páginas
    for c in chunks:
        c["_total_pages"] = total_pages
    chunks = assign_pages_to_chunks(md_text, chunks)
    print(f"  {len(chunks)} chunks criados.", file=sys.stderr)

    # 4. Indexar no ChromaDB
    print(f"  Indexando no ChromaDB...", file=sys.stderr)
    collection = get_chromadb_collection(
        collection_name, config.get("embedding_model", "FremyCompany/BioLORD-2023-M")
    )
    index_chunks(
        chunks, collection, sha,
        source_file=pdf_path.name,
        book_title=book_title,
        collection_name=collection_name,
        page_images=page_images,
    )

    duration = time.time() - t0
    return {
        "source": pdf_path.name,
        "collection": collection_name,
        "pages_total": total_pages,
        "chunks_created": len(chunks),
        "images_extracted": total_images,
        "embedding_model": config.get("embedding_model"),
        "chunk_size_tokens": config.get("chunk_size_tokens"),
        "overlap_tokens": config.get("chunk_overlap_tokens"),
        "duration_seconds": round(duration, 1),
        "book_hash": sha,
    }


# -- CLI -----------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Ingere PDFs médicos no RAG")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Caminho para um arquivo PDF")
    group.add_argument("--dir", help="Diretório com PDFs para ingerir")
    p.add_argument("--collection", "-c", required=True, help="Nome da coleção")
    p.add_argument("--force-ocr", action="store_true", help="Forçar OCR em todas as páginas")
    p.add_argument("--json", action="store_true", help="Saída em JSON")
    return p.parse_args()


def main():
    ensure_initialized()
    args = parse_args()
    config = load_config()

    pdf_files = []
    if args.file:
        p = Path(args.file)
        if not p.exists():
            print(f"ERRO: arquivo não encontrado: {p}", file=sys.stderr)
            sys.exit(1)
        pdf_files.append(p)
    else:
        d = Path(args.dir)
        if not d.is_dir():
            print(f"ERRO: diretório não encontrado: {d}", file=sys.stderr)
            sys.exit(1)
        pdf_files = sorted(d.glob("*.pdf"))
        if not pdf_files:
            print(f"ERRO: nenhum PDF encontrado em {d}", file=sys.stderr)
            sys.exit(1)

    results = []
    for pdf in pdf_files:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"  Processando: {pdf.name}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        result = process_pdf(pdf, args.collection, config, force_ocr=args.force_ocr)
        results.append(result)

    if args.json:
        output = {"ingest": results if len(results) > 1 else results[0]}
        print(json_mod.dumps(output, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"\n--- {r['source']} ---")
            print(f"  Coleção: {r['collection']}")
            print(f"  Páginas: {r['pages_total']}")
            print(f"  Chunks: {r['chunks_created']}")
            print(f"  Imagens: {r['images_extracted']}")
            print(f"  Tempo: {r['duration_seconds']}s")


if __name__ == "__main__":
    main()
