#!/usr/bin/env python3
"""
briefing.py — Session opener da skill /cto.

Coleta estado atual do projeto via gh CLI e filesystem (docs/adr/),
emitindo JSON consumido pelo orquestrador para apresentar briefing ao usuário.

CLI:
  python scripts/briefing.py [--repo <owner/name>] [--json]

Exit codes:
  0  sucesso
  1  erro inesperado
  2  argumento inválido
  4  gh CLI não autenticado
  5  repo GitHub não detectado
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def ensure_gh_auth() -> None:
    r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write("Erro: gh CLI não autenticado. Rode `gh auth login`.\n")
        sys.exit(4)


def detect_repo() -> str:
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


def gh_api(path: str) -> object:
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(f"Erro chamando gh api {path}: {r.stderr}\n")
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def list_milestones(repo: str) -> list[dict]:
    raw = gh_api(f"repos/{repo}/milestones?state=open")
    if not isinstance(raw, list):
        return []
    out = []
    for m in raw:
        open_issues = m.get("open_issues", 0)
        closed_issues = m.get("closed_issues", 0)
        total = open_issues + closed_issues
        progress = round(closed_issues / total, 2) if total > 0 else 0.0
        out.append(
            {
                "number": m["number"],
                "title": m["title"],
                "due_on": m.get("due_on"),
                "progress": progress,
                "issues_open": open_issues,
                "issues_closed": closed_issues,
                "url": m.get("html_url", ""),
            }
        )
    return out


def list_issues_in_progress(repo: str) -> list[dict]:
    r = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--label",
            "in-progress",
            "--limit",
            "50",
            "--json",
            "number,title,labels,assignees,milestone,updatedAt,url",
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        sys.stderr.write(f"Aviso: falha listando issues in-progress: {r.stderr}\n")
        return []
    try:
        raw = json.loads(r.stdout)
    except json.JSONDecodeError:
        return []
    out = []
    for it in raw:
        out.append(
            {
                "number": it["number"],
                "title": it["title"],
                "labels": [l["name"] for l in it.get("labels", [])],
                "assignee": (
                    it["assignees"][0]["login"] if it.get("assignees") else None
                ),
                "milestone": (
                    it["milestone"].get("number") if it.get("milestone") else None
                ),
                "last_update": it.get("updatedAt"),
                "url": it.get("url", ""),
            }
        )
    return out


def find_blockers(repo: str) -> list[dict]:
    r = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--label",
            "blocked",
            "--limit",
            "50",
            "--json",
            "number,body",
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return []
    try:
        raw = json.loads(r.stdout)
    except json.JSONDecodeError:
        return []
    out = []
    blocked_by_pat = re.compile(r"blocked by\s+#(\d+)", re.IGNORECASE)
    for it in raw:
        body = it.get("body", "") or ""
        matches = blocked_by_pat.findall(body)
        out.append(
            {
                "issue": it["number"],
                "blocked_by": [int(m) for m in matches],
                "reason": (
                    f"Bloqueada (ver corpo da issue #{it['number']})"
                    if not matches
                    else f"Aguardando #{', #'.join(matches)}"
                ),
            }
        )
    return out


def recent_adrs(limit: int = 5) -> list[dict]:
    adr_dir = Path("docs/adr")
    if not adr_dir.is_dir():
        return []
    files = sorted(
        [p for p in adr_dir.glob("*.md") if p.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:limit]
    out = []
    fm_pat = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        m = fm_pat.match(text)
        title = f.stem
        status = "unknown"
        date = ""
        if m:
            fm = m.group(1)
            t_match = re.search(r"^title:\s*(.+)$", fm, re.MULTILINE)
            s_match = re.search(r"^status:\s*(.+)$", fm, re.MULTILINE)
            d_match = re.search(r"^date:\s*(.+)$", fm, re.MULTILINE)
            if t_match:
                title = t_match.group(1).strip()
            if s_match:
                status = s_match.group(1).strip()
            if d_match:
                date = d_match.group(1).strip()
        out.append(
            {
                "path": str(f),
                "title": title,
                "status": status,
                "date": date,
            }
        )
    return out


def suggest_next_steps(
    milestones: list[dict], issues: list[dict], blockers: list[dict]
) -> list[dict]:
    suggestions: list[dict] = []
    blocked_issue_numbers = {b["issue"] for b in blockers}
    blocking_issue_numbers: set[int] = set()
    for b in blockers:
        for n in b.get("blocked_by", []):
            blocking_issue_numbers.add(n)
    for n in sorted(blocking_issue_numbers):
        suggestions.append(
            {
                "priority": 1,
                "description": f"Resolver issue #{n} — está bloqueando outras",
                "rationale": "Destrava cadeia de dependências",
            }
        )
    for m in milestones:
        if m.get("progress", 0) >= 0.7:
            suggestions.append(
                {
                    "priority": 2,
                    "description": (
                        f"Considerar fechamento de milestone #{m['number']} "
                        f"({m['title']}) — progresso {m['progress']:.0%}"
                    ),
                    "rationale": "Próximo do critério de release",
                }
            )
    in_progress_count = len(issues)
    if in_progress_count == 0 and milestones:
        suggestions.append(
            {
                "priority": 3,
                "description": "Selecionar próxima issue do milestone ativo para iniciar",
                "rationale": "Nenhuma issue em andamento",
            }
        )
    return suggestions


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Session opener — briefing de estado do projeto"
    )
    parser.add_argument(
        "--repo",
        help="repo GitHub (formato owner/name); default = repo do cwd",
    )
    parser.add_argument(
        "--json", action="store_true", help="emite apenas JSON em stdout"
    )
    args = parser.parse_args()

    ensure_gh_auth()
    repo = args.repo or detect_repo()

    sys.stderr.write(f"Coletando estado de {repo}...\n")
    milestones = list_milestones(repo)
    issues = list_issues_in_progress(repo)
    blockers = find_blockers(repo)
    adrs = recent_adrs()
    next_steps = suggest_next_steps(milestones, issues, blockers)

    out = {
        "repo": repo,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "milestones": milestones,
        "issues_in_progress": issues,
        "blockers": blockers,
        "recent_adrs": adrs,
        "next_steps": next_steps,
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
