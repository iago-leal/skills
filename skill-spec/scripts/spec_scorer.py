#!/usr/bin/env python3
"""
spec_scorer.py — Avalia uma SPEC.md determinística de skill.

Aplica a rubrica de 5 dimensões (ver references/determinism_rubric.md):
  Determinismo     30 pts
  Reprodutibilidade 25 pts
  Completude       20 pts
  Testabilidade    15 pts
  Delimitação      10 pts
  Total           100 pts

Uso:
    python scripts/spec_scorer.py <caminho/SPEC.md>
    python scripts/spec_scorer.py <caminho/SPEC.md> --json

Sem dependências externas — stdlib pura.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

SECTION_RE = re.compile(r"^## (\d+)\.\s+(.+?)\s*$", re.MULTILINE)
CODE_BLOCK_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
CHECKBOX_RE = re.compile(r"^\s*-\s*\[\s?\]\s+.+$", re.MULTILINE)


REQUIRED_SECTIONS = {
    1: "Identidade",
    2: "Estrutura de Arquivos",
    3: "SKILL.md",
    4: "Scripts",
    5: "Dependências",
    6: "Armazenamento",
    7: "Padrões de Implementação",
    8: "Fluxo Interativo",
    9: "Critérios de Aceite",
    10: "O que",  # "O que esta Skill NÃO faz" — match pelo prefixo
    11: "Changelog",  # opcional mas contabilizado se ausente na Seção 11 via heurística
}

# Seção 11 (Changelog) é opcional em v1.0.0 — só obrigatória após primeiro UPGRADE.
OPTIONAL_SECTIONS = {11}


@dataclass
class Section:
    number: int
    title: str
    body: str
    is_na: bool = False
    na_justified: bool = False


@dataclass
class DimensionScore:
    name: str
    weight: int
    earned: float
    signals: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)


@dataclass
class SpecReport:
    spec_path: str
    total_score: float
    verdict: str
    dimensions: list[DimensionScore]
    missing_sections: list[int]
    critical_gaps: list[str]


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def parse_sections(text: str) -> dict[int, Section]:
    """Extrai seções numeradas (## N. Título) da SPEC."""
    matches = list(SECTION_RE.finditer(text))
    sections: dict[int, Section] = {}
    for i, m in enumerate(matches):
        number = int(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()

        body_lower = body.lower()
        # N/A explícito no corpo da seção
        is_na = bool(re.search(r"\bn/?a\b", body_lower[:200]))
        # Justificativa na mesma linha do N/A ou próximas 2 linhas
        na_justified = (
            is_na
            and len(body.strip().split("\n")[0].strip()) > 10  # mais que só "N/A"
        )

        sections[number] = Section(
            number=number,
            title=title,
            body=body,
            is_na=is_na,
            na_justified=na_justified,
        )
    return sections


def code_blocks(text: str, lang: str | None = None) -> list[str]:
    """Retorna corpos de code blocks, opcionalmente filtrando por linguagem."""
    out = []
    for m in CODE_BLOCK_RE.finditer(text):
        block_lang = m.group(1).strip().lower()
        if lang is None or block_lang == lang.lower():
            out.append(m.group(2))
    return out


# ---------------------------------------------------------------------------
# Heurísticas por dimensão
# ---------------------------------------------------------------------------


VAGUE_TERMS = [
    "geralmente",
    "normalmente",
    "aproximadamente",
    "se necessário",
    "mais ou menos",
    "cerca de",
    "talvez",
    "provavelmente",
    "deveria",
]

PLACEHOLDER_PATTERNS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bXXX\b",
    r"<preencher>",
    r"<inserir>",
    r"<\.\.\.>",
]


def score_determinism(sections: dict[int, Section], full_text: str) -> DimensionScore:
    d = DimensionScore(name="Determinismo", weight=30, earned=0)

    # Dependências pinadas (6 pts)
    deps_section = sections.get(5)
    if deps_section and not deps_section.is_na:
        pinned = len(re.findall(r"==\s*\d+\.\d+", deps_section.body))
        any_dep_row = len(re.findall(r"^\|\s*`[^`]+`\s*\|", deps_section.body, re.MULTILINE))
        if any_dep_row == 0:
            d.gaps.append("Seção 5 (Dependências) sem tabela de pacotes identificável")
        elif pinned >= any_dep_row * 0.8:
            d.earned += 6
            d.signals.append(f"{pinned}/{any_dep_row} dependências pinadas (==X.Y)")
        elif pinned > 0:
            d.earned += 3
            d.gaps.append(f"Apenas {pinned}/{any_dep_row} dependências pinadas com ==")
        else:
            d.gaps.append("Nenhuma dependência tem versão pinada (==X.Y.Z)")
    elif deps_section and deps_section.is_na:
        d.earned += 6  # N/A justificado em skill conversacional vale o ponto
        d.signals.append("Seção 5 marcada N/A (skill sem deps)")

    # JSON schemas em blocos de código (5 pts)
    json_blocks = code_blocks(full_text, "json")
    if len(json_blocks) >= 2:
        d.earned += 5
        d.signals.append(f"{len(json_blocks)} blocos JSON de schema/exemplo")
    elif len(json_blocks) == 1:
        d.earned += 3
        d.gaps.append("Apenas 1 bloco JSON — faltam exemplos de output por script")
    else:
        scripts_section = sections.get(4)
        if scripts_section and not scripts_section.is_na:
            d.gaps.append("Seção 4 declara scripts mas SPEC não tem blocos JSON")

    # CLI especificada (5 pts)
    scripts_section = sections.get(4)
    if scripts_section and not scripts_section.is_na:
        cli_blocks = re.findall(r"python scripts/\S+\.py", scripts_section.body)
        if len(cli_blocks) >= 1:
            d.earned += 5
            d.signals.append(f"{len(cli_blocks)} invocações de CLI documentadas")
        else:
            d.gaps.append("Seção 4 sem invocação `python scripts/X.py ...` literal")
    elif scripts_section and scripts_section.is_na:
        d.earned += 5  # N/A vale

    # Caminhos explícitos (4 pts)
    path_hits = len(re.findall(r"[~/][\w./-]+/", full_text))
    if path_hits >= 3:
        d.earned += 4
        d.signals.append(f"{path_hits} caminhos literais encontrados")
    elif path_hits >= 1:
        d.earned += 2
    else:
        d.gaps.append("Nenhum caminho literal de arquivo/diretório na SPEC")

    # Valores de config literais (6 pts) — procurar por números concretos em deps/config
    config_section = sections.get(6)
    has_numeric_config = False
    for sec_num in [4, 6, 7]:
        sec = sections.get(sec_num)
        if sec and not sec.is_na:
            nums = re.findall(r":\s*\d+[a-zA-Z]*", sec.body)
            if len(nums) >= 2:
                has_numeric_config = True
                break
    if has_numeric_config:
        d.earned += 6
        d.signals.append("Valores numéricos literais em config/scripts")
    else:
        d.gaps.append("Sem valores numéricos literais em config/scripts (possível ambiguidade)")

    # Linguagem vaga em seções técnicas (penalidade até −5)
    technical_body = "\n".join(
        sections[n].body for n in [4, 5, 7] if n in sections and not sections[n].is_na
    )
    vague_hits = []
    for term in VAGUE_TERMS:
        count = len(re.findall(rf"\b{term}\b", technical_body, re.IGNORECASE))
        if count > 0:
            vague_hits.append(f"'{term}' ({count}x)")
    if vague_hits:
        penalty = min(5, len(vague_hits) * 2)
        d.earned -= penalty
        d.gaps.append(f"Linguagem vaga em seções prescritivas: {', '.join(vague_hits)}")

    # Afirmações tipo "padrão X" sem âncora (penalidade até −5)
    unanchored = re.findall(r"padrão\s+(?:do|da|de)\s+\w+", full_text, re.IGNORECASE)
    if len(unanchored) > 2:
        d.earned -= 3
        d.gaps.append(f"{len(unanchored)} menções a 'padrão de X' — verifique se cita skill/arquivo")

    d.earned = max(0, min(d.weight, d.earned))
    return d


def score_reproducibility(sections: dict[int, Section], full_text: str) -> DimensionScore:
    d = DimensionScore(name="Reprodutibilidade", weight=25, earned=0)

    # Árvore ASCII de estrutura (5 pts)
    sec2 = sections.get(2)
    if sec2 and ("├──" in sec2.body or "└──" in sec2.body):
        d.earned += 5
        d.signals.append("Árvore ASCII na Seção 2 (Estrutura de Arquivos)")
    else:
        d.gaps.append("Seção 2 sem árvore ASCII (use ├── └── para desenhar)")

    # Frontmatter literal do SKILL.md (5 pts)
    sec3 = sections.get(3)
    if sec3:
        yaml_blocks = code_blocks(sec3.body, "yaml")
        literal_frontmatter = any(
            "name:" in b and "description:" in b for b in yaml_blocks
        )
        if literal_frontmatter:
            d.earned += 5
            d.signals.append("Frontmatter YAML literal na Seção 3")
        else:
            d.gaps.append("Seção 3 sem bloco YAML com name+description literal")

    # Corpo do SKILL.md com seções em ordem (4 pts)
    if sec3 and re.search(r"####?\s+Seção:", sec3.body):
        sub_sections = len(re.findall(r"####?\s+Seção:", sec3.body))
        if sub_sections >= 3:
            d.earned += 4
            d.signals.append(f"{sub_sections} sub-seções obrigatórias listadas em Seção 3")
        elif sub_sections >= 1:
            d.earned += 2
            d.gaps.append(f"Apenas {sub_sections} sub-seções em Seção 3 — especifique mais")
    else:
        d.gaps.append("Seção 3 não lista sub-seções obrigatórias do corpo do SKILL.md")

    # Deps de sistema com comando de instalação (4 pts)
    sec5 = sections.get(5)
    if sec5 and not sec5.is_na:
        install_cmds = re.findall(r"`(brew|apt|apt-get|yum|pip)\s+install[^`]*`", sec5.body)
        if install_cmds:
            d.earned += 4
            d.signals.append(f"{len(install_cmds)} comandos de instalação literais")
        else:
            # Se não há deps de sistema, não penaliza
            has_system_subsection = re.search(r"Sistema|system", sec5.body, re.IGNORECASE)
            if has_system_subsection:
                d.gaps.append("Seção 5 menciona deps de sistema sem comando de instalação")
            else:
                d.earned += 4  # não há deps de sistema, OK
    elif sec5 and sec5.is_na:
        d.earned += 4

    # Schemas literais de dados persistidos (4 pts)
    sec6 = sections.get(6)
    if sec6 and not sec6.is_na:
        has_schema = len(code_blocks(sec6.body, "json")) >= 1
        if has_schema:
            d.earned += 4
            d.signals.append("Schema literal de config/dados na Seção 6")
        else:
            d.gaps.append("Seção 6 descreve persistência sem schema JSON literal")
    elif sec6 and sec6.is_na:
        d.earned += 4

    # Fluxo interativo com mock literal (3 pts)
    sec8 = sections.get(8)
    if sec8 and not sec8.is_na:
        has_mock = bool(re.search(r"={5,}|\[1/\d+\]|\bEscolha\s*\[", sec8.body))
        if has_mock:
            d.earned += 3
            d.signals.append("Fluxo interativo com mock literal na Seção 8")
        else:
            d.gaps.append("Seção 8 descreve fluxo sem mock literal de prompts")
    elif sec8 and sec8.is_na:
        d.earned += 3

    # Penalidade: placeholders não resolvidos
    placeholder_hits = 0
    for p in PLACEHOLDER_PATTERNS:
        placeholder_hits += len(re.findall(p, full_text))
    if placeholder_hits > 0:
        d.earned -= min(5, placeholder_hits)
        d.gaps.append(f"{placeholder_hits} placeholders não resolvidos (TODO/XXX/<preencher>)")

    # Penalidade: marcadores [INFERIDO] pendentes
    inferidos = len(re.findall(r"\[INFERIDO[^\]]*\]", full_text))
    if inferidos > 0:
        d.earned -= min(5, inferidos)
        d.gaps.append(f"{inferidos} marcadores [INFERIDO] pendentes — confirmar com usuário")

    d.earned = max(0, min(d.weight, d.earned))
    return d


def score_completeness(sections: dict[int, Section], full_text: str) -> DimensionScore:
    d = DimensionScore(name="Completude", weight=20, earned=0)

    section_points = {
        1: 2,  # Identidade
        2: 2,  # Estrutura
        3: 3,  # SKILL.md
        4: 2,  # Scripts
        5: 2,  # Dependências
        6: 1,  # Armazenamento
        7: 2,  # Padrões
        8: 1,  # Fluxo Interativo
        9: 2,  # Critérios
        10: 2,  # NÃO faz
    }
    # Propósito (cabeçalho antes da Seção 1) — 1 pt
    has_proposito = bool(
        re.search(r"^##\s+Propósito\s*$", full_text, re.MULTILINE | re.IGNORECASE)
    )
    if has_proposito:
        d.earned += 1
        d.signals.append("Cabeçalho 'Propósito' presente")
    else:
        d.gaps.append("Cabeçalho '## Propósito' ausente antes da Seção 1")

    for num, pts in section_points.items():
        sec = sections.get(num)
        if sec is None:
            d.gaps.append(f"Seção {num} ({REQUIRED_SECTIONS.get(num, '?')}) ausente")
            continue
        # N/A sem justificativa penaliza
        if sec.is_na and not sec.na_justified:
            d.earned += pts * 0.5
            d.gaps.append(f"Seção {num} marcada N/A sem justificativa")
        else:
            d.earned += pts

    # Critérios de aceite devem ter ≥ 3 itens
    sec9 = sections.get(9)
    if sec9:
        checkboxes = len(CHECKBOX_RE.findall(sec9.body))
        if checkboxes < 3:
            d.earned -= 3
            d.gaps.append(f"Seção 9 tem apenas {checkboxes} critérios (< 3 mínimos)")

    d.earned = max(0, min(d.weight, d.earned))
    return d


def score_testability(sections: dict[int, Section], full_text: str) -> DimensionScore:
    d = DimensionScore(name="Testabilidade", weight=15, earned=0)

    # CLI executável em critério de aceite (4 pts)
    sec9 = sections.get(9)
    if sec9:
        cli_in_criteria = len(re.findall(r"`python scripts/[^`]+`", sec9.body))
        if cli_in_criteria >= 2:
            d.earned += 4
            d.signals.append(f"{cli_in_criteria} CLIs executáveis nos critérios")
        elif cli_in_criteria == 1:
            d.earned += 2
        else:
            # Se skill é conversacional (seção 4 N/A), não penaliza
            sec4 = sections.get(4)
            if sec4 and sec4.is_na:
                d.earned += 4
            else:
                d.gaps.append("Seção 9 sem CLI executável — critérios viram manuais")

    # Critérios binários (4 pts) — heurística: ausência de termos subjetivos
    subjective_terms = ["rápido", "bom", "útil", "adequado", "suficiente", "apropriado"]
    if sec9:
        subjective_hits = sum(
            len(re.findall(rf"\b{t}\b", sec9.body, re.IGNORECASE)) for t in subjective_terms
        )
        if subjective_hits == 0:
            d.earned += 4
            d.signals.append("Critérios sem linguagem subjetiva")
        elif subjective_hits <= 2:
            d.earned += 2
        else:
            d.gaps.append(f"{subjective_hits} termos subjetivos nos critérios de aceite")

    # Exemplos JSON concretos (3 pts)
    json_blocks = code_blocks(full_text, "json")
    # distinguir schema (só tipos) de exemplo (valores literais)
    with_literal_values = sum(
        1
        for b in json_blocks
        if re.search(r":\s*(\d+(\.\d+)?|\"[^\"]+\"|true|false)", b)
        and "<" not in b
    )
    if with_literal_values >= 2:
        d.earned += 3
        d.signals.append(f"{with_literal_values} exemplos JSON com valores literais")
    elif with_literal_values == 1:
        d.earned += 2
    else:
        d.gaps.append("Sem exemplos JSON com valores literais (só schemas)")

    # Exit codes documentados (2 pts)
    exit_code_hits = len(re.findall(r"exit\s*code", full_text, re.IGNORECASE))
    if exit_code_hits >= 2:
        d.earned += 2
        d.signals.append(f"{exit_code_hits} menções a exit codes")
    elif exit_code_hits == 1:
        d.earned += 1
    else:
        sec4 = sections.get(4)
        if not (sec4 and sec4.is_na):
            d.gaps.append("Comportamento de erro sem exit codes documentados")

    # Happy path mockado (2 pts) — presença de bloco bash com comando + output esperado
    bash_blocks = code_blocks(full_text, "bash") + code_blocks(full_text, "sh") + code_blocks(full_text, "")
    has_happy_path = any("python scripts/" in b or "#" in b for b in bash_blocks)
    if has_happy_path:
        d.earned += 2
        d.signals.append("Happy path executável presente")
    else:
        d.gaps.append("Sem exemplos executáveis de uso (happy path)")

    d.earned = max(0, min(d.weight, d.earned))
    return d


def score_delimitation(sections: dict[int, Section], full_text: str) -> DimensionScore:
    d = DimensionScore(name="Delimitação", weight=10, earned=0)

    sec10 = sections.get(10)
    if not sec10:
        d.gaps.append("Seção 10 ('O que NÃO faz') ausente")
        return d

    # ≥ 3 itens (3 pts)
    items = re.findall(r"^\s*-\s+(NÃO|NAO|Não)\b", sec10.body, re.MULTILINE)
    if len(items) >= 3:
        d.earned += 3
        d.signals.append(f"{len(items)} itens 'NÃO faz'")
    elif len(items) > 0:
        d.earned += 1
        d.gaps.append(f"Apenas {len(items)} itens 'NÃO faz' (< 3 mínimos)")
    else:
        d.gaps.append("Seção 10 sem itens começando com 'NÃO'")

    # Especificidade (3 pts) — cada item tem mais que 5 palavras
    bullet_lines = re.findall(r"^\s*-\s+(.+)$", sec10.body, re.MULTILINE)
    specific = [l for l in bullet_lines if len(l.split()) >= 6]
    if len(specific) >= 3:
        d.earned += 3
        d.signals.append(f"{len(specific)} itens específicos (≥ 6 palavras)")
    elif len(specific) >= 1:
        d.earned += 1

    # Delegação para skill nomeada (2 pts) — backtick + nome
    delegated = re.findall(r"`[a-z][a-z0-9-]+`", sec10.body)
    if len(delegated) >= 1:
        d.earned += 2
        d.signals.append(f"Delega para skills nomeadas: {', '.join(set(delegated))}")
    else:
        d.gaps.append("Seção 10 não delega explicitamente para skill nomeada")

    # Frontmatter do SKILL.md repete "NÃO ative" (2 pts)
    sec3 = sections.get(3)
    if sec3 and re.search(r"NÃO\s+(ative|active|ativar)", sec3.body, re.IGNORECASE):
        d.earned += 2
        d.signals.append("Frontmatter da Seção 3 repete 'NÃO ative'")
    else:
        d.gaps.append("Frontmatter do SKILL.md (Seção 3) não repete 'NÃO ative'")

    # Penalidade por itens genéricos
    generic_patterns = [
        r"não faz mágica",
        r"não substitui julgamento",
        r"não é perfeit",
    ]
    generic_hits = sum(len(re.findall(p, sec10.body, re.IGNORECASE)) for p in generic_patterns)
    if generic_hits > 0:
        d.earned -= 3
        d.gaps.append(f"{generic_hits} itens genéricos em Seção 10")

    d.earned = max(0, min(d.weight, d.earned))
    return d


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------


def verdict_for(score: float) -> str:
    if score >= 90:
        return "Exemplar — entregue. Considere usar como referência."
    if score >= 80:
        return "Pronta — entregue (revisar 1–2 gaps se possível)."
    if score >= 70:
        return "Quase lá — corrija gaps e re-avalie. Sem nova entrevista."
    if score >= 60:
        return "Incompleta — volte ao interview_protocol.md nas perguntas em aberto."
    return "Inviável — recomece a entrevista. SPEC atual dará origem a skill inconsistente."


def score_spec(spec_path: Path) -> SpecReport:
    text = spec_path.read_text(encoding="utf-8")
    sections = parse_sections(text)

    dims = [
        score_determinism(sections, text),
        score_reproducibility(sections, text),
        score_completeness(sections, text),
        score_testability(sections, text),
        score_delimitation(sections, text),
    ]
    total = round(sum(d.earned for d in dims), 1)

    missing = [
        n
        for n in REQUIRED_SECTIONS
        if n not in sections and n not in OPTIONAL_SECTIONS
    ]

    critical_gaps = []
    for d in dims:
        if d.earned < d.weight * 0.5:
            critical_gaps.append(
                f"{d.name}: {d.earned:.1f}/{d.weight} ({len(d.gaps)} gaps)"
            )

    return SpecReport(
        spec_path=str(spec_path),
        total_score=total,
        verdict=verdict_for(total),
        dimensions=dims,
        missing_sections=missing,
        critical_gaps=critical_gaps,
    )


# ---------------------------------------------------------------------------
# Apresentação
# ---------------------------------------------------------------------------


def format_human(report: SpecReport) -> str:
    out = []
    out.append("=" * 60)
    out.append(f"  spec_scorer — {report.spec_path}")
    out.append("=" * 60)
    out.append("")
    out.append(f"Score total: {report.total_score:.1f} / 100")
    out.append(f"Veredicto:   {report.verdict}")
    out.append("")
    out.append("Breakdown por dimensão:")
    for d in report.dimensions:
        bar = "█" * int(d.earned / d.weight * 20) if d.weight else ""
        bar = bar.ljust(20, "·")
        out.append(f"  {d.name:<18} {d.earned:>5.1f}/{d.weight:<3} [{bar}]")
    out.append("")

    if report.missing_sections:
        out.append("Seções obrigatórias ausentes:")
        for n in report.missing_sections:
            out.append(f"  - Seção {n}: {REQUIRED_SECTIONS.get(n, '?')}")
        out.append("")

    if report.critical_gaps:
        out.append("Dimensões críticas (< 50%):")
        for g in report.critical_gaps:
            out.append(f"  ⚠  {g}")
        out.append("")

    out.append("Gaps por dimensão:")
    for d in report.dimensions:
        if not d.gaps and not d.signals:
            continue
        out.append(f"  [{d.name}]")
        for s in d.signals:
            out.append(f"    ✓ {s}")
        for g in d.gaps:
            out.append(f"    ✗ {g}")
    out.append("")
    out.append("=" * 60)
    return "\n".join(out)


def format_json(report: SpecReport) -> str:
    data = {
        "spec_path": report.spec_path,
        "total_score": report.total_score,
        "verdict": report.verdict,
        "dimensions": [asdict(d) for d in report.dimensions],
        "missing_sections": report.missing_sections,
        "critical_gaps": report.critical_gaps,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Avalia uma SPEC.md de skill contra a rubrica de determinismo."
    )
    parser.add_argument("spec_path", type=Path, help="Caminho da SPEC.md")
    parser.add_argument("--json", action="store_true", help="Output JSON em stdout")
    args = parser.parse_args(argv)

    if not args.spec_path.exists():
        print(f"ERRO: arquivo não encontrado: {args.spec_path}", file=sys.stderr)
        return 1
    if not args.spec_path.is_file():
        print(f"ERRO: não é um arquivo: {args.spec_path}", file=sys.stderr)
        return 1

    report = score_spec(args.spec_path)

    if args.json:
        print(format_json(report))
    else:
        print(format_human(report))

    return 0 if report.total_score >= 60 else 2


if __name__ == "__main__":
    sys.exit(main())
