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
    name = 'jrj'
    start_urls = [
                'http://insurance.jrj.com.cn/action/SearchIPJson.jspa', # 保险产品
                'http://bank.jrj.com.cn/txtBank/banklist_1.html', # 银行列表
                'http://insurance.jrj.com.cn/html/ic/list/ics-0.shtml', # 保险公司
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
            if url == 'http://insurance.jrj.com.cn/action/SearchIPJson.jspa':
                req.append(self.request(
                    url,
                    method='POST',
                    body=self.post_data(1),
                    redis_flag=REDISFLAG,
                    headers=self.default_header,
                    callback=self.jrj_insurance_in))
            elif url == 'http://bank.jrj.com.cn/txtBank/banklist_1.html':
                req.append(self.request(
                    url,
                    redis_flag=REDISFLAG,
                    headers=self.default_header,
                    callback=self.jrj_bank_in))
            elif url == 'http://insurance.jrj.com.cn/html/ic/list/ics-0.shtml':
                req.append(self.request(
                    url,
                    redis_flag=REDISFLAG,
                    headers=self.default_header,
                    callback=self.jrj_insurance_org_in))
        return req

    @SpiderHelp.check_response
    def jrj_insurance_in(self, response):
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'items/id',
                                                   },
                                           callback=self.jrj_insurance_prod_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://insurance.jrj.com.cn/html/ip/detail/ip_%s.shtml' % page,
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                method='POST',
                config={'t': 'json',
                        'v': 'pageCount',
                        },
                callback=self.jrj_insurance_in,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://insurance.jrj.com.cn/action/SearchIPJson.jspa',
                bodyfunc=self.post_data,
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='json')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def jrj_insurance_prod_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//table[@class="dt3"]',    
                    't': 'xpath',
                    'db': 'Jrj.Jrj_InsuranceProd',
                    'keys': ['ProdName','ComName'],
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
                        'ip_(.+?)\.shtml',
                        't': 'url_re'
                    },{
                        'n': '产品名称',
                        'En': 'ProdName',
                        'v':
                        './/*[text()="产品名称"]/following-sibling::*[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': 'Logo',
                        'En': 'Logo',
                        'v':
                        './/@src',
                        't': 'xpath_first'
                    },{
                        'n': '保险类别',
                        'En': 'Category',
                        'v':
                        './/*[text()="保险类别"]/following-sibling::*[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '保险公司',
                        'En': 'ComName',
                        'v':
                        './/*[text()="保险公司"]/following-sibling::*[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '投保年龄',
                        'En': 'Age',
                        'v':
                        './/*[text()="投保年龄"]/following-sibling::*[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '缴费方式',
                        'En': 'PayMethod',
                        'v':
                        './/*[text()="缴费方式"]/following-sibling::*[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '缴费期限',
                        'En': 'PayTerm',
                        'v':
                        './/*[text()="缴费期限"]/following-sibling::*[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '保障期限',
                        'En': 'GuaranteeTerm',
                        'v':
                        './/*[text()="保障期限"]/following-sibling::*[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '产品特色',
                        'En': 'ProdFeatures',
                        'v':
                        './/*[text()="产品特色"]/following-sibling::*[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '保险责任',
                        'En': 'Responsibility',
                        'v':
                        'string(.//table[@class="dt3"]//*[text()="保险责任"]/following-sibling::*[1])',
                        't': 'xpath_first'
                    }
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def jrj_bank_in(self, response):
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//td//a/@href',
                                                   're': 'banknews_(.+?).shtml'
                                                   },
                                           callback=self.jrj_bank_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://bank.jrj.com.cn/txtBank/bankdetail_%s.html' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                method='POST',
                config={'t': 'xpath_first',
                        'v': '//div[@class="pn dot1"]/a[last()-1]/text()',
                        },
                callback=self.jrj_bank_in,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://bank.jrj.com.cn/txtBank/banklist_%s.html' % page,
                bodyfunc=self.post_data,
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def jrj_bank_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//table',    
                    't': 'xpath',
                    'db': 'Jrj.Jrj_BankInfo',
                    'keys': ['FullName'],
                    'check': 'FullName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID',
                        'En': 'HTML_ID',
                        'v':
                        'bankdetail_(.+?)\.html',
                        't': 'url_re'
                    },{
                        'n': '银行全称',
                        'En': 'FullName',
                        'v':
                        './/*[starts-with(text(),"银行全称")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '银行简称',
                        'En': 'ShortName',
                        'v':
                        './/*[starts-with(text(),"银行简称")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '组织形式',
                        'En': 'OrganForm',
                        'v':
                        './/*[starts-with(text(),"组织形式")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '设立日期',
                        'En': 'SetupTime',
                        'v':
                        './/*[starts-with(text(),"设立日期")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '注册资本(万元)',
                        'En': 'RegCapital',
                        'v':
                        './/*[starts-with(text(),"注册资本(万元)")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '法人代表',
                        'En': 'LegalRepresentative',
                        'v':
                        './/*[starts-with(text(),"法人代表")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '注册地址',
                        'En': 'RegAddr',
                        'v':
                        './/*[starts-with(text(),"注册地址")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '总行地址',
                        'En': 'HeadAddr',
                        'v':
                        './/*[starts-with(text(),"总行地址")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '邮政编码',
                        'En': 'ZipCode',
                        'v':
                        './/*[starts-with(text(),"邮政编码")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '电话',
                        'En': 'PhoneNumber',
                        'v':
                        './/*[starts-with(text(),"电话")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '传真',
                        'En': 'FaxNumber',
                        'v':
                        './/*[starts-with(text(),"传真")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '网址',
                        'En': 'Website',
                        'v':
                        './/*[starts-with(text(),"网址")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '公司Email',
                        'En': 'ComEmail',
                        'v':
                        './/*[starts-with(text(),"公司Email")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '公司简介',
                        'En': 'ComProfile',
                        'v':
                        './/*[starts-with(text(),"公司简介")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    }
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def jrj_insurance_org_in(self, response):
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//div[@class="win2 bd1"]//div[@class="right"]//@href',
                                                   },
                                           callback=self.jrj_insurance_org_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://insurance.jrj.com.cn%s' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '共有(\d+)家保险公司',
                        },
                callback=self.jrj_insurance_org_in,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://insurance.jrj.com.cn/html/ic/list/ics-%s.shtml' %  int(page)-1,
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def jrj_insurance_org_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//table',    
                    't': 'xpath',
                    'db': 'Jrj.Jrj_BankInfo',
                    'keys': ['ComName'],
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
                        'ic_(.+?)\.s?html',
                        't': 'url_re'
                    },{
                        'n': '公司简称',
                        'En': 'ComName',
                        'v':
                        '//*[contains(text(),"公司简称")]/strong/text()',
                        't': 'xpath_first'
                    },{
                        'n': 'Logo',
                        'En': 'Logo',
                        'v':
                        '//div[@class="wrap2"]//img[not(contains(@src,"error"))]/@src',
                        't': 'xpath_first'
                    },{
                        'n': '英文名称',
                        'En': 'EnName',
                        'v':
                        'string(.//em[contains(text(),"英文名称")]/following-sibling::node()[1])',
                        't': 'xpath_first'
                    },{
                        'n': '公司属性',
                        'En': 'OrganForm',
                        'v':
                        'string(.//em[contains(text(),"公司属性")]/following-sibling::node()[1])',
                        't': 'xpath_first'
                    },{
                        'n': '注册资本（万元）',
                        'En': 'SetupTime',
                        'v':
                        'string(.//em[contains(text(),"注册资本")]/following-sibling::node()[1])',
                        't': 'xpath_first'
                    },{
                        'n': '设立时间',
                        'En': 'RegCapital',
                        'v':
                        'string(.//em[contains(text(),"设立时间")]/following-sibling::node()[1])',
                        't': 'xpath_first'
                    },{
                        'n': '注册地址',
                        'En': 'LegalRepresentative',
                        'v':
                        '//td[contains(text(),"注册地址")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '办公地址',
                        'En': 'RegAddr',
                        'v':
                        '//td[contains(text(),"办公地址")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '邮政编码',
                        'En': 'RegAddr',
                        'v':
                        '//td[contains(text(),"邮政编码")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '传　　真',
                        'En': 'RegAddr',
                        'v':
                        '//td[contains(text(),"传　　真")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '电　　话',
                        'En': 'HeadAddr',
                        'v':
                        '//td[contains(text(),"电　　话")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '公司Email',
                        'En': 'ZipCode',
                        'v':
                        '//td[contains(text(),"公司Email")]/following-sibling::td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '公司简介',
                        'En': 'ZipCode',
                        'v':
                        '//div[@class="cont3"]/p/text()',
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
