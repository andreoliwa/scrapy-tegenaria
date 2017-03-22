# -*- coding: utf-8 -*-
"""Forms of the application."""
from datetime import datetime, timedelta

from flask_wtf import Form
from sqlalchemy import Numeric
from wtforms import IntegerField, PasswordField, RadioField
from wtforms.fields.core import SelectField, StringField
from wtforms.validators import DataRequired

from tegenaria.models import Apartment
from tegenaria.user.models import User


class LoginForm(Form):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create an instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate login info."""
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(username=self.username.data).first()  # pylint: disable=no-member
        if not self.user:
            self.username.errors.append('Unknown username')
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        if not self.user.active:
            self.username.errors.append('User not activated')
            return False
        return True


class ApartmentSearchForm(Form):
    """Apartment search form."""

    SORT_TIME_TO_PIN = 'time'
    SORT_WARM_RENT = 'warm_rent'

    days = IntegerField('Last days')
    opinion = SelectField('Opinion', coerce=int)
    min_rooms = IntegerField('Min rooms')
    max_rooms = IntegerField('Max rooms')
    max_warm_rent = IntegerField('Max warm rent')
    max_time_to_pin = IntegerField('Max time to pin')
    preset_sort = RadioField('Sort options', choices=[
        (SORT_TIME_TO_PIN, 'Time to pin'),
        (SORT_WARM_RENT, 'Warm rent')])

    def apply_where_order_by(self, query, duration_value_column):
        """Apply WHERE filters and ORDER BY to the query."""
        for condition in (self.filter_last_days(), self.filter_opinion(), self.filter_min_rooms(),
                          self.filter_max_rooms(), self.filter_max_warm_rent(),
                          self.filter_max_time_to_pin(duration_value_column)):
            if condition is not None:
                query = query.filter(condition)
        for sort_columns in (self.order_by_time_or_rent(duration_value_column),):
            if sort_columns:
                query = query.order_by(*sort_columns)
        return query

    def order_by_time_or_rent(self, duration_value_column):
        """Order by time to pin or warm rent."""
        by_rent = [Apartment.warm_rent.cast(Numeric), Apartment.cold_rent.cast(Numeric)]
        if self.preset_sort.data == self.SORT_WARM_RENT:
            return by_rent
        return [duration_value_column.asc()] + by_rent

    def filter_last_days(self):
        """Filter ads from last N days."""
        if not self.days.data:
            return
        past_date = datetime.now() - timedelta(self.days.data)
        return Apartment.created_at >= past_date

    def filter_opinion(self):
        """Filter ads by opinion."""
        if self.opinion.data is None:
            return
        opinion_id = int(self.opinion.data)
        if opinion_id <= -1:
            return
        return Apartment.opinion_id == opinion_id if opinion_id else Apartment.opinion_id.is_(None)

    def filter_min_rooms(self):
        """Filter ads with a minimum room count."""
        if self.min_rooms.data is None:
            return
        return Apartment.rooms.cast(Numeric) >= self.min_rooms.data

    def filter_max_rooms(self):
        """Filter ads with a maximum room count."""
        if self.max_rooms.data is None:
            return
        return Apartment.rooms.cast(Numeric) <= self.max_rooms.data

    def filter_max_warm_rent(self):
        """Filter ads with a maximum war rent."""
        if self.max_warm_rent.data is None:
            return
        return Apartment.warm_rent.cast(Numeric) <= self.max_warm_rent.data

    def filter_max_time_to_pin(self, duration_value_column):
        """Filter ads with a maximum time to pin."""
        if self.max_time_to_pin.data is None:
            return
        seconds = self.max_time_to_pin.data * 60
        return duration_value_column <= seconds
