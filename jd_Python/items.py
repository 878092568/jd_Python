# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdPythonItem(scrapy.Item):
    # define the fields for your item here like:
    sku=scrapy.Field()
    url=scrapy.Field()
    price = scrapy.Field()
    name=scrapy.Field()
    comments=scrapy.Field()
