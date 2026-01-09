from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Dict, Iterable

from .reports.schema import RenderedReport


SECTION_KEYS = {
    "summary": "summary",
    "assets": "assets",
    "assignment_coverage": "assignment_coverage",
}


def _filter_sections(report: RenderedReport, include_sections: Iterable[str]) -> RenderedReport:
    allowed = {SECTION_KEYS.get(section, section) for section in include_sections}
    if not allowed:
        return report

    filtered_sections = [
        section
        for section in report.sections
        if any(key in allowed for key in section.payload.keys())
    ]
    return replace(report, sections=filtered_sections)


def write_rendered_reports(
    rendered: Dict[str, RenderedReport],
    output_prefix: Path,
    include_sections: Iterable[str],
) -> Dict[str, Path]:
    output_paths: Dict[str, Path] = {}
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    for format_name, report in rendered.items():
        filtered_report = _filter_sections(report, include_sections)
        output_path = output_prefix.with_name(f"{output_prefix.name}-{format_name}.json")
        output_path.write_text(
            json.dumps(asdict(filtered_report), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        output_paths[format_name] = output_path

    return output_paths


def write_raw_export(raw_export: Dict[str, object], output_prefix: Path) -> Path:
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_path = output_prefix.with_name(f"{output_prefix.name}-raw.json")
    output_path.write_text(json.dumps(raw_export, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path
