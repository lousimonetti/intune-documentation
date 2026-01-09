from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable, Dict, Iterable, List, Optional
import urllib.error

from .assignments import collect_assignments

logger = logging.getLogger(__name__)


SettingsExtractor = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass(frozen=True)
class ResourceDefinition:
    type_key: str
    graph_resource_name: str
    collection_path: str
    assignment_path_template: str
    display_name_key: str = "displayName"
    settings_extractor: Optional[SettingsExtractor] = None
    query_params: Optional[Dict[str, str]] = None


def paginate(graph_client: Any, path: str, params: Optional[Dict[str, str]] = None) -> Iterable[Dict[str, Any]]:
    suppress_errors = bool(params and "$select" in params)
    try:
        response = graph_client.get(path, params=params, log_errors=not suppress_errors)
    except urllib.error.HTTPError as exc:
        if exc.code == 400 and params and "$select" in params:
            logger.warning(
                "Graph GET request failed for %s with $select. Retrying without $select parameters.",
                path,
            )
            try:
                response = graph_client.get(path)
            except urllib.error.HTTPError as retry_exc:
                if retry_exc.code in {403, 404}:
                    logger.warning("Graph GET request for %s returned %s. Skipping export.", path, retry_exc.code)
                    return
                raise
        elif exc.code in {403, 404}:
            logger.warning("Graph GET request for %s returned %s. Skipping export.", path, exc.code)
            return
        else:
            logger.error("Graph GET request for %s failed with %s.", path, exc.code)
            raise
    for item in response.get("value", []):
        yield item

    next_link = response.get("@odata.nextLink")
    while next_link:
        response = graph_client.get(next_link, is_absolute=True)
        for item in response.get("value", []):
            yield item
        next_link = response.get("@odata.nextLink")


def normalize_asset(
    raw: Dict[str, Any],
    resource: ResourceDefinition,
    assignments: List[Dict[str, Any]],
) -> Dict[str, Any]:
    display_name = raw.get(resource.display_name_key) or raw.get("name") or raw.get("id")
    settings = {}
    if resource.settings_extractor:
        settings = resource.settings_extractor(raw)

    return {
        "id": raw.get("id"),
        "displayName": display_name,
        "type": resource.type_key,
        "settings": settings,
        "assignments": assignments,
        "sourceResource": {
            "graphResourceName": resource.graph_resource_name,
            "graphCollectionPath": resource.collection_path,
        },
        "raw": raw,
    }


def export_resources(graph_client: Any, resources: List[ResourceDefinition]) -> List[Dict[str, Any]]:
    exported: List[Dict[str, Any]] = []

    for resource in resources:
        for item in paginate(graph_client, resource.collection_path, params=resource.query_params):
            assignment_path = resource.assignment_path_template.format(id=item.get("id"))
            assignments = collect_assignments(graph_client, assignment_path)
            exported.append(normalize_asset(item, resource, assignments))

    return exported
