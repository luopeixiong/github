# -*- coding: utf-8 -*-
import scrapy


class SzseSpider(scrapy.Spider):
    name = "szse"
    allowed_domains = ["szse.cn"]
    start_urls = ['http://szse.cn/']

    def parse(self, response):
        pass
