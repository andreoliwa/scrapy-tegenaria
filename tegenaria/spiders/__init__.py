"""
This package will contain the spiders of your Scrapy project.

Please refer to the documentation for information on how to create and manage your spiders.
"""
from scrapy.exceptions import CloseSpider
from typing import Dict, Any


class CleanMixin:
    """Mixin to clean data in spiders."""

    shutdown_message = None  # type: str

    def clean_item(self, data: Dict[str, Any]):
        """Clean the item before loading.

        This method can be overridden in the inherited class.
        """
        return data

    def shutdown_on_error(self):
        """Shutdown the spider when an error occur. Call this method while parsing."""
        if self.shutdown_message:
            raise CloseSpider(self.shutdown_message)
