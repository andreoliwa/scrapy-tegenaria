# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
from pytest import fixture, yield_fixture
from webtest import TestApp

from tegenaria.app import create_app
from tegenaria.database import db as _db
from tegenaria.settings import TestConfig


@yield_fixture(scope="function")
def app():
    """Yield a new app."""
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@fixture(scope="function")
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@yield_fixture(scope="function")
def db(app):
    """Yield an empty database."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    _db.drop_all()
