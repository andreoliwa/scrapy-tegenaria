# -*- coding: utf-8 -*-
"""Furnished apartments from City Wohnen."""
import re  # noqa
from datetime import datetime
from typing import Any, Dict
from urllib.parse import unquote_plus

import requests  # noqa
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from w3lib.url import url_query_cleaner

from tegenaria.items import ApartmentItem
from tegenaria.spiders import SpiderMixin


class CityWohnenSpider(CrawlSpider, SpiderMixin):
    """Furnished apartments from City Wohnen."""

    name = 'city_wohnen'
    allowed_domains = ['city-wohnen.de']

    MAX_RECORDS = 300
    start_urls = (
        # This link shows an empty page...
        # 'https://www.city-wohnen.de/eng/berlin/furnished-flats/flat-search/'

        # ... because the actual results are loaded by an AJAX call.
        'https://www.city-wohnen.de/rpc.php?pageid=401&action=services&service=ciwo_search&cmd=search&'
        'filters=city%3Dberlin%26date_from%3D%26room_count%3D1%26rent_amount_min%3D0%26rent_amount_max%3D4375%26'
        'person_count%3D1&order=available_from&page_nr=1&page_size={}'.format(MAX_RECORDS),
    )

    URL_REGEX = r'/eng/berlin/[0-9]+[a-z-]+'
    rules = (
        Rule(LinkExtractor(allow=URL_REGEX, process_value=url_query_cleaner), callback='parse_item', follow=True),
    )

    field_regex = {
        'availability': re.compile(r'.*from (?P<availability>[0-9/]+).*', re.MULTILINE),
        'neighborhood': re.compile(r'furnished apartment in Berlin-(?P<neighborhood>.+)'),
        'address': re.compile(r'.+/maps/search/(?P<address>.+)/@[0-9.,]+')
    }

    def start_requests(self):
        """Parse the results from the hidden AJAX call, and start requests to parse the ads.

        @url https://www.city-wohnen.de
        @returns items 0 0
        @returns requests 1 200
        """
        for url in self.start_urls:
            response = requests.get(url)
            results = response.json().get('results')
            for link in re.compile(self.URL_REGEX).findall(results):
                yield Request('https://www.city-wohnen.de{}'.format(link), callback=self.parse_item)

    def parse_item(self, response):
        """Parse a page with an apartment.

        @url https://www.city-wohnen.de/eng/berlin/32638-moeblierte-wohnung-berlin-friedrichshain-gruenberger-strasse
        @returns items 1 1
        @scrapes url title availability description neighborhood address warm_rent_price size rooms
        """
        self.shutdown_on_error()
        item = ItemLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)

        item.add_css('title', 'div.text_data > h2::text')
        item.add_css('availability', 'div.row > div.text_data > p::text')
        item.add_css('description', 'div.object_details div.col_left p::text')
        item.add_value('neighborhood',
                       response.css('div.object_meta div.container div.text_data p strong::text').extract()[0])
        item.add_xpath('address', "//li[@class='map']/a/@href")

        keys = response.css('div.object_meta table.object_meta_data th::text').extract()
        values = response.css('div.object_meta table.object_meta_data td::text').extract()
        features = dict(zip(keys, values))
        item.add_value('warm_rent_price', features.get('Rent'))
        item.add_value('size', features.get('Size'))
        item.add_value('rooms', features.get('Room/s'))

        return item.load_item()

    def before_marshmallow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean the item before loading schema on Marshmallow."""
        for field, regex in self.field_regex.items():
            clean_field = data.get(field, '').strip(' \t\n')
            match = regex.match(clean_field)
            if not match:
                continue

            data.update(match.groupdict())
            if field == 'availability':
                # Must be an ISO date for the database.
                data['availability'] = datetime.strptime(data.get('availability'), '%d/%m/%Y').date().isoformat()
            elif field == 'address':
                # Decode the URL.
                data['address'] = unquote_plus(data['address'])

        return data
