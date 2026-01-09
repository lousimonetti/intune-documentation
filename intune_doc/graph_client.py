from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


class GraphClient:
    def __init__(self, token: str, base_url: str = "https://graph.microsoft.com/beta") -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token

    def get(self, path: str, params: Optional[Dict[str, str]] = None, is_absolute: bool = False) -> Dict[str, Any]:
        if is_absolute:
            url = path
        else:
            url = f"{self.base_url}/{path.lstrip('/')}"

        if params:
            query = urllib.parse.urlencode(params)
            url = f"{url}?{query}"

        request = urllib.request.Request(url)
        request.add_header("Authorization", f"Bearer {self.token}")
        request.add_header("Accept", "application/json")

        with urllib.request.urlopen(request) as response:
            payload = response.read().decode("utf-8")

        return json.loads(payload)
