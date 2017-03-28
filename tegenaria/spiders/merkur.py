# -*- coding: utf-8 -*-
"""Apartments from the Merkur Berlin real estate agency."""
import re

from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from tegenaria.items import ApartmentItem


class MerkurSpider(CrawlSpider):
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
        Rule(LinkExtractor(allow=r'exposeID=[\dA-F]+'), callback='parse_item', follow=True),
    )

    SIZE_REGEX = re.compile(r'(?P<size>\d+[,.]\d+)')

    def clean_item(self, in_data):
        """Clean the size field."""
        match = self.SIZE_REGEX.search(in_data['size'].replace(',', '.'))
        if match:
            in_data['size'] = match.groupdict()['size']
        return in_data

    def parse_item(self, response):
        """Parse a page with an apartment.

        @url http://www.merkur-berlin.de/?page_id=39&showExpose=1&exposeID=A640D86F42744BAC8EBF09390EC17E97
        @returns items 1 1
        @scrapes url title address rooms size warm_rent description equipment location other
        """
        item = ItemLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_xpath('title', '//h4[@class="entry-title"]/text()')
        item.add_xpath('address', '//address/text()')

        for field, info in dict(rooms='Rooms', size='AreaLiving', warm_rent='PriceWarmmiete',
                                cold_rent='Price').items():
            item.add_xpath(field, '//div[@class="infotables"]//tr[@id="infotable_{info}"]/td[@class='
                                  '"infotable_value"]/text()'.format(info=info))

        for field, h2 in dict(description='Objekt', equipment='Ausstattung',
                              location='Lage', other='Mehr Angebote').items():
            item.add_xpath(field, '//div[@class="infoblock"]/h2[starts-with(normalize-space(.),'
                                  ' "{h2}")]/following-sibling::p/text()'.format(h2=h2))

        return item.load_item()
