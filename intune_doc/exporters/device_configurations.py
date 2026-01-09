from __future__ import annotations

from typing import Any, Dict, List

from .common import ResourceDefinition, export_resources


def _extract_settings(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "settings": raw.get("settings") or raw.get("omaSettings"),
        "payload": raw.get("payload"),
        "platforms": raw.get("platforms"),
    }


RESOURCES = [
    ResourceDefinition(
        type_key="device_configurations",
        graph_resource_name="deviceConfiguration",
        collection_path="/deviceManagement/deviceConfigurations",
        assignment_path_template="/deviceManagement/deviceConfigurations/{id}/assignments",
        settings_extractor=_extract_settings,
        query_params={"$select": "id,displayName,description,platforms,settings,omaSettings,payload"},
    ),
]


def export_device_configurations(graph_client: Any) -> List[Dict[str, Any]]:
    return export_resources(graph_client, RESOURCES)
