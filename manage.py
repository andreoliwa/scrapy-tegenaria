#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Management script."""
import os
from glob import glob
from subprocess import call

from flask_migrate import MigrateCommand
from flask_script import Command, Manager, Option, Server, Shell

from tegenaria.app import create_app
from tegenaria.database import db
from tegenaria.generic import read_from_keyring
from tegenaria.settings import DevConfig, ProdConfig
from tegenaria.utils import PROJECT_NAME, calculate_distance, remove_inactive_apartments, reprocess_invalid_apartments

if os.environ.get('TEGENARIA_ENV') == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(HERE, 'tests')

manager = Manager(app)


class Lint(Command):
    """Lint and check code style with flake8."""

    def get_options(self):
        """Command line options."""
        return (
            Option('-f', '--fix-imports', action='store_true', dest='fix_imports', default=False,
                   help='Fix imports using isort, before linting'),
        )

    def run(self, fix_imports):  # pylint: disable=arguments-differ,method-hidden
        """Run command."""
        skip = ['requirements', 'docker']
        root_files = glob('*.py')
        root_directories = [name for name in next(os.walk('.'))[1] if not name.startswith('.')]
        files_and_directories = [arg for arg in root_files + root_directories if arg not in skip]

        def execute_tool(description, *args):
            """Execute a checking tool with its arguments."""
            command_line = list(args) + files_and_directories
            print('{0}: {1}'.format(description, ' '.join(command_line)))
            rv = call(command_line)
            if rv is not 0:
                exit(rv)

        if fix_imports:
            execute_tool('Fixing import order', 'isort', '-rc')
        execute_tool('Checking code style', 'flake8')


def _make_context():
    """Return context dict for a shell session so you can access app, db, and the User model by default."""
    return dict(app=app, db=db)


@manager.command
def test():
    """Run the tests."""
    import pytest
    exit_code = pytest.main([TEST_PATH, '--verbose'])
    return exit_code


@manager.command
def distance():
    """Calculate distances."""
    calculate_distance()


@manager.command
def vacuum():
    """Vacuum clean apartments: deactivate 404 pages, reprocess records with empty addresses."""
    remove_inactive_apartments()
    reprocess_invalid_apartments(read_from_keyring(PROJECT_NAME, 'json_dir', secret=False))


# Server available in the local network:
# http://flask.pocoo.org/docs/0.10/api/#flask.Flask.run
manager.add_command('server', Server(host='0.0.0.0'))
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)
manager.add_command('lint', Lint())


if __name__ == '__main__':
    manager.run()
