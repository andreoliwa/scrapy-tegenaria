# pylint: disable=invalid-name,no-member
"""Opinions.

Create Date: 2015-10-26 01:03:59.737396
"""
import sqlalchemy as sa
from alembic import op

revision = 'f209d19cf3'
down_revision = '4af9b2e2cd5'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.create_table(
        'opinion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('apartment', sa.Column('opinion_id', sa.Integer(), nullable=True))
    op.create_foreign_key('apartment_opinion_id_fkey', 'apartment', 'opinion', ['opinion_id'], ['id'])
    op.drop_column('apartment', 'interesting')

    op.execute('DROP TYPE interesting_enum')


def downgrade():
    """Reverse actions performed during upgrade."""
    interesting_enum = sa.dialects.postgresql.ENUM('no', 'maybe', 'yes', name='interesting_enum')
    interesting_enum.create(bind=op.get_bind())

    op.add_column('apartment',
                  sa.Column('interesting', interesting_enum, nullable=True))
    op.drop_constraint('apartment_opinion_id_fkey', 'apartment', type_='foreignkey')
    op.drop_column('apartment', 'opinion_id')
    op.drop_table('opinion')
