# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class JdPythonPipeline(object):
    def process_item(self, item, spider):
        if item['name']==None:
            return item
        else:
            book_name=item['name'].strip()
            item['name']=book_name
            return item
