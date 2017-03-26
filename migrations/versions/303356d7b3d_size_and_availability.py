"""Size and availability.

Create Date: 2015-10-28 02:32:48.214820
"""
import sqlalchemy as sa
from alembic import op

revision = '303356d7b3d'
down_revision = 'f209d19cf3'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.add_column('apartment', sa.Column('availability', sa.Date(), nullable=True))
    op.add_column('apartment', sa.Column('size', sa.String(), nullable=True))


def downgrade():
    """Reverse actions performed during upgrade."""
    op.drop_column('apartment', 'size')
    op.drop_column('apartment', 'availability')
