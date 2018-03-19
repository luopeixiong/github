# -*- coding: utf-8 -*-
import scrapy

import urllib.parse
from user_agent import generate_user_agent


def default_hebei_data(page,perpage=6):
    data =  {'page':str(page),
            'channelid':'260465',
            'orderby':'RELEVANCE',
            'perpage': str(perpage),  # 该参数可以自定义
            'outlinepage': '10',
            'searchscope':'',
            'timescope':'',
            'timescopecolumn':'',
            'orderby':'RELEVANCE',
            'andsen':'',
            'total':'',
            'orsen':'',
            'exclude':''}
    return urllib.parse.urlencode(data)

def default_headers(os=('win',),connect_type='json'):
    return {'User-Agent': generate_user_agent(os=os),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
           }

class CreditSpider(scrapy.Spider):
    name = "credit"
#    allowed_domains = ["credit.com"]
    start_urls = ['http://www.credithebei.gov.cn:8082/was5/web/search']
    
    def start_requests(self):
        for start_url in self.start_urls:
            page = 1
            if start_url == 'http://www.credithebei.gov.cn:8082/was5/web/search':
                params = '?' + default_hebei_data(page)
                start_url += params
                yield scrapy.Request(start_url,
                                     headers=default_headers())
    def parse(self, response):
        print(response.text)
