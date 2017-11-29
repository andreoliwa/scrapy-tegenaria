"""Apartment and distance.

Revision ID: 19d5ee083f8
Revises: 2ac931bbe13
Create Date: 2015-08-23 02:36:38.002640
"""
import sqlalchemy as sa  # noqa
from alembic import op

revision = '19d5ee083f8'
down_revision = '2ac931bbe13'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.create_table('apartment',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('url', sa.String(), nullable=False),
                    sa.Column('title', sa.String(), nullable=True),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('equipment', sa.String(), nullable=True),
                    sa.Column('location', sa.String(), nullable=True),
                    sa.Column('other', sa.String(), nullable=True),
                    sa.Column('address', sa.String(), nullable=True),
                    sa.Column('neighborhood', sa.String(), nullable=True),
                    sa.Column('cold_rent', sa.String(), nullable=True),
                    sa.Column('warm_rent', sa.String(), nullable=True),
                    sa.Column('warm_rent_notes', sa.String(), nullable=True),
                    sa.Column('rooms', sa.String(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('active', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('url'))
    op.create_table('distance',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('distance_text', sa.String(), nullable=False),
                    sa.Column('distance_value', sa.Integer(), nullable=False),
                    sa.Column('duration_text', sa.String(), nullable=False),
                    sa.Column('duration_value', sa.Integer(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.Column('apartment_id', sa.Integer(), nullable=False),
                    sa.Column('pin_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['apartment_id'], ['apartment.id'], ),
                    sa.ForeignKeyConstraint(['pin_id'], ['pin.id'], ),
                    sa.PrimaryKeyConstraint('id'))


def downgrade():
    """Reverse actions performed during upgrade."""
    op.drop_table('distance')
    op.drop_table('apartment')
