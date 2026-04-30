#!/usr/bin/env python3
"""
session_close.py — Fechamento de sessão da skill /cto (v1.2.0).

Consolida estado da sessão em `.cto/last-session.md` (narrativa compacta) e
atualiza `.cto/state.json` (cache do briefing). Reporta status das memórias
per-archetype para acionamento de refresh no próximo spawn.

Fluxo:
  1. Valida que .cto/ está gitignored e não staged (exit 9 se leak)
  2. Atualiza .cto/state.json via briefing.py --update-memory
  3. Lê narrativa estruturada via --narrative <path|->
  4. Compõe .cto/last-session.md com frontmatter YAML + corpo
  5. Reporta status das memórias per-archetype (stale, fresh, ausente)

CLI:
  python scripts/session_close.py --narrative <path|->
                                  [--archetypes <csv>]
                                  [--turns <int>] [--duration-min <int>]
                                  [--repo <owner/name>] [--json]

Exit codes:
  0  sucesso
  1  erro inesperado
  2  argumento inválido
  4  gh CLI não autenticado
  5  repo GitHub não detectado
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
LAST_SESSION_PATH = CTO_DIR / "last-session.md"
STATE_PATH = CTO_DIR / "state.json"
AGENTS_DIR = CTO_DIR / "agents"
GITIGNORE_PATH = Path(".gitignore")
STALE_HOURS = 24
ARCHETYPE_STALE_DAYS = 7
SCRIPT_DIR = Path(__file__).resolve().parent


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


# ---------- segurança ----------

def assert_cto_not_tracked() -> None:
    r = subprocess.run(
        ["git", "status", "--porcelain", "--", ".cto/"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return  # não é repo git; tolerar
    for line in r.stdout.splitlines():
        if line and line[0] not in (" ", "?"):
            sys.stderr.write(
                "Erro: .cto/ aparece staged em git. "
                "Adicione .cto/ ao .gitignore e remova do staging.\n"
            )
            sys.exit(9)


def ensure_gitignored() -> bool:
    """Garante .cto/ no .gitignore. Retorna True se acabou de adicionar."""
    line = ".cto/"
    if GITIGNORE_PATH.exists():
        content = GITIGNORE_PATH.read_text(encoding="utf-8")
        if any(l.strip() in (".cto/", ".cto") for l in content.splitlines()):
            return False
        sep = "" if content.endswith("\n") else "\n"
        GITIGNORE_PATH.write_text(content + sep + line + "\n", encoding="utf-8")
    else:
        GITIGNORE_PATH.write_text(line + "\n", encoding="utf-8")
    return True


# ---------- briefing snapshot ----------

def update_state_via_briefing(repo: str | None) -> dict:
    """Chama briefing.py --update-memory --json e retorna o state."""
    cmd = [sys.executable, str(SCRIPT_DIR / "briefing.py"), "--update-memory", "--json"]
    if repo:
        cmd.extend(["--repo", repo])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(f"Erro: briefing.py --update-memory falhou:\n{r.stderr}")
        sys.exit(r.returncode if r.returncode != 0 else 1)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.stderr.write("Erro: briefing.py retornou JSON inválido.\n")
        sys.exit(1)


# ---------- archetype memory status ----------

def archetype_memory_status(archetype: str, state: dict) -> dict:
    """Retorna dict com status da memória de um archetype: fresh|stale|missing."""
    mem_path = AGENTS_DIR / archetype / "memory.md"
    if not mem_path.exists():
        return {
            "archetype": archetype,
            "status": "missing",
            "path": str(mem_path),
            "action": "bootstrap no próximo spawn",
        }
    try:
        text = mem_path.read_text(encoding="utf-8")
    except OSError:
        return {"archetype": archetype, "status": "unreadable", "path": str(mem_path)}

    fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    last_synced = None
    synced_adr = 0
    synced_ms = 0
    if fm_match:
        fm = fm_match.group(1)
        m_last = re.search(r"^last_synced_at:\s*(.+)$", fm, re.MULTILINE)
        if m_last:
            last_synced = parse_iso(m_last.group(1).strip())
        m_adr = re.search(r"latest_adr_number:\s*(\d+)", fm)
        if m_adr:
            synced_adr = int(m_adr.group(1))
        m_ms = re.search(r"latest_milestone_number:\s*(\d+)", fm)
        if m_ms:
            synced_ms = int(m_ms.group(1))

    cur_adr = state.get("synced_against", {}).get("latest_adr_number", 0)
    cur_ms = state.get("synced_against", {}).get("latest_milestone_number", 0)

    if last_synced is None:
        return {"archetype": archetype, "status": "stale", "path": str(mem_path),
                "reason": "frontmatter sem last_synced_at",
                "action": "delta-check no próximo spawn"}

    age = datetime.now(timezone.utc) - last_synced
    if age > timedelta(days=ARCHETYPE_STALE_DAYS):
        return {"archetype": archetype, "status": "stale", "path": str(mem_path),
                "reason": f"last_synced_at > {ARCHETYPE_STALE_DAYS}d",
                "action": "refresh completo no próximo spawn"}
    if cur_adr > synced_adr or cur_ms > synced_ms:
        delta = []
        if cur_adr > synced_adr:
            delta.append(f"ADRs {synced_adr}→{cur_adr}")
        if cur_ms > synced_ms:
            delta.append(f"milestones {synced_ms}→{cur_ms}")
        return {"archetype": archetype, "status": "stale", "path": str(mem_path),
                "reason": "; ".join(delta),
                "action": "delta-check no próximo spawn"}
    return {"archetype": archetype, "status": "fresh", "path": str(mem_path)}


# ---------- last-session.md ----------

def read_narrative(src: str) -> str:
    if src == "-":
        return sys.stdin.read()
    p = Path(src)
    if not p.exists():
        sys.stderr.write(f"Erro: --narrative {src} não existe.\n")
        sys.exit(2)
    return p.read_text(encoding="utf-8")


def compose_last_session(narrative: str, state: dict, archetypes: list[str],
                         turns: int | None, duration_min: int | None) -> str:
    closed_at = now_iso()
    snapshot_at = state.get("last_synced_at", closed_at)
    repo = state.get("repo", "?")
    arch_yaml = "[" + ", ".join(archetypes) + "]" if archetypes else "[]"
    fm_lines = [
        "---",
        f"closed_at: {closed_at}",
        f"repo: {repo}",
        f"state_snapshot_at: {snapshot_at}",
        f"archetypes_spawned: {arch_yaml}",
    ]
    if turns is not None:
        fm_lines.append(f"turns_estimate: {turns}")
    if duration_min is not None:
        fm_lines.append(f"duration_minutes_estimate: {duration_min}")
    fm_lines.append("---")
    fm = "\n".join(fm_lines) + "\n\n"

    body = narrative.strip()
    # Sanity check leve: avisar se narrativa não tem as seções esperadas
    expected = ["## Marcos da sessão", "## Decisões em flight", "## Threads abertas",
                "## TL;DRs de ADRs tocados", "## TL;DRs de issues tocadas",
                "## Próximos passos sugeridos"]
    missing = [s for s in expected if s not in body]
    if missing:
        sys.stderr.write(
            "Aviso: narrativa não contém seções esperadas: " + ", ".join(missing) + "\n"
        )
    return fm + body + "\n"


# ---------- main ----------

def main() -> int:
    p = argparse.ArgumentParser(description="Fechamento de sessão /cto")
    p.add_argument("--narrative", required=True,
                   help="caminho para .md com narrativa estruturada, ou - para stdin")
    p.add_argument("--archetypes", default="",
                   help="CSV de archetypes spawnados (ex: backend-dev,security-engineer)")
    p.add_argument("--turns", type=int, help="estimativa de turns da sessão")
    p.add_argument("--duration-min", type=int, help="duração estimada em minutos")
    p.add_argument("--repo", help="repo GitHub (formato owner/name)")
    p.add_argument("--json", action="store_true", help="emite JSON em stdout")
    args = p.parse_args()

    archetypes = [a.strip() for a in args.archetypes.split(",") if a.strip()]

    # 1. segurança
    CTO_DIR.mkdir(parents=True, exist_ok=True)
    gitignore_added = ensure_gitignored()
    assert_cto_not_tracked()

    # 2. snapshot do estado
    state = update_state_via_briefing(args.repo)

    # 3. narrativa
    narrative = read_narrative(args.narrative)

    # 4. compor last-session.md
    last_session = compose_last_session(
        narrative, state, archetypes, args.turns, args.duration_min
    )
    LAST_SESSION_PATH.write_text(last_session, encoding="utf-8")
    sys.stderr.write(f"Escrito: {LAST_SESSION_PATH}\n")

    # 5. status de memórias per-archetype
    archetype_statuses = [archetype_memory_status(a, state) for a in archetypes]
    artifacts = [str(STATE_PATH), str(LAST_SESSION_PATH)]
    for s in archetype_statuses:
        if s.get("status") == "fresh":
            artifacts.append(s["path"])

    out = {
        "session_closed_at": state.get("last_synced_at"),
        "repo": state.get("repo"),
        "artifacts_written": artifacts,
        "gitignore_validated": True,
        "gitignore_added_now": gitignore_added,
        "archetype_memory_status": archetype_statuses,
    }

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=False))
    else:
        print(f"Sessão fechada — {out['repo']}")
        print(f"Snapshot: {out['session_closed_at']}")
        print(f"Artefatos: {', '.join(artifacts)}")
        if archetypes:
            print("Memórias per-archetype:")
            for s in archetype_statuses:
                line = f"  {s['archetype']} [{s['status']}]"
                if s.get("reason"):
                    line += f" — {s['reason']}"
                if s.get("action"):
                    line += f" → {s['action']}"
                print(line)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        sys.stderr.write(f"Erro: {e}\n")
        sys.exit(1)
