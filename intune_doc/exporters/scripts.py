from __future__ import annotations

from typing import Any, Dict, List

from .common import ResourceDefinition, export_resources


def _extract_windows_script_settings(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "runAsAccount": raw.get("runAsAccount"),
        "runAs32Bit": raw.get("runAs32Bit"),
        "enforceSignatureCheck": raw.get("enforceSignatureCheck"),
        "fileName": raw.get("fileName"),
    }


def _extract_shell_script_settings(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "runAsAccount": raw.get("runAsAccount"),
        "fileName": raw.get("fileName"),
        "scriptType": raw.get("scriptType"),
    }


def _extract_health_script_settings(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "publisher": raw.get("publisher"),
        "detectionScriptContent": raw.get("detectionScriptContent"),
        "remediationScriptContent": raw.get("remediationScriptContent"),
        "runAsAccount": raw.get("runAsAccount"),
    }


RESOURCES = [
    ResourceDefinition(
        type_key="scripts",
        graph_resource_name="deviceManagementScript",
        collection_path="/deviceManagement/deviceManagementScripts",
        assignment_path_template="/deviceManagement/deviceManagementScripts/{id}/assignments",
        settings_extractor=_extract_windows_script_settings,
        query_params={"$select": "id,displayName,description,runAsAccount,runAs32Bit,enforceSignatureCheck,fileName"},
    ),
    ResourceDefinition(
        type_key="scripts",
        graph_resource_name="deviceShellScript",
        collection_path="/deviceManagement/deviceShellScripts",
        assignment_path_template="/deviceManagement/deviceShellScripts/{id}/assignments",
        settings_extractor=_extract_shell_script_settings,
        query_params={"$select": "id,displayName,description,runAsAccount,fileName,scriptType"},
    ),
    ResourceDefinition(
        type_key="scripts",
        graph_resource_name="deviceHealthScript",
        collection_path="/deviceManagement/deviceHealthScripts",
        assignment_path_template="/deviceManagement/deviceHealthScripts/{id}/assignments",
        settings_extractor=_extract_health_script_settings,
        query_params={"$select": "id,displayName,description,publisher,runAsAccount,detectionScriptContent,remediationScriptContent"},
    ),
]


def export_scripts(graph_client: Any) -> List[Dict[str, Any]]:
    return export_resources(graph_client, RESOURCES)
