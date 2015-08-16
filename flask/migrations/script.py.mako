"""${message}.

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}
"""

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    ${upgrades if upgrades else "pass"}


def downgrade():
    """Reverse actions performed during upgrade."""
    ${downgrades if downgrades else "pass"}
