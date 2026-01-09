"""Report rendering utilities and templates."""

from .cli import ReportOptions, build_parser, parse_args
from .registry import render_reports
from .schema import (
    AssetDetail,
    AssignmentCoverage,
    DEFAULT_REPORT_SCOPE,
    ReportMetadata,
    ReportScope,
    ReportSchema,
    ReportSection,
    RenderedReport,
    SummarySection,
)
from .templates import TemplateSet, get_template_set

__all__ = [
    "AssetDetail",
    "AssignmentCoverage",
    "DEFAULT_REPORT_SCOPE",
    "ReportMetadata",
    "ReportOptions",
    "ReportScope",
    "ReportSchema",
    "ReportSection",
    "RenderedReport",
    "SummarySection",
    "TemplateSet",
    "build_parser",
    "get_template_set",
    "parse_args",
    "render_reports",
]
