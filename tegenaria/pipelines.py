# -*- coding: utf-8 -*-
"""
Define your item pipelines here.

Don't forget to add your pipeline to the ITEM_PIPELINES setting
See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
"""
from flask import current_app
from scrapy.exceptions import CloseSpider

from tegenaria.app import create_app
from tegenaria.extensions import db
from tegenaria.models import Apartment
from tegenaria.schemas import ApartmentSchema
from tegenaria.settings import DevConfig
from tegenaria.spiders import CleanMixin


class ApartmentPipeline(object):
    """Clean and save an apartment to the database."""

    def __init__(self):
        """Constructor."""
        self.app = current_app or create_app(DevConfig)  # FIXME: get the right config according to the env variable
        self.app.app_context().push()

    def process_item(self, item, spider: CleanMixin):
        """Process an item through the pipeline."""
        try:
            schema = ApartmentSchema()
            schema.context['spider'] = spider

            json_data = dict(item)
            json_data['json'] = dict(item)
            json_data['errors'] = None

            apartment = Apartment.get_or_create(item['url'])
            result = schema.load(json_data, instance=apartment)
            if result.errors:
                # Apply all valid fields to the new instance.
                for key, value in result.data.items():
                    setattr(apartment, key, value)

                # Save the errors and continue.
                apartment.errors = result.errors

                db.session.add(apartment)
            else:
                # On success, we will have a model instance on `result.data`.
                db.session.add(result.data)

            db.session.commit()
        except Exception as err:
            spider.shutdown_message = str(err)
            raise CloseSpider('[{}] {}'.format(self.__class__.__name__, spider.shutdown_message))
        return item
