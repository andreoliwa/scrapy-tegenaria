# -*- coding: utf-8 -*-
"""Apartments from the Merkur Berlin real estate agency."""
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from tegenaria.items import ApartmentItem


class MerkurSpider(CrawlSpider):

    """Apartments from the Merkur Berlin real estate agency."""

    name = 'merkur'
    allowed_domains = ['merkur-berlin.de']
    start_urls = ['http://www.merkur-berlin.de/?page_id=39']

    rules = (
        Rule(LinkExtractor(allow=r'ic_estate_view=[0-9]+&estate_id=[0-9]+'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        """Parse a page with an apartment."""
        item = ItemLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_xpath('title', '//h4[@class="entry-title"]/text()')
        item.add_xpath('address', '//address/text()')

        for field, value in dict(rooms='NumberOfRooms', size='LivingSpace',
                                 warm_rent='TotalRent', cold_rent='BaseRent').items():
            item.add_css(field, 'tr#ImmocasterContentObjectInfoTable-{}'
                                ' td.ImmocasterContentObjectInfoTableRgt::text'.format(value))

        for field, value in dict(description='desc', equipment='furnishing',
                                 location='location', other='other').items():
            item.add_xpath(field, '//div[@class="merkur_infoblock"]'
                                  '[@style="immocaster_infoblock_{}"]/p/text()'.format(value))

        return item.load_item()
