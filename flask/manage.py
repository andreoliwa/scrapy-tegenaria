#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from flask_migrate import MigrateCommand
from flask_script import Manager, Server, Shell

from tegenaria_web.app import create_app
from tegenaria_web.database import db, save_json_to_db
from tegenaria_web.models import Apartment
from tegenaria_web.settings import DevConfig, ProdConfig
from tegenaria_web.user.models import User

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
def json():
    """Load JSON files into the database."""
    json_dir = os.environ.get("TEGENARIA_WEB_JSON_DIR")
    if not json_dir:
        raise ValueError('JSON directory not set in the TEGENARIA_WEB_JSON_DIR env variable.')
    save_json_to_db(json_dir, os.path.join(json_dir, 'out'), Apartment)


manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
