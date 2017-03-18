# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
# pylint: disable=redefined-outer-name
import pytest
from webtest import TestApp

from tegenaria.app import create_app
from tegenaria.database import db as _db
from tegenaria.settings import TestConfig

from .factories import UserFactory


@pytest.yield_fixture(scope='function')
def app():
    """Yield a new app."""
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='function')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.yield_fixture(scope='function')
def db(app):
    """Yield an empty database."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    _db.drop_all()


@pytest.fixture
def user(db):
    """Yield a new user."""
    user = UserFactory(password='myprecious')
    db.session.commit()
    return user
