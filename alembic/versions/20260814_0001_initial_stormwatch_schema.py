"""Initial StormWatch schema baseline."""

from typing import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260814_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "locations",
        sa.Column("area_code", sa.String(), primary_key=True),
        sa.Column("area_name", sa.String(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
    )
    op.create_table(
        "weather_forecasts",
        sa.Column("area_code", sa.String(), nullable=False),
        sa.Column("area_name", sa.String(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("forecast_for", sa.DateTime(), nullable=False),
        sa.Column("temperature_c", sa.Float()),
        sa.Column("humidity_pct", sa.Float()),
        sa.Column("precipitation_mm", sa.Float()),
        sa.Column("rain_mm", sa.Float()),
        sa.Column("wind_speed_kmh", sa.Float()),
        sa.PrimaryKeyConstraint(
            "area_code",
            "forecast_for",
            name="uq_weather_forecast_area_time",
        ),
    )
    op.create_table(
        "daily_weather_forecasts",
        sa.Column("area_code", sa.String(), nullable=False),
        sa.Column("area_name", sa.String(), nullable=False),
        sa.Column("forecast_date", sa.Date(), nullable=False),
        sa.Column("total_rain_mm", sa.Float(), nullable=False),
        sa.Column("total_precipitation_mm", sa.Float(), nullable=False),
        sa.Column("min_temperature_c", sa.Float()),
        sa.Column("max_temperature_c", sa.Float()),
        sa.Column("max_wind_speed_kmh", sa.Float()),
    )
    op.create_table(
        "pipeline_runs",
        sa.Column("run_id", sa.String(), primary_key=True),
        sa.Column("pipeline_name", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("locations_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locations_successful", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locations_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.String()),
    )
    op.create_table(
        "flood_risk_forecasts",
        sa.Column("area_code", sa.String(), nullable=False),
        sa.Column("forecast_date", sa.Date(), nullable=False),
        sa.Column("daily_rain_mm", sa.Float(), nullable=False),
        sa.Column("max_3h_rain_mm", sa.Float(), nullable=False),
        sa.Column("previous_48h_rain_mm", sa.Float(), nullable=False),
        sa.Column("daily_rain_score", sa.Float(), nullable=False),
        sa.Column("intensity_score", sa.Float(), nullable=False),
        sa.Column("previous_rain_score", sa.Float(), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(), nullable=False),
        sa.UniqueConstraint("area_code", "forecast_date", name="uq_flood_risk_area_date"),
    )


def downgrade() -> None:
    op.drop_table("flood_risk_forecasts")
    op.drop_table("pipeline_runs")
    op.drop_table("daily_weather_forecasts")
    op.drop_table("weather_forecasts")
    op.drop_table("locations")
