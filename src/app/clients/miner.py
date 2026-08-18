from typing import Any

import httpx
from pydantic import BaseModel


class MinerResponse(BaseModel):
    payload: dict[str, Any]


class MinerClient:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def health(self) -> dict[str, Any]:
        return await self._get("/health")

    async def extract(self, url: str) -> MinerResponse:
        data = await self._post("/api/extract", {"source": url})
        return MinerResponse(payload=data)

    async def convert(self, url: str) -> MinerResponse:
        data = await self._post("/convert", {"url": url})
        return MinerResponse(payload=data)

    async def _get(self, path: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{path}")
            response.raise_for_status()
            return response.json()

    async def _post(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}{path}", json=json)
            response.raise_for_status()
            return response.json()
