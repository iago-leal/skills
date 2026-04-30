#!/usr/bin/env python3
"""
decompose.py — Estrutura proposta de decomposição em milestones + issues atômicas.

Comportamento:
- Aceita SOAP do mdcu (--input <path>) ou texto livre (--text "...").
- Não faz a decomposição em si — geração da proposta é responsabilidade do
  orquestrador (LLM). Este script:
    (a) lê o input e produz um esqueleto JSON com input_summary preenchido
        e seções vazias para o orquestrador completar; OU
    (b) com --validate-only, lê JSON via stdin e valida contra schema.

CLI:
  python scripts/decompose.py {--input <path> | --text <string>}
                              [--validate-only] [--json]

Exit codes:
  0  sucesso
  1  erro inesperado
  2  argumento inválido
  7  validação de schema falhou
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_TOP_KEYS = {
    "input_summary",
    "milestones_proposed",
    "open_questions",
    "tradeoffs",
}
REQUIRED_MILESTONE_KEYS = {
    "title",
    "scope",
    "release_criterion",
    "raci",
    "complexity_estimate",
    "issues",
}
REQUIRED_RACI_KEYS = {"responsible", "accountable", "consulted", "informed"}
REQUIRED_ISSUE_KEYS = {
    "title",
    "type",
    "hypothesis",
    "acceptance_criteria",
    "definition_of_done",
    "dependencies",
    "complexity",
}
ALLOWED_ISSUE_TYPES = {"feat", "bug", "chore", "spike", "incident", "tech-debt"}
ALLOWED_COMPLEXITY = {"S", "M", "L", "XL"}


def validate_proposal(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["raiz não é objeto JSON"]

    missing_top = REQUIRED_TOP_KEYS - set(data.keys())
    if missing_top:
        errors.append(f"chaves de topo ausentes: {sorted(missing_top)}")

    if not isinstance(data.get("input_summary"), str):
        errors.append("input_summary deve ser string")

    milestones = data.get("milestones_proposed")
    if not isinstance(milestones, list) or len(milestones) == 0:
        errors.append("milestones_proposed deve ser lista não-vazia")
    else:
        for i, m in enumerate(milestones):
            if not isinstance(m, dict):
                errors.append(f"milestones_proposed[{i}] não é objeto")
                continue
            missing = REQUIRED_MILESTONE_KEYS - set(m.keys())
            if missing:
                errors.append(
                    f"milestones_proposed[{i}] sem chaves: {sorted(missing)}"
                )
            raci = m.get("raci")
            if not isinstance(raci, dict):
                errors.append(f"milestones_proposed[{i}].raci não é objeto")
            else:
                missing_raci = REQUIRED_RACI_KEYS - set(raci.keys())
                if missing_raci:
                    errors.append(
                        f"milestones_proposed[{i}].raci sem chaves: "
                        f"{sorted(missing_raci)}"
                    )
            issues = m.get("issues")
            if not isinstance(issues, list) or len(issues) == 0:
                errors.append(
                    f"milestones_proposed[{i}].issues deve ser lista não-vazia"
                )
            else:
                for j, it in enumerate(issues):
                    if not isinstance(it, dict):
                        errors.append(
                            f"milestones_proposed[{i}].issues[{j}] não é objeto"
                        )
                        continue
                    missing_it = REQUIRED_ISSUE_KEYS - set(it.keys())
                    if missing_it:
                        errors.append(
                            f"milestones_proposed[{i}].issues[{j}] sem chaves: "
                            f"{sorted(missing_it)}"
                        )
                    if it.get("type") not in ALLOWED_ISSUE_TYPES:
                        errors.append(
                            f"milestones_proposed[{i}].issues[{j}].type "
                            f"deve estar em {sorted(ALLOWED_ISSUE_TYPES)}"
                        )
                    if it.get("complexity") not in ALLOWED_COMPLEXITY:
                        errors.append(
                            f"milestones_proposed[{i}].issues[{j}].complexity "
                            f"deve estar em {sorted(ALLOWED_COMPLEXITY)}"
                        )
                    for list_key in (
                        "acceptance_criteria",
                        "definition_of_done",
                        "dependencies",
                    ):
                        if not isinstance(it.get(list_key), list):
                            errors.append(
                                f"milestones_proposed[{i}].issues[{j}].{list_key} "
                                f"deve ser lista"
                            )

    if not isinstance(data.get("open_questions"), list):
        errors.append("open_questions deve ser lista")
    if not isinstance(data.get("tradeoffs"), list):
        errors.append("tradeoffs deve ser lista")

    return errors


def skeleton_from_input(summary: str) -> dict:
    return {
        "input_summary": summary,
        "milestones_proposed": [],
        "open_questions": [],
        "tradeoffs": [],
        "_instructions_for_orchestrator": (
            "Preencha milestones_proposed seguindo schema do SPEC §4.2. "
            "Cada issue precisa de hipótese, critério de aceite testável, "
            "definição de pronto, dependências, complexidade S/M/L/XL e "
            "archetype sugerido. Liste open_questions e tradeoffs explícitos. "
            "Após preencher, valide com: "
            "python scripts/decompose.py --validate-only --json < proposta.json"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estrutura proposta de decomposição em milestones + issues"
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--input", help="caminho do SOAP (do mdcu) ou markdown livre")
    g.add_argument("--text", help="texto livre como alternativa ao --input")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="lê JSON via stdin e valida contra schema",
    )
    parser.add_argument(
        "--json", action="store_true", help="força output JSON em stdout"
    )
    args = parser.parse_args()

    if args.validate_only:
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"Erro: stdin não é JSON válido: {e}\n")
            sys.exit(2)
        errors = validate_proposal(data)
        if errors:
            sys.stderr.write("Erro: input não conforma ao schema esperado:\n")
            for e in errors:
                sys.stderr.write(f"  - {e}\n")
            sys.exit(7)
        print(
            json.dumps(
                {"valid": True, "errors": []},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if not args.input and not args.text:
        sys.stderr.write(
            "Erro: argumento inválido — forneça --input <path> ou --text <string> "
            "(ou --validate-only com JSON via stdin)\n"
        )
        sys.exit(2)

    if args.input:
        path = Path(args.input)
        if not path.is_file():
            sys.stderr.write(f"Erro: argumento inválido — arquivo não existe: {path}\n")
            sys.exit(2)
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as e:
            sys.stderr.write(f"Erro lendo {path}: {e}\n")
            sys.exit(1)
        summary = content.strip().split("\n\n")[0][:500]
    else:
        summary = (args.text or "").strip()[:500]

    if not summary:
        sys.stderr.write("Erro: input vazio.\n")
        sys.exit(2)

    out = skeleton_from_input(summary)
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
