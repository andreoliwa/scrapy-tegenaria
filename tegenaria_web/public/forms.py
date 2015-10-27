# -*- coding: utf-8 -*-
"""Forms of the application."""
from flask_wtf import Form
from wtforms import HiddenField, IntegerField, PasswordField
from wtforms.fields.core import SelectField, StringField
from wtforms.validators import DataRequired

from tegenaria_web.user.models import User


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

    days = IntegerField('Days')
    opinion = SelectField('Opinion', coerce=int)
    order_by = HiddenField()
