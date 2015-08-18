"""Pins and distances.

Revision ID: 48a616b1f23
Revises: 3603fd9002f
Create Date: 2015-08-16 23:42:26.886334

"""
# pylint: disable=invalid-name,no-member
import sqlalchemy as sa
from alembic import op

revision = '48a616b1f23'
down_revision = '3603fd9002f'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.create_table('pin',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('address', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id'))
    op.create_table('distance',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('apartment_id', sa.Integer(), nullable=False),
                    sa.Column('pin_id', sa.Integer(), nullable=False),
                    sa.Column('distance_text', sa.String(), nullable=False),
                    sa.Column('distance_value', sa.Integer(), nullable=False),
                    sa.Column('duration_text', sa.String(), nullable=False),
                    sa.Column('duration_value', sa.Integer(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['apartment_id'], ['apartment.id'], ),
                    sa.ForeignKeyConstraint(['pin_id'], ['pin.id'], ),
                    sa.PrimaryKeyConstraint('id'))


def downgrade():
    """Reverse actions performed during upgrade."""
    op.drop_table('distance')
    op.drop_table('pin')
