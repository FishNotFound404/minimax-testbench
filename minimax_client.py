from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from config import (
    DEFAULT_TIMEOUT,
    LONG_TIMEOUT,
    MINIMAX_API_KEY,
    MINIMAX_BASE_URL,
)


class MiniMaxAPIError(RuntimeError):
    def __init__(self, status_code: int, message: str, payload: Any = None):
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.payload = payload


class MiniMaxClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or MINIMAX_API_KEY
        self.base_url = (base_url or MINIMAX_BASE_URL).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def _check(self, resp: requests.Response) -> Dict[str, Any]:
        if resp.status_code >= 400:
            try:
                payload = resp.json()
            except Exception:
                payload = resp.text
            raise MiniMaxAPIError(resp.status_code, resp.text, payload)
        if not resp.content:
            return {}
        try:
            return resp.json()
        except json.JSONDecodeError:
            raise MiniMaxAPIError(resp.status_code, f"非 JSON 响应: {resp.text[:200]}")

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        resp = self.session.post(self._url(path), json=json or {}, timeout=timeout)
        return self._check(resp)

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        resp = self.session.get(self._url(path), params=params, timeout=timeout)
        return self._check(resp)

    def upload(
        self,
        path: str,
        file_path: str,
        purpose: str,
        extra_fields: Optional[Dict[str, Any]] = None,
        timeout: int = LONG_TIMEOUT,
    ) -> Dict[str, Any]:
        url = self._url(path)
        data = {"purpose": purpose, **(extra_fields or {})}
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f)}
            resp = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=data,
                files=files,
                timeout=timeout,
            )
        return self._check(resp)

    def download(self, url: str, save_path: str, timeout: int = LONG_TIMEOUT) -> str:
        with requests.get(url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return save_path


_client: Optional[MiniMaxClient] = None


def get_client() -> MiniMaxClient:
    global _client
    if _client is None:
        _client = MiniMaxClient()
    return _client
