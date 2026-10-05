# SQLAlchemy table metadata used by repositories and Alembic migrations.
from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Table,
    UniqueConstraint,
)

metadata = MetaData()


weather_forecasts = Table(
    "weather_forecasts",
    metadata,

    Column(
        "area_code",
        String,
        nullable=False,
    ),

    Column(
        "area_name",
        String,
        nullable=False,
    ),

    Column(
        "latitude",
        Float,
        nullable=False,
    ),

    Column(
        "longitude",
        Float,
        nullable=False,
    ),

    Column(
        "forecast_for",
        DateTime,
        nullable=False,
    ),

    Column(
        "temperature_c",
        Float,
    ),

    Column(
        "humidity_pct",
        Float,
    ),

    Column(
        "precipitation_mm",
        Float,
    ),

    Column(
        "rain_mm",
        Float,
    ),

    Column(
        "wind_speed_kmh",
        Float,
    ),

    Column(
        "precipitation_probability_pct",
        SmallInteger,
    ),

    CheckConstraint(
        "precipitation_probability_pct IS NULL OR "
        "precipitation_probability_pct BETWEEN 0 AND 100",
        name="ck_weather_forecasts_precipitation_probability_pct",
    ),

    PrimaryKeyConstraint(
        "area_code",
        "forecast_for",
        name="uq_weather_forecast_area_time",
    ),
)


daily_weather_forecasts = Table(
    "daily_weather_forecasts",
    metadata,

    Column(
        "area_code",
        String,
        nullable=False,
    ),

    Column(
        "area_name",
        String,
        nullable=False,
    ),

    Column(
        "forecast_date",
        Date,
        nullable=False,
    ),

    Column(
        "total_rain_mm",
        Float,
        nullable=False,
    ),

    Column(
        "total_precipitation_mm",
        Float,
        nullable=False,
    ),

    Column(
        "min_temperature_c",
        Float,
    ),

    Column(
        "max_temperature_c",
        Float,
    ),

    Column(
        "max_wind_speed_kmh",
        Float,
    ),
    UniqueConstraint(
        "area_code",
        "forecast_date",
        name="uq_daily_weather_forecast_area_date",
    ),
)

pipeline_runs = Table(
    "pipeline_runs",
    metadata,

    Column(
        "run_id",
        String,
        primary_key=True,
    ),

    Column(
        "pipeline_name",
        String,
        nullable=False,
    ),

    Column(
        "status",
        String,
        nullable=False,
    ),

    Column(
        "started_at",
        DateTime,
        nullable=False,
    ),

    Column(
        "completed_at",
        DateTime,
    ),

    Column(
        "locations_total",
        Integer,
        nullable=False,
        default=0,
    ),

    Column(
        "locations_successful",
        Integer,
        nullable=False,
        default=0,
    ),

    Column(
        "locations_failed",
        Integer,
        nullable=False,
        default=0,
    ),

    Column(
        "error_message",
        String,
    ),
)

locations = Table(
    "locations",
    metadata,

    Column(
        "area_code",
        String,
        primary_key=True,
    ),

    Column(
        "area_name",
        String,
        nullable=False,
    ),

    Column(
        "latitude",
        Float,
        nullable=False,
    ),

    Column(
        "longitude",
        Float,
        nullable=False,
    ),
)

flood_risk_forecasts = Table(
    "flood_risk_forecasts",
    metadata,

    Column("area_code", String, nullable=False),
    Column("forecast_date", Date, nullable=False),

    Column("daily_rain_mm", Float, nullable=False),
    Column("max_3h_rain_mm", Float, nullable=False),
    Column("previous_48h_rain_mm", Float, nullable=False),

    Column("daily_rain_score", Float, nullable=False),
    Column("intensity_score", Float, nullable=False),
    Column("previous_rain_score", Float, nullable=False),

    Column("risk_score", Float, nullable=False),
    Column("risk_level", String, nullable=False),

    UniqueConstraint(
        "area_code",
        "forecast_date",
        name="uq_flood_risk_area_date",
    ),
)

pipeline_failures = Table(
    "pipeline_failures",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "run_id",
        String,
        ForeignKey("pipeline_runs.run_id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("area_code", String, nullable=False),
    Column("area_name", String, nullable=False),
    Column("stage", String, nullable=False),
    Column("error_message", String, nullable=False),
    Column("attempt", Integer, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Index("ix_pipeline_failures_run_id", "run_id"),
)
