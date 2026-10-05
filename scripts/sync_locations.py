# province sync script
from pathlib import Path

import pandas as pd
import requests

VULU_API_URL = (
    "http://127.0.0.1:8000/admin/provinces"
)

OUTPUT_FILE = Path(
    "data/reference/province_coordinates.csv"
)


def fetch_provinces() -> list[dict]:
    response = requests.get(
        VULU_API_URL,
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    return payload["provinces"]


def transform_provinces(
    provinces: list[dict],
) -> list[dict]:

    rows = []

    for province in provinces:
        rows.append(
            {
                "area_code": str(
                    province["code"]
                ),
                "area_name": province[
                    "fullName"
                ],
                "latitude": float(
                    province["latitude"]
                ),
                "longitude": float(
                    province["longitude"]
                ),
            }
        )

    return rows


def save_locations(
    rows: list[dict],
) -> None:

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe = pd.DataFrame(rows)

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )


def main() -> None:
    provinces = fetch_provinces()

    print(
        f"Fetched {len(provinces)} provinces."
    )

    rows = transform_provinces(
        provinces
    )

    save_locations(rows)

    print(
        f"Saved {len(rows)} locations to "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()