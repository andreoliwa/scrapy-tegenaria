# -*- coding: utf-8 -*-
"""A spider to crawl the Immobilien Scout 24 website."""
import itertools
import re
from getpass import getpass
from typing import Any, Dict

import keyring
from imapclient import IMAPClient
from scrapy import Request, Spider
from scrapy.linkextractors import LinkExtractor
from w3lib.url import url_query_cleaner

from tegenaria.items import ApartmentItem, ApartmentLoader, clean_number
from tegenaria.spiders import SpiderMixin

IMAP_HOST = ''  # TODO: get this from .env json_config(__file__, 'imap_host')
IMAP_USERNAME = ''  # TODO: get this from .env json_config(__file__, 'imap_username')
IMAP_FOLDER = ''  # TODO: get this from .env json_config(__file__, 'imap_folder')
AD_URL_TEMPLATE = 'http://www.immobilienscout24.de/expose/{id}'
REGEX = re.compile(r'expose/([0-9]+)')


class ImmobilienScout24Spider(Spider, SpiderMixin):
    """A spider to crawl the Immobilien Scout 24 website."""

    name = 'immobilien_scout_24'
    allowed_domains = ['immobilienscout24.de']
    start_urls = (
        # TODO: get this from .env or from spider arguments
        'https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Fahrzeitsuche/Berlin/10178/228300/2512424'
        '/Alexanderstra_dfe/-/30/-3,00?enteredFrom=result_list',
    )
    searched_pages = set()

    CITY = ' Berlin'
    DIV_PRE_MAPPING = {
        'description': 'is24qa-objektbeschreibung',
        'equipment': 'is24qa-ausstattung',
        'location': 'is24qa-lage',
        'other': 'is24qa-sonstiges'
    }
    WARM_RENT_RE = re.compile(r'(?P<warm_rent_price>[0-9,.]+)[\s(]*(?P<comments>[^)]*)')
    DEACTIVATED = 'Angebot wurde deaktiviert'
    FULL_ADDRESS_TEXT = 'Die vollständige Adresse der Immobilie erhalten Sie vom Anbieter.'

    def start_requests(self):
        """Read e-mails (if any) and then crawl URLs."""
        # TODO: get this from .env or from spider arguments
        # self.start_urls = json_config(__file__, 'start_urls')
        return itertools.chain(
            self.read_emails(),
            super(ImmobilienScout24Spider, self).start_requests())

    def parse(self, response):
        """Parse a search results HTML page.

        @url https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Berlin/Berlin?enteredFrom=one_step_search
        @returns items 0 0
        @returns requests 21
        """
        # TODO These spiders should inherit from CrawlSpider, which already implements something like this.
        for link in LinkExtractor(allow='/Suche/S-T/P-').extract_links(response):
            if link.url not in (self.searched_pages, self.start_urls):
                self.searched_pages.add(link.url)
                yield Request(link.url, callback=self.parse)

        for link in LinkExtractor(allow=r'expose/[0-9]+$', process_value=url_query_cleaner).extract_links(response):
            yield Request(link.url, callback=self.parse_item)

    def parse_item(self, response):
        """Parse an ad page with an apartment.

        @url https://www.immobilienscout24.de/expose/93354819
        @returns items 1 1
        @scrapes url title address neighborhood cold_rent_price warm_rent_price rooms
        """
        self.shutdown_on_error()
        item = ApartmentLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_css('title', 'h1#expose-title::text')

        for field, css_class in self.DIV_PRE_MAPPING.items():
            item.add_xpath(field, "//div/pre[contains(@class, '{}')]/text()".format(css_class))

        full_address = ''.join(response.xpath("//span[@data-qa='is24-expose-address']/div//text()").extract()).strip()
        parts = full_address.split(self.CITY)
        if len(parts) == 1:
            item.add_value('address', full_address)
        else:
            street_zip = (parts[0] + self.CITY).strip(' ,').replace(' (zur Karte) ', '')
            item.add_value('address', street_zip)
            item.add_value('neighborhood', ''.join(parts[1:]).strip(' ,'))

        item.add_css('cold_rent_price', 'div.is24qa-kaltmiete::text')
        item.add_css('warm_rent_price', 'dd.is24qa-gesamtmiete::text')
        item.add_css('rooms', 'div.is24qa-zi::text')
        item.add_xpath('size', '//div[contains(@class, "is24qa-flaeche ")]/text()')
        item.add_xpath('active', '//div[contains(@class, "status-message")]'
                                 '/h3[starts-with(normalize-space(.), "Angebot")]/text()')
        yield item.load_item()

    def before_marshmallow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean the item before loading schema on Marshmallow."""
        # Warm rent can have additional notes to the right.
        if 'warm_rent_price' in data:
            match = self.WARM_RENT_RE.match(data['warm_rent_price'])
            if match:
                data.update(match.groupdict())
                data['warm_rent_price'] = clean_number(data['warm_rent_price'])

        # Join repeated neighbourhood names.
        if 'neighborhood' in data:
            data['neighborhood'] = data['neighborhood'].replace(self.FULL_ADDRESS_TEXT, '')
            data['neighborhood'] = ' '.join(set(re.split('\W+', data['neighborhood'].strip(' ()'))))

        if data.get('active') == self.DEACTIVATED:
            data['active'] = False

        return data

    def read_emails(self, ask_password=False):
        """Read email messages.

        :param ask_password: Force a prompt for the password.
        :return: Yield Scrapy requests.
        """
        self.logger.info('Reading emails')
        if not IMAP_HOST:
            self.logger.info('Empty host')
            return

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
                yield Request(url, callback=self.parse_item)


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
