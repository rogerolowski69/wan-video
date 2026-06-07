"""Users table and generation_runs.user_id."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("telegram_id", sa.Integer(), nullable=True),
        sa.Column("wallet_address", sa.String(length=128), nullable=True),
        sa.Column("username", sa.String(length=128), nullable=True),
        sa.Column("display_name", sa.String(length=256), nullable=True),
        sa.Column("photo_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_users_telegram_id"), ["telegram_id"], unique=True)
        batch_op.create_index(batch_op.f("ix_users_wallet_address"), ["wallet_address"], unique=True)

    with op.batch_alter_table("generation_runs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_generation_runs_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(batch_op.f("ix_generation_runs_user_id"), ["user_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("generation_runs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_generation_runs_user_id"))
        batch_op.drop_constraint("fk_generation_runs_user_id_users", type_="foreignkey")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_wallet_address"))
        batch_op.drop_index(batch_op.f("ix_users_telegram_id"))

    op.drop_table("users")
