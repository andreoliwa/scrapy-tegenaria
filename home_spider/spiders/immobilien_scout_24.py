# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from home_spider.items import HomeItem, json_config

CITY = ' Berlin,'


class ImmobilienScout24Spider(scrapy.Spider):
    name = "immobilien_scout_24"
    allowed_domains = ["immobilienscout24.de"]
    start_urls = (
        'http://www.immobilienscout24.de/',
    )

    def parse(self, response):
        for link in LinkExtractor(allow=r'expose/[0-9]+$').extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_item)

    def parse_item(self, response):
        item = ItemLoader(HomeItem(), response=response)
        item.add_value('url', response.url)
        item.add_xpath('id', "//div/ul[contains(@class, 'is24-ex-id')]/li[1]/text()")
        item.add_css('title', 'h1#expose-title::text')

        full_address = ''.join(response.xpath("//span[@data-qa='is24-expose-address']/text()").extract()).strip()
        parts = full_address.split(CITY)
        if len(parts) == 1:
            item.add_value('address', full_address)
        else:
            item.add_value('address', (parts[0] + CITY).strip(' ,'))
            item.add_value('neighborhood', ''.join(parts[1:]).strip(' ,'))

        item.add_css('cold_rent', 'div.is24qa-kaltmiete::text')
        item.add_css('warm_rent', 'dd.is24qa-gesamtmiete::text')
        yield item.load_item()

ImmobilienScout24Spider.start_urls = json_config(__file__, 'start_urls')
