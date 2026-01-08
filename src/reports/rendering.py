from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from .schema import DEFAULT_REPORT_SCOPE, ReportSchema, ReportScope, ReportSection, RenderedReport
from .templates import TemplateSet


def _distill_assignment_mappings(assignments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    mappings: List[Dict[str, Any]] = []
    for assignment in assignments:
        target = assignment.get("target") or {}
        if not target:
            continue
        mappings.append(
            {
                "groupId": target.get("groupId"),
                "groupDisplayName": target.get("groupDisplayName"),
                "groupType": target.get("groupType"),
                "assignmentType": target.get("assignmentType"),
                "intent": assignment.get("intent"),
                "delivery": assignment.get("delivery"),
                "schedule": assignment.get("schedule"),
            }
        )
    return mappings


def _build_asset_payloads(report: ReportSchema, scope: ReportScope) -> List[Dict[str, Any]]:
    payloads: List[Dict[str, Any]] = []
    for asset in report.assets:
        assignment_mappings = asset.assignment_mappings or _distill_assignment_mappings(asset.assignments)
        if scope == "assignment_summary":
            payloads.append(
                {
                    "asset_id": asset.asset_id,
                    "name": asset.name,
                    "asset_type": asset.asset_type,
                    "assignment_mappings": assignment_mappings,
                }
            )
        else:
            asset_payload = asdict(asset)
            asset_payload["assignment_mappings"] = assignment_mappings
            payloads.append(asset_payload)
    return payloads


def build_sections(
    report: ReportSchema,
    template: TemplateSet,
    scope: ReportScope = DEFAULT_REPORT_SCOPE,
) -> List[ReportSection]:
    return [
        ReportSection(
            title=template.summary.title,
            description=template.summary.description,
            payload={template.summary.data_key: asdict(report.summary)},
        ),
        ReportSection(
            title=template.asset_details.title,
            description=template.asset_details.description,
            payload={template.asset_details.data_key: _build_asset_payloads(report, scope)},
        ),
        ReportSection(
            title=template.assignment_coverage.title,
            description=template.assignment_coverage.description,
            payload={template.assignment_coverage.data_key: asdict(report.assignment_coverage)},
        ),
    ]


def render_report(
    format_name: str,
    report: ReportSchema,
    template: TemplateSet,
    scope: ReportScope = DEFAULT_REPORT_SCOPE,
) -> RenderedReport:
    sections = build_sections(report, template, scope)
    return RenderedReport(
        format=format_name,
        audience=template.name,
        sections=sections,
        metadata=report.metadata,
    )
