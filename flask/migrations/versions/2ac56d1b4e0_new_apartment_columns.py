"""New apartment columns.

Revision ID: 2ac56d1b4e0
Revises: 18c4460b11c
Create Date: 2015-08-12 00:17:08.293722
"""
# pylint: disable=invalid-name,no-member
import sqlalchemy as sa
from alembic import op

revision = '2ac56d1b4e0'
down_revision = '18c4460b11c'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.).

    Drop column in SQLite:
    http://stackoverflow.com/questions/30394222/why-flask-migrate-cannot-upgrade-when-drop-column
    """
    op.add_column('apartment', sa.Column('description', sa.String(), nullable=True))
    op.add_column('apartment', sa.Column('equipment', sa.String(), nullable=True))
    op.add_column('apartment', sa.Column('location', sa.String(), nullable=True))
    op.add_column('apartment', sa.Column('other', sa.String(), nullable=True))

    with op.batch_alter_table('apartment') as batch_op:
        batch_op.drop_column('external_id')


def downgrade():
    """Reverse actions performed during upgrade."""
    op.add_column('apartment', sa.Column('external_id', sa.VARCHAR(), nullable=True))
    with op.batch_alter_table('apartment') as batch_op:
        batch_op.drop_column('other')
        batch_op.drop_column('location')
        batch_op.drop_column('equipment')
        batch_op.drop_column('description')
