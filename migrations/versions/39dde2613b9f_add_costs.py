"""Add additional and heating costs.

Create Date: 2017-10-07 03:18:39.964460
"""
import sqlalchemy as sa
from alembic import op

revision = "39dde2613b9f"
down_revision = "ca07021224c2"


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.add_column("apartment", sa.Column("additional_costs", sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column("apartment", sa.Column("heating_costs", sa.Numeric(precision=10, scale=2), nullable=True))
    op.alter_column(
        "apartment",
        "rooms",
        existing_type=sa.NUMERIC(precision=2, scale=1),
        type_=sa.Numeric(precision=3, scale=1),
        existing_nullable=True,
    )
    op.alter_column(
        "apartment",
        "size",
        existing_type=sa.NUMERIC(precision=4, scale=1),
        type_=sa.Numeric(precision=5, scale=2),
        existing_nullable=True,
    )


def downgrade():
    """Reverse actions performed during upgrade."""
    op.drop_column("apartment", "heating_costs")
    op.drop_column("apartment", "additional_costs")
    op.alter_column(
        "apartment",
        "size",
        existing_type=sa.Numeric(precision=5, scale=2),
        type_=sa.NUMERIC(precision=4, scale=1),
        existing_nullable=True,
    )
    op.alter_column(
        "apartment",
        "rooms",
        existing_type=sa.Numeric(precision=3, scale=1),
        type_=sa.NUMERIC(precision=2, scale=1),
        existing_nullable=True,
    )
