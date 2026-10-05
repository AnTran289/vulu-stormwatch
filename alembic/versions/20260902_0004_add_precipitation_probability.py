"""Add hourly precipitation probability."""

from typing import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260902_0004"
down_revision: str | None = "20260818_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "weather_forecasts",
        sa.Column(
            "precipitation_probability_pct",
            sa.SmallInteger(),
            nullable=True,
        ),
    )
    op.create_check_constraint(
        "ck_weather_forecasts_precipitation_probability_pct",
        "weather_forecasts",
        "precipitation_probability_pct IS NULL OR "
        "precipitation_probability_pct BETWEEN 0 AND 100",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_weather_forecasts_precipitation_probability_pct",
        "weather_forecasts",
        type_="check",
    )
    op.drop_column(
        "weather_forecasts",
        "precipitation_probability_pct",
    )
