"""empty message.

Create Date: 2017-03-26 04:38:43.954950
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '10e28a1a0962'
down_revision = '303356d7b3d'


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    op.drop_table('roles')
    op.drop_table('users')


def downgrade():
    """Reverse actions performed during upgrade."""
    op.create_table(
        'users',
        sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('users_id_seq'::regclass)"),
                  nullable=False),
        sa.Column('username', sa.VARCHAR(length=80), autoincrement=False, nullable=False),
        sa.Column('email', sa.VARCHAR(length=80), autoincrement=False, nullable=False),
        sa.Column('password', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('first_name', sa.VARCHAR(length=30), autoincrement=False, nullable=True),
        sa.Column('last_name', sa.VARCHAR(length=30), autoincrement=False, nullable=True),
        sa.Column('active', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column('is_admin', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='users_pkey'),
        sa.UniqueConstraint('email', name='users_email_key'),
        sa.UniqueConstraint('username', name='users_username_key'),
        postgresql_ignore_search_path=False
    )
    op.create_table(
        'roles',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('name', sa.VARCHAR(length=80), autoincrement=False, nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='roles_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='roles_pkey'),
        sa.UniqueConstraint('name', name='roles_name_key')
    )
