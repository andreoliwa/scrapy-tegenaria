# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
# pylint: disable=no-name-in-module,import-error
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required, login_user, logout_user
from flask_table import Col, Table
from sqlalchemy import Numeric
from sqlalchemy.orm import aliased

from tegenaria_web.extensions import db, login_manager
from tegenaria_web.models import Apartment, Distance, Pin
from tegenaria_web.public.forms import LoginForm
from tegenaria_web.user.forms import RegisterForm
from tegenaria_web.user.models import User
from tegenaria_web.utils import UrlCol, flash_errors

blueprint = Blueprint('public', __name__, static_folder="../static")  # pylint: disable=invalid-name


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

        title = Col('Title')
        url = UrlCol('URL')
        address = Col('Address')
        neighborhood = Col('Neighborhood')
        rooms = Col('Rooms')
        cold_rent = Col('Cold Rent')
        warm_rent = Col('Warm Rent')
        warm_rent_notes = Col('Notes')

        def sort_url(self, col_id, reverse=False):
            """Sort the table by clicking its headers."""
            pass

    # pylint: disable=no-member
    query = db.session.query(
        Apartment.title, Apartment.url, Apartment.address, Apartment.neighborhood, Apartment.rooms,
        Apartment.cold_rent, Apartment.warm_rent, Apartment.warm_rent_notes)
    for pin in Pin.query.all():
        duration_text_field = 'duration_text_{}'.format(pin.id)
        duration_value_field = 'duration_value_{}'.format(pin.id)

        ApartmentTable.add_column(duration_text_field, Col(pin.name))
        distance_alias = aliased(Distance)
        query = query.join(distance_alias, distance_alias.apartment_id == Apartment.id).add_columns(
            distance_alias.duration_text.label(duration_text_field),
            distance_alias.duration_value.label(duration_value_field),
        ).filter(distance_alias.pin_id == pin.id)
    query = query.filter(Apartment.active.is_(True))

    # TODO Sort by column headers
    if False:
        query = query.order_by(Apartment.warm_rent.cast(Numeric), Apartment.cold_rent.cast(Numeric))
    else:
        query = query.order_by('duration_value_2', 'duration_value_1')

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
