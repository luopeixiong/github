# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .pipe import sqlserver,HowbuyMangerPipeline
import pymssql

class AmacProductPipeline(HowbuyMangerPipeline,sqlserver):
    def __init__(self):
        HowbuyMangerPipeline.__init__(self)
        host = "10.1.12.16\HFDATA"
        db = "Haifeng.CrawlerData"
        user = "luopx"
        passwd = "Hf.123"
        self.conn = pymssql.connect(host=host, database=db, user=user, password=passwd, charset="utf8")
        self.cursor = self.conn.cursor()
        self.conn.autocommit(True)
        self.conn1 = pymssql.connect(host=host, database=db, user=user, password=passwd, charset="utf8")
        self.cursor1 = self.conn1.cursor()