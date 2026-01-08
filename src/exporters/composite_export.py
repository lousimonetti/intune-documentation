from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from .autopilot_profiles import export_autopilot_profiles
from .device_configurations import export_device_configurations
from .enrollment_profiles import export_enrollment_profiles
from .images import export_images
from .initial_access_policies import export_initial_access_policies
from .provisioning_profiles import export_provisioning_profiles
from .scripts import export_scripts
from .settings_catalog import export_settings_catalog
from .windows365 import export_windows365


def export_all(graph_client: Any) -> Dict[str, List[Dict[str, Any]]]:
    assets: List[Dict[str, Any]] = []
    assets.extend(export_device_configurations(graph_client))
    assets.extend(export_settings_catalog(graph_client))
    assets.extend(export_autopilot_profiles(graph_client))
    assets.extend(export_enrollment_profiles(graph_client))
    assets.extend(export_scripts(graph_client))
    assets.extend(export_initial_access_policies(graph_client))
    assets.extend(export_windows365(graph_client))
    assets.extend(export_provisioning_profiles(graph_client))
    assets.extend(export_images(graph_client))

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "assets": assets,
    }
