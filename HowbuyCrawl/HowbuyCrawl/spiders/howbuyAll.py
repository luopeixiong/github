# -*- coding: utf-8 -*-
import scrapy


class HowbuyallSpider(scrapy.Spider):
    name = "howbuyAll"
    allowed_domains = ["howbuy.com"]
    start_urls = ['http://howbuy.com/']

    def parse(self, response):
        pass
