# -*- coding: utf-8 -*-
"""Apartments from the Akelius real estate agency."""
import re
from typing import Any, Dict

import requests
from lxml import etree
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from tegenaria.items import ApartmentItem
from tegenaria.spiders import CleanMixin


class AkeliusSpider(CrawlSpider, CleanMixin):
    """Apartments from the Akelius real estate agency."""

    name = 'akelius'
    allowed_domains = ['akelius.de']
    start_urls = [
        'https://www.akelius.de/en/search/apartments/osten/berlin/list'
    ]

    rules = (
        Rule(LinkExtractor(allow=r'berlin/[0-9\.]+'), callback='parse_item'),
    )

    ADDRESS_REGEX = re.compile(r'<div class="g-map-marker".+<p>.+</div>.+infowindow', re.DOTALL)

    def parse_item(self, response):
        """Parse a page with an apartment.

        @url https://www.akelius.de/en/search/apartments/osten/berlin/2.7037.16
        @returns items 1 1
        @scrapes url title warm_rent size availability cold_rent description address
        """
        self.shutdown_on_error()
        item = ItemLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_xpath('title', '//h2/text()')
        item.add_xpath('warm_rent', '//h2/following-sibling::p[starts-with(normalize-space(.), "Total rent")]/text()')
        item.add_xpath('size', '//h2//following-sibling::p[2]/text()')
        item.add_xpath('location',
                       '//h3[starts-with(normalize-space(.), "Location")]/following-sibling::div//span/text()')
        item.add_xpath('availability', '//h2//following-sibling::p[4]/text()')
        item.add_xpath('cold_rent',
                       '//h3[starts-with(normalize-space(.), "Apartment")]/following-sibling::div[1]/p[2]/span/text()')
        item.add_xpath('description',
                       '//h3[starts-with(normalize-space(.), "Building")]/following-sibling::div//span/text()')

        # The map is shown with JavaScript; get the HTML
        # and use a regex to extract the part of the script with the address.
        map_response = requests.get(response.url + '/karte')
        if map_response.status_code == 200:
            html_string = ''.join(self.ADDRESS_REGEX.findall(map_response.text))

            # Extract the address from the HTML.
            root = etree.fromstring(html_string, etree.HTMLParser())
            item.add_value('address', ', '.join(root.xpath('//p/text()')))

        return item.load_item()

    def clean_item(self, data: Dict[str, Any]):
        """Clean the item before loading."""
        self.clean_number(data, 'warm_rent')
        self.clean_number(data, 'size')
        self.clean_number(data, 'availability', separator=None)
        return data
