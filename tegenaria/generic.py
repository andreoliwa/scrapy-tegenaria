"""Generic utilities that can be reused by other projects."""
import re
from getpass import getpass
from typing import Any, Optional

import arrow as arrow
import keyring
from markupsafe import Markup

FIELDS_REGEX = re.compile(r'{([^}]+)}')


def read_from_keyring(project_name, key, secret=True, always_ask=False):
    """Read a key from the keyring.

    :param project_name: Name of the project.
    :param key: Name of the key.
    :param secret: If True, don't show characters while typing in the prompt.
    :param always_ask: Always ask for the value in a prompt.
    :return: Value stored in the keyring.
    """
    value = keyring.get_password(project_name, key)
    if not value or always_ask:
        prompt_function = getpass if secret else input
        value = prompt_function("Type a value for the key '{}.{}': ".format(project_name, key))
    if not value:
        raise ValueError('{}.{} is not set in the keyring.'.format(project_name, key))
    keyring.set_password(project_name, key, value)
    return value


def format_as_human_date(view, value):
    """Format a date for the list view."""
    return arrow.get(value).humanize()


def render_link(url: str, text: str = None, target: Optional[str] = '_blank', title: str = None) -> str:
    """Render a HTML link (the <a> tag)."""
    return Markup('<a title="{title}" href="{url}"{target}>{text}</a>'.format(
        url=url, text=text,
        target=' target="{}"'.format(target) if target else '',
        title=title if title else text))


def when_none(value: Any, something: Any = '') -> str:
    """Return something when the value is None. Default: empty string."""
    return something if value is None else value
