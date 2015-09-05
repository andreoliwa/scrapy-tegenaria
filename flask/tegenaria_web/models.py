# -*- coding: utf-8 -*-
"""Tegenaria models."""
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.functions import func

from tegenaria_web.database import Column, Model, SurrogatePK, db, reference_column, relationship

INTERESTING_NO = 'no'
INTERESTING_MAYBE = 'maybe'
INTERESTING_YES = 'yes'
INTERESTING_ENUM = postgresql.ENUM(INTERESTING_NO, INTERESTING_MAYBE, INTERESTING_YES, name='interesting_enum')


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
    rooms = Column(db.String())
    interesting = Column(INTERESTING_ENUM)
    comments = Column(db.String())
    created_at = Column(db.DateTime, default=func.now())
    updated_at = Column(db.DateTime, onupdate=func.now(), default=func.now())
    active = Column(db.Boolean, default=False)

    distances = db.relationship('Distance')

    def __repr__(self):
        """Represent the object as a unique string."""
        return '<Apartment({id}: {url})>'.format(id=self.id, url=self.url)


class Pin(SurrogatePK, Model):

    """A pin in the map, a reference address to be used when calculating distances."""

    __tablename__ = 'pin'

    name = Column(db.String())
    address = Column(db.String())

    def __repr__(self):
        """Represent the object as a unique string."""
        return '<Pin({}, {})>'.format(self.name, self.address)


class Distance(SurrogatePK, Model):

    """Distance from a pin to an apartment."""

    __tablename__ = 'distance'

    distance_text = Column(db.String(), nullable=False)
    distance_value = Column(db.Integer(), nullable=False)
    duration_text = Column(db.String(), nullable=False)
    duration_value = Column(db.Integer(), nullable=False)
    updated_at = Column(db.DateTime, nullable=False, onupdate=func.now(), default=func.now())

    apartment_id = reference_column('apartment')
    apartment = relationship('Apartment')

    pin_id = reference_column('pin')
    pin = relationship('Pin')

    def __repr__(self):
        """Represent the object as a unique string."""
        return "<Distance('{}' to '{}', {}/{})>".format(
            self.apartment.address, self.pin.address, self.distance_text, self.duration_text)
