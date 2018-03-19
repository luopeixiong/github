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

'''
http://simudata.howbuy.com/login.htm
name:howbuyi
psw:808080
提交:登录

'''
conn_flag = False
REDISFLAG = True
TODAY = time.strftime('%Y-%m-%d')
Headers = {'User-Agent': generate_user_agent(os=('win',))}
Cookies = {"simu_qualified_v2": "5"}
MAX = 2**15
from myselector import pdf_to_html


#redis数据库使用FOFI先进后出的规则 对url进行队列选择
class SinaspiderSpider(_RedisSpider, SpiderHelp):  #,scrapy.Spider
    name = 'howbuy2'
    start_urls = [
        'https://simu.howbuy.com'
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

    def _start_requests(self):
        req = []
        logger.info('Start Crawl Spider %s at rediskey %s' % (self.name,self.redis_key))
        for url in self.start_urls:
            yield self.request(url,
                headers=self.default_header,
                redis_flag=True,
                cookies=Cookies,
                meta={'cookiejar':1},
                callback=self.howbuy_in)

    @SpiderHelp.check_response        
    def howbuy_in(self, response):
        # # 私募产品 
        yield self.request('https://simu.howbuy.com/mlboard.htm',
            method='POST',
            body=self.howbuy_mlboard_data()(),
            headers=self.default_header,
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.howbuy_mlboard_list)

        # 私募经理
        yield self.request('https://simu.howbuy.com/manager/',
            headers=self.default_header,
            method='POST',
            body=self.howbuy_manager_data()(),
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.howbuy_manager_list)

        # 私募公司
        yield self.request('https://simu.howbuy.com/company/',
            headers=self.default_header,
            method='POST',
            body=self.howbuy_company_data()(),
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.howbuy_company_list)

        # 公募经理
        yield self.request('https://www.howbuy.com/fund/manager/',
            headers=self.default_header,
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.howbuy_public_manager_list)

        # 公募产品
        yield self.request('https://www.howbuy.com/fund/fundranking/',
            headers=self.default_header,
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.howbuy_public_prod_list)

        # 公募公司
        yield self.request('https://www.howbuy.com/fund/company/',
            headers=self.default_header,
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.howbuy_public_company_list)

    @SpiderHelp.check_response
    def howbuy_public_company_list(self, response):
        urls = ('https://www.howbuy.com/fund/company/%s/files/' % url for url in re.compile('/fund/company/(\d+)/').findall(response.text))
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                callback=self.howbuy_public_company_info)

    @SpiderHelp.check_response
    def howbuy_public_company_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Howbuy.Howbuy_PublicCompany',
                'keys': ['HTML_ID'],
                'check': 'ComName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    '\/([^\/]+?)\/files\/',
                    't': 'url_re',
                },{
                    'n': '公司简称',
                    'En': 'ComName',
                    'v':
                    '//div[@class="fund_name ftYahei fl"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司全称',
                    'En': 'ComFullName',
                    'v':
                    'string(//td[contains(text(),"公司名称")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '组织形式',
                    'En': 'OrganizationalForm',
                    'v': 'string(//td[contains(text(),"组织形式")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '注册资本',
                    'En': 'RegisteredCapital',
                    'v': 'string(//td[contains(text(),"注册资本")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '总经理',
                    'En': 'GeneralManager',
                    'v':'string(//td[contains(text(),"总经理")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '法定代表人',
                    'En': 'LegalMan',
                    'v':'string(//td[contains(text(),"法定代表人")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '董事长',
                    'En': 'Chairman',
                    'v': 'string(//td[contains(text(),"董事长")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '办公地址',
                    'En': 'OfficeAddress',
                    'v': 'string(//td[contains(text(),"办公地址")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v': 'string(//td[contains(text(),"注册地址")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '公司电话',
                    'En': 'ComPhoneNumber',
                    'v': 'string(//td[contains(text(),"公司电话")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '公司传真',
                    'En': 'ComFax',
                    'v': 'string(//td[contains(text(),"公司传真")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '电子邮箱',
                    'En': 'ComEmail',
                    'v': 'string(//td[contains(text(),"电子邮箱")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '公司网址',
                    'En': 'ComWebSite',
                    'v': 'string(//td[contains(text(),"公司网址")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '客服电话',
                    'En': 'ServerTelephone',
                    'v': 'string(//td[contains(text(),"客服电话")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '公司旗下产品数',
                    'En': 'ProdNumbers',
                    'v': 'string(//td[contains(text(),"公司旗下产品数")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '旗下基金经理数',
                    'En': 'ManagerNumbers',
                    'v': 'string(//td[contains(text(),"旗下基金经理数")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '公司资产规模',
                    'En': 'CapitalScale',
                    'v': 'string(//td[contains(text(),"公司资产规模")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '主要人员数量',
                    'En': 'MajorPersonnelNumber',
                    'v': 'count(//div[@id="nTab401_0"]/div)',
                    't': 'xpath_first'
                },{
                    'n': '投资决策委员会成员数量',
                    'En': 'PolicyDecisionNumbers',
                    'v': 'count(//div[@id="nTab401_1"]/div)',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def howbuy_public_prod_list(self, response):
        urls = ('https://www.howbuy.com/fund/ajax/gmfund/fundsummary.htm?jjdm=%s' % url for url in set(re.compile('/fund/(\d+)/').findall(response.text)))
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                callback=self.howbuy_public_prod_info)

    @SpiderHelp.check_response
    def howbuy_public_prod_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Howbuy.Howbuy_PublicProd',
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
                    '//td[contains(text(),"基金代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '基金简称',
                    'En': 'Name',   
                    'v': '//td[contains(text(),"基金简称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '基金全称',
                    'En': 'FullName',
                    'v': '//td[contains(text(),"基金全称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '基金类型',
                    'En': 'FundType',
                    'v': 'string(//td[contains(text(),"基金类型")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '基金状态',
                    'En': 'State',
                    'v': 'string(//td[contains(text(),"基金状态")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '基金公司',
                    'En': 'Company',
                    'v': 'string(//td[contains(text(),"基金公司")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '基金管理费',
                    'En': 'FundManagementFee',
                    'v': 'string(//td[contains(text(),"基金管理费")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '首募规模',
                    'En': 'InitialRecruitmentScale',
                    'v': 'string(//td[contains(text(),"首募规模")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '托管银行',
                    'En': 'TrusteeBank',
                    'v': 'string(//td[contains(text(),"托管银行")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': 'string(//td[contains(text(),"成立日期")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '交易状态',
                    'En': 'TradingState',
                    'v': 'string(//td[contains(text(),"交易状态")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '基金经理', 
                    'En': 'FundManager',
                    'v': '//td[contains(text(),"基金经理")]/following-sibling::td[1]/*/text()',
                    't': 'xpath_join,'
                },{
                    'n': '投资目标', 
                    'En': 'InvestmentTarget',
                    'v': 'string(//div[text()="投资目标"]/following-sibling::div[1])',
                    't': 'xpath_first'
                },{
                    'n': '投资范围', 
                    'En': 'InvestmentFields',
                    'v': 'string(//div[text()="投资范围"]/following-sibling::div[1])',
                    't': 'xpath_first'
                },{
                    'n': '投资策略', 
                    'En': 'InvestmentStrategy',
                    'v': 'string(//div[text()="投资策略"]/following-sibling::div[1])',
                    't': 'xpath_first'
                },{
                    'n': '收益分配原则', 
                    'En': 'IncomePrinciple',
                    'v': 'string(//div[text()="收益分配原则"]/following-sibling::div[1])',
                    't': 'xpath_first'
                },{
                    'n': '风险收益特征', 
                    'En': 'CharacteristicsOfRiskIncome',
                    'v': 'string(//div[text()="风险收益特征"]/following-sibling::div[1])',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            _item = item.copy()
            url = 'https://www.howbuy.com/fund/ajax/gmfund/fundrate.htm?jjdm=%s' % item['result']['HTML_ID']
            yield self.request(url,
                headers=self.default_header,
                meta=item['result'],
                callback=self.howbuy_public_prod_info2)

    def howbuy_public_prod_info2(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Howbuy.Howbuy_PublicProd',
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
                    'HTML_ID',
                    't': 'meta',
                },{
                    'n': '基金简称',
                    'En': 'Name',   
                    'v': 'Name',
                    't': 'meta'
                },{
                    'n': '基金全称',
                    'En': 'FullName',
                    'v': 'FullName',
                    't': 'meta'
                },{
                    'n': '基金类型',
                    'En': 'FundType',
                    'v': 'FundType',
                    't': 'meta'
                },
                {
                    'n': '基金状态',
                    'En': 'State',
                    'v': 'State',
                    't': 'meta'
                },
                {
                    'n': '基金公司',
                    'En': 'Company',
                    'v': 'Company',
                    't': 'meta'
                },
                {
                    'n': '基金管理费',
                    'En': 'FundManagementFee',
                    'v': 'FundManagementFee',
                    't': 'meta'
                },
                {
                    'n': '首募规模',
                    'En': 'InitialRecruitmentScale',
                    'v': 'InitialRecruitmentScale',
                    't': 'meta'
                },
                {
                    'n': '托管银行',
                    'En': 'TrusteeBank',
                    'v': 'TrusteeBank',
                     't': 'meta'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': 'SetupTime',
                    't': 'meta'
                },
                {
                    'n': '交易状态',
                    'En': 'TradingState',
                    'v': 'TradingState',
                    't': 'meta'
                },
                {
                    'n': '基金经理', 
                    'En': 'FundManager',
                    'v': 'FundManager',
                    't': 'meta'
                },{
                    'n': '投资目标', 
                    'En': 'InvestmentTarget',
                    'v': 'InvestmentTarget',
                    't': 'meta'
                },{
                    'n': '投资范围', 
                    'En': 'InvestmentFields',
                    'v': 'InvestmentFields',
                    't': 'meta'
                },{
                    'n': '投资策略', 
                    'En': 'InvestmentStrategy',
                    'v': 'InvestmentStrategy',
                    't': 'meta'
                },{
                    'n': '收益分配原则', 
                    'En': 'IncomePrinciple',
                    'v': 'IncomePrinciple',
                    't': 'meta'
                },{
                    'n': '风险收益特征', 
                    'En': 'CharacteristicsOfRiskIncome',
                    'v': 'CharacteristicsOfRiskIncome',
                    't': 'meta'
                },
                {
                    'n': '基金托管费',
                    'En': 'FundCustodianFee',
                    'v': 'string(//td[contains(text(),"基金托管费")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '最新份额',
                    'En': 'LatestShare',
                    'v': 'string(//td[contains(text(),"最新份额")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '最新规模', 
                    'En': 'LatestScale',
                    'v': 'string(//td[contains(text(),"最新规模")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '申购起点', 
                    'En': 'PurchaseStartingPoint',
                    'v': 'string(//td[contains(text(),"申购起点")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '定投起点', 
                    'En': 'InvestmentStartingPoint',
                    'v': 'string(//td[contains(text(),"定投起点")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '日累计申购限额',
                    'En': 'DailyPurchaseQuotas',
                    'v': 'string(//td[contains(text(),"日累计申购限额")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '首次购买',
                    'En': 'FirstPurchase',
                    'v': 'string(//td[contains(text(),"首次购买")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '追加购买',
                    'En': 'AdditionalPurchase',
                    'v': 'string(//td[contains(text(),"追加购买")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '申购金额（万元）', 
                    'En': 'PurchaseAmount',
                    'v': 'string(//td[contains(text(),"申购金额")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '申购费率', 
                    'En': 'PurchaseRates',
                    'v': 'string(//td[contains(text(),"申购费率")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '持有年限', 
                    'En': 'HoldingYears',
                    'v': 'string(//td[contains(text(),"持有年限")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '赎回费率', 
                    'En': 'RedemptionRate',
                    'v': 'string(//td[contains(text(),"赎回费率")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '单笔最小赎回份额', 
                    'En': 'MinimumRedemptionShare',
                    'v': 'string(//td[contains(text(),"单笔最小赎回份额")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '账户最低保留份额', 
                    'En': 'MinimumReservedShare',
                    'v': 'string(//td[contains(text(),"账户最低保留份额")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '销售服务费率',
                    'En': 'SalesServiceRate',
                    'v': 'string(//td[contains(text(),"销售服务费率")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '基金管理费率',
                    'En': 'FundManagementRate',
                    'v': 'string(//td[contains(text(),"基金管理费率")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '基金托管费率', 
                    'En': 'FundTrusteeshipRate',
                    'v': 'string(//td[contains(text(),"基金托管费率")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def howbuy_public_manager_list(self, response):
        urls = (response.urljoin(url) 
            for url in re.compile('/fund/manager/\d+/').findall(response.text))
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                callback=self.howbuy_public_manager_info)

    @SpiderHelp.check_response
    def howbuy_public_manager_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Howbuy.Howbuy_PublicManager',
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
                    '\/([^\/]+?)\/$',
                    't': 'url_re',
                },{
                    'n': '姓名',
                    'En': 'Name',   
                    'v': '//div[@class="manager_name"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '当前所在公司',
                    'En': 'ComName',
                    'v': 'string(//li[contains(text(),"当前所在公司: ")]/*[1])',
                    't': 'xpath_first'
                },{
                    'n': '最擅长的基金类型',
                    'En': 'GoodAtType',
                    'v': 'string(//li[contains(text(),"擅长的基金类型:")]/*[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '首次任职时间',
                    'En': 'FirstOfficeTime',
                    'v': 'string(//td[contains(text(),"首次任职时间")]/following-sibling::td[1])',
                    't': 'xpath_join,'
                },
                {
                    'n': '任基金经理时间',
                    'En': 'BecomeFundManagerTime',
                    'v': 'string(//td[contains(text(),"任基金经理时间")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '历任公司数',
                    'En': 'NumberOfSuccessiveCompanies',
                    'v': 'string(//td[contains(text(),"历任公司数")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '跳槽频率',
                    'En': 'FrequencyHoppingFrequency',
                    'v': 'string(//td[contains(text(),"跳槽频率")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '历史管理基金数',
                    'En': 'HisManagerFundNums',
                    'v': 'string(//td[contains(text(),"历史管理基金数")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '从业年均回报',
                    'En': 'YieldPerYear',
                    'v': 'string(//td[contains(text(),"从业年均回报")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '简介',
                    'En': 'Profile',
                    'v': 'string(//div[@class="des_con"])',
                    't': 'xpath_first'
                },
                {
                    'n': '历史过往',
                    'En': 'PastExperience',
                    'v': 'string(//div[@class="content_des_main"])',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def howbuy_company_data(self,totalpage=145):
        def data(page=1, response=None):
            return urllib.parse.urlencode(
                {
                'orderType':'Desc',
                'sortField':'hb1nscclzyjj',
                'ejflsccl':'',
                'djbh':'',
                'skey':'',
                'page':str(page),
                'perPage':'100',
                'allPage':str(totalpage),
                'targetPage':''
                })
        return data

    @SpiderHelp.check_response
    def howbuy_company_list(self, response):
        # 翻页
        _totalpage = response.meta.get('totalpage') 
        totalpage = _totalpage if _totalpage else int(response.xpath('//*[@id="allPage"]/@value').extract_first()) or 1
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//*[@id="allPage"]/@value'
                        },
                callback=self.howbuy_company_list,
                method='POST',
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.url,
                bodyfunc=self.howbuy_manager_data(totalpage),
                meta={'cookiejar': response.meta['cookiejar']},
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # 解析产品页
        urls = (response.urljoin(url) for url in response.xpath('//div[@class="fund_list"]//tr[@class="tr_normal"]/td[2]//@href[string(.)!="#"]').extract())
        for url in urls:
            yield scrapy.Request(url,
                priority=MAX,
                meta={'cookiejar': response.meta['cookiejar']},
                callback=self.howbuy_company_info)

    @SpiderHelp.check_response
    def howbuy_company_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Howbuy.Howbuy_Company',
                'keys': ['HTML_ID'],
                'check': 'ComName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    '\/([^\/]+?)\/$',
                    't': 'url_re',
                },{
                    'n': '公司名称',
                    'En': 'ComName',
                    'v': '//h2/text()',
                    't': 'xpath_first'
                },{
                    'n': '备案证号',
                    'En': 'RecordNumber',
                    'v': 'string(//li[contains(text(),"备案证号：")]/*[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '核心人物',
                    'En': 'CoreFigure',
                    'v': '//li[contains(text(),"核心人物：")]/*/text()',
                    't': 'xpath_join,'
                },
                {
                    'n': '所在区域',
                    'En': 'AreaName',
                    'v': 'string(//li[contains(text(),"所在区域：")]/*[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '旗下基金',
                    'En': 'FundNumbers',
                    'v':'string(//li[contains(text(),"旗下基金：")]/*[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': 'string(//li[contains(text(),"成立日期：")]/*[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '注册资本',
                    'En': 'RegisteredCapital',
                    'v': 'string(//li[contains(text(),"注册资本：")]/*[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '公司类型',
                    'En': 'CompanyType',
                    'v': 'string(//li[contains(text(),"公司类型：")])',
                    't': 'xpath_re',
                    're': '：(.+)'
                },
                {
                    'n': '投资理念',
                    'En': 'InvestmentIdea',
                    'v': 'string(//div[text()="投资理念"]/following-sibling::div[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '成立时间',
                    'En': 'SetupYears',
                    'v': 'string(//div[@id="company_intro1"]//*[@class="situation"]/li[2])',
                    't': 'xpath_first'
                },
                {
                    'n': '投研团队',
                    'En': 'ResearchTeam',
                    'v': 'string(//div[@id="company_intro1"]//*[@class="situation"]/li[3])',
                    't': 'xpath_first'
                },
                {
                    'n': '基金经理人数',
                    'En': 'ManagerNumbers',
                    'v': 'string(//div[@id="company_intro1"]//*[@class="situation"]/li[5])',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def howbuy_manager_data(self, totalpage=53):
        def data(page=1, response=None):
            return urllib.parse.urlencode(
                {
                'cynxRang':'',
                'orderType':'Desc',
                'sortField':'hb1nscclzyjj',
                'ejflsccl':'',
                'jjjlly':'',
                'skey':'',
                'page':str(page),
                'perPage':'100',
                'allPage':str(totalpage),
                'targetPage':''
                })
        return data

    @SpiderHelp.check_response 
    def howbuy_manager_list(self, response):
        # 翻页
        _totalpage = response.meta.get('totalpage') 
        totalpage = _totalpage if _totalpage else int(response.xpath('//*[@id="allPage"]/@value').extract_first()) or 1
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//*[@id="allPage"]/@value'
                        },
                callback=self.howbuy_manager_list,
                method='POST',
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.url,
                bodyfunc=self.howbuy_manager_data(totalpage),
                meta={'cookiejar': response.meta['cookiejar']},
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # 解析产品页
        urls = (response.urljoin(url) for url in response.xpath('//div[@class="fund_list"]//tr/td[2]//a[contains(@href,"manager")]/@href').extract())
        for url in urls:
            yield scrapy.Request(url,
                priority=MAX,
                meta={'cookiejar': response.meta['cookiejar']},
                callback=self.howbuy_manager_info)

    def howbuy_manager_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Howbuy.Howbuy_Manager',
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
                    '\/([^\/]+?)\.s?html',
                    't': 'url_re',
                },{
                    'n': '经理名称',
                    'En': 'Name',
                    'v':
                    '//div[@class="manager_name"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '所在公司',
                    'En': 'Company',
                    'v': 'string(//li[contains(text(),"所在公司:")]/*[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '擅长类型',
                    'En': 'GoodAtType',
                    'v': 'string(//li[contains(text(),"擅长类型: ")]/*[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '所获奖项',
                    'En': 'Awards',
                    'v':'string(//li[contains(text(),"所获奖项: ")]/*[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '简介',
                    'En': 'Profile',
                    'v':'string(//div[p[contains(text(),"简介")]]/following-sibling::div[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '从业年限',
                    'En': 'PractitionersYears',
                    'v': 'string(//td[text()="从业年限"]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '任职私募年限',
                    'En': 'PrivatePlacementYears',
                    'v': 'string(//td[text()="任职私募年限"]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '履历背景',
                    'En': 'BackgroundOfResume',
                    'v': 'string(//td[text()="履历背景"]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '任职私募日期',
                    'En': 'PrivatePlacementDate',
                    'v': 'string(//td[text()="任职私募日期"]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '年均回报',
                    'En': 'YieldPerYear',
                    'v': 'string(//td[text()="年均回报"]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '过往履历',
                    'En': 'PastExperience',
                    'v': 'string(//div[@class="content_des_con fl"])',
                    't': 'xpath_re',
                    're': '过往履历：([\s\S]+)'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response  
    def howbuy_mlboard_list(self, response):
        # 翻页

        _totalpage = response.meta.get('totalpage') 
        totalpage = _totalpage if _totalpage else int(response.xpath('//*[@id="allPage"]/@value').extract_first()) or 1
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//*[@id="allPage"]/@value'
                        },
                callback=self.howbuy_mlboard_list,
                method='POST',
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.url,
                bodyfunc=self.howbuy_mlboard_data(totalpage),
                meta={'cookiejar': response.meta['cookiejar']},
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # 解析产品页
        urls = (response.urljoin(url) for url in response.xpath('//table[@id="spreadDetails"]//tr/td[3]//@href').extract())
        for url in urls:
            yield scrapy.Request(url,
                priority=MAX,
                meta={'cookiejar': response.meta['cookiejar']},
                callback=self.howbuy_mlboard_info)

    @SpiderHelp.check_response  
    def howbuy_mlboard_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Howbuy.Howbuy_Prod',
                'keys': ['HTML_ID'],
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
                    '\/([^\/]+?)\/$',
                    't': 'url_re',
                },{
                    'n': '产品名称',
                    'En': 'ProdName',
                    'v':
                    '//h1/text()',
                    't': 'xpath_first'
                },{
                    'n': '累计净值',
                    'En': 'AccumulatedNet',
                    'v': 'string(//p[contains(text(),"累计净值:")]/*[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '基金公司',
                    'En': 'Company',
                    'v': 'string(//p[contains(text(),"基金公司:")]/*[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '基金经理',
                    'En': 'Manager',
                    'v':'string(//p[contains(text(),"基金经理:")]/*[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '基金全称',
                    'En': 'ProdFullName',
                    'v':'string(//td[contains(text(),"基金全称")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '基金类型',
                    'En': 'FundType',
                    'v': 'string(//td[contains(text(),"基金类型")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '组织形式',
                    'En': 'OrganizationalForm',
                    'v': 'string(//td[contains(text(),"组织形式")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '托管银行',
                    'En': 'TrusteeBank',
                    'v': 'string(//td[contains(text(),"托管银行")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '开放日期',
                    'En': 'OpenDay',
                    'v': 'string(//td[contains(text(),"开放日期")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '币种',
                    'En': 'Currency',
                    'v': 'string(//td[contains(text(),"币种")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '封闭期',
                    'En': 'ClosedPeriod',
                    'v': 'string(//td[contains(text(),"封闭期")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '备案号',
                    'En': 'RecordNumber',
                    'v': 'string(//td[contains(text(),"备案号")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': 'string(//td[contains(text(),"成立日期")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '结构形式',
                    'En': 'StructuralStyle',
                    'v': 'string(//td[contains(text(),"结构形式")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '基金发行人',
                    'En': 'Issuer',
                    'v': 'string(//td[contains(text(),"基金发行人")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '基金状态',
                    'En': 'State',
                    'v': 'string(//td[contains(text(),"基金状态")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '净值单位',
                    'En': 'NetValueUnit',
                    'v': 'string(//td[contains(text(),"净值单位")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '准封闭期',
                    'En': 'QuasiClosedPeriod',
                    'v': 'string(//td[contains(text(),"准封闭期")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
                {
                    'n': '风险等级',
                    'En': 'RiskGradE',
                    'v': 'string(//td[contains(text(),"风险等级")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def howbuy_mlboard_data(self,totalpage=1784):
        def data(page=1, response=None):
            return urllib.parse.urlencode(
                {'orderType':'Desc',
                'sortField':'hb1n',
                'ejfl':'',
                'sylx':'J',
                'gzkxd':'1',
                'jgxs':'',
                'skey':'',
                'zsbz':'',
                'page':str(page),
                'perPage':'100',
                'allPage':str(totalpage),
                'targetPage':''})
        return data

def main():
    SinaspiderSpider.put_redis()

if __name__=='__main__':
    main()
    # def iter_max_min(iters):
    #     x = y = None
    #     for item in iters:
    #         _max,_min = max(item),min(item)
    #         if not x or _max > x:
    #             x = _max
    #         if not y or _min < y:
    #             y = _min
    #     return x, y

    # print(iter_max_min(((1,2),(3,4),(5,6))))
