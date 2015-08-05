# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import json
import os
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


def json_config(current_file, key):
    var_dir = os.path.abspath(os.path.join(os.path.dirname(current_file), '../../var'))
    basename_no_ext = os.path.splitext(os.path.basename(current_file))[0]
    full_name = os.path.join(var_dir, '{}.config.json'.format(basename_no_ext))
    with open(full_name) as handle:
        json_content = json.load(handle)
    return json_content.get(key)
