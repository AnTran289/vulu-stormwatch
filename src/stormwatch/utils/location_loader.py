# Create a reusable location loader
from pathlib import Path

import pandas as pd

from stormwatch.models.location import Location


def load_locations(
    csv_path: Path,
) -> list[Location]:

    dataframe = pd.read_csv(
        csv_path,

        # administrative code should usually be treated as an identifier -> string
        dtype={
            "area_code": str,
        },
    )

    required_columns = {
        "area_code",
        "area_name",
        "latitude",
        "longitude",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    locations: list[Location] = []

    for row in dataframe.itertuples(
        index=False
    ):
        location = Location(
            area_code=str(row.area_code),
            area_name=str(row.area_name),
            latitude=float(row.latitude),
            longitude=float(row.longitude),
        )

        locations.append(location)

    return locations