"""${message}.

Create Date: ${create_date}
"""
import sqlalchemy as sa  # noqa
from alembic import op
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}


def upgrade():
    """Apply changes to a database (create tables, columns, etc.)."""
    ${upgrades if upgrades else "pass"}


def downgrade():
    """Reverse actions performed during upgrade."""
    ${downgrades if downgrades else "pass"}
