#!/usr/bin/env python3
"""
prompt_contract.py — Cria contrato de prompt versionado em prompts/.

Obriga, antes do merge:
  --task           descrição curta
  --model          ID literal de modelo (ex: claude-haiku-4-5-20251001)
  --input-schema   JSON Schema (string JSON ou caminho de arquivo)
  --output-schema  JSON Schema (string JSON ou caminho de arquivo)
  --fallback       descrição do caminho determinístico
  --budget-tokens  teto de tokens por chamada (int)

CLI:
  python scripts/prompt_contract.py --task <str> --model <str>
                                    --input-schema <json-or-path>
                                    --output-schema <json-or-path>
                                    --fallback <str>
                                    --budget-tokens <int>
                                    [--eval-cases <path>]
                                    [--json]

Exit codes:
  0  sucesso
  1  erro inesperado
  2  argumento inválido (faltou --fallback ou --budget-tokens; schema inválido)
  3  prompt com número duplicado (race)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path


def slugify(title: str, max_len: int = 50) -> str:
    norm = unicodedata.normalize("NFKD", title)
    ascii_only = "".join(c for c in norm if not unicodedata.combining(c))
    lowered = ascii_only.lower()
    safe = re.sub(r"[^a-z0-9\s-]", "", lowered)
    hyphen = re.sub(r"\s+", "-", safe).strip("-")
    collapsed = re.sub(r"-+", "-", hyphen)
    return collapsed[:max_len].rstrip("-") or "prompt"


def next_number(prompts_dir: Path) -> int:
    if not prompts_dir.exists():
        return 1
    pat = re.compile(r"^(\d{4})-")
    used: list[int] = []
    for p in prompts_dir.glob("*.md"):
        m = pat.match(p.name)
        if m:
            used.append(int(m.group(1)))
    return (max(used) + 1) if used else 1


def load_schema(value: str) -> object:
    candidate = Path(value)
    if candidate.is_file():
        text = candidate.read_text(encoding="utf-8")
    else:
        text = value
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        sys.stderr.write(
            f"Erro: argumento inválido — schema não é JSON válido: {e}\n"
        )
        sys.exit(2)


def build_prompt_md(
    number: int,
    task: str,
    version: str,
    model: str,
    budget_tokens: int,
    input_schema: object,
    output_schema: object,
    fallback: str,
    eval_cases_path: str | None,
) -> str:
    today = date.today().isoformat()
    has_eval = bool(eval_cases_path)
    fm = (
        "---\n"
        f"prompt: {number}\n"
        f"task: {task}\n"
        f"version: {version}\n"
        f"model: {model}\n"
        f"budget_tokens: {budget_tokens}\n"
        f"date: {today}\n"
        f"has_fallback: true\n"
        f"has_eval: {'true' if has_eval else 'false'}\n"
        "---\n\n"
    )
    body = (
        f"# Prompt-{number:04d}: {task}\n\n"
        f"## Versão\n{version} (criado em {today})\n\n"
        f"## Modelo Alvo\n`{model}`\n\n"
        f"## Input Schema\n```json\n"
        f"{json.dumps(input_schema, ensure_ascii=False, indent=2)}\n"
        f"```\n\n"
        f"## Output Schema\n```json\n"
        f"{json.dumps(output_schema, ensure_ascii=False, indent=2)}\n"
        f"```\n\n"
        f"## Eval Offline\n"
    )
    if has_eval:
        body += (
            f"- Casos: `{eval_cases_path}`\n"
            f"- Critério: pass/fail binário por caso (ver formato em "
            f"`references/ai_engineering.md`).\n"
            f"- Action: `.github/workflows/eval-{slugify(task)}.yml` (a configurar).\n\n"
        )
    else:
        body += (
            "- ⚠️ AUSENTE — adicione `evals/<task>/cases.jsonl` com mínimo 20 casos\n"
            "  e configure GitHub Action que rode em PR. Sem eval offline, o contrato\n"
            "  está incompleto. Veja `references/ai_engineering.md`.\n\n"
        )
    body += (
        f"## Fallback Determinístico\n{fallback}\n\n"
        f"## Budget de Tokens\n"
        f"- Teto por chamada: `{budget_tokens}` tokens\n"
        f"- Alarme: configurar para p95 de uso real exceder o teto por 7 dias.\n\n"
        f"## Telemetria (campos obrigatórios)\n"
        f"- `request_id` (UUID)\n"
        f"- `prompt_version` (SemVer string)\n"
        f"- `model` (string)\n"
        f"- `tokens_in` (int)\n"
        f"- `tokens_out` (int)\n"
        f"- `latency_ms` (int)\n"
        f"- `confidence` (float [0,1] ou null)\n"
        f"- `fallback_used` (bool)\n\n"
        f"## Prompt (system + user)\n"
        f"<!-- Preencher com o prompt literal versionado. Mudança aqui = bump de versão. -->\n"
    )
    return fm + body


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cria contrato de prompt versionado em prompts/"
    )
    parser.add_argument("--task", required=True)
    parser.add_argument("--model", required=True, help="ID literal do modelo")
    parser.add_argument("--input-schema", required=True, help="JSON ou path")
    parser.add_argument("--output-schema", required=True, help="JSON ou path")
    parser.add_argument("--fallback", required=True, help="caminho determinístico")
    parser.add_argument(
        "--budget-tokens",
        type=int,
        required=True,
        help="teto de tokens por chamada",
    )
    parser.add_argument(
        "--eval-cases", help="caminho para evals/<task>/cases.jsonl"
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.fallback or not args.fallback.strip():
        sys.stderr.write(
            "Erro: argumento inválido — --fallback é obrigatório.\n"
        )
        sys.exit(2)
    if args.budget_tokens <= 0:
        sys.stderr.write(
            "Erro: argumento inválido — --budget-tokens deve ser inteiro positivo.\n"
        )
        sys.exit(2)

    input_schema = load_schema(args.input_schema)
    output_schema = load_schema(args.output_schema)

    prompts_dir = Path("prompts")
    prompts_dir.mkdir(parents=True, exist_ok=True)

    number = next_number(prompts_dir)
    slug = slugify(args.task)
    filename = f"{number:04d}-{slug}.md"
    out_path = prompts_dir / filename

    if out_path.exists():
        sys.stderr.write(
            f"Erro: prompt {number:04d} já existe em {out_path}.\n"
        )
        sys.exit(3)

    version = "1.0.0"
    content = build_prompt_md(
        number=number,
        task=args.task,
        version=version,
        model=args.model,
        budget_tokens=args.budget_tokens,
        input_schema=input_schema,
        output_schema=output_schema,
        fallback=args.fallback,
        eval_cases_path=args.eval_cases,
    )
    out_path.write_text(content, encoding="utf-8")

    out = {
        "prompt_contract": {
            "number": number,
            "path": str(out_path),
            "task": args.task,
            "version": version,
            "model": args.model,
            "budget_tokens": args.budget_tokens,
            "has_fallback": True,
            "has_eval": bool(args.eval_cases),
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
