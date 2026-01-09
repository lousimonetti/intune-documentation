from __future__ import annotations

from typing import Any, Dict, List

from .common import ResourceDefinition, export_resources


def _extract_provisioning_settings(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "imageId": raw.get("imageId"),
        "cloudPcNamingTemplate": raw.get("cloudPcNamingTemplate"),
        "domainJoinConfiguration": raw.get("domainJoinConfiguration"),
        "windowsSetting": raw.get("windowsSetting"),
    }


def _extract_user_settings(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "localAdminEnabled": raw.get("localAdminEnabled"),
        "resetPolicy": raw.get("resetPolicy"),
        "restorePointSetting": raw.get("restorePointSetting"),
    }


RESOURCES = [
    ResourceDefinition(
        type_key="windows365",
        graph_resource_name="cloudPcProvisioningPolicy",
        collection_path="/deviceManagement/virtualEndpoint/provisioningPolicies",
        assignment_path_template="/deviceManagement/virtualEndpoint/provisioningPolicies/{id}/assignments",
        settings_extractor=_extract_provisioning_settings,
        query_params={"$select": "id,displayName,description,imageId,cloudPcNamingTemplate,domainJoinConfiguration,windowsSetting"},
    ),
    ResourceDefinition(
        type_key="windows365",
        graph_resource_name="cloudPcUserSetting",
        collection_path="/deviceManagement/virtualEndpoint/userSettings",
        assignment_path_template="/deviceManagement/virtualEndpoint/userSettings/{id}/assignments",
        settings_extractor=_extract_user_settings,
        query_params={"$select": "id,displayName,description,localAdminEnabled,resetPolicy,restorePointSetting"},
    ),
]


def export_windows365(graph_client: Any) -> List[Dict[str, Any]]:
    return export_resources(graph_client, RESOURCES)
