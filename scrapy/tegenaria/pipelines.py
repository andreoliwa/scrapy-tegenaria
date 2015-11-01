# -*- coding: utf-8 -*-
"""
Define your item pipelines here.

Don't forget to add your pipeline to the ITEM_PIPELINES setting
See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
"""


class TegenariaPipeline(object):
    """An example of pipeline."""

    def process_item(self, item, spider):  # pylint: disable=no-self-use
        """Process an item through the pipeline."""
        assert spider
        return item
