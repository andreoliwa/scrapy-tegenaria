"""
This package will contain the spiders of your Scrapy project.

Please refer to the documentation for information on how to create and manage your spiders.
"""
import re

from scrapy.exceptions import CloseSpider
from typing import Dict, Any, Optional


class CleanMixin:
    """Mixin to clean data in spiders."""

    shutdown_message = None  # type: str

    DIGIT_ONLY_REGEX = re.compile(r'[\d,.]+')

    def clean_item(self, data: Dict[str, Any]):
        """Clean the item before loading.

        This method can be overridden in the inherited class.
        """
        return data

    def clean_number(self, data: Dict[str, Any], key: str, separator: Optional[str]=','):
        """Clean a numeric value from the dictionary."""
        if key not in data:
            return None

        values = self.DIGIT_ONLY_REGEX.findall(data[key])
        clean_value = ''.join(values)
        if separator == ',':
            clean_value = clean_value.replace('.', '').replace(',', '.')
        elif separator == '.':
            clean_value = clean_value.replace(',', '')
        data[key] = clean_value
        return clean_value

    def shutdown_on_error(self):
        """Shutdown the spider when an error occur. Call this method while parsing."""
        if self.shutdown_message:
            raise CloseSpider(self.shutdown_message)
