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
import socket
import random

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
TODAY = time.strftime('%Y-%m-%d')
MAX = 2**15
from myselector import pdf_to_html


#redis数据库使用FOFI先进后出的规则 对url进行队列选择
class SinaspiderSpider(_RedisSpider, SpiderHelp):  #,scrapy.Spider
    name = 'csrc'
    start_urls = [
        'http://fund.csrc.gov.cn/web/login_do.login'
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

    @property
    def ctime(self):
        return '%.13s' % (time.time()*1000)

    def __str__(self): 
        return 'SinaspiderSpider'

    def start_requests(self):
        req = []
        logger.info('Start Crawl Spider %s at rediskey %s' % (self.name,self.redis_key))
        for url in self.start_urls:
            yield self.request(url,
                headers=self.default_header,
                redis_flag=True,
                callback=self.csrc_in)

    @SpiderHelp.check_response
    def csrc_in(self, response):
        # # 基金销售机构
        # for i in range(1, 10):
        #     url = 'http://fund.csrc.gov.cn/web/sales_show.organization?type=%s' % i
        #     yield self.request(url,
        #         headers=self.default_header,
        #         callback=self.csrc_fund_sales_agency)

        # # 基金托管人
        # yield self.request('http://fund.csrc.gov.cn/web/bank_show.organization',
        #     headers=self.default_header,
        #     callback=self.csrc_custodian)

        # # 基金管理人名录
        # yield self.request('http://fund.csrc.gov.cn/web/fund_company_show.organization',
        #     headers=self.default_header,
        #     callback=self.csrc_fund_manager)

        # 分级基金
        yield self.request('http://fund.csrc.gov.cn/web/classification_show.organization',
            headers=self.default_header,
            callback=self.csrc_classification_fund)
    
    @SpiderHelp.check_response
    def csrc_classification_fund(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//tr[@class="aa" or @class="dd"]',    
                't': 'xpath',
                'db': 'Csrc.Csrc_ClassificationFund',
                'keys': ['ClassificationFundCode'],
                'check': 'ClassificationFundCode',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '分级基金代码',
                    'En': 'ClassificationFundCode',
                    'v':
                    'string(./td[2])',
                    't': 'xpath_first'
                },{
                    'n': '分级基金名称',
                    'En': 'ClassificationFundName',
                    'v':
                    'string(./td[3])',
                    't': 'xpath_first'
                },{
                    'n': '主基金代码',
                    'En': 'MainFundCode',
                    'v':
                    'string(./td[4])',
                    't': 'xpath_first'
                },{
                    'n': '基金全称',
                    'En': 'FundFullName',
                    'v': 'string(./td[5])',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def csrc_fund_manager(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//tr[@class="aa" or @class="dd"]',    
                't': 'xpath',
                'db': 'Csrc.Csrc_FundManager',
                'keys': ['ManagerCode'],
                'check': 'ManagerCode',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '基金管理人代码',
                    'En': 'ManagerCode',
                    'v':
                    'string(./td[2])',
                    't': 'xpath_first'
                },{
                    'n': '基金管理人简称',
                    'En': 'ShortName',
                    'v':
                    'string(./td[3])',
                    't': 'xpath_first'
                },{
                    'n': '基金管理人全称',
                    'En': 'FullName',
                    'v':
                    'string(./td[4])',
                    't': 'xpath_first'
                },{
                    'n': '网站地址',
                    'En': 'WebSite',
                    'v': 'string(./td[5])',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def csrc_custodian(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//tr[@class="aa" or @class="dd"]',    
                't': 'xpath',
                'db': 'Csrc.Csrc_Custodian',
                'keys': ['CustodianCode'],
                'check': 'CustodianCode',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '托管人代码',
                    'En': 'CustodianCode',
                    'v':
                    'string(./td[2])',
                    't': 'xpath_first'
                },{
                    'n': '托管人名称',
                    'En': 'CustodianName',
                    'v':
                    'string(./td[3])',
                    't': 'xpath_first'
                },{
                    'n': '注册地域',
                    'En': 'RegistrationArea',
                    'v':
                    'string(./td[4])',
                    't': 'xpath_first'
                },{
                    'n': '取得托管资格时间',
                    'En': 'AccessToTrusteeship',
                    'v': 'string(./td[5])',
                    't': 'xpath_first'
                },{
                    'n': '地址',
                    'En': 'Address',
                    'v': 'string(./td[6])',
                    't': 'xpath_first'
                },
                {
                    'n': '电话',
                    'En': 'ContactNumber',
                    'v': 'string(./td[7])',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def csrc_fund_sales_agency(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//tr[@class="aa" or @class="dd"]',    
                't': 'xpath',
                'db': 'Csrc.Csrc_FuncSalseAgency',
                'keys': ['AgencyName','AgencyNature'],
                'check': 'AgencyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '机构名称',
                    'En': 'AgencyName',
                    'v':
                    'string(./td[2])',
                    't': 'xpath_first'
                },{
                    'n': '机构性质',
                    'En': 'AgencyNature',
                    'v':
                    '//td[@class="menuSubLinkOn_next"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '网址',
                    'En': 'WebSite',
                    'v':
                    'string(./td[3])',
                    't': 'xpath_first'
                },{
                    'n': '联系地址',
                    'En': 'ContactAddress',
                    'v': 'string(./td[4])',
                    't': 'xpath_first'
                },
                {
                    'n': '电话',
                    'En': 'ContactNumber',
                    'v': 'string(./td[5])',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
            # print(item)

def main():
    SinaspiderSpider.put_redis()

if __name__=='__main__':
    main()