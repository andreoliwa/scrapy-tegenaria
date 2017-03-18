#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from flask_migrate import MigrateCommand
from flask_script import Manager, Server, Shell

from tegenaria.app import create_app
from tegenaria.database import db
from tegenaria.models import Apartment
from tegenaria.settings import DevConfig, ProdConfig
from tegenaria.user.models import User
from tegenaria.utils import (calculate_distance, read_from_keyring, remove_inactive_apartments,
                             reprocess_invalid_apartments, save_json_to_db)

if os.environ.get("TEGENARIA_ENV") == 'prod':
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
def add():
    """Add and update data: import JSON files, calculate distances, etc."""
    json_dir = read_from_keyring("json_dir", secret=False)
    save_json_to_db(json_dir, os.path.join(json_dir, 'out'), Apartment)
    calculate_distance()


@manager.command
def clean():
    """Clean apartments: deactivate 404 pages, reprocess records with empty addresses."""
    remove_inactive_apartments()
    reprocess_invalid_apartments(read_from_keyring("json_dir", secret=False))

# Server available in the local network:
# http://flask.pocoo.org/docs/0.10/api/#flask.Flask.run
manager.add_command('server', Server(host='0.0.0.0'))

manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
