"""Marshmallow schemas."""
from marshmallow.decorators import pre_load
from marshmallow_sqlalchemy import ModelSchema
from scrapy import Spider  # noqa

from tegenaria.extensions import db
from tegenaria.models import Apartment


class ApartmentSchema(ModelSchema):
    """Schema to represent an apartment."""

    class Meta:
        """Schema config."""

        model = Apartment
        sqla_session = db.session

    @pre_load
    def clean_item(self, in_data):
        """Clean an item before loading."""
        spider = self.context['spider']  # type: Spider
        return spider.clean_item(in_data)
