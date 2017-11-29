"""Size column with numeric overflow (https://github.com/andreoliwa/scrapy-tegenaria/issues/225).

Create Date: 2017-10-27 01:16:21.177093
"""
import sqlalchemy as sa  # noqa
from alembic import op

revision = '2a4073217d5d'
down_revision = '87be69f7b2e2'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.alter_column('apartment', 'size',
                    existing_type=sa.NUMERIC(precision=6, scale=2),
                    type_=sa.Numeric(precision=7, scale=2),
                    existing_nullable=True)


def downgrade():
    """Reverse actions performed during upgrade."""
    op.alter_column('apartment', 'size',
                    existing_type=sa.Numeric(precision=7, scale=2),
                    type_=sa.NUMERIC(precision=6, scale=2),
                    existing_nullable=True)
