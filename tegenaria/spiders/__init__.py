"""
This package will contain the spiders of your Scrapy project.

Please refer to the documentation for information on how to create and manage your spiders.
"""


class CleanMixin:
    """Mixin to clean data in spiders."""

    def clean_item(self, in_data):
        """Clean an item before loading.

        This method can be overridden in the inherited class.
        """
        return in_data
