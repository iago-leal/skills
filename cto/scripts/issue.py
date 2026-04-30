#!/usr/bin/env python3
"""
issue.py — CRUD de issue via gh CLI, com template literal obrigatório.

Subcomandos:
  open    cria issue com label tipada + corpo seguindo template
  update  append de comentário (achado/atualização)
  close   exige --pr <url> --commit <sha>

CLI completa: ver SPEC §4.4.

Exit codes:
  0  sucesso
  1  erro inesperado
  2  argumento inválido (label fora do enum, --pr/--commit ausentes em close)
  4  gh CLI não autenticado
  5  repo GitHub não detectado
  6  issue não encontrada
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


ALLOWED_TYPES = {"feat", "bug", "chore", "spike", "incident", "tech-debt"}
ALLOWED_COMPLEXITY = {"S", "M", "L", "XL"}


def ensure_gh_auth() -> None:
    r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write("Erro: gh CLI não autenticado. Rode `gh auth login`.\n")
        sys.exit(4)


def detect_repo(explicit: str | None) -> str:
    if explicit:
        return explicit
    r = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0 or not r.stdout.strip():
        sys.stderr.write(
            "Erro: repo GitHub não detectado. Use --repo <owner/name>.\n"
        )
        sys.exit(5)
    return r.stdout.strip()


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def render_list(items: list[str]) -> str:
    if not items:
        return "—"
    return "\n".join(f"- {item}" for item in items)


def build_body(
    issue_type: str,
    hypothesis: str,
    acceptance: list[str],
    dod: list[str],
    dependencies: list[str],
    complexity: str,
    archetype: str | None,
) -> str:
    iso_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    deps_str = (
        render_list([f"#{d}" for d in dependencies]) if dependencies else "—"
    )
    archetype_str = archetype if archetype else "—"
    return (
        f"## Hipótese\n{hypothesis}\n\n"
        f"## Critério de Aceite\n{render_list(acceptance)}\n\n"
        f"## Definição de Pronto\n{render_list(dod)}\n\n"
        f"## Dependências\n{deps_str}\n\n"
        f"## Complexidade\n{complexity}\n\n"
        f"## Archetype sugerido\n{archetype_str}\n\n"
        f"---\nAberta via `/cto` em {iso_date}.\n"
    )


def cmd_open(args: argparse.Namespace) -> dict:
    if args.type not in ALLOWED_TYPES:
        sys.stderr.write(
            f"Erro: argumento inválido — --type deve estar em "
            f"{sorted(ALLOWED_TYPES)}\n"
        )
        sys.exit(2)
    if args.complexity not in ALLOWED_COMPLEXITY:
        sys.stderr.write(
            f"Erro: argumento inválido — --complexity deve estar em "
            f"{sorted(ALLOWED_COMPLEXITY)}\n"
        )
        sys.exit(2)

    repo = detect_repo(args.repo)
    acceptance = parse_csv(args.acceptance)
    dod = parse_csv(args.dod)
    dependencies = parse_csv(args.depends_on)
    if not acceptance:
        sys.stderr.write(
            "Erro: argumento inválido — --acceptance precisa de pelo menos 1 item.\n"
        )
        sys.exit(2)
    if not dod:
        sys.stderr.write(
            "Erro: argumento inválido — --dod precisa de pelo menos 1 item.\n"
        )
        sys.exit(2)

    body = build_body(
        issue_type=args.type,
        hypothesis=args.hypothesis,
        acceptance=acceptance,
        dod=dod,
        dependencies=dependencies,
        complexity=args.complexity,
        archetype=args.archetype,
    )

    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        repo,
        "--title",
        args.title,
        "--body",
        body,
        "--label",
        args.type,
    ]
    if args.milestone:
        cmd.extend(["--milestone", str(args.milestone)])

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(f"Erro abrindo issue: {r.stderr}\n")
        sys.exit(1)

    url = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    number = None
    if "/issues/" in url:
        try:
            number = int(url.rsplit("/", 1)[-1])
        except ValueError:
            number = None

    return {
        "action": "open",
        "issue": {
            "number": number,
            "title": args.title,
            "url": url,
            "state": "open",
            "labels": [args.type],
            "milestone": args.milestone,
        },
    }


def cmd_update(args: argparse.Namespace) -> dict:
    repo = detect_repo(args.repo)
    iso_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = f"**Achado em {iso_date}**\n\n{args.finding}"
    r = subprocess.run(
        ["gh", "issue", "comment", str(args.number), "--repo", repo, "--body", body],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        if "could not resolve" in r.stderr.lower() or "not found" in r.stderr.lower():
            sys.stderr.write(
                f"Erro: issue #{args.number} não existe no repo {repo}.\n"
            )
            sys.exit(6)
        sys.stderr.write(f"Erro comentando: {r.stderr}\n")
        sys.exit(1)
    return {
        "action": "update",
        "issue": {
            "number": args.number,
            "url": r.stdout.strip(),
        },
    }


def cmd_close(args: argparse.Namespace) -> dict:
    if not args.pr or not args.commit:
        sys.stderr.write(
            "Erro: argumento inválido — close exige --pr <url> e --commit <sha>.\n"
        )
        sys.exit(2)
    repo = detect_repo(args.repo)
    iso_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    closing_comment = (
        f"**Fechada em {iso_date}**\n\n"
        f"- PR: {args.pr}\n"
        f"- Commit: `{args.commit}`\n"
    )
    cr = subprocess.run(
        [
            "gh",
            "issue",
            "comment",
            str(args.number),
            "--repo",
            repo,
            "--body",
            closing_comment,
        ],
        capture_output=True,
        text=True,
    )
    if cr.returncode != 0:
        if "could not resolve" in cr.stderr.lower() or "not found" in cr.stderr.lower():
            sys.stderr.write(
                f"Erro: issue #{args.number} não existe no repo {repo}.\n"
            )
            sys.exit(6)
        sys.stderr.write(f"Erro postando comentário de fechamento: {cr.stderr}\n")
        sys.exit(1)

    r = subprocess.run(
        ["gh", "issue", "close", str(args.number), "--repo", repo],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        sys.stderr.write(f"Erro fechando issue: {r.stderr}\n")
        sys.exit(1)

    return {
        "action": "close",
        "issue": {
            "number": args.number,
            "state": "closed",
            "pr": args.pr,
            "commit": args.commit,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="CRUD de issue no GitHub")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_open = sub.add_parser("open", help="cria issue com template")
    p_open.add_argument("--title", required=True)
    p_open.add_argument(
        "--type",
        required=True,
        choices=sorted(ALLOWED_TYPES),
        help=f"label tipada (uma de {sorted(ALLOWED_TYPES)})",
    )
    p_open.add_argument("--hypothesis", required=True)
    p_open.add_argument(
        "--acceptance",
        required=True,
        help="critérios de aceite (CSV)",
    )
    p_open.add_argument(
        "--dod",
        required=True,
        help="definição de pronto (CSV)",
    )
    p_open.add_argument(
        "--complexity",
        required=True,
        choices=sorted(ALLOWED_COMPLEXITY),
    )
    p_open.add_argument("--milestone", type=int)
    p_open.add_argument("--depends-on", help="numbers de issues bloqueadoras (CSV)")
    p_open.add_argument("--archetype")
    p_open.add_argument("--repo")
    p_open.add_argument("--json", action="store_true")

    p_upd = sub.add_parser("update", help="adiciona comentário com achado")
    p_upd.add_argument("--number", type=int, required=True)
    p_upd.add_argument("--finding", required=True)
    p_upd.add_argument("--repo")
    p_upd.add_argument("--json", action="store_true")

    p_close = sub.add_parser("close", help="fecha issue exigindo PR + commit")
    p_close.add_argument("--number", type=int, required=True)
    p_close.add_argument("--pr", required=True)
    p_close.add_argument("--commit", required=True)
    p_close.add_argument("--repo")
    p_close.add_argument("--json", action="store_true")

    args = parser.parse_args()

    ensure_gh_auth()

    if args.cmd == "open":
        out = cmd_open(args)
    elif args.cmd == "update":
        out = cmd_update(args)
    elif args.cmd == "close":
        out = cmd_close(args)
    else:
        sys.stderr.write("Erro: subcomando inválido.\n")
        return 2

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
