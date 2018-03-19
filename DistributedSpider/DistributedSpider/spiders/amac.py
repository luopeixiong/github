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
Cookies = {'.ASPXANONYMOUS':'pdtC5gfC0wEkAAAAOWIzZDNiMGEtYjUzOS00YzYyLWEyZTctNWM2OTdmOGM2ZDcz0'}
MAX = 2**15
from myselector import pdf_to_html

'''
redis数据库使用FOFI先进后出的规则 对url进行队列选择
'''

class SinaspiderSpider(_RedisSpider, SpiderHelp):  #,scrapy.Spider
    name = 'amac'
    start_urls = [
        'http://www.amac.org.cn/'
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
                callback=self.amac_in)

    @SpiderHelp.check_response
    def amac_in(self, response):
        reqs = []
        # 证券公司私募产品备案确认函  47*20
        reqs.append(self.request('http://www.amac.org.cn/xxgs/zqgs/index.shtml',
            redis_flag=True,
            callback=self.amac_Confirmation_record))

        # 不予登记机构  79
        reqs.append(self.request('http://www.amac.org.cn/xxgs/bydjjg/',
            redis_flag=True,
            callback=self.amac_non_egistration))

        # 纪律处分  21
        reqs.append(self.request('http://www.amac.org.cn/xxgs/jlcf/',
            redis_flag=True,
            callback=self.amac_disciplinary_sanction))

        # 黑名单 blacklis 17
        reqs.append(self.request('http://www.amac.org.cn/xxgs/hmd/',
            redis_flag=True,
            callback=self.amac_blacklis))

        # 私募基金管理人  22899
        reqs.append(self.request('http://gs.amac.org.cn/amac-infodisc/res/pof/manager/index.html',
            redis_flag=True,
            callback=self.amac_private_fund_manager))

        # 私募基金管理人基金产品  84546
        reqs.append(self.request('http://gs.amac.org.cn/amac-infodisc/res/pof/fund/index.html',
            redis_flag=True,
            callback=self.amac_private_fund_prod))

        # 从业机构 9类
        reqs.append(self.request('http://www.amac.org.cn/xxgs/cyjggs/',
            redis_flag=True,
            callback=self.amac_employment_agency))

        # 从业人员 15W
        reqs.append(self.request('http://person.amac.org.cn/pages/registration/amac-publicity-report.html',
            redis_flag=True,
            callback=self.amac_employee))

        # 私募基金服务机构 3类 82
        reqs.append(self.request('http://fo.amac.org.cn/amac/allNotice.do',
            redis_flag=True,
            callback=self.amac_servers))

        # 证券公司私募产品备案信息公示----证券公司私募产品 7446+
        reqs.append(self.request('http://ba.amac.org.cn/pages/amacWeb/web-list.html',
            redis_flag=True,
            callback=self.amac_Management_plan))

        # 撤销管理人登记的名单
        reqs.append(self.request('http://www.amac.org.cn/xxgs/cxdj/',
            redis_flag=True,
            callback=self.amac_Manager_revocation))

        # 账户公示
        reqs.append(self.request('http://www.amac.org.cn/xxgs/zhgs/382728.shtml',
            redis_flag=True,
            callback=self.amac_Account_publicity))

        # 资产支持专项计划备案确认函公示
        reqs.append(self.request('http://www.amac.org.cn/xxgs/zczczxjhbaqrhgs/',
            redis_flag=True,
            callback=self.amac_Asset_recognition))

        # 期货资管产品备案信息公示
        reqs.append(self.request('http://ba.amac.org.cn/pages/amacWeb/qh-web-list.html',
            redis_flag=True,
            callback=self.amac_Futures_management))

        # 基金专户备案  43234
        reqs.append(self.request('http://gs.amac.org.cn/amac-infodisc/res/fund/account/index.html',
            redis_flag=True,
            callback=self.amac_special_account))

        # 证券公司直投基金  496
        reqs.append(self.request('http://gs.amac.org.cn/amac-infodisc/res/aoin/product/index.html',
            redis_flag=True,
            callback=self.amac_Sc_Direct_investment_fund))

        # 证券公司私募投资基金
        reqs.append(self.request('http://gs.amac.org.cn/amac-infodisc/res/pof/subfund/index.html',
            redis_flag=True,
            callback=self.amac_SC_private_investment_fund))
        # 资产支持专项计划
        reqs.append(self.request('http://ba.amac.org.cn/pages/amacWeb/abs-web-list.html',
            redis_flag=True,
            callback=self.amac_Asset_support_special_plan))
        return reqs
    
    # @SpiderHelp.check_response
    def amac_Confirmation_record(self, response):
        yield self.response_try(response)
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '\/(\d+)页'
                        },
                callback=self.amac_Confirmation_record,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://www.amac.org.cn/xxgs/zqgs/index_%s.shtml' % (page-1),
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req
        # 确认函
        urls = (response.urljoin(url) for url in response.xpath('//*[@class="newsName"]//@href').extract())
        for url in urls:
            yield scrapy.Request(url,
                priority=MAX,
                callback=self.Confirmation_record)
    
    # @SpiderHelp.check_response
    def Confirmation_record(self, response):
        yield self.response_try(response)
        # 证券公司私募产品备案确认函 信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'AMAC.Amac_PrivateProductRecordConfirmationLetter',
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
                    '\/([^\/]+?)\.shtml',
                    't': 'url_re'
                },
                {
                    'n': '标题',
                    'En': 'Title',
                    'v':
                    '//div[@class="ldT"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '日期',
                    'En': 'Date',
                    'v': '//div[@class="ldDate"]/text()',
                    't': 'xpath_re',
                    're': '：(.+)'
                },
                {
                    'n': '文号',
                    'En': 'DocNo',
                    'v': '//div[@class="ldContent"]/p[contains(text(),"函")][1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司',
                    'En': 'Company',
                    'v': '//div[@class="ldContent"]/p[contains(text(),"：")][1]/text()',
                    't': 'xpath_re',
                    're':'(.+)：'
                },
                {
                    'n': '正文',
                    'En': 'Content',
                    'v': '//div[@class="ldContent"]/p[re:test(text(),"根据|你公司")]/text()',
                    't': 'xpath_join'
                },
                {
                    'n': '发布单位',
                    'En': 'ReleaseAgency',
                    'v': '//div[@class="ldContent"]/p[@align="right" and contains(text(),"年")][1]/preceding-sibling::p[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '生效日期',
                    'En': 'EffectiveDate',
                    'v': '//div[@class="ldContent"]/p[@align="right" and contains(text(),"年")][1]/text()',
                    't': 'xpath_first'
                },
               
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def amac_non_egistration(self, response):
        yield self.response_try(response)
        # 不予登记机构 暂无翻页
        urls = (response.urljoin(url) for url in response.xpath('//*[@class="newsName"]//@href').extract())
        for url in urls:
            yield scrapy.Request(url,
                priority=MAX,
                callback=self.amac_non_egistration_list)

    # @SpiderHelp.check_response
    def amac_non_egistration_list(self, response):
        yield self.response_try(response)
        # 不予登记机构 信息提取 
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//table//tr[td][position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_NonRegistrationInstitution',
                'keys': ['Company','FromUrl'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '不予登记的申请机构',
                    'En': 'Company',
                    'v':
                    './td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '机构组织机构代码',
                    'En': 'OrganCode',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '不予登记日期',
                    'En': 'NonRegistrationDate',
                    'v': './td[3]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '不予登记情形',
                    'En': 'Reason',
                    'v': './td[4]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '出具法律意见书的律师事务所',
                    'En': 'LawFirm',
                    'v': './td[5]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '经办律师姓名',
                    'En': 'Lawyer',
                    'v': './td[6]/text()',
                    't': 'xpath_join,'
                },
                {
                    'n': '发布日期',
                    'En': 'PublishDate',
                    'v': '//div[@class="ldDate"]/text()',
                    't': 'xpath_re',
                    're': '：(.+)'
                },
                {
                    'n': '来源',
                    'En': 'FromUrl',
                    'v': 'url',
                    't': 'url'
                },
               
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    # @SpiderHelp.check_response
    def amac_disciplinary_sanction(self, response):
        yield self.response_try(response)
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '\/(\d+)页'
                        },
                callback=self.amac_disciplinary_sanction,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://www.amac.org.cn/xxgs/jlcf/index_%s.shtml' % (page-1),
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # 纪律处分 
        urls = (response.urljoin(url) for url in response.xpath('//*[@class="newsName"]//@href').extract())
        for url in urls:
            yield scrapy.Request(url,
                priority=MAX,
                callback=self.amac_disciplinary_sanction_info)

    # @SpiderHelp.check_response
    def amac_disciplinary_sanction_info(self, response):
        yield self.response_try(response)
        # 纪律处分 信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'AMAC.Amac_DisciplinarySanction',
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
                    '\/([^\/]+?)\.shtml',
                    't': 'url_re'
                },{
                    'n': '当事人',
                    'En': 'Objects',
                    'v':
                    '//div[@class="ldT"]/text()',
                    't': 'xpath_re',
                    're': '(?:\（|注销)(.*)(?:\）|私募)'
                },
                {
                    'n': '标题',
                    'En': 'Title',
                    'v':
                    '//div[@class="ldT"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '日期',
                    'En': 'Date',
                    'v': '//div[@class="ldDate"]/text()',
                    't': 'xpath_re',
                    're': '：(.+)'
                },{
                    'n': '正文',
                    'En': 'Content',
                    'v': '//div[@class="ldContent"]//text()[./self::node()/parent::*[local-name()!="a"]]',
                    't': 'xpath_join',
                },
                {
                    'n': '附件',
                    'En': 'Enclosure',
                    'v': '//div[@class="ldContent"]//@href',
                    't': 'xpath_first'
                },{
                    'n': '附件标题',
                    'En': 'EnclosureTitle',
                    'v': '//div[@class="ldContent"]//a/text()',
                    't': 'xpath_first'
                },
                
               
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    # @SpiderHelp.check_response
    def amac_blacklis(self, response):
        yield self.response_try(response)
        # 黑名单
        urls = (response.urljoin(url) for url in response.xpath('//*[@class="newsName"]//@href').extract())
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                priority=MAX,
                callback=self.amac_blacklis_info)

        # 暂无翻页
    
    # @SpiderHelp.check_response
    def amac_blacklis_info(self, response):
        yield self.response_try(response)
        # 黑名单 信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//table//tr[position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_Blacklis',
                'keys': ['HTML_ID','Name'],
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
                    '\/([^\/]+?)\.shtml',
                    't': 'url_re'
                },{
                    'n': '处分时间',
                    'En': 'Date',
                    'v':
                    './td[1][p]/p/text()|./td[1][not(p)]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '姓名',
                    'En': 'Name',
                    'v':
                    './td[last()=4][position()=2 and not(p)]//text()|./td[last()=4][position()=2 and p]/p/text()|./td[last()=3][2]/p/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '任职机构和职务',
                    'En': 'Company_Position',
                    'v': './td[last()=4][3]//text()',
                    't': 'xpath_join'
                },{
                    'n': '纪律处分',
                    'En': 'DocNo',
                    'v': './td[last()]/p[.//a]//a/text()|./td[last()]/p[not(.//a)]/text()',
                    't': 'xpath_first',
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @property
    def amac_postdata(self):
        return json.dumps({})

    # @SpiderHelp.check_response
    def amac_private_fund_manager(self, response):
        yield self.response_try(response)
        url = 'http://gs.amac.org.cn/amac-infodisc/api/pof/manager?rand=%.18f&page=%s&size=100' % (random.random(),1)
        yield self.request(url,
            method='POST',
            body=self.amac_postdata,
            headers=self.default_jheader,
            callback=self.amac_private_fund_manager_list)

    # @SpiderHelp.check_response
    def amac_private_fund_manager_list(self, response):
        yield self.response_try(response)
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages'
                        },
                callback=self.amac_private_fund_manager_list,
                headers=self.default_jheader,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://gs.amac.org.cn/amac-infodisc/api/pof/manager?rand=%.18f&page=%s&size=100' % (random.random(),page-1),
                bodyfunc=lambda page,response=None:self.amac_postdata,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='json')
        for req in reqs:
            yield req

        # 私募基金管理人 
        JS = json.loads(response.text)
        items = JS['content']
        for item in items:
            url = 'http://gs.amac.org.cn/amac-infodisc/res/pof/manager/%s.html' % item['id']
            yield self.request(url,
                headers=self.default_header,
                meta=item,
                callback=self.amac_private_fund_manager_info
                )
    
    # @SpiderHelp.check_response
    def amac_private_fund_manager_info(self, response):
        yield self.response_try(response)
        # 私募基金管理人 信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'AMAC.Amac_PrivateFundManager',
                'keys': ['HTML_ID'],
                'check': 'fundManagerName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                'n': 'HTML_ID',
                'En': 'HTML_ID',
                'v': 'manager\/(.+?)\.s?html',
                't': 'url_re'
            }, {
                'n':
                '基金管理人全称(中文)',
                'En':
                'fundManagerName',
                'v':
                '//tr[td[contains(text(),"基金管理人全称(中文)")]]/td[@class="td-content"]/div[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '基金管理人全称(英文)',
                'En':
                'fundManagerEname',
                'v':
                '//tr[td[contains(text(),"基金管理人全称(英文)")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '登记编号',
                'En':
                'RegistrationNumber',
                'v':
                '//tr[td[contains(text(),"登记编号")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '组织机构代码',
                'En':
                'OrganizationCode',
                'v':
                '//tr[td[contains(text(),"组织机构代码")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '登记时间',
                'En':
                'RegistrationDate',
                'v':
                '//tr[td[contains(text(),"登记时间")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '成立时间',
                'En':
                'setup_date',
                'v':
                '//tr[td[contains(text(),"成立时间")]]/td[@class="td-content"][2]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '注册地址',
                'En':
                'RegisteredAddress',
                'v':
                '//tr[td[contains(text(),"注册地址")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '办公地址',
                'En':
                'OfficeAddress',
                'v':
                '//tr[td[contains(text(),"办公地址")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '注册资本(万元)(人民币)',
                'En':
                'RegisteredCapital',
                'v':
                '//tr[td[contains(text(),"注册资本(万元)(人民币)")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '实缴资本(万元)(人民币)',
                'En':
                'PaidInCapital1',
                'v':
                '//tr[td[contains(text(),"实缴资本(万元)(人民币)")]]/td[@class="td-content"][2]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '企业性质',
                'En':
                'EnterpriseNature',
                'v':
                '//tr[td[contains(text(),"企业性质")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '注册资本实缴比例',
                'En':
                'PaidInProportion',
                'v':
                '//tr[td[contains(text(),"注册资本实缴比例")]]/td[@class="td-content"][2]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '机构类型',
                'En':
                'MechanismType',
                'v':
                '//tr[td[contains(text(),"机构类型")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '业务类型',
                'En':
                'BusinessType',
                'v':
                '//tr[td[contains(text(),"业务类型")]]/td[@class="td-content"][2]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '员工人数',
                'En':
                'EmployeesNumber',
                'v':
                '//tr[td[contains(text(),"员工人数")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n': '机构网址',
                'En': 'InstitutionalWebsite',
                'v': "机构网址.*?gotoWebsite\(\'(.*?)\'\)",
                't': 'regex1'
            }, {
                'n':
                '是否为会员',
                'En':
                'IsMember',
                'v':
                '//tr[td[contains(text(),"是否为会员")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '当前会员类型',
                'En':
                'MemberType',
                'v':
                '//tr[td[contains(text(),"当前会员类型")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '入会时间',
                'En':
                'InitiationDate',
                'v':
                '//tr[td[contains(text(),"入会时间")]]/td[@class="td-content"][2]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '法律意见书状态',
                'En':
                'LegalOpinionsStatus',
                'v':
                '//tr[td[contains(text(),"法律意见书状态")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '法定代表人/执行事务合伙人(委派代表)姓名',
                'En':
                'LegalRepresentative',
                'v':
                '//tr[td[contains(text(),"法定代表人/执行事务合伙人(委派代表)姓名")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '是否有从业资格',
                'En':
                'IsQualification',
                'v':
                '//tr[td[contains(text(),"是否有从业资格")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '资格取得方式',
                'En':
                'QualificationMethod',
                'v':
                '//tr[td[contains(text(),"资格取得方式")]]/td[@class="td-content"][2]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '机构信息最后更新时间',
                'En':
                'LastUpdateDate',
                'v':
                '//tr[td[contains(text(),"机构信息最后更新时间")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '特别提示信息',
                'En':
                'SpecialInformation',
                'v':
                '//tr[td[contains(text(),"特别提示信息")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n': '失联机构',
                'En': 'LostContactMechanism',
                'v': '//td[span[text()="失联机构"]]//text()',
                't': 'xpath_first'
            }, {
                'n': '异常机构',
                'En': 'AbnormalMechanism',
                'v': '//td[span[text()="异常机构"]]//text()',
                't': 'xpath_first'
            }, {
                'n': '重大遗漏',
                'En': 'MajorOmission',
                'v': '//td[span[text()="重大遗漏"]]//text()',
                't': 'xpath_first'
            }, {
                'n': '虚假填报',
                'En': 'FalseFilling',
                'v': '//td[span[text()="虚假填报"]]//text()',
                't': 'xpath_first'
            }, {
                'n': '违反八条底线',
                'En': 'Violation8Baseline',
                'v': '//td[span[text()="违反八条底线"]]//text()',
                't': 'xpath_first'
            }, {
                'n': '不良诚信',
                'En': 'BadFaith',
                't': 'xpath_first',
                'v': '//td[span[text()="不良诚信"]]//text()'
            }, {
                'n': '基金数量',
                'En': 'fundCount',
                't': 'meta',
                'v': 'fundCount'
            }, {
                'n': '基金规模',
                'En': 'fundScale',
                't': 'meta',
                'v': 'fundScale'
            }, {
                'n': '是否有信用提示',
                'En': 'hasCreditTips',
                't': 'meta',
                'v': 'hasCreditTips'
            }, {
                'n': '是否有特别提示',
                'En': 'hasSpecialTips',
                't': 'meta',
                'v': 'hasSpecialTips'
            }, {
                'n': '登记省',
                'En': 'registerProvince',
                't': 'meta',
                'v': 'registerProvince'
            }, {
                'n': '是否在黑名单',
                'En': 'inBlacklist',
                't': 'meta',
                'v': 'inBlacklist'
            }, {
                'n': '管理人是否有产品',
                'En': 'managerHasProduct',
                't': 'meta',
                'v': 'managerHasProduct'
            }, {
                'n': '办公所在城市',
                'En': 'officeCity',
                't': 'meta',
                'v': 'officeCity'
            }, {
                'n': '办公点坐标',
                'En': 'officeCoordinate',
                't': 'meta',
                'v': 'officeCoordinate'
            }, {
                'n': '办公省份',
                'En': 'officeProvince',
                't': 'meta',
                'v': 'officeProvince'
            }, {
                'n': '实收资本',
                'En': 'paidInCapital',
                't': 'meta',
                'v': 'paidInCapital'
            }, {
                'n': '注册地址坐标',
                'En': 'regCoordinate',
                't': 'meta',
                'v': 'regCoordinate'
            }, {
                'n': '注册所在城市',
                'En': 'registerCity',
                't': 'meta',
                'v': 'registerCity'
            }, {
                'n': '认缴资本',
                'En': 'subscribedCapital',
                't': 'meta',
                'v': 'subscribedCapital'
            }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    # @SpiderHelp.check_response
    def amac_private_fund_prod(self, response):
        yield self.response_try(response)
        url = 'http://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand=%.18f&page=%s&size=100' % (random.random(),0)
        yield self.request(url,
            method='POST',
            body=self.amac_postdata,
            headers=self.default_jheader,
            callback=self.amac_private_fund_prod_list)

    # @SpiderHelp.check_response
    def amac_private_fund_prod_list(self, response):
        yield self.response_try(response)
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages'
                        },
                callback=self.amac_private_fund_prod_list,
                headers=self.default_jheader,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand=%.18f&page=%s&size=100' % (random.random(),page),
                bodyfunc=lambda page,response=None:self.amac_postdata,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='json')
        for req in reqs:
            yield req

        # 私募基金管理人基金产品
        JS = json.loads(response.text)
        items = JS['content']
        for item in items:
            url = 'http://gs.amac.org.cn/amac-infodisc/res/pof/fund/%s.html' % item['id']
            yield self.request(url,
                headers=self.default_header,
                meta=item,
                callback=self.amac_private_fund_prod_info
                )
    
    # @SpiderHelp.check_response
    def amac_private_fund_prod_info(self, response):
        yield self.response_try(response)
        # 私募基金管理人基金产品 信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'AMAC.Amac_ManagerFundProd',
                'keys': ['HTML_ID'],
                'check': 'fundName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v': '\/([^\/]+?)\.s?html',
                    't': 'url_re'
                },{
                    'n':
                    '基金名称',
                    'En':
                    'fundName',
                    'v':
                    '//tr[td[contains(text(),"基金名称")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金备案号',
                    'En':
                    'fundNo',
                    'v':
                    '//tr[td[contains(text(),"基金编号")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金管理公司',
                    'En':
                    'managerName',
                    'v':
                    '//tr[td[contains(text(),"基金管理人")]]/td[@class="td-content"]/a/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '管理类型',
                    'En':
                    'managerType',
                    'v':
                    '//tr[td[contains(text(),"管理类型")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n': '基金管理人ID',
                    'En': 'managerID',
                    'v': '//tr[td[contains(text(),"基金管理人名称")]]/td[@class="td-content"]/a/@href',
                    't': 'xpath_re',
                    're': '\/([^\/]+?)\.s?html'
                },
                {
                    'n':
                    '托管人名称',
                    'En':
                    'mandatorName',
                    'v':
                    '//tr[td[contains(text(),"基金管理人名称")]]/td[@class="td-content"]/a/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '成立时间',
                    'En':
                    'setup_date',
                    'v':
                    '//tr[td[contains(text(),"成立时间")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '备案时间',
                    'En':
                    'record_date',
                    'v':
                    '//tr[td[contains(text(),"备案时间")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金备案阶段',
                    'En':
                    'record_stage',
                    'v':
                    '//tr[td[contains(text(),"基金备案阶段")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金类型',
                    'En':
                    'fund_type',
                    'v':
                    '//tr[td[contains(text(),"基金类型")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '运作状态',
                    'En':
                    'status',
                    'v':
                    '//tr[td[contains(text(),"运作状态")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '币种',
                    'En':
                    'currency',
                    'v':
                    '//tr[td[contains(text(),"币种")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金信息最后更新时间',
                    'En':
                    'lastupdateTime',
                    'v':
                    '//tr[td[contains(text(),"基金信息最后更新时间")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金协会特别提示',
                    'En':
                    'special_note',
                    'v':
                    '//tr[td[contains(text(),"基金协会特别提示")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n': '月报应披露',
                    'En': 'month_should_reveal',
                    'v': '//tr[td[starts-with(text(),"月报")]]/td[@class="td-content"]/text()',
                    't': 'xpath_re',
                    're': '应披露(\d+)条'
                },
                {
                    'n': '月报按时披露',
                    'En': 'month_reveal_intime',
                    'v': '//tr[td[starts-with(text(),"月报")]]/td[@class="td-content"]/text()',
                    't': 'xpath_re',
                    're': '按时披露(\d+)条'
                },
                {
                    'n': '月报未披露',
                    'En': 'month_None_reveal',
                    'v': '//tr[td[starts-with(text(),"月报")]]/td[@class="td-content"]/text()',
                    't': 'xpath_re',
                    're': '未披露(\d+)条'
                },
                {
                    'n': '半年报应披露',
                    'En': 'halfYear_should_reveal',
                    'v': '//tr[td[starts-with(text(),"半年报")]]/td[@class="td-content"]/text()',
                    't': 'xpath_re',
                    're': '应披露(\d+)条'
                },
                {
                    'n': '半年报按时披露',
                    'En': 'halfYear_reveal_intime',
                    'v': '//tr[td[starts-with(text(),"半年报")]]/td[@class="td-content"]/text()',
                    't': 'xpath_re',
                    're': '按时披露(\d+)条'
                },
                {
                    'n': '半年报未披露',
                    'En': 'halfYear_None_reveal',
                    'v': '//tr[td[starts-with(text(),"半年报")]]/td[@class="td-content"]/text()',
                    't': 'xpath_re',
                    're': '未披露(\d+)条'
                },
                {
                    'n': '年报应披露',
                    'En': 'Year_should_reveal',
                    'v': '//tr[td[starts-with(text(),"年报")]]/td[@class="td-content"]/text()',
                    't': 'xpath_re',
                    're': '应披露(\d+)条'
                },
                {
                    'n': '年报按时披露',
                    'En': 'Year_reveal_intime',
                    'v': '//tr[td[starts-with(text(),"年报")]]/td[@class="td-content"]/text()',
                    't': 'xpath_re',
                    're': '按时披露(\d+)条'
                },
                {
                    'n': '年报未披露',
                    'En': 'Year_None_reveal',
                    'v': '//tr[td[starts-with(text(),"年报")]]/td[@class="td-content"]/text()',
                    't': 'xpath_re',
                    're': '未披露(\d+)条'
                },
                {
                    'n': '季报应披露',
                    'En': 'quarter_should_reveal',
                    'v': '//tr[td[starts-with(text(),"季报:")]]/td[@class="td-content"]/text()',
                    't': 'xpath_re',
                    're': '应披露(\d+)条'
                },
                {
                    'n': '季报按时披露',
                    'En': 'quarter_reveal_intime',
                    'v': '//tr[td[starts-with(text(),"季报:")]]/td[@class="td-content"]/text()',
                    't': 'xpath_re',
                    're': '按时披露(\d+)条'
                },
                {
                    'n': '季报未披露',
                    'En': 'quarter_None_reveal',
                    'v': '//tr[td[starts-with(text(),"季报:")]]/td[@class="td-content"]/text()',
                    't': 'xpath_re',
                    're': '未披露(\d+)条'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    # @SpiderHelp.check_response
    def amac_employment_agency(self, response):
        yield self.response_try(response)
        # 基金管理公司
        yield self.request('http://www.amac.org.cn/xxgs/cyjggs/jjglgs/382721.shtml',
            headers=self.default_header,
            callback=self.fund_management_company)
        # 基金托管人
        yield self.request('http://www.amac.org.cn/xxgs/cyjggs/jjtgx/382722.shtml',
            headers=self.default_header,
            callback=self.fund_custodian)
        # 资产管理类机构
        yield self.request('http://www.amac.org.cn/xxgs/cyjggs/zcglljg/382713.shtml',
            headers=self.default_header,
            callback=self.asset_management_agency)
        # 基金销售机构
        yield self.request('http://www.amac.org.cn/xxgs/cyjggs/jjxsjg/382714.shtml',
            headers=self.default_header,
            callback=self.fund_sales_ageny)
        # 基金评价机构
        yield self.request('http://www.amac.org.cn/xxgs/cyjggs/jjpjjg/382715.shtml',
            headers=self.default_header,
            callback=self.fund_evaluation_ageny)
        # 支付结算机构
        yield self.request('http://www.amac.org.cn/xxgs/cyjggs/zfjsjg/382716.shtml',
            headers=self.default_header,
            callback=self.fund_payment_settlement_agency)
        # 律师事务所
        yield self.request('http://www.amac.org.cn/xxgs/cyjggs/lssws/382717.shtml',
            headers=self.default_header,
            callback=self.fund_law_firm)
        # 会计师事务所
        yield self.request('http://www.amac.org.cn/xxgs/cyjggs/hjsws/382718.shtml',
            headers=self.default_header,
            callback=self.fund_account_firm)
        # 信息技术系统服务机构
        yield self.request('http://www.amac.org.cn/xxgs/cyjggs/xxjsxtfwjg/382719.shtml',
            headers=self.default_header,
            callback=self.fund_information_technology_server_agency)

    # @SpiderHelp.check_response
    def fund_information_technology_server_agency(self, response):
        yield self.response_try(response)
        # 信息技术系统服务机构  信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_FundInformationTechnologyServerAgency',
                'keys': ['Name'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '信息技术服务机构名称',
                    'En': 'Name',
                    'v': './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n':
                    '成立时间',
                    'En':
                    'SetupDate',
                    'v':
                    './td[3]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '网址',
                    'En':
                    'WebSite',
                    'v':
                    './td[4][not(a)]/text()|./td[4][a]/a/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '联系地址',
                    'En':
                    'Address',
                    'v':
                    './td[5]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '电话',
                    'En':
                    'Tel',
                    'v':
                    './td[6]/text()',
                    't':
                    'xpath_first'
                },{
                    'n':
                    '协会会员',
                    'En':
                    'Member',
                    'v':
                    './td[7]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def fund_account_firm(self, response):
        yield self.response_try(response)
        # 会计师事务所  信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_FundAccountFirm',
                'keys': ['Name'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '会计师事务所名称',
                    'En': 'Name',
                    'v': './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n':
                    '成立时间',
                    'En':
                    'SetupDate',
                    'v':
                    './td[3]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '网址',
                    'En':
                    'WebSite',
                    'v':
                    './td[4][not(a)]/text()|./td[4][a]/a/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '联系地址',
                    'En':
                    'Address',
                    'v':
                    './td[5]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '电话',
                    'En':
                    'Tel',
                    'v':
                    './td[6]/text()',
                    't':
                    'xpath_first'
                },{
                    'n':
                    '协会会员',
                    'En':
                    'Member',
                    'v':
                    './td[7]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def fund_law_firm(self, response):
        yield self.response_try(response)
        # 律师事务所  信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_FundLawFirm',
                'keys': ['Name'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律师事务所名称 ',
                    'En': 'Name',
                    'v': './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n':
                    '成立时间',
                    'En':
                    'SetupDate',
                    'v':
                    './td[3]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '网址',
                    'En':
                    'WebSite',
                    'v':
                    './td[4][not(a)]/text()|./td[4][a]/a/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '联系地址',
                    'En':
                    'Address',
                    'v':
                    './td[5]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '电话',
                    'En':
                    'Tel',
                    'v':
                    './td[6]/text()',
                    't':
                    'xpath_first'
                },{
                    'n':
                    '协会会员',
                    'En':
                    'Member',
                    'v':
                    './td[7]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def fund_payment_settlement_agency(self, response):
        yield self.response_try(response)
        # 支付结算机构  信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_FundPaymentSettlementAgency',
                'keys': ['Name'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '支付结算机构名称',
                    'En': 'Name',
                    'v': './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n':
                    '首次在中国证监会备案时间',
                    'En':
                    'ApprovalTime',
                    'v':
                    './td[3]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '网址',
                    'En':
                    'WebSite',
                    'v':
                    './td[4][not(a)]/text()|./td[4][a]/a/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '联系地址',
                    'En':
                    'Address',
                    'v':
                    './td[5]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '电话',
                    'En':
                    'Tel',
                    'v':
                    './td[6]/text()',
                    't':
                    'xpath_first'
                },{
                    'n':
                    '协会会员',
                    'En':
                    'Member',
                    'v':
                    './td[7]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def fund_evaluation_ageny(self, response):
        yield self.response_try(response)
        # 基金评价机构  信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_FundEvaluationAgeny',
                'keys': ['Name'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '基金评价机构名称',
                    'En': 'Name',
                    'v': './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n':
                    '业务核准时间',
                    'En':
                    'ApprovalTime',
                    'v':
                    './td[3]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '网址',
                    'En':
                    'WebSite',
                    'v':
                    './td[4][not(a)]/text()|./td[4][a]/a/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '联系地址',
                    'En':
                    'Address',
                    'v':
                    './td[5]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '电话',
                    'En':
                    'Tel',
                    'v':
                    './td[6]/text()',
                    't':
                    'xpath_first'
                },{
                    'n':
                    '协会会员',
                    'En':
                    'Member',
                    'v':
                    './td[7]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        
    # @SpiderHelp.check_response
    def fund_sales_ageny(self, response):
        yield self.response_try(response)
        # 基金销售机构  信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_FundSalesAgeny',
                'keys': ['Name'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '基金销售机构名称',
                    'En': 'Name',
                    'v': './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n':
                    '业务核准时间',
                    'En':
                    'ApprovalTime',
                    'v':
                    './td[3]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '网址',
                    'En':
                    'WebSite',
                    'v':
                    './td[4][not(a)]/text()|./td[4][a]/a/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '联系地址',
                    'En':
                    'Address',
                    'v':
                    './td[5]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '电话',
                    'En':
                    'Tel',
                    'v':
                    './td[6]/text()',
                    't':
                    'xpath_first'
                },{
                    'n':
                    '协会会员',
                    'En':
                    'Member',
                    'v':
                    './td[7]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    # @SpiderHelp.check_response
    def asset_management_agency(self, response):
        yield self.response_try(response)
        #资产管理类机构 信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_AssetManagementAgency',
                'keys': ['Name'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '机构名称 ',
                    'En': 'Name',
                    'v': './td[2]/p/span/text()',
                    't': 'xpath_first'
                },{
                    'n':
                    '成立时间',
                    'En':
                    'SetupDate',
                    'v':
                    './td[3]/p/span/text()',
                    't':
                    'xpath_join'
                },
                {
                    'n':
                    '网址 ',
                    'En':
                    'WebSite',
                    'v':
                    './td[4]/p/span/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '联系地址 ',
                    'En':
                    'Address',
                    'v':
                    './td[5]/p/span/text()',
                    't':
                    'xpath_join'
                },
                {
                    'n':
                    '电话',
                    'En':
                    'Tel',
                    'v':
                    './td[6]/p/span/text()',
                    't':
                    'xpath_first'
                },{
                    'n':
                    '协会会员',
                    'En':
                    'Member',
                    'v':
                    './td[7]/p/span/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def fund_custodian(self, response):
        yield self.response_try(response)
        # 基金托管人 信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_FundCustodian',
                'keys': ['Custodian'],
                'check': 'Custodian',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '托管人名称',
                    'En': 'Custodian',
                    'v': './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n':
                    '注册地',
                    'En':
                    'RegisteredAddress',
                    'v':
                    './td[3]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '取得托管业务资格时间',
                    'En':
                    'DateOfGetEligibility',
                    'v':
                    './td[4]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '官方网站',
                    'En':
                    'WebSite',
                    'v':
                    './td[5]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '客服电话',
                    'En':
                    'Tel',
                    'v':
                    './td[6]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def fund_management_company(self, response):
        yield self.response_try(response)
        # 基金管理公司 信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_FundManagerCompany',
                'keys': ['Name'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '基金管理公司名称',
                    'En': 'Name',
                    'v': './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n':
                    '成立时间',
                    'En':
                    'SetupDate',
                    'v':
                    './td[3]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '网址',
                    'En':
                    'WebSite',
                    'v':
                    './td[4][a]/a/text()|./td[4][not(a)]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '联系地址',
                    'En':
                    'Address',
                    'v':
                    './td[5]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '电话 ',
                    'En':
                    'Tel',
                    'v':
                    './td[6]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n': '协会会员',
                    'En': 'Member',
                    'v': './td[7]/text()',
                    't': 'xpath_first',
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    def amac_employee_data(self, page, response=None,**kwargs):
        # 公司从业人员概览 表单
        kw = {'filter_EQS_OTC_ID':'',
            'filter_LIKES_AOI_NAME':'',
            'page.searchFileName':'registration',
            'page.sqlKey':'SELECT_LINE_PERSON_LIST',
            'page.sqlCKey':'SELECT_LINE_PERSON_SIZE',
            '_search':'false',
            'nd':self.ctime,
            'page.pageSize':'200',
            'page.pageNo':str(page),
            'page.orderBy':'AOI.AOI_NAME',
            'page.order':'desc'}
        return urllib.parse.urlencode(kw)

    def amac_employee_data2(self, html_id):
        # 公司从业人员列表 表单
        kw = {'filter_EQS_PTI_ID':'',
            'filter_EQS_AOI_ID':html_id,
            'ORDERNAME':'PP#PTI_ID,PP#PPP_NAME',
            'ORDER':'ASC',
            'sqlkey':'registration',
            'sqlval':'SEARCH_FINISH_PUBLICITY'}
        return urllib.parse.urlencode(kw)

    def amac_employee_data3(self, html_id):
        # 从业人员基本信息 表单
        kw = {'filter_EQS_RPI_ID':html_id,
            'sqlkey':'registration',
            'sqlval':'SELECT_PERSON_INFO'}
        return urllib.parse.urlencode(kw)

    def amac_employee_change_data(self, html_id):
        # 从业人员变更信息 表单
        kw = {'filter_EQS_RH#RPI_ID':html_id,
            'sqlkey':'registration',
            'sqlval':'SEARCH_LIST_BY_PERSON'}
        return urllib.parse.urlencode(kw)

    def amac_employee_jianzhi_data(self, html_id):
        # 从业人员兼职信息 表单
        kw = {'filter_EQS_RF#RPI_ID':html_id,
            'sqlkey':'registration',
            'sqlval':'SEARCH_LISY_BY_JIANZHI'}
        return urllib.parse.urlencode(kw)

    # @SpiderHelp.check_response
    def amac_employee(self, response):
        yield self.response_try(response)
        # 跳转页面  获取json接口数据
        yield self.request('http://person.amac.org.cn/pages/registration/train-line-register!list.action',
            method='POST',
            body=self.amac_employee_data(1),
            headers=self.default_header,
            callback=self.company_employee_first)
        # 不变 不定期爬取
        # # 机构类型对照表
        # yield self.request('http://person.amac.org.cn/pages/registration/train-line-register!search.action',
        #     method='POST',
        #     body=urllib.parse.urlencode({'sqlkey':'registration','sqlval':'ORG_TYPE_CODE'}),
        #     headers=self.default_header,
        #     callback=self.company_category)
        # # 所有机构对应类型
        # yield self.request('http://person.amac.org.cn/pages/registration/train-line-register!search.action',
        #     method='POST',
        #     body=urllib.parse.urlencode({'filter_EQS_AOI_ID':'','sqlkey':'registration','sqlval':'SERAOI_TYPE'}),
        #     headers=self.default_header,
        #     callback=self.company_employee_category)
        
    # @SpiderHelp.check_response
    def company_category(self, response):
        yield self.response_try(response)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'json',
                'db': 'AMAC.Amac_CorpCategoryContrast',
                'keys': ['CategoryID'],
                'check': 'CategoryID',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '类别ID',
                    'En': 'CategoryID',
                    'v': 'OTC_ID',
                    't': 'json'
                },
                {
                    'n': '机构类别',
                    'En': 'Category',
                    'v': 'OTC_NAME',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def company_employee_category(self, response):
        yield self.response_try(response)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'json',
                'db': 'AMAC.Amac_CorpCategory',
                'keys': ['CorpRawID'],
                'check': 'CorpRawID',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '机构ID',
                    'En': 'CorpRawID',
                    'v': 'AOI_ID',
                    't': 'json'
                },
                {
                    'n': '机构类别',
                    'En': 'CategoryID',
                    'v': 'AOI_TYPE_ID',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        
    # @SpiderHelp.check_response
    def company_employee_first(self, response):
        yield self.response_try(response)
        # 所有公司概览

        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages'
                        },
                callback=self.company_employee_first,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://person.amac.org.cn/pages/registration/train-line-register!list.action',
                bodyfunc=self.amac_employee_data,
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='json')
        for req in reqs:
            yield req

        # 次级页面
        JS = json.loads(response.text)
        url = 'http://person.amac.org.cn/pages/registration/train-line-register!search.action'
        for item in JS['result']:
            # 从业人员列表
            yield self.request(url,
                method='POST',
                priority=1500,
                meta={'AOI_ID': item['AOI_ID']},
                body=self.amac_employee_data2(item['AOI_ID']),
                callback=self.company_employee_sencond)
            # 机构类型

        # 数据提取
        _configs = [{
            'list': {
                'n': '',
                'v': 'result',    
                't': 'json',
                'db': 'AMAC.Amac_CorpEmployeeStat',
                'keys': ['CorpRawID'],
                'check': 'CorpRawID',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '机构ID',
                    'En': 'CorpRawID',
                    'v': 'AOI_ID',
                    't': 'json'
                },
                {
                    'n': '机构名称',
                    'En': 'CorpFullName',
                    'v': 'AOI_NAME',
                    't': 'json'
                },
                {
                    'n': '人员数量',
                    'En': 'EmployeeCount',
                    'v': 'PR_COUNT_PERSON',
                    't': 'json'
                },
                {
                    'n': '基金从业人员数量',
                    'En': 'FundQualificationCount',
                    'v': 'PTI0PERSON',
                    't': 'json'
                },
                {
                    'n': '基金销售资格人数',
                    'En': 'SaleQualificationCount',
                    'v': 'PTI2PERSON',
                    't': 'json'
                },
                {
                    'n': '其他从业资格人数',
                    'En': 'OtherQualificationCount',
                    'v': 'PTI3PERSON',
                    't': 'json'
                },
                {
                    'n': 'PE/VC从业资格人数',
                    'En': 'PEQualificationCount',
                    'v': 'PTI4PERSON',
                    't': 'json'
                },
                {
                    'n': '合规风控负责人人数',
                    'En': 'RiskEmployeeCount',
                    'v': 'PTI6PERSON',
                    't': 'json'
                },
                {
                    'n': '基金投资顾问人数',
                    'En': 'FundInvestAdviserCount',
                    'v': 'PTI7PERSON',
                    't': 'json'
                },
                {
                    'n': '基金经理人数',
                    'En': 'FundManagerCount',
                    'v': 'PTI8PERSON',
                    't': 'json'
                },
                {
                    'n': '投资经理人数',
                    'En': 'InvestManagerCount',
                    'v': 'PTI9PERSON',
                    't': 'json'
                },
                {
                    'n': '投资总监人数',
                    'En': 'InvestDirectorCount',
                    'v': 'PTI10PERSON',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def company_employee_sencond(self, response):
        yield self.response_try(response)
        # 公司内从业人员列表

        JS = json.loads(response.text)

        AOI_ID = response.meta['AOI_ID']
        url = 'http://person.amac.org.cn/pages/registration/train-line-register!search.action'
        for item in JS:
            # 从业资格基本信息
            yield self.request(url,
                body=self.amac_employee_data3(item['RPI_ID']),
                method='POST',
                meta={**item,'AOI_ID':AOI_ID},
                priority=2000,
                callback=self.company_employee_info)

            # 变更信息
            yield self.request(url,
                body=self.amac_employee_change_data(item['RPI_ID']),
                method='POST',
                meta={**item,'AOI_ID':AOI_ID},
                priority=2000,
                callback=self.company_employee_change_info)

            # 兼职信息
            yield self.request(url,
                body=self.amac_employee_jianzhi_data(item['RPI_ID']),
                method='POST',
                meta={**item,'AOI_ID':AOI_ID},
                priority=2000,
                callback=self.company_employee_jianzhi_info)

    # @SpiderHelp.check_response
    def company_employee_info(self, response):
        yield self.response_try(response)
        # 数据提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'json',
                'db': 'AMAC.Amac_CorpEmployee',
                'keys': ['EmpID'],
                'check': 'EmpFullName',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '人员ID',
                    'En': 'EmpID',
                    'v': 'RPI_ID',
                    't': 'meta'
                },
                {
                    'n': '人员全称',
                    'En': 'EmpFullName',
                    'v': 'RPI_NAME',
                    't': 'json'
                },
                {
                    'n': '机构全称',
                    'En': 'CorpFullName',
                    'v': 'AOI_NAME',
                    't': 'json'
                },
                {
                    'n': '机构ID',
                    'En': 'CorpRawID',
                    'v': 'AOI_ID',
                    't': 'json'
                },
                {
                    'n': '部门名称',
                    'En': 'ADI_NAME',
                    'v': 'ADI_NAME',
                    't': 'json'
                },
                {
                    'n': '部门ID',
                    'En': 'ADI_ID',
                    'v': 'ADI_ID',
                    't': 'json'
                },
                {
                    'n': '性别',
                    'En': 'Gender',
                    'v': 'SCO_NAME',
                    't': 'json'
                },
                {
                    'n': '学历',
                    'En': 'Education',
                    'v': 'ECO_NAME',
                    't': 'json'
                },
                {
                    'n': '证书类型',
                    'En': 'QualificationType',
                    'v': 'PTI_NAME',
                    't': 'json'
                },
                {
                    'n': '证书编号',
                    'En': 'QualificationNo',
                    'v': 'CER_NUM',
                    't': 'json'
                },
                {
                    'n': '证书发布日期',
                    'En': 'QualificationStartDate',
                    'v': 'OBTAIN_DATE',
                    't': 'json'
                },
                {
                    'n': '证书截至有效日期',
                    'En': 'QualificationEndDate',
                    'v': 'ARRIVE_DATE',
                    't': 'json'
                },
                {
                    'n': '变更信息',
                    'En': 'ChangeInformationCount',
                    'v': 'COUNTCER',
                    't': 'meta'
                },
                {
                    'n': '诚信记录',
                    'En': 'CreditTip',
                    'v': 'COUNTCX',
                    't': 'meta'
                },{
                    'n': 'Image', #http://person.amac.org.cn/photo/apache-tomcat-6.0.35/webapps/image_product/images/{}
                    'En': 'Image',
                    'v': 'RPI_PHOTO_PATH',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def company_employee_change_info(self, response):
        yield self.response_try(response)
        # 数据提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'json',
                'db': 'AMAC.Amac_CorpEmployeeChange',
                'keys': ['QualificationNo'],
                'check': 'CorpFullName',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '人员ID',
                    'En': 'EmpID',
                    'v': 'RPI_ID',
                    't': 'meta'
                },
                {
                    'n': '从业机构',
                    'En': 'CorpFullName',
                    'v': 'AOI_NAME',
                    't': 'json'
                },
                {
                    'n': '从业资格类别',
                    'En': 'QualificationType',
                    'v': 'PTI_NAME',
                    't': 'json'
                },
                {
                    'n': '证书编号',
                    'En': 'QualificationNo',
                    'v': 'CER_NUM',
                    't': 'json'
                },
                {
                    'n': '取得日期',
                    'En': 'QualificationStartDate',
                    'v': 'OBTAIN_DATE',
                    't': 'json'
                },
                {
                    'n': '证书状态',
                    'En': 'QualificationStatus',
                    'v': 'CERTC_NAME',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def company_employee_jianzhi_info(self, response):
        yield self.response_try(response)
        # 数据提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'json',
                'db': 'AMAC.Amac_EmplyeePartTime',
                'keys': ['PartTimeCorp','EmpID','PartTimeAddTime'],
                'check': 'PartTimeCorp',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '人员ID',
                    'En': 'EmpID',
                    'v': 'RPI_ID',
                    't': 'meta'
                },
                {
                    'n': '兼职机构',
                    'En': 'PartTimeCorp',
                    'v': 'AOI_NAME',
                    't': 'json'
                },
                {
                    'n': '兼职职位',
                    'En': 'PartTimePost',
                    'v': 'AOP_POST',
                    't': 'json'
                },
                {
                    'n': '开始时间',
                    'En': 'PartTimeAddTime',
                    'v': 'AOP_ADD_TIME',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def amac_servers_data(self, GSFWLX):
        def data(page, response=None):
            # 2 3 4
            return urllib.parse.urlencode({'currentPage':str(page),
            'mname':'listNoticeForm',
            'GSJGMC':'',
            'GSFWLX':str(GSFWLX),
            'GSID':''})
        return data

    def amac_servers_data2(self, GSID, index,currentpage):
         return urllib.parse.urlencode({'currentPage':currentpage,
            'mname':'viewNoticeForm',
            'GSJGMC':'',
            'GSFWLX':str(index),
            'GSID':GSID})

    # @SpiderHelp.check_response
    def amac_servers(self, response):
        yield self.response_try(response)
        url = 'http://fo.amac.org.cn/amac/allNotice.do'
        # 份额登记业务服务
        # 估值核算业务服务
        # 信息技术系统服务
        for index in range(2,5):
            yield self.request(url,
                method='POST',
                body=self.amac_servers_data(index)(1),
                meta={'index':index},
                callback=self.amac_service_list
                )

    # @SpiderHelp.check_response
    def amac_service_list(self, response):
        yield self.response_try(response)
        url = 'http://fo.amac.org.cn/amac/allNotice.do'

        # 翻页
        index = response.meta['index']
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '共(\d+)页'
                        },
                callback=self.amac_service_list,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: url,
                bodyfunc=self.amac_servers_data(index),
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # 详情页
        currentpage = re.findall('第(\d+)页', response.text)[0]
        for item in re.findall('\"viewNoticeForm\",\s*?\"(.*?)\"',response.text):
            yield self.request(url,
                method='POST',
                body=self.amac_servers_data2(item,index,currentpage),
                meta={'item':item},
                callback=self.amac_service_info)

    # @SpiderHelp.check_response
    def amac_service_info(self, response):
        yield self.response_try(response)
        # 服务机构 数据提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'AMAC.Amac_FundServiceAgency',# 基金服务机构
                'keys': ['CorpName','ServiceType'],
                'check': 'CorpName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '机构名称',
                    'En': 'CorpName',
                    'v': '//td[b[contains(text(),"机构名称")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构代码',
                    'En': 'CorpCode',
                    'v': '//td[b[contains(text(),"机构代码")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '备案编号',
                    'En': 'RecordNumber',
                    'v': '//td[b[contains(text(),"备案编号")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构类型',
                    'En': 'CorpType',
                    'v': '//td[b[contains(text(),"机构类型")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司网址',
                    'En': 'WebSite',
                    'v': '//td[b[contains(text(),"公司网址")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v': '//td[b[contains(text(),"注册地址")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '办公地址',
                    'En': 'OfficeAddress',
                    'v': '//td[b[contains(text(),"办公地址")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '服务类型',
                    'En': 'ServiceType',
                    'v': '//td[b[contains(text(),"服务类型")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '本服务备案时间',
                    'En': 'ThisServiceRecordTime',
                    'v': '//td[b[contains(text(),"本服务备案时间")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '团队人员数量',
                    'En': 'TeamsNumber',
                    'v': '//td[b[contains(text(),"团队人员数量")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '基金从业人员数量',
                    'En': 'FundEmployeesNumber',
                    'v': '//td[b[contains(text(),"基金从业人员数量")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': 'IT系统名称',
                    'En': 'ItSysteamName',
                    'v': '//td[b[contains(text(),"IT系统名称")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '备注',
                    'En': 'ReMark',
                    'v': '//td[b[contains(text(),"备注")]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },
               
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def amac_Management_data(self, page, response=None):
        # 证券公司私募产品 表单数据
        return urllib.parse.urlencode({'filter_LIKES_CPMC':'',
                                    'filter_LIKES_GLJG':'',
                                    'filter_LIKES_CPBM':'',
                                    'filter_GES_SLRQ':'',
                                    'filter_LES_SLRQ':'',
                                    'page.searchFileName':'publicity_web',
                                    'page.sqlKey':'PAGE_PUBLICITY_WEB',
                                    'page.sqlCKey':'SIZE_PUBLICITY_WEB',
                                    '_search':'false',
                                    'nd':self.ctime,
                                    'page.pageSize':'200',
                                    'page.pageNo':str(page),
                                    'page.orderBy':'SLRQ',
                                    'page.order':'desc'})

    # @SpiderHelp.check_response
    def amac_Management_plan(self, response):
        yield self.response_try(response)
        # 证券公司私募产品
        url = 'http://ba.amac.org.cn/pages/amacWeb/user!list.action'
        body=self.amac_Management_data(1)
        yield self.request(url,
            body=body,
            method='POST',
            headers=self.default_header,
            callback=self.amac_Management_plan_list)

    # @SpiderHelp.check_response
    def amac_Management_plan_list(self, response):
        yield self.response_try(response)
        url = 'http://ba.amac.org.cn/pages/amacWeb/ab-special-plan!list.action'
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages'
                        },
                callback=self.amac_Management_plan_list,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: url,
                bodyfunc=self.amac_Management_data,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='json')
        for req in reqs:
            yield req

        # 数据提取
        _configs = [{
            'list': {
                'n': '',
                'v': 'result',    
                't': 'json',
                'db': 'AMAC.Amac_ScPrivateProduct',
                'keys': ['HTML_ID'],
                'check': 'HTML_ID',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v': 'MPI_ID',
                    't': 'json'
                },
                {
                    'n': '产品名称',
                    'En': 'ProdName',
                    'v': 'CPMC',
                    't': 'json'
                },
                {
                    'n': '产品编码',
                    'En': 'ProdNo',
                    'v': 'CPBM',
                    't': 'json'
                },
                {
                    'n': '管理机构',
                    'En': 'ManagementAgency',
                    'v': 'GLJG',
                    't': 'json'
                },
                {
                    'n': '设立日期',
                    'En': 'SetupDate',
                    'v': 'SLRQ',
                    't': 'json'
                },{
                    'n': '到期日',
                    'En': 'EndDate',
                    'v': 'DQR',
                    't': 'json'
                },{
                    'n': '投资类型',
                    'En': 'InvestmentType',
                    'v': 'TZLX',
                    't': 'json'
                },{
                    'n': '是否分级',
                    'En': 'WhetherGrading',
                    'v': 'SFFJ',
                    't': 'json'
                },{
                    'n': '管理方式',
                    'En': 'ManagementStyle',
                    'v': 'GLFS',
                    't': 'json'
                },{
                    'n': '成立规模',
                    'En': 'Scale',
                    'v': 'CLGM',
                    't': 'json'
                },{
                    'n': '成立时参与户数',
                    'En': 'Participating',
                    'v': 'CLSCYHS',
                    't': 'json'
                },{
                    'n': '托管机构',
                    'En': 'TrusteeshipAgency',
                    'v': 'TGJG',
                    't': 'json'
                },{
                    'n': '份额登记机构',
                    'En': 'ShareRegistrationAgency',
                    'v': 'FEDJJG',
                    't': 'json'
                },{
                    'n': '投资范围',
                    'En': 'ScopeOfInvestment',
                    'v': 'TZFW',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def amac_Manager_revocation(self, response):
        yield self.response_try(response)
        # 撤销管理人登记的名单
        urls = (response.urljoin(url) for url in response.xpath('//*[@class="newsName"]//@href').extract())
        for url in urls:
            yield scrapy.Request(url,
                priority=MAX,
                callback=self.amac_Manager_revocation_info)

    # @SpiderHelp.check_response
    def amac_Manager_revocation_info(self, response):
        yield self.response_try(response)
        # 撤销管理人登记的名单 提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//table//tr[position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_ManagerRevocation',
                'keys': ['Date','CorpName'],
                'check': 'CorpName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '撤销时间',
                    'En': 'Date',
                    'v':
                    './td[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '机构名称',
                    'En': 'CorpName',
                    'v':
                    './td[2]/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '机构file',
                    'En': 'CorpFile',
                    'v':
                    './td[2]/a/@href',
                    't': 'xpath_first'
                },
                {
                    'n': '纪律处分',
                    'En': 'DocNo',
                    'v': './td[3]/p/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '纪律处分file',
                    'En': 'DocFile',
                    'v': './td[3]/p/a/@href',
                    't': 'xpath_first',
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def amac_Account_publicity(self, response):
        yield self.response_try(response)
        # 账户公示 提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="ldContent"]//table//tr[./td[contains(@style,"width: 68px")]][position()>1]',    
                't': 'xpath',
                'db': 'AMAC.Amac_AccountPublicity',
                'keys': ['AccountNo'],
                'check': 'AccountNo',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '公司名称',
                    'En': 'ComName',
                    'v':
                    'string(./self::tr[td[last()=7]]/td[1]|./self::tr[td[last()=3]]/preceding::tr[td[last()=7]][1]/td[1]|./self::tr[td[last()=1]]/preceding::tr[td[last()=7]][1]/td[1])',
                    't': 'xpath_first',
                },
                {
                    'n': '账户名称',
                    'En': 'AccountName',
                    'v':
                    'string(./self::tr[td[last()=7]]/td[2]|./self::tr[td[last()=3]]/td[1]|./self::tr[td[last()=1]]/preceding::tr[td[last()=7]][1]/td[2])',
                    't': 'xpath_first'
                },
                {
                    'n': '开户行',
                    'En': 'OpeningBank',
                    'v':
                    'string(./self::tr[td[last()=7]]/td[3]|./self::tr[td[last()=3]]/td[2]|./self::tr[td[last()=1]]/preceding::tr[td[last()=7]][1]/td[3])',
                    't': 'xpath_first'
                },
                {
                    'n': '账号',
                    'En': 'AccountNo',
                    'v': 'string(./self::tr[td[last()=7]]/td[4]|./self::tr[td[last()=3]]/td[3]|./self::tr[td[last()=1]]/td[1])',
                    't': 'xpath_first'
                },{
                    'n': '公司网址',
                    'En': 'WebSite',
                    'v': 'string(./self::tr[td[last()=7]]/td[5]|./self::tr[td[last()=3]]/preceding::tr[td[last()=7]][1]/td[5]|./self::tr[td[last()=1]]/preceding::tr[td[last()=7]][1]/td[5])',
                    't': 'xpath_first',
                },{
                    'n': '公司地址',
                    'En': 'Address',
                    'v': 'string(./self::tr[td[last()=7]]/td[6]|./self::tr[td[last()=3]]/preceding::tr[td[last()=7]][1]/td[6]|./self::tr[td[last()=1]]/preceding::tr[td[last()=7]][1]/td[6])',
                    't': 'xpath_first',
                },{
                    'n': '联系电话',
                    'En': 'PhoneNumber',
                    'v': 'string(./self::tr[td[last()=7]]/td[7]|./self::tr[td[last()=3]]/preceding::tr[td[last()=7]][1]/td[7]|./self::tr[td[last()=1]]/preceding::tr[td[last()=7]][1]/td[7])',
                    't': 'xpath_first',
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            # print(item)
            yield item

    # @SpiderHelp.check_response
    def amac_Asset_recognition(self, response):
        yield self.response_try(response)
        # 资产支持专项计划备案确认函公示

        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '\/(\d+)页'
                        },
                callback=self.amac_Asset_recognition,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://www.amac.org.cn/xxgs/zczczxjhbaqrhgs/index_%s.shtml' % (page-1),
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='xpath')
        for req in reqs:
            yield req

        urls = (response.urljoin(url) for url in response.xpath('//*[@class="newsName"]//@href').extract())
        for url in urls:
            yield scrapy.Request(url,
                priority=MAX,
                callback=self.amac_Asset_recognition_info)

    # @SpiderHelp.check_response
    def amac_Asset_recognition_info(self, response):
        yield self.response_try(response)
        # 资产支持专项计划备案确认函公示 提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'AMAC.Amac_AssetSupportConfirmationLetter',
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
                    '\/([^\/]+?)\.s?html',
                    't': 'url_re',
                },{
                    'n': '代码',
                    'En': 'Code',
                    'v':
                    'string(.//div[@class="ldContent"])',
                    't': 'xpath_re',
                    're':'([a-zA-Z0-9]+?)-'
                },{
                    'n': '日期',
                    'En': 'Date',
                    'v':
                    '//div[@class="ldDate"]/text()',
                    't': 'xpath_re',
                    're': '日期：(.+)'
                },
                {
                    'n': '标题',
                    'En': 'Title',
                    'v':
                    '//div[@class="ldT"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '文件地址',
                    'En': 'FileAddr',
                    'v':
                    '//div[@class="ldContent"]//@href',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            # print(item)
            yield item

    def amac_Futures_management_data(self, page, response=None):
        return urllib.parse.urlencode({'filter_LIKES_MPI_NAME':'',
                                        'filter_LIKES_AOI_NAME':'',
                                        'filter_LIKES_MPI_PRODUCT_CODE':'',
                                        'filter_GES_MPI_CREATE_DATE':'',
                                        'filter_LES_MPI_CREATE_DATE':'',
                                        'page.searchFileName':'publicity_web',
                                        'page.sqlKey':'PAGE_QH_PUBLICITY_WEB',
                                        'page.sqlCKey':'SIZE_QH_PUBLICITY_WEB',
                                        '_search':'false',
                                        'nd':self.ctime,
                                        'page.pageSize':'200',
                                        'page.pageNo':str(page),
                                        'page.orderBy':'MPI_CREATE_DATE',
                                        'page.order':'desc'})

    # @SpiderHelp.check_response
    def amac_Futures_management(self, response):
        yield self.response_try(response)
        # 期货资管产品Post
        url = 'http://ba.amac.org.cn/pages/amacWeb/user!list.action'
        body = self.amac_Futures_management_data(1)
        yield self.request(url,
            method='POST',
            body=body,
            headers=self.default_header,
            callback=self.amac_Futures_management_list)

    # @SpiderHelp.check_response
    def amac_Futures_management_list(self, response):
        yield self.response_try(response)
        # 期货资管产品 
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages'
                        },
                callback=self.amac_Futures_management_list,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://ba.amac.org.cn/pages/amacWeb/user!list.action',
                bodyfunc=self.amac_Futures_management_data,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='json')
        for req in reqs:
            yield req

        JS = json.loads(response.text)
        url = 'http://ba.amac.org.cn/pages/amacWeb/user!search.action'
        for item in JS['result']:
            body = self.amac_Futures_management_info_data(item['MPI_ID'])
            yield scrapy.Request(url,
                body=body,
                method='POST',
                headers=self.default_header,
                priority=MAX,
                meta=item,
                callback=self.amac_Futures_management_info)

    def amac_Futures_management_info_data(self, MPI_ID):
        return urllib.parse.urlencode({'filter_EQS_MPI_ID':MPI_ID,
                                    'sqlkey':'publicity_web',
                                    'sqlval':'GET_QH_WEB_BY_MPI_ID'})

    # @SpiderHelp.check_response
    def amac_Futures_management_info(self, response):
        yield self.response_try(response)
        # 期货资产管理计划  提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'json',
                'db': 'AMAC.Amac_FuturesManagement',
                'keys': ['HTML_ID'],
                'check': 'HTML_ID',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'MPI_ID',
                    't': 'meta',
                },{
                    'n': '产品名称',
                    'En': 'ProdName',
                    'v':
                    'MPI_NAME',
                    't': 'json'
                },{
                    'n': '产品编码',
                    'En': 'ProdNo',
                    'v':
                    'MPI_PRODUCT_CODE',
                    't': 'json'
                },
                {
                    'n': '管理人',
                    'En': 'ManagementAgency',
                    'v':
                    'AOI_NAME',
                    't': 'json'
                },
                {
                    'n': '托管人',
                    'En': 'TrusteeshipAgency',
                    'v':
                    'MPI_TRUSTEE',
                    't': 'json'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupDate',
                    'v':
                    'MPI_CREATE_DATE',
                    't': 'json'
                },
                {
                    'n': '投资类型',
                    'En': 'InvestmentType',
                    'v':
                    'TZLX',
                    't': 'json'
                },
                {
                    'n': '募集规模（万元）',
                    'En': 'Scale',
                    'v':
                    'MPI_TOTAL_MONEY',
                    't': 'json'
                },
                {
                    'n': '是否结构化',
                    'En': 'WhetherStructured',
                    'v':
                    'SFJGH',
                    't': 'json'
                },
                {
                    'n': '初始委托人数量',
                    'En': 'NumberOfClients',
                    'v':
                    'MPI_PARTICIPATION_USER',
                    't': 'json'
                },
                {
                    'n': '投资范围',
                    'En': 'ScopeOfInvestment',
                    'v':
                    'MPI_GROUP_RATIO',
                    't': 'json'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            # print(item)
            yield item

    # @SpiderHelp.check_response
    def amac_special_account(self, response):
        yield self.response_try(response)
        url = 'http://gs.amac.org.cn/amac-infodisc/api/fund/account?rand=%.18f&page=%s&size=100' % (random.random(),0)
        body = self.amac_postdata
        yield self.request(url,
            method='POST',
            body=body,
            headers=self.default_jheader,
            callback=self.amac_special_account_list)

    # @SpiderHelp.check_response
    def amac_special_account_list(self, response):
        yield self.response_try(response)
        # 基金专户产品 
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages'
                        },
                callback=self.amac_special_account_list,
                headers=self.default_jheader,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://gs.amac.org.cn/amac-infodisc/api/fund/account?rand=%.18f&page=%s&size=100' % (random.random(),page-1),
                bodyfunc=lambda page,response=None:self.amac_postdata,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='json')
        for req in reqs:
            yield req

        JS = json.loads(response.text)
        url = 'http://gs.amac.org.cn/amac-infodisc/res/fund/account/%s.html'
        for item in JS['content']:
            _url = url % item['id']
            yield scrapy.Request(_url,
                headers=self.default_header,
                priority=MAX,
                meta=item,
                callback=self.amac_special_account_info)

    # @SpiderHelp.check_response
    def amac_special_account_info(self, response):
        yield self.response_try(response)
        # 基金专户产品  提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'AMAC.Amac_SpecialFund',
                'keys': ['SpecialAccountName','RecordCode'],
                'check': 'SpecialAccountName',
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
                    'n': '专户名称',
                    'En': 'SpecialAccountName',
                    'v':
                    '//td[contains(text(),"专户名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '备案编码',
                    'En': 'RecordCode',
                    'v':
                    '//td[contains(text(),"备案编码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '管理人名称',
                    'En': 'ManagementAgency',
                    'v':
                    '//td[contains(text(),"管理人名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '托管人名称',
                    'En': 'TrusteeshipAgency',
                    'v':
                    '//td[contains(text(),"托管人名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '备案日期',
                    'En': 'RecordDate',
                    'v':
                    '//td[contains(text(),"备案日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '合同期限（月）',
                    'En': 'ContractPeriod',
                    'v':
                    '//td[contains(text(),"合同期限")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '起始规模（亿元）',
                    'En': 'Scale',
                    'v':
                    '//td[contains(text(),"起始规模")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '是否分级',
                    'En': 'WhetherGrading',
                    'v':
                    '//td[contains(text(),"是否分级")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '成立时投资者数量',
                    'En': 'NumberOfInvestors',
                    'v':
                    '//td[contains(text(),"投资者数量")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '非专项资产管理计划产品类型',
                    'En': 'ProdType',
                    'v':
                    '//td[contains(text(),"产品类型")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '专户类型',
                    'En': 'AccountType',
                    'v':
                    'type',
                    't': 'meta'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            # print(item)
            yield item

    # @SpiderHelp.check_response
    def amac_Sc_Direct_investment_fund(self, response):
        yield self.response_try(response)
        # 证券公司直投基金
        url = 'http://gs.amac.org.cn/amac-infodisc/api/aoin/product?rand=%.18f&page=%s&size=100' % (random.random(),0)
        body = self.amac_postdata
        yield self.request(url,
            method='POST',
            body=body,
            headers=self.default_jheader,
            callback=self.Sc_Direct_investment_fund_list)

    # @SpiderHelp.check_response
    def Sc_Direct_investment_fund_list(self, response):
        yield self.response_try(response)
        # 证券公司直投基金
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages'
                        },
                callback=self.Sc_Direct_investment_fund_list,
                headers=self.default_jheader,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://gs.amac.org.cn/amac-infodisc/api/aoin/product?rand=%.18f&page=%s&size=100' % (random.random(),page-1),
                bodyfunc=lambda page,response=None:self.amac_postdata,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='json')
        for req in reqs:
            yield req

        JS = json.loads(response.text)
        url = 'http://gs.amac.org.cn/amac-infodisc/res/aoin/product/%s.html'
        for item in JS['content']:
            _url = url % item['id']
            yield scrapy.Request(_url,
                headers=self.default_header,
                priority=MAX,
                callback=self.Sc_Direct_investment_fund_info)

    # @SpiderHelp.check_response
    def Sc_Direct_investment_fund_info(self, response):
        yield self.response_try(response)
        # 证券公司直投基金  提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'AMAC.Amac_ScDirectInvestmentFund',
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
                    '\/([^\/]+?)\.s?html',
                    't': 'url_re',
                },{
                    'n': '产品名称',
                    'En': 'ProdName',
                    'v':
                    '//td[contains(text(),"产品名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '产品编码',
                    'En': 'ProdNo',
                    'v':
                    '//td[contains(text(),"产品编码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '直投子公司名称',
                    'En': 'Subsidiary',
                    'v':
                    '//td[contains(text(),"直投子公司名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '管理机构名称',
                    'En': 'ManagementAgency',
                    'v':
                    '//td[contains(text(),"管理机构名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '设立日期',
                    'En': 'SetupDate',
                    'v':
                    '//td[contains(text(),"设立日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '备案日期',
                    'En': 'RecordDate',
                    'v':
                    '//td[contains(text(),"备案日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '基金类型',
                    'En': 'FundType',
                    'v':
                    '//td[contains(text(),"基金类型")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '组织形式',
                    'En': 'OrganizationalForm',
                    'v':
                    '//td[contains(text(),"组织形式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '运作状态',
                    'En': 'OperationalState',
                    'v':
                    '//td[contains(text(),"运作状态")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '是否托管',
                    'En': 'WhetherTrusteeship',
                    'v':
                    '//td[contains(text(),"是否托管")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '托管人名称',
                    'En': 'TrusteeshipAgency',
                    'v':
                    '//td[contains(text(),"托管人名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            # print(item)
            yield item

    # @SpiderHelp.check_response
    def amac_SC_private_investment_fund(self, response):
        yield self.response_try(response)
        # 证券公司私募投资基金
        url = 'http://gs.amac.org.cn/amac-infodisc/api/pof/subfund?rand=%.18f&page=%s&size=100' % (random.random(),0)
        body = self.amac_postdata
        yield self.request(url,
            method='POST',
            body=body,
            headers=self.default_jheader,
            callback=self.amac_SC_private_investment_fund_list)

    # @SpiderHelp.check_response
    def amac_SC_private_investment_fund_list(self, response):
        # 证券公司私募投资基金
        # 翻页
        yield self.response_try(response)
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages'
                        },
                callback=self.amac_SC_private_investment_fund_list,
                headers=self.default_jheader,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://gs.amac.org.cn/amac-infodisc/api/pof/subfund?rand=%.18f&page=%s&size=100' % (random.random(),page-1),
                bodyfunc=lambda page,response=None:self.amac_postdata,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='json')
        for req in reqs:
            yield req

        JS = json.loads(response.text)
        url = 'http://gs.amac.org.cn/amac-infodisc/res/pof/subfund/%s.html'
        for item in JS['content']:
            _url = url % item['productId']
            yield scrapy.Request(_url,
                headers=self.default_header,
                priority=MAX,
                callback=self.amac_SC_private_investment_fund_info)

    # @SpiderHelp.check_response
    def amac_SC_private_investment_fund_info(self, response):
        # 证券公司私募投资基金  提取
        # if not response.xpath('//td[contains(text(),"产品名称")]/following-sibling::td[1]/text()'):
        yield self.response_try(response)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'AMAC.Amac_SCPrivateInvestmentFund',
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
                    '\/([^\/]+?)\.s?html',
                    't': 'url_re',
                },{
                    'n': '产品名称',
                    'En': 'ProdName',
                    'v':
                    '//td[contains(text(),"产品名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '产品编码',
                    'En': 'ProdNo',
                    'v':
                    '//td[contains(text(),"产品编码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '管理人名称',
                    'En': 'ManagementAgency',
                    'v':
                    '//td[contains(text(),"管理机构名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '设立日期',
                    'En': 'SetupDate',
                    'v':
                    '//td[contains(text(),"设立日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '备案日期',
                    'En': 'RecordDate',
                    'v':
                    '//td[contains(text(),"备案日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '基金类型',
                    'En': 'FundType',
                    'v':
                    '//td[contains(text(),"基金类型")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '组织形式',
                    'En': 'OrganizationalForm',
                    'v':
                    '//td[contains(text(),"组织形式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '运作状态',
                    'En': 'OperationalState',
                    'v':
                    '//td[contains(text(),"运作状态")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '是否托管',
                    'En': 'WhetherTrusteeship',
                    'v':
                    '//td[contains(text(),"是否托管")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '托管人名称',
                    'En': 'TrusteeshipAgency',
                    'v':
                    '//td[contains(text(),"托管人名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def amac_Asset_support_special_plan(self, response):
        yield self.response_try(response)
        # 证券公司私募投资基金
        url = 'http://ba.amac.org.cn/pages/amacWeb/ab-special-plan!list.action'
        body = self.amac_Asset_support_special_plan_data(1)
        yield self.request(url,
            method='POST',
            body=body,
            headers=self.default_header,
            callback=self.amac_Asset_support_special_plan_list)

    def amac_Asset_support_special_plan_data(self, page, response=None):
        return urllib.parse.urlencode({'filter_LIKES_ASPI_NAME':'',
                                        'filter_GES_AT_AUDIT_DATE':'',
                                        'filter_LES_AT_AUDIT_DATE':'',
                                        'page.searchFileName':'publicity_abs_web',
                                        'page.sqlKey':'PAGE_ABS_PUBLICITY_WEB',
                                        'page.sqlCKey':'SIZE_ABS_PUBLICITY_WEB',
                                        '_search':'false',
                                        'nd':self.ctime,
                                        'page.pageSize':'200',
                                        'page.pageNo':str(page),
                                        'page.orderBy':'AT_AUDIT_DATE',
                                        'page.order':'desc'})

    def amac_Asset_support_special_plan_list(self, response):
        yield self.response_try(response)
        # 资产专项计划 
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages'
                        },
                callback=self.amac_Asset_support_special_plan_list,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://ba.amac.org.cn/pages/amacWeb/ab-special-plan!list.action',
                bodyfunc=self.amac_Asset_support_special_plan_data,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='json')
        for req in reqs:
            yield req

        # 资产支持专项计划  信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': 'result',    
                't': 'json',
                'db': 'AMAC.Amac_AssetSupportSpecialPlan',
                'keys': ['ASPI_Name'],
                'check': 'ASPI_Name',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'ASPI_ID',
                    't': 'json'
                },{
                    'n': '备案编号',
                    'En': 'RecordNumber',
                    'v':
                    'ASPI_BA_NUMBER',
                    't': 'json'
                },{
                    'n': '专项计划全称',
                    'En': 'ASPI_Name',
                    'v':
                    'ASPI_NAME',
                    't': 'json'
                },
                {
                    'n': '管理人',
                    'En': 'ManagementAgency',
                    'v':
                    'ASPI_GL_NAME',
                    't': 'json'
                },
                {
                    'n': '托管人名称',
                    'En': 'TrusteeshipAgency',
                    'v':
                    'AII_TGR',
                    't': 'json'
                },
                {
                    'n': '备案通过时间',
                    'En': 'RecordDate',
                    'v':
                    'AT_AUDIT_DATE',
                    't': 'json'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

def main():
    SinaspiderSpider.put_redis()

if __name__=='__main__':
    main()