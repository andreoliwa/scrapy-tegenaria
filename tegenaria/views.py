"""Admin views."""
import re
from datetime import date
from typing import Any, Optional, Union

import arrow as arrow
from flask_admin.contrib.sqla import ModelView
from flask_admin.model import typefmt
from markupsafe import Markup
from sqlalchemy import func, lateral, true

from tegenaria.models import Apartment, Distance, Pin
from tegenaria.public.views import MAPS_PLACE_URL

FIELDS_REGEX = re.compile(r'{([^}]+)}')


def format_date(view, value):
    """Format a date for the list view."""
    return arrow.get(value).humanize()


MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
    date: format_date
})


def format_hyperlink(href: str = None, href_column: Union[str, Any] = None,
                     title: str = None, title_column: Union[str, Any] = None, target: Optional[str] = '_blank'):
    """Format as an HTML hyperlink.

    :param href:
        A URL string to use as href.
    :param href_column:
        A string column name, or a SQLAlchemy column, to use as href if the argument above is None.
    :param title:
        A string to use as the title of the <a> tag.
    :param title_column:
        A string column name, or a SQLAlchemy column, to use as title if the argument above is None.
    :param target:
        Target for the URL. Default: _blank.
    """
    def formatter(view, context, model, name):
        """Inner function to actually format as an HTML hyperlink.

        :param view:
            Current administrative view.
        :param context:
            Instance of jinja2.runtime.Context.
        :param model:
            Model instance.
        :param name:
            Property name.
        :return: <a> HTML tag.
        """
        def choose_between(the_string: str, the_column: Union[str, Any]):
            """Get value from the string or the column."""
            rv = None
            if the_string:
                fields_in_brackets = FIELDS_REGEX.findall(the_string)
                if fields_in_brackets:
                    # A literal string with fields inside brackets was provided (like a Python format string).
                    # Get the values from the model and...
                    values = {field: getattr(model, field) for field in fields_in_brackets}

                    # ... format the Python bracketed string.
                    rv = the_string.format(**values)
                else:
                    # A literal string was provided.
                    rv = the_string
            elif isinstance(the_column, str):
                # A column name was provided, as a string.
                rv = getattr(model, the_column)
            elif the_column is not None:
                # A column was provided, as a SQLAlchemy column.
                rv = getattr(model, the_column.name)
            if rv is None:
                # Get the own column value as the URL for the tag.
                rv = getattr(model, name)
            return rv

        return Markup('<a href="{url}"{target}>{title}</a>'.format(
            url=choose_between(href, href_column),
            title=choose_between(title, title_column),
            target=' target="{}"'.format(target) if target else ''
        ))

    return formatter


class ApartmentModelView(ModelView):
    """Custom model view for the apartment."""

    can_create = False
    can_delete = False
    can_view_details = True

    form_columns = ('url', 'active', 'title', 'address', 'neighborhood', 'rooms', 'size', 'cold_rent', 'warm_rent',
                    'warm_rent_notes', 'opinion', 'description', 'equipment', 'location', 'other', 'availability',
                    'comments', 'created_at', 'updated_at')

    column_list = ('title', 'address', 'neighborhood', 'rooms', 'size', 'cold_rent', 'warm_rent', 'updated_at',
                   'duration_text', 'distance_text')
    column_formatters = dict(
        title=format_hyperlink(href_column=Apartment.url),
        address=format_hyperlink(href=MAPS_PLACE_URL),
        duration_text=lambda view, context, model, name: context['row'].duration_text,
        distance_text=lambda view, context, model, name: context['row'].distance_text,
    )
    column_labels = dict(
        duration_text='Time to pin',
        distance_text='Distance to pin',
    )

    column_type_formatters = MY_DEFAULT_FORMATTERS
    column_searchable_list = ('url', 'address', 'neighborhood', 'comments', 'description', 'equipment', 'location',
                              'other')
    column_details_list = ('url', 'active', 'title', 'address', 'neighborhood', 'rooms', 'size', 'cold_rent',
                           'warm_rent', 'warm_rent_notes', 'opinion', 'description', 'equipment', 'location', 'other',
                           'availability', 'comments', 'created_at', 'updated_at', 'duration_text', 'distance_text')
    column_default_sort = ('warm_rent', False)
    column_filters = ('title', 'address', 'neighborhood', 'rooms', 'size', 'cold_rent', 'warm_rent', 'updated_at')

    details_modal = True
    edit_modal = True

    def get_query(self):
        """Return a query for apartments and their distances to pins."""
        lateral_pin = lateral(
            Pin.query.with_entities(Pin.id.label('id'), Pin.name.label('name'), Pin.address.label('address')),
            name='pin')
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
                  [lateral_distance.c.duration_text, lateral_distance.c.duration_value,
                   lateral_distance.c.distance_text, lateral_distance.c.distance_value]
        query = self.session.query(*columns)

        # All pins that might have a distance or not.
        return query.join(lateral_pin, true()).outerjoin(lateral_distance, true())

    def get_count_query(self):
        """Return the count query for the query above."""
        return self.get_query().with_entities(func.count('*'))
