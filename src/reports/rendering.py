from __future__ import annotations

from dataclasses import asdict
from typing import List

from .schema import ReportSchema, ReportSection, RenderedReport
from .templates import TemplateSet


def build_sections(report: ReportSchema, template: TemplateSet) -> List[ReportSection]:
    return [
        ReportSection(
            title=template.summary.title,
            description=template.summary.description,
            payload={template.summary.data_key: asdict(report.summary)},
        ),
        ReportSection(
            title=template.asset_details.title,
            description=template.asset_details.description,
            payload={template.asset_details.data_key: [asdict(asset) for asset in report.assets]},
        ),
        ReportSection(
            title=template.assignment_coverage.title,
            description=template.assignment_coverage.description,
            payload={template.assignment_coverage.data_key: asdict(report.assignment_coverage)},
        ),
    ]


def render_report(format_name: str, report: ReportSchema, template: TemplateSet) -> RenderedReport:
    sections = build_sections(report, template)
    return RenderedReport(
        format=format_name,
        audience=template.name,
        sections=sections,
        metadata=report.metadata,
    )
