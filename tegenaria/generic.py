"""Generic utilities that can be reused by other projects."""
import re
from getpass import getpass
from typing import Any, Optional

import arrow
from alembic import op
from flask import json
from keyring import get_password, set_password
from markupsafe import Markup
from sqlalchemy import Column

FIELDS_REGEX = re.compile(r"{([^}]+)}")


def read_from_keyring(project_name, key, secret=True, always_ask=False):
    """Read a key from the keyring.

    :param project_name: Name of the project.
    :param key: Name of the key.
    :param secret: If True, don't show characters while typing in the prompt.
    :param always_ask: Always ask for the value in a prompt.
    :return: Value stored in the keyring.
    """
    value = get_password(project_name, key)
    if not value or always_ask:
        prompt_function = getpass if secret else input
        value = prompt_function("Type a value for the key '{}.{}': ".format(project_name, key))
    if not value:
        raise ValueError("{}.{} is not set in the keyring.".format(project_name, key))
    set_password(project_name, key, value)
    return value


def format_as_human_date(view, value):
    """Format a date for the list view."""
    return arrow.get(value).humanize()


def render_link(url: str, text: str = None, target: Optional[str] = "_blank", title: str = None) -> str:
    """Render a HTML link (the <a> tag)."""
    return Markup(
        '<a title="{title}" href="{url}"{target}>{text}</a>'.format(
            url=url, text=text, target=' target="{}"'.format(target) if target else "", title=title if title else text
        )
    )


def when_none(value: Any, something: Any = "") -> str:
    """Return something when the value is None. Default: empty string."""
    return something if value is None else value


def add_mandatory_column(
    table_name: str,
    column_name: str,
    column_type: Any,
    default_value: str = None,
    column_exists: bool = False,
    update_only_null: bool = False,
):
    """Add a mandatory column to a table.

    NOT NULL fields must be populated with some value before setting `nullable=False`.

    :param table_name: Name of the table.
    :param column_name: Name of the column.
    :param column_type: Type of the column. E.g.: sqlalchemy.String().
    :param default_value: The default value to be UPDATEd in the column.
        If not informed, then generates UUIDs with `uuid_generate_v4()`.
    :param column_exists: Flag to indicate if the column already exists (to skip creation).
    :param update_only_null: Flag to only update values that are null and leave the others
    """
    if default_value is None:
        default_value = "uuid_generate_v4()"

    if not column_exists:
        op.add_column(table_name, Column(column_name, column_type, nullable=True))

    sql = 'UPDATE "{table}" SET "{column}" = {default_value}'
    if update_only_null:
        sql += ' WHERE "{column}" IS NULL'

    op.execute(sql.format(table=table_name, column=column_name, default_value=default_value))
    op.alter_column(table_name, column_name, nullable=False)


def format_json_textarea(view, value):
    """Format a dict as a (not so) pretty JSON.

    For the future:
    - Better formatting (don't use textarea);
    - Highlight with Pygments.
    """
    return Markup(
        '<pre><textarea rows="30" cols="50">{}</textarea></pre>'.format(json.dumps(value, indent=2, sort_keys=True))
    )
