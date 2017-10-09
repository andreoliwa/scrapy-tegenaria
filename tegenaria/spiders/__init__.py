"""
This package will contain the spiders of your Scrapy project.

Please refer to the documentation for information on how to create and manage your spiders.
"""
from scrapy.exceptions import CloseSpider
from typing import Dict, Any


class SpiderMixin:
    """Mixin to clean data in spiders."""

    shutdown_message = None  # type: str

    def before_marshmallow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean the item before loading schema on Marshmallow."""
        return data

    def shutdown_on_error(self) -> None:
        """Shutdown the spider when an error occurs on the pipeline.

        Call this method while parsing (on parse_item), as the first thing.
        """
        if self.shutdown_message:
            raise CloseSpider(self.shutdown_message)
