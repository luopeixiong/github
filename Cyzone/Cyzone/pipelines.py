# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pipeline import Pipeline

class CyzonePipeline(Pipeline):
    def __init__(self):
        Pipeline.__init__(self)
