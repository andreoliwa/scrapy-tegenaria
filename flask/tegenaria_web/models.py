# -*- coding: utf-8 -*-
"""Tegenaria models."""
from tegenaria_web.database import Column, Model, SurrogatePK, db, reference_column


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

    apartment_id = reference_column('apartment')
    pin_id = reference_column('pin')
    distance_text = Column(db.String(), nullable=False)
    distance_value = Column(db.Integer(), nullable=False)
    duration_text = Column(db.String(), nullable=False)
    duration_value = Column(db.Integer(), nullable=False)

    def __repr__(self):
        """Represent the object as a unique string."""
        return '<Distance({} to {}, {}/{})>'.format(
            self.apartment_id, self.pin_id, self.distance_text, self.duration_text)
