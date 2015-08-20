"""Active apartment.

Revision ID: 115098256e
Revises: 1a01e10797d
Create Date: 2015-08-21 01:04:32.756407
"""
# pylint: disable=invalid-name,no-member
import sqlalchemy as sa
from alembic import op

revision = '115098256e'
down_revision = '1a01e10797d'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.add_column('apartment', sa.Column('active', sa.Boolean(), nullable=True))


def downgrade():
    """Reverse actions performed during upgrade."""
    op.drop_column('apartment', 'active')
