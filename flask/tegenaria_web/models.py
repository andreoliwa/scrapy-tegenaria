# -*- coding: utf-8 -*-
"""Tegenaria models."""
from tegenaria_web.database import Column, Model, SurrogatePK, db


class Apartment(SurrogatePK, Model):

    """A home (apartment, flat, etc.)."""

    __tablename__ = 'apartment'

    url = Column(db.String(), unique=True, nullable=False)
    title = Column(db.String())
    description = Column(db.String())
    equipment = Column(db.String())
    location = Column(db.String())
    other = Column(db.String())
    address = Column(db.String())
    neighborhood = Column(db.String())
    cold_rent = Column(db.String())
    warm_rent = Column(db.String())
    warm_rent_notes = Column(db.String())

    def __repr__(self):
        """Represent the object as a unique string."""
        return '<Apartment({url})>'.format(url=self.url)
