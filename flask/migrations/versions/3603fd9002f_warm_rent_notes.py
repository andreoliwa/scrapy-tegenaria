"""Warm rent notes.

Revision ID: 3603fd9002f
Revises: 2ac56d1b4e0
Create Date: 2015-08-13 23:45:16.956456
"""
# pylint: disable=invalid-name,no-member
import sqlalchemy as sa
from alembic import op

revision = '3603fd9002f'
down_revision = '2ac56d1b4e0'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.add_column('apartment', sa.Column('warm_rent_notes', sa.String(), nullable=True))


def downgrade():
    """Reverse actions performed during upgrade."""
    op.drop_column('apartment', 'warm_rent_notes')
