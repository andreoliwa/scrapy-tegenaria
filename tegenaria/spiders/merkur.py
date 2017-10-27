# -*- coding: utf-8 -*-
"""Apartments from the Merkur Berlin real estate agency."""
import re

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from w3lib.url import url_query_cleaner

from tegenaria.items import ApartmentItem, ApartmentLoader
from tegenaria.spiders import SpiderMixin


class MerkurSpider(CrawlSpider, SpiderMixin):
    """Apartments from the Merkur Berlin real estate agency.

    @url http://www.merkur-berlin.de/?page_id=39
    @returns items 0 0
    @returns requests 1 10
    """

    name = 'merkur'
    allowed_domains = ['merkur-berlin.de']
    start_urls = [
        # Mietwohnungen on the left menu
        'http://www.merkur-berlin.de/?page_id=39'
    ]

    rules = (
        Rule(LinkExtractor(allow=r'exposeID=[\dA-F]+',
                           process_value=lambda url: url_query_cleaner(url, parameterlist=('exposeID', 'showExpose'))),
             callback='parse_item', follow=True),
    )

    SIZE_REGEX = re.compile(r'(?P<size>\d+[,.]\d+)')

    def parse_item(self, response):
        """Parse a page with an apartment.

        @url http://www.merkur-berlin.de/?page_id=39&showExpose=1&exposeID=84857B0AD5B146159C73D483F5299839
        @returns items 1 1
        @scrapes url title address rooms size warm_rent_price description location
        """
        self.shutdown_on_error()
        item = ApartmentLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_xpath('title', '//h4[@class="entry-title"]/text()')
        item.add_xpath('address', '//address/text()')

        for field, info in {'rooms': 'Rooms', 'size': 'AreaLiving', 'warm_rent_price': 'PriceWarmmiete',
                            'cold_rent_price': 'Price'}.items():
            item.add_xpath(field, '//div[@class="infotables"]//tr[@id="infotable_{info}"]/td[@class='
                                  '"infotable_value"]/text()'.format(info=info))

        for field, h2 in {'description': 'Objekt', 'equipment': 'Ausstattung', 'location': 'Lage',
                          'other': 'Mehr Angebote'}.items():
            item.add_xpath(field, '//div[@class="infoblock"]/h2[starts-with(normalize-space(.),'
                                  ' "{h2}")]/following-sibling::p/text()'.format(h2=h2))

        return item.load_item()
