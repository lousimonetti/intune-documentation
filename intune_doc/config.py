from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml


@dataclass(frozen=True)
class ReportOptionsConfig:
    template_set: str = "client"
    include_sections: List[str] = field(default_factory=list)
    include_raw_exports: bool = False


@dataclass(frozen=True)
class AppConfig:
    tenant_id: str
    client_id: str
    client_secret: str
    use_device_code: bool
    output_directory: Path
    report_options: ReportOptionsConfig


def _parse_report_options(payload: dict) -> ReportOptionsConfig:
    payload = payload or {}
    include_sections = payload.get("include_sections") or []
    if not isinstance(include_sections, list):
        raise ValueError("report_options.include_sections must be a list")

    return ReportOptionsConfig(
        template_set=payload.get("template_set", "client"),
        include_sections=[str(section).strip() for section in include_sections if str(section).strip()],
        include_raw_exports=bool(payload.get("include_raw_exports", False)),
    )


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    tenant_id = payload.get("tenant_id")
    client_id = payload.get("client_id")
    client_secret = payload.get("client_secret") or ""
    use_device_code = bool(payload.get("use_device_code", False))
    output_directory = Path(payload.get("output_directory", "./output"))

    missing = [
        name
        for name, value in ("tenant_id", tenant_id), ("client_id", client_id)
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required config values: {', '.join(missing)}")

    if not client_secret and not use_device_code:
        raise ValueError("client_secret is required unless use_device_code is true")

    report_options = _parse_report_options(payload.get("report_options", {}))

    return AppConfig(
        tenant_id=str(tenant_id),
        client_id=str(client_id),
        client_secret=str(client_secret),
        use_device_code=use_device_code,
        output_directory=output_directory,
        report_options=report_options,
    )
