#!/usr/bin/env python3
"""
recicla — Reciclagem determinística de componentes entre projetos.

Usage:
    python recicla.py <command> [options]

Commands:
    scan          List candidates for extraction in workspace.
    extract       Move component(s) from workspace to library.
    suggest       List library components matching workspace needs.
    inject        Copy component from library to workspace.
    audit         Check integrity of library and workspace manifest.
    render-index  Regenerate INDEX.md from index.json.

See SPEC.md and reference/operations.md for details.

This implementation uses only the Python standard library (>= 3.9).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERSION = "1.1.0"
INDEX_SCHEMA_VERSION = "1.1"
MANIFEST_SCHEMA_VERSION = "1.1"

# --- Bundle constants (schema 1.1) ---
BUNDLE_DIR_REL = ".recicla/bundles"          # workspace-relative path
BUNDLE_DECL_VERSION = "1.0"
BUNDLE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
BUNDLE_RELPATH_INVALID_RE = re.compile(r"(^/|^\.\./|/\.\./|/\.\.$|^\.\.$)")

CATEGORIES = ("prompt", "template", "function", "schema", "snippet", "config")

CANONICAL_DIRS = {
    "lib", "libs", "utils", "util", "shared", "common",
    "components", "helpers", "helper",
    "templates", "template",
    "prompts", "prompt",
    "schemas", "schema",
    "snippets", "snippet",
    "configs", "config",
    "functions", "function",
    "types",
}

DIR_TO_CATEGORY = {
    "prompts": "prompt", "prompt": "prompt",
    "templates": "template", "template": "template",
    "lib": "function", "libs": "function",
    "utils": "function", "util": "function",
    "helpers": "function", "helper": "function",
    "functions": "function", "function": "function",
    "schemas": "schema", "schema": "schema", "types": "schema",
    "configs": "config", "config": "config",
    "snippets": "snippet", "snippet": "snippet",
    "shared": "snippet", "common": "snippet", "components": "snippet",
}

EXCLUDED_DIRS = {
    ".git", ".svn", ".hg", ".bzr",
    "node_modules",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox",
    "dist", "build", "target", "out",
    ".next", ".nuxt", ".cache", ".parcel-cache",
    ".venv", "venv", "env", ".env",
    ".recicla",
}

EXCLUDED_FILE_PATTERNS = (
    re.compile(r"\.lock$"),
    re.compile(r"\.min\.js$"),
    re.compile(r"\.min\.css$"),
    re.compile(r"\.map$"),
    re.compile(r"\.pyc$"), re.compile(r"\.pyo$"),
    re.compile(r"\.class$"),
    re.compile(r"\.o$"), re.compile(r"\.so$"),
    re.compile(r"\.dll$"), re.compile(r"\.exe$"),
    re.compile(r"^\.DS_Store$"),
)

EXTENSION_TO_LANG = {
    ".py": "python",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript", ".tsx": "typescript",
    ".rb": "ruby",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".swift": "swift",
    ".c": "c", ".h": "c",
    ".cpp": "cpp", ".cc": "cpp", ".hpp": "cpp",
    ".cs": "csharp",
    ".php": "php",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell",
    ".sql": "sql",
    ".md": "markdown", ".markdown": "markdown",
    ".txt": "text",
    ".json": "json",
    ".yaml": "yaml", ".yml": "yaml",
    ".toml": "toml",
    ".html": "html", ".htm": "html",
    ".css": "css", ".scss": "css", ".sass": "css",
    ".xml": "xml",
}

DEFAULT_MAX_SIZE = 51200  # 50 KB
BINARY_SCAN_BYTES = 8192

MARKER_RE = re.compile(r"^\s*[^\w\n]*\s*@recicla:(\w+)\s*(.*?)\s*$")
MARKER_PRESENCE = "@recicla:reusable"

STOPWORDS = {
    "the", "and", "or", "but", "this", "that", "a", "an", "is", "are",
    "was", "were", "in", "on", "at", "of", "for", "to", "with", "by",
    "from", "as", "be", "it", "its", "their", "they", "we", "our",
    "you", "your", "i", "if", "then", "else", "when", "where", "what",
    "how", "why", "which", "who", "whom", "whose",
    "not", "no", "do", "does", "did", "have", "has", "had",
    "will", "would", "should", "could", "may", "might", "can", "must",
}

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def now_iso() -> str:
    """ISO 8601 UTC timestamp."""
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def short_id(sha: str) -> str:
    return f"c-{sha[:8]}"


def slugify(text: str) -> str:
    """ASCII kebab-case slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "component"


def is_binary(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            chunk = f.read(BINARY_SCAN_BYTES)
        return b"\x00" in chunk
    except OSError:
        return True


def file_lang(path: Path) -> str:
    return EXTENSION_TO_LANG.get(path.suffix.lower(), "unknown")


def format_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def is_excluded_path(rel: Path) -> bool:
    parts = rel.parts
    for p in parts:
        if p in EXCLUDED_DIRS:
            return True
    name = rel.name
    for pat in EXCLUDED_FILE_PATTERNS:
        if pat.search(name):
            return True
    return False


def closest_canonical_dir(rel: Path) -> Optional[str]:
    """Return the closest canonical-dir ancestor name, or None."""
    parents = rel.parts[:-1]
    for p in reversed(parents):
        if p in CANONICAL_DIRS:
            return p
    return None


def category_from_dir(rel: Path) -> str:
    d = closest_canonical_dir(rel)
    if d is None:
        return "snippet"
    return DIR_TO_CATEGORY.get(d, "snippet")


# ---------------------------------------------------------------------------
# Header parsing
# ---------------------------------------------------------------------------

def parse_header(path: Path, max_lines: int = 50) -> tuple[bool, dict]:
    """Return (has_marker, metadata_dict). Reads up to max_lines."""
    has_marker = False
    meta: dict[str, Any] = {}
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                if MARKER_PRESENCE in line:
                    has_marker = True
                m = MARKER_RE.match(line)
                if m:
                    key, value = m.group(1), m.group(2).strip()
                    if key == "reusable":
                        has_marker = True
                    elif key == "tags":
                        meta["tags"] = [
                            t.strip() for t in value.split(",") if t.strip()
                        ]
                    elif key in ("name", "category", "description"):
                        meta[key] = value
    except OSError:
        pass
    return has_marker, meta


def first_meaningful_line(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
                # skip purely decorative comments
                if re.fullmatch(r"[#/<*\-=;]+\s*", stripped):
                    continue
                # skip recicla markers
                if "@recicla:" in stripped:
                    continue
                return stripped[:200]
    except OSError:
        pass
    return "(sem descrição)"


# ---------------------------------------------------------------------------
# Library and manifest IO
# ---------------------------------------------------------------------------

def ensure_library(library_path: Path) -> None:
    """Bootstrap empty library if not present."""
    library_path.mkdir(parents=True, exist_ok=True)
    components_dir = library_path / "components"
    components_dir.mkdir(exist_ok=True)
    for cat in CATEGORIES:
        # plural folder name
        plural = "schema" if cat == "schema" else f"{cat}s"
        # actually use category as-is + "s"
        plural = f"{cat}s"
        (components_dir / plural).mkdir(exist_ok=True)
    index_path = library_path / "index.json"
    if not index_path.exists():
        write_index(library_path, {
            "version": INDEX_SCHEMA_VERSION,
            "library_path": str(library_path.resolve()),
            "updated_at": now_iso(),
            "components": [],
            "bundles": [],
        })
    index_md_path = library_path / "INDEX.md"
    if not index_md_path.exists():
        render_index_md(library_path)


def read_index(library_path: Path) -> dict:
    p = library_path / "index.json"
    if not p.exists():
        return {
            "version": INDEX_SCHEMA_VERSION,
            "library_path": str(library_path.resolve()),
            "updated_at": now_iso(),
            "components": [],
            "bundles": [],
        }
    with p.open("r", encoding="utf-8") as f:
        idx = json.load(f)
    return _migrate_index(idx)


def _migrate_index(idx: dict) -> dict:
    """Read-time migration v1.0 → v1.1. Idempotent."""
    if "bundles" not in idx:
        idx["bundles"] = []
    if idx.get("version") in (None, "1.0"):
        idx["version"] = INDEX_SCHEMA_VERSION
    return idx


def write_index(library_path: Path, index: dict) -> None:
    index["updated_at"] = now_iso()
    index["library_path"] = str(library_path.resolve())
    index["version"] = INDEX_SCHEMA_VERSION
    # sort components by added_at ascending
    index["components"] = sorted(
        index["components"], key=lambda c: c.get("added_at", "")
    )
    # sort bundles by added_at ascending
    index["bundles"] = sorted(
        index.get("bundles", []), key=lambda b: b.get("added_at", "")
    )
    p = library_path / "index.json"
    with p.open("w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def manifest_path_for(workspace: Path) -> Path:
    return workspace / ".recicla" / "manifest.json"


def read_manifest(workspace: Path) -> dict:
    p = manifest_path_for(workspace)
    if not p.exists():
        return {
            "version": MANIFEST_SCHEMA_VERSION,
            "workspace_path": str(workspace.resolve()),
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "components": [],
            "bundles": [],
        }
    with p.open("r", encoding="utf-8") as f:
        m = json.load(f)
    return _migrate_manifest(m)


def _migrate_manifest(m: dict) -> dict:
    """Read-time migration v1.0 → v1.1. Idempotent."""
    if "bundles" not in m:
        m["bundles"] = []
    for c in m.get("components", []):
        if "via_bundle" not in c:
            c["via_bundle"] = None
    if m.get("version") in (None, "1.0"):
        m["version"] = MANIFEST_SCHEMA_VERSION
    return m


def write_manifest(workspace: Path, manifest: dict) -> None:
    manifest["updated_at"] = now_iso()
    manifest["workspace_path"] = str(workspace.resolve())
    manifest["version"] = MANIFEST_SCHEMA_VERSION
    manifest["components"] = sorted(
        manifest["components"], key=lambda c: c.get("timestamp", "")
    )
    manifest["bundles"] = sorted(
        manifest.get("bundles", []), key=lambda b: b.get("timestamp", "")
    )
    p = manifest_path_for(workspace)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")


# ---------------------------------------------------------------------------
# Bundle utilities (schema 1.1)
# ---------------------------------------------------------------------------

def bundle_dir_for(workspace: Path) -> Path:
    return workspace / BUNDLE_DIR_REL


def bundle_decl_path(workspace: Path, name: str) -> Path:
    return bundle_dir_for(workspace) / f"{name}.json"


def list_bundle_decls(workspace: Path) -> list[Path]:
    """List all *.json under .recicla/bundles/, deterministically sorted."""
    bdir = bundle_dir_for(workspace)
    if not bdir.is_dir():
        return []
    return sorted([p for p in bdir.iterdir() if p.is_file() and p.suffix == ".json"])


def read_bundle_decl(path: Path) -> dict:
    """Read a bundle declaration. Raises ValueError on JSON error."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_bundle_decl(decl: dict) -> list[str]:
    """Return list of validation errors. Empty list = valid."""
    errs: list[str] = []
    if not isinstance(decl, dict):
        return ["declaration must be a JSON object"]

    name = decl.get("name")
    if not isinstance(name, str) or not BUNDLE_NAME_RE.match(name):
        errs.append(
            "name must be a slug matching ^[a-z0-9][a-z0-9-]{0,63}$"
        )

    if "description" in decl and not isinstance(decl["description"], str):
        errs.append("description must be a string")

    tags = decl.get("tags", [])
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        errs.append("tags must be a list of strings")

    entrypoint = decl.get("entrypoint")
    if entrypoint is not None and not isinstance(entrypoint, str):
        errs.append("entrypoint must be a string or null")

    members = decl.get("members")
    if not isinstance(members, list) or len(members) == 0:
        errs.append("members must be a non-empty list")
        return errs

    seen_ws: set[str] = set()
    seen_bundle: set[str] = set()
    bundle_relpaths: list[str] = []
    for i, m in enumerate(members):
        if not isinstance(m, dict):
            errs.append(f"members[{i}] must be an object")
            continue
        ws = m.get("workspace_relpath")
        br = m.get("bundle_relpath")
        if not isinstance(ws, str) or not ws:
            errs.append(f"members[{i}].workspace_relpath must be a non-empty string")
        if not isinstance(br, str) or not br:
            errs.append(f"members[{i}].bundle_relpath must be a non-empty string")
        if isinstance(br, str):
            if BUNDLE_RELPATH_INVALID_RE.search(br):
                errs.append(
                    f"members[{i}].bundle_relpath '{br}' contains '..' or is absolute"
                )
            if br in seen_bundle:
                errs.append(f"duplicate bundle_relpath: {br}")
            seen_bundle.add(br)
            bundle_relpaths.append(br)
        if isinstance(ws, str):
            if ws in seen_ws:
                errs.append(f"duplicate workspace_relpath: {ws}")
            seen_ws.add(ws)
        if "role" in m and not isinstance(m["role"], str):
            errs.append(f"members[{i}].role must be a string")

    if isinstance(entrypoint, str) and entrypoint not in bundle_relpaths:
        errs.append(
            f"entrypoint '{entrypoint}' must match one of members[].bundle_relpath"
        )

    return errs


def compute_bundle_id(name: str, members_for_id: list[dict]) -> str:
    """Deterministic bundle ID.

    Canonical serialization:
        name + '|' + ','.join(sorted([
            f"{m['component_id']}:{m['bundle_relpath']}" for m in members
        ]))

    members_for_id is a list of dicts each with keys 'component_id' and
    'bundle_relpath'. Other keys are ignored.
    """
    parts = sorted(
        f"{m['component_id']}:{m['bundle_relpath']}" for m in members_for_id
    )
    canonical = name + "|" + ",".join(parts)
    return "b-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:8]


def find_bundle_in_index(
    library: Path,
    bundle_id: Optional[str] = None,
    name: Optional[str] = None,
    include_superseded: bool = False,
) -> Optional[dict]:
    """Look up a bundle by id or name. By default, returns only active
    (non-superseded) bundles. If both id and name are passed, id wins."""
    idx = read_index(library)
    bundles = idx.get("bundles", [])
    if bundle_id:
        for b in bundles:
            if b["bundle_id"] == bundle_id:
                if include_superseded or not b.get("superseded_by"):
                    return b
                return b  # explicit lookup by id returns it even if superseded
        return None
    if name:
        # Among bundles with same name, prefer the active (superseded_by null) one.
        active = [
            b for b in bundles
            if b["name"] == name and not b.get("superseded_by")
        ]
        if active:
            # in deterministic order, latest added wins (sorted by added_at asc)
            return active[-1]
        if include_superseded:
            same_name = [b for b in bundles if b["name"] == name]
            return same_name[-1] if same_name else None
        return None
    return None


def render_bundles_section_md(index: dict) -> list[str]:
    """Return INDEX.md lines for the Bundles section. Pure function."""
    bundles = [b for b in index.get("bundles", []) if not b.get("superseded_by")]
    components = {c["component_id"]: c for c in index.get("components", [])}
    lines: list[str] = []
    if not bundles:
        return lines

    lines.append("## Bundles")
    lines.append("")
    lines.append(
        "> Bundles são composições nomeadas de componentes que andam juntos."
    )
    lines.append("")
    lines.append("| ID | Name | Members | Tags | Entrypoint |")
    lines.append("|---|---|---|---|---|")
    for b in sorted(bundles, key=lambda x: x["name"]):
        tags = ", ".join(b.get("tags", []))
        ep = b.get("entrypoint") or "—"
        lines.append(
            f"| `{b['bundle_id']}` | {b['name']} | "
            f"{len(b['members'])} | {tags} | "
            f"{('`' + ep + '`') if ep != '—' else '—'} |"
        )
    lines.append("")

    for b in sorted(bundles, key=lambda x: x["name"]):
        lines.append(f"### `{b['bundle_id']}` — {b['name']}")
        lines.append("")
        desc = b.get("description") or ""
        lines.append(f"- **Description:** {desc}")
        tags = ", ".join(b.get("tags", [])) or "(none)"
        lines.append(f"- **Tags:** {tags}")
        ep = b.get("entrypoint") or "(none)"
        lines.append(
            f"- **Entrypoint:** {('`' + ep + '`') if ep != '(none)' else '(none)'}"
        )
        added = (b.get("added_at") or "")[:10]
        lines.append(f"- **Added:** {added}")
        lines.append(f"- **Members ({len(b['members'])}):**")
        lines.append("")
        lines.append("  | Component | Bundle path | Role |")
        lines.append("  |---|---|---|")
        for m in b["members"]:
            cid = m["component_id"]
            present = "" if cid in components else " ⚠ missing"
            role = m.get("role") or ""
            lines.append(
                f"  | `{cid}`{present} | `{m['bundle_relpath']}` | {role} |"
            )
        lines.append("")
        lines.append(
            f"- **Inject:** `python recicla.py bundle-inject "
            f"--id {b['bundle_id']} --target-root <path>`"
        )
        lines.append("")

    return lines


# ---------------------------------------------------------------------------
# INDEX.md rendering
# ---------------------------------------------------------------------------

def render_index_md(library_path: Path) -> int:
    """Regenerate INDEX.md from index.json. Returns count of components."""
    index = read_index(library_path)
    components = index["components"]
    bundles_active = [
        b for b in index.get("bundles", []) if not b.get("superseded_by")
    ]
    n = len(components)
    nb = len(bundles_active)

    lines: list[str] = []
    lines.append("# Component Library Index")
    lines.append("")
    lines.append(
        "> Generated by `recicla` — do not edit manually. Source of truth: "
        "`index.json`."
    )
    lines.append(f"> Updated: {index.get('updated_at', now_iso())}")
    lines.append(f"> Components: {n}")
    lines.append(f"> Bundles: {nb}")
    lines.append("")

    if n == 0 and nb == 0:
        lines.append("> Library is empty.")
        lines.append("")
    else:
        if n > 0:
            lines.append("## Quick lookup")
            lines.append("")
            lines.append("| ID | Name | Category | Tags | Path |")
            lines.append("|---|---|---|---|---|")
            for c in sorted(components, key=lambda x: x["name"]):
                tags = ", ".join(c.get("tags", []))
                lines.append(
                    f"| `{c['component_id']}` | {c['name']} | {c['category']} | "
                    f"{tags} | `{c['library_relpath']}` |"
                )
            lines.append("")

            lines.append("## Components by category")
            lines.append("")
            for cat in CATEGORIES:
                in_cat = sorted(
                    [c for c in components if c["category"] == cat],
                    key=lambda x: x["name"],
                )
                if not in_cat:
                    continue
                plural = f"{cat.capitalize()}s"
                lines.append(f"### {plural} ({len(in_cat)})")
                lines.append("")
                for c in in_cat:
                    lines.append(f"#### `{c['component_id']}` — {c['name']}")
                    lines.append(f"- **Path:** `{c['library_relpath']}`")
                    tags = ", ".join(c.get("tags", [])) or "(none)"
                    lines.append(f"- **Tags:** {tags}")
                    lines.append(f"- **Description:** {c.get('description', '')}")
                    lines.append(f"- **Language:** {c.get('language', 'unknown')}")
                    short_hash = c["sha256"][:12]
                    lines.append(f"- **Hash:** `sha256:{short_hash}...`")
                    lines.append(f"- **Size:** {format_size(c['size_bytes'])}")
                    added = c.get("added_at", "")[:10]
                    lines.append(f"- **Added:** {added}")
                    lines.append("")

        # Bundles section (after components, before protocol)
        lines.extend(render_bundles_section_md(index))

    lines.append("## Consultation protocol (for agents)")
    lines.append("")
    lines.append("To find a component matching a need:")
    lines.append("")
    lines.append(
        "1. Filter the **Quick lookup** table by `category` and/or `tags` "
        "matching the user's intent."
    )
    lines.append(
        "2. Read the matched components' descriptions in the section above."
    )
    lines.append(
        "3. To import: invoke `python <path-to-recicla>/scripts/recicla.py "
        "inject --id <ID> --library $RECICLA_LIBRARY --workspace . "
        "--target <relative-destination>`."
    )
    lines.append(
        "4. Never copy file contents from this index — always use `inject` to "
        "preserve manifest tracking and avoid drift."
    )
    lines.append(
        "5. For composed patterns (pipelines, multi-file architectures), "
        "filter the **Bundles** table above. Import via `bundle-inject` "
        "(not `inject`), passing `--target-root` to anchor the bundle's "
        "internal layout into the destination workspace."
    )
    lines.append("")

    out = "\n".join(lines)
    (library_path / "INDEX.md").write_text(out, encoding="utf-8")
    return n


# ---------------------------------------------------------------------------
# Walk
# ---------------------------------------------------------------------------

def walk_workspace(workspace: Path) -> Iterable[Path]:
    """Yield relative paths of files under workspace, skipping excluded dirs."""
    for root, dirs, files in os.walk(workspace):
        root_path = Path(root)
        # prune excluded dirs in place
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for fn in files:
            full = root_path / fn
            try:
                rel = full.relative_to(workspace)
            except ValueError:
                continue
            yield rel


# ---------------------------------------------------------------------------
# Output envelope
# ---------------------------------------------------------------------------

def envelope(command: str, ok: bool, data: Any, errors: list) -> dict:
    return {
        "command": command,
        "version": VERSION,
        "ok": ok,
        "data": data,
        "errors": errors,
    }


def emit(out: dict, json_mode: bool, human_render=None) -> None:
    if json_mode:
        print(json.dumps(out, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        if human_render is not None:
            human_render(out)
        else:
            print(json.dumps(out, indent=2, ensure_ascii=False, sort_keys=True))


# ---------------------------------------------------------------------------
# scan
# ---------------------------------------------------------------------------

def cmd_scan(args) -> int:
    workspace = Path(args.workspace).resolve()
    library = Path(args.library).resolve()
    max_size = args.max_size

    if not workspace.is_dir():
        print(f"Error: workspace not found: {workspace}", file=sys.stderr)
        return 1

    ensure_library(library)
    index = read_index(library)
    manifest = read_manifest(workspace)

    index_hashes = {c["sha256"]: c["component_id"] for c in index["components"]}
    manifest_hashes = {
        c["sha256_at_op"]: c["component_id"] for c in manifest["components"]
    }

    candidates = []
    skipped = []
    scanned = 0

    for rel in sorted(walk_workspace(workspace), key=lambda p: str(p)):
        scanned += 1
        if is_excluded_path(rel):
            continue  # silently — too many of these
        full = workspace / rel

        try:
            size = full.stat().st_size
        except OSError:
            continue

        if size == 0:
            skipped.append({
                "path": str(rel),
                "skip_reason": "empty_file",
            })
            continue

        if size > max_size:
            skipped.append({
                "path": str(rel),
                "skip_reason": "size_exceeded",
            })
            continue

        if is_binary(full):
            skipped.append({
                "path": str(rel),
                "skip_reason": "binary_file",
            })
            continue

        has_marker, meta = parse_header(full)
        in_canonical = closest_canonical_dir(rel) is not None

        if not (has_marker or in_canonical):
            # not eligible — skip silently to keep skipped[] focused
            continue

        sha = sha256_file(full)

        if sha in manifest_hashes:
            skipped.append({
                "path": str(rel),
                "skip_reason": "already_processed_in_workspace",
                "existing_component_id": manifest_hashes[sha],
            })
            continue

        if sha in index_hashes:
            skipped.append({
                "path": str(rel),
                "skip_reason": "duplicate_hash_in_library",
                "existing_component_id": index_hashes[sha],
            })
            continue

        # build inferred metadata
        inferred_name = meta.get("name") or slugify(rel.stem)
        inferred_category = meta.get("category") or category_from_dir(rel)
        if inferred_category not in CATEGORIES:
            inferred_category = "snippet"
        inferred_tags = sorted(meta.get("tags", []))
        inferred_description = (
            meta.get("description") or first_meaningful_line(full)
        )
        lang = file_lang(full)

        candidates.append({
            "path": str(rel),
            "absolute_path": str(full),
            "size_bytes": size,
            "category_inferred": inferred_category,
            "language_inferred": lang,
            "has_marker": has_marker,
            "in_canonical_dir": in_canonical,
            "metadata_from_header": {
                "name": inferred_name,
                "category": inferred_category,
                "tags": inferred_tags,
                "description": inferred_description,
            },
            "sha256": sha,
        })

    # --- Bundle declarations in workspace ---
    bundle_candidates: list[dict] = []
    for decl_path in list_bundle_decls(workspace):
        rel_decl = str(decl_path.relative_to(workspace)).replace(os.sep, "/")
        try:
            decl = read_bundle_decl(decl_path)
        except (OSError, json.JSONDecodeError) as e:
            bundle_candidates.append({
                "path": rel_decl,
                "name": decl_path.stem,
                "valid": False,
                "errors": [f"parse error: {type(e).__name__}: {e}"],
                "members_count": 0,
            })
            continue
        errs = validate_bundle_decl(decl)
        bundle_candidates.append({
            "path": rel_decl,
            "name": decl.get("name", decl_path.stem),
            "valid": len(errs) == 0,
            "errors": errs,
            "members_count": len(decl.get("members", [])),
        })

    data = {
        "workspace_path": str(workspace),
        "library_path": str(library),
        "scanned_files": scanned,
        "candidates": candidates,
        "skipped": skipped,
        "bundle_candidates": bundle_candidates,
    }
    out = envelope("scan", True, data, [])

    def human(o):
        d = o["data"]
        n_idx = len(index["components"])
        nb_idx = len([
            b for b in index.get("bundles", []) if not b.get("superseded_by")
        ])
        print(
            f"Library: {d['library_path']}  "
            f"({n_idx} components, {nb_idx} bundles indexed)"
        )
        print(f"Workspace: {d['workspace_path']}")
        print(f"Scanned: {d['scanned_files']} files\n")
        if d["candidates"]:
            print(f"Candidates ({len(d['candidates'])}):")
            for i, c in enumerate(d["candidates"], 1):
                marker = "yes" if c["has_marker"] else "no"
                print(
                    f"  [{i}] {c['path']:<50} "
                    f"{format_size(c['size_bytes']):>9}  "
                    f"{c['category_inferred']:<10} marker: {marker}"
                )
        else:
            print("Candidates: none.")
        print()
        if d["skipped"]:
            print(f"Skipped ({len(d['skipped'])}):")
            for s in d["skipped"]:
                tail = ""
                if s.get("existing_component_id"):
                    tail = f" ({s['existing_component_id']})"
                print(f"  - {s['path']:<50} {s['skip_reason']}{tail}")
            print()
        if d["bundle_candidates"]:
            print(f"Bundle declarations ({len(d['bundle_candidates'])}):")
            for b in d["bundle_candidates"]:
                tag = "✓" if b["valid"] else "✗"
                print(
                    f"  {tag} {b['name']:<30} {b['members_count']} members  "
                    f"{b['path']}"
                )
                if not b["valid"]:
                    for e in b["errors"][:3]:
                        print(f"      └─ {e}")
            print()
        print("Use 'recicla extract --component <path>' to extract a candidate.")
        if d["bundle_candidates"]:
            print("Use 'recicla bundle-extract --name <name>' to register a bundle.")

    emit(out, args.json, human)
    return 0


# ---------------------------------------------------------------------------
# extract
# ---------------------------------------------------------------------------

def _resolve_component_path(workspace: Path, comp: str) -> Path:
    p = Path(comp)
    if not p.is_absolute():
        p = workspace / p
    return p.resolve()


def _allocate_library_path(
    library: Path,
    category: str,
    name: str,
    ext: str,
    sha: str,
    index: dict,
) -> Path:
    """Pick a non-colliding path under library/components/<category>s/."""
    plural = f"{category}s"
    folder = library / "components" / plural
    folder.mkdir(parents=True, exist_ok=True)
    candidate = folder / f"{name}{ext}"
    if not candidate.exists():
        # also check name uniqueness in index
        existing_names = {c["name"] for c in index["components"]}
        if name in existing_names:
            candidate = folder / f"{name}-{sha[:8]}{ext}"
        return candidate
    # exists on disk → check if it's same content elsewhere
    candidate = folder / f"{name}-{sha[:8]}{ext}"
    return candidate


def cmd_extract(args) -> int:
    workspace = Path(args.workspace).resolve()
    library = Path(args.library).resolve()

    if not workspace.is_dir():
        print(f"Error: workspace not found: {workspace}", file=sys.stderr)
        return 1

    ensure_library(library)
    index = read_index(library)
    manifest = read_manifest(workspace)

    extracted = []
    skipped = []
    errors = []

    index_hashes = {c["sha256"]: c["component_id"] for c in index["components"]}
    manifest_hashes = {
        c["sha256_at_op"]: c["component_id"] for c in manifest["components"]
    }

    for comp in args.component:
        full = _resolve_component_path(workspace, comp)
        if not full.exists() or not full.is_file():
            skipped.append({
                "path": comp,
                "reason": "file_not_found",
            })
            continue

        try:
            rel = full.relative_to(workspace)
        except ValueError:
            skipped.append({
                "path": comp,
                "reason": "outside_workspace",
            })
            continue

        if is_excluded_path(rel) or is_binary(full):
            skipped.append({
                "path": str(rel),
                "reason": "not_eligible",
            })
            continue

        size = full.stat().st_size
        if size == 0 or size > (
            args.max_size if args.max_size else DEFAULT_MAX_SIZE
        ):
            skipped.append({
                "path": str(rel),
                "reason": "not_eligible",
            })
            continue

        sha = sha256_file(full)

        if sha in index_hashes:
            skipped.append({
                "path": str(rel),
                "reason": "duplicate_hash_in_library",
                "existing_component_id": index_hashes[sha],
            })
            continue

        if sha in manifest_hashes:
            skipped.append({
                "path": str(rel),
                "reason": "already_processed_in_workspace",
                "existing_component_id": manifest_hashes[sha],
            })
            continue

        has_marker, meta = parse_header(full)
        name = meta.get("name") or slugify(rel.stem)
        category = meta.get("category") or category_from_dir(rel)
        if category not in CATEGORIES:
            category = "snippet"
        tags = sorted(meta.get("tags", []))
        description = meta.get("description") or first_meaningful_line(full)
        lang = file_lang(full)

        ext = full.suffix
        target = _allocate_library_path(
            library, category, name, ext, sha, index
        )
        # adjust name if it was rewritten
        if target.stem != name:
            name = target.stem

        try:
            shutil.copyfile(full, target)
        except OSError as e:
            errors.append({
                "kind": "io_error",
                "path": str(rel),
                "details": str(e),
            })
            continue

        # verify post-copy hash
        if sha256_file(target) != sha:
            try:
                target.unlink()
            except OSError:
                pass
            errors.append({
                "kind": "post_copy_hash_mismatch",
                "path": str(rel),
            })
            continue

        cid = short_id(sha)
        library_relpath = str(target.relative_to(library)).replace(os.sep, "/")

        entry = {
            "added_at": now_iso(),
            "added_from_workspace": str(workspace),
            "category": category,
            "component_id": cid,
            "description": description,
            "language": lang,
            "library_relpath": library_relpath,
            "name": name,
            "sha256": sha,
            "size_bytes": size,
            "tags": tags,
        }
        index["components"].append(entry)
        index_hashes[sha] = cid

        manifest["components"].append({
            "component_id": cid,
            "direction": "extracted",
            "library_relpath": library_relpath,
            "sha256_at_op": sha,
            "timestamp": now_iso(),
            "via_bundle": None,
            "workspace_relpath": str(rel).replace(os.sep, "/"),
        })
        manifest_hashes[sha] = cid

        extracted.append({
            "component_id": cid,
            "library_relpath": library_relpath,
            "name": name,
            "workspace_relpath": str(rel).replace(os.sep, "/"),
        })

    if extracted:
        write_index(library, index)
        write_manifest(workspace, manifest)
        render_index_md(library)

    data = {
        "extracted": extracted,
        "skipped": skipped,
        "index_updated": bool(extracted),
        "manifest_updated": bool(extracted),
        "index_md_regenerated": bool(extracted),
    }
    ok = bool(extracted) or not args.component
    out = envelope("extract", ok, data, errors)

    def human(o):
        d = o["data"]
        ne = len(d["extracted"])
        ns = len(d["skipped"])
        print(f"Extracted {ne} components, skipped {ns}.")
        print()
        if ne:
            print("Extracted:")
            for e in d["extracted"]:
                print(
                    f"  ✓ {e['component_id']}  {e['name']:<24}  "
                    f"← {e['workspace_relpath']}"
                )
            print()
        if ns:
            print("Skipped:")
            for s in d["skipped"]:
                tail = ""
                if s.get("existing_component_id"):
                    tail = f" ({s['existing_component_id']})"
                print(f"  ✗ {s['path']:<50} reason: {s['reason']}{tail}")
            print()
        if ne:
            print("INDEX.md regenerated.")

    emit(out, args.json, human)
    if errors:
        return 3
    if not extracted and args.component:
        return 1
    return 0


# ---------------------------------------------------------------------------
# suggest
# ---------------------------------------------------------------------------

def _infer_workspace_tags(workspace: Path) -> set[str]:
    tags: set[str] = set()

    pkg = workspace / "package.json"
    if pkg.exists():
        try:
            with pkg.open("r", encoding="utf-8") as f:
                data = json.load(f)
            for key in ("dependencies", "devDependencies"):
                deps = data.get(key, {})
                for name in deps.keys():
                    base = name.split("/")[-1]
                    if 2 < len(base) < 25:
                        tags.add(base.lower())
        except (json.JSONDecodeError, OSError):
            pass

    pyproject = workspace / "pyproject.toml"
    if pyproject.exists():
        try:
            text = pyproject.read_text(encoding="utf-8")
            # poetry style and PEP 621 — simple regex extraction
            for m in re.finditer(
                r'^\s*([a-zA-Z0-9_\-]+)\s*=\s*["\']', text, re.MULTILINE
            ):
                name = m.group(1).lower()
                if 2 < len(name) < 25:
                    tags.add(name)
            for m in re.finditer(r'["\']([a-zA-Z0-9_\-]+)[<>=~!]', text):
                name = m.group(1).lower()
                if 2 < len(name) < 25:
                    tags.add(name)
        except OSError:
            pass

    cargo = workspace / "Cargo.toml"
    if cargo.exists():
        try:
            text = cargo.read_text(encoding="utf-8")
            in_deps = False
            for line in text.splitlines():
                ls = line.strip()
                if ls.startswith("["):
                    in_deps = "dependencies" in ls
                    continue
                if in_deps:
                    m = re.match(r'^\s*([a-zA-Z0-9_\-]+)\s*=', ls)
                    if m:
                        tags.add(m.group(1).lower())
        except OSError:
            pass

    gomod = workspace / "go.mod"
    if gomod.exists():
        try:
            text = gomod.read_text(encoding="utf-8")
            for m in re.finditer(r'^\s*require\s+([^\s]+)', text, re.MULTILINE):
                pkg_path = m.group(1)
                segment = pkg_path.split("/")[-1].lower()
                if 2 < len(segment) < 25:
                    tags.add(segment)
        except OSError:
            pass

    for fn in ("README.md", "ARCHITECTURE.md"):
        p = workspace / fn
        if p.exists():
            try:
                text = p.read_text(encoding="utf-8", errors="replace")[:2000]
                tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]{2,19}", text)
                for tok in tokens:
                    low = tok.lower()
                    if low in STOPWORDS:
                        continue
                    tags.add(low)
            except OSError:
                pass

    # detect top languages
    ext_count: dict[str, int] = {}
    for rel in walk_workspace(workspace):
        if is_excluded_path(rel):
            continue
        lang = EXTENSION_TO_LANG.get(rel.suffix.lower())
        if lang and lang != "unknown":
            ext_count[lang] = ext_count.get(lang, 0) + 1
    top_langs = sorted(ext_count.items(), key=lambda x: -x[1])[:3]
    for lang, _ in top_langs:
        tags.add(lang)

    # cap
    return set(list(tags)[:30])


def cmd_suggest(args) -> int:
    library = Path(args.library).resolve()
    workspace = Path(args.workspace).resolve() if args.workspace else None

    if not (library / "index.json").exists():
        print(f"Error: library has no index.json: {library}", file=sys.stderr)
        return 1

    index = read_index(library)
    manifest_ids: set[str] = set()
    if workspace and workspace.is_dir():
        m = read_manifest(workspace)
        manifest_ids = {c["component_id"] for c in m["components"]}

    auto = bool(args.auto)
    if auto:
        if not workspace:
            print("Error: --auto requires --workspace", file=sys.stderr)
            return 1
        query_tags = _infer_workspace_tags(workspace)
    elif args.tags:
        query_tags = set(t.strip().lower() for t in args.tags.split(",") if t.strip())
    else:
        print("Error: provide --tags or --auto", file=sys.stderr)
        return 1

    matches = []
    type_filter = (args.type or "all").lower()
    include_components = type_filter in ("all", "component")
    include_bundles = type_filter in ("all", "bundle")

    if include_components:
        for c in index["components"]:
            if args.language and c.get("language") != args.language:
                continue
            if args.category and c["category"] != args.category:
                continue
            ctags = set(t.lower() for t in c.get("tags", []))
            union = ctags | query_tags
            inter = ctags & query_tags
            if union:
                score = len(inter) / len(union)
            else:
                score = 0.0
            if not ctags and (args.language or args.category):
                score = max(score, 0.01)
            matches.append({
                "type": "component",
                "already_in_workspace": c["component_id"] in manifest_ids,
                "category": c["category"],
                "component_id": c["component_id"],
                "description": c.get("description", ""),
                "language": c.get("language", "unknown"),
                "library_relpath": c["library_relpath"],
                "name": c["name"],
                "score": round(score, 3),
                "tags": c.get("tags", []),
            })

    if include_bundles:
        manifest_bundle_ids: set[str] = set()
        if workspace and workspace.is_dir():
            m = read_manifest(workspace)
            manifest_bundle_ids = {b["bundle_id"] for b in m.get("bundles", [])}
        # category/language don't apply to bundles; if either is set,
        # bundles are filtered out unless --type bundle is explicit
        if args.category or args.language:
            if type_filter != "bundle":
                include_bundles = False

    if include_bundles:
        for b in index.get("bundles", []):
            if b.get("superseded_by"):
                continue
            btags = set(t.lower() for t in b.get("tags", []))
            roles = set(
                (m.get("role") or "").lower()
                for m in b["members"] if m.get("role")
            )
            searchable = btags | {r for r in roles if r}
            union = searchable | query_tags
            inter = searchable & query_tags
            score = (len(inter) / len(union)) if union else 0.0
            matches.append({
                "type": "bundle",
                "already_in_workspace": b["bundle_id"] in manifest_bundle_ids,
                "bundle_id": b["bundle_id"],
                "category": None,
                "description": b.get("description", ""),
                "language": None,
                "members_count": len(b["members"]),
                "name": b["name"],
                "score": round(score, 3),
                "tags": b.get("tags", []),
            })

    def _added_at_int_for_match(m: dict) -> int:
        if m["type"] == "component":
            return _added_at_for(index, m["component_id"])
        else:
            return _added_at_for_bundle(index, m["bundle_id"])

    matches.sort(
        key=lambda x: (-x["score"], -_added_at_int_for_match(x))
    )
    matches = matches[: args.top]

    data = {
        "library_path": str(library),
        "query": {
            "auto_inferred": auto,
            "category": args.category,
            "language": args.language,
            "tags": sorted(list(query_tags)),
            "type": type_filter,
        },
        "matches": matches,
    }
    out = envelope("suggest", True, data, [])

    def human(o):
        d = o["data"]
        q = d["query"]
        print(f"Library: {d['library_path']}")
        tags_disp = ", ".join(q["tags"]) or "(none)"
        lang = q.get("language") or "any"
        cat = q.get("category") or "any"
        print(
            f"Query: tags=[{tags_disp}], language={lang}, category={cat}, "
            f"type={q['type']} (auto-inferred: {q['auto_inferred']})\n"
        )
        if not d["matches"]:
            print("No matches.")
            return
        print(f"Top {len(d['matches'])} matches:")
        for i, m in enumerate(d["matches"], 1):
            mark = "  " if not m["already_in_workspace"] else " *"
            if m["type"] == "component":
                print(
                    f" [{i}]{mark}{m['component_id']}  {m['name']:<22}  "
                    f"score: {m['score']:<5}  ← component, {m['category']}, "
                    f"{m['language']}"
                )
                print(f"       Tags: {', '.join(m['tags']) or '(none)'}")
                print(f"       {m['description'][:80]}")
                print(f"       {m['library_relpath']}")
            else:
                print(
                    f" [{i}]{mark}{m['bundle_id']}  {m['name']:<22}  "
                    f"score: {m['score']:<5}  ← bundle, "
                    f"{m['members_count']} members"
                )
                print(f"       Tags: {', '.join(m['tags']) or '(none)'}")
                print(f"       {m['description'][:80]}")
            print()
        print(
            "Use 'recicla inject --id <ID> --target <path>' for components, or "
            "'recicla bundle-inject --id <ID> --target-root <path>' for bundles. "
            "( * = already in this workspace )"
        )

    emit(out, args.json, human)
    return 0


def _added_at_for(index: dict, cid: str) -> int:
    for c in index["components"]:
        if c["component_id"] == cid:
            return int(
                _dt.datetime.fromisoformat(
                    c["added_at"].replace("Z", "+00:00")
                ).timestamp()
            )
    return 0


def _added_at_for_bundle(index: dict, bid: str) -> int:
    for b in index.get("bundles", []):
        if b["bundle_id"] == bid:
            return int(
                _dt.datetime.fromisoformat(
                    b["added_at"].replace("Z", "+00:00")
                ).timestamp()
            )
    return 0


# ---------------------------------------------------------------------------
# inject
# ---------------------------------------------------------------------------

def cmd_inject(args) -> int:
    library = Path(args.library).resolve()
    workspace = Path(args.workspace).resolve()

    if not (library / "index.json").exists():
        print(f"Error: library has no index.json", file=sys.stderr)
        return 1
    if not workspace.is_dir():
        print(f"Error: workspace not found: {workspace}", file=sys.stderr)
        return 1
    if Path(args.target).is_absolute():
        print("Error: --target must be relative to workspace", file=sys.stderr)
        return 1

    index = read_index(library)
    components = index["components"]

    matched = None
    if args.id:
        for c in components:
            if c["component_id"] == args.id:
                matched = c
                break
    elif args.library_relpath:
        for c in components:
            if c["library_relpath"] == args.library_relpath:
                matched = c
                break
    else:
        print(
            "Error: provide --id or --library-relpath",
            file=sys.stderr,
        )
        return 1

    if matched is None:
        print(f"Error: component not found in library", file=sys.stderr)
        return 1

    src = library / matched["library_relpath"]
    if not src.exists():
        print(
            f"Error: library file missing: {matched['library_relpath']}",
            file=sys.stderr,
        )
        return 1

    src_hash = sha256_file(src)
    if src_hash != matched["sha256"]:
        print(
            f"Error: library hash drift on {matched['component_id']}. "
            "Run 'recicla audit'.",
            file=sys.stderr,
        )
        return 1

    target_full = (workspace / args.target).resolve()
    try:
        target_rel = target_full.relative_to(workspace)
    except ValueError:
        print("Error: target outside workspace", file=sys.stderr)
        return 1

    manifest = read_manifest(workspace)

    # idempotency
    for entry in manifest["components"]:
        if (
            entry["component_id"] == matched["component_id"]
            and entry["direction"] == "injected"
            and entry["workspace_relpath"] == str(target_rel).replace(os.sep, "/")
        ):
            data = {
                "component_id": matched["component_id"],
                "destination_workspace_path": str(target_full),
                "manifest_updated": False,
                "name": matched["name"],
                "source_library_path": str(src),
                "status": "already_injected",
            }
            out = envelope("inject", True, data, [])
            emit(out, args.json, lambda o: print(
                f"Status: already_injected. No changes."
            ))
            return 0

    status = "ok"
    if target_full.exists():
        existing_hash = sha256_file(target_full)
        if existing_hash == src_hash:
            status = "identical_file_at_destination"
        elif not args.force:
            data = {
                "component_id": matched["component_id"],
                "destination_workspace_path": str(target_full),
                "manifest_updated": False,
                "name": matched["name"],
                "source_library_path": str(src),
                "status": "conflict",
            }
            out = envelope("inject", False, data, [{
                "kind": "conflict",
                "details": (
                    f"existing_hash={existing_hash[:12]} "
                    f"component_hash={src_hash[:12]}"
                ),
            }])
            emit(out, args.json, lambda o: print(
                "Status: conflict. File exists with different content. "
                "Use --force to overwrite.\n"
                f"  Existing hash:  {existing_hash[:12]}...\n"
                f"  Component hash: {src_hash[:12]}..."
            ))
            return 2

    if status == "ok":
        target_full.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copyfile(src, target_full)
        except OSError as e:
            print(f"Error: I/O failure: {e}", file=sys.stderr)
            return 3
        if sha256_file(target_full) != src_hash:
            try:
                target_full.unlink()
            except OSError:
                pass
            print("Error: post-copy hash mismatch.", file=sys.stderr)
            return 3

    manifest["components"].append({
        "component_id": matched["component_id"],
        "direction": "injected",
        "library_relpath": matched["library_relpath"],
        "sha256_at_op": src_hash,
        "timestamp": now_iso(),
        "via_bundle": None,
        "workspace_relpath": str(target_rel).replace(os.sep, "/"),
    })
    write_manifest(workspace, manifest)

    data = {
        "component_id": matched["component_id"],
        "destination_workspace_path": str(target_full),
        "manifest_updated": True,
        "name": matched["name"],
        "source_library_path": str(src),
        "status": status,
    }
    out = envelope("inject", True, data, [])

    def human(o):
        d = o["data"]
        print(
            f"Injected {d['component_id']} ({d['name']}) → "
            f"{Path(d['destination_workspace_path']).relative_to(workspace)}"
        )
        print(f"Status: {d['status']}")
        print("Manifest updated.")

    emit(out, args.json, human)
    return 0


# ---------------------------------------------------------------------------
# audit
# ---------------------------------------------------------------------------

def cmd_audit(args) -> int:
    library = Path(args.library).resolve()
    workspace = Path(args.workspace).resolve() if args.workspace else None

    if not (library / "index.json").exists():
        print(f"Error: library has no index.json", file=sys.stderr)
        return 1

    index = read_index(library)
    findings = []

    # library checks
    seen_hashes: dict[str, str] = {}
    for c in index["components"]:
        full = library / c["library_relpath"]
        if not full.exists():
            findings.append({
                "component_id": c["component_id"],
                "details": f"index.json references missing file at {c['library_relpath']}",
                "kind": "library_file_missing",
                "severity": "error",
            })
            continue
        actual = sha256_file(full)
        if actual != c["sha256"]:
            findings.append({
                "component_id": c["component_id"],
                "details": (
                    f"index claims sha256={c['sha256'][:12]}... "
                    f"but file has sha256={actual[:12]}..."
                ),
                "kind": "library_hash_drift",
                "severity": "error",
            })
        if c["sha256"] in seen_hashes and seen_hashes[c["sha256"]] != c["component_id"]:
            findings.append({
                "component_id": c["component_id"],
                "details": (
                    f"duplicate sha256 between {c['component_id']} "
                    f"and {seen_hashes[c['sha256']]}"
                ),
                "kind": "library_duplicate_hash",
                "severity": "error",
            })
        seen_hashes[c["sha256"]] = c["component_id"]

    # index.md staleness
    idx_md = library / "INDEX.md"
    idx_json = library / "index.json"
    if idx_md.exists() and idx_json.exists():
        if idx_md.stat().st_mtime < idx_json.stat().st_mtime:
            findings.append({
                "component_id": None,
                "details": "INDEX.md older than index.json. Run render-index.",
                "kind": "index_md_stale",
                "severity": "info",
            })

    # --- Bundle checks (library) ---
    cid_set = {c["component_id"] for c in index["components"]}
    for b in index.get("bundles", []):
        # Skip superseded bundles for member integrity warnings (history is
        # immutable; we only require ACTIVE bundles to be injectable).
        if b.get("superseded_by"):
            continue
        for m in b["members"]:
            if m["component_id"] not in cid_set:
                findings.append({
                    "component_id": m["component_id"],
                    "bundle_id": b["bundle_id"],
                    "details": (
                        f"bundle '{b['name']}' references component "
                        f"{m['component_id']} which is missing from index"
                    ),
                    "kind": "bundle_member_missing",
                    "severity": "error",
                })

    # workspace checks
    if workspace and workspace.is_dir():
        mp = manifest_path_for(workspace)
        if mp.exists():
            manifest = read_manifest(workspace)
            cid_in_index = {c["component_id"] for c in index["components"]}
            for entry in manifest["components"]:
                wsfull = workspace / entry["workspace_relpath"]
                if not wsfull.exists():
                    findings.append({
                        "component_id": entry["component_id"],
                        "details": (
                            f"workspace path {entry['workspace_relpath']} missing"
                        ),
                        "kind": "manifest_orphan",
                        "severity": "warn",
                    })
                    continue
                cur_hash = sha256_file(wsfull)
                if cur_hash != entry["sha256_at_op"]:
                    findings.append({
                        "component_id": entry["component_id"],
                        "details": (
                            f"workspace file modified since "
                            f"{entry['direction']} "
                            f"(was {entry['sha256_at_op'][:12]}, "
                            f"now {cur_hash[:12]})"
                        ),
                        "kind": "workspace_hash_drift",
                        "severity": "warn",
                    })
                if (
                    entry["direction"] == "injected"
                    and entry["component_id"] not in cid_in_index
                ):
                    findings.append({
                        "component_id": entry["component_id"],
                        "details": "injected component no longer in library",
                        "kind": "injected_component_removed_from_library",
                        "severity": "warn",
                    })

            # Local bundle declarations vs library
            bundle_id_in_index = {b["bundle_id"] for b in index.get("bundles", [])}
            for decl_path in list_bundle_decls(workspace):
                try:
                    decl = read_bundle_decl(decl_path)
                except (OSError, json.JSONDecodeError):
                    continue
                if validate_bundle_decl(decl):
                    continue
                # Resolve members against current workspace state
                members_for_id = []
                resolvable = True
                for m in decl["members"]:
                    ws_full = workspace / m["workspace_relpath"]
                    if not ws_full.is_file():
                        resolvable = False
                        break
                    sha = sha256_file(ws_full)
                    matched = next(
                        (c for c in index["components"] if c["sha256"] == sha),
                        None,
                    )
                    if not matched:
                        resolvable = False
                        break
                    members_for_id.append({
                        "component_id": matched["component_id"],
                        "bundle_relpath": m["bundle_relpath"],
                    })
                if not resolvable:
                    continue
                computed_id = compute_bundle_id(decl["name"], members_for_id)
                if computed_id not in bundle_id_in_index:
                    findings.append({
                        "component_id": None,
                        "bundle_id": computed_id,
                        "details": (
                            f"local declaration '{decl['name']}' would compute "
                            f"bundle_id {computed_id}, which is not registered. "
                            f"Run 'recicla bundle-extract --name {decl['name']}'"
                        ),
                        "kind": "bundle_definition_drift",
                        "severity": "warn",
                    })

            # Injected bundle entries vs library
            for b_entry in manifest.get("bundles", []):
                if b_entry["direction"] != "injected":
                    continue
                lib_b = next(
                    (b for b in index.get("bundles", [])
                     if b["bundle_id"] == b_entry["bundle_id"]),
                    None,
                )
                if lib_b is None:
                    findings.append({
                        "component_id": None,
                        "bundle_id": b_entry["bundle_id"],
                        "details": (
                            f"injected bundle '{b_entry['name']}' no longer "
                            f"in library"
                        ),
                        "kind": "injected_bundle_removed_from_library",
                        "severity": "warn",
                    })

    summary = {"info": 0, "warn": 0, "error": 0}
    for f in findings:
        summary[f["severity"]] += 1

    data = {
        "findings": findings,
        "library_path": str(library),
        "summary": summary,
        "workspace_path": str(workspace) if workspace else None,
    }
    out = envelope("audit", True, data, [])

    def human(o):
        d = o["data"]
        s = d["summary"]
        print("Audit summary:")
        print(f"  Library:    {d['library_path']}")
        if d["workspace_path"]:
            print(f"  Workspace:  {d['workspace_path']}")
        print()
        print(f"  ℹ INFO:  {s['info']}")
        print(f"  ⚠ WARN:  {s['warn']}")
        print(f"  ✗ ERROR: {s['error']}")
        print()
        if not d["findings"]:
            print("All clean.")
            return
        print("Findings:")
        for f in d["findings"]:
            tag = {"info": "INFO ", "warn": "WARN ", "error": "ERROR"}[f["severity"]]
            cid = f.get("component_id") or "-"
            print(f"\n[{tag}] {f['kind']}  ({cid})")
            print(f"  {f['details']}")

    emit(out, args.json, human)

    if summary["error"] > 0:
        return 2
    if summary["warn"] > 0:
        return 1
    return 0


# ---------------------------------------------------------------------------
# render-index
# ---------------------------------------------------------------------------

def cmd_render_index(args) -> int:
    library = Path(args.library).resolve()
    if not (library / "index.json").exists():
        print(f"Error: library has no index.json", file=sys.stderr)
        return 1
    n = render_index_md(library)
    index = read_index(library)
    cats = sorted(
        {c["category"] for c in index["components"]},
        key=lambda c: CATEGORIES.index(c) if c in CATEGORIES else 999,
    )
    data = {
        "categories_with_components": cats,
        "components_rendered": n,
        "index_md_path": str(library / "INDEX.md"),
        "library_path": str(library),
    }
    out = envelope("render-index", True, data, [])

    def human(o):
        d = o["data"]
        print(
            f"INDEX.md regenerated. {d['components_rendered']} components "
            f"rendered across {len(d['categories_with_components'])} categories."
        )

    emit(out, args.json, human)
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _resolve_library_default() -> Optional[str]:
    val = os.environ.get("RECICLA_LIBRARY")
    if val:
        return val
    cfg = os.environ.get("RECICLA_CONFIG")
    if not cfg:
        cfg_dir = os.environ.get("XDG_CONFIG_HOME") or str(
            Path.home() / ".config"
        )
        cfg = str(Path(cfg_dir) / "recicla" / "config.json")
    p = Path(cfg)
    if p.exists():
        try:
            with p.open("r", encoding="utf-8") as f:
                return json.load(f).get("library_path")
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _resolve_max_size_default() -> int:
    v = os.environ.get("RECICLA_MAX_SIZE")
    if v:
        try:
            return int(v)
        except ValueError:
            pass
    return DEFAULT_MAX_SIZE


# ---------------------------------------------------------------------------
# bundle-init
# ---------------------------------------------------------------------------

def cmd_bundle_init(args) -> int:
    workspace = Path(args.workspace).resolve()
    if not workspace.is_dir():
        print(f"Error: workspace not found: {workspace}", file=sys.stderr)
        return 1
    name = args.name.strip()
    if not BUNDLE_NAME_RE.match(name):
        print(
            "Error: name must match ^[a-z0-9][a-z0-9-]{0,63}$",
            file=sys.stderr,
        )
        return 1

    members_csv = [m.strip() for m in args.members.split(",") if m.strip()]
    if not members_csv:
        print("Error: --members must list at least one path", file=sys.stderr)
        return 1

    # Validate each member exists, build template
    members_decl = []
    seen_ws = set()
    seen_basename = set()
    for ws_rel in members_csv:
        if Path(ws_rel).is_absolute():
            print(
                f"Error: member path must be relative to workspace: {ws_rel}",
                file=sys.stderr,
            )
            return 1
        ws_full = (workspace / ws_rel).resolve()
        try:
            ws_full.relative_to(workspace)
        except ValueError:
            print(
                f"Error: member path escapes workspace: {ws_rel}",
                file=sys.stderr,
            )
            return 1
        if not ws_full.is_file():
            print(f"Error: member not found: {ws_rel}", file=sys.stderr)
            return 1
        if ws_rel in seen_ws:
            print(f"Error: duplicate member: {ws_rel}", file=sys.stderr)
            return 1
        seen_ws.add(ws_rel)

        basename = Path(ws_rel).name
        bundle_relpath = basename
        if basename in seen_basename:
            # Disambiguate using parent dir
            parent = Path(ws_rel).parent.name or "x"
            bundle_relpath = f"{parent}/{basename}"
            i = 2
            while bundle_relpath in seen_basename:
                bundle_relpath = f"{parent}{i}/{basename}"
                i += 1
        seen_basename.add(bundle_relpath)

        members_decl.append({
            "workspace_relpath": ws_rel.replace(os.sep, "/"),
            "bundle_relpath": bundle_relpath,
            "role": "",
        })

    decl = {
        "version": BUNDLE_DECL_VERSION,
        "name": name,
        "description": args.description or "",
        "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()],
        "entrypoint": None,
        "members": members_decl,
    }

    decl_path = bundle_decl_path(workspace, name)
    if decl_path.exists() and not args.force:
        print(
            f"Error: declaration already exists: {decl_path}. "
            f"Use --force to overwrite.",
            file=sys.stderr,
        )
        return 2
    decl_path.parent.mkdir(parents=True, exist_ok=True)
    with decl_path.open("w", encoding="utf-8") as f:
        json.dump(decl, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    rel_decl = str(decl_path.relative_to(workspace)).replace(os.sep, "/")
    data = {
        "declaration_path": str(decl_path),
        "declaration_relpath": rel_decl,
        "decl": decl,
    }
    out = envelope("bundle-init", True, data, [])

    def human(o):
        d = o["data"]
        print(f"Created {d['declaration_relpath']}")
        print(
            f"Bundle '{d['decl']['name']}' template with "
            f"{len(d['decl']['members'])} members."
        )
        print(
            "Edit bundle_relpath/role/entrypoint as needed, then run "
            f"'recicla bundle-extract --name {d['decl']['name']}'."
        )

    emit(out, args.json, human)
    return 0


# ---------------------------------------------------------------------------
# bundle-extract
# ---------------------------------------------------------------------------

def cmd_bundle_extract(args) -> int:
    library = Path(args.library).resolve()
    workspace = Path(args.workspace).resolve()
    if not workspace.is_dir():
        print(f"Error: workspace not found: {workspace}", file=sys.stderr)
        return 1

    decl_path = bundle_decl_path(workspace, args.name)
    if not decl_path.exists():
        print(
            f"Error: declaration not found: {decl_path}. "
            f"Run 'recicla bundle-init' first.",
            file=sys.stderr,
        )
        return 1

    try:
        decl = read_bundle_decl(decl_path)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error: cannot read declaration: {e}", file=sys.stderr)
        return 1

    errs = validate_bundle_decl(decl)
    if errs:
        print("Error: invalid declaration:", file=sys.stderr)
        for er in errs:
            print(f"  - {er}", file=sys.stderr)
        return 1

    # Verify all member files exist in workspace
    for m in decl["members"]:
        ws_full = workspace / m["workspace_relpath"]
        if not ws_full.is_file():
            print(
                f"Error: member file missing in workspace: "
                f"{m['workspace_relpath']}",
                file=sys.stderr,
            )
            return 1

    ensure_library(library)
    index = read_index(library)
    index_by_hash = {c["sha256"]: c for c in index["components"]}

    # Resolve members → component_ids; auto-extract if requested
    resolved_members: list[dict] = []
    auto_extracted: list[dict] = []
    missing: list[dict] = []
    for m in decl["members"]:
        ws_full = workspace / m["workspace_relpath"]
        sha = sha256_file(ws_full)
        if sha in index_by_hash:
            comp = index_by_hash[sha]
            resolved_members.append({
                "component_id": comp["component_id"],
                "bundle_relpath": m["bundle_relpath"],
                "role": m.get("role", ""),
                "workspace_relpath": m["workspace_relpath"],
            })
        else:
            missing.append({
                "workspace_relpath": m["workspace_relpath"],
                "bundle_relpath": m["bundle_relpath"],
                "sha256": sha,
            })

    if missing and not args.extract_members:
        print(
            "Error: the following members are not yet in library. "
            "Extract them first or pass --extract-members:",
            file=sys.stderr,
        )
        for mm in missing:
            print(f"  - {mm['workspace_relpath']}", file=sys.stderr)
        return 1

    if missing and args.extract_members:
        # Run cmd_extract programmatically per missing member
        class _ExtractArgs:
            pass

        for mm in missing:
            ex_args = _ExtractArgs()
            ex_args.component = [mm["workspace_relpath"]]
            ex_args.workspace = str(workspace)
            ex_args.library = str(library)
            ex_args.max_size = args.max_size
            ex_args.json = True
            # Suppress human output by redirecting
            buf_stdout = sys.stdout
            try:
                sys.stdout = open(os.devnull, "w")
                rc = cmd_extract(ex_args)
            finally:
                sys.stdout.close()
                sys.stdout = buf_stdout
            if rc != 0:
                print(
                    f"Error: auto-extract failed for {mm['workspace_relpath']}",
                    file=sys.stderr,
                )
                return 1
            auto_extracted.append(mm["workspace_relpath"])

        # Re-resolve after extraction
        index = read_index(library)
        index_by_hash = {c["sha256"]: c for c in index["components"]}
        resolved_members = []
        for m in decl["members"]:
            ws_full = workspace / m["workspace_relpath"]
            sha = sha256_file(ws_full)
            if sha not in index_by_hash:
                print(
                    f"Error: post-extract resolve failed for "
                    f"{m['workspace_relpath']}",
                    file=sys.stderr,
                )
                return 1
            comp = index_by_hash[sha]
            resolved_members.append({
                "component_id": comp["component_id"],
                "bundle_relpath": m["bundle_relpath"],
                "role": m.get("role", ""),
                "workspace_relpath": m["workspace_relpath"],
            })

    members_for_id = [
        {
            "component_id": m["component_id"],
            "bundle_relpath": m["bundle_relpath"],
        }
        for m in resolved_members
    ]
    bundle_id = compute_bundle_id(decl["name"], members_for_id)

    # Idempotency: same bundle_id already in index
    existing_same_id = next(
        (b for b in index.get("bundles", []) if b["bundle_id"] == bundle_id),
        None,
    )
    if existing_same_id is not None:
        data = {
            "bundle_id": bundle_id,
            "name": decl["name"],
            "auto_extracted": auto_extracted,
            "members_count": len(resolved_members),
            "registered": False,
            "status": "already_registered",
            "superseded_id": None,
        }
        out = envelope("bundle-extract", True, data, [])
        emit(out, args.json, lambda o: print(
            f"Bundle {bundle_id} ({decl['name']}) already registered."
        ))
        return 0

    # Same name, different composition → mark previous as superseded
    superseded_id = None
    for b in index.get("bundles", []):
        if b["name"] == decl["name"] and not b.get("superseded_by"):
            b["superseded_by"] = bundle_id
            superseded_id = b["bundle_id"]
            # only one active bundle per name expected; keep loop simple

    # Register new bundle
    new_bundle = {
        "bundle_id": bundle_id,
        "name": decl["name"],
        "added_at": now_iso(),
        "added_from_workspace": str(workspace),
        "description": decl.get("description", ""),
        "tags": decl.get("tags", []),
        "entrypoint": decl.get("entrypoint"),
        "members": [
            {
                "component_id": m["component_id"],
                "bundle_relpath": m["bundle_relpath"],
                "role": m.get("role", ""),
            }
            for m in resolved_members
        ],
        "superseded_by": None,
    }
    index["bundles"].append(new_bundle)
    write_index(library, index)
    render_index_md(library)

    data = {
        "bundle_id": bundle_id,
        "name": decl["name"],
        "auto_extracted": auto_extracted,
        "members_count": len(resolved_members),
        "registered": True,
        "status": "registered",
        "superseded_id": superseded_id,
    }
    out = envelope("bundle-extract", True, data, [])

    def human(o):
        d = o["data"]
        if d["auto_extracted"]:
            print(f"Auto-extracted {len(d['auto_extracted'])} members:")
            for ae in d["auto_extracted"]:
                print(f"  - {ae}")
            print()
        print(
            f"Bundle {d['bundle_id']} ({d['name']}) registered with "
            f"{d['members_count']} members."
        )
        if d["superseded_id"]:
            print(f"Previous bundle {d['superseded_id']} marked as superseded.")
        print("INDEX.md regenerated.")

    emit(out, args.json, human)
    return 0


# ---------------------------------------------------------------------------
# bundle-inject
# ---------------------------------------------------------------------------

def cmd_bundle_inject(args) -> int:
    library = Path(args.library).resolve()
    workspace = Path(args.workspace).resolve()
    if not (library / "index.json").exists():
        print(f"Error: library has no index.json: {library}", file=sys.stderr)
        return 1
    if not workspace.is_dir():
        print(f"Error: workspace not found: {workspace}", file=sys.stderr)
        return 1

    target_root = (args.target_root or "").strip()
    if Path(target_root).is_absolute():
        print("Error: --target-root must be relative to workspace", file=sys.stderr)
        return 1

    # Parse --remap entries
    remap: dict[str, str] = {}
    for entry in (args.remap or []):
        if "=" not in entry:
            print(
                f"Error: --remap entry must be 'orig=new': {entry}",
                file=sys.stderr,
            )
            return 1
        k, v = entry.split("=", 1)
        k, v = k.strip(), v.strip()
        if not k or not v:
            print(f"Error: invalid --remap entry: {entry}", file=sys.stderr)
            return 1
        if BUNDLE_RELPATH_INVALID_RE.search(v) or Path(v).is_absolute():
            print(
                f"Error: --remap target must be a safe relative path: {v}",
                file=sys.stderr,
            )
            return 1
        remap[k] = v

    bundle = find_bundle_in_index(
        library,
        bundle_id=args.id,
        name=args.name,
        include_superseded=True,
    )
    if bundle is None:
        print("Error: bundle not found in library", file=sys.stderr)
        return 1
    if bundle.get("superseded_by") and not args.allow_superseded:
        print(
            f"Error: bundle {bundle['bundle_id']} is superseded by "
            f"{bundle['superseded_by']}. Use --allow-superseded to inject anyway.",
            file=sys.stderr,
        )
        return 1

    # Validate all referenced components exist & hashes match
    index = read_index(library)
    components_by_id = {c["component_id"]: c for c in index["components"]}
    plan: list[dict] = []
    for m in bundle["members"]:
        cid = m["component_id"]
        comp = components_by_id.get(cid)
        if comp is None:
            print(
                f"Error: bundle member {cid} missing from library index",
                file=sys.stderr,
            )
            return 1
        src = library / comp["library_relpath"]
        if not src.is_file():
            print(
                f"Error: library file missing: {comp['library_relpath']}",
                file=sys.stderr,
            )
            return 1
        actual = sha256_file(src)
        if actual != comp["sha256"]:
            print(
                f"Error: library hash drift on {cid}. Run 'recicla audit'.",
                file=sys.stderr,
            )
            return 1

        bundle_relpath = m["bundle_relpath"]
        eff_relpath = remap.get(bundle_relpath, bundle_relpath)
        # Compose final destination
        if target_root:
            dest_rel = (Path(target_root) / eff_relpath).as_posix()
        else:
            dest_rel = eff_relpath
        dest_full = (workspace / dest_rel).resolve()
        try:
            dest_full.relative_to(workspace)
        except ValueError:
            print(
                f"Error: destination escapes workspace: {dest_rel}",
                file=sys.stderr,
            )
            return 1
        plan.append({
            "component_id": cid,
            "library_relpath": comp["library_relpath"],
            "bundle_relpath": bundle_relpath,
            "dest_rel": dest_rel,
            "dest_full": dest_full,
            "src_hash": comp["sha256"],
            "src": src,
        })

    # Path collision among the plan itself
    seen: dict[str, str] = {}
    for p in plan:
        if p["dest_rel"] in seen:
            print(
                f"Error: bundle_path_collision at {p['dest_rel']} "
                f"(members {seen[p['dest_rel']]} and {p['bundle_relpath']})",
                file=sys.stderr,
            )
            return 2
        seen[p["dest_rel"]] = p["bundle_relpath"]

    # Idempotency: bundle entry already in manifest with same target_root + remap
    manifest = read_manifest(workspace)
    norm_remap = dict(sorted(remap.items()))
    for be in manifest.get("bundles", []):
        if (
            be["bundle_id"] == bundle["bundle_id"]
            and be["direction"] == "injected"
            and be.get("target_root", "") == target_root
            and dict(sorted((be.get("remap") or {}).items())) == norm_remap
        ):
            data = {
                "bundle_id": bundle["bundle_id"],
                "name": bundle["name"],
                "injected": [],
                "members_count": len(plan),
                "skipped": [p["bundle_relpath"] for p in plan],
                "status": "already_injected",
                "target_root": target_root,
            }
            out = envelope("bundle-inject", True, data, [])
            emit(out, args.json, lambda o: print(
                f"Bundle {bundle['bundle_id']} ({bundle['name']}) already injected. "
                "No changes."
            ))
            return 0

    # Pre-check destination conflicts (without writing)
    conflicts: list[dict] = []
    for p in plan:
        if p["dest_full"].exists():
            existing_hash = sha256_file(p["dest_full"])
            if existing_hash != p["src_hash"]:
                conflicts.append({
                    "dest_rel": p["dest_rel"],
                    "existing_hash": existing_hash[:12],
                    "component_hash": p["src_hash"][:12],
                })

    if conflicts and not args.force:
        data = {
            "bundle_id": bundle["bundle_id"],
            "name": bundle["name"],
            "conflicts": conflicts,
            "status": "conflict",
        }
        out = envelope(
            "bundle-inject", False, data,
            [{"kind": "conflict", "details": f"{len(conflicts)} destination(s) differ"}],
        )

        def human(o):
            print(
                f"Conflict: {len(conflicts)} destination(s) exist with "
                f"different content. Use --force to overwrite."
            )
            for c in conflicts:
                print(
                    f"  {c['dest_rel']}: existing={c['existing_hash']} "
                    f"component={c['component_hash']}"
                )

        emit(out, args.json, human)
        return 2

    # Atomic copy: track written files; on failure, revert
    written: list[Path] = []
    pre_existing_data: dict[str, bytes] = {}
    try:
        for p in plan:
            if p["dest_full"].exists():
                # Save existing content for revert
                pre_existing_data[str(p["dest_full"])] = p["dest_full"].read_bytes()
            else:
                p["dest_full"].parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p["src"], p["dest_full"])
            if sha256_file(p["dest_full"]) != p["src_hash"]:
                raise OSError(f"post-copy hash mismatch on {p['dest_rel']}")
            written.append(p["dest_full"])
    except OSError as e:
        # Revert
        for w in written:
            try:
                if str(w) in pre_existing_data:
                    w.write_bytes(pre_existing_data[str(w)])
                else:
                    w.unlink(missing_ok=True)
            except OSError:
                pass
        print(f"Error: I/O failure during bundle-inject: {e}", file=sys.stderr)
        return 3

    # Update manifest
    timestamp = now_iso()
    for p in plan:
        manifest["components"].append({
            "component_id": p["component_id"],
            "direction": "injected",
            "library_relpath": p["library_relpath"],
            "sha256_at_op": p["src_hash"],
            "timestamp": timestamp,
            "via_bundle": bundle["bundle_id"],
            "workspace_relpath": p["dest_rel"],
        })
    manifest["bundles"].append({
        "bundle_id": bundle["bundle_id"],
        "name": bundle["name"],
        "direction": "injected",
        "members_count": len(plan),
        "remap": norm_remap,
        "target_root": target_root,
        "timestamp": timestamp,
    })
    write_manifest(workspace, manifest)

    data = {
        "bundle_id": bundle["bundle_id"],
        "name": bundle["name"],
        "injected": [
            {
                "component_id": p["component_id"],
                "bundle_relpath": p["bundle_relpath"],
                "destination_workspace_relpath": p["dest_rel"],
            }
            for p in plan
        ],
        "members_count": len(plan),
        "status": "ok" if not conflicts else "ok_overwritten",
        "target_root": target_root,
    }
    out = envelope("bundle-inject", True, data, [])

    def human(o):
        d = o["data"]
        print(
            f"Injecting bundle {d['bundle_id']} ({d['name']}) into "
            f"{workspace}..."
        )
        for inj in d["injected"]:
            print(
                f"  → {inj['destination_workspace_relpath']}  "
                f"(from {inj['component_id']})"
            )
        print(f"\n{d['members_count']} members injected. Manifest updated.")

    emit(out, args.json, human)
    return 0


def build_parser() -> argparse.ArgumentParser:
    lib_default = _resolve_library_default()
    max_default = _resolve_max_size_default()

    p = argparse.ArgumentParser(
        prog="recicla",
        description=(
            "Reciclagem determinística de componentes entre projetos. "
            "Veja SPEC.md para a especificação completa."
        ),
    )
    p.add_argument("--version", action="version", version=f"recicla {VERSION}")
    sub = p.add_subparsers(dest="command", required=True)

    # scan
    sp = sub.add_parser("scan", help="List candidates for extraction.")
    sp.add_argument("--workspace", default=".", help="Workspace path.")
    sp.add_argument(
        "--library", default=lib_default,
        help="Library path. Default: $RECICLA_LIBRARY.",
    )
    sp.add_argument(
        "--max-size", type=int, default=max_default,
        help=f"Max file size in bytes. Default: {max_default}.",
    )
    sp.add_argument("--json", action="store_true", help="JSON output.")

    # extract
    sp = sub.add_parser("extract", help="Move component(s) to library.")
    sp.add_argument(
        "--component", action="append", required=True,
        help="Component path (relative or absolute). Repeatable.",
    )
    sp.add_argument("--workspace", default=".", help="Workspace path.")
    sp.add_argument("--library", default=lib_default, help="Library path.")
    sp.add_argument("--max-size", type=int, default=max_default)
    sp.add_argument("--json", action="store_true")

    # suggest
    sp = sub.add_parser("suggest", help="List components matching needs.")
    sp.add_argument("--library", default=lib_default, help="Library path.")
    sp.add_argument(
        "--workspace", default=".",
        help="Workspace (for --auto and already_in_workspace marks).",
    )
    grp = sp.add_mutually_exclusive_group(required=True)
    grp.add_argument("--tags", help="CSV of tags.")
    grp.add_argument("--auto", action="store_true", help="Infer tags from workspace.")
    sp.add_argument("--language", default=None)
    sp.add_argument("--category", default=None, choices=list(CATEGORIES))
    sp.add_argument(
        "--type", default="all", choices=["all", "component", "bundle"],
        help="Filter results by entity type. Default: all.",
    )
    sp.add_argument("--top", type=int, default=10)
    sp.add_argument("--json", action="store_true")

    # inject
    sp = sub.add_parser("inject", help="Copy component to workspace.")
    grp = sp.add_mutually_exclusive_group(required=True)
    grp.add_argument("--id", help="Component ID.")
    grp.add_argument("--library-relpath", help="Library relative path.")
    sp.add_argument("--library", default=lib_default, help="Library path.")
    sp.add_argument("--workspace", default=".", help="Workspace path.")
    sp.add_argument(
        "--target", required=True, help="Destination relative to workspace.",
    )
    sp.add_argument(
        "--force", action="store_true", help="Overwrite on hash conflict.",
    )
    sp.add_argument("--json", action="store_true")

    # audit
    sp = sub.add_parser("audit", help="Verify integrity.")
    sp.add_argument("--workspace", default=None)
    sp.add_argument("--library", default=lib_default)
    sp.add_argument("--json", action="store_true")

    # render-index
    sp = sub.add_parser("render-index", help="Regenerate INDEX.md.")
    sp.add_argument("--library", default=lib_default)
    sp.add_argument("--json", action="store_true")

    # bundle-init
    sp = sub.add_parser(
        "bundle-init",
        help="Create a bundle declaration template in the workspace.",
    )
    sp.add_argument("--name", required=True, help="Bundle slug (a-z0-9-).")
    sp.add_argument(
        "--members", required=True,
        help="CSV of member paths (workspace-relative).",
    )
    sp.add_argument("--workspace", default=".", help="Workspace path.")
    sp.add_argument("--description", default="", help="Free text description.")
    sp.add_argument("--tags", default="", help="CSV of tags (optional).")
    sp.add_argument(
        "--force", action="store_true",
        help="Overwrite existing declaration.",
    )
    sp.add_argument("--json", action="store_true")

    # bundle-extract
    sp = sub.add_parser(
        "bundle-extract",
        help="Register a bundle in the library from local declaration.",
    )
    sp.add_argument("--name", required=True, help="Bundle name (slug).")
    sp.add_argument("--workspace", default=".", help="Workspace path.")
    sp.add_argument("--library", default=lib_default, help="Library path.")
    sp.add_argument(
        "--extract-members", action="store_true",
        help="Side-effect: extract members not yet in library before register.",
    )
    sp.add_argument("--max-size", type=int, default=max_default)
    sp.add_argument("--json", action="store_true")

    # bundle-inject
    sp = sub.add_parser(
        "bundle-inject",
        help="Materialize all members of a bundle into the workspace.",
    )
    grp = sp.add_mutually_exclusive_group(required=True)
    grp.add_argument("--id", help="Bundle ID (b-XXXXXXXX).")
    grp.add_argument("--name", help="Bundle name (slug).")
    sp.add_argument("--library", default=lib_default, help="Library path.")
    sp.add_argument("--workspace", default=".", help="Workspace path.")
    sp.add_argument(
        "--target-root", default="",
        help="Workspace-relative prefix for all members. Default: workspace root.",
    )
    sp.add_argument(
        "--remap", action="append", default=[],
        help="Remap a member: --remap <bundle_relpath>=<override_relpath>. Repeatable.",
    )
    sp.add_argument(
        "--force", action="store_true",
        help="Overwrite on hash conflict at destination.",
    )
    sp.add_argument(
        "--allow-superseded", action="store_true",
        help="Allow injecting a bundle marked superseded_by.",
    )
    sp.add_argument("--json", action="store_true")

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # bundle-init does not touch the library; skip the lib check for it.
    if args.command != "bundle-init":
        if not getattr(args, "library", None):
            print(
                "Error: --library not provided and $RECICLA_LIBRARY is not set.\n"
                "Set RECICLA_LIBRARY env var or pass --library.",
                file=sys.stderr,
            )
            return 1

    cmd = args.command
    try:
        if cmd == "scan":
            return cmd_scan(args)
        if cmd == "extract":
            return cmd_extract(args)
        if cmd == "suggest":
            return cmd_suggest(args)
        if cmd == "inject":
            return cmd_inject(args)
        if cmd == "audit":
            return cmd_audit(args)
        if cmd == "render-index":
            return cmd_render_index(args)
        if cmd == "bundle-init":
            return cmd_bundle_init(args)
        if cmd == "bundle-extract":
            return cmd_bundle_extract(args)
        if cmd == "bundle-inject":
            return cmd_bundle_inject(args)
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 99

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
