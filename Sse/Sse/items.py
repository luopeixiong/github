# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SseItem(scrapy.Item):
    # define the fields for your item here like:
    result = scrapy.Field()
    db = scrapy.Field()
    keys = scrapy.Field()
    pass
