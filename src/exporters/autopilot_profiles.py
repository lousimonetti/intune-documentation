from __future__ import annotations

from typing import Any, Dict, List

from .common import ResourceDefinition, export_resources


def _extract_settings(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "outOfBoxExperienceSettings": raw.get("outOfBoxExperienceSettings"),
        "enrollmentStatusScreenSettings": raw.get("enrollmentStatusScreenSettings"),
        "deviceNameTemplate": raw.get("deviceNameTemplate"),
        "language": raw.get("language"),
        "isAssigned": raw.get("isAssigned"),
    }


RESOURCES = [
    ResourceDefinition(
        type_key="autopilot_profiles",
        graph_resource_name="windowsAutopilotDeploymentProfile",
        collection_path="/deviceManagement/windowsAutopilotDeploymentProfiles",
        assignment_path_template="/deviceManagement/windowsAutopilotDeploymentProfiles/{id}/assignments",
        settings_extractor=_extract_settings,
        query_params={
            "$select": "id,displayName,description,deviceNameTemplate,language,outOfBoxExperienceSettings,enrollmentStatusScreenSettings,isAssigned"
        },
    ),
]


def export_autopilot_profiles(graph_client: Any) -> List[Dict[str, Any]]:
    return export_resources(graph_client, RESOURCES)
