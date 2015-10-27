# -*- coding: utf-8 -*-
"""A spider to crawl the Immobilien Scout 24 website."""
import itertools
import re
from getpass import getpass

import keyring

import scrapy
from imapclient import IMAPClient
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from tegenaria.items import ApartmentItem, json_config

IMAP_HOST = json_config(__file__, 'imap_host')
IMAP_USERNAME = json_config(__file__, 'imap_username')
IMAP_FOLDER = json_config(__file__, 'imap_folder')
AD_URL_TEMPLATE = 'http://www.immobilienscout24.de/expose/{id}'
REGEX = re.compile(r'expose/([0-9]+)')


class ImmobilienScout24Spider(scrapy.Spider):

    """A spider to crawl the Immobilien Scout 24 website."""

    name = "immobilien_scout_24"
    allowed_domains = ["immobilienscout24.de"]
    start_urls = (
        'http://www.immobilienscout24.de/',
    )
    searched_pages = set()

    CITY = ' Berlin'
    DIV_PRE_MAPPING = {
        'description': 'is24qa-objektbeschreibung',
        'equipment': 'is24qa-ausstattung',
        'location': 'is24qa-lage',
        'other': 'is24qa-sonstiges'
    }
    WARM_RENT_RE = re.compile(r'(?P<warm_rent>[0-9,.]+)[\s(]*(?P<warm_rent_notes>[^)]*)')

    def start_requests(self):
        """Read e-mails (if any) and then crawl URLs."""
        self.start_urls = json_config(__file__, 'start_urls')
        return itertools.chain(
            self.read_emails(),
            super(ImmobilienScout24Spider, self).start_requests())

    def parse(self, response):
        """Parse a search results HTML page."""
        # TODO These spiders should inherit from CrawlSpider, which already implements something like this.
        for link in LinkExtractor(allow='/Suche/S-T/P-').extract_links(response):
            if link.url not in (self.searched_pages, self.start_urls):
                self.searched_pages.add(link.url)
                yield scrapy.Request(link.url, callback=self.parse)

        for link in LinkExtractor(allow=r'expose/[0-9]+$').extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_item)

    def parse_item(self, response):
        """Parse an ad page, with an apartment."""
        item = ItemLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_css('title', 'h1#expose-title::text')

        for field, css_class in self.DIV_PRE_MAPPING.items():
            item.add_xpath(field, "//div/pre[contains(@class, '{}')]/text()".format(css_class))

        full_address = ''.join(response.xpath("//span[@data-qa='is24-expose-address']/div//text()").extract()).strip()
        parts = full_address.split(self.CITY)
        if len(parts) == 1:
            item.add_value('address', full_address)
        else:
            item.add_value('address', (parts[0] + self.CITY).strip(' ,'))
            item.add_value('neighborhood', ''.join(parts[1:]).strip(' ,'))

        item.add_css('cold_rent', 'div.is24qa-kaltmiete::text')
        item.add_css('warm_rent', 'dd.is24qa-gesamtmiete::text')
        item.add_css('rooms', 'div.is24qa-zi::text')
        item_dict = item.load_item()

        # Warm rent can have additional notes to the right.
        match = self.WARM_RENT_RE.match(item_dict['warm_rent'])
        if match:
            item_dict.update(match.groupdict())

        yield item_dict

    def read_emails(self, ask_password=False):
        """Read email messages.

        :param ask_password: Force a prompt for the password.
        :return: Yield Scrapy requests.
        """
        self.logger.info('Reading emails')
        password = keyring.get_password(IMAP_HOST, IMAP_USERNAME)
        if not password or ask_password:
            password = getpass(prompt='Type your email password: ')
        if not password:
            self.logger.error('Empty password.')
            return

        server = IMAPClient(IMAP_HOST, use_uid=True, ssl=True)
        server.login(IMAP_USERNAME, password)
        keyring.set_password(IMAP_HOST, IMAP_USERNAME, password)
        server.select_folder(IMAP_FOLDER)
        messages = server.search('UNSEEN')
        self.logger.info("%d unread messages in folder '%s'.", len(messages), IMAP_FOLDER)

        response = server.fetch(messages, ['BODY[TEXT]', 'RFC822.SIZE'])
        for msg_id, data in response.items():
            size = data[b'RFC822.SIZE']
            self.logger.info('Reading message ID %d (size %d).', msg_id, size)
            raw_body = data[b'BODY[TEXT]']
            try:
                body = raw_body.decode(imap_charset(raw_body))
            except LookupError as err:
                self.logger.error(err)
                body = ''
            for url in [AD_URL_TEMPLATE.format(id=ad_id) for ad_id in set(REGEX.findall(body))]:
                yield scrapy.Request(url, callback=self.parse_item)


def imap_charset(raw_body):
    """Find the charset from the body of a raw (bytes) email message.

    :param raw_body: Raw text, byte string.
    :return: Charset.

    :type raw_body: bytes
    :rtype: str
    """
    start = raw_body.find(b'charset')
    end = start + raw_body[start:].find(b'\r')
    charset = raw_body[start:end].split(b'=')[1].decode()
    if ';' in charset:
        charset = charset.split(';')[0]
    return charset
