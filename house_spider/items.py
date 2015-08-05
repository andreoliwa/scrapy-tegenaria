# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from string import strip

from scrapy import Item, Field
from scrapy.loader.processors import Join, MapCompose


def sanitize_price(value):
    """Remove the euro symbol and thousands separator.

    :param value: Value to sanitize.
    :type value: str

    :return: Clean value.
    """
    return value.replace(u'\u20ac', '').replace('.', '')


class HouseItem(Item):
    url = Field(
        output_processor=Join()
    )
    id = Field(
        input_processor=MapCompose(strip),
        output_processor=Join()
    )
    title = Field(
        output_processor=Join()
    )
    address = Field(
        output_processor=Join()
    )
    neighborhood = Field(
        output_processor=Join()
    )
    cold_rent = Field(
        input_processor=MapCompose(sanitize_price, strip),
        output_processor=Join()
    )
    warm_rent = Field(
        input_processor=MapCompose(sanitize_price, strip),
        output_processor=Join()
    )
