"""Initial schema: generation_runs and output_artifacts."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "generation_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("script_name", sa.String(length=128), nullable=False),
        sa.Column("model_id", sa.String(length=256), nullable=False),
        sa.Column("backend", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("generation_runs", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_generation_runs_script_name"), ["script_name"], unique=False)
        batch_op.create_index(batch_op.f("ix_generation_runs_status"), ["status"], unique=False)

    op.create_table(
        "output_artifacts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("file_kind", sa.String(length=32), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["generation_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("output_artifacts", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_output_artifacts_run_id"), ["run_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("output_artifacts", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_output_artifacts_run_id"))

    op.drop_table("output_artifacts")

    with op.batch_alter_table("generation_runs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_generation_runs_status"))
        batch_op.drop_index(batch_op.f("ix_generation_runs_script_name"))

    op.drop_table("generation_runs")
