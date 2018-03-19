# -*- coding: utf-8 -*-
import scrapy
import os
import sys
import urllib.parse
import re
import requests
import json
import time
BASEDIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# 加入环境变量  临时性非全局
sys.path.append(BASEDIR)
sys.path.append('../')

from SpiderHelp import SpiderHelp
from RedisHelp import _Request,_RedisSpider,logger

conn_flag = False
REDISFLAG = True

class DaikuanSpider(_RedisSpider, SpiderHelp):
    name = 'daikuan'
    start_urls = ['http://www.credithunan.gov.cn/search/enterpriseCreditTips2.do']
    state = {}
    redis_flag=True
    redis_key = 'qqq:starturls'
    signel = 1
    host = '10.1.18.35'

    def __init__(self):
        # 获取本爬虫redis_key
        super(DaikuanSpider,self).__init__()

    def _start_requests(self):
        req = []
        for url in self.start_urls:
            if url == 'http://www.credithunan.gov.cn/search/enterpriseCreditTips2.do':
                req.append(self.request(
                    url,
                    redis_flag=REDISFLAG,
                    callback=self.hunan_start))
        return req

    def hunan_start(self, response):
        Microfinance = response.xpath('//a[text()="小额贷款公司数据"]/@href').extract()
        FinancingGuarantee = response.xpath('//a[text()="融资担保公司许可信息(设立/撤销)"]/@href').extract()
        for url in Microfinance:
            yield scrapy.Request(response.urljoin(url),
                                callback=self.hunan_Microfinance)
        for url in FinancingGuarantee:
            yield scrapy.Request(response.urljoin(url),
                callback=self.hunan_FinancingGuarantee)

    def hunan_Microfinance(self, response):
        # size 5066
        '''
        湖南小额贷款
        '''
        # 搜索页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 're_findall',
                                                    #正则匹配公司 个体名称
                                                   'v': 'E\$(.+?)\$',
                                                   },
                                           callback=self.hunan_Microfinance_info,
                                           headers=self.default_header,
                                           method='POST',
                                           urlfunc=
                                           lambda page, response: 'http://www.credithunan.gov.cn/page/info/promptsDetail.jsp',
                                           bodyfunc=lambda page,response:urllib.parse.urlencode({'tableId': '76DBCAE2AA431BE7EA52F50F8ECB7802','cId':page,'inTime':time.strftime("%a %b %d %Y %H:%M:%S")+' GMT+0800 (中国标准时间)'},encoding='GBK'),
                                           priority=100,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs2:
            yield req
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': 'totalRecord:(\d+)'
                        },
                callback=self.hunan_Microfinance,
                method='POST',
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://www.credithunan.gov.cn/page/info/promptsProxy.jsp?startrecord=%s&endrecord=%s&perpage=20&totalRecord=5066' % (page*20-19,page*20),
                bodyfunc=
                lambda page, response=None: urllib.parse.urlencode({'id': '76DBCAE2AA431BE7EA52F50F8ECB7802','inTime':time.strftime("%Y-%m-%d %H:%M:%S")}),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                response_type='xpath')
        for req in reqs:
            yield req

    def hunan_Microfinance_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Hunan_MicrofinanceData',
                'keys': ['HTML_ID'],
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
                    'cId',
                    't': 'request_body'
                },
                {
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v':
                    '//td[contains(text(),"企业名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v':
                    '//td[contains(text(),"统一社会信用代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法人代表',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//td[contains(text(),"法人代表")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册（营业）地址',
                    'En': 'RegisteredAddress',
                    'v': '//td[contains(text(),"注册（营业）地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '备案情况',
                    'En': 'Record',
                    'v':
                    '//td[contains(text(),"备案情况")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '邮政编码',
                    'En': 'ZipCode',
                    'v': '//td[contains(text(),"邮政编码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司联系电话',
                    'En': 'ContactNumber',
                    'v': '//td[contains(text(),"公司联系电话")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册资金',
                    'En': 'RegisteredCapital',
                    'v': '//td[contains(text(),"注册资金")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法人手机号码',
                    'En': 'PhoneNumberOfLegal',
                    'v': '//td[contains(text(),"法人手机号码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '批复文号',
                    'En': 'ReplyNumber',
                    'v': '//td[contains(text(),"批复文号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                }, {
                    'n': '批复时间',
                    'En': 'ReplyDate',
                    'v': '//td[contains(text(),"许可时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                }, {
                    'n': '备案登记证号码',
                    'En': 'RecordNumber',
                    'v': '//td[contains(text(),"行政许可证编号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                }, {
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v': '//td[contains(text(),"经营范围")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '更新时间',
                    'En': 'LastUpdateTime',
                    'v': '更新时间：\s*?(.+?)\'',
                    't': 'regex1'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def hunan_FinancingGuarantee(self, response):
        # size 5066
        '''
        湖南融资担保
        '''
        # 搜索页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 're_findall',
                                                    #正则匹配公司 个体名称
                                                   'v': 'E\$(.+?)\$',
                                                   },
                                           callback=self.hunan_FinancingGuarantee_info,
                                           headers=self.default_header,
                                           method='POST',
                                           urlfunc=
                                           lambda page, response: 'http://www.credithunan.gov.cn/page/info/promptsDetail.jsp',
                                           bodyfunc=lambda page,response:urllib.parse.urlencode({'tableId': 'F2CD2715CFB122FB882C77FFAE21C5C3AA3246C8626E78E8','cId':page,'inTime':time.strftime("%a+%b+%d+%Y+%H:%M:%S")+'+GMT+0800+(中国标准时间)'},encoding='GBK'),
                                           priority=100,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs2:
            yield req
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': 'totalRecord:(\d+)'
                        },
                callback=self.hunan_FinancingGuarantee,
                method='POST',
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://www.credithunan.gov.cn/page/info/promptsProxy.jsp?startrecord=%s&endrecord=%s&perpage=20&totalRecord=2576' % (page*20-19,page*20),
                bodyfunc=
                lambda page, response=None: urllib.parse.urlencode({'id': 'F2CD2715CFB122FB882C77FFAE21C5C3AA3246C8626E78E8','inTime':time.strftime("%Y-%m-%d %H:%M:%S")}),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                response_type='xpath')
        for req in reqs:
            yield req

    def hunan_FinancingGuarantee_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Hunan_FinancingGuaranteeData',
                'keys': ['HTML_ID'],
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
                    'cId',
                    't': 'request_body'
                },
                {
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v':
                    '//td[contains(text(),"企业名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v':
                    '//td[contains(text(),"统一社会信用代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '批准情况',
                    'En': 'Ratification',
                    'v':
                    '//td[contains(text(),"批准情况")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册（营业）地址',
                    'En': 'RegisteredAddress',
                    'v': '//td[contains(text(),"注册（营业）地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司联系电话',
                    'En': 'ContactNumber',
                    'v': '//td[contains(text(),"公司联系电话")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '邮政编码',
                    'En': 'ZipCode',
                    'v': '//td[contains(text(),"邮政编码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册资金',
                    'En': 'RegisteredCapital',
                    'v': '//td[contains(text(),"注册资金")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法人代表',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//td[contains(text(),"法人代表")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法人手机号码',
                    'En': 'PhoneNumberOfLegal',
                    'v': '//td[contains(text(),"法人手机号码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '批准文号',
                    'En': 'ApprovalNumber',
                    'v': '//td[contains(text(),"批准文号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                }, {
                    'n': '许可时间',
                    'En': 'LicenseDate',
                    'v': '//td[contains(text(),"许可时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                }, {
                    'n': '行政许可证编号',
                    'En': 'LicenseNumber',
                    'v': '//td[contains(text(),"行政许可证编号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                }, {
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v': '//td[contains(text(),"经营范围")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '更新时间',
                    'En': 'LastUpdateTime',
                    'v': '更新时间：\s*?(.+?)\'',
                    't': 'regex1'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def parse(self, response):
        pass


if __name__ == '__main__':
    DaikuanSpider.put_redis()