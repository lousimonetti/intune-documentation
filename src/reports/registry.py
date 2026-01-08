from __future__ import annotations

from typing import Dict, Iterable

from . import excel, pdf, powerpoint, word
from .schema import ReportSchema, RenderedReport
from .templates import get_template_set


RENDERERS = {
    word.FORMAT_NAME: word.render,
    excel.FORMAT_NAME: excel.render,
    pdf.FORMAT_NAME: pdf.render,
    powerpoint.FORMAT_NAME: powerpoint.render,
}


def render_reports(
    report: ReportSchema,
    formats: Iterable[str],
    audience: str,
) -> Dict[str, RenderedReport]:
    template = get_template_set(audience)
    rendered: Dict[str, RenderedReport] = {}
    for format_name in formats:
        if format_name not in RENDERERS:
            raise ValueError(f"Unknown report format: {format_name}")
        rendered[format_name] = RENDERERS[format_name](report, template)
    return rendered
