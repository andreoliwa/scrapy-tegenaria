"""Fitted kitchen flag (https://github.com/andreoliwa/scrapy-tegenaria/issues/205).

Create Date: 2017-10-27 01:53:58.712106
"""
from alembic import op
import sqlalchemy as sa


revision = 'e84eec0e8a2a'
down_revision = '2a4073217d5d'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.add_column('apartment', sa.Column('fitted_kitchen', sa.Boolean(), nullable=True))


def downgrade():
    """Reverse actions performed during upgrade."""
    op.drop_column('apartment', 'fitted_kitchen')
