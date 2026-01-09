from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class GraphClient:
    def __init__(self, token: str, base_url: str = "https://graph.microsoft.com/beta") -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token

    def get(
        self,
        path: str,
        params: Optional[Dict[str, str]] = None,
        is_absolute: bool = False,
        log_errors: bool = True,
    ) -> Dict[str, Any]:
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
        request.add_header("consistencylevel", "eventual")

        logger.debug("Graph GET request to %s", url)
        try:
            with urllib.request.urlopen(request) as response:
                payload = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8") if exc.fp else ""
            if log_errors:
                logger.error(
                    "Graph GET request failed (%s %s) for %s. Response: %s",
                    exc.code,
                    exc.reason,
                    url,
                    error_body,
                )
            raise
        except urllib.error.URLError as exc:
            logger.error("Graph GET request failed for %s: %s", url, exc.reason)
            raise

        return json.loads(payload)
