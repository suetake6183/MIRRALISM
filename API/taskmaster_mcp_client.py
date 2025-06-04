import os
import logging
from typing import Any, Dict, List, Optional

import requests


class TaskMasterMCPClient:
    """Client for interacting with the TaskMaster MCP server."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: int = 30):
        self.base_url = (base_url or os.getenv("TASKMASTER_MCP_URL", "http://localhost:3000")).rstrip("/")
        self.api_key = api_key or os.getenv("TASKMASTER_MCP_API_KEY")
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def test_connection(self) -> bool:
        """Return True if the MCP server responds to a ping request."""
        try:
            resp = self.session.get(f"{self.base_url}/mcp/ping", timeout=self.timeout)
            return resp.status_code == 200
        except Exception as exc:
            self.logger.error("MCP connection test failed: %s", exc)
            return False

    def get_tasks(self) -> List[Dict[str, Any]]:
        resp = self.session.get(f"{self.base_url}/mcp/tasks", headers=self._headers(), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def next_task(self) -> Dict[str, Any]:
        resp = self.session.post(f"{self.base_url}/mcp/next", headers=self._headers(), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def set_task_status(self, task_id: str, status: str) -> Dict[str, Any]:
        data = {"status": status}
        resp = self.session.post(
            f"{self.base_url}/mcp/tasks/{task_id}/status",
            json=data,
            headers=self._headers(),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def create_task(self, title: str, description: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"title": title, "description": description}
        if extra:
            payload.update(extra)
        resp = self.session.post(
            f"{self.base_url}/mcp/tasks",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()
