# -*- coding: utf-8 -*-
"""Flats from ImmoNet."""
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from w3lib.url import url_query_cleaner

from tegenaria.items import ApartmentItem
from tegenaria.spiders import SpiderMixin


class ImmoNetSpider(CrawlSpider, SpiderMixin):
    """Flats from ImmoNet."""

    name = 'immo_net'
    allowed_domains = ['immonet.de']
    start_urls = [
        'https://www.immonet.de/berlin/wohnung-mieten.html',
    ]

    rules = (
        Rule(LinkExtractor(allow=r'/berlin/.+(wohnung|wg|wohnen|haus)',
                           deny='/berlin/.+(studenten|senioren|behinderten|immobilien)')),
        Rule(LinkExtractor(allow=r'/angebot', process_value=url_query_cleaner), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        """Parse the flat response.

        @url https://www.immonet.de/angebot/32188674
        @returns items 1 1
        @scrapes url title address rooms size cold_rent warm_rent additional_costs heating_costs description equipment
        @scrapes location other
        """
        self.shutdown_on_error()
        item = ItemLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_xpath('title', '//h1/text()')
        item.add_xpath('address', '//div[contains(@class, "row")]//span[@id = "infobox-static-address"]/text()')

        for field, id_ in {'rooms': 'equipmentid_1', 'size': 'areaid_1', 'cold_rent': 'priceid_2',
                           'warm_rent': 'priceid_4', 'additional_costs': 'priceid_20',
                           'heating_costs': 'priceid_5', 'description': 'objectDescription',
                           'equipment': 'ausstattung', 'location': 'locationDescription',
                           'other': 'otherDescription'}.items():
            item.add_xpath(field, '//*[@id="{}"]/text()'.format(id_))

        yield item.load_item()
