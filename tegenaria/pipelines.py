# -*- coding: utf-8 -*-
"""
Define your item pipelines here.

Don't forget to add your pipeline to the ITEM_PIPELINES setting
See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
"""
from flask import current_app
from scrapy.exceptions import DropItem

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
        apartment = Apartment.query.filter_by(url=item['url']).first()
        schema = ApartmentSchema()
        schema.context['spider'] = spider

        json_data = dict(item)
        json_data['json'] = dict(item)
        result = schema.load(json_data, instance=apartment)
        if result.errors:
            raise DropItem()  # FIXME: save apartment and errors to the database

        db.session.add(result.data)
        db.session.commit()
        return item
