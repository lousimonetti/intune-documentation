from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional


def _chunked(items: Iterable[str], size: int = 15) -> Iterable[List[str]]:
    batch: List[str] = []
    for item in items:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def _group_type(group: Mapping[str, Any]) -> str:
    group_types = set(group.get("groupTypes", []) or [])
    if "Unified" in group_types:
        return "microsoft365"
    if "DynamicMembership" in group_types:
        return "dynamic"
    return "security"


def _assignment_type(target: Mapping[str, Any]) -> str:
    odata_type = (target.get("@odata.type") or "").lower()
    if "exclusion" in odata_type:
        return "exclude"
    return "include"


def _extract_assignment_target(assignment: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    target = assignment.get("target") or {}
    group_id = target.get("groupId")
    if not group_id:
        return None

    return {
        "groupId": group_id,
        "assignmentType": _assignment_type(target),
    }


def _resolve_groups(graph_client: Any, group_ids: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    resolved: Dict[str, Dict[str, Any]] = {}
    ids = [group_id for group_id in group_ids if group_id]
    if not ids:
        return resolved

    for batch in _chunked(ids):
        filter_value = ",".join(f"'{group_id}'" for group_id in batch)
        response = graph_client.get(
            "/groups",
            params={
                "$select": "id,displayName,groupTypes,securityEnabled,mailEnabled",
                "$filter": f"id in ({filter_value})",
            },
        )
        for group in response.get("value", []):
            resolved[group.get("id")] = group

    return resolved


def collect_assignments(graph_client: Any, assignment_path: str) -> List[Dict[str, Any]]:
    response = graph_client.get(assignment_path)
    assignments = response.get("value", [])
    targets = [_extract_assignment_target(assignment) for assignment in assignments]
    group_ids = [target["groupId"] for target in targets if target]
    resolved_groups = _resolve_groups(graph_client, group_ids)

    normalized: List[Dict[str, Any]] = []
    for assignment, target in zip(assignments, targets):
        if not target:
            continue
        group = resolved_groups.get(target["groupId"], {})
        normalized.append(
            {
                "target": {
                    "groupId": target["groupId"],
                    "groupDisplayName": group.get("displayName"),
                    "groupType": _group_type(group),
                    "assignmentType": target["assignmentType"],
                },
                "intent": assignment.get("intent") or assignment.get("installIntent") or "notApplicable",
                "delivery": assignment.get("delivery"),
                "schedule": assignment.get("schedule"),
            }
        )

    return normalized
