"""Admin views."""
from datetime import date

from flask_admin.contrib.sqla import ModelView
from flask_admin.model import typefmt
from sqlalchemy import func, lateral, true

from tegenaria.generic import format_as_human_date, render_link, when_none
from tegenaria.models import Apartment, Distance, Pin
from tegenaria.public.views import MAPS_DIRECTIONS_URL, MAPS_PLACE_URL

MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
    date: format_as_human_date
})


class ApartmentModelView(ModelView):
    """Custom model view for the apartments, times and distances."""

    can_create = False
    can_delete = False
    can_view_details = True

    form_columns = ('url', 'active', 'title', 'address', 'neighborhood', 'rooms', 'size', 'cold_rent', 'warm_rent',
                    'warm_rent_notes', 'opinion', 'description', 'equipment', 'location', 'other', 'availability',
                    'comments', 'created_at', 'updated_at')

    column_list = ('title', 'address', 'neighborhood', 'rooms', 'size', 'cold_rent', 'warm_rent',
                   'updated_at', 'duration_text', 'distance_text')
    column_labels = dict(
        duration_text='Time to pin',
        distance_text='Distance to pin',
    )

    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.column_formatters
    column_formatters = dict(
        title=lambda v, c, m, n: render_link(m.url, m.title),
        address=lambda v, c, m, n: render_link(
            url=MAPS_PLACE_URL.format(address=m.address),
            text=m.address
        ),
        duration_text=lambda v, c, m, n: render_link(
            url=MAPS_DIRECTIONS_URL.format(origin=m.address, destination=c['row'].pin_address),
            text=when_none(c['row'].duration_text),
            title='from {} to {}'.format(m.address, c['row'].pin_address)
        ),
        distance_text=lambda v, c, m, n: render_link(
            url=MAPS_DIRECTIONS_URL.format(origin=m.address, destination=c['row'].pin_address),
            text=when_none(c['row'].distance_text),
            title='from {} to {}'.format(m.address, c['row'].pin_address)
        ),
    )

    column_type_formatters = MY_DEFAULT_FORMATTERS
    column_searchable_list = ('url', 'address', 'neighborhood', 'comments', 'description', 'equipment', 'location',
                              'other')
    column_details_list = ('title', 'address', 'neighborhood', 'rooms', 'size', 'cold_rent',
                           'warm_rent', 'warm_rent_notes', 'opinion', 'description', 'equipment', 'location', 'other',
                           'availability', 'comments', 'created_at', 'updated_at')
    column_default_sort = ('warm_rent', False)
    column_filters = ('active', 'title', 'address', 'neighborhood', 'rooms', 'size', 'cold_rent', 'warm_rent',
                      'updated_at')

    details_modal = True
    edit_modal = True

    def get_query(self):
        """Return a query for apartments and their distances to pins."""
        lateral_pin = lateral(
            Pin.query.with_entities(Pin.id.label('id'), Pin.address.label('pin_address')), name='pin')
        lateral_distance = lateral(Distance.query.with_entities(
            Distance.duration_text.label('duration_text'),
            Distance.duration_value.label('duration_value'),
            Distance.distance_text.label('distance_text'),
            Distance.distance_value.label('distance_value')).filter(
            Distance.apartment_id == Apartment.id, Distance.pin_id == lateral_pin.c.id), name='distance')

        # We need all apartment columns expanded.
        # If the query has only `Apartment` plus the columns, this error is raised:
        # AttributeError: 'result' object has no attribute 'id'
        columns = [c for c in Apartment.__table__.columns] + \
                  [lateral_pin.c.pin_address,
                   lateral_distance.c.duration_text, lateral_distance.c.duration_value,
                   lateral_distance.c.distance_text, lateral_distance.c.distance_value]
        query = self.session.query(*columns).filter(Apartment.active.is_(True))

        # All pins that might have a distance or not.
        return query.join(lateral_pin, true()).outerjoin(lateral_distance, true())

    def get_count_query(self):
        """Return the count query for the query above."""
        return self.get_query().with_entities(func.count('*'))
