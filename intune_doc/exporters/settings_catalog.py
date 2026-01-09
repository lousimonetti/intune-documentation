from __future__ import annotations

from typing import Any, Dict, List

from .common import ResourceDefinition, export_resources


def _extract_settings(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "settings": raw.get("settings"),
        "settingCount": raw.get("settingCount"),
        "platforms": raw.get("platforms"),
        "technologies": raw.get("technologies"),
    }


RESOURCES = [
    ResourceDefinition(
        type_key="settings_catalog",
        graph_resource_name="deviceManagementConfigurationPolicy",
        collection_path="/deviceManagement/configurationPolicies",
        assignment_path_template="/deviceManagement/configurationPolicies/{id}/assignments",
        settings_extractor=_extract_settings,
        query_params={"$select": "id,displayName,description,platforms,technologies,settingCount,settings"},
    ),
]


def export_settings_catalog(graph_client: Any) -> List[Dict[str, Any]]:
    return export_resources(graph_client, RESOURCES)
