# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask_login import UserMixin

from tegenaria.database import Column, Model, SurrogatePK, db, reference_column, relationship
from tegenaria.extensions import bcrypt


class Role(SurrogatePK, Model):
    """A role."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_column('users', nullable=True)
    user = relationship('User', backref='roles')

    def __init__(self, name, **kwargs):
        """Create a role."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent the object as a unique string."""
        return '<Role({name})>'.format(name=self.name)


class User(UserMixin, SurrogatePK, Model):
    """An user."""

    __tablename__ = 'users'
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    password = Column(db.String(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)

    def __init__(self, username, email, password=None, **kwargs):
        """Create an user."""
        db.Model.__init__(self, username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set the user password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check the user password."""
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        """Full name of the user."""
        return "{0} {1}".format(self.first_name, self.last_name)

    def __repr__(self):
        """Represent the object as a unique string."""
        return '<User({username!r})>'.format(username=self.username)
