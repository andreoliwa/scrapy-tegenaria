#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from flask_migrate import MigrateCommand
from flask_script import Manager, Server, Shell

from tegenaria_web.app import create_app
from tegenaria_web.database import db
from tegenaria_web.models import Apartment
from tegenaria_web.settings import DevConfig, ProdConfig
from tegenaria_web.user.models import User
from tegenaria_web.utils import calculate_distance, read_from_keyring, save_json_to_db

if os.environ.get("TEGENARIA_WEB_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(HERE, 'tests')

manager = Manager(app)


def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User}


@manager.command
def test():
    """Run the tests."""
    import pytest
    exit_code = pytest.main([TEST_PATH, '--verbose'])
    return exit_code


@manager.command
def data():
    """Process data: import JSON files, calculate distances, etc."""
    json_dir = read_from_keyring("json_dir", secret=False)
    save_json_to_db(json_dir, os.path.join(json_dir, 'out'), Apartment)
    calculate_distance()

manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
