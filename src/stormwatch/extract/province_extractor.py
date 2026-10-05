# Convert external API responses into internal models

from stormwatch.clients.province_client import ProvinceClient
from stormwatch.models.province import Province


class ProvinceExtractor:
    def __init__(self, client: ProvinceClient) -> None:
        self.client = client

    def extract(self) -> list[Province]:
        raw_provinces = self.client.get_all_provinces()

        provinces = []

        for item in raw_provinces:
            province = Province(
                code=str(item["code"]),
                name=item["name"],
                administrative_unit=item.get(
                    "administrative_unit_name"
                ),
            )

            provinces.append(province)

        return provinces