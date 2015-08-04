# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from house_spider.items import HouseItem

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
        item = HouseItem()
        item['url'] = response.url
        item['id'] = int(''.join(response.css('div ul.is24-ex-id li::text').extract()).strip())
        item['title'] = ''.join(response.css('h1#expose-title::text').extract())

        full_address = ''.join(response.xpath("//span[@data-qa='is24-expose-address']/text()").extract()).strip()
        parts = full_address.split(CITY)
        if len(parts) == 1:
            item['address'] = full_address
        else:
            item['address'] = (parts[0] + CITY).strip(' ,')
            item['neighborhood'] = ''.join(parts[1:]).strip(' ,')

        item['cold_rent'] = ''.join(response.css('div.is24qa-kaltmiete::text').extract()).strip()
        item['warm_rent'] = ''.join(response.css('dd.is24qa-gesamtmiete::text').extract()).strip()
        yield item
