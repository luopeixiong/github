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
from myselector import pdf_to_html

'''
redis数据库使用FOFI先进后出的规则 对url进行队列选择
'''

class SinaspiderSpider(_RedisSpider, SpiderHelp):  #,scrapy.Spider
    name = 'sina'
    start_urls = [
                  'http://stock.finance.sina.com.cn/xintuo/view/vProdList.php?prodtype={}',  # 新浪信托
                  'http://finance.sina.com.cn/js/data/20140924/category.js',  # 新浪股票
                  'http://money.finance.sina.com.cn/bank/api/json_v2.php/Bank_FinanceService.searchFinaceProd?page=1&num=20', #  银行理财
                  'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodes', # 债券
                  'http://vip.stock.finance.sina.com.cn/quotes_service/view/js/qihuohangqing.js?20170823', # 期货
                  'http://money.finance.sina.com.cn/fund_center/index.html'# 新浪-基金入口
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

    def start_requests(self):
        req = []
        logger.info('Start Crawl Spider %s at rediskey %s' % (self.name,self.redis_key))
        for url in self.start_urls:
            if url == 'http://stock.finance.sina.com.cn/xintuo/view/vProdList.php?prodtype={}':
                for i in range(1,5):
                    _url = url.format(i)
                    req.append(self.request(
                        _url,
                        meta={'formatter':_url+'&page={}'},
                        redis_flag=REDISFLAG,
                        priority=5000,
                        callback=self.sina_trust))
            elif url == 'http://finance.sina.com.cn/js/data/20140924/category.js':
                req.append(self.request(
                        url,
                        redis_flag=REDISFLAG,
                        priority=5000,
                        callback=self.sina_stock_in))
            elif url == 'http://money.finance.sina.com.cn/bank/api/json_v2.php/Bank_FinanceService.searchFinaceProd?page=1&num=20':
                req.append(self.request(
                        url,
                        redis_flag=REDISFLAG,
                        priority=5000,
                        callback=self.sina_bank_finance))
            elif url == 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodes':
                req.append(self.request(
                        url,
                        redis_flag=REDISFLAG,
                        priority=5000,
                        callback=self.sina_Capital))
            elif url == 'http://vip.stock.finance.sina.com.cn/quotes_service/view/js/qihuohangqing.js?20170823':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        priority=5000,
                        callback=self.sina_futures))
            elif url == 'http://money.finance.sina.com.cn/fund_center/index.html':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        priority=5000,
                        callback=self.sina_funds_in))

        return req

    @SpiderHelp.check_response
    def sina_trust(self, response):
        # size 
        '''
        新浪信托
        '''
        # 列表页
        # 信托产品
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[contains(text(),"查看")]/@href',
                                                   },
                                           callback=self.sina_truse_info,
                                           headers=self.default_header,
                                           method='POST',
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs2:
            yield req

        # 信托发行机构
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//div[@class="tab_blk"]/table//tr/td[3]/a/@href',
                                                   },
                                           callback=self.sina_truse_com_info,
                                           headers=self.default_header,
                                           method='POST',
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[text()="下一页"]/@onclick'
                        },
                callback=self.sina_trust,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(page),
                divmod=1,
                flag=True,
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        

    @SpiderHelp.check_response
    def sina_truse_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.SinaTrustData',
                'keys': ['TrustProdFullName','TrustProdShortName'],
                'check': 'TrustProdFullName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'prodid=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '信托产品全称',
                    'En': 'TrustProdFullName',
                    'v':
                    '//td[div[contains(text(),"信托产品全称")]]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '信托产品简称',
                    'En': 'TrustProdShortName',
                    'v':
                    '//td[contains(text(),"信托产品简称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '信托机构',
                    'En': 'Trusts',
                    'v': '//td[contains(text(),"信托机构")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '信托机构ID',
                    'En': 'TrustsID',
                    'v': '//td[contains(text(),"信托机构")]/following-sibling::td[1]/a/@href',
                    't': 'xpath_re',
                    're': 'comid=(.+)'
                },
                {
                    'n': '投资领域',
                    'En': 'InvestmentField',
                    'v': '//td[contains(text(),"投资领域")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '投资经理',
                    'En': 'InvestmentManager',
                    'v': '//td[contains(text(),"投资经理")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '产品大类',
                    'En': 'ProductCategory',
                    'v': '//td[contains(text(),"产品大类")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '是否结构化',
                    'En': 'Structured',
                    'v': '//td[contains(text(),"是否结构化")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '预计年化收益率(%)',
                    'En': 'YieldExcept',
                    'v': '//td[contains(text(),"预计年化收益率(%)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '到期年化收益率(%)',
                    'En': 'YieldToMaturity',
                    'v': '//td[contains(text(),"到期年化收益率(%)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '产品说明',
                    'En': 'ProdDescription',
                    'v': '//td[contains(text(),"产品说明")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '预期收益说明',
                    'En': 'YieldExceptDescription',
                    'v': '//td[contains(text(),"预期收益说明")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '到期收益说明',
                    'En': 'YieldToMaturityDescription',
                    'v': '//td[contains(text(),"到期收益说明")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '认购资金递增说明',
                    'En': 'ExplanationOfIncreasing',
                    'v': '//td[contains(text(),"认购资金递增说明")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '信用增级方式',
                    'En': 'CreditRating',
                    'v': '//td[contains(text(),"信用增级方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '推介起始日',
                    'En': 'RecommendStartDate',
                    'v': '//td[div[contains(text(),"推介起始日")]]/following-sibling::td[1]/div[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '推介截止日',
                    'En': 'RecommendEndDate',
                    'v': '//td[contains(text(),"推介截止日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '存续期(年)',
                    'En': 'SurvivalPeriod',
                    'v': '//td[contains(text(),"存续期(年)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//td[contains(text(),"成立日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '终止日期',
                    'En': 'EndTime',
                    'v': '//td[contains(text(),"终止日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '预计发行规模(万元)',
                    'En': 'ExpectedDistributionScale',
                    'v': '//td[contains(text(),"预计发行规模(万元)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '实际发行规模(万元)',
                    'En': 'ActualDistributionScale',
                    'v': '//td[contains(text(),"实际发行规模(万元)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行地',
                    'En': 'PlaceOfDistribution',
                    'v': '//td[contains(text(),"发行地")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最低认购资金(万元)',
                    'En': 'MinimumSubscribedFunds',
                    'v': '//td[contains(text(),"最低认购资金(万元)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_truse_com_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.SinaTrustComData',
                'keys': ['HTML_ID'],
                'check': 'HTML_ID',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'comid=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '机构名称',
                    'En': 'NameOfTrustAgency',
                    'v':
                    '//td[div[contains(text(),"机构名称")]]/following-sibling::td[1]/div[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法人代表',
                    'En': 'NameOfLegalRepresentative',
                    'v':
                    '//td[contains(text(),"法人代表")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '总经理',
                    'En': 'GeneralManager',
                    'v': '//td[contains(text(),"总经理")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '所属地区',
                    'En': 'AreaName',
                    'v': '//td[contains(text(),"所属地区")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v': '//td[contains(text(),"注册地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司电话',
                    'En': 'OfficePhoneNumber',
                    'v': '//td[contains(text(),"公司电话")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司电子邮箱',
                    'En': 'OfficeEmailAddress',
                    'v': '//td[contains(text(),"公司电子邮箱")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v': '//td[contains(text(),"经营范围")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司简介',
                    'En': 'CompanyProfile',
                    'v': '//td[contains(text(),"公司简介")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '英文名称',
                    'En': 'EnglishName',
                    'v': '//td[div[contains(text(),"英文名称")]]/following-sibling::td[1]/div[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '董事长',
                    'En': 'Chairman',
                    'v': '//td[contains(text(),"董事长")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//td[contains(text(),"成立日期")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资本(万元)',
                    'En': 'RegisteredCapital',
                    'v': '//td[contains(text(),"注册资本(万元)")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '办公地址',
                    'En': 'OfficeAddress',
                    'v': '//td[contains(text(),"办公地址")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司传真',
                    'En': 'OfficeFaxNumber',
                    'v': '//td[contains(text(),"公司传真")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司网址',
                    'En': 'OfficeWebsite',
                    'v': '//td[contains(text(),"公司网址")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_stock_in(self,response):
        # 解析js获取param页面
        regex = re.compile('\{.*\}',re.S)
        result = regex.search(response.text).group(0)
        JS = json.loads(result)
        key_list = list(JS['stock']['category']['schq']['category']['hsgs']['category'].keys())
        # ['qbag', 'zxqy', 'cyb', 'xlhy', 'gnbk', 'dybk', 'zs', 'zscf', 'szzz', 'szcz', 'hs300']
        # 前3为全部A股,中小板,创业板key
        for key in key_list[0:3]:
            url = 'http://finance.sina.com.cn/data/blocks/stock_schq_hsgs_%s.txt' % key
            yield _Request(url,
                headers=self.default_header,
                priority=10000,
                redis_flag=True,
                redis_conn=self.r,
                callback=self.sina_stock_get_param)
    
    @SpiderHelp.check_response
    def sina_stock_get_param(self, response):
        # 正则提取param
        regex = re.compile('param:\"(.*?)\"')
        param = regex.search(response.text).group(1)
        # 拼接url
        formatter = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php/?__s=["+param+"]"+"&callback=FDC_DC.theTableData"
        url = formatter.format(sort='', asc=0, page=1, num=40)
        yield scrapy.Request(url,
            headers=self.default_header,
            meta={'formatter':formatter,'proxys':True},
            priority=30000,
            callback=self.sina_stock_list)

    @SpiderHelp.check_response
    def sina_stock_list(self, response):
        response = response.replace(body=re.search('\{.*?\}',response.text,re.S).group(0))
        # size 
        '''
        新浪股票
        '''

        # #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'count'
                        },
                callback=self.sina_stock_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(sort='', asc=0, page=page, num=40),
                divmod=40,
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='json')
        for req in reqs:
            yield req

        #  排序相同
        # '"symbol","code","name","trade","pricechange","changepercent","buy","sell","settlement","open","high","low","volume","amount","ticktime","per","per_d","nta","pb","mktcap","nmc","turnoverratio","favor","guba"'
        # '"symbol","code","name","trade","pricechange","changepercent","buy","sell","settlement","open","high","low","volume","amount","ticktime","per","per_d","nta","pb","mktcap","nmc","turnoverratio","favor","guba"'
        # '"symbol","code","name","trade","pricechange","changepercent","buy","sell","settlement","open","high","low","volume","amount","ticktime","per","per_d","nta","pb","mktcap","nmc","turnoverratio","favor","guba"'

        # 列表页
        # 股票
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'items',
                                                   },
                                           callback=self.sina_stock_com,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://finance.sina.com.cn/realstock/company/%s/nc.shtml' % page[0],
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs2:
            yield req

    @SpiderHelp.check_response
    def sina_stock_com(self, response):
        #  公司简介
        reqs = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="公司简介"]/@href',
                                                   },
                                           callback=self.sina_stock_com_info,
                                           headers=self.default_header,
                                           priority=1000,
                                           meta={'proxys':True},
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs:
            yield req 

        # 公司高管
        reqs = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="公司高管"]/@href',
                                                   },
                                           callback=self.sina_com_senior_executive_info,
                                           headers=self.default_header,
                                           priority=1000,
                                           meta={'proxys':True},
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs:
            yield req 

        #  所属行业,所属板块
        reqs = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="所属行业"]/@href',
                                                   },
                                           callback=self.sina_stock_com_industry_classification,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs:
            yield req 
        #  股本结构
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="股本结构"]/@href',
                                                   },
                                           callback=self.sina_stock_com_capital_structure,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs2:
            yield req

        #  主要股东
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_re',
                                                   'v': '//a[text()="主要股东"]/@href',
                                                   're': '(https?:\/\/.*?)\/displaytype'
                                                   },
                                           callback=self.sina_stock_com_major_shareholders,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page + '.phtml',
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #  流通股东
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_re',
                                                   'v': '//a[text()="流通股东"]/@href',
                                                   're': '(https?:\/\/.*?)\/displaytype'
                                                   },
                                           callback=self.sina_stock_com_circulating_shareholders,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page + '.phtml',
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req
        #  基金持股
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_re',
                                                   'v': '//a[text()="基金持股"]/@href',
                                                   're': '(https?:\/\/.*?)\/displaytype'
                                                   },
                                           callback=self.sina_com_fund_shares,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page + '.phtml',
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req

        #  融资融券
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_re',
                                                   'v': '//a[text()="融资融券"]/@href',
                                                   're': '(https?:\/\/.*?)bdate'
                                                   },
                                           callback=self.sina_com_margin_financing,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page + 'bdate=2001-01-01&edate={}'.format(TODAY),
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req

        #  内部交易
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_re',
                                                   'v': '//a[text()="内部交易"]/@href',
                                                   're': '(https?:\/\/.*?)bdate'
                                                   },
                                           callback=self.sina_com_internal_transaction,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page + 'bdate=2001-01-01&edate={}'.format(TODAY),
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req

        #  大宗交易
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_re',
                                                   'v': '//a[text()="大宗交易"]/@href',
                                                   're': '(https?:\/\/.*?)bdate'
                                                   },
                                           callback=self.sina_com_block_trade,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page + 'bdate=2001-01-01&edate={}'.format(TODAY),
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req

        #  历史交易 页面跳转 获取年份列表 详细页可跳转 每日交易明细
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="历史交易"]/@href',
                                                   },
                                           callback=self.sina_com_historical_transaction,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req



        #  复权交易 页面跳转 获取年份列表
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="复权交易"]/@href',
                                                   },
                                           callback=self.sina_com_right_transaction,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req

        # 持仓明细 可以需要抓取交易明细数据后 聚合计算 买入 卖出 向量运算

        #  分红送配
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="分红送配"]/@href',
                                                   },
                                           callback=self.sina_com_dividends_and_allotment,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req

        #  新股发行
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="新股发行"]/@href',
                                                   },
                                           callback=self.sina_com_ipo,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req

        #  限售解禁
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="限售解禁"]/@href',
                                                   },
                                           callback=self.sina_com_lift_a_ban_on_sale,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page + '&p=1',
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req

        #  增发
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="增发"]/@href',
                                                   },
                                           callback=self.sina_com_seasoned_new_issue,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req


        

    @SpiderHelp.check_response
    def sina_stock_com_info(self, response):
        # 新浪公司基本信息
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComInfoData',
                'keys': ['ComCode'],
                'check': 'ComCode',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },
                {
                    'n': '公司名称',
                    'En': 'ComFullName',
                    'v':
                    '//td[contains(text(),"公司名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//h1[@id="stockName"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司代码',
                    'En': 'ComCode',
                    'v':
                    '//h1[@id="stockName"]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司英文名称',
                    'En': 'ComEnglishName',
                    'v':
                    '//td[contains(text(),"公司英文名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '上市市场',
                    'En': 'ListedMarket',
                    'v': '//td[contains(text(),"上市市场")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '发行价格',
                    'En': 'IssuePrice',
                    'v': '//td[contains(text(),"发行价格")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//td[contains(text(),"成立日期")]/following-sibling::td[1]//text()',
                    't': 'xpath_first'
                },
                {
                    'n': '机构类型',
                    'En': 'OrganizationType',
                    'v': '//td[contains(text(),"机构类型")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '董事会秘书',
                    'En': 'SecretaryName',
                    'v': '//td[contains(text(),"董事会秘书")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '董秘电话',
                    'En': 'SecretaryPhoneNumber',
                    'v': '//td[contains(text(),"董秘电话")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '董秘传真',
                    'En': 'SecretaryFaxNumber',
                    'v': '//td[contains(text(),"董秘传真")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '董秘电子邮箱',
                    'En': 'SecretaryEmailAddress',
                    'v': '//td[contains(text(),"董秘电子邮箱")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '邮政编码',
                    'En': 'ZipCode',
                    'v': '//td[contains(text(),"邮政编码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证券简称更名历史',
                    'En': 'RenameHistory',
                    'v': '//td[contains(text(),"证券简称更名历史")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v': '//td[contains(text(),"注册地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '办公地址',
                    'En': 'OfficeAddress',
                    'v': '//td[contains(text(),"办公地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司简介',
                    'En': 'Companyprofile',
                    'v': '//td[contains(text(),"公司简介")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v': '//td[contains(text(),"经营范围")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市日期',
                    'En': 'ListedDate',
                    'v': '//td[contains(text(),"上市日期")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '主承销商',
                    'En': 'MainUnderwriter',
                    'v': '//td[contains(text(),"主承销商")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资本',
                    'En': 'RegisteredCapital',
                    'v': '//td[contains(text(),"注册资本")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '组织形式',
                    'En': 'OrganizationalForm',
                    'v': '//td[contains(text(),"组织形式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司电话',
                    'En': 'OfficePhoneNumber',
                    'v': '//td[contains(text(),"公司电话")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司传真',
                    'En': 'OfficeFaxNumber',
                    'v': '//td[contains(text(),"公司传真")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司电子邮箱',
                    'En': 'OfficeEmailAddress',
                    'v': '//td[contains(text(),"公司电子邮箱")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司网址',
                    'En': 'OfficeWebsite',
                    'v': '//td[contains(text(),"公司网址")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '信息披露网址',
                    'En': 'DisclosureWebsite',
                    'v': '//td[contains(text(),"信息披露网址")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_senior_executive_info(self, response):
        #//*[@id="comInfo1"]/tbody/tr[39]
        #
        _configs = [{
            'list': {
                'n': '',
                'v': '//*[@id="comInfo1"]//tr[td[last()=4] and td[@class="ccl"]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_SeniorExcutive',
                'keys': ['CompanyName','Name','Title','postion'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v':
                    '//h1[@id="stockName"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '任期',
                    'En': 'Capital',
                    'v':
                    '../..//tr/th/text()',
                    't': 'xpath_first'
                },{
                    'n': '标题',
                    'En': 'Title',
                    'v':
                    './preceding-sibling::tr[td[last()=1]][1]/td/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '高管姓名',
                    'En': 'Name',
                    'v':
                    './td[1]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '职务',
                    'En': 'postion',
                    'v':
                    './td[2]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '任期开始',
                    'En': 'StartTime',
                    'v':
                    './td[3]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '任期结束',
                    'En': 'EndTime',
                    'v':
                    './td[4]/div/text()',
                    't': 'xpath_first'
                },
                
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_stock_com_industry_classification(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComClassification',
                'keys': ['HTML_ID'],
                'check': 'ComShortName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\/',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//h1[@id="stockName"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '所属行业板块',
                    'En': 'IndustryPlate',
                    'v':
                    '//div[@class="tagmain"]/table[@class="comInfo1"][1]//tr[position()>2 and td[last()=2]]/td[1]/text()',
                    't': 'xpath_join,'
                },{
                    'n': '所属概念板块',
                    'En': 'ConceptualPlate',
                    'v':
                    '//div[@class="tagmain"]/table[@class="comInfo1"][2]//tr[position()>2 and td[last()=2]]/td[1]/text()',
                    't': 'xpath_join,'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_stock_com_capital_structure(self, response):
        # 最多五列
        # 竖向迭代
        for i in range(2,7):
            _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="tagmain"]/table',    
                    't': 'xpath',
                    'db': 'CreditDataBase.Sina_ListedComCapitalStructure',
                    'keys': ['HTML_ID','DateOfChange','CauseOfChange'],
                    'check': 'DateOfChange',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID',
                        'En': 'HTML_ID',
                        'v':
                        'stockid\/(.+?)\.phtml',
                        't': 'url_re'
                    },
                    {
                        'n': '公司简称',
                        'En': 'ComShortName',
                        'v':
                        '//div[@class="tbtb01"]/h1/a/text()',
                        't': 'xpath_first'
                    },{
                        'n': '变动日期',
                        'En': 'DateOfChange',
                        'v':
                        './/tr[td[contains(text(),"变动日期")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '公告日期',
                        'En': 'DateOfAnnouncement',
                        'v':
                        './/tr[td[contains(text(),"公告日期")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '变动原因',
                        'En': 'CauseOfChange',
                        'v':
                        './/tr[td[contains(text(),"变动原因")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '总股本',
                        'En': 'TotalCapitalStock',
                        'v':
                        './/tr[td[contains(text(),"总股本")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '流通A股',
                        'En': 'CirculationOfAshares',
                        'v':
                        './/tr[td[contains(text(),"流通A股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '高管股',
                        'En': 'ExecutiveStock',
                        'v':
                        './/tr[td[contains(text(),"高管股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '限售A股',
                        'En': 'LimitedSaleOfAshares',
                        'v':
                        './/tr[td[contains(text(),"限售A股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '流通B股',
                        'En': 'CirculationOfBshares',
                        'v':
                        './/tr[td[contains(text(),"流通B股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '限售B股',
                        'En': 'LimitedSaleOfBshares',
                        'v':
                        './/tr[td[contains(text(),"限售B股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '流通H股',
                        'En': 'CirculationOfHshares',
                        'v':
                        './/tr[td[contains(text(),"流通H股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '国家股',
                        'En': 'StateOwnedShare',
                        'v':
                        './/tr[td[contains(text(),"国家股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '国有法人股',
                        'En': 'StateOwnedCorporateShares',
                        'v':
                        './/tr[td[contains(text(),"国有法人股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '境内法人股',
                        'En': 'DomesticLegalPersonShares',
                        'v':
                        './/tr[td[contains(text(),"境内法人股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '境内发起人股',
                        'En': 'DomesticSponsorsStock',
                        'v':
                        './/tr[td[contains(text(),"境内发起人股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '募集法人股',
                        'En': 'RaisingCorporateShares',
                        'v':
                        './/tr[td[contains(text(),"募集法人股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '一般法人股',
                        'En': 'GeneralCorporateShares',
                        'v':
                        './/tr[td[contains(text(),"一般法人股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '战略投资者持股',
                        'En': 'ShareholdingOfStrategicInvestors',
                        'v':
                        './/tr[td[contains(text(),"战略投资者持股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '基金持股',
                        'En': 'FundShares',
                        'v':
                        './/tr[td[contains(text(),"基金持股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '转配股',
                        'En': 'AllotmentOfShares',
                        'v':
                        './/tr[td[contains(text(),"转配股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '内部职工股',
                        'En': 'InternalEmployeeStock',
                        'v':
                        './/tr[td[contains(text(),"内部职工股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '优先股',
                        'En': 'PreferredStock',
                        'v':
                        './/tr[td[contains(text(),"优先股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },
                ]
            }]
            results = self.item_parse(_configs, response)
            for item in results:
                yield item

    @SpiderHelp.check_response
    def sina_stock_com_major_shareholders(self, response):
        # 主要股东
        _configs = [{
            'list': {
                'n': '',
                'v': '//tr[td[last()=5] and td[.//a]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComMajorShareHolders',
                'keys': ['HTML_ID','ShareholderName','Deadline'],
                'check': 'ShareholderName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '截至日期',
                    'En': 'Deadline',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="截至日期"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="公告日期"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股东说明',
                    'En': 'ShareHoldersExplanation',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="股东说明"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股东总数',
                    'En': 'TotalNumberOfShareholders',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="股东总数"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '平均持股数',
                    'En': 'AverageStockHoldingNumber',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="平均持股数"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股东名称',
                    'En': 'ShareholderName',
                    'v':
                    './td[2]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '排序',
                    'En': 'Rank',
                    'v':
                    './td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '持股数量(股)',
                    'En': 'StockHoldingNumber',
                    'v':
                    './td[3]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '持股比例(%)',
                    'En': 'ShareholdingRatio',
                    'v':
                    './td[4]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '股本性质',
                    'En': 'NatureOfCapitalStock',
                    'v':
                    './td[5]/div/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_stock_com_circulating_shareholders(self, response):
        # 流通股东
        _configs = [{
            'list': {
                'n': '',
                'v': '//tr[td[last()=5] and td[1][div[text()>0]]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComCirculatingShareholders',
                'keys': ['HTML_ID','ShareholderName','Deadline'],
                'check': 'ShareholderName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '截止日期',
                    'En': 'Deadline',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="截止日期"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="公告日期"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股东名称',
                    'En': 'ShareholderName',
                    'v':
                    './td[2]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '排序',
                    'En': 'Rank',
                    'v':
                    './td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '持股数量(股)',
                    'En': 'StockHoldingNumber',
                    'v':
                    './td[3]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '占流通股比例(%)',
                    'En': 'ProportionOfCirculatingShares',
                    'v':
                    './td[4]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '股本性质',
                    'En': 'NatureOfCapitalStock',
                    'v':
                    './td[5]/div/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_fund_shares(self, response):
        # 基金持股
        _configs = [{
            'list': {
                'n': '',
                'v': '//tr[td[last()=6] and td[2][div[a[text()>0]]]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComFundShares',
                'keys': ['HTML_ID','FundCode','Deadline'],
                'check': 'FundCode',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '截止日期',
                    'En': 'Deadline',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="截止日期"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '基金名称',
                    'En': 'NameOfFundProd',
                    'v':
                    './td[1]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '基金代码',
                    'En': 'FundCode',
                    'v':
                    './td[2]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '持仓数量(股)',
                    'En': 'HoldingNumber',
                    'v':
                    './td[3]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '占流通股比例(%)',
                    'En': 'ProportionOfCirculatingShares',
                    'v':
                    './td[4]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '持股市值（元）',
                    'En': 'StockMarketValue',
                    'v':
                    './td[5]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '占净值比例（%）',
                    'En': 'ProportionOfNetValue',
                    'v':
                    './td[6]/div/a/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_margin_financing(self, response):
        # 融资融券字段提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="list_table"]//tr[td[1][text()>0]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComMarginFinancing',
                'keys': ['HTML_ID','DateOfTransaction'],
                'check': 'DateOfTransaction',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'symbol=[a-zA-Z]*(\d+?)&',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//table[@class="list_table"]//tr[1]/td/span/text()',
                    't': 'xpath_re',
                    're':'\s*(\S+)\s*融资融券交易明细'
                },{
                    'n': '日期',
                    'En': 'DateOfTransaction',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融资余额',
                    'En': 'FinancingBalance',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融资买入额',
                    'En': 'FinancingBuyingAmount',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融资偿还额',
                    'En': 'FinancingReimbursement',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融资余量金额',
                    'En': 'AmountOfFinancialRemainder',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融券余量',
                    'En': 'FinancingMargin',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融券卖出量',
                    'En': 'MarginSelling',
                    'v':
                    './td[8]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融券偿还量',
                    'En': 'MarginRepayment',
                    'v':
                    './td[9]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融券余额',
                    'En': 'MarginBalance',
                    'v':
                    './td[10]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_internal_transaction(self, response):
        # 内部交易字段提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="list_table"]//tr[td[a[string-length(text())=6]]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComInternalTransaction',
                'keys': ['HTML_ID','ChangingPerson','ChangeDate','PostChangeStockHoldingNumber'],
                'check': 'ChangingPerson',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    './td[1]/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    './td[2]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '变动人',
                    'En': 'ChangingPerson',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '变动类型',
                    'En': 'ChangeType',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '变动股数',
                    'En': 'VariableNumberOfShares',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成交均价',
                    'En': 'AverageTransactionPrice',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '变动金额(万元)',
                    'En': 'AmountOfChange',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '变动后持股数',
                    'En': 'PostChangeStockHoldingNumber',
                    'v':
                    './td[8]/text()',
                    't': 'xpath_first'
                },{
                    'n': '变动原因',
                    'En': 'ChangeReason',
                    'v':
                    './td[9]/text()',
                    't': 'xpath_first'
                },{
                    'n': '变动日期',
                    'En': 'ChangeDate',
                    'v':
                    './td[10]/text()',
                    't': 'xpath_first'
                },{
                    'n': '持股种类',
                    'En': 'TypeOfStockOwnership',
                    'v':
                    './td[11]/text()',
                    't': 'xpath_first'
                },{
                    'n': '与董监高关系',
                    'En': 'RelationsWithDirector',
                    'v':
                    './td[12]/text()',
                    't': 'xpath_first'
                },{
                    'n': '董监高职务',
                    'En': 'DirectorPosition',
                    'v':
                    './td[13]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[text()="下一页"]/@onclick'
                        },
                callback=self.sina_com_internal_transaction,
                headers=self.default_header,
                urlfunc=
                lambda page, response: re.compile('(https?:\/\/.*?)bdate').search(response.url).group(1) + 'bdate=2001-01-01&edate={}'.format(TODAY) + '&p={}'.format(page),
                divmod=1,
                flag=True,
                redis_conn=self.r,
                redis_flag=True,
                readpage=5,
                response_type='xpath')
        for req in reqs:
            yield req

    def sina_com_block_trade(self, response):
        # 大宗交易字段提取
        # 字段可能会重复  -- 字段完全相同 
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="list_table"]//tr[td[a[string-length(text())=6]]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComBlockTrade',
                'keys': ['HTML_ID','DateOfTransaction','Buyer','Seller','TransactionAmount'],
                'check': 'DateOfTransaction',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '交易日期',
                    'En': 'DateOfTransaction',
                    'v':
                    './td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    './td[2]/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    './td[3]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '成交价格(元)',
                    'En': 'TransactionPrice',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成交量(万股)',
                    'En': 'TransactionVolume',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成交金额(万元)',
                    'En': 'TransactionAmount',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '买方营业部',
                    'En': 'Buyer',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '卖方营业部',
                    'En': 'Seller',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证券类型',
                    'En': 'TypeOfShares',
                    'v':
                    './td[8]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[text()="下一页"]/@onclick'
                        },
                callback=self.sina_com_block_trade,
                headers=self.default_header,
                urlfunc=
                lambda page, response: re.compile('(https?:\/\/.*?)bdate').search(response.url).group(1) + 'bdate=2001-01-01&edate={}'.format(TODAY) + '&p={}'.format(page),
                divmod=1,
                flag=True,
                redis_conn=self.r,
                redis_flag=True,
                readpage=5,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sina_com_historical_transaction(self, response):
        # 生成generotor对象 会多几个无效页面 忽略(无法验证--起始好像可以从日期伪造,略过)
        years = response.xpath('//select[@name="year"]/option/@value').extract()
        jidus = response.xpath('//select[@name="jidu"]/option/@value').extract()
        # 节省内存
        urls = ('%s?year=%s&jidu=%s' % (response.url,year,jidu) for year in years for jidu in jidus)
        for url in urls:
            yield scrapy.Request(url,
                headers=self.default_header,
                priority=1000,
                callback=self.sina_com_historical_transaction_info)

    @SpiderHelp.check_response
    def sina_com_historical_transaction_info(self, response):
        # 历史交易字段提取
        # 这里可以跳转历史交易详细... 数据量庞大 再考虑
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="FundHoldSharesTable"]//tr[td[1][div/a/@href]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComHistoricalTransaction',
                'keys': ['HTML_ID','DateOfTransaction'],
                'check': 'DateOfTransaction',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(\d+)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '交易日期',
                    'En': 'DateOfTransaction',
                    'v':
                    './td[1]/div/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '开盘价',
                    'En': 'OpenPrice',
                    'v':
                    './td[2]/div/text()',
                    't': 'xpath_first',
                },{
                    'n': '最高价',
                    'En': 'HighestPrice',
                    'v':
                    './td[3]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '收盘价',
                    'En': 'ClosingPrice',
                    'v':
                    './td[4]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '最低价',
                    'En': 'MinimumPrice',
                    'v':
                    './td[5]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易量(股)',
                    'En': 'VolumeOfTransaction',
                    'v':
                    './td[6]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易金额(元)',
                    'En': 'TransactionAmount',
                    'v':
                    './td[7]/div/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        # # 成交明细
        # # http://market.finance.sina.com.cn/transHis.php?date=2013-03-29&symbol=sh600010&page=1
        # # 数据量庞大 
        # urls_generator = ('http://market.finance.sina.com.cn/transHis.php?'+ url+'&page=1' for url in response.xpath('//table[@id="FundHoldSharesTable"]//tr[td[1][div/a/@href]]/td[1]/div/a/@href').re('(symbol=.+)'))
        # for url in urls_generator:
        #     yield scrapy.Request(
        #         url,
        #         headers=self.default_header,
        #         priority=3000,
        #         callback=self.sina_com_transaction_details)

    @SpiderHelp.check_response
    def sina_com_transaction_details(self, response):
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': "detailPages=.*?\[(\d+),'\d+:\d+:\d+','\d+:\d+:\d+']];;"
                        },
                callback=self.sina_com_transaction_details,
                headers=self.default_header,
                urlfunc=
                lambda page, response: re.compile('(https?:\/\/.*?&page=)').search(response.url).group(1) + str(page),
                divmod=1,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # 每日交易明细 时间序列
        _configs = [{
            'list': {
                'n': '',
                'v': '//table//tr[.//*[contains(text(),":")]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComTransactionDetails',
                'keys': ['HTML_ID','DateOfTransaction','TimeOfTransaction','VolumeOfTransaction','Nature'],
                'check': 'TimeOfTransaction',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'symbol=(.+?)&',
                    't': 'url_re'
                },
                {
                    'n': '交易日期',
                    'En': 'DateOfTransaction',
                    'v':
                    'date=(.+?)&',
                    't': 'url_re'
                },
                {
                    'n': '成交时间',
                    'En': 'TimeOfTransaction',
                    'v':
                    './*[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '成交价',
                    'En': 'TransactionPrice',
                    'v':
                    './*[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '价格变动',
                    'En': 'PriceChange',
                    'v':
                    './*[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成交量(手)',
                    'En': 'VolumeOfTransaction',
                    'v':
                    './*[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成交额(元)',
                    'En': 'Turnover',
                    'v':
                    './*[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '性质',
                    'En': 'Nature',
                    'v':
                    './*[6]/*[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_right_transaction(self, response):
        # 生成generotor对象 会多几个无效页面 忽略(无法验证--起始好像可以从日期伪造,略过)
        years = response.xpath('//select[@name="year"]/option/@value').extract()
        jidus = response.xpath('//select[@name="jidu"]/option/@value').extract()
        # 节省内存
        urls = ('%s?year=%s&jidu=%s' % (response.url,year,jidu) for year in years for jidu in jidus)
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                callback=self.sina_com_right_transaction_info)

    @SpiderHelp.check_response
    def sina_com_right_transaction_info(self, response):
        # 复权交易分列信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="FundHoldSharesTable"]//tr[td[1][div/a/@href]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComRightTransaction',
                'keys': ['HTML_ID','DateOfTransaction'],
                'check': 'DateOfTransaction',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(\d+)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '交易日期',
                    'En': 'DateOfTransaction',
                    'v':
                    './td[1]/div/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '开盘价',
                    'En': 'OpenPrice',
                    'v':
                    './td[2]/div/text()',
                    't': 'xpath_first',
                },{
                    'n': '最高价',
                    'En': 'HighestPrice',
                    'v':
                    './td[3]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '收盘价',
                    'En': 'ClosingPrice',
                    'v':
                    './td[4]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '最低价',
                    'En': 'MinimumPrice',
                    'v':
                    './td[5]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易量(股)',
                    'En': 'VolumeOfTransaction',
                    'v':
                    './td[6]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易金额(元)',
                    'En': 'TransactionAmount',
                    'v':
                    './td[7]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '复权因子',
                    'En': 'RightFactor',
                    'v':
                    './td[8]/div/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_dividends_and_allotment(self, response):
        # # 进详情页
        # sharebonus_1 = ('http://vip.stock.finance.sina.com.cn' + url for url in response.xpath('//table[@id="sharebonus_1"]//a[contains(text(),"查看")]/@href').extract())
        # sharebonus_2 = ('http://vip.stock.finance.sina.com.cn' + url for url in response.xpath('//table[@id="sharebonus_2"]//a[contains(text(),"查看")]/@href').extract())
        # # 股息
        # for url in sharebonus_1:
        #     yield scrapy.Request(url,
        #         headers=self.default_header,
        #         callback=self.sina_com_dividends)

        # # 配股
        # for url in sharebonus_2:
        #     yield scrapy.Request(url,
        #         headers=self.default_header,
        #         callback=self.sina_com_allotment)

        # 红利信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="sharebonus_1"]//tr[td[1][contains(text(),"-")]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComDividends',
                'keys': ['HTML_ID','DateOfAnnouncement'],
                'check': 'DateOfAnnouncement',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '送股(股)-每10股',
                    'En': 'BonusShares',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first',
                },{
                    'n': '转增(股)-每10股',
                    'En': 'TransferOfShares',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '派息(税前)(元)-每10股',
                    'En': 'PreTaxDividend',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '进度',
                    'En': 'Schedule',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '除权除息日',
                    'En': 'ExDividendDate',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股权登记日',
                    'En': 'ShareholdersOfRecordDate',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '红股上市日',
                    'En': 'BonusSharesListedDate',
                    'v':
                    './td[8]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        # 配股信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="sharebonus_2"]//tr[td[1][contains(text(),"-")]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComAllotment',
                'keys': ['HTML_ID','DateOfAnnouncement'],
                'check': 'DateOfAnnouncement',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '配股方案(每10股配股股数)',
                    'En': 'AllotmentOffering',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first',
                },{
                    'n': '配股价格(元)',
                    'En': 'AllotmentPrice',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '基准股本(万股)',
                    'En': 'BenchmarkShareCapital',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '除权日',
                    'En': 'ExRightDate',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股权登记日',
                    'En': 'ShareholdersOfRecordDate',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '缴款起始日',
                    'En': 'PaymentStartDate',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '缴款终止日',
                    'En': 'PaymentEndDate',
                    'v':
                    './td[8]/text()',
                    't': 'xpath_first'
                },{
                    'n': '配股上市日 ',
                    'En': 'AllotmentListedDate',
                    'v':
                    './td[9]/text()',
                    't': 'xpath_first'
                },{
                    'n': '募集资金合计(元)',
                    'En': 'CollectionOfCapital',
                    'v':
                    './td[10]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_ipo(self, response):
        # 上市信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="comInfo1"]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComIpo',
                'keys': ['HTML_ID'],
                'check': 'StockExchange',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '上市地',
                    'En': 'StockExchange',
                    'v':
                    './/td[.//*[contains(text(),"上市地")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '主承销商',
                    'En': 'MainUnderwriter',
                    'v':
                    './/td[.//*[contains(text(),"主承销商")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '承销方式',
                    'En': 'AllotmentPrice',
                    'v':
                    './/td[.//*[contains(text(),"承销方式")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市推荐人',
                    'En': 'ListedRecommendation',
                    'v':
                    './/td[.//*[contains(text(),"上市推荐人")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '每股发行价(元)',
                    'En': 'PricePerShare',
                    'v':
                    './/td[.//*[contains(text(),"每股发行价")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行方式',
                    'En': 'DistributionMode',
                    'v':
                    './/td[.//*[contains(text(),"发行方式")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行市盈率（按发行后总股本）',
                    'En': 'IPO_PE_Ratio',
                    'v':
                    './/td[.//*[contains(text(),"发行市盈率")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '首发前总股本（万股）',
                    'En': 'PreStartTotalEquity',
                    'v':
                    './/td[.//*[contains(text(),"首发前总股本")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '首发后总股本（万股）',
                    'En': 'FirstPostTotalEquity',
                    'v':
                    './/td[.//*[contains(text(),"首发后总股本")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '实际发行量（万股）',
                    'En': 'ActualCirculation',
                    'v':
                    './/td[.//*[contains(text(),"实际发行量")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '预计募集资金（万元）',
                    'En': 'ExpectedFundRaising',
                    'v':
                    './/td[.//*[contains(text(),"预计募集资金")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '实际募集资金合计（万元）',
                    'En': 'ActualFundRaising',
                    'v':
                    './/td[.//*[contains(text(),"实际募集资金合计")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行费用总额（万元）',
                    'En': 'TotalIssueCost',
                    'v':
                    './/td[.//*[contains(text(),"发行费用总额")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '募集资金净额（万元）',
                    'En': 'NetRaisedFunds',
                    'v':
                    './/td[.//*[contains(text(),"募集资金净额")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '承销费用（万元）',
                    'En': 'UnderwritingFee',
                    'v':
                    './/td[.//*[contains(text(),"承销费用")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '招股公告日',
                    'En':'AnnouncementDate',
                    'v':
                    './/td[.//*[contains(text(),"招股公告日")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市日期',
                    'En': 'ListedDate',
                    'v':
                    './/td[.//*[contains(text(),"上市日期")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_lift_a_ban_on_sale(self, response):
        # 限售解禁提取  可能翻页
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="dataTable"]//tr[td[1]//a[string-length(text())=6]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedUnBanOnSale',
                'keys': ['HTML_ID','DateOfUnBanDate'],
                'check': 'HTML_ID',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    './td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    './td[2]/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '解禁日期',
                    'En': 'DateOfUnBanDate',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '解禁数量(万股)',
                    'En': 'UnBanNumbers',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first',
                },{
                    'n': '解禁股流通市值(亿元)',
                    'En': 'UnbanStockCirculationMarketValue',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市批次',
                    'En': 'ListedBatch',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        # 翻页逻辑
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[text()="下一页" and @class="page"]'
                        },
                callback=self.sina_com_lift_a_ban_on_sale,
                headers=self.default_header,
                urlfunc=
                lambda page, response: re.compile('(https?:\/\/.*?&p=)').search(response.url).group(1) + str(page),
                divmod=1,
                flag=True,
                readpage=2,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sina_com_seasoned_new_issue(self, response):
        # 增发新股信息提取    不定序
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[contains(@id,"addStock")]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedSeasonedNewIssue',
                'keys': ['HTML_ID','DateOfAnnouncement','AdditionalType'],
                'check': 'AdditionalType',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './/comment()[contains(string(),"公告日期")]',
                    't': 'xpath_re',
                    're':'(\d{4}-\d{2}-\d{2})'
                },
                {
                    'n': '增发类型',
                    'En': 'AdditionalType',
                    'v':
                    './/td[strong[contains(text(),"增发类型")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '发行价格',
                    'En': 'IssuePrice',
                    'v':
                    './/td[strong[contains(text(),"发行价格")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '货币名称',
                    'En': 'CurrencyEname',
                    'v':
                    './/td[strong[contains(text(),"货币名称")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '募集资金合计',
                    'En': 'CollectionOfFunds',
                    'v':
                    './/td[strong[contains(text(),"募集资金合计")]]/following-sibling::*[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行费用',
                    'En': 'DistributionCost',
                    'v':
                    './/td[strong[contains(text(),"发行费用")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行数量',
                    'En': 'IssueNumber',
                    'v':
                    './/td[strong[starts-with(text(),"发行数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上网发行数量',
                    'En': 'OnlineIssueNumber',
                    'v':
                    './/td[strong[contains(text(),"上网发行数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '向老股东配售数量',
                    'En': 'DistributionToOld',
                    'v':
                    './/td[strong[contains(text(),"向老股东配售数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '向其他公众投资者配售数量',
                    'En': 'DistributionToOhther',
                    'v':
                    './/td[strong[contains(text(),"向其他公众投资者配售数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '网下发行数量',
                    'En': 'DistributionToUnderLine',
                    'v':
                    './/td[strong[contains(text(),"网下发行数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '老股东配售有效申购数量',
                    'En': 'NumberOfEffectiveOld',
                    'v':
                    './/td[strong[contains(text(),"老股东配售有效申购数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '其他公众投资者有效申购户数',
                    'En': 'SubscriptionsOfEffectivePublic',
                    'v':
                    './/td[strong[contains(text(),"其他公众投资者有效申购户数")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '其他公众投资者有效申购数量',
                    'En': 'NumberOfEffectivePublic',
                    'v':
                    './/td[strong[contains(text(),"其他公众投资者有效申购数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '网下发行有效申购户数',
                    'En': 'SubscriptionsOfEffectiveUnderLine',
                    'v':
                    './/td[strong[contains(text(),"网下发行有效申购户数")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '网下机构投资者有效申购数量',
                    'En': 'NumberOfEffectiveUnderLine',
                    'v':
                    './/td[strong[contains(text(),"网下机构投资者有效申购数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_bank_finance(self, response):
        # 银行理财
        # 理财产品
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'id',
                                                   },
                                           callback=self.sina_bank_finance_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://money.finance.sina.com.cn/bank/mall/financingDetail.php?id=' + page,
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'abs',
                        'v': '4760'
                        },
                callback=self.sina_bank_finance,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://money.finance.sina.com.cn/bank/api/json_v2.php/Bank_FinanceService.searchFinaceProd?page=%s&num=20' % page,
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sina_bank_finance_info(self,response):
        # 增发新股信息提取    不定序
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="comp_tb prd_tb"]',    
                't': 'xpath',
                'db': 'CreditDataBase.SinaBankFinance',
                'keys': ['HTML_ID', 'FinancialProductName'],
                'check': 'FinancialProductName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'id=(.+)',
                    't': 'url_re'
                },{
                    'n': '产品名称',
                    'En': 'FinancialProductName',
                    'v':
                    './/*[contains(text(),"产品名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '所属银行',
                    'En': 'AffiliatedBank',
                    'v':
                    './/*[contains(text(),"所属银行")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '投资币种',
                    'En': 'InvestmentCurrency',
                    'v':
                    './/*[contains(text(),"投资币种")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '投资起始金额(元)',
                    'En': 'InitialAmountOfInvestment',
                    'v':
                    './/*[contains(text(),"投资起始金额(元)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '增加购买起始金额(元)',
                    'En': 'IncreaseInitialAmountOfInvestment',
                    'v':
                    './/*[contains(text(),"增加购买起始金额(元)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发售时间',
                    'En': 'SaleStartTime',
                    'v':
                    './/*[contains(text(),"发售时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '停售时间',
                    'En': 'SaleEndTime',
                    'v':
                    './/*[contains(text(),"停售时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '投资天数(天)',
                    'En': 'IssueNumber',
                    'v':
                    './/*[contains(text(),"投资天数(天)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '计息起始日',
                    'En': 'NumberOfInvestmentDays',
                    'v':
                    './/*[contains(text(),"计息起始日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '预期收益(%)',
                    'En': 'ExpectedYield',
                    'v':
                    './/*[contains(text(),"预期收益(%)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '是否保本',
                    'En': 'CapitalPreservation',
                    'v':
                    './/*[contains(text(),"是否保本")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '产品规模',
                    'En': 'ProductScale',
                    'v':
                    './/*[contains(text(),"产品规模")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '到期收益',
                    'En': 'MaturityReturn',
                    'v':
                    './/*[contains(text(),"到期收益")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '同期存款利率差额（10万元）',
                    'En': 'InterestRateDifference',
                    'v':
                    './/*[contains(text(),"同期存款利率差额（10万元）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '预期实际收益计算（10万元）',
                    'En': 'RealIncome',
                    'v':
                    './/*[contains(text(),"预期实际收益计算（10万元）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '投资范围',
                    'En': 'ScopeOfInvestment',
                    'v':
                    './/*[contains(text(),"投资范围")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_Capital(self, response):
        JS = execjs.eval(response.text)
        # 0.沪深股市
        stock_key = JS[1][0]
        # 1.创业板
        cyb_key = JS[0][1]
        # 2.基金
        funds_key = JS[0][2]
        # 3.香港股市 
        HK_stock_key = JS[0][3]
        # 4.债券
        bouns_key = JS[1][4]
        # 5.美国股市
        # 6.外汇
        # 7.期货
        # 8.黄金
        # 9.环球股指
        # 10.板块汇总行情
        for key_list in bouns_key[1]:
            key = key_list[2]
            url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeStockCount?node=%s' % key
            yield scrapy.Request(url,
                headers=self.default_header,
                callback=self.sina_bonds_page_count)

    @SpiderHelp.check_response
    def sina_bonds_page_count(self, response):
        totalpage = math.ceil(int(re.compile('\"(\d+)\"').search(response.text).group(1)) / 40)
        symbol = re.compile('node=(.+)').search(response.url).group(1)
        formatter = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple?page={}&num=40&sort=symbol&asc=1&node=%s&_s_r_a=page' % symbol
        url = formatter.format(1)
        yield _Request(url,
            callback=self.sina_bonds_list,
            headers=self.default_header,
            meta={'page':1,'totalpage': totalpage,'formatter': formatter},
            priority=10000,
            redis_flag=True,
            redis_conn=self.r)

    @SpiderHelp.check_response
    def sina_bonds_list(self, response):
        # 新浪债券列表
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'symbol',
                                                   },
                                           callback=self.sina_bonds_jump,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://money.finance.sina.com.cn/bond/quotes/%s.html' % page,
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'abs',
                        'v': '4760'
                        },
                callback=self.sina_bonds_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

    def sina_bonds_jump(self, response):
        # 基本资料
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[text()="基本资料"]/@href',
                                                   },
                                           callback=self.sina_bonds_basic,
                                           headers=self.default_header,
                                           priority=2000,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req
        # # 发行信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[text()="发行信息"]/@href',
                                                   },
                                           callback=self.sina_bonds_issue,
                                           headers=self.default_header,
                                           priority=2000,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 发行人信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[text()="发行人信息"]/@href',
                                                   },
                                           callback=self.sina_bonds_issuer,
                                           headers=self.default_header,
                                           priority=2000,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 转股条款
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[text()="转股条款"]/@href',
                                                   },
                                           callback=self.sina_bonds_transfer_clause,
                                           headers=self.default_header,
                                           priority=2000,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 利率变动
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[text()="利率变动"]/@href',
                                                   },
                                           callback=self.sina_bonds_interest_rate_change,
                                           headers=self.default_header,
                                           priority=2000,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 转债行权
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[text()="转债行权"]/@href',
                                                   },
                                           callback=self.sina_bonds_transfer_of_debt,
                                           headers=self.default_header,
                                           priority=2000,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

    @SpiderHelp.check_response
    def sina_bonds_basic(self, response):
        # 债券基本信息提取    不定序
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[div[text()="基本资料"]]/table',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsBasic',
                'keys': ['BondsCode','BondsName'],
                'check': 'BondsName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'info\/(.+?)\.html',
                    't': 'url_re'
                },{
                    'n': '债券名称',
                    'En': 'BondsName',
                    'v':
                    './/*[contains(text(),"债券名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '债券简称',
                    'En': 'BondsShortName',
                    'v':
                    './/*[contains(text(),"债券简称")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '债券代码',
                    'En': 'BondsCode',
                    'v':
                    './/*[contains(text(),"债券代码")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '债券类型',
                    'En': 'BondsType',
                    'v':
                    './/*[contains(text(),"债券类型")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '债券面值（元）',
                    'En': 'BondsFacevalue',
                    'v':
                    './/*[contains(text(),"债券面值（元）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '债券年限（年）',
                    'En': 'BondAgeLimit',
                    'v':
                    './/*[contains(text(),"债券年限（年）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '票面利率（%）',
                    'En': 'ParInterestRate',
                    'v':
                    './/*[contains(text(),"票面利率（%）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '到期日',
                    'En': 'DueDate',
                    'v':
                    './/*[contains(text(),"到期日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '兑付日',
                    'En': 'HonourDate',
                    'v':
                    './/*[contains(text(),"兑付日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '摘牌日',
                    'En': 'DelistingDate',
                    'v':
                    './/*[contains(text(),"摘牌日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '计息方式',
                    'En': 'InterestRate',
                    'v':
                    './/*[contains(text(),"计息方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '利率说明',
                    'En': 'InterestRateDescription',
                    'v':
                    './/*[contains(text(),"利率说明")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '付息方式',
                    'En': 'ModeOfInterestPayment',
                    'v':
                    './/*[contains(text(),"付息方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '起息日期',
                    'En': 'DateOfInterestStart',
                    'v':
                    './/*[contains(text(),"起息日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '止息日期',
                    'En': 'DateOfInterestEnd',
                    'v':
                    './/*[contains(text(),"止息日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '付息日期',
                    'En': 'DateOfInterestPayment',
                    'v':
                    './/*[contains(text(),"付息日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '年付息次数',
                    'En': 'InterestPaymentTimesPerYear',
                    'v':
                    './/*[contains(text(),"年付息次数")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行价格（元）',
                    'En': 'IssuePrice',
                    'v':
                    './/*[contains(text(),"发行价格（元）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行规模（亿元）',
                    'En': 'Issuescale',
                    'v':
                    './/*[contains(text(),"发行规模（亿元）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行日期',
                    'En': 'DateOfIssue',
                    'v':
                    './/*[contains(text(),"发行日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市日期',
                    'En': 'DateOfListing',
                    'v':
                    './/*[contains(text(),"上市日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市场所',
                    'En': 'Exchange',
                    'v':
                    './/*[contains(text(),"上市场所")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '信用等级',
                    'En': 'CredictLevel',
                    'v':
                    './/*[contains(text(),"信用等级")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '内部信用增级方式',
                    'En': 'InternalCreditEnhancement',
                    'v':
                    './/*[contains(text(),"内部信用增级方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '外部信用增级方式',
                    'En': 'ExternalCreditEnhancement',
                    'v':
                    './/*[contains(text(),"外部信用增级方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item


    @SpiderHelp.check_response
    def sina_bonds_issue(self, response):
        # 债券发行信息提取    不定序
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[div[text()="发行基本情况"]]/table',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsIssue',
                'keys': ['BondsShortName','HTML_ID'],
                'check': 'BondsShortName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'issue\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '债券简称',
                    'En': 'BondsShortName',
                    'v':
                    './/*[contains(text(),"债券简称及代码")]/following-sibling::td[1]/a[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '债券代码',
                    'En': 'BondsCode',
                    'v':
                    './/*[contains(text(),"债券简称及代码")]/following-sibling::td[1]/a[2]/text()',
                    't': 'xpath_first',
                },{
                    'n': '票面利率/发行参考利率（%）',
                    'En': 'ParInterestRate',
                    'v':
                    './/*[contains(text(),"票面利率")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '债券面值（元）',
                    'En': 'BondsFacevalue',
                    'v':
                    './/*[contains(text(),"债券面值")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '是否公开发行',
                    'En': 'PubliclyIssued',
                    'v':
                    './/*[contains(text(),"是否公开发行")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行价格（元）',
                    'En': 'IssuePrice',
                    'v':
                    './/*[contains(text(),"发行价格")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './/*[contains(text(),"公告日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '招标日期',
                    'En': 'DateOfBidding',
                    'v':
                    './/*[contains(text(),"招标日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '招标方式',
                    'En': 'BiddingMethod',
                    'v':
                    './/*[contains(text(),"招标方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '招标标的',
                    'En': 'BiddingTarget',
                    'v':
                    './/*[contains(text(),"招标标的")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '招标上线（元）',
                    'En': 'UpLineOfTender ',
                    'v':
                    './/*[contains(text(),"招标上线")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '招标下线（元）',
                    'En': 'DownLineOfTender',
                    'v':
                    './/*[contains(text(),"招标下线")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行起始日',
                    'En': 'IssueStartDate',
                    'v':
                    './/*[contains(text(),"发行起始日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行终止日',
                    'En': 'IssueEndDate',
                    'v':
                    './/*[contains(text(),"发行终止日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行方式',
                    'En': 'IssueMethod',
                    'v':
                    './/*[contains(text(),"发行方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '缴款日期',
                    'En': 'DateOfPayment',
                    'v':
                    './/*[contains(text(),"缴款日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '本次实际发行规模（亿元）',
                    'En': 'ActualIssueScale',
                    'v':
                    './/*[contains(text(),"本次实际发行规模")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '网上实际发行规模（亿元）',
                    'En': 'ActualscaleOnline',
                    'v':
                    './/following::td[contains(text(),"网上实际发行规模")][last()-1]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '本次计划发行规模（亿元）',
                    'En': 'ScaleOfPlanissue',
                    'v':
                    './/*[contains(text(),"本次计划发行规模")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '网上实际发行规模（亿元）',
                    'En': 'ActualscaleOnline2',
                    'v':
                    './/following::td[contains(text(),"网上实际发行规模")][last()]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '累计发行规模（亿元）',
                    'En': 'CumulativeIssueScale',
                    'v':
                    './/*[contains(text(),"累计发行规模")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最低申购金额（千元）',
                    'En': 'MinimumPurchaseAmount',
                    'v':
                    './/*[contains(text(),"最低申购金额")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行费用（百万元）',
                    'En': 'DistributionCost',
                    'v':
                    './/*[contains(text(),"发行费用")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行对象',
                    'En': 'IssueObject',
                    'v':
                    './/*[contains(text(),"发行对象")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '主承销商',
                    'En': 'MainUnderwriter',
                    'v':
                    './/*[text()="主承销商"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '副主承销商',
                    'En': 'VicePrincipalUnderwriter',
                    'v':
                    './/*[text()="副主承销商"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '承销方式',
                    'En': 'UnderwriteManner',
                    'v':
                    './/*[contains(text(),"承销方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 


    @SpiderHelp.check_response
    def sina_bonds_issuer(self, response):
        # 债券发行人信息提取    不定序
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[div[contains(text(),"基本情况")]]/table',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsIssuer',
                'keys': ['HTML_ID','CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'issuer\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v':
                    './/*[contains(text(),"公司名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    './/*[contains(text(),"公司简称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '英文名称',
                    'En': 'ComEnglishName',
                    'v':
                    './/*[contains(text(),"英文名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '英文简称',
                    'En': 'ComEshortName',
                    'v':
                    './/*[contains(text(),"英文简称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法人代表',
                    'En': 'NameOfLegalRepresentative',
                    'v':
                    './/*[contains(text(),"法人代表")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '总经理',
                    'En': 'GeneralManager',
                    'v':
                    './/*[contains(text(),"总经理")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v':
                    './/*[contains(text(),"注册地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '办公邮编',
                    'En': 'ZipCode',
                    'v':
                    './/*[contains(text(),"办公邮编")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '办公地址',
                    'En': 'OfficeAddress',
                    'v':
                    './/*[contains(text(),"办公地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司电话',
                    'En': 'OfficePhoneNumber',
                    'v':
                    './/*[contains(text(),"公司电话")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司传真',
                    'En': 'OfficeFaxNumber',
                    'v':
                    './/*[contains(text(),"公司传真")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司电子邮箱',
                    'En': 'OfficeEmailAddress',
                    'v':
                    './/*[contains(text(),"公司电子邮箱")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司网址',
                    'En': 'OfficeWebsite',
                    'v':
                    './/*[contains(text(),"公司网址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v':
                    './/*[contains(text(),"成立日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资本（千万）',
                    'En': 'RegisteredCapital',
                    'v':
                    './/*[contains(text(),"注册资本")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市日期',
                    'En': 'DateOfListing',
                    'v':
                    './/*[contains(text(),"上市日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v':
                    './/*[contains(text(),"经营范围")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '主营业务',
                    'En': 'MainBusiness',
                    'v':
                    './/following::td[contains(text(),"主营业务")][last()-1]',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item  


    @SpiderHelp.check_response
    def sina_bonds_transfer_clause(self, response):
        # 债券转股条款信息提取    不定序
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[div[contains(text(),"转股条款")]]/table',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsTransferClause',
                'keys': ['HTML_ID','TransitionStartDate'],
                'check': 'TransitionStartDate',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'convertItem\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '转换起始日',
                    'En': 'TransitionStartDate',
                    'v':
                    './/*[contains(text(),"转换起始日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '初始转换比例（股/百元）',
                    'En': 'InitialTransitionRatio',
                    'v':
                    './/*[contains(text(),"初始转换比例")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '最新转换比例（股/百元）',
                    'En': 'NewestConversionRatio',
                    'v':
                    './/*[contains(text(),"最新转换比例")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '转换结束日',
                    'En': 'TransitionEndDate',
                    'v':
                    './/*[contains(text(),"转换结束日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '初始转换价格（元）',
                    'En': 'InitialTransitionPrice',
                    'v':
                    './/*[contains(text(),"初始转换价格")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最新转换价格（元）',
                    'En': 'NewestTransitionPrice',
                    'v':
                    './/*[contains(text(),"最新转换价格")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '换股价格调整标准',
                    'En': 'StandardOfTransitionPriceAdjustment',
                    'v':
                    './/*[contains(text(),"换股价格调整标准")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '转股价格确定标准',
                    'En': 'StandardOfTransitionPriceDetermining',
                    'v':
                    './/*[contains(text(),"转股价格确定标准")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '赎回条款',
                    'En': 'RedemptionClause',
                    'v':
                    './/*[contains(text(),"赎回条款")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '回售条款',
                    'En': 'ResaleClause',
                    'v':
                    './/*[contains(text(),"回售条款")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '强制性转股条款',
                    'En': 'MandatoryClause ',
                    'v':
                    './/*[contains(text(),"强制性转股条款")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '转换余股处理',
                    'En': 'ConversionOfSurplusStockTreatment',
                    'v':
                    './/*[contains(text(),"转换余股处理")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '转股价格修正',
                    'En': 'TransferPriceCorrection',
                    'v':
                    './/*[contains(text(),"转股价格修正")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '特别向下修正条款',
                    'En': 'SpecialDownwardClause',
                    'v':
                    './/*[contains(text(),"特别向下修正条款")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 


    @SpiderHelp.check_response
    def sina_bonds_interest_rate_change(self, response):
        # 债券利率变动
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[div[contains(text(),"债券利率变动")]]/table//tr[position()>1]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsInterestRateChange',
                'keys': ['HTML_ID', 'InterestRateStartDate'],
                'check': 'InterestRateStartDate',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'rateChange\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '起息日期',
                    'En': 'InterestRateStartDate',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '止息日期',
                    'En': 'InterestRateEndDate',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first',
                },{
                    'n': '适用利率（%）',
                    'En': 'ApplicableInterestRate',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '利率变更原因',
                    'En': 'CauseOfInterestRatioChange',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '基本利差',
                    'En': 'BasicMargin',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '基准利率',
                    'En': 'BenchmarkInterestRate',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 


    @SpiderHelp.check_response
    def sina_bonds_transfer_of_debt(self, response):
        # 可转债行权
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[contains(text(),"可转债行权")]/following-sibling::table[1]//tr[position()>1]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsConvertibleBondRight',
                'keys': ['HTML_ID', 'DateOfAnnouncement'],
                'check': 'DateOfAnnouncement',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'conversion\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '行权类型',
                    'En': 'RightType',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first',
                },{
                    'n': '截止日期',
                    'En': 'ClosingDate',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '转股价格（元）',
                    'En': 'ConversionStocksPrice',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '本期转股数（万股）',
                    'En': 'NumbersOfThisPeriodConversionStocks',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '累计转股数（万股）',
                    'En': 'TotalNumbersOfConversionStocks',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '累计转股金额（万元）',
                    'En': 'TotalConversionStocksAmount',
                    'v':
                    './td[8]/text()',
                    't': 'xpath_first'
                },{
                    'n': '债券流通金额（万元）',
                    'En': 'BondCirculationAmount',
                    'v':
                    './td[9]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

        # 转股价变动
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[contains(text(),"转股价变动")]/following-sibling::table[1]//tr[position()>1]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ConversionStocksPriceChange',
                'keys': ['HTML_ID', 'DateOfAnnouncement'],
                'check': 'DateOfAnnouncement',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'conversion\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '价格变动类型',
                    'En': 'PriceChangeType',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first',
                },{
                    'n': '转股价格生效日期',
                    'En': 'EffectiveDateOfConversionStocksPrice',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '执行日期',
                    'En': 'ExecutionDate',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '转股价格（元）',
                    'En': 'ConversionStocksPrice',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '转股比例（%）',
                    'En': 'RatioOfConversionStocks',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

        # 回售赎回结果
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[contains(text(),"回售赎回结果")]/following-sibling::table[1]//tr[position()>1]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsRecoveryRedemptionResults',
                'keys': ['HTML_ID', 'DateOfAnnouncement'],
                'check': 'DateOfAnnouncement',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'conversion\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '事件类型',
                    'En': 'EventType',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first',
                },{
                    'n': '赎回金额（万元）',
                    'En': 'RedemptionAmount',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '赎回价格（元/张）',
                    'En': 'RedemptionPrice',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '回收金额（万元）',
                    'En': 'RecoveryAmount',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '回收价格（元/张）',
                    'En': 'RecoveryPrice',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '债券类型（万元）',
                    'En': 'BondsType',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

    @SpiderHelp.check_response
    def sina_futures(self, response):
        # 获取分类参数
        TotalUrl = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQFuturesCount?node=%s'
        nodes = re.compile("\['.+?', '(\w+?)', '\d+?'\]").findall(response.text)
        for node in nodes:
            url = TotalUrl % node
            yield _Request(
                url,
                redis_flag=True,
                redis_conn=self.r,
                callback=self.sina_futures_jumps)

    @SpiderHelp.check_response
    def sina_futures_jumps(self, response):
        # 页面跳转
        node = re.compile('node=(.+)').search(response.url).group(1)
        formater = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQFuturesData?page={}&num=5&sort=position&asc=0&node=%s&base=futures' % node
        match = re.compile('String\(\"(\d+)\"\)').search(response.text)
        url = formater.format(1)
        totalpage =  math.ceil(int(match.group(1)) / 5) if match else 1
        yield self.request(url,
            callback=self.sina_futures_list,
            priority=2000,
            meta={'formatter':formater,'totalpage':totalpage,'proxys':True},
            headers=self.default_header,
            redis_flag=True,
            redis_conn=self.r)

    @SpiderHelp.check_response
    def sina_futures_list(self, response):
        # 新浪 期货列表
        # logger.error(response)
        reqs = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'symbol',
                                                   },
                                           callback=self.sina_futures_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://finance.sina.com.cn/futures/quotes/%s.shtml' % page,
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'abs',
                        'v': '4760'
                        },
                callback=self.sina_futures_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='json')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sina_futures_info(self, response):
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
                    'n': 'Code',
                    'En': 'Code',
                    'v':
                    '//span[@class="code"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '期货名称',
                    'En': 'FuritersName',
                    'v':
                    '//h1[@class="title"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '交易品种',
                    'En': 'ETradingVariety',
                    'v':
                    './/*[contains(text(),"交易品种")]/following-sibling::td[1]/text()',
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

    @SpiderHelp.check_response
    def sina_funds_in(self, response):
        #
        for i in range(2):
            formatter = 'http://app.xincai.com/fund/api/jsonp.json//XinCaiOtherService.getManagerFundInfo?page={}&num=40&sort=NavRate&asc=0&ccode=&date=&type2=%s' % i
            url = formatter.format(1)
            yield self.request(
                        url,
                        meta={'formatter': formatter},
                        redis_flag=REDISFLAG,
                        callback=self.sina_fund_manager_list)

    @SpiderHelp.check_response
    def sina_fund_manager_list(self, response):
        response = response.replace(body=re.compile('(\{.+\})').search(response.text).group(1))
        _configs = [{
            'list': {
                'n': '',
                'v': 'data',    
                't': 'json',
                'db': 'Sina.Sina_Fund_ManagerState',
                'keys': ['ManagerId','State','Bdate'],
                'check': 'ManagerId',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '基金经理姓名',
                    'En': 'Name',
                    'v':
                    'Name',
                    't': 'json'
                },{
                    'n': '基金经理Id',
                    'En': 'ManagerId',
                    'v':
                    'ManagerId',
                    't': 'json'
                },
                {
                    'n': '任职日期', 
                    'En': 'Bdate',
                    'v':
                    'BDate',
                    't': 'json'
                },{
                    'n': '离职时间', # 若Edate 不等于1900-01-01 00:00:00 说明为离职状态
                    'En': 'Edate',
                    'v':
                    'EDate',
                    't': 'json'
                },
                {
                    'n': '是否在职', # 1 在任 2离任
                    'En': 'State',
                    'v':
                    'type2=(\d+)',
                    't': 'url_re'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'total_num'
                        },
                callback=self.sina_fund_manager_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                divmod=40,
                redis_conn=self.r,
                meta={'proxys':True},
                redis_flag=True,
                readpage=16,
                response_type='json')
        for req in reqs:
            yield req

        # # 列表页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'data/ManagerId',
                                                   },
                                           callback=self.sina_fund_manager,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://stock.finance.sina.com.cn/manager/view/mInfo.php?mid=%s' % page,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs2:
            yield req

    @SpiderHelp.check_response
    def sina_fund_manager(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Sina.Sina_Fund_ManagerBasic',
                'keys': ['ManagerName','HTML_ID'],
                'check': 'ManagerName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'mid=(.+)',
                    't': 'url_re'
                },{
                    'n': '基金经理',
                    'En': 'ManagerName',
                    'v':
                    '//td[contains(text(),"基金经理")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '基金经理image',
                    'En': 'ImagePath',
                    'v':
                    '//td[@class="pic"]//@src',
                    't': 'xpath_first'
                },{
                    'n': '年龄', 
                    'En': 'Age',
                    'v':
                    '//td[contains(text(),"年龄")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '学历', 
                    'En': 'Education',
                    'v':
                    '//td[contains(text(),"学历")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '首次任职', 
                    'En': 'FirstTimesHoldThePost',
                    'v':
                    '//td[contains(text(),"首次任职")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '从业时间',
                    'En': 'EmploymentTime',
                    'v':
                    '//td[contains(text(),"从业时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资历排名',
                    'En': 'SeniorityRank',
                    'v':
                    '//td[contains(text(),"资历排名")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '任职公司',
                    'En': 'Moodyhas',
                    'v':
                    '//td[contains(text(),"任职公司")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '任职公司ID',
                    'En': 'MoodyhasId',
                    'v':
                    '//td[contains(text(),"任职公司")]/following-sibling::td[1]/a/@href',
                    't': 'xpath_re',
                    're': 'company\/(.+)\.shtml'
                },{
                    'n': '跳槽次数', 
                    'En': 'JobHopping',
                    'v':
                    '//td[contains(text(),"跳槽次数")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '职业资质', 
                    'En': 'VocationalQualifications',
                    'v':
                    '//td[contains(text(),"职业资质")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '简历', 
                    'En': 'Industry',
                    'v':
                    '//td[contains(text(),"简历")]/following-sibling::td[1]/p/text()|//span[@id="detail"]/text()',
                    't': 'xpath_join'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        _configs = [{
            'list': {
                'n': '',
                'v': '//h3[text()="历史业绩"]/following-sibling::table[1]//tr[position()>1]',    
                't': 'xpath',
                'db': 'Sina.Sina_Fund_ManagerPerformance',
                'keys': ['ProdName','HTML_ID'],
                'check': 'ProdName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'mid=(.+)',
                    't': 'url_re'
                },{
                    'n': '基金经理',
                    'En': 'ManagerName',
                    'v':
                    '//td[contains(text(),"基金经理")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '产品名称', 
                    'En': 'ProdName',
                    'v':
                    './td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '产品ID', 
                    'En': 'ProdId',
                    'v':
                    './td[1]/a/@href',
                    't': 'xpath_re',
                    're': 'quotes\/(.+?)\/'
                },{
                    'n': '任职公司', 
                    'En': 'Moodyhas',
                    'v':
                    './td[2]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '任职公司ID', 
                    'En': 'MoodyhasId',
                    'v':
                    './td[2]/a/@href',
                    't': 'xpath_re',
                    're': 'company\/(.+)\.shtml'
                },{
                    'n': '管理类型', 
                    'En': 'ManagementType',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '任职时间', 
                    'En': 'TenureTime',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '任期回报', 
                    'En': 'TermOfReturn',
                    'v':
                    './td[5]/text()',
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