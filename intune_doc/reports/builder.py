from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from .schema import (
    AssignmentCoverage,
    AssetDetail,
    ReportMetadata,
    ReportSchema,
    SummarySection,
)


def _assignment_groups(assignments: Iterable[Dict[str, Any]]) -> Iterable[str]:
    for assignment in assignments:
        target = assignment.get("target") or {}
        name = target.get("groupDisplayName") or target.get("groupId")
        if name:
            yield name


def _build_summary(assets: List[AssetDetail]) -> SummarySection:
    total_assets = len(assets)
    assigned_assets = sum(1 for asset in assets if asset.assignments)
    type_counts = Counter(asset.asset_type for asset in assets)

    highlights = [
        f"Exported {total_assets} Intune assets.",
        f"{assigned_assets} assets have assignments.",
    ]

    return SummarySection(
        title="Intune export summary",
        highlights=highlights,
        metrics={"total_assets": total_assets, "assigned_assets": assigned_assets, "assets_by_type": dict(type_counts)},
    )


def _build_assignment_coverage(assets: List[AssetDetail]) -> AssignmentCoverage:
    total_assets = len(assets)
    assigned_assets = sum(1 for asset in assets if asset.assignments)
    group_counts = Counter()
    for asset in assets:
        group_counts.update(_assignment_groups(asset.assignments))

    return AssignmentCoverage(
        total_assets=total_assets,
        assigned_assets=assigned_assets,
        unassigned_assets=total_assets - assigned_assets,
        assignments_by_group=dict(group_counts),
    )


def _build_asset_details(raw_assets: Iterable[Dict[str, Any]]) -> List[AssetDetail]:
    assets: List[AssetDetail] = []
    for raw in raw_assets:
        assets.append(
            AssetDetail(
                asset_id=str(raw.get("id")),
                name=str(raw.get("displayName") or raw.get("name") or raw.get("id")),
                asset_type=str(raw.get("type")),
                settings=raw.get("settings") or {},
                assignments=raw.get("assignments") or [],
                assignment_mappings=raw.get("assignmentMappings") or [],
            )
        )
    return assets


def build_report_schema(
    raw_export: Dict[str, Any],
    audience: str,
    organization: str,
    generated_at: str | None = None,
) -> ReportSchema:
    assets = _build_asset_details(raw_export.get("assets", []))
    metadata = ReportMetadata(
        organization=organization,
        generated_at=generated_at or datetime.now(timezone.utc).isoformat(),
        audience=audience,
    )
    summary = _build_summary(assets)
    assignment_coverage = _build_assignment_coverage(assets)

    return ReportSchema(
        metadata=metadata,
        summary=summary,
        assets=assets,
        assignment_coverage=assignment_coverage,
    )


def as_dict(report: ReportSchema) -> Dict[str, Any]:
    return asdict(report)
