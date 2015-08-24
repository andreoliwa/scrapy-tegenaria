"""Pin.

Revision ID: 2ac931bbe13
Revises: 18c4460b11c
Create Date: 2015-08-23 02:31:31.170542
"""
# pylint: disable=invalid-name,no-member
import sqlalchemy as sa
from alembic import op

revision = '2ac931bbe13'
down_revision = '18c4460b11c'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.create_table('pin',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('address', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id'))


def downgrade():
    """Reverse actions performed during upgrade."""
    op.drop_table('pin')
