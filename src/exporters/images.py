from __future__ import annotations

from typing import Any, Dict, List

from .common import ResourceDefinition, export_resources


def _extract_settings(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "version": raw.get("version"),
        "size": raw.get("size"),
        "source": raw.get("source"),
        "operatingSystem": raw.get("operatingSystem"),
    }


RESOURCES = [
    ResourceDefinition(
        type_key="images",
        graph_resource_name="cloudPcDeviceImage",
        collection_path="/deviceManagement/virtualEndpoint/deviceImages",
        assignment_path_template="/deviceManagement/virtualEndpoint/deviceImages/{id}/assignments",
        settings_extractor=_extract_settings,
        query_params={"$select": "id,displayName,version,size,source,operatingSystem"},
    ),
]


def export_images(graph_client: Any) -> List[Dict[str, Any]]:
    return export_resources(graph_client, RESOURCES)
