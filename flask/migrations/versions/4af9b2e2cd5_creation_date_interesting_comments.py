# pylint: disable=invalid-name,no-member
"""Creation date, interesting, comments.

Create Date: 2015-09-05 23:53:52.621665
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '4af9b2e2cd5'
down_revision = '19d5ee083f8'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    interesting_enum = postgresql.ENUM('no', 'maybe', 'yes', name='interesting_enum')
    interesting_enum.create(bind=op.get_bind())

    op.add_column('apartment', sa.Column('comments', sa.String(), nullable=True))
    op.add_column('apartment', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('apartment',
                  sa.Column('interesting', interesting_enum, nullable=True))


def downgrade():
    """Reverse actions performed during upgrade."""
    op.drop_column('apartment', 'interesting')
    op.drop_column('apartment', 'created_at')
    op.drop_column('apartment', 'comments')

    op.execute('DROP TYPE interesting_enum')
