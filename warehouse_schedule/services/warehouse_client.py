import httpx

from config import WAREHOUSE_API_URL


class WarehouseClient:

    def __init__(self):
        self.base_url = WAREHOUSE_API_URL

    async def get(self, path: str, params=None):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}{path}",
                params=params
            )

            response.raise_for_status()
            return response.json()

    async def post(self, path: str, data: dict):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}{path}",
                json=data
            )

            response.raise_for_status()
            return response.json()

    async def put(self, path: str, data: dict):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.put(
                f"{self.base_url}{path}",
                json=data
            )

            response.raise_for_status()
            return response.json()