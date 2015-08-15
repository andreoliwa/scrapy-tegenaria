# -*- coding: utf-8 -*-
"""Database module, including the SQLAlchemy database object and DB-related utilities."""
import logging
import os
import shutil
from uuid import uuid4

from flask import json
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

from .compat import basestring
from .extensions import db

# Alias common SQLAlchemy names
Column = db.Column  # pylint: disable=invalid-name
relationship = relationship  # pylint: disable=invalid-name


class CRUDMixin(object):

    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):

    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True


class SurrogatePK(object):

    """A mixin that adds a surrogate integer 'primary key' column named ``id`` to any declarative-mapped class.

    From Mike Bayer's "Building the app" talk
    https://speakerdeck.com/zzzeek/building-the-app
    """

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, id):  # pylint: disable=redefined-builtin
        """Get a record by its ID."""
        if any((isinstance(id, basestring) and id.isdigit(),
                isinstance(id, (int, float))),):
            return cls.query.get(int(id))  # pylint: disable=no-member
        return None


def reference_column(table_name, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_column('category')
        category = relationship('Category', backref='categories')
    """
    return db.Column(
        db.ForeignKey("{0}.{1}".format(table_name, pk_name)),
        nullable=nullable, **kwargs)


def save_json_to_db(input_dir, output_dir, model_class):
    """Save JSON records in a database model.

    :param input_dir: Input directory (must exist).
    :type input_dir: str
    :param output_dir: Output directory (will be created if doesn't exist).
    :type output_dir: str
    :param model_class: A SQLAlchemy model class.
    :type model_class: Model
    """
    if not os.path.isdir(input_dir):
        raise ValueError('Input dir {} is not a directory.'.format(input_dir))
    os.makedirs(output_dir, exist_ok=True)

    logger = logging.getLogger(__name__)
    logger.warning('Searching for JSON files in %s', input_dir)
    for name in os.listdir(input_dir):
        full_name = os.path.join(input_dir, name)
        if not os.path.isfile(full_name):
            continue

        logger.warning('Reading %s', full_name)
        with open(full_name) as handle:
            for line in handle:
                json_record = json.loads(line)
                model = model_class(**json_record)
                try:
                    logger.warning(model)
                    model.save()
                except IntegrityError:
                    db.session.rollback()
                    existing = model_class.query.filter_by(url=model.url).one()
                    existing.update(**json_record)

        suffix, extension = os.path.splitext(name)
        destination_name = os.path.join(output_dir, '{}_{}{}'.format(suffix, str(uuid4()), extension))
        logger.warning('Moving file to %s', destination_name)
        shutil.move(full_name, destination_name)
    logger.warning('Done.')
