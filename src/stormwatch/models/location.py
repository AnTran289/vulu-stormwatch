# After collecting provinces, define a location with coordinates.

from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    area_code: str
    area_name: str
    latitude: float
    longitude: float