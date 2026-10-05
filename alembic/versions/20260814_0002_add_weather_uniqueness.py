"""Add uniqueness required by weather upserts."""

from typing import Sequence

from alembic import op


def _promote_unique_index_or_create(
    *,
    table_name: str,
    constraint_name: str,
    columns: str,
) -> None:
    op.execute(f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = '{constraint_name}'
                  AND conrelid = '{table_name}'::regclass
            ) THEN
                IF EXISTS (
                    SELECT 1 FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relname = '{constraint_name}'
                      AND n.nspname = current_schema()
                      AND c.relkind = 'i'
                ) THEN
                    EXECUTE 'ALTER TABLE {table_name} '
                        'ADD CONSTRAINT {constraint_name} '
                        'UNIQUE USING INDEX {constraint_name}';
                ELSE
                    EXECUTE 'ALTER TABLE {table_name} '
                        'ADD CONSTRAINT {constraint_name} '
                        'UNIQUE ({columns})';
                END IF;
            END IF;
        END $$;
    """)

revision: str = "20260814_0002"
down_revision: str | None = "20260814_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _promote_unique_index_or_create(
        table_name="weather_forecasts",
        constraint_name="uq_weather_forecast_area_time",
        columns="area_code, forecast_for",
    )
    _promote_unique_index_or_create(
        table_name="daily_weather_forecasts",
        constraint_name="uq_daily_weather_forecast_area_date",
        columns="area_code, forecast_date",
    )


def downgrade() -> None:
    # Keep uq_weather_forecast_area_time because revision 0001 defines it as
    # the weather_forecasts primary key.
    op.drop_constraint(
        "uq_daily_weather_forecast_area_date",
        "daily_weather_forecasts",
        type_="unique",
    )
