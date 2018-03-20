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
Headers = {'User-Agent': generate_user_agent(os=('win',))}

MAX = 2**15
from myselector import pdf_to_html



def get_cookies():
    url = 'https://www.licai.com/api/v1/auth/login/pass'
    body = json.dumps({"username":"17600811823","password":"8927968"})
    while True:
        try:
            return requests.put(url,body).cookies.get_dict()
        except BaseException as e:
            logger.info(repr(e))

# 获取登陆cookie
Cookies = get_cookies()

def get_cookie():
    return Cookies

# 此网站封会封禁  限制速度



#redis数据库使用FOFI先进后出的规则 对url进行队列选择
class SinaspiderSpider(_RedisSpider, SpiderHelp):  #,scrapy.Spider
    name = 'licai3'
    start_urls = [
        'https://www.licai.com/simu/'
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
        'DOWNLOAD_DELAY': 3,
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
                cookies=get_cookie(),
                meta={'cookiejar':1},
                redis_flag=True,
                callback=self.licai_in)

    @SpiderHelp.check_response
    def licai_in(self, response):
        # 私募产品 需要cookie

        # yield self.request('https://www.licai.com/simu/jijin.html',
        #     headers=self.default_header,
        #     meta={'cookiejar': response.meta['cookiejar']},
        #     callback=self.licai_prod_list
        #     )

        # # 私募经理 无需cookie
        # yield self.request('https://www.licai.com/simu/jingli.html',
        #     cookies=get_cookie(),
        #     headers=self.default_jheader,
        #     callback=self.licai_manager_list
        #     )

        # 私募公司
        yield self.request('https://www.licai.com/simu/gongsi.html',
            cookies=get_cookie(),
            headers=self.default_jheader,
            callback=self.licai_company_list
            )

    @SpiderHelp.check_response
    def licai_prod_list(self, response):
        yield self.request('https://www.licai.com/api/v1/private/productlist',
            method='POST',
            body=self.licai_prod_data(1),
            headers=self.default_jheader,
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.licai_prod_list2)

    def licai_prod_list2(self, response):
        # 翻译设置
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'result'
                        },
                callback=self.licai_prod_list2,
                headers=self.default_jheader,
                method='POST',
                urlfunc=lambda page, response=None: 'https://www.licai.com/api/v1/private/productlist',
                bodyfunc=self.licai_prod_data,
                redis_conn=self.r,
                redis_flag=True,
                meta={'cookiejar': response.meta['cookiejar']},
                readpage=5,
                flag=True,
                response_type='json')
        for req in reqs:
            yield req

        JS = json.loads(response.text)
        for item in JS['result']:
            url = 'https://www.licai.com/simu/product/%s.html' % item['product_id']
            yield self.request(url,
                headers=self.default_header,
                meta={'cookiejar': response.meta['cookiejar'],**item},
                callback=self.licai_prod_info)
            # return

    def licai_prod_data(self, page=1, response=None):
        return json.dumps({"offset":str(page*50-50),
                   "sortName":"rr_since_this_year",
                   "sortType":'-1',
                   "investment_strategy_1":"0",
                   "investment_strategy_2":"0",
                   "annualized_rr_since_start":"0",
                   "investment_risk":"0",
                   "performance_0":"0",
                   "performance_1":"0",
                   "performance_3":"0",
                   "performance_5":"0",
                   "manager_type":"0",
                   "aum":"0",
                   "duration":"0",
                   "product_status":"0",
                   "keyname":""})

    @SpiderHelp.check_response
    def licai_prod_info(self, response):

        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'GeShang.Licai_Prod',
                'keys': ['ProdName'],
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
                    '\/([^\/]+?)\.s?html',
                    't': 'url_re',
                },{
                    'n': '产品名称',
                    'En': 'ProdName',
                    'v':
                    '//h1/text()',
                    't': 'xpath_first'
                },{
                    'n': '产品类型',
                    'En': 'ProdType',
                    'v':
                    'string(//div[@class="l tb_icon"])',
                    't': 'xpath_first'
                },
                {
                    'n': '年化收益',
                    'En': 'YieldPerYear',
                    'v':'string(.//p[contains(text(),"年化收益")])',
                    't': 'xpath_re',
                    're': '：([\s\S]+)'
                },
                {
                    'n': '私募公司',
                    'En': 'Company',
                    'v':'string(.//p[contains(text(),"私募公司")])',
                    't': 'xpath_re',
                    're': '：([\s\S]+)'
                },
                {
                    'n': '是否备案',
                    'En': 'WherherRecord',
                    'v':'string(.//p[contains(text(),"是否备案")])',
                    't': 'xpath_re',
                    're': '：([\s\S]+)'
                },
                {
                    'n': '近一年收益',
                    'En': 'YieldThisYear',
                    'v':'string(.//p[contains(text(),"近一年收益")])',
                    't': 'xpath_re',
                    're': '：([\s\S]+)'
                },
                {
                    'n': '复权净值',
                    'En': 'RehabilitationNet',
                    'v':'string(.//p[contains(text(),"复权净值")])',
                    't': 'xpath_re',
                    're': '：([\s\S]+)'
                },
                {
                    'n': '夏普比率',
                    'En': 'SharpeRatio',
                    'v':'string(.//p[contains(text(),"夏普比率")])',
                    't': 'xpath_re',
                    're': '：([\s\S]+)'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v':'string(.//p[contains(text(),"成立日期")])',
                    't': 'xpath_re',
                    're': '：([\s\S]+)'
                },
                {
                    'n': '基金经理',
                    'En': 'FundManger',
                    'v':'string(.//p[contains(text(),"基金经理")])',
                    't': 'xpath_re',
                    're': '：([\s\S]+)'
                },
                {
                    'n': '产品状态',
                    'En': 'ProdState',
                    'v':
                    'string(.//*[starts-with(text(),"产品状态")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '发行平台',
                    'En': 'IssuePlatform',
                    'v':
                    'string(.//*[starts-with(text(),"发行平台")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '托管银行',
                    'En': 'TrusteeshipAgency',
                    'v':'string(.//*[starts-with(text(),"托管银行")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '证券经纪',
                    'En': 'ShareBroking',
                    'v':'string(.//*[starts-with(text(),"证券经纪")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '基金性质',
                    'En': 'FundNature',
                    'v':'string(.//*[starts-with(text(),"基金性质")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '投资策略',
                    'En': 'InvestmentStrategy',
                    'v':'string(.//*[starts-with(text(),"投资策略")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '投资子策略',
                    'En': 'InvestmentSubStrategy',
                    'v':'string(.//*[starts-with(text(),"投资子策略")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '是否结构化',
                    'En': 'WhetherStructured',
                    'v':'string(.//*[starts-with(text(),"是否结构化")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '开放日',
                    'En': 'OpenDay',
                    'v':'string(.//*[starts-with(text(),"开放日")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '认购起点',
                    'En': 'SubscribeStartPoint',
                    'v':'string(.//*[starts-with(text(),"认购起点")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '认购费',
                    'En': 'SubscribeFee',
                    'v':'string(.//*[starts-with(text(),"认购费")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '退出费用',
                    'En': 'ExitFee',
                    'v':'string(.//*[starts-with(text(),"退出费用")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '浮动管理费',
                    'En': 'FloatManagementFee',
                    'v':'string(.//*[starts-with(text(),"浮动管理费")]/following-sibling::td[1])',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
            # print(item)

    def licai_manager_data(self, page=1, response=None):
        return json.dumps({
            "num":"50",
            "offset":str(page*50-50),
            "wherestring":"",
            "orderstring":"\"is_show_nv\":-1,\"order\":-1,\"rr_since_start\":-1"})

    @SpiderHelp.check_response
    def licai_manager_list(self, response):
        yield self.request('https://www.licai.com/api/v1/private/managerlist',
            method='POST',
            body=self.licai_manager_data(1),
            headers=self.default_jheader,
            # meta={'cookiejar': response.meta['cookiejar']},
            callback=self.licai_manager_list2)

    @SpiderHelp.check_response
    def licai_manager_list2(self, response):
        # 翻译设置
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'result/total'
                        },
                callback=self.licai_manager_list2,
                headers=self.default_jheader,
                method='POST',
                urlfunc=lambda page, response=None: response.url,
                bodyfunc=self.licai_manager_data,
                redis_conn=self.r,
                redis_flag=True,
                divmod=50,
               # meta={'cookiejar': response.meta['cookiejar']},
                readpage=16,
                response_type='json')
        for req in reqs:
            yield req

        JS = json.loads(response.text)
        for item in JS['result']['items']:
            url = 'https://www.licai.com/simu/manager/%s.html' % item['manager_id']
            yield self.request(url,
                headers=self.default_header,
                meta=item,
                callback=self.licai_manager_info)

    def licai_manager_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'GeShang.Licai_Manager',
                'keys': ['HTML_ID'],
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
                    'manager_id',
                    't': 'meta',
                },{
                    'n': '姓名',
                    'En': 'Name',
                    'v':
                    '//h1/text()',
                    't': 'xpath_first'
                },{
                    'n': '私募公司',
                    'En': 'Company',
                    'v':
                    'company_abbr_name',
                    't': 'meta'
                },{
                    'n': '私募公司ID',
                    'En': 'CompanyID',
                    'v':
                    'company_id',
                    't': 'meta'
                },
                {
                    'n': '派系',
                    'En': 'ManagerType',
                    'v':'manager_type',
                    't': 'meta'
                },
                {
                    'n': '从业年限',
                    'En': 'Duration',
                    'v':'duration',
                    't': 'meta',
                },
                {
                    'n': '学历',
                    'En': 'Education',
                    'v':'education',
                    't': 'meta',
                },
                {
                    'n': '实习日期',
                    'En': 'PracticeDate',
                    'v':'practice_date',
                    't': 'meta'
                },
                {
                    'n': '毕业院校',
                    'En': 'Graduate',
                    'v':'string(//p[contains(text(),"毕业院校")]/span)',
                    't': 'xpath_first'
                },
                {
                    'n': '过往从业机构',
                    'En': 'PastEmploymentAgencies',
                    'v':'string(//p[contains(text(),"过往从业机构")]/span[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '人物简介',
                    'En': 'Profile',
                    'v':'string(//div[@id="jj1"])',
                    't': 'xpath_re',
                    're': '^([\s\S]+?)(?=业绩表现|公募基金时期管理业绩|$)'
                },
                {
                    'n': 'Image',
                    'En': 'image',
                    'v':
                    '//li[@class="tx_box"]//@src',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
            # print(item)

    def licai_company_data(self, page=1, response=None):
        return json.dumps({"num":"50",
            "offset":str(page*50-50),
            "wherestring":"",
            "orderstring":"\"order\":-1,\"rr_since_start\":-1"})

    @SpiderHelp.check_response
    def licai_company_list(self, response):
        yield self.request('https://www.licai.com/api/v1/private/companylist',
            method='POST',
            body=self.licai_company_data(1),
            headers=self.default_jheader,
            # meta={'cookiejar': response.meta['cookiejar']},
            callback=self.licai_company_list2)

    @SpiderHelp.check_response
    def licai_company_list2(self, response):
        # 翻译设置
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'result/total'
                        },
                callback=self.licai_company_list2,
                headers=self.default_jheader,
                method='POST',
                urlfunc=lambda page, response=None: response.url,
                bodyfunc=self.licai_company_data,
                redis_conn=self.r,
                redis_flag=True,
                divmod=50,
               # meta={'cookiejar': response.meta['cookiejar']},
                readpage=16,
                response_type='json')
        for req in reqs:
            yield req

        JS = json.loads(response.text)
        for item in JS['result']['items']:
            url = 'https://www.licai.com/simu/company/%s.html' % item['company_id']
            yield self.request(url,
                headers=self.default_header,
                meta=item,
                callback=self.licai_company_info)

    @SpiderHelp.check_response
    def licai_company_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'GeShang.Licai_Company',
                'keys': ['HTML_ID'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'company_id',
                    't': 'meta',
                },{
                    'n': '私募公司',
                    'En': 'Company',
                    'v':
                    '//h1/text()',
                    't': 'xpath_first'
                },{
                    'n': '私募公司ID',
                    'En': 'CompanyID',
                    'v':
                    'company_id',
                    't': 'meta'
                },
                {
                    'n': '成立时间',
                    'En': 'SetupTime',
                    'v':'establishment_date_accurate',
                    't': 'meta'
                },
                {
                    'n': '核心人物',
                    'En': 'CoreFigure',
                    'v':'string(//p[contains(text(),"核心人物：")])',
                    't': 'xpath_re',
                    're':'：(.+)'
                },
                {
                    'n': '注册资本',
                    'En': 'RegisteredCapital',
                    'v':'string(//p[contains(text(),"注册资本：")])',
                    't': 'xpath_re',
                    're':'：(.+)'
                },
                {
                    'n': '所在地',
                    'En': 'AreaName',
                    'v':'location',
                    't': 'meta'
                },
                {
                    'n': '是否备案',
                    'En': 'WhetherRecord',
                    'v':'string(//p[contains(text(),"是否备案：")])',
                    't': 'xpath_re',
                    're':'：([\s\S]+)'
                },
                {
                    'n': '基金规模类型',
                    'En': 'Scale',
                    'v':'string(//div[contains(text(),"基金规模类型")]/following-sibling::div[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '公司介绍',
                    'En': 'Profile',
                    'v':'string(//div[span[text()="公司介绍"]]/following-sibling::div[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '投资理念',
                    'En': 'InvestmentIdea',
                    'v':
                    'string(//div[span[text()="投资理念"]]/following-sibling::div[1])',
                    't': 'xpath_first'
                },
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
