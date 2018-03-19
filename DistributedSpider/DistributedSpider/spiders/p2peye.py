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
TODAY = time.strftime('%Y-%m-%d')
Headers = {'User-Agent': generate_user_agent(os=('win',))}
Cookies = {'.ASPXANONYMOUS':'pdtC5gfC0wEkAAAAOWIzZDNiMGEtYjUzOS00YzYyLWEyZTctNWM2OTdmOGM2ZDcz0'}
from myselector import pdf_to_html

'''
redis数据库使用FOFI先进后出的规则 对url进行队列选择
'''

class SinaspiderSpider(_RedisSpider, SpiderHelp):  #,scrapy.Spider
    name = 'p2peye'
    start_urls = [
                'http://www.p2peye.com/platform/all/p1/', #网贷天眼
                  ]
    state = {}
    redis_flag=True
    redis_key = '%s:starturls' % name
    signel = 1
    host = '10.1.18.35'
    website_possible_httpstatus_list = [404, 502, 500, 504, 407]
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': 
        {
            # 启用UA中间件
            # 'DistributedSpider.middlewares.RotateUserAgentMiddleware': 401,
            # 启用代理
            'DistributedSpider.middlewares.ProxyMiddleware': 700,
        },
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

    def _start_requests(self):
        req = []
        logger.info('Start Crawl Spider %s at rediskey %s' % (self.name,self.redis_key))
        for url in self.start_urls:
            if url == 'http://www.p2peye.com/platform/all/p1/':
                req.append(self.request(
                    url,
                    redis_flag=REDISFLAG,
                    callback=self.p2peye_list))
        return req

    @SpiderHelp.check_response
    def p2peye_list(self, response):
        # 新浪 期货列表
        # logger.error(response)
        reqs = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//li[@class="ui-result-item"]//a[@class="ui-result-pname"]/@href',
                                                   },
                                           callback=self.p2peye_company,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//div[@class="ui-total-num"]/strong/text()'
                        },
                callback=self.p2peye_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://www.p2peye.com/platform/all/p%s/' % page,
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

    def p2peye_company(self, response):
        # 新浪 期货信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="table-futures-basic-data"]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_FuturesBasic',
                'keys': ['Code'],
                'check': 'Code',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'quotes/(.+)\.shtml',
                    't': 'url_re'
                },{
                    'n': '平台名称',
                    'En': 'Code',
                    'v':
                    '//span[@class="code"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '状态标签',
                    'En': 'FuritersName',
                    'v':
                    '//div[@class="tags"]/*[1]/div[@class="tag_icon"]/following-sibling::text()',
                    't': 'xpath_first'
                },
                {
                    'n': '状态标签2',
                    'En': 'ETradingVariety',
                    'v':
                    '//div[@class="tags"]/*[2]//text()[last()]',
                    't': 'xpath_first',
                },
                {
                    'n': '交易单位',
                    'En': 'TradingUnit',
                    'v':
                    './/*[contains(text(),"交易单位")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '报价单位',
                    'En': 'QuotationUnit',
                    'v':
                    './/*[contains(text(),"报价单位")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最小变动价位',
                    'En': 'MinimumPriceChange',
                    'v':
                    './/*[contains(text(),"最小变动价位")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '涨跌停板幅度',
                    'En': 'PriceLimits',
                    'v':
                    './/*[contains(text(),"涨跌停板幅度")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '合约交割月份',
                    'En': 'ContractMonth',
                    'v':
                    './/*[contains(text(),"合约交割月份")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易时间',
                    'En': 'TradingTime',
                    'v':
                    './/*[contains(text(),"交易时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最后交易日',
                    'En': 'LastTradingDate',
                    'v':
                    './/*[contains(text(),"最后交易日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最后交割日',
                    'En': 'FinalDeliveryDate',
                    'v':
                    './/*[contains(text(),"最后交割日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交割品级',
                    'En': 'DeliveryGrade',
                    'v':
                    './/*[contains(text(),"交割品级")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最低交易保证金',
                    'En': 'MinimumTransactionMargin',
                    'v':
                    './/*[contains(text(),"最低交易保证金")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易手续费',
                    'En': 'TransactionFee',
                    'v':
                    './/*[contains(text(),"交易手续费")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交割方式',
                    'En': 'DeliveryMethods',
                    'v':
                    './/*[contains(text(),"交割方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易代码',
                    'En': 'TransactionCode',
                    'v':
                    './/*[contains(text(),"交易代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市交易所',
                    'En': 'StockExchange',
                    'v':
                    './/*[contains(text(),"上市交易所")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

def main():
    SinaspiderSpider.put_redis()

if __name__=='__main__':
    main()