# -*- coding: utf-8 -*-
import scrapy
from house_spider.items import HouseSpiderItem

CITY = ' Berlin,'


class ImmobilienScout24Spider(scrapy.Spider):
    name = "immobilien_scout_24"
    allowed_domains = ["immobilienscout24.de"]
    start_urls = (
        'http://www.immobilienscout24.de/',
    )

    def parse(self, response):
        item = HouseSpiderItem()
        item['title'] = response.css('h1#expose-title::text').extract()

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
