"""Store per-province pipeline failures."""

from typing import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260818_0003"
down_revision: str | None = "20260814_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pipeline_failures",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "run_id",
            sa.String(),
            sa.ForeignKey("pipeline_runs.run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("area_code", sa.String(), nullable=False),
        sa.Column("area_name", sa.String(), nullable=False),
        sa.Column("stage", sa.String(), nullable=False),
        sa.Column("error_message", sa.String(), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_pipeline_failures_run_id",
        "pipeline_failures",
        ["run_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_pipeline_failures_run_id", table_name="pipeline_failures")
    op.drop_table("pipeline_failures")
