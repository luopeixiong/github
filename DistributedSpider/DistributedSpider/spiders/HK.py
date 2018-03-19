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
_Compile = re.compile('Base64-AES-Encrypted-Token".*?"(.*?)"',re.S)
from myselector import pdf_to_html

'''
redis数据库使用FOFI先进后出的规则 对url进行队列选择
'''

class SinaspiderSpider(_RedisSpider , SpiderHelp):  #,scrapy.Spider
    name = 'HK'
    start_urls = [
                'http://www1.hkex.com.hk', #银行理财
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
        'DOWNLOAD_TIMEOUT': 1800,
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
            if url == 'http://www1.hkex.com.hk':
                req.append(self.request(
                    url,
                    redis_flag=REDISFLAG,
                    callback=self.HK_in))
        return req

    @SpiderHelp.check_response
    def HK_in(self, response):
        yield self.request(
            'https://www1.hkex.com.hk/hkexwidget/data/getequityfilter?lang=chn&token=evLtsLsBNAUVTPxtGqVeGxtmc9CEx4eNEM8C69B7seWQFwD3aod1XgLQpPi1614e&sort=5&order=0&all=1&qid=1516870569848',
            redis_flag=REDISFLAG,
                    callback=self.HK_stock_list)

    @SpiderHelp.check_response
    def HK_stock_list(self, response):
        JS = json.loads(response.text)
        for item in JS['data']['stocklist']:
            sym = item.get('sym')
            if sym:
                yield scrapy.Request(
                    'https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym={0}&sc_lang=zh-cn'.format(sym),
                    headers=self.default_header,
                    meta={'item': item},
                    callback=self.Hk_get_token)

    @SpiderHelp.check_response
    def Hk_get_token(self, response):
        token = _Compile.search(response.text).group(1)
        item = response.meta['item']
        url = 'https://www1.hkex.com.hk/hkexwidget/data/getequityquote?sym={0}&token={1}&lang=chn'.format(item['sym'], token)
        yield scrapy.Request(
            url,
            headers=self.default_header,
            priority=1000,
            callback=self.HK_stock_info)

    @SpiderHelp.check_response
    def HK_stock_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'json',
                'db': 'Hkex.Hkex_SrockClass',
                'keys': ['StockCode'],
                'check': 'StockCode',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '股票代码',
                    'En': 'StockCode',
                    'v':
                    'data/quote/sym',
                    't': 'json'
                },{
                    'n': '股票全称',
                    'En': 'StockFullName',
                    'v':
                    'data/quote/nm',
                    't': 'json'
                },{
                    'n': '股票名称',
                    'En': 'StockName',
                    'v':
                    'data/quote/nm_s',
                    't': 'json'
                },{
                    'n': '中证行业分类',
                    'En': 'CsicClass',
                    'v':
                    'data/quote/csic_classification',
                    't': 'json'
                },{
                    'n': '恒生行业分类',
                    'En': 'HsicClass',
                    'v':
                    'data/quote/hsic_ind_classification',
                    't': 'json'
                },{
                    'n': '恒生行业分类_子类',
                    'En': 'HsicSubClass',
                    'v':
                    'data/quote/hsic_sub_sector_classification',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            print(item)
            _item = item.copy()
            _item['result']['StockCode'] = '{0:{1}>5}'.format(_item['result']['StockCode'],'0')
            yield _item

def main():
    SinaspiderSpider.put_redis()

if __name__=='__main__':
    main()
