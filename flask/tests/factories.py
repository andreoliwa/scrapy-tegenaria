# -*- coding: utf-8 -*-
"""Factories used in tests."""
from factory import PostGenerationMethodCall, Sequence
from factory.alchemy import SQLAlchemyModelFactory

from tegenaria_web.database import db
from tegenaria_web.user.models import User


class BaseFactory(SQLAlchemyModelFactory):

    """Base class for all factories."""

    class Meta:

        """Configuration of this factory."""

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):

    """User factory."""

    username = Sequence(lambda n: "user{0}".format(n))  # pylint: disable=unnecessary-lambda
    email = Sequence(lambda n: "user{0}@example.com".format(n))  # pylint: disable=unnecessary-lambda
    password = PostGenerationMethodCall('set_password', 'example')
    active = True

    class Meta:

        """Configuration of this factory."""

        model = User
