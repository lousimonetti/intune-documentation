from __future__ import annotations

from typing import Any, Dict, List

from .common import ResourceDefinition, export_resources


def _extract_settings(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "bodyText": raw.get("bodyText"),
        "acceptanceStatement": raw.get("acceptanceStatement"),
        "version": raw.get("version"),
        "termsAndConditionsType": raw.get("termsAndConditionsType"),
    }


RESOURCES = [
    ResourceDefinition(
        type_key="initial_access_policies",
        graph_resource_name="termsAndConditions",
        collection_path="/deviceManagement/termsAndConditions",
        assignment_path_template="/deviceManagement/termsAndConditions/{id}/assignments",
        settings_extractor=_extract_settings,
        query_params={"$select": "id,displayName,description,bodyText,acceptanceStatement,version,termsAndConditionsType"},
    ),
]


def export_initial_access_policies(graph_client: Any) -> List[Dict[str, Any]]:
    return export_resources(graph_client, RESOURCES)
