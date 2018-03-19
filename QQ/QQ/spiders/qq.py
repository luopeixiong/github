# -*- coding: utf-8 -*-
import scrapy
from .myselector import Selector as S

class QqSpider(scrapy.Spider):
    name = "qq"
    allowed_domains = ["qq.com"]
    start_urls = ['http://qq.com/']

    def parse(self, response):
        pass
