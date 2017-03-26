# -*- coding: utf-8 -*-
"""Factories used in tests."""
from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory

from tegenaria.database import db
from tegenaria.models import Pin


class BaseFactory(SQLAlchemyModelFactory):
    """Base class for all factories."""

    class Meta:
        """Configuration of this factory."""

        abstract = True
        sqlalchemy_session = db.session


class PinFactory(BaseFactory):
    """Pin factory."""

    name = Sequence(lambda n: 'name{0}'.format(n))
    address = Sequence(lambda n: 'address {0}'.format(n))

    class Meta:
        """Configuration of this factory."""

        model = Pin
