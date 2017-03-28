# -*- coding: utf-8 -*-
"""SQLAlchemy models."""
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.functions import func

from tegenaria.database import Column, Model, SurrogatePK, db, reference_column, relationship


class Apartment(SurrogatePK, Model):
    """A home (apartment, flat, etc.)."""

    __tablename__ = 'apartment'

    url = Column(db.String(), unique=True, nullable=False)
    active = Column(db.Boolean, default=True, nullable=False)
    title = Column(db.String())
    address = Column(db.String())
    neighborhood = Column(db.String())
    rooms = Column(db.Numeric(2, 1))
    size = Column(db.Numeric(4, 1))
    cold_rent = Column(db.Numeric(7, 2))
    warm_rent = Column(db.Numeric(7, 2))

    opinion_id = reference_column('opinion', True)
    opinion = relationship('Opinion')

    description = Column(db.String())
    equipment = Column(db.String())
    location = Column(db.String())
    other = Column(db.String())
    availability = Column(db.Date)
    comments = Column(db.String())

    # Scrapy JSON
    json = db.Column(postgresql.JSONB, nullable=False)
    created_at = Column(db.DateTime, default=func.now())
    updated_at = Column(db.DateTime, onupdate=func.now(), default=func.now())

    distances = relationship('Distance')

    def __repr__(self):
        """Represent the object as a unique string."""
        return '<Apartment({}: {} {})>'.format(self.id, self.url, self.opinion.title if self.opinion else '')


class Opinion(SurrogatePK, Model):
    """An opinion about an apartment."""

    __tablename__ = 'opinion'

    title = Column(db.String())


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
    apartment = relationship('Apartment')

    pin_id = reference_column('pin')
    pin = relationship('Pin')

    meters = Column(db.Integer(), nullable=False)
    minutes = Column(db.Integer(), nullable=False)

    # Google Matrix JSON
    json = db.Column(postgresql.JSONB, nullable=False)
    updated_at = Column(db.DateTime, nullable=False, onupdate=func.now(), default=func.now())

    def __repr__(self):
        """Represent the object as a unique string."""
        return "<Distance('{}' to '{}', {}/{})>".format(
            self.apartment.address, self.pin.address, self.distance_text, self.duration_text)
