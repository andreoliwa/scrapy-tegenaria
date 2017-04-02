"""Admin views."""
from datetime import date

from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import FilterEmpty
from flask_admin.model import typefmt
from sqlalchemy import func, lateral, true

from tegenaria.generic import format_as_human_date, format_json_textarea, render_link, when_none
from tegenaria.models import Apartment, Distance, Pin

MAPS_PLACE_URL = 'https://www.google.de/maps/place/{address}/'
MAPS_DIRECTIONS_URL = 'https://www.google.de/maps/dir/{origin}/{destination}/'

MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
    date: format_as_human_date,
    dict: format_json_textarea
})


class PinModelView(ModelView):
    """Custom model view for pins."""

    can_create = False
    can_delete = False


class ApartmentModelView(ModelView):
    """Custom model view for the apartments, times and distances."""

    can_create = False
    can_delete = False
    can_view_details = True
    can_set_page_size = True

    form_columns = ('url', 'active', 'title', 'address', 'neighborhood', 'rooms', 'size', 'cold_rent', 'warm_rent',
                    'opinion', 'description', 'equipment', 'location', 'other', 'availability',
                    'comments', 'created_at', 'updated_at')

    column_list = ('title', 'address', 'neighborhood', 'rooms', 'size', 'cold_rent', 'warm_rent',
                   'updated_at', 'minutes', 'meters')
    column_labels = dict(
        minutes='Minutes to pin',
        meters='Meters to pin',
    )

    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.column_formatters
    column_formatters = dict(
        title=lambda v, c, m, n: render_link(m.url, m.title),
        address=lambda v, c, m, n: render_link(
            url=MAPS_PLACE_URL.format(address=m.address),
            text=m.address
        ),
        minutes=lambda v, c, m, n: render_link(
            url=MAPS_DIRECTIONS_URL.format(origin=m.address, destination=c['row'].pin_address),
            text=when_none(c['row'].minutes),
            title='from {} to {}'.format(m.address, c['row'].pin_address)
        ),
        meters=lambda v, c, m, n: render_link(
            url=MAPS_DIRECTIONS_URL.format(origin=m.address, destination=c['row'].pin_address),
            text=when_none(c['row'].meters),
            title='from {} to {}'.format(m.address, c['row'].pin_address)
        ),
    )

    column_type_formatters = MY_DEFAULT_FORMATTERS
    column_searchable_list = ('address', 'neighborhood', 'comments', 'description', 'equipment', 'location', 'other')
    column_details_list = ('url', 'title', 'errors', 'address', 'neighborhood', 'rooms', 'size', 'cold_rent',
                           'warm_rent', 'opinion', 'description', 'equipment', 'location', 'other', 'availability',
                           'comments', 'created_at', 'updated_at', 'json')
    column_default_sort = ('warm_rent', False)
    column_filters = ('url', 'active', 'title',
                      FilterEmpty(Apartment.errors, 'Errors'),
                      'address', 'neighborhood', 'rooms', 'size', 'cold_rent',
                      'warm_rent', 'updated_at', 'distances.minutes', 'distances.meters')

    details_modal = True
    edit_modal = True

    def get_query(self):
        """Return a query for apartments and their distances to pins."""
        lateral_pin = lateral(
            Pin.query.with_entities(Pin.id.label('id'), Pin.address.label('pin_address')), name='pin')
        lateral_distance = lateral(Distance.query.with_entities(
            Distance.minutes.label('minutes'), Distance.meters.label('meters')).filter(
            Distance.apartment_id == Apartment.id, Distance.pin_id == lateral_pin.c.id), name='distance')

        # We need all apartment columns expanded.
        # If the query has only `Apartment` plus the columns, this error is raised:
        # AttributeError: 'result' object has no attribute 'id'
        columns = [c for c in Apartment.__table__.columns] + \
                  [lateral_pin.c.pin_address, lateral_distance.c.minutes, lateral_distance.c.meters]
        query = self.session.query(*columns).filter(Apartment.active.is_(True))

        # All pins that might have a distance or not.
        return query.join(lateral_pin, true()).outerjoin(lateral_distance, true())

    def get_count_query(self):
        """Return the count query for the query above."""
        return self.get_query().with_entities(func.count('*'))
