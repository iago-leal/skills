#!/usr/bin/env python3
"""
milestone.py — CRUD de milestone via gh CLI.

Subcomandos:
  open    cria milestone com escopo + critério de release + RACI
  update  atualiza campos
  close   fecha milestone

CLI completa: ver SPEC §4.3.

Exit codes:
  0  sucesso
  1  erro inesperado
  2  argumento inválido
  4  gh CLI não autenticado
  5  repo GitHub não detectado
  6  milestone não encontrado
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


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


def build_description(
    scope: str,
    release_criterion: str,
    responsible: str,
    accountable: str,
    consulted: list[str],
    informed: list[str],
) -> str:
    consulted_str = ", ".join(consulted) if consulted else "—"
    informed_str = ", ".join(informed) if informed else "—"
    iso_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return (
        f"## Escopo\n{scope}\n\n"
        f"## Critério de Release\n{release_criterion}\n\n"
        f"## RACI (Responsible Accountable Consulted Informed)\n"
        f"- **Responsible**: {responsible}\n"
        f"- **Accountable**: {accountable}\n"
        f"- **Consulted**: {consulted_str}\n"
        f"- **Informed**: {informed_str}\n\n"
        f"---\nCriado via `/cto` em {iso_date}.\n"
    )


def cmd_open(args: argparse.Namespace) -> dict:
    repo = detect_repo(args.repo)
    description = build_description(
        scope=args.scope,
        release_criterion=args.release_criterion,
        responsible=args.raci_responsible,
        accountable=args.raci_accountable,
        consulted=parse_csv(args.raci_consulted),
        informed=parse_csv(args.raci_informed),
    )
    api_args = [
        "gh",
        "api",
        f"repos/{repo}/milestones",
        "-f",
        f"title={args.title}",
        "-f",
        f"description={description}",
    ]
    if args.due:
        api_args.extend(["-f", f"due_on={args.due}"])
    r = subprocess.run(api_args, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(f"Erro abrindo milestone: {r.stderr}\n")
        sys.exit(1)
    data = json.loads(r.stdout)
    return {
        "action": "open",
        "milestone": {
            "number": data["number"],
            "title": data["title"],
            "url": data.get("html_url", ""),
            "state": data.get("state", "open"),
            "due_on": data.get("due_on"),
        },
    }


def cmd_update(args: argparse.Namespace) -> dict:
    repo = detect_repo(args.repo)
    api_args = ["gh", "api", "-X", "PATCH", f"repos/{repo}/milestones/{args.number}"]
    if args.title:
        api_args.extend(["-f", f"title={args.title}"])
    if args.due:
        api_args.extend(["-f", f"due_on={args.due}"])
    if args.scope or args.release_criterion:
        cur = subprocess.run(
            ["gh", "api", f"repos/{repo}/milestones/{args.number}"],
            capture_output=True,
            text=True,
        )
        if cur.returncode != 0:
            sys.stderr.write(
                f"Erro: milestone #{args.number} não existe no repo {repo}.\n"
            )
            sys.exit(6)
        cur_data = json.loads(cur.stdout)
        cur_desc = cur_data.get("description", "")
        new_desc = cur_desc
        if args.scope:
            new_desc = _replace_section(new_desc, "Escopo", args.scope)
        if args.release_criterion:
            new_desc = _replace_section(
                new_desc, "Critério de Release", args.release_criterion
            )
        api_args.extend(["-f", f"description={new_desc}"])
    r = subprocess.run(api_args, capture_output=True, text=True)
    if r.returncode != 0:
        if "Not Found" in r.stderr:
            sys.stderr.write(
                f"Erro: milestone #{args.number} não existe no repo {repo}.\n"
            )
            sys.exit(6)
        sys.stderr.write(f"Erro atualizando milestone: {r.stderr}\n")
        sys.exit(1)
    data = json.loads(r.stdout)
    return {
        "action": "update",
        "milestone": {
            "number": data["number"],
            "title": data["title"],
            "url": data.get("html_url", ""),
            "state": data.get("state", "open"),
            "due_on": data.get("due_on"),
        },
    }


def cmd_close(args: argparse.Namespace) -> dict:
    repo = detect_repo(args.repo)
    r = subprocess.run(
        [
            "gh",
            "api",
            "-X",
            "PATCH",
            f"repos/{repo}/milestones/{args.number}",
            "-f",
            "state=closed",
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        if "Not Found" in r.stderr:
            sys.stderr.write(
                f"Erro: milestone #{args.number} não existe no repo {repo}.\n"
            )
            sys.exit(6)
        sys.stderr.write(f"Erro fechando milestone: {r.stderr}\n")
        sys.exit(1)
    data = json.loads(r.stdout)
    return {
        "action": "close",
        "milestone": {
            "number": data["number"],
            "title": data["title"],
            "url": data.get("html_url", ""),
            "state": data.get("state", "closed"),
            "due_on": data.get("due_on"),
        },
    }


def _replace_section(body: str, section_name: str, new_content: str) -> str:
    import re

    pattern = re.compile(
        rf"(##\s+{re.escape(section_name)}\s*\n)(.*?)(\n##\s|\Z)",
        re.DOTALL,
    )
    if pattern.search(body):
        return pattern.sub(rf"\g<1>{new_content}\n\g<3>", body, count=1)
    return body + f"\n\n## {section_name}\n{new_content}\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="CRUD de milestone no GitHub")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_open = sub.add_parser("open", help="cria milestone")
    p_open.add_argument("--title", required=True)
    p_open.add_argument("--scope", required=True)
    p_open.add_argument("--release-criterion", required=True)
    p_open.add_argument("--raci-responsible", required=True)
    p_open.add_argument("--raci-accountable", required=True)
    p_open.add_argument("--raci-consulted")
    p_open.add_argument("--raci-informed")
    p_open.add_argument("--due", help="ISO 8601 (ex: 2026-05-15T00:00:00Z)")
    p_open.add_argument("--repo")
    p_open.add_argument("--json", action="store_true")

    p_upd = sub.add_parser("update", help="atualiza milestone")
    p_upd.add_argument("--number", type=int, required=True)
    p_upd.add_argument("--title")
    p_upd.add_argument("--scope")
    p_upd.add_argument("--release-criterion")
    p_upd.add_argument("--due")
    p_upd.add_argument("--repo")
    p_upd.add_argument("--json", action="store_true")

    p_close = sub.add_parser("close", help="fecha milestone")
    p_close.add_argument("--number", type=int, required=True)
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
