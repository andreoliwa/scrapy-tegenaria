"""Rename price columns.

Create Date: 2017-10-09 03:02:45.271499
"""
from alembic import op

revision = 'd22783a120e7'
down_revision = '39dde2613b9f'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.alter_column('apartment', 'warm_rent', new_column_name='warm_rent_price')
    op.alter_column('apartment', 'heating_costs', new_column_name='heating_price')
    op.alter_column('apartment', 'additional_costs', new_column_name='additional_price')
    op.alter_column('apartment', 'cold_rent', new_column_name='cold_rent_price')


def downgrade():
    """Reverse actions performed during upgrade."""
    op.alter_column('apartment', 'warm_rent_price', new_column_name='warm_rent')
    op.alter_column('apartment', 'heating_price', new_column_name='heating_costs')
    op.alter_column('apartment', 'cold_rent_price', new_column_name='cold_rent')
    op.alter_column('apartment', 'additional_price', new_column_name='additional_costs')
