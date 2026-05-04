#!/usr/bin/env python3
"""
adr_new.py — Cria novo ADR (Architectural Decision Record) em docs/adr/.

CLI:
  python scripts/adr_new.py --title <str> --status <enum>
                            --context <str> --decision <str>
                            --consequences <str>
                            [--alternatives <csv>]
                            [--supersedes <int>]
                            [--debt-conscious]
                            [--json]

Exit codes:
  0  sucesso
  1  erro inesperado
  2  argumento inválido
  3  ADR com número duplicado (race)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path


ALLOWED_STATUS = {"proposed", "accepted", "deprecated", "superseded"}


def slugify(title: str, max_len: int = 50) -> str:
    norm = unicodedata.normalize("NFKD", title)
    ascii_only = "".join(c for c in norm if not unicodedata.combining(c))
    lowered = ascii_only.lower()
    safe = re.sub(r"[^a-z0-9\s-]", "", lowered)
    hyphen = re.sub(r"\s+", "-", safe).strip("-")
    collapsed = re.sub(r"-+", "-", hyphen)
    return collapsed[:max_len].rstrip("-") or "adr"


def next_number(adr_dir: Path) -> int:
    if not adr_dir.exists():
        return 1
    pat = re.compile(r"^(\d{4})-")
    used: list[int] = []
    for p in adr_dir.glob("*.md"):
        m = pat.match(p.name)
        if m:
            used.append(int(m.group(1)))
    return (max(used) + 1) if used else 1


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def render_alternatives(alts: list[str]) -> str:
    if not alts:
        return "—"
    out = []
    for i, a in enumerate(alts, start=1):
        out.append(f"### Alternativa {chr(64 + i)}: {a}\n_(motivo de descarte a registrar)_")
    return "\n\n".join(out)


def update_superseded(adr_dir: Path, target_number: int, new_number: int) -> None:
    pat = re.compile(rf"^{target_number:04d}-")
    for p in adr_dir.glob("*.md"):
        if pat.match(p.name):
            text = p.read_text(encoding="utf-8")
            text = re.sub(
                r"^(status:\s*)(.+)$",
                rf"\g<1>superseded",
                text,
                count=1,
                flags=re.MULTILINE,
            )
            text = re.sub(
                r"^(superseded_by:\s*)(.+)$",
                rf"\g<1>{new_number}",
                text,
                count=1,
                flags=re.MULTILINE,
            )
            if "superseded_by:" not in text:
                text = text.replace(
                    "---\n\n",
                    f"superseded_by: {new_number}\n---\n\n",
                    1,
                )
            p.write_text(text, encoding="utf-8")
            return
    sys.stderr.write(
        f"Aviso: ADR #{target_number} não encontrado para superseded link.\n"
    )


def build_adr(
    number: int,
    title: str,
    status: str,
    context: str,
    decision: str,
    consequences: str,
    alternatives: list[str],
    supersedes: int | None,
    debt_conscious: bool,
) -> str:
    today = date.today().isoformat()
    fm = (
        "---\n"
        f"adr: {number}\n"
        f"title: {title}\n"
        f"status: {status}\n"
        f"date: {today}\n"
        f"supersedes: {supersedes if supersedes else 'null'}\n"
        f"superseded_by: null\n"
        f"debt_conscious: {'true' if debt_conscious else 'false'}\n"
        "---\n\n"
    )

    body = f"# ADR-{number:04d}: {title}\n\n## Status\n{status}\n\n"
    if supersedes:
        body += f"Substitui ADR-{supersedes:04d}.\n\n"
    body += (
        f"## Contexto\n{context}\n\n"
        f"## Decisão\n{decision}\n\n"
        f"## Consequências\n{consequences}\n\n"
        f"## Alternativas Consideradas\n{render_alternatives(alternatives)}\n\n"
    )
    if debt_conscious:
        body += (
            "## Dívida Consciente Assumida\n"
            f"- **Assumida em**: {today}\n"
            "- **Justificativa**: ver seção Decisão.\n"
            "- **Prazo de revisita**: a definir e linkar à issue `tech-debt` correspondente.\n"
            "- **Issue tech-debt linkada**: #(preencher após abrir)\n\n"
        )
    body += "## Referências\n- (preencher com links de issue, milestone, benchmark, etc.)\n"
    return fm + body


def main() -> int:
    parser = argparse.ArgumentParser(description="Cria novo ADR em docs/adr/")
    parser.add_argument("--title", required=True)
    parser.add_argument(
        "--status",
        required=True,
        choices=sorted(ALLOWED_STATUS),
    )
    parser.add_argument("--context", required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--consequences", required=True)
    parser.add_argument("--alternatives", help="CSV de alternativas consideradas")
    parser.add_argument(
        "--supersedes",
        type=int,
        help="número de ADR substituído (atualiza o antigo)",
    )
    parser.add_argument(
        "--debt-conscious",
        action="store_true",
        help="marca como dívida técnica consciente assumida",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    adr_dir = Path("docs/adr")
    adr_dir.mkdir(parents=True, exist_ok=True)

    number = next_number(adr_dir)
    slug = slugify(args.title)
    filename = f"{number:04d}-{slug}.md"
    out_path = adr_dir / filename

    if out_path.exists():
        sys.stderr.write(
            f"Erro: ADR {number:04d} já existe em {out_path}.\n"
        )
        sys.exit(3)

    content = build_adr(
        number=number,
        title=args.title,
        status=args.status,
        context=args.context,
        decision=args.decision,
        consequences=args.consequences,
        alternatives=parse_csv(args.alternatives),
        supersedes=args.supersedes,
        debt_conscious=args.debt_conscious,
    )
    out_path.write_text(content, encoding="utf-8")

    if args.supersedes:
        update_superseded(adr_dir, args.supersedes, number)

    out = {
        "adr": {
            "number": number,
            "path": str(out_path),
            "title": args.title,
            "status": args.status,
            "date": date.today().isoformat(),
            "supersedes": args.supersedes,
            "debt_conscious": args.debt_conscious,
        }
    }
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        sys.stderr.write(f"Erro: {e}\n")
        sys.exit(1)
