"""
setup.py — Inicializacao da skill medical-rag.

Cria o .venv, instala dependencias Python, verifica o Tesseract,
cria diretorios de dados, e conduz configuracao interativa.

Uso:
    python setup.py [--reconfigure]
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
VENV_DIR = SKILL_DIR / ".venv"

DATA_DIR = Path.home() / ".medical-rag"
CHROMADB_DIR = DATA_DIR / "chromadb"
IMAGES_DIR = DATA_DIR / "images"
CONFIG_PATH = DATA_DIR / "config.json"

PACKAGES = [
    "pymupdf4llm",
    "pymupdf",
    "chromadb",
    "sentence-transformers",
    "rank-bm25",
    "tiktoken",
]

EMBEDDING_MODELS = {
    "1": ("FremyCompany/BioLORD-2023-M", "BioLORD-2023-M (RECOMENDADO — biomédico, ~400MB)"),
    "2": ("all-MiniLM-L6-v2", "all-MiniLM-L6-v2 (genérico, leve, ~80MB)"),
    "3": ("pritamdeka/S-PubMedBert-MS-MARCO", "S-PubMedBert-MS-MARCO (PubMed, ~400MB)"),
}

DEFAULT_OCR_LANGUAGES = ["por", "eng"]
AVAILABLE_OCR_LANGUAGES = {
    "por": "Português", "eng": "Inglês", "spa": "Espanhol",
    "fra": "Francês", "deu": "Alemão", "ita": "Italiano",
}

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_MIN_IMAGE_DIM = 50


def venv_python() -> Path:
    win = VENV_DIR / "Scripts" / "python.exe"
    unix = VENV_DIR / "bin" / "python"
    return win if win.exists() else unix


def run(cmd, **kwargs):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"\nERRO: comando falhou com codigo {result.returncode}")
        sys.exit(result.returncode)


def check_tesseract() -> bool:
    import shutil
    if shutil.which("tesseract") is None:
        return False
    try:
        r = subprocess.run(["tesseract", "--version"], capture_output=True, text=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False


def get_tesseract_languages() -> list[str]:
    try:
        r = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True, timeout=5)
        if r.returncode != 0:
            return []
        lines = r.stdout.strip().split("\n")
        return [l.strip() for l in lines[1:] if l.strip()]
    except Exception:
        return []


def interactive_config() -> dict:
    print("\n" + "=" * 60)
    print("  medical-rag — Configuração Inicial")
    print("=" * 60)
    print("\n  Bem-vindo! Vou configurar o RAG para seus livros médicos.\n")

    # 1. Modelo de embeddings
    print("[1/3] Modelo de embeddings para busca semântica:")
    for key, (name, label) in EMBEDDING_MODELS.items():
        print(f"  [{key}] {label}")
    print("  [4] Outro (digitar nome do HuggingFace)\n")

    choice = input("  Escolha [1]: ").strip() or "1"
    if choice == "4":
        model_name = input("  Nome do modelo HuggingFace: ").strip()
        if not model_name:
            model_name = "FremyCompany/BioLORD-2023-M"
    elif choice in EMBEDDING_MODELS:
        model_name = EMBEDDING_MODELS[choice][0]
    else:
        model_name = "FremyCompany/BioLORD-2023-M"
    print(f"  → Modelo: {model_name}\n")

    # 2. Idiomas OCR
    print("[2/3] Idiomas para OCR (separados por vírgula):")
    for code, name in AVAILABLE_OCR_LANGUAGES.items():
        marker = " ←" if code in DEFAULT_OCR_LANGUAGES else ""
        print(f"    {code} = {name}{marker}")
    print("  Ou digite outro código Tesseract.\n")

    lang_input = input(f"  Idiomas [{','.join(DEFAULT_OCR_LANGUAGES)}]: ").strip()
    ocr_languages = [l.strip() for l in lang_input.split(",") if l.strip()] if lang_input else DEFAULT_OCR_LANGUAGES.copy()

    installed = get_tesseract_languages()
    if installed:
        missing = [l for l in ocr_languages if l not in installed]
        if missing:
            print(f"  AVISO: idiomas não encontrados no Tesseract: {', '.join(missing)}")
    print(f"  → Idiomas OCR: {', '.join(ocr_languages)}\n")

    # 3. Chunk size
    print("[3/3] Tamanho do chunk (em tokens):")
    print("  Para livros de 1000+ páginas, recomendamos 1000 tokens com 200 de overlap.\n")

    cs = input(f"  Chunk size [{DEFAULT_CHUNK_SIZE}]: ").strip()
    chunk_size = int(cs) if cs.isdigit() else DEFAULT_CHUNK_SIZE
    ov = input(f"  Overlap [{DEFAULT_CHUNK_OVERLAP}]: ").strip()
    chunk_overlap = int(ov) if ov.isdigit() else DEFAULT_CHUNK_OVERLAP
    print(f"  → Chunk: {chunk_size} tokens, overlap: {chunk_overlap}\n")

    return {
        "embedding_model": model_name,
        "ocr_languages": ocr_languages,
        "chunk_size_tokens": chunk_size,
        "chunk_overlap_tokens": chunk_overlap,
        "min_image_dimension": DEFAULT_MIN_IMAGE_DIM,
        "data_dir": str(DATA_DIR),
        "configured_at": datetime.now(timezone.utc).isoformat(),
    }


def save_config(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Configuração salva em {CONFIG_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Setup da skill medical-rag")
    parser.add_argument("--reconfigure", action="store_true", help="Re-executa a configuração interativa")
    args = parser.parse_args()

    print("=" * 60)
    print("  medical-rag — Inicialização")
    print("=" * 60)
    print(f"\n  Skill dir: {SKILL_DIR}")
    print(f"  Venv dir:  {VENV_DIR}\n")

    N = 5

    # 1. Criar venv
    if not VENV_DIR.exists():
        print(f"[1/{N}] Criando ambiente virtual (.venv)...")
        run([sys.executable, "-m", "venv", str(VENV_DIR)])
        print("  OK\n")
    else:
        print(f"[1/{N}] .venv já existe, pulando.\n")

    python = venv_python()
    if not python.exists():
        print(f"ERRO: Python do venv não encontrado em {python}")
        sys.exit(1)

    # 2. Pip
    print(f"[2/{N}] Atualizando pip...")
    run([str(python), "-m", "pip", "install", "--upgrade", "pip", "-q"])
    print("  OK\n")

    # 3. Deps
    print(f"[3/{N}] Instalando dependências: {', '.join(PACKAGES)}")
    run([str(python), "-m", "pip", "install"] + PACKAGES + ["-q"])
    print("  OK\n")

    # 4. Tesseract
    print(f"[4/{N}] Verificando Tesseract...")
    tess_ok = check_tesseract()
    if tess_ok:
        langs = get_tesseract_languages()
        print(f"  OK (idiomas: {', '.join(langs[:8])}{'...' if len(langs) > 8 else ''})")
    else:
        print("  AVISO: Tesseract não encontrado (OCR não funcionará)")
    print()

    # 5. Diretórios e config
    print(f"[5/{N}] Configurando diretórios e preferências...")
    for d in [DATA_DIR, CHROMADB_DIR, IMAGES_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    if args.reconfigure or not CONFIG_PATH.exists():
        config = interactive_config()
        save_config(config)
    else:
        print(f"  Config existe em {CONFIG_PATH}, pulando. (Use --reconfigure para alterar)")
    print()

    print("=" * 60)
    print("  Inicialização concluída!")
    print("=" * 60)
    print(f"\n  Python: {python}")
    print(f"  Dados:  {DATA_DIR}")
    if not tess_ok:
        print("\n  ATENÇÃO: Instale Tesseract: brew install tesseract tesseract-lang")
    print()


if __name__ == "__main__":
    main()
