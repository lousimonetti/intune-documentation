from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class SectionTemplate:
    title: str
    description: str
    data_key: str


@dataclass(frozen=True)
class TemplateSet:
    name: str
    summary: SectionTemplate
    asset_details: SectionTemplate
    assignment_coverage: SectionTemplate


ADMIN_TEMPLATE = TemplateSet(
    name="admin",
    summary=SectionTemplate(
        title="Executive Summary",
        description="Operational overview with compliance and configuration highlights.",
        data_key="summary",
    ),
    asset_details=SectionTemplate(
        title="Asset Detail Pages",
        description="Full configuration details, settings, and assignments per asset.",
        data_key="assets",
    ),
    assignment_coverage=SectionTemplate(
        title="Assignment Coverage",
        description="Coverage analysis with group-level assignments and gaps.",
        data_key="assignment_coverage",
    ),
)

CLIENT_TEMPLATE = TemplateSet(
    name="client",
    summary=SectionTemplate(
        title="Summary",
        description="Customer-facing overview of key metrics and outcomes.",
        data_key="summary",
    ),
    asset_details=SectionTemplate(
        title="Asset Details",
        description="Curated asset highlights with essential settings and ownership.",
        data_key="assets",
    ),
    assignment_coverage=SectionTemplate(
        title="Assignment Coverage",
        description="Assignment rollup for key groups and coverage status.",
        data_key="assignment_coverage",
    ),
)

TEMPLATE_SETS: Dict[str, TemplateSet] = {
    ADMIN_TEMPLATE.name: ADMIN_TEMPLATE,
    CLIENT_TEMPLATE.name: CLIENT_TEMPLATE,
}


def get_template_set(name: str) -> TemplateSet:
    try:
        return TEMPLATE_SETS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown template set: {name}") from exc
