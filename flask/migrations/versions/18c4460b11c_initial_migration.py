"""Initial migration.

Revision ID: 18c4460b11c
Revises: None
Create Date: 2015-08-10 00:12:27.516484
"""
# pylint: disable=invalid-name,no-member
import sqlalchemy as sa
from alembic import op

revision = '18c4460b11c'
down_revision = None


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.create_table('apartment',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('url', sa.String(), nullable=False),
                    sa.Column('external_id', sa.String(), nullable=True),
                    sa.Column('title', sa.String(), nullable=True),
                    sa.Column('address', sa.String(), nullable=True),
                    sa.Column('neighborhood', sa.String(), nullable=True),
                    sa.Column('cold_rent', sa.String(), nullable=True),
                    sa.Column('warm_rent', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('url'))
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('username', sa.String(length=80), nullable=False),
                    sa.Column('email', sa.String(length=80), nullable=False),
                    sa.Column('password', sa.String(length=128), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('first_name', sa.String(length=30), nullable=True),
                    sa.Column('last_name', sa.String(length=30), nullable=True),
                    sa.Column('active', sa.Boolean(), nullable=True),
                    sa.Column('is_admin', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email'),
                    sa.UniqueConstraint('username'))
    op.create_table('roles',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=80), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name'))


def downgrade():
    """Reverse actions performed during upgrade."""
    op.drop_table('roles')
    op.drop_table('users')
    op.drop_table('apartment')
