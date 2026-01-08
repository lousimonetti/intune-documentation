from __future__ import annotations

from typing import Any, Dict, List

from .common import ResourceDefinition, export_resources


def _extract_settings(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "tokenName": raw.get("tokenName"),
        "tokenExpirationDateTime": raw.get("tokenExpirationDateTime"),
        "defaultiOSSettings": raw.get("defaultiOSSettings"),
        "defaultMacOSSettings": raw.get("defaultMacOSSettings"),
    }


RESOURCES = [
    ResourceDefinition(
        type_key="provisioning_profiles",
        graph_resource_name="depOnboardingSetting",
        collection_path="/deviceManagement/depOnboardingSettings",
        assignment_path_template="/deviceManagement/depOnboardingSettings/{id}/assignments",
        settings_extractor=_extract_settings,
        query_params={
            "$select": "id,displayName,description,tokenName,tokenExpirationDateTime,defaultiOSSettings,defaultMacOSSettings"
        },
    ),
]


def export_provisioning_profiles(graph_client: Any) -> List[Dict[str, Any]]:
    return export_resources(graph_client, RESOURCES)
