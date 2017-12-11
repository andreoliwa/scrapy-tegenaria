# -*- coding: utf-8 -*-
"""Flats, houses and furnished apartments from Immo Welt."""
from string import digits
from typing import Any, Dict

from scrapy.exceptions import DropItem
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from w3lib.url import url_query_cleaner

from tegenaria.items import ApartmentItem
from tegenaria.spiders import SpiderMixin


class ImmoWeltSpider(CrawlSpider, SpiderMixin):
    """Flats, houses and furnished apartments from Immo Welt."""

    name = 'immo_welt'
    allowed_domains = ['immowelt.de']
    start_urls = [
        'https://www.immowelt.de/liste/berlin/wohnungen/mieten?sort=relevanz',
        'https://www.immowelt.de/liste/berlin/haeuser/mieten?sort=relevanz',
        'https://www.immowelt.de/liste/berlin/wohnen-auf-zeit/mieten?sort=relevanz',
    ]

    rules = (
        Rule(LinkExtractor(allow=r'/berlin/wohnungen/mieten')),
        Rule(LinkExtractor(allow=r'/expose', process_value=url_query_cleaner), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        """Parse the flat response.

        @url https://www.immowelt.de/expose/2GT7W4N
        @returns items 1 1
        @scrapes url title address rooms size cold_rent_price warm_rent_price additional_price heating_price description
        """
        self.shutdown_on_error()
        item = ItemLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_xpath('title', '//h1/text()')
        item.add_xpath('address', '//div[@class="location"]/span[@class="no_s"]/text()')
        item.add_xpath('rooms', '//div[contains(@class, "quickfacts")]//div[@class="hardfact rooms"]/text()[1]')
        item.add_xpath('size', '//div[contains(@class, "hardfacts")]/div[contains(@class, "hardfact")][2]/text()[1]')
        item.add_xpath('cold_rent_price', '//div[contains(@class, "hardfacts")]/div[contains(@class, "hardfact")][1]'
                                          '/strong/text()')

        item.add_xpath('description', '//div[contains(@class, "section_label")][starts-with('
                                      'normalize-space(.), "Objekt")]/following-sibling::div/child::p/text()')

        for field, cell_text in {'warm_rent_price': 'Warmmiete', 'additional_price': 'Nebenkosten',
                                 'heating_price': 'Heizkosten'}.items():
            item.add_xpath(
                field, '//div[contains(@class, "datatable")]/div[contains(@class, "datarow")]/div[contains'
                       '(@class, "datalabel")][starts-with(normalize-space(.), "{}")]/following-sibling::div'
                       '[contains(@class, "datacontent")]/text()'.format(cell_text))
        yield item.load_item()

    def before_marshmallow(self, data: Dict[str, Any]):
        """Clean the item before loading schema on Marshmallow."""
        if 'address' in data:
            zip_city_neighborhood, *_ = data['address'].split(',')
            city_neighborhood = zip_city_neighborhood.translate(str.maketrans('', '', digits))
            if 'Berlin' not in city_neighborhood:
                raise DropItem

            data['neighborhood'] = city_neighborhood.replace('Berlin', '').strip(' ()')

        if not data.get('warm_rent_price', 0):
            result = 0.0
            for field in ('cold_rent_price', 'additional_price', 'heating_price'):
                try:
                    result += float(data.get(field, 0))
                except ValueError:
                    # Ignore string data on fields
                    pass
            data['warm_rent_price'] = result

        return data
