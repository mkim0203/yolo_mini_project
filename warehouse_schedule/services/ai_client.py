import httpx

from config import WAREHOUSE_AI_URL


class WarehouseAIClient:

    def __init__(self):
        self.base_url = WAREHOUSE_AI_URL

    async def classify(self, data: dict):
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{WAREHOUSE_AI_URL}/classify",
                json=data
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