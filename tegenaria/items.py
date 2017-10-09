# -*- coding: utf-8 -*-
"""
Define here the models for your scraped items.

See documentation in:
http://doc.scrapy.org/en/latest/topics/items.html
"""
import re

from scrapy import Field, Item
from scrapy.loader.processors import Join, MapCompose

REGEX_DIGITS_SEPARATORS_ONLY = re.compile(r'[\d,.]+')
REGEX_DECIMAL_POINT = re.compile(r'^[\d,]+\.\d{1,2}$')
REGEX_DECIMAL_COMMA = re.compile(r'^[\d.]+,\d{1,2}$')
REGEX_GROUP_OF_THREE_COMMA = re.compile(r'^\d+(,\d{3})+$')
REGEX_GROUP_OF_THREE_POINT = re.compile(r'^\d+(.\d{3})+$')


def clean_number(value: str) -> str:
    """Clean a numeric value, fix the decimal separator, remove any extra chars."""
    digits_separators = REGEX_DIGITS_SEPARATORS_ONLY.findall(value)
    value = ''.join(digits_separators)

    if REGEX_DECIMAL_POINT.match(value) or REGEX_GROUP_OF_THREE_COMMA.match(value):
        value = value.replace(',', '')
    elif REGEX_DECIMAL_COMMA.match(value) or REGEX_GROUP_OF_THREE_POINT.match(value):
        value = value.replace('.', '').replace(',', '.')

    for ending in ('.00', '.0'):
        if value.endswith(ending):
            value = value[0:-len(ending)]
    return value


class ApartmentItem(Item):
    """An apartment item."""

    url = Field(output_processor=Join())
    active = Field(output_processor=Join())
    title = Field(output_processor=Join())
    address = Field(output_processor=Join())
    neighborhood = Field(output_processor=Join())
    rooms = Field(input_processor=MapCompose(clean_number), output_processor=Join())
    size = Field(input_processor=MapCompose(clean_number), output_processor=Join())

    cold_rent_price = Field(input_processor=MapCompose(clean_number), output_processor=Join())
    warm_rent_price = Field(input_processor=MapCompose(clean_number), output_processor=Join())
    additional_price = Field(input_processor=MapCompose(clean_number), output_processor=Join())
    heating_price = Field(input_processor=MapCompose(clean_number), output_processor=Join())

    comments = Field(output_processor=Join())
    description = Field(output_processor=Join())
    equipment = Field(output_processor=Join())
    location = Field(output_processor=Join())
    availability = Field(output_processor=Join())
    other = Field(output_processor=Join())
