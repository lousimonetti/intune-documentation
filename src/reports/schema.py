from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class ReportMetadata:
    organization: str
    generated_at: str
    audience: str


@dataclass(frozen=True)
class SummarySection:
    title: str
    highlights: List[str]
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssetDetail:
    asset_id: str
    name: str
    asset_type: str
    settings: Dict[str, Any] = field(default_factory=dict)
    assignments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class AssignmentCoverage:
    total_assets: int
    assigned_assets: int
    unassigned_assets: int
    assignments_by_group: Dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class ReportSchema:
    metadata: ReportMetadata
    summary: SummarySection
    assets: List[AssetDetail]
    assignment_coverage: AssignmentCoverage


@dataclass(frozen=True)
class ReportSection:
    title: str
    description: str
    payload: Dict[str, Any]


@dataclass(frozen=True)
class RenderedReport:
    format: str
    audience: str
    sections: List[ReportSection]
    metadata: ReportMetadata
