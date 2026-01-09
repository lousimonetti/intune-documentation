from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
from typing import Iterable, List, Optional

from .reports.cli import SUPPORTED_AUDIENCES, SUPPORTED_FORMATS, SUPPORTED_SCOPES, _parse_formats
from .reports.schema import DEFAULT_REPORT_SCOPE, ReportScope


@dataclass(frozen=True)
class ExportCommandOptions:
    formats: List[str]
    audience: str
    scope: ReportScope
    output: str


def _build_export_parser(parent: argparse._SubParsersAction) -> argparse.ArgumentParser:
    export_parser = parent.add_parser("export", help="Export Intune documentation.")
    export_parser.add_argument(
        "--format",
        dest="formats",
        action="append",
        default=[],
        help=(
            "Output format(s). Repeat or comma-separate values. "
            f"Supported: {', '.join(SUPPORTED_FORMATS)}"
        ),
    )
    export_parser.add_argument(
        "--audience",
        dest="audience",
        choices=SUPPORTED_AUDIENCES,
        default="client",
        help="Audience template to use for report output.",
    )
    export_parser.add_argument(
        "--scope",
        dest="scope",
        choices=SUPPORTED_SCOPES,
        default=DEFAULT_REPORT_SCOPE,
        help="Scope of report output: full_settings or assignment_summary.",
    )
    export_parser.add_argument(
        "--output",
        dest="output",
        default="intune-report",
        help="Output path or file prefix for generated reports.",
    )
    export_parser.set_defaults(command="export")
    return export_parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="intune-doc", description="Generate Intune documentation exports.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    _build_export_parser(subparsers)
    return parser


def parse_args(args: Iterable[str]) -> ExportCommandOptions:
    parser = build_parser()
    parsed = parser.parse_args(list(args))
    if parsed.command != "export":
        raise ValueError(f"Unknown command: {parsed.command}")
    formats = _parse_formats(parsed.formats)
    return ExportCommandOptions(
        formats=formats,
        audience=parsed.audience,
        scope=parsed.scope,
        output=parsed.output,
    )


def main(argv: Optional[Iterable[str]] = None) -> int:
    parse_args(list(sys.argv[1:]) if argv is None else argv)
    return 0
