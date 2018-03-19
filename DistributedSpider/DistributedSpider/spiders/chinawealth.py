# -*- coding: utf-8 -*-
'''
-beta 1.1
-为理财网 增加了cookie获取数据
-增加了代理池 -- 默认50个
'''
import scrapy
import urllib.parse
import re
import requests
import json
import time
import execjs
import json
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
Headers = {'User-Agent': generate_user_agent(os=('win',))}
Cookies = {'.ASPXANONYMOUS':'pdtC5gfC0wEkAAAAOWIzZDNiMGEtYjUzOS00YzYyLWEyZTctNWM2OTdmOGM2ZDcz0'}
from myselector import pdf_to_html




def cookies_pool(n:int):
    CookiesPool = []
    url = 'https://www.chinawealth.com.cn/zzlc/jsp/lccp.jsp'
    for i in range(n):
        cookies = cookies_get(url)
        if cookies:CookiesPool.append(cookies)
    return CookiesPool

def cookies_get(url):
    res = requests.get(url)
    return res.cookies.get_dict()

'''
redis数据库使用FOFI先进后出的规则 对url进行队列选择
'''

class ChinaSpider(_RedisSpider , SpiderHelp):  #,scrapy.Spider
    name = 'chinawealth1'
    start_urls = [
                'https://www.chinawealth.com.cn/zzlc/jsp/lccp.jsp', #银行理财
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
        super(ChinaSpider,self).__init__(**kwargs)

    def __str__(self): 
        return 'ChinaSpider'

    def Cookies(self):
        self.CookiesPool = cookies_pool(50)

    @property
    def cookies(self):
        if not hasattr(self,'CookiesPool'):
            self.Cookies()
        return random.choice(self.CookiesPool)

    @property
    def default_header(self):
        return {'Referer': 'https://www.chinawealth.com.cn/zzlc/jsp/lccp.jsp',
                'User-Agent': generate_user_agent(os=('mac',)),
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

    def _start_requests(self):
        req = []
        logger.info('Start Crawl Spider %s at rediskey %s' % (self.name,self.redis_key))
        for url in self.start_urls:
            if url == 'https://www.chinawealth.com.cn/zzlc/jsp/lccp.jsp':
                req.append(self.request(
                    url,
                    redis_flag=REDISFLAG,
                    cookies=self.cookies,
                    # meta={'proxys': True},
                    callback=self.chinawealth_jumps))
        return req

    @SpiderHelp.check_response
    def chinawealth_jumps(self, response):
        url = 'https://www.chinawealth.com.cn/lccpAllProJzyServlet.go'
        for index in ['01','02','03','04']:
            body = urllib.parse.urlencode({'tzzlxdm':index,
                    'cpdjbm':' ' ,
                    'cpmc':'',
                    'pagenum':'1',
                    'orderby':'desc_cpdjbm',   #'desc_cpdjbm',
                    'code':'',
                    })
            yield self.request(
                        url,
                        method='POST',
                        body=body,
                        meta={'index': index},#'proxys': True},
                        redis_flag=REDISFLAG,
                        priority=2000,
                        cookies=self.cookies,
                        callback=self.chinawealth_list)

    @SpiderHelp.check_response
    def chinawealth_list(self, response):
        # 中国理财网
        
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'Count'
                        },
                callback=self.chinawealth_list,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: 'https://www.chinawealth.com.cn/lccpAllProJzyServlet.go',
                bodyfunc=self.get_lxdm,
                redis_conn=self.r,
                divmod=500,
                redis_flag=True,
                cookies=self.cookies,
                readpage=128,
                response_type='json')
        for req in reqs:
            yield req

        reqs = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'List/cpid',
                                                   },
                                           callback=self.chinawealth_sales_area,
                                           headers=self.default_header,
                                           method='POST',
                                           priority=1999,
                                           urlfunc=
                                           lambda page, response: 'https://www.chinawealth.com.cn/cpxsqyQuery.go',
                                           bodyfunc=self.get_xsqy,
                                           errback=self.errbackparse,
                                           cookies=self.cookies,
                                           response_type='json')
        for req in reqs:
            yield req

        _configs = [{
            'list': {
                'n': '',
                'v': 'List',    
                't': 'json',
                'db': 'Chinawealth.ChinawealthProd',
                'keys': ['InvestorType', 'ProdID'],
                'check': 'HTML_ID',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '产品登记编码',
                    'En': 'HTML_ID',
                    'v':
                    'cpdjbm',
                    't': 'json'
                },{
                    'n': '产品名称',
                    'En': 'ProdName',
                    'v':
                    'cpms',
                    't': 'json'
                },{
                    'n': '产品代码',
                    'En': 'ProdCode',
                    'v':
                    'cpdm',
                    't': 'json'
                },{
                    'n': '产品类型',
                    'En': 'ProdType',
                    'v':
                    'cplxms',
                    't': 'json'
                },{
                    'n': '投资者类型',
                    'En': 'InvestorType',
                    'v':
                    'tzzlxms',
                    't': 'json'
                },
                {
                    'n': '产品状态',
                    'En': 'ProductStatus',
                    'v':
                    'cpztms',
                    't': 'json'
                },
                {
                    'n': '产品运作模式',
                    'En': 'ProdOperationMode',
                    'v':
                    'cpyzmsms',
                    't': 'json'
                },
                {
                    'n': '起始销售金额',
                    'En': 'InitialSalesAmount',
                    'v':
                    'qdxsje',
                    't': 'json'
                },
                {
                    'n': '募集起始日期',
                    'En': 'RaiseStartDate',
                    'v':
                    'mjqsrq',
                    't': 'json'
                },
                {
                    'n': '产品起始日期',
                    'En': 'ProdStartDate',
                    'v':
                    'cpqsrq',
                    't': 'json'
                },
                {
                    'n': '初始净值',
                    'En': 'InitialNetValue',
                    'v':
                    'csjz',
                    't': 'json'
                },
                {
                    'n': '本期净值',
                    'En': 'ThisPeriodNetValue',
                    'v':
                    'bqjz',
                    't': 'json'
                },
                {
                    'n': '预期最低收益率%',
                    'En': 'ExpectedLowestYields',
                    'v':
                    'yjkhzdnsyl',
                    't': 'json'
                },
                {
                    'n': '产品期限',
                    'En': 'ProdTerm',
                    'v':
                    'cpqx',
                    't': 'json'
                },
                {
                    'n': '产品收益类型',
                    'En': 'ProdIncomeType',
                    'v':
                    'cpsylxms',
                    't': 'json'
                },
                {
                    'n': '募集币种',
                    'En': 'RaiseCurrcy',
                    'v':
                    'mjbz',
                    't': 'json'
                },
                {
                    'n': '风险等级',
                    'En': 'RiskGrade',
                    'v':
                    'fxdjms',
                    't': 'json'
                },
                {
                    'n': '募集结束日期',
                    'En': 'RaiseEndDate',
                    'v':
                    'mjjsrq',
                    't': 'json'
                },
                {
                    'n': '产品终止日期',
                    'En': 'ProdEndDate',
                    'v':
                    'cpyjzzrq',
                    't': 'json'
                },
                {
                    'n': '产品净值',
                    'En': 'ProdNetValue',
                    'v':
                    'cpjz',
                    't': 'json'
                },
                {
                    'n': '到期实际收益率',
                    'En': 'ActualYields',
                    'v':
                    'dqsjsyl',
                    't': 'json'
                },
                {
                    'n': '业务起始日',
                    'En': 'BusinessStartDate',
                    'v':
                    'kfzqqsr',
                    't': 'json'
                },
                {
                    'n': '业务结束日',
                    'En': 'BusinessEndDate',
                    'v':
                    'kfzqjsr',
                    't': 'json'
                },
                {
                    'n': '投资资产类型',
                    'En': 'TypeOfInvestmentAssets',
                    'v':
                    'tzlxms',
                    't': 'json'
                },
                {
                    'n': '预计最高收益率',
                    'En': 'ExpectedHigestYields',
                    'v':
                    'yjkhzgnsyl',
                    't': 'json'
                },
                {
                    'n': '发行机构名称',
                    'En': 'IssuerName',
                    'v':
                    'fxjgms',
                    't': 'json'
                },
                {
                    'n': '发行机构代码',
                    'En': 'IssuerCode',
                    'v':
                    'fxjgdm',
                    't': 'json'
                },
                {
                    'n': '产品id',
                    'En': 'ProdID',
                    'v':
                    'cpid',
                    't': 'json'
                },
                {
                    'n': 'qxms',
                    'En': 'Term',
                    'v':
                    'qxms',
                    't': 'json'
                },

            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def chinawealth_sales_area(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'json',
                'db': 'Chinawealth.ChinawealthSalesArea',
                'keys': ['HTML_ID'],
                'check': 'SalesArea',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'cpid',
                    't': 'request_body'
                },{
                    'n': '销售区域',
                    'En': 'SalesArea',
                    'v':
                    'List/cpxsqy',
                    't': 'json_join,'
                },

            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def get_lxdm(self,page, response=None):
        index = response.meta['index']
        return urllib.parse.urlencode({'cpjglb':'',
                'cpsylx':'',
                'cpyzms':'',
                'cpfxdj':'',
                'cpqx':'',
                'cpzt':'',
                'cpdjbm':' ',
                'cpmc':'',
                'cpfxjg':'',
                'mjqsrq':'',
                'mjjsrq':'',
                'areacode':'',
                'tzzlxdm':index,
                'pagenum':str(page),
                'orderby':'', #'desc_cpdjbm', # 按产品编码倒叙 即有限提取最新的产品信息
                'code':'',
                'changeTableFlage':'0',
                'drawPageToolEnd':'5'})

    def get_xsqy(self, page,response=None):
        index = response.meta['index']
        return urllib.parse.urlencode({"tzzlxdm":index,
                                    "cpid":str(page),
                                    "cpjglb":"",
                                    "cpsylx":"",
                                    "cpyzms":"",
                                    "cpqx":"",
                                    "cpzt":"",
                                    "cpdjbm":"",
                                    "cpmc":"",
                                    "cpfxjg":"",
                                    "mjqsrq":"",
                                    "mjjsrq":"",
                                    "pagenum":"1"
                                        })


def main():
    ChinaSpider.put_redis()

if __name__=='__main__':
    main()
