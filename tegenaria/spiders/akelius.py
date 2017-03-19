# -*- coding: utf-8 -*-
"""Apartments from the Akelius real estate agency."""
import re

import requests
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from tegenaria.items import ApartmentItem


class AkeliusSpider(CrawlSpider):
    """Apartments from the Akelius real estate agency."""

    name = 'akelius'
    allowed_domains = ['akelius.de']
    start_urls = ['https://akelius.de/en/search/apartments/osten/berlin/;list/']

    rules = (
        Rule(LinkExtractor(allow=r'berlin/[0-9]+/'), callback='parse_item'),
    )

    field_regex = dict(
        title=re.compile(r'\s*(?P<rooms>[0-9.]+)\s*Room[s], [(Bezirk)]\s*(?P<neighborhood>.*)'),
        availability=re.compile(r'\s*Available from\s*(?P<availability>.+)[\s\t]*')
    )

    ADDRESS_REGEX = re.compile(r'markers.+width.+?>(.+)<br \\/>(.+)<.+div>')

    def parse_item(self, response):
        """Parse a page with an apartment."""
        item = ItemLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_css('title', 'article.node.asset.view > header > h2::text')
        item.add_css('warm_rent', 'div.metadata > p.fact-netrent > span.label-text::text')
        item.add_css('size', 'div.metadata > p.fact-size::text')
        item.add_css('location', 'div.metadata > p.fact-location::text')
        item.add_css('availability', 'div.metadata > p.fact-availability::text')

        keys = response.css('div.set > p.features > span.bundle > strong.key > span.factlabel::text').extract()
        values = response.css('div.set > p.features > span.bundle > span.value::text').extract()
        features = dict(zip(keys, values))
        item.add_value('cold_rent', features.get('Net Rent'))

        item.add_value('description',
                       u''.join(sorted([u'{}: {}\n'.format(key, value) for key, value in features.items()])))

        map_response = requests.get(response.url + u'map/')
        match = self.ADDRESS_REGEX.search(map_response.content)
        item.add_value('address', ', '.join(match.groups()))

        item_dict = item.load_item()

        # After loading: get rooms and neighborhood from the title, clean availability date.
        for field, regex in self.field_regex.items():
            match = regex.match(item_dict.get(field))
            if match:
                item_dict.update(match.groupdict())

        return item_dict
