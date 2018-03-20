# -*- coding: utf-8 -*-
import scrapy
import urllib.parse
import re
import requests
import json
import time
import execjs
import math
import time
from user_agent import generate_user_agent
from scrapy.http.cookies import CookieJar 
import tabula

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


from SpiderHelp import SpiderHelp
from RedisHelp import _Request,_RedisSpider,logger

conn_flag = False
REDISFLAG = True
COOKIE = {"simu_qualified_v2": "5"}
from myselector import pdf_to_html

'''
redis数据库使用FOFI先进后出的规则 对url进行队列选择
'''

class SinaspiderSpider(_RedisSpider, SpiderHelp):  #,scrapy.Spider
    name = 'howbuy'
    start_urls = [
                'https://www.howbuy.com'
                  ]
    state = {}
    redis_flag=True
    redis_key = '%s:starturls' % name
    signel = 1
    host = '10.1.18.35'
    website_possible_httpstatus_list = [404, 502, 500, 504, 407]
    custom_settings = {
        # 'DOWNLOADER_MIDDLEWARES': 
        # {
        #     # 启用UA中间件
        #     # 'DistributedSpider.middlewares.RotateUserAgentMiddleware': 401,
        #     # 启用代理
        #     'DistributedSpider.middlewares.ProxyMiddleware': 700,
        # },
        # 最大并发
         'CONCURRENT_REQUESTS': 16,
        # 单ip最大并发
        # 'CONCURRENT_REQUESTS_PER_IP': 8,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        #下载延迟
        # 'DOWNLOAD_DELAY': 3,
        # 爬虫策略
        'DEPTH_PRIORITY': 1,
        # 允许的status
        'HTTPERROR_ALLOWED_CODES': [404, 502, 500, 504],
    }

    def __init__(self, _job=None,**kwargs):
        # 获取本爬虫redis_key
        super(SinaspiderSpider,self).__init__(**kwargs)

    def __str__(self): 
        return 'SinaspiderSpider'

    def post_data(self, page, response=None):
        lastpage = page-1 if page != 1 else ''
        string = 'pageIndex=%s&pageSize=18&insuranceTypeId=&insuranceCompanyId=&ageInterval=&productName=&order=0&desc=1&pageIndex=%s&pageSize=18&' % (page,lastpage)
        return string

    def start_requests(self):
        req = []
        logger.info('Start Crawl Spider %s at rediskey %s' % (self.name,self.redis_key))
        for url in self.start_urls:
            req.append(self.request(
                url,
                method='POST',
                body=self.post_data(1),
                redis_flag=REDISFLAG,
                headers=self.default_header,
                cookies=COOKIE,
                callback=self.howbuy_in))
        return req

    def howbuy_in(self, response):
        '''https://www.howbuy.com/fund/company/', # 公募公司
        'https://www.howbuy.com/fund/fundranking/', # 公募基金产品
        'https://www.howbuy.com/fund/manager/', # 公募基金经理
        'https://simu.howbuy.com/company/', # 私募基金公司
        'https://simu.howbuy.com/mlboard.htm', # 私募产品
        'https://simu.howbuy.com/manager/' # 私募基金经理'''
        yield scrapy.Request('https://www.howbuy.com/fund/company/',
            headers=self.default_header,
            cookies=COOKIE,
            callback=self.howbuy_public_fund_list)

    def howbuy_public_fund_list(self, response):
        pass