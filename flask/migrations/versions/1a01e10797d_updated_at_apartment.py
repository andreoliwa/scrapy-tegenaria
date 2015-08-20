"""Updated_at for apartments.

Revision ID: 1a01e10797d
Revises: 48a616b1f23
Create Date: 2015-08-21 00:34:52.971234
"""
# pylint: disable=invalid-name,no-member
import sqlalchemy as sa
from alembic import op

revision = '1a01e10797d'
down_revision = '48a616b1f23'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.add_column('apartment', sa.Column('updated_at', sa.DateTime()))


def downgrade():
    """Reverse actions performed during upgrade."""
    op.drop_column('apartment', 'updated_at')
