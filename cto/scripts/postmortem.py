#!/usr/bin/env python3
"""
postmortem.py — Gera issue postmortem a partir de issue incident fechada.

CLI:
  python scripts/postmortem.py --incident <int> [--repo <owner/name>] [--json]

Validações:
  - issue deve ter label `incident`
  - issue deve estar com state=closed

Exit codes:
  0  sucesso
  1  erro inesperado
  2  argumento inválido (issue não tem label `incident`, ou state != closed)
  4  gh CLI não autenticado
  5  repo não detectado
  6  issue não encontrada
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
        sys.stderr.write("Erro: repo GitHub não detectado. Use --repo <owner/name>.\n")
        sys.exit(5)
    return r.stdout.strip()


def fetch_incident(repo: str, number: int) -> dict:
    r = subprocess.run(
        [
            "gh",
            "issue",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            "number,title,state,labels,body,createdAt,closedAt,comments,url",
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        if "could not resolve" in r.stderr.lower() or "not found" in r.stderr.lower():
            sys.stderr.write(f"Erro: issue #{number} não existe no repo {repo}.\n")
            sys.exit(6)
        sys.stderr.write(f"Erro lendo issue: {r.stderr}\n")
        sys.exit(1)
    return json.loads(r.stdout)


def validate_incident(data: dict, number: int) -> None:
    labels = {l["name"] for l in data.get("labels", [])}
    if "incident" not in labels:
        sys.stderr.write(
            f"Erro: argumento inválido — issue #{number} não tem label `incident`.\n"
        )
        sys.exit(2)
    if data.get("state", "").lower() != "closed":
        sys.stderr.write(
            f"Erro: argumento inválido — issue #{number} não está fechada "
            f"(state={data.get('state')}).\n"
        )
        sys.exit(2)


def build_timeline(data: dict) -> list[dict]:
    events: list[dict] = []
    if data.get("createdAt"):
        events.append({"at": data["createdAt"], "event": "incidente reportado (issue aberta)"})
    for c in data.get("comments", []) or []:
        author = (c.get("author") or {}).get("login", "?")
        events.append(
            {
                "at": c.get("createdAt", ""),
                "event": f"comentário de @{author}",
                "preview": (c.get("body", "") or "")[:120],
            }
        )
    if data.get("closedAt"):
        events.append({"at": data["closedAt"], "event": "incidente contido (issue fechada)"})
    return events


def render_timeline(events: list[dict]) -> str:
    if not events:
        return "_(sem eventos extraídos automaticamente — preencher)_"
    lines = []
    for e in events:
        line = f"- **{e['at']}** — {e['event']}"
        if e.get("preview"):
            line += f"\n  > {e['preview']}"
        lines.append(line)
    return "\n".join(lines)


def build_postmortem_body(incident: dict, timeline: list[dict]) -> str:
    iso_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return (
        f"# Pós-morto — {incident['title']}\n\n"
        f"Linkado ao incidente original #{incident['number']}.\n\n"
        f"## Timeline\n{render_timeline(timeline)}\n\n"
        f"## Impacto\n"
        f"- Usuários afetados: _(preencher)_\n"
        f"- Duração: _(do reporte ao fechamento — extrair do timeline)_\n"
        f"- Receita / dados / SLA impactados: _(preencher)_\n\n"
        f"## Causa Raiz\n_(preencher após análise — não causa imediata, causa raiz)_\n\n"
        f"## Ação Corretiva (Tomada)\n- _(o que estancou o incidente — descrever)_\n\n"
        f"## Ação Preventiva (Proposta)\n"
        f"- [ ] ADR-NNNN: _(decisão arquitetural para evitar recorrência)_\n"
        f"- [ ] Issue chore #NNNN: _(ação operacional — alarme, runbook, etc.)_\n\n"
        f"## ADRs Gerados\n_(listar quando criados — link relativo)_\n\n"
        f"---\n"
        f"Gerado via `python scripts/postmortem.py --incident {incident['number']}` "
        f"em {iso_date}.\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gera issue postmortem a partir de incident fechado"
    )
    parser.add_argument("--incident", type=int, required=True)
    parser.add_argument("--repo")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ensure_gh_auth()
    repo = detect_repo(args.repo)
    incident = fetch_incident(repo, args.incident)
    validate_incident(incident, args.incident)
    timeline = build_timeline(incident)
    body = build_postmortem_body(incident, timeline)

    title = f"Pós-morto — {incident['title']}"
    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        repo,
        "--title",
        title,
        "--body",
        body,
        "--label",
        "postmortem",
        "--label",
        "incident",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(f"Erro criando pós-morto: {r.stderr}\n")
        sys.exit(1)

    url = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    number = None
    if "/issues/" in url:
        try:
            number = int(url.rsplit("/", 1)[-1])
        except ValueError:
            number = None

    out = {
        "postmortem": {
            "number": number,
            "url": url,
            "linked_incident": args.incident,
            "timeline_events": len(timeline),
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
