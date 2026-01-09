from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Dict, Iterable

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

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
    document.add_page_break()
    _add_table_of_contents(document)

    assets_payload = next(
        (section.payload.get("assets") for section in report.sections if "assets" in section.payload),
        None,
    )

    for section in report.sections:
        document.add_page_break()
        document.add_heading(section.title, level=1)
        if section.description:
            document.add_paragraph(section.description)
        for key, payload in section.payload.items():
            if key == "summary":
                _render_summary_section(document, payload, assets_payload)
            elif key == "assets":
                _render_assets_section(document, payload)
            elif key == "assignment_coverage":
                _render_assignment_coverage_section(document, payload)
            else:
                payload_text = json.dumps(payload, indent=2, ensure_ascii=False)
                document.add_paragraph(payload_text)

    document.save(output_path)


def _add_table_of_contents(document: Document) -> None:
    document.add_heading("Table of Contents", level=1)
    paragraph = document.add_paragraph()
    run = paragraph.add_run()
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), 'TOC \\o "1-3" \\h \\z \\u')
    run._r.append(field)


def _set_cell_shading(cell, color: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), color)
    tc_pr.append(shading)


def _render_summary_section(document: Document, payload: Dict[str, object], assets_payload: object) -> None:
    title = payload.get("title")
    if title:
        document.add_heading(str(title), level=2)
    highlights = payload.get("highlights", [])
    if highlights:
        document.add_paragraph("Highlights", style="List Bullet")
        for item in highlights:
            document.add_paragraph(str(item), style="List Bullet")

    metrics = payload.get("metrics", {})
    if metrics:
        document.add_paragraph("Key Metrics")
        table = document.add_table(rows=1, cols=2)
        table.style = "Light Grid"
        header_cells = table.rows[0].cells
        header_cells[0].text = "Metric"
        header_cells[1].text = "Value"
        _set_cell_shading(header_cells[0], "D9E1F2")
        _set_cell_shading(header_cells[1], "D9E1F2")
        for key, value in metrics.items():
            row_cells = table.add_row().cells
            row_cells[0].text = str(key)
            row_cells[1].text = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)

    if assets_payload:
        document.add_paragraph("Group KPI Dashboard")
        _render_group_kpi_table(document, assets_payload)


def _render_group_kpi_table(document: Document, assets_payload: object) -> None:
    group_summary = _summarize_groups(assets_payload)
    if not group_summary:
        document.add_paragraph("No group assignments available.")
        return
    table = document.add_table(rows=1, cols=5)
    table.style = "Light Grid Accent 1"
    header_cells = table.rows[0].cells
    headers = ["Group", "Type", "Dynamic Rule", "Assigned Assets", "Settings Applied"]
    for idx, header in enumerate(headers):
        header_cells[idx].text = header
        _set_cell_shading(header_cells[idx], "BDD7EE")
    for row in group_summary:
        row_cells = table.add_row().cells
        row_cells[0].text = row["name"]
        row_cells[1].text = row["type"]
        row_cells[2].text = row["dynamic_rule"] or "N/A"
        row_cells[3].text = str(row["assigned_assets"])
        row_cells[4].text = str(row["settings_applied"])
        _set_cell_shading(row_cells[3], "C6E0B4")
        _set_cell_shading(row_cells[4], "FCE4D6")


def _summarize_groups(assets_payload: object) -> list[dict[str, object]]:
    summary: Dict[str, dict[str, object]] = {}
    if not isinstance(assets_payload, list):
        return []
    for asset in assets_payload:
        asset_id = asset.get("asset_id")
        assignments = asset.get("assignment_mappings", [])
        settings = asset.get("settings", {}) or {}
        settings_count = len(settings) if isinstance(settings, dict) else 0
        for mapping in assignments:
            group_id = mapping.get("groupId")
            if not group_id:
                continue
            group_entry = summary.setdefault(
                group_id,
                {
                    "name": mapping.get("groupDisplayName") or group_id,
                    "type": mapping.get("groupType") or "unknown",
                    "dynamic_rule": mapping.get("groupDynamicRule"),
                    "assigned_assets": set(),
                    "settings_applied": 0,
                },
            )
            group_entry["assigned_assets"].add(asset_id)
            group_entry["settings_applied"] += settings_count

    results: list[dict[str, object]] = []
    for group in summary.values():
        results.append(
            {
                "name": group["name"],
                "type": group["type"],
                "dynamic_rule": group["dynamic_rule"],
                "assigned_assets": len(group["assigned_assets"]),
                "settings_applied": group["settings_applied"],
            }
        )
    return sorted(results, key=lambda item: item["name"].lower())


def _render_assets_section(document: Document, assets_payload: object) -> None:
    if not isinstance(assets_payload, list):
        document.add_paragraph("No asset data available.")
        return
    for asset in assets_payload:
        asset_name = asset.get("name") or "Unnamed Asset"
        asset_type = asset.get("asset_type") or "Unknown"
        document.add_heading(f"{asset_name} ({asset_type})", level=2)
        document.add_paragraph(f"Asset ID: {asset.get('asset_id')}")

        settings = asset.get("settings", {}) or {}
        document.add_paragraph("Settings")
        if settings:
            table = document.add_table(rows=1, cols=2)
            table.style = "Light Grid"
            header_cells = table.rows[0].cells
            header_cells[0].text = "Setting"
            header_cells[1].text = "Value"
            _set_cell_shading(header_cells[0], "E2EFDA")
            _set_cell_shading(header_cells[1], "E2EFDA")
            for key, value in settings.items():
                row_cells = table.add_row().cells
                row_cells[0].text = str(key)
                row_cells[1].text = (
                    json.dumps(value, ensure_ascii=False)
                    if isinstance(value, (dict, list))
                    else str(value)
                )
        else:
            document.add_paragraph("No settings recorded.")

        assignments = asset.get("assignment_mappings", []) or []
        document.add_paragraph("Assignments")
        if assignments:
            table = document.add_table(rows=1, cols=7)
            table.style = "Light Grid"
            headers = [
                "Group",
                "Type",
                "Assignment",
                "Intent",
                "Delivery",
                "Schedule",
                "Dynamic Rule",
            ]
            header_cells = table.rows[0].cells
            for idx, header in enumerate(headers):
                header_cells[idx].text = header
                _set_cell_shading(header_cells[idx], "FFF2CC")
            for mapping in assignments:
                row_cells = table.add_row().cells
                row_cells[0].text = mapping.get("groupDisplayName") or mapping.get("groupId", "")
                row_cells[1].text = mapping.get("groupType") or ""
                row_cells[2].text = mapping.get("assignmentType") or ""
                row_cells[3].text = mapping.get("intent") or ""
                row_cells[4].text = mapping.get("delivery") or ""
                schedule = mapping.get("schedule")
                row_cells[5].text = (
                    json.dumps(schedule, ensure_ascii=False)
                    if isinstance(schedule, (dict, list))
                    else str(schedule or "")
                )
                row_cells[6].text = mapping.get("groupDynamicRule") or "N/A"
        else:
            document.add_paragraph("No assignments recorded.")


def _render_assignment_coverage_section(document: Document, payload: Dict[str, object]) -> None:
    overview_table = document.add_table(rows=1, cols=2)
    overview_table.style = "Light Grid"
    header_cells = overview_table.rows[0].cells
    header_cells[0].text = "Metric"
    header_cells[1].text = "Value"
    _set_cell_shading(header_cells[0], "DDEBF7")
    _set_cell_shading(header_cells[1], "DDEBF7")
    for key in ("total_assets", "assigned_assets", "unassigned_assets"):
        row_cells = overview_table.add_row().cells
        row_cells[0].text = key.replace("_", " ").title()
        row_cells[1].text = str(payload.get(key, 0))

    assignments_by_group = payload.get("assignments_by_group", {}) or {}
    document.add_paragraph("Assignments by Group")
    if assignments_by_group:
        table = document.add_table(rows=1, cols=2)
        table.style = "Light Grid Accent 2"
        header_cells = table.rows[0].cells
        header_cells[0].text = "Group"
        header_cells[1].text = "Assigned Assets"
        _set_cell_shading(header_cells[0], "F8CBAD")
        _set_cell_shading(header_cells[1], "F8CBAD")
        for group, count in assignments_by_group.items():
            row_cells = table.add_row().cells
            row_cells[0].text = str(group)
            row_cells[1].text = str(count)
    else:
        document.add_paragraph("No group assignment coverage available.")


def write_raw_export(raw_export: Dict[str, object], output_prefix: Path) -> Path:
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_path = output_prefix.with_name(f"{output_prefix.name}-raw.json")
    output_path.write_text(json.dumps(raw_export, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path
