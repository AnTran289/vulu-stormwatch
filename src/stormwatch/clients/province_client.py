# Use the base client to access the provinces API

from typing import Any

from stormwatch.clients.base_client import APIClient
from stormwatch.config.settings import PROVINCE_API_BASE_URL


class ProvinceClient:
    def __init__(self) -> None:
        self.client = APIClient(PROVINCE_API_BASE_URL)

    def get_all_provinces(self) -> list[dict[str, Any]]:
        response = self.client.get(endpoint="p")

        if not isinstance(response, list):
            raise ValueError("Province API returned an invalid response.")
        
        return response