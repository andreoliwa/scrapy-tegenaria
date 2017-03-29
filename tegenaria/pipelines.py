# -*- coding: utf-8 -*-
"""
Define your item pipelines here.

Don't forget to add your pipeline to the ITEM_PIPELINES setting
See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
"""
from flask import current_app

from tegenaria.app import create_app
from tegenaria.extensions import db
from tegenaria.models import Apartment
from tegenaria.schemas import ApartmentSchema
from tegenaria.settings import DevConfig


class ApartmentPipeline(object):
    """Clean and save an apartment to the database."""

    def __init__(self):
        """Constructor."""
        self.app = current_app or create_app(DevConfig)  # FIXME: get the right config according to the env variable
        self.app.app_context().push()

    def process_item(self, item, spider):
        """Process an item through the pipeline."""
        schema = ApartmentSchema()
        schema.context['spider'] = spider

        json_data = dict(item)
        json_data['json'] = dict(item)
        json_data['errors'] = None

        apartment = Apartment.get_or_create(item['url'])
        result = schema.load(json_data, instance=apartment)
        if result.errors:
            # Save the errors and continue.
            apartment.errors = result.errors

            # Apply all valid fields to the new instance.
            for key, value in result.data.items():
                setattr(apartment, key, value)
            db.session.add(apartment)
        else:
            # On success, we will have a model instance on `result.data`.
            db.session.add(result.data)

        db.session.commit()
        return item
