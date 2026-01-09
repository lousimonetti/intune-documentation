from __future__ import annotations

from typing import Any, Dict, List

from .common import ResourceDefinition, export_resources


def _extract_settings(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "deviceEnrollmentConfigurationType": raw.get("deviceEnrollmentConfigurationType"),
        "priority": raw.get("priority"),
        "platformType": raw.get("platformType"),
        "enrollmentMode": raw.get("enrollmentMode"),
    }


RESOURCES = [
    ResourceDefinition(
        type_key="enrollment_profiles",
        graph_resource_name="deviceEnrollmentConfiguration",
        collection_path="/deviceManagement/deviceEnrollmentConfigurations",
        assignment_path_template="/deviceManagement/deviceEnrollmentConfigurations/{id}/assignments",
        settings_extractor=_extract_settings,
        query_params={"$select": "id,displayName,description,deviceEnrollmentConfigurationType,priority,platformType,enrollmentMode"},
    ),
]


def export_enrollment_profiles(graph_client: Any) -> List[Dict[str, Any]]:
    return export_resources(graph_client, RESOURCES)
