# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class HouseItem(Item):
    id = Field()
    url = Field()
    title = Field()
    address = Field()
    neighborhood = Field()
    cold_rent = Field()
    warm_rent = Field()
