# -*- coding: utf-8 -*-
"""
Define here the models for your scraped items.

See documentation in:
http://doc.scrapy.org/en/latest/topics/items.html
"""
import json
import os
import re

from scrapy import Field, Item
from scrapy.loader.processors import Join, MapCompose

REGEX_DECIMAL_POINT = re.compile(r'^[\d,]+\.\d{2}$')
REGEX_DECIMAL_COMMA = re.compile(r'^[\d.]+,\d{2}$')
REGEX_GROUP_OF_THREE_COMMA = re.compile(r'^\d+(,\d{3})+$')
REGEX_GROUP_OF_THREE_POINT = re.compile(r'^\d+(.\d{3})+$')


def sanitize_price(value):
    """Remove the euro symbol and thousands separator.

    Some prices already have a decimal point, so we don't mess with them.

    :param str value: Value to sanitize.

    :return: Clean value.
    """
    value = value.replace(u'\u20ac', '').replace(u'EUR', '').strip()
    if REGEX_DECIMAL_POINT.match(value) or REGEX_GROUP_OF_THREE_COMMA.match(value):
        value = value.replace(',', '')
    elif REGEX_DECIMAL_COMMA.match(value) or REGEX_GROUP_OF_THREE_POINT.match(value):
        value = value.replace('.', '').replace(',', '.')
    if value.endswith('.00'):
        value = value[0:-3]
    return value


class ApartmentItem(Item):
    """An apartment item."""

    url = Field(output_processor=Join())
    active = Field(output_processor=Join())
    title = Field(output_processor=Join())
    address = Field(output_processor=Join())
    neighborhood = Field(output_processor=Join())
    rooms = Field(output_processor=Join())
    size = Field(output_processor=Join())

    cold_rent = Field(input_processor=MapCompose(sanitize_price), output_processor=Join())
    warm_rent = Field(input_processor=MapCompose(sanitize_price), output_processor=Join())
    additional_costs = Field(input_processor=MapCompose(sanitize_price), output_processor=Join())
    heating_costs = Field(input_processor=MapCompose(sanitize_price), output_processor=Join())

    comments = Field(output_processor=Join())
    description = Field(output_processor=Join())
    equipment = Field(output_processor=Join())
    location = Field(output_processor=Join())
    availability = Field(output_processor=Join())
    other = Field(output_processor=Join())


def json_config(current_file, key):
    """Read a configuration from the JSON file.

    :param current_file: Call from a spider, should be __file__.
    :param key: Key to search in the JSON config file.
    :return: The configuration value.
    """
    config_dir = os.path.abspath(os.path.join(os.path.dirname(current_file), '../../_sandbox/config'))
    basename_no_ext = os.path.splitext(os.path.basename(current_file))[0]
    full_name = os.path.join(config_dir, '{}.json'.format(basename_no_ext))
    with open(full_name) as handle:
        json_content = json.load(handle)
    return json_content.get(key)
