# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
# pylint: disable=no-name-in-module,import-error
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required, login_user, logout_user
from sqlalchemy import Numeric
from sqlalchemy.orm import aliased

from tegenaria_web.extensions import db, login_manager
from tegenaria_web.flask_table_ex import Col, Table
from tegenaria_web.models import Apartment, Distance, Pin
from tegenaria_web.public.forms import LoginForm
from tegenaria_web.user.forms import RegisterForm
from tegenaria_web.user.models import User
from tegenaria_web.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder="../static")  # pylint: disable=invalid-name
MAPS_PLACE_URL = 'https://www.google.de/maps/place/{address}/'
MAPS_DIRECTIONS_URL = 'https://www.google.de/maps/dir/{origin}/{destination}/'


@login_manager.user_loader
def load_user(id):  # pylint: disable=redefined-builtin
    """Load user by ID."""
    return User.get_by_id(int(id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", 'success')
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout page."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route("/register/", methods=['GET', 'POST'])
def register():
    """Register user page."""
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        User.create(username=form.username.data, email=form.email.data,
                    password=form.password.data, active=True)
        flash("Thank you for registering. You can now log in.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)


@blueprint.route("/apartments/")
def apartments():
    """List all apartments."""
    class ApartmentTable(Table):

        """An HTML table for the apartments."""

        classes = ['table-bordered', 'table-striped']
        allow_sort = True

        title = Col(
            'Title',
            cell=lambda row, col, value: '<a href="{}" target="_blank">{}</a>'.format(row.url, value))
        address = Col(
            'Address',
            cell=lambda row, col, value: '<a href="{href}" target="_blank">{text}</a>'.format(
                href=MAPS_PLACE_URL.format(address=value.replace(' ', '+')), text=value))
        neighborhood = Col('Neighborhood')
        rooms = Col('Rooms')
        cold_rent = Col('Cold Rent')
        warm_rent = Col('Warm Rent', allow_sort=True)
        warm_rent_notes = Col('Notes')

        def sort_url(self, col_key, reverse=False):
            """Sort the table by clicking its headers."""
            return url_for('public.apartments', sort=col_key, direction='desc' if reverse else 'asc')

    # pylint: disable=no-member
    query = db.session.query(
        Apartment.title, Apartment.url, Apartment.address, Apartment.neighborhood, Apartment.rooms,
        Apartment.cold_rent, Apartment.warm_rent, Apartment.warm_rent_notes)

    for pin in Pin.query.all():
        pin_address_field = 'pin_address_{}'.format(pin.id)

        duration_text_field = 'duration_text_{}'.format(pin.id)
        duration_value_field = 'duration_value_{}'.format(pin.id)
        ApartmentTable.add_column(duration_text_field, Col('Time to {}'.format(pin.name), allow_sort=True))

        def show_directions(row, col, value):
            """Show the Google Maps link with directions from the address to the pin."""
            pin_address = getattr(row, 'pin_address_' + col.field.split('_')[-1])
            return '<a href="{href}" target="_blank">{text}</a>'.format(
                href=MAPS_DIRECTIONS_URL.format(
                    origin=row.address.replace(' ', '+'),
                    destination=pin_address.replace(' ', '+')),
                text=value)

        distance_text_field = 'distance_text_{}'.format(pin.id)
        distance_value_field = 'distance_value_{}'.format(pin.id)
        ApartmentTable.add_column(distance_text_field,
                                  Col('Distance to {}'.format(pin.name), cell=show_directions))

        distance_alias = aliased(Distance)
        pin_alias = aliased(Pin)
        query = query.join(
            distance_alias, Apartment.id == distance_alias.apartment_id
        ).join(
            pin_alias, distance_alias.pin_id == pin_alias.id
        ).add_columns(
            distance_alias.duration_text.label(duration_text_field),
            distance_alias.duration_value.label(duration_value_field),
            distance_alias.distance_text.label(distance_text_field),
            distance_alias.distance_value.label(distance_value_field),
            pin_alias.address.label(pin_address_field)
        ).filter(distance_alias.pin_id == pin.id)
    query = query.filter(Apartment.active.is_(True))

    sort = request.args.get('sort', 'warm_rent')
    """:type: str"""
    direction = request.args.get('direction', 'asc')

    if sort.startswith('duration_text'):
        query = query.order_by('duration_value_{} {}'.format(sort.split('_')[-1], direction))
    elif sort == 'warm_rent':
        query = query.order_by(Apartment.warm_rent.cast(Numeric), Apartment.cold_rent.cast(Numeric))

    table = ApartmentTable(query.all())
    return render_template("public/apartments.html", table=table)


@blueprint.route("/pins/")
def pins():
    """List all pins."""
    class PinTable(Table):

        """An HTML table for the pins."""

        name = Col('Name')
        address = Col('Address')

        def sort_url(self, col_id, reverse=False):
            """Sort the table by clicking its headers."""
            pass

    # pylint: disable=no-member
    items = Pin.query.all()
    table = PinTable(items, classes=['table-bordered', 'table-striped'])
    return render_template("public/pins.html", table=table)
