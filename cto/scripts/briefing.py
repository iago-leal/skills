#!/usr/bin/env python3
"""
briefing.py — Session opener da skill /cto (v1.2.0).

Coleta estado atual do projeto via gh CLI e filesystem (docs/adr/),
emitindo briefing consumido pelo orquestrador.

Modos (mutuamente exclusivos):
  default             coleta via gh, sem cache (comportamento legado v1.1.x)
  --from-memory       lê .cto/state.json; falha (exit 8) se stale/ausente
  --update-memory     coleta via gh + escreve .cto/state.json + valida .gitignore

CLI:
  python scripts/briefing.py [--repo <owner/name>]
                              [--from-memory | --update-memory]
                              [--verbose] [--json]

Exit codes:
  0  sucesso
  1  erro inesperado
  2  argumento inválido
  4  gh CLI não autenticado
  5  repo GitHub não detectado
  8  memória stale ou ausente (--from-memory)
  9  .cto/ rastreado em git (privacy leak)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CTO_DIR = Path(".cto")
STATE_PATH = CTO_DIR / "state.json"
GITIGNORE_PATH = Path(".gitignore")
STALE_HOURS = 24


# ---------- gh & repo detection ----------

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
        sys.stderr.write("Erro: repo GitHub não detectado. Use --repo <owner/name>.\n")
        sys.exit(5)
    return r.stdout.strip()


def gh_api(path: str) -> object:
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(f"Aviso: gh api {path} falhou: {r.stderr}\n")
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


# ---------- coleta ----------

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
        out.append({
            "number": m["number"],
            "title": m["title"],
            "due_on": m.get("due_on"),
            "progress": progress,
            "issues_open": open_issues,
            "issues_closed": closed_issues,
            "url": m.get("html_url", ""),
        })
    return out


def latest_milestone_number(repo: str) -> int:
    """Maior milestone number conhecido (aberto OU fechado), pra delta-check."""
    raw = gh_api(f"repos/{repo}/milestones?state=all&per_page=1&sort=created&direction=desc")
    if isinstance(raw, list) and raw:
        return raw[0].get("number", 0)
    return 0


def list_issues_in_progress(repo: str) -> list[dict]:
    r = subprocess.run(
        ["gh", "issue", "list", "--repo", repo, "--state", "open",
         "--label", "in-progress", "--limit", "50",
         "--json", "number,title,labels,assignees,milestone,updatedAt,url"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return []
    try:
        raw = json.loads(r.stdout)
    except json.JSONDecodeError:
        return []
    out = []
    for it in raw:
        out.append({
            "number": it["number"],
            "title": it["title"],
            "labels": [l["name"] for l in it.get("labels", [])],
            "assignee": it["assignees"][0]["login"] if it.get("assignees") else None,
            "milestone": it["milestone"].get("number") if it.get("milestone") else None,
            "last_update": it.get("updatedAt"),
            "url": it.get("url", ""),
        })
    return out


def latest_issue_event_at(repo: str) -> str | None:
    """ISO8601 do updatedAt mais recente entre issues abertas, pra delta-check."""
    r = subprocess.run(
        ["gh", "issue", "list", "--repo", repo, "--state", "all", "--limit", "1",
         "--json", "updatedAt"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return None
    try:
        raw = json.loads(r.stdout)
        if raw:
            return raw[0].get("updatedAt")
    except json.JSONDecodeError:
        pass
    return None


def find_blockers(repo: str) -> list[dict]:
    r = subprocess.run(
        ["gh", "issue", "list", "--repo", repo, "--state", "open",
         "--label", "blocked", "--limit", "50", "--json", "number,body"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return []
    try:
        raw = json.loads(r.stdout)
    except json.JSONDecodeError:
        return []
    out = []
    pat = re.compile(r"blocked by\s+#(\d+)", re.IGNORECASE)
    for it in raw:
        body = it.get("body", "") or ""
        matches = pat.findall(body)
        out.append({
            "issue": it["number"],
            "blocked_by": [int(m) for m in matches],
            "reason": (f"Aguardando #{', #'.join(matches)}"
                       if matches else f"Bloqueada (ver corpo da issue #{it['number']})"),
        })
    return out


def recent_adrs(limit: int = 5) -> list[dict]:
    adr_dir = Path("docs/adr")
    if not adr_dir.is_dir():
        return []
    files = sorted(
        [p for p in adr_dir.glob("*.md") if p.is_file()],
        key=lambda p: p.stat().st_mtime, reverse=True,
    )[:limit]
    out = []
    fm_pat = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        m = fm_pat.match(text)
        title, status, date = f.stem, "unknown", ""
        if m:
            fm = m.group(1)
            for field, var_name in (("title", "title"), ("status", "status"), ("date", "date")):
                mm = re.search(rf"^{field}:\s*(.+)$", fm, re.MULTILINE)
                if mm:
                    val = mm.group(1).strip()
                    if var_name == "title":
                        title = val
                    elif var_name == "status":
                        status = val
                    else:
                        date = val
        out.append({"path": str(f), "title": title, "status": status, "date": date})
    return out


def latest_adr_number() -> int:
    """Maior NNNN encontrado em docs/adr/. 0 se diretório vazio/ausente."""
    adr_dir = Path("docs/adr")
    if not adr_dir.is_dir():
        return 0
    pat = re.compile(r"^(\d{4})-")
    nums = []
    for p in adr_dir.glob("*.md"):
        m = pat.match(p.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else 0


def suggest_next_steps(milestones, issues, blockers) -> list[dict]:
    suggestions = []
    blocking_nums = set()
    for b in blockers:
        for n in b.get("blocked_by", []):
            blocking_nums.add(n)
    for n in sorted(blocking_nums):
        suggestions.append({
            "priority": 1,
            "description": f"Resolver issue #{n} — está bloqueando outras",
            "rationale": "Destrava cadeia de dependências",
        })
    for m in milestones:
        if m.get("progress", 0) >= 0.7:
            suggestions.append({
                "priority": 2,
                "description": (f"Considerar fechamento de milestone #{m['number']} "
                                f"({m['title']}) — progresso {m['progress']:.0%}"),
                "rationale": "Próximo do critério de release",
            })
    if not issues and milestones:
        suggestions.append({
            "priority": 3,
            "description": "Selecionar próxima issue do milestone ativo para iniciar",
            "rationale": "Nenhuma issue em andamento",
        })
    return suggestions


# ---------- memória (.cto/state.json) ----------

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def ensure_gitignored() -> None:
    """Cria .gitignore se ausente; adiciona linha .cto/ se não existe."""
    line = ".cto/"
    if GITIGNORE_PATH.exists():
        content = GITIGNORE_PATH.read_text(encoding="utf-8")
        if any(l.strip() == line or l.strip() == ".cto" for l in content.splitlines()):
            return
        sep = "" if content.endswith("\n") else "\n"
        GITIGNORE_PATH.write_text(content + sep + line + "\n", encoding="utf-8")
    else:
        GITIGNORE_PATH.write_text(line + "\n", encoding="utf-8")


def assert_cto_not_tracked() -> None:
    """Aborta com exit 9 se .cto/ aparece staged em git."""
    r = subprocess.run(
        ["git", "status", "--porcelain", "--", ".cto/"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return  # não é repo git ou git ausente; tolerar
    for line in r.stdout.splitlines():
        # Formato: "XY path"; X = staged, Y = unstaged. Linha staged não-vazia indica problema.
        if line and line[0] not in (" ", "?"):
            sys.stderr.write(
                "Erro: .cto/ aparece staged em git. "
                "Adicione .cto/ ao .gitignore e remova do staging antes de prosseguir.\n"
            )
            sys.exit(9)


def read_state() -> dict | None:
    if not STATE_PATH.exists():
        return None
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def is_state_stale(state: dict, repo: str) -> tuple[bool, str]:
    """Retorna (stale?, reason). Faz delta-check leve contra gh."""
    last = parse_iso(state.get("last_synced_at", ""))
    if last is None:
        return True, "last_synced_at ausente ou inválido"
    age = datetime.now(timezone.utc) - last
    if age > timedelta(hours=STALE_HOURS):
        return True, f"last_synced_at ({state.get('last_synced_at')}) > {STALE_HOURS}h"
    synced = state.get("synced_against", {})
    cur_adr = latest_adr_number()
    if cur_adr > synced.get("latest_adr_number", 0):
        return True, f"novo ADR detectado ({synced.get('latest_adr_number')} → {cur_adr})"
    cur_ms = latest_milestone_number(repo)
    if cur_ms > synced.get("latest_milestone_number", 0):
        return True, f"novo milestone detectado ({synced.get('latest_milestone_number')} → {cur_ms})"
    return False, "fresh"


def write_state(data: dict) -> None:
    CTO_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False),
        encoding="utf-8",
    )


def collect_full(repo: str) -> dict:
    sys.stderr.write(f"Coletando estado de {repo}...\n")
    milestones = list_milestones(repo)
    issues = list_issues_in_progress(repo)
    blockers = find_blockers(repo)
    adrs = recent_adrs()
    next_steps = suggest_next_steps(milestones, issues, blockers)
    return {
        "last_synced_at": now_iso(),
        "repo": repo,
        "synced_against": {
            "latest_adr_number": latest_adr_number(),
            "latest_milestone_number": latest_milestone_number(repo),
            "latest_issue_event_at": latest_issue_event_at(repo),
        },
        "milestones": milestones,
        "issues_in_progress": issues,
        "blockers": blockers,
        "recent_adrs": adrs,
        "next_steps": next_steps,
    }


# ---------- output ----------

def render_compact(data: dict, source: str) -> str:
    """Renderiza briefing humano compacto. source ∈ {'gh', 'cache'}."""
    lines = [
        f"Repo: {data['repo']}",
        f"Sincronizado: {data.get('last_synced_at', data.get('generated_at', '?'))} ({source})",
        "",
    ]
    ms = data.get("milestones", [])
    lines.append(f"Milestones abertos ({len(ms)}):")
    if not ms:
        lines.append("  (nenhum)")
    for m in ms:
        due = f" — vence {m['due_on'][:10]}" if m.get("due_on") else ""
        lines.append(f"  #{m['number']} {m['title']} — {m['progress']:.0%}{due}")
    lines.append("")

    issues = data.get("issues_in_progress", [])
    lines.append(f"Issues em andamento ({len(issues)}):")
    if not issues:
        lines.append("  (nenhuma)")
    for it in issues:
        labels = ",".join(it.get("labels", [])) or "—"
        assignee = f"@{it['assignee']}" if it.get("assignee") else "—"
        lines.append(f"  #{it['number']} [{labels}] {it['title']} — {assignee}")
    lines.append("")

    blockers = data.get("blockers", [])
    if blockers:
        lines.append(f"Bloqueios ({len(blockers)}):")
        for b in blockers:
            bl = ",".join(f"#{n}" for n in b.get("blocked_by", [])) or "—"
            lines.append(f"  #{b['issue']} ← {bl}")
        lines.append("")

    adrs = data.get("recent_adrs", [])
    if adrs:
        lines.append(f"ADRs recentes ({len(adrs)}):")
        for a in adrs:
            lines.append(f"  {Path(a['path']).stem} [{a['status']}] {a['title']}")
        lines.append("")

    next_steps = data.get("next_steps", [])
    if next_steps:
        lines.append(f"Próximos passos sugeridos ({len(next_steps)}):")
        for s in sorted(next_steps, key=lambda x: x.get("priority", 99)):
            lines.append(f"  {s['priority']}. {s['description']}")
    return "\n".join(lines)


# ---------- main ----------

def main() -> int:
    p = argparse.ArgumentParser(
        description="Briefing de estado do projeto (memory-aware)"
    )
    p.add_argument("--repo", help="repo GitHub (formato owner/name)")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--from-memory", action="store_true",
                      help="lê .cto/state.json; falha (exit 8) se stale")
    mode.add_argument("--update-memory", action="store_true",
                      help="coleta via gh + escreve .cto/state.json")
    p.add_argument("--verbose", action="store_true", help="output detalhado")
    p.add_argument("--json", action="store_true", help="emite JSON em stdout")
    args = p.parse_args()

    # Caso A: --from-memory (sem chamar gh)
    if args.from_memory:
        state = read_state()
        if state is None:
            sys.stderr.write(
                "Erro: .cto/state.json ausente. Rode com --update-memory.\n"
            )
            sys.exit(8)
        repo = args.repo or state.get("repo") or detect_repo()
        # delta-check leve (precisa de gh para latest_milestone_number)
        ensure_gh_auth()
        stale, reason = is_state_stale(state, repo)
        if stale:
            sys.stderr.write(
                f"Erro: memória stale — {reason}. Rode com --update-memory.\n"
            )
            sys.exit(8)
        if args.json:
            print(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=False))
        else:
            print(render_compact(state, source="cache"))
        return 0

    # Caso B: --update-memory (coleta + escreve)
    if args.update_memory:
        ensure_gh_auth()
        assert_cto_not_tracked()
        repo = args.repo or detect_repo()
        data = collect_full(repo)
        ensure_gitignored()
        write_state(data)
        sys.stderr.write(f"Memória escrita: {STATE_PATH}\n")
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False))
        else:
            print(render_compact(data, source="gh+cache"))
        return 0

    # Caso C: legado (sem cache)
    ensure_gh_auth()
    repo = args.repo or detect_repo()
    data = collect_full(repo)
    # remove campos de cache pra não confundir
    data.pop("synced_against", None)
    data["generated_at"] = data.pop("last_synced_at")
    if args.json or args.verbose:
        print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False))
    else:
        print(render_compact(data, source="gh"))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        sys.stderr.write(f"Erro: {e}\n")
        sys.exit(1)
