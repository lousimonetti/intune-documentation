from __future__ import annotations

from .rendering import render_report
from .schema import DEFAULT_REPORT_SCOPE, ReportSchema, RenderedReport, ReportScope
from .templates import TemplateSet


FORMAT_NAME = "word"


def render(
    report: ReportSchema,
    template: TemplateSet,
    scope: ReportScope = DEFAULT_REPORT_SCOPE,
) -> RenderedReport:
    return render_report(FORMAT_NAME, report, template, scope)
