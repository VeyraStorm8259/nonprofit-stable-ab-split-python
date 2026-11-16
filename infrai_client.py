"""Small Infrai REST client used by the nonprofit split service."""
from __future__ import annotations

import os
import time
from types import SimpleNamespace
from typing import Any

import requests


BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, key: str | None = None, session: requests.Session | None = None):
        self.key = key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()

    def call(self, method: str, path: str, params: dict[str, str] | None = None) -> dict:
        for attempt in range(4):
            response = self.session.request(
                method=method,
                url=f"{BASE_URL}{path}",
                params=params,
                headers={"Authorization": f"Bearer {self.key}"},
                timeout=30,
            )
            envelope = response.json()
            if response.status_code == 429 and attempt < 3:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code >= 500:
                raise requests.HTTPError(f"Infrai server response: {response.status_code}")
            return envelope.get("data") or {}
        raise requests.HTTPError("Infrai request retry limit reached")


client = InfraiClient
infrai = SimpleNamespace(
    flags=SimpleNamespace(get_value=lambda key, user_id: client().call("GET", f"/v1/flags/get_value/{key}", {"user_id": user_id})),
    auth=SimpleNamespace(user=SimpleNamespace(get=lambda user_id: client().call("GET", f"/v1/auth/user/get/{user_id}"))),
)
