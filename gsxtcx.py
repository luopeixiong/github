# -*- coding: utf-8 -*-
import scrapy


class GsxtcxSpider(scrapy.Spider):
    name = "gsxtcx"
    allowed_domains = ["gsxt.gov.cn"]
    start_urls = ['http://gsxt.gov.cn/']

    def parse(self, response):
        pass
