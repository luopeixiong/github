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


from myselector import pdf_to_html
from SpiderHelp import SpiderHelp
from RedisHelp import _Request,_RedisSpider,logger


conn_flag = False
REDISFLAG = True
TODAY = time.strftime('%Y-%m-%d')
Headers = {'User-Agent': generate_user_agent(os=('win',))}
Cookies = {'.ASPXANONYMOUS':'pdtC5gfC0wEkAAAAOWIzZDNiMGEtYjUzOS00YzYyLWEyZTctNWM2OTdmOGM2ZDcz0'}


'''
redis数据库使用FOFI先进后出的规则 对url进行队列选择
'''

class SinaspiderSpider(_RedisSpider, SpiderHelp):  #,scrapy.Spider
    name = 'cyzone'
    start_urls = [
                'http://wwv.cyzone.cn', # 创业邦入口
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
            if url == 'http://wwv.cyzone.cn':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        callback=self.cyzone_start))
        return req

    @SpiderHelp.check_response
    def cyzone_start(self, response):
        yield self.request('http://wwv.cyzone.cn/vcompany/list-0-0-1-0-0/',
            redis_flag=True,
            meta={'formatter':'http://wwv.cyzone.cn/vcompany/list-0-0-{}-0-0/','proxys':True},
            callback=self.cyzone_vcompany
            )
        yield self.request('http://wwv.cyzone.cn/company/list-0-1-4/',
            redis_flag=True,
            meta={'formatter':'http://wwv.cyzone.cn/company/list-0-{}-4/','proxys':True},
            callback=self.cyzone_company
            )
        yield self.request('http://wwv.cyzone.cn/people/list-0-1-0-0/',
            redis_flag=True,
            meta={'formatter':'http://wwv.cyzone.cn/people/list-0-{}-0-0/','proxys':True},
            callback=self.cyzone_people
            )
        yield self.request('http://wwv.cyzone.cn/event/list-764-0-1-0-0-0-0/',
            redis_flag=True,
            meta={'formatter':'http://wwv.cyzone.cn/event/list-764-0-{}-0-0-0-0/','proxys':True},
            callback=self.cyzone_event
            )
        yield self.request('http://wwv.cyzone.cn/vpeople/list-0-1/',
            redis_flag=True,
            meta={'formatter':'http://wwv.cyzone.cn/vpeople/list-0-{}/','proxys':True},
            callback=self.cyzone_vpeople
            )

    @SpiderHelp.check_response
    def cyzone_vcompany(self, response):
        # 创业邦-创业公司
        # #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[@id="lastpage"]/preceding-sibling::a[1]/text()'
                        },
                callback=self.cyzone_vcompany,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                divmod=1,
                redis_conn=self.r,
                meta={'proxys':True},
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # 列表页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[span[@class="tit"]]/@href',
                                                   },
                                           callback=self.cyzone_vcompany_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           meta={'proxys':True},
                                           response_type='xpath')
        for req in reqs2:
            yield req

    @SpiderHelp.check_response
    def cyzone_vcompany_info(self, response):
        # 创业公司
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Cyzone_StartupsCompany',
                'keys': ['HTML_ID','StartsComShortName'],
                'check': 'StartsComShortName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'r\/(.+)\.html',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'StartsComShortName',
                    'v':
                    '//li[h1 and @class="name"]/h1/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司全称',
                    'En': 'StartsComName',
                    'v':
                    '//li[contains(text(),"公司全称")]/text()',
                    't': 'xpath_re',
                    're':'公司全称[:：](.+)'
                },{
                    'n': '公司官网',
                    'En': 'OfficeWebsite',
                    'v':
                    '//div[@class="com-url"]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立时间1',
                    'En': 'SetupTime1',
                    'v':
                    '//li[i[@class="i1"]]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '所属地区',
                    'En': 'AreaName',
                    'v':
                    '//li[i[@class="i2"]]/span/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '融资轮次',
                    'En': 'Turns',
                    'v':
                    '//li[i[@class="i3"]]/span/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '行业标签',
                    'En': 'Industry',
                    'v':
                    '//li[i[@class="i6"]]/span/a/text()',
                    't': 'xpath_join,'
                },{
                    'n': '公司简介',
                    'En': 'CompanyProfile',
                    'v':
                    '//h3[contains(text(),"简介")]/following-sibling::div[1]/p/text()',
                    't': 'xpath_join,'
                },{
                    'n': '注册号',
                    'En': 'RegistrationNumber',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"注册号")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营状态',
                    'En': 'OperatingState',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"注册号")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表',
                    'En': 'NameOfLegalRepresentative',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"法定代表")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股东',
                    'En': 'Shareholder',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"股东")]]/span[2]/text()',
                    't': 'xpath_join,'
                },{
                    'n': '公司类型',
                    'En': 'CompanyType',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"公司类型")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"成立日期")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资本',
                    'En': 'RegisteredCapital',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"注册资本")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '住所',
                    'En': 'OfficeAddress',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"住所")]]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

    @SpiderHelp.check_response
    def cyzone_company(self, response):
        # 创业邦-投资公司
        # '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[@id="lastpage"]/preceding-sibling::a[1]/text()'
                        },
                callback=self.cyzone_company,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                meta={'proxys':True},
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # # 列表页 -投资公司信息
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//td[@class="table-company2-tit"]/a/@href',
                                                   },
                                           callback=self.cyzone_company_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           meta={'proxys':True},
                                           response_type='xpath')
        for req in reqs2:
            yield req

        # # 列表页 -投资公司投资事件 
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//td[@class="table-company2-tit"]/a/@href',
                                                   're': '\/([^\/]+)\.html'
                                                   },
                                           callback=self.cyzone_company_investment_events,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://wwv.cyzone.cn/company/case-%s-0-0-1/' % page,
                                           errback=self.errbackparse,
                                           meta={'proxys':True,},
                                           response_type='xpath')
        for req in reqs2:
            yield req
            return

    @SpiderHelp.check_response
    def cyzone_company_investment_events(self, response):
        # 投资公司投资事件提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//tr[@class="table-plate3"]',    
                't': 'xpath',
                'db': 'CreditDataBase.Cyzone_InvestmentCompanyEvents',
                'keys': ['HTML_ID', 'ObtainInvestmentComShortName','ObtainInvestmentTime'],
                'check': 'ObtainInvestmentComShortName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'case-(\d+)-',
                    't': 'url_re'
                },
                {
                    'n': '投资公司',
                    'En': 'ComShortName',
                    'v':
                    '//li[@class="organize"]//h2/text()',
                    't': 'xpath_first'
                },{
                    'n': '投资公司ID',
                    'En': 'InvestmentCompanyID',
                    'v':
                    '//li[@class="organize"]/a[1]/@href',
                    't': 'xpath_re',
                    're': 'd\/(.+)\.html'
                },{
                    'n': '获投公司',
                    'En': 'ObtainInvestmentComShortName',
                    'v':
                    './/span[@class="tp2_tit"]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '获投公司ID',
                    'En': 'ObtainInvestmentComID',
                    'v':
                    './/span[@class="tp2_tit"]/a/@href',
                    't': 'xpath_re',
                    're': 'r\/(.+)\.html'
                },{
                    'n': '金额',
                    'En': 'Amount',
                    'v':
                    './/div[@class="money"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '轮次',
                    'En': 'Turns',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '投资方',
                    'En': 'InvestmentCompanys',
                    'v':
                    './td[5]/@title',
                    't': 'xpath_first'
                },{
                    'n': '获投时间',
                    'En': 'ObtainInvestmentTime',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },
                
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

        # '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[@id="lastpage"]/preceding-sibling::a[1]/text()'
                        },
                callback=self.cyzone_company_investment_events,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://wwv.cyzone.cn/company/case-{}-0-0-{}/'.format(re.compile('case-(\d+)-').search(response.url).group(1),page),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                meta={'proxys':True},
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cyzone_company_info(self, response):
        # 投资公司提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.CyZONE_InvestmentCompany',
                'keys': ['HTML_ID', 'ComShortName'],
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
                    'd\/(.+)\.html',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//li[h1 and @class="organize"]/h1/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '成立时间',
                    'En': 'SetupTime',
                    'v':
                    '//li[contains(text(),"成立时间")]/text()',
                    't': 'xpath_re',
                    're':'成立时间[:：](.+)'
                },{
                    'n': '投资偏好',
                    'En': 'Preference',
                    'v':
                    '//li[contains(text(),"投资偏好")]/text()',
                    't': 'xpath_re',
                    're':'投资偏好[:：](.+)'
                },{
                    'n': '机构官网',
                    'En': 'OfficialWebsite',
                    'v':
                    '//li[contains(text(),"机构官网")]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '简介',
                    'En': 'Introduction',
                    'v':
                    '//div[h2[text()="简介"]]/div[1]//p//text()',
                    't': 'xpath_join'
                },{
                    'n': '投资团队人数',
                    'En': 'NumbersOfTeam',
                    'v':
                    'count(//div[h2[text()="投资团队"]]//li)',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

    @SpiderHelp.check_response
    def cyzone_people(self, response):
        # 创业邦-投资人
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[@id="lastpage"]/preceding-sibling::a[1]/text()'
                        },
                callback=self.cyzone_people,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                divmod=1,
                redis_conn=self.r,
                meta={'proxys':True},
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # # 列表页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//td[contains(@class,"people-name")]/a[1]/@href',
                                                   },
                                           callback=self.cyzone_people_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           meta={'proxys':True},
                                           response_type='xpath')
        for req in reqs2:
            yield req

    @SpiderHelp.check_response
    def cyzone_people_info(self, response):
        # 投资人提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Cyzone_Investor',
                'keys': ['HTML_ID', 'Name'],
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
                    'f\/(.+)\.html',
                    't': 'url_re'
                },
                {
                    'n': '姓名',
                    'En': 'Name',
                    'v':
                    '//li[@class="name" and h1]/h1/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '职务',
                    'En': 'Position',
                    'v':
                    '//li[@class="name" and h1]/following-sibling::li[last()]',
                    't': 'xpath_first'
                },{
                    'n': '所在机构',
                    'En': 'Institution',
                    'v':
                    '//div[@class="project-info"]/p[@class="name organize-name"]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构ID',
                    'En': 'InstitutionID',
                    'v':
                    '//div[@class="project-info"]/p[@class="name organize-name"]/a/@href',
                    't': 'xpath_re',
                    're': 'd\/(.+)\.html'
                },
                {
                    'n': '关注领域',
                    'En': 'AreasOfConcern',
                    'v':
                    '//span[contains(text(),"关注领域")]/following-sibling::span/text()',
                    't': 'xpath_join,',
                },{
                    'n': '投资阶段',
                    'En': 'InvestmentStage',
                    'v':
                    '//span[contains(text(),"投资阶段")]/following-sibling::span/text()',
                    't': 'xpath_first',
                },{
                    'n': '常驻城市',
                    'En': 'ResidentCity',
                    'v':
                    '//span[contains(text(),"常驻城市")]/following-sibling::span/text()',
                    't': 'xpath_first',
                },{
                    'n': '简介',
                    'En': 'Introduction',
                    'v':
                    '//div[h2[text()="简介"]]/h2/following-sibling::div[1]//p//text()',
                    't': 'xpath_join'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

        # 工作经历
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[h2[text()="工作经历"]]/div',    
                't': 'xpath',
                'db': 'CreditDataBase.Cyzone_InvestorWorkExperience',
                'keys': ['HTML_ID', 'Name','Position','ComName'],
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
                    'f\/(.+)\.html',
                    't': 'url_re'
                },
                {
                    'n': '姓名',
                    'En': 'Name',
                    'v':
                    '//li[@class="name" and h1]/h1/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司',
                    'En': 'ComName',
                    'v':
                    './/span[@class="com"]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司ID',
                    'En': 'ComNID',
                    'v':
                    './/span[@class="com"]/a/@href',
                    't': 'xpath_re',
                    're':'d\/(.+)\.html'
                },{
                    'n': '职务',
                    'En': 'Position',
                    'v':
                    './/span[@class="job"]/text()',
                    't': 'xpath_first',
                },{
                    'n': '时间',
                    'En': 'TimeInterval',
                    'v':
                    '//div[@class="time"]/text()',
                    't': 'xpath_first',
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

    @SpiderHelp.check_response
    def cyzone_vpeople(self, response):
        # 创业邦-创业者
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[@id="lastpage"]/preceding-sibling::a[1]/text()'
                        },
                callback=self.cyzone_vpeople,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                divmod=1,
                redis_conn=self.r,
                meta={'proxys':True},
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # # 列表页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//td[@class="people-name"]/a[1]/@href',
                                                   },
                                           callback=self.cyzone_vpeople_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs2:
            yield req

    @SpiderHelp.check_response
    def cyzone_vpeople_info(self, response):
        # 创业邦-创业者
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Cyzone_Entrepreneur',
                'keys': ['HTML_ID', 'Name'],
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
                    's\/(.+)\.html',
                    't': 'url_re'
                },
                {
                    'n': '姓名',
                    'En': 'Name',
                    'v':
                    '//li[@class="name"]/h1/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '所在公司',
                    'En': 'Com1',
                    'v':
                    '//li[@class="name"]/following-sibling::li[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '职务',
                    'En': 'Position',
                    'v':
                    '//li[@class="name"]/following-sibling::li[last()]/text()',
                    't': 'xpath_first',
                },{
                    'n': '简介',
                    'En': 'BriefIntroduction',
                    'v':
                    '//div[h2[text()="简介"]]/div[1]//p//text()',
                    't': 'xpath_join',
                },{
                    'n': '项目名称',
                    'En': 'ProjName',
                    'v':
                    '//div[@class="project-info"]/p[@class="name"]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '项目ID',
                    'En': 'ProjID',
                    'v':
                    '//div[@class="project-info"]/p[@class="name"]/a/@href',
                    't': 'xpath_re',
                    're': 'r\/(.+)\.html'
                },{
                    'n': '官网',
                    'En': 'OfficialWebsite',
                    'v':
                    '//div[@class="project-info"]/p[contains(text(),"公司官网")]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '轮次',
                    'En': 'Turns',
                    'v':
                    '//div[@class="project-info"]/p[contains(text(),"轮次")]/text()',
                    't': 'xpath_re',
                    're': '轮次[:：],{0,1}([\s\S]+?),?$'
                },{
                    'n': '行业',
                    'En': 'Industry',
                    'v':
                    '//div[@class="project-info"]/p[contains(text(),"行业")]/a/text()',
                    't': 'xpath_join,',
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

    @SpiderHelp.check_response
    def cyzone_event(self, response):
        # 创业邦-投资事件
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[@id="lastpage"]/preceding-sibling::a[1]/text()'
                        },
                callback=self.cyzone_event,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                meta={'proxys':True},
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # 投资事件
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="list-table3"]//tr[contains(@class,"table") and position()>1]',    
                't': 'xpath',
                'db': 'CreditDataBase.Cyzone_InvestmentEvents',
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
                    './/a[text()="详情"]/@href',
                    't': 'xpath_re',
                    're': 'e\/(.+)\.html'
                },
                {
                    'n': '获投公司简称',
                    'En': 'ObtainInvestmentComShortName',
                    'v':
                    './/span[@class="tp2_tit"]/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '获投公司全称',
                    'En': 'ObtainInvestmentComName',
                    'v':
                    './/span[@class="tp2_com"]/text()',
                    't': 'xpath_first',
                },{
                    'n': '获投公司ID',
                    'En': 'ObtainInvestmentComID',
                    'v':
                    './/span[@class="tp2_tit"]/a/@href',
                    't': 'xpath_re',
                    're':'r\/(.+)\.html'
                },{
                    'n': '金额',
                    'En': 'Amount',
                    'v':
                    './td[3]/div[@class="money"]/text()',
                    't': 'xpath_first',
                },{
                    'n': '轮次',
                    'En': 'Turns',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first',
                },{
                    'n': '投资公司',
                    'En': 'InvestmentCompanys',
                    'v':
                    './td[5]/@title',
                    't': 'xpath_re',
                    're': ',([\s\S]+),'
                },{
                    'n': '行业',
                    'En': 'Industry',
                    'v':
                    './td[6]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '获投时间',
                    'En': 'ObtainInvestmentTime',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first',
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