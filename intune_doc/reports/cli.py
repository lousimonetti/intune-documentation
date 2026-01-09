from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable, List

from .registry import RENDERERS
from .schema import DEFAULT_REPORT_SCOPE, ReportScope
from .templates import TEMPLATE_SETS


SUPPORTED_FORMATS = tuple(RENDERERS.keys())
SUPPORTED_AUDIENCES = tuple(TEMPLATE_SETS.keys())
SUPPORTED_SCOPES = ("full_settings", "assignment_summary")


@dataclass(frozen=True)
class ReportOptions:
    formats: List[str]
    audience: str
    scope: ReportScope = DEFAULT_REPORT_SCOPE


def _parse_formats(values: Iterable[str]) -> List[str]:
    formats: List[str] = []
    for value in values:
        for item in value.split(","):
            cleaned = item.strip().lower()
            if cleaned:
                formats.append(cleaned)

    if not formats:
        return list(SUPPORTED_FORMATS)

    invalid = [fmt for fmt in formats if fmt not in SUPPORTED_FORMATS]
    if invalid:
        raise ValueError(f"Unsupported formats: {', '.join(invalid)}")

    return formats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Intune reports.")
    parser.add_argument(
        "--format",
        dest="formats",
        action="append",
        default=[],
        help=(
            "Output format(s). Repeat or comma-separate values. "
            f"Supported: {', '.join(SUPPORTED_FORMATS)}"
        ),
    )
    parser.add_argument(
        "--audience",
        dest="audience",
        choices=SUPPORTED_AUDIENCES,
        default="client",
        help="Audience template to use for report output.",
    )
    parser.add_argument(
        "--scope",
        dest="scope",
        choices=SUPPORTED_SCOPES,
        default=DEFAULT_REPORT_SCOPE,
        help="Scope of report output: full_settings or assignment_summary.",
    )
    return parser


def parse_args(args: Iterable[str]) -> ReportOptions:
    parser = build_parser()
    parsed = parser.parse_args(list(args))
    formats = _parse_formats(parsed.formats)
    return ReportOptions(formats=formats, audience=parsed.audience, scope=parsed.scope)
