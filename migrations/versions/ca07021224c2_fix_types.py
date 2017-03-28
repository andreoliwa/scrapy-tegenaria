"""Fix columns types (https://github.com/andreoliwa/python-tegenaria/issues/69).

Create Date: 2017-03-27 00:49:50.053095
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from tegenaria.generic import add_mandatory_column

revision = 'ca07021224c2'
down_revision = '10e28a1a0962'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    add_mandatory_column('apartment', 'json', postgresql.JSONB(astext_type=sa.Text()), "'{}'::json")
    op.alter_column('apartment', 'active', existing_type=sa.BOOLEAN(), nullable=False)
    op.drop_column('apartment', 'warm_rent_notes')

    op.alter_column('apartment', 'cold_rent',
                    existing_type=sa.VARCHAR(),
                    type_=sa.Numeric(precision=7, scale=2),
                    existing_nullable=True,
                    postgresql_using='cold_rent::numeric(7,2)')
    op.alter_column('apartment', 'rooms',
                    existing_type=sa.VARCHAR(),
                    type_=sa.Numeric(precision=2, scale=1),
                    existing_nullable=True,
                    postgresql_using='rooms::numeric(2,1)')
    op.alter_column('apartment', 'size',
                    existing_type=sa.VARCHAR(),
                    type_=sa.Numeric(precision=4, scale=1),
                    existing_nullable=True,
                    postgresql_using='size::numeric(4,1)')
    op.alter_column('apartment', 'warm_rent',
                    existing_type=sa.VARCHAR(),
                    type_=sa.Numeric(precision=7, scale=2),
                    existing_nullable=True,
                    postgresql_using='warm_rent::numeric(7,2)')

    add_mandatory_column('distance', 'json', postgresql.JSONB(astext_type=sa.Text()), "'{}'::json")
    add_mandatory_column('distance', 'meters', sa.Integer(), 'distance_value::INTEGER')
    add_mandatory_column('distance', 'minutes', sa.Integer(), '(duration_value / 60)::INTEGER')
    op.drop_column('distance', 'distance_value')
    op.drop_column('distance', 'distance_text')
    op.drop_column('distance', 'duration_value')
    op.drop_column('distance', 'duration_text')


def downgrade():
    """Reverse actions performed during upgrade."""
    add_mandatory_column('distance', 'duration_text', sa.VARCHAR(), "''")
    add_mandatory_column('distance', 'duration_value', sa.INTEGER(), '-1')
    add_mandatory_column('distance', 'distance_text', sa.VARCHAR(), "''")
    add_mandatory_column('distance', 'distance_value', sa.INTEGER(), '-1')
    op.drop_column('distance', 'minutes')
    op.drop_column('distance', 'meters')
    op.drop_column('distance', 'json')

    op.alter_column('apartment', 'warm_rent',
                    existing_type=sa.Numeric(precision=7, scale=2),
                    type_=sa.VARCHAR(),
                    existing_nullable=True)
    op.alter_column('apartment', 'size',
                    existing_type=sa.Numeric(precision=4, scale=1),
                    type_=sa.VARCHAR(),
                    existing_nullable=True)
    op.alter_column('apartment', 'rooms',
                    existing_type=sa.Numeric(precision=2, scale=1),
                    type_=sa.VARCHAR(),
                    existing_nullable=True)
    op.alter_column('apartment', 'cold_rent',
                    existing_type=sa.Numeric(precision=7, scale=2),
                    type_=sa.VARCHAR(),
                    existing_nullable=True)

    op.add_column('apartment', sa.Column('warm_rent_notes', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.alter_column('apartment', 'active', existing_type=sa.BOOLEAN(), nullable=True)
    op.drop_column('apartment', 'json')
