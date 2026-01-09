from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
from pathlib import Path
from typing import Iterable, List, Optional

from .auth import request_client_credentials_token, request_device_code_token
from .config import AppConfig, load_config
from .exporters.composite_export import export_all
from .graph_client import GraphClient
from .output import write_raw_export, write_rendered_reports
from .reports.builder import build_report_schema
from .reports.cli import SUPPORTED_AUDIENCES, SUPPORTED_FORMATS, SUPPORTED_SCOPES, _parse_formats
from .reports.registry import render_reports
from .reports.schema import DEFAULT_REPORT_SCOPE, ReportScope


@dataclass(frozen=True)
class ExportCommandOptions:
    formats: List[str]
    audience: str
    scope: ReportScope
    output: str


def _build_export_parser(
    parent: argparse._SubParsersAction,
    default_audience: str,
    default_scope: ReportScope,
    default_output: str,
) -> argparse.ArgumentParser:
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
        default=default_audience,
        help="Audience template to use for report output.",
    )
    export_parser.add_argument(
        "--scope",
        dest="scope",
        choices=SUPPORTED_SCOPES,
        default=default_scope,
        help="Scope of report output: full_settings or assignment_summary.",
    )
    export_parser.add_argument(
        "--output",
        dest="output",
        default=default_output,
        help="Output path or file prefix for generated reports.",
    )
    export_parser.set_defaults(command="export")
    return export_parser


def build_parser(
    default_audience: str = "client",
    default_scope: ReportScope = DEFAULT_REPORT_SCOPE,
    default_output: str = "intune-report",
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="intune-doc", description="Generate Intune documentation exports.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    _build_export_parser(subparsers, default_audience, default_scope, default_output)
    return parser


def parse_args(
    args: Iterable[str],
    default_audience: str = "client",
    default_scope: ReportScope = DEFAULT_REPORT_SCOPE,
    default_output: str = "intune-report",
) -> ExportCommandOptions:
    parser = build_parser(default_audience, default_scope, default_output)
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


def _load_config_or_exit() -> AppConfig:
    try:
        return load_config(Path("config.yaml"))
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def _resolve_output_prefix(config: AppConfig, output: str) -> Path:
    output_path = Path(output)
    if output_path.is_absolute():
        return output_path
    return config.output_directory / output_path


def _resolve_organization(graph_client: GraphClient) -> str:
    response = graph_client.get("/organization", params={"$select": "displayName"})
    organizations = response.get("value", [])
    if organizations:
        return organizations[0].get("displayName") or "Unknown organization"
    return "Unknown organization"


def main(argv: Optional[Iterable[str]] = None) -> int:
    config = _load_config_or_exit()
    options = parse_args(
        list(sys.argv[1:]) if argv is None else argv,
        default_audience=config.report_options.template_set,
    )

    if config.use_device_code:
        token = request_device_code_token(config.tenant_id, config.client_id)
    else:
        token = request_client_credentials_token(
            config.tenant_id,
            config.client_id,
            config.client_secret,
        )

    graph_client = GraphClient(token.access_token)
    raw_export = export_all(graph_client)
    organization = _resolve_organization(graph_client)
    report = build_report_schema(
        raw_export,
        audience=options.audience,
        organization=organization,
        generated_at=raw_export.get("generatedAt"),
    )
    rendered = render_reports(report, options.formats, options.audience, options.scope)

    output_prefix = _resolve_output_prefix(config, options.output)
    write_rendered_reports(rendered, output_prefix, config.report_options.include_sections)

    if config.report_options.include_raw_exports:
        write_raw_export(raw_export, output_prefix)

    return 0
