# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
import logging
import os
from datetime import date, datetime, timedelta

import requests
from flask import flash, json
from googlemaps import Client
from googlemaps.exceptions import HTTPError
from sqlalchemy import and_, or_

from tegenaria.extensions import db
from tegenaria.generic import read_from_keyring
from tegenaria.models import Apartment, Distance, Pin

PROJECT_NAME = 'tegenaria'
LOGGER = logging.getLogger(__name__)


def flash_errors(form, category='warning'):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash('{0} - {1}'
                  .format(getattr(form, field).label.text, error), category)


def remove_inactive_apartments():
    """Remove 404 links."""
    LOGGER.warning('Searching not found (404) among active records that were not updated in the last 24h')
    last_24h = datetime.now() - timedelta(days=1)
    for record in Apartment.query.filter_by(active=True).filter(Apartment.updated_at <= last_24h).all():
        response = requests.head(record.url)
        if response.status_code == requests.codes.NOT_FOUND:
            LOGGER.warning('Not found: %s', record.url)
            record.update(active=False)
        else:
            LOGGER.warning('Still active: %s', record.url)


def reprocess_invalid_apartments(output_dir):
    """Generate a text file with invalid apartments, so they can be reprocessed by Scrapy on the next run."""
    os.makedirs(output_dir, exist_ok=True)
    LOGGER.warning('Searching active apartments with empty addresses')
    query = db.session.query(Apartment.url).filter_by(active=True).filter(
        or_(Apartment.address == '', Apartment.rooms == ''))
    with open(os.path.join(output_dir, 'invalid.txt'), 'w') as handle:
        handle.writelines(['{}\n'.format(record.url) for record in query.all()])


def calculate_distance():
    """Calculate the distance for all apartments that were not calculated yet.

    - Query all pins;
    - Query all apartments not yet calculated;
    - Call Google Maps Distance Matrix;
    - Save the results.
    """
    maps = Client(key=read_from_keyring(PROJECT_NAME, 'google_maps_api_key'))
    assert maps
    tomorrow = date.today() + timedelta(0 if datetime.now().hour < 9 else 1)
    morning = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0)
    LOGGER.warning('Next morning: %s', morning)

    empty = dict(text='ERROR', value=-1)
    for pin in Pin.query.all():
        while True:
            apartments = Apartment.query.outerjoin(Distance, and_(
                Apartment.id == Distance.apartment_id, Distance.pin_id == pin.id)) \
                .filter(Apartment.active.is_(True), Distance.apartment_id.is_(None)).limit(20)
            search = {apartment.id: apartment.address for apartment in apartments.all()}
            if not search:
                LOGGER.warning('All distances already calculated for %s', pin)
                break

            ids = list(search.keys())
            origin_addresses = list(search.values())
            LOGGER.warning('Calling Google Maps for %s', pin)
            try:
                result = maps.distance_matrix(
                    origin_addresses, [pin.address], mode='transit', units='metric', arrival_time=morning)
            except HTTPError as err:
                LOGGER.error('Error on Google Distance Matrix: %s', str(err))
                continue
            LOGGER.warning('Processing results from Google Maps for %s', pin)
            for row_dict in [row['elements'][0] for row in result['rows']]:
                duration, distance = row_dict.get('duration', empty), row_dict.get('distance', empty)
                meters = distance.get('value')
                apt_id = ids.pop(0)
                model = Distance.create(apartment_id=apt_id, pin_id=pin.id, json=row_dict, meters=meters,
                                        minutes=round(duration.get('value') / 60))
                if meters <= 0:
                    LOGGER.error('Error calculating %s: %s', model, json.dumps(row_dict))
                else:
                    LOGGER.warning('Calculating %s', model)
