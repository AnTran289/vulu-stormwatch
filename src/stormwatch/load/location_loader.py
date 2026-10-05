
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from stormwatch.database.schema import locations
from stormwatch.models.location import Location


class LocationLoader:

    def __init__(
        self,
        engine: Engine,
    ) -> None:
        self.engine = engine

    def load(
        self,
        location_records: list[Location],
    ) -> int:

        rows = []

        for location in location_records:
            rows.append(
                {
                    "area_code": location.area_code,
                    "area_name": location.area_name,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                }
            )

        if not rows:
            return 0

        statement = insert(
            locations
        ).values(rows)

        statement = (
            statement.on_conflict_do_update(
                index_elements=[
                    "area_code",
                ],
                set_={
                    "area_name": (
                        statement.excluded.area_name
                    ),
                    "latitude": (
                        statement.excluded.latitude
                    ),
                    "longitude": (
                        statement.excluded.longitude
                    ),
                },
            )
        )

        with self.engine.begin() as connection:
            connection.execute(statement)

        return len(rows)