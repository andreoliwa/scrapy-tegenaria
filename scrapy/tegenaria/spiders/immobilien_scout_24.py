# -*- coding: utf-8 -*-
"""A spider to crawl the Immobilien Scout 24 website."""
import re

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

from tegenaria.items import ApartmentItem, json_config


class ImmobilienScout24Spider(scrapy.Spider):

    """A spider to crawl the Immobilien Scout 24 website."""

    name = "immobilien_scout_24"
    allowed_domains = ["immobilienscout24.de"]
    start_urls = (
        'http://www.immobilienscout24.de/',
    )

    CITY = ' Berlin,'
    DIV_PRE_MAPPING = {
        'description': 'is24qa-objektbeschreibung',
        'equipment': 'is24qa-ausstattung',
        'location': 'is24qa-lage',
        'other': 'is24qa-sonstiges'
    }
    WARM_RENT_RE = re.compile(r'(?P<warm_rent>[0-9,.]+)[\s(]*(?P<warm_rent_notes>[^)]*)')

    def parse(self, response):
        """Parse a search results HTML page."""
        for link in LinkExtractor(allow=r'expose/[0-9]+$').extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_item)

    def parse_item(self, response):
        """Parse an ad page, with an apartment."""
        item = ItemLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_css('title', 'h1#expose-title::text')

        for field, css_class in self.DIV_PRE_MAPPING.items():
            item.add_xpath(field, "//div/pre[contains(@class, '{}')]/text()".format(css_class))

        full_address = ''.join(response.xpath("//span[@data-qa='is24-expose-address']/text()").extract()).strip()
        parts = full_address.split(self.CITY)
        if len(parts) == 1:
            item.add_value('address', full_address)
        else:
            item.add_value('address', (parts[0] + self.CITY).strip(' ,'))
            item.add_value('neighborhood', ''.join(parts[1:]).strip(' ,'))

        item.add_css('cold_rent', 'div.is24qa-kaltmiete::text')
        item.add_css('warm_rent', 'dd.is24qa-gesamtmiete::text')
        item.add_css('rooms', 'div.is24qa-zimmer::text')
        item_dict = item.load_item()

        # Warm rent can have additional notes to the right.
        match = self.WARM_RENT_RE.match(item_dict['warm_rent'])
        if match:
            item_dict.update(match.groupdict())

        yield item_dict

ImmobilienScout24Spider.start_urls = json_config(__file__, 'start_urls')
