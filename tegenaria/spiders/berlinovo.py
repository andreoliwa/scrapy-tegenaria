# -*- coding: utf-8 -*-
"""Furnished and regular apartments from Berlinovo."""
import re
from typing import Any, Dict

from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from w3lib.url import url_query_cleaner

from tegenaria.items import ApartmentItem
from tegenaria.spiders import SpiderMixin


class BerlinovoSpider(CrawlSpider, SpiderMixin):
    """Furnished and regular apartments from Berlinovo."""

    name = 'berlinovo'
    allowed_domains = ['berlinovo.de']
    start_urls = [
        # Furnished apartments
        'https://www.berlinovo.de/en/suche-apartments',
        # Regular housing
        'https://www.berlinovo.de/en/suche-wohnungen',
    ]
    rules = (
        Rule(LinkExtractor(allow=r'/en/suche-(apartments|wohnungen).+page=')),
        Rule(LinkExtractor(allow=r'/en/apartment/', process_value=url_query_cleaner),
             callback='parse_furnished', follow=True),
        Rule(LinkExtractor(allow=r'/en/wohnung/', process_value=url_query_cleaner),
             callback='parse_regular', follow=True),
    )

    def parse_common(self, response):
        """Parse common fields for both."""
        self.shutdown_on_error()
        item = ItemLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_css('title', 'h1.title::text')
        return item

    def parse_furnished(self, response):
        """Parse an ad page, with an apartment.

        @url https://www.berlinovo.de/en/apartment/2-room-suite-house-heinrich-heine-stra-e-18-24-berlin-mitte
        @returns items 1 1
        @scrapes url title description location address other neighborhood rooms
        """
        item = self.parse_common(response)
        item.add_xpath('description', '//div[contains(@class, field-name-body)]/div/div[4]/div/div/p/text()')
        item.add_xpath('location', '//div[contains(@class, field-name-field-position)]/div/div[5]/div[2]/div/text()')

        zipcode = response.xpath(
            '//*[@id="block-views-aktuelle-wohnung-block-3"]/div/div/div/div/div[3]/div/span/text()[1]') \
            .extract()[0].strip()
        street = response.xpath(
            '//*[@id="block-views-aktuelle-wohnung-block-3"]/div/div/div/div/div[3]/div/span/text()[2]') \
            .extract()[0].strip()
        item.add_value('address', u'{}, {}'.format(street, zipcode))

        item.add_xpath(
            'equipment',
            '//*[@id="block-views-aktuelle-wohnung-block-3"]/div/div/div/div/div[18]/div/div/ul/li/span/text()')
        item.add_xpath('warm_rent',
                       '//*[@id="block-views-aktuelle-wohnung-block-3"]/div/div/div/div/div[5]/span[2]/text()')

        item.add_xpath('other', '//*[@id="block-views-aktuelle-wohnung-block-3"]/div/div/div/div/div/span/text()')

        item.add_value('neighborhood', response.css('#page-title::text').extract()[0].strip().split('Berlin-')[-1])

        room_list = response.xpath('//*[@id="block-views-aktuelle-wohnung-block-3"]/div/div/div/div/div'
                                   '[contains(@class, views-field-field-rooms-description)]/div/text()').extract()
        item.add_value('rooms', re.findall(r'([0-9]+)', ' '.join(room_list))[0])

        yield item.load_item()

    def parse_regular(self, response):
        """Parse a regular housing apartment ad.

        @url https://www.berlinovo.de/en/wohnung/single-wohnung-hellersdorf-zu-vermieten
        @returns items 1 1
        @scrapes url title address rooms size cold_rent warm_rent description equipment
        """
        item = self.parse_common(response)
        item.add_xpath('address', '//span[@class="address"]/text()')

        for field, class_ in {'rooms': 'views-label-field-rooms', 'size': 'views-label-field-net-area-1',
                              'cold_rent': 'views-label-field-net-rent'}.items():
            item.add_xpath(field, '//span[contains(@class, "{}")]/following-sibling::span/text()'.format(class_))

        item.add_xpath('warm_rent', '//div[contains(@class, "views-field-field-total-rent")]'
                                    '/child::span[@class="field-content"]/text()')
        item.add_xpath('description', '//div[contains(@class, field-name-field-description)]/div/div/p/text()')
        item.add_xpath('equipment', '//div[starts-with(normalize-space(.), "Ausstattung")]//div/text()')
        yield item.load_item()

    def clean_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean the item before loading."""
        self.clean_number(data, 'rooms')
        self.clean_number(data, 'size')
        return data
