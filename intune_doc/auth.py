from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Dict, Iterable


GRAPH_SCOPE = "https://graph.microsoft.com/.default"
DELEGATED_SCOPES = [
    "DeviceManagementConfiguration.Read.All",
    "DeviceManagementApps.Read.All",
    "DeviceManagementServiceConfig.Read.All",
    "CloudPC.Read.All",
    "Group.Read.All",
]


@dataclass(frozen=True)
class TokenResponse:
    access_token: str


def _post_form(url: str, data: Dict[str, str]) -> Dict[str, str]:
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(url, data=encoded)
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(request) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def _format_scopes(scopes: Iterable[str]) -> str:
    return " ".join(scopes)


def request_client_credentials_token(tenant_id: str, client_id: str, client_secret: str) -> TokenResponse:
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    payload = _post_form(
        url,
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": GRAPH_SCOPE,
            "grant_type": "client_credentials",
        },
    )
    return TokenResponse(access_token=payload["access_token"])


def request_device_code_token(tenant_id: str, client_id: str) -> TokenResponse:
    device_code_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/devicecode"
    device_response = _post_form(
        device_code_url,
        {
            "client_id": client_id,
            "scope": _format_scopes(DELEGATED_SCOPES),
        },
    )

    message = device_response.get("message")
    if message:
        print(message)

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    device_code = device_response["device_code"]
    interval = int(device_response.get("interval", 5))

    while True:
        token_response = _post_form(
            token_url,
            {
                "client_id": client_id,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code,
            },
        )
        if "access_token" in token_response:
            return TokenResponse(access_token=token_response["access_token"])

        error = token_response.get("error")
        if error == "authorization_pending":
            time.sleep(interval)
            continue
        if error == "slow_down":
            interval += 5
            time.sleep(interval)
            continue

        raise RuntimeError(token_response.get("error_description", "Device code authentication failed"))
