# -*- coding: utf-8 -*-
"""Flats, houses and furnished apartments from Immo Welt."""
from string import digits
from typing import Any, Dict

from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from tegenaria.items import ApartmentItem
from tegenaria.spiders import CleanMixin


class ImmoWeltSpider(CrawlSpider, CleanMixin):
    """Flats, houses and furnished apartments from Immo Welt."""

    name = 'immo_welt'
    allowed_domains = ['immowelt.de']
    start_urls = [
        'https://www.immowelt.de/liste/berlin/wohnungen/mieten?sort=relevanz',
        'https://www.immowelt.de/liste/berlin/haeuser/mieten?sort=relevanz',
        'https://www.immowelt.de/liste/berlin/wohnen-auf-zeit/mieten?sort=relevanz',
    ]

    rules = (
        Rule(LinkExtractor(allow=r'/wohnungen/mieten')),
        Rule(LinkExtractor(allow=r'/expose'), callback='parse_flat', follow=True),
    )

    def parse_flat(self, response):
        """Parse the flat response.

        @url https://www.immowelt.de/expose/2GEZJ4D?bc=101
        @returns items 1 1
        @scrapes url title address rooms size cold_rent warm_rent additional_costs heating_costs description
        """
        self.shutdown_on_error()
        item = ItemLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_xpath('title', '//h1/text()')
        item.add_xpath('address', '//div[@class="location"]/span[@class="no_s"]/text()')
        item.add_xpath('rooms', '//div[contains(@class, "quickfacts")]//div[@class="hardfact rooms"]/text()[1]')
        item.add_xpath('size', '//div[contains(@class, "hardfacts")]/div[contains(@class, "hardfact")][2]/text()[1]')
        item.add_xpath('cold_rent', '//div[contains(@class, "hardfacts")]/div[contains(@class, "hardfact")][1]'
                                    '/strong/text()')

        item.add_xpath('description', '//div[contains(@class, "section_label")][starts-with('
                                      'normalize-space(.), "Objekt")]/following-sibling::div/child::p/text()')

        for field, cell_text in {'warm_rent': 'Warmmiete', 'additional_costs': 'Nebenkosten',
                                 'heating_costs': 'Heizkosten'}.items():
            item.add_xpath(
                field, '//div[contains(@class, "datatable")]/div[contains(@class, "datarow")]/div[contains'
                       '(@class, "datalabel")][starts-with(normalize-space(.), "{}")]/following-sibling::div'
                       '[contains(@class, "datacontent")]/text()'.format(cell_text))
        yield item.load_item()

    def clean_item(self, data: Dict[str, Any]):
        """Clean the item before loading."""
        if 'address' in data:
            zip_city_neighborhood, *_ = data['address'].split(',')
            data['neighborhood'] = zip_city_neighborhood.translate(str.maketrans('', '', digits)).replace(
                'Berlin', '').strip(' ()')

        self.clean_number(data, 'rooms')
        self.clean_number(data, 'size')

        if not data.get('warm_rent', 0):
            result = 0
            for field in ('cold_rent', 'additional_costs', 'heating_costs'):
                try:
                    result += float(data.get(field, 0))
                except ValueError:
                    # Ignore string data on fields
                    pass
            data['warm_rent'] = result

        return data
