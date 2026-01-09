from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Dict, Iterable

from docx import Document

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
        output_path = _write_report_output(filtered_report, output_prefix, format_name)
        output_paths[format_name] = output_path

    return output_paths


def _write_report_output(report: RenderedReport, output_prefix: Path, format_name: str) -> Path:
    json_output_path = output_prefix.with_name(f"{output_prefix.name}-{format_name}.json")
    json_output_path.write_text(
        json.dumps(asdict(report), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if format_name == "word":
        docx_output_path = output_prefix.with_name(f"{output_prefix.name}-{format_name}.docx")
        _write_docx_report(report, docx_output_path)
        return docx_output_path
    return json_output_path


def _write_docx_report(report: RenderedReport, output_path: Path) -> None:
    document = Document()
    document.add_heading(f"{report.metadata.organization} Intune Report", level=0)
    document.add_paragraph(f"Audience: {report.audience}")
    document.add_paragraph(f"Generated at: {report.metadata.generated_at}")

    for section in report.sections:
        document.add_heading(section.title, level=1)
        if section.description:
            document.add_paragraph(section.description)
        payload_text = json.dumps(section.payload, indent=2, ensure_ascii=False)
        document.add_paragraph(payload_text)

    document.save(output_path)


def write_raw_export(raw_export: Dict[str, object], output_prefix: Path) -> Path:
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_path = output_prefix.with_name(f"{output_prefix.name}-raw.json")
    output_path.write_text(json.dumps(raw_export, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path
