from __future__ import annotations

from .rendering import render_report
from .schema import ReportSchema, RenderedReport
from .templates import TemplateSet


FORMAT_NAME = "pdf"


def render(report: ReportSchema, template: TemplateSet) -> RenderedReport:
    return render_report(FORMAT_NAME, report, template)
