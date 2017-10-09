"""Increase size column.

Create Date: 2017-10-10 01:00:56.023061
"""
import sqlalchemy as sa
from alembic import op

revision = '87be69f7b2e2'
down_revision = 'd22783a120e7'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.alter_column('apartment', 'size',
                    existing_type=sa.NUMERIC(precision=5, scale=2),
                    type_=sa.Numeric(precision=6, scale=2),
                    existing_nullable=True)


def downgrade():
    """Reverse actions performed during upgrade."""
    op.alter_column('apartment', 'size',
                    existing_type=sa.Numeric(precision=6, scale=2),
                    type_=sa.NUMERIC(precision=5, scale=2),
                    existing_nullable=True)
