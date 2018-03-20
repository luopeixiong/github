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
    name = 'cfa'
    start_urls = [
                'http://www.cfachina.org/', # 期货业协会
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
            if url == 'http://www.cfachina.org/':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        headers=self.default_header,
                        callback=self.cfa_in))
        return req

    @SpiderHelp.check_response
    def cfa_in(self, response):
        # 期货信息入口列表页
        yield self.request('http://www.cfachina.org/cfainfo/organbaseinfoServlet',
            headers=self.default_header,
            method='POST',
            body=urllib.parse.urlencode({'currentPage':'1',
                'pageSize':'20',
                'all':'organbaseinfo'}),
            redis_flag=True,
            callback=self.cfa_com_list)

    @SpiderHelp.check_response
    def cfa_com_list(self, response):
        '''中国期货业协会--证券公司信息'''
        # 基本情况
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_base_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=organbaseinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 历史情况
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_his_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=organhisinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 分支机构
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_branch_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=organbranchinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 高管人员信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_supervisor_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=supervisorinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 从业人员信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_person_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=personinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 股东信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_shareholder_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=organshareholderinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 诚信记录信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_credit_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=organcreditinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 财务信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_financial_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=organfinancialinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 次级债信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_subdebt_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=subdebtmonthinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_list,
                headers=self.default_header,
                method="POST",
                urlfunc=lambda page,response=None:'http://www.cfachina.org/cfainfo/organbaseinfoServlet',
                bodyfunc=lambda page,response=None:urllib.parse.urlencode({'currentPage':str(page),
                                                                            'pageSize':'20',
                                                                            'all':'organbaseinfo'}),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_base_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComBasic',
                    'keys': ['ComName'],
                    'check': 'ComName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '公司名称',
                        'En': 'ComName',
                        'v':
                        './/td[contains(text(),"公司名称")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '许可证号',
                        'En': 'LicenceNumber',
                        'v':
                        './/td[contains(text(),"许可证号")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '经营范围', 
                        'En': 'ScopeOfoperation',
                        'v':
                        './/td[contains(text(),"经营范围")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '金融期货业务资格类别', 
                        'En': 'QualificationCategory',
                        'v':
                        './/td[contains(text(),"资格类别")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '取得会员资格的期货交易所名称', 
                        'En': 'FuturesExchange',
                        'v':
                        './/td[contains(text(),"期货交易所名称")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '注册资本(元)', 
                        'En': 'RegisteredCapital',
                        'v':
                        './/td[contains(text(),"注册资本")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '公司住所', 
                        'En': 'Address',
                        'v':
                        './/td[contains(text(),"公司住所")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '法定代表人', 
                        'En': 'NameOfLegalRepresentative',
                        'v':
                        './/td[contains(text(),"法定代表人")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '办公地址和邮编', 
                        'En': 'OfficeAddress_ZipCode',
                        'v':
                        './/td[contains(text(),"办公地址和邮编")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '客户服务及投诉电话', 
                        'En': 'OfficePhoneNumber',
                        'v':
                        './/td[contains(text(),"客户服务及投诉电话")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '公司网址网址', 
                        'En': 'OfficeWebsite',
                        'v':
                        './/td[contains(text(),"公司网址")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '公司电子邮箱', 
                        'En': 'OfficeEmailAddress',
                        'v':
                        './/td[contains(text(),"电子邮箱")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def cfa_com_his_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComHis',
                    'keys': ['Date', 'HTML_ID','Event'],
                    'check': 'Date',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '时间',
                        'En': 'Date',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '事件简称',
                        'En': 'Event',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '事件内容(200字以内)',
                        'En': 'Content',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_his_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_branch_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComBranch',
                    'keys': ['BranchName', 'HTML_ID'],
                    'check': 'BranchName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '序号',
                        'En': 'No',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '分支机构名称',
                        'En': 'BranchName',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '所在地',
                        'En': 'AreaName',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '许可证号',
                        'En': 'LicenceNumber',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '设立时间',
                        'En': 'SetTime',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '负责人',
                        'En': 'PersonInCharge',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '客户服务与投诉电话',
                        'En': 'OfficePhoneNumber',
                        'v':
                        './td[7]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '详细地址(邮编)',
                        'En': 'OfficeAddress_ZipCode',
                        'v':
                        './td[8]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '电子邮箱',
                        'En': 'OfficeEmailAddress',
                        'v':
                        './td[9]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_branch_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_supervisor_info(self, response):
        '''高管'''
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComSupervisor',
                    'keys': ['HTML_ID', 'Name','Position','PresentTime'],
                    'check': 'Name',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '姓名',
                        'En': 'Name',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '性别',
                        'En': 'Gender',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '现任职务',
                        'En': 'Position',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '高管资格批准文号',
                        'En': 'ApprovalNumber',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '任现职时间',
                        'En': 'PresentTime',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '其它任职经历(与期货相关)',
                        'En': 'PostExperience',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '备注',
                        'En': 'ReMark',
                        'v':
                        './td[7]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_supervisor_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_person_info(self, response):
        '''从业人员'''
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComPerson',
                    'keys': ['Name', 'HTML_ID','Position','PresentTime'],
                    'check': 'Name',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '姓名',
                        'En': 'Name',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '性别',
                        'En': 'Gender',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '从业资格号',
                        'En': 'QualificationNumber',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '投资咨询从业证书号',
                        'En': 'InvestmentConsultingCert',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '任职部门',
                        'En': 'Department',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '职务',
                        'En': 'Position',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '任现职时间',
                        'En': 'PresentTime',
                        'v':
                        './td[7]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_person_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_shareholder_info(self, response):
        '''股东信息'''
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComShareHolder',
                    'keys': ['ShareholderName', 'HTML_ID'],
                    'check': 'ShareholderName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '股东名称',
                        'En': 'ShareholderName',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '持股比例(%)',
                        'En': 'ShareholdingRatio',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '入股时间',
                        'En': 'ShareTime',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '法定代表人',
                        'En': 'NameOfLegalRepresentative',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '注册资本(元)',
                        'En': 'RegisteredCapital',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '办公地址',
                        'En': 'OfficeAddress',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '公司网址',
                        'En': 'OfficeWebsite',
                        'v':
                        './td[7]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '所属行业',
                        'En': 'Industry',
                        'v':
                        './td[8]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '经济类型',
                        'En': 'EconomicType',
                        'v':
                        './td[9]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '备注',
                        'En': 'ReMark',
                        'v':
                        './td[10]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]

        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_shareholder_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_credit_info(self, response):
        '''诚信记录信息'''
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComCredit',
                    'keys': ['DocumentNumber', 'HTML_ID'],
                    'check': 'Date',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '时间',
                        'En': 'Date',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '类别',
                        'En': 'Category',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '实施机关',
                        'En': 'ImplementationOrgan',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '文号',
                        'En': 'DocumentNumber',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '情况简介(200字以内)',
                        'En': 'BriefIntroduction',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    }
                ]
            }]
            
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_credit_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_financial_info(self, response):
        '''财务信息'''
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComFinancial',
                    'keys': ['Years', 'HTML_ID'],
                    'check': 'Years',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '年份',
                        'En': 'Years',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '净资本 (万元)',
                        'En': 'NetCapital',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '净资产 (万元)',
                        'En': 'NetAssets',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '权益总额 (万元)',
                        'En': 'TotalRights',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '手续费收入 (万元)',
                        'En': 'FeeIncome',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '净利润 (万元)',
                        'En': 'NetProfit',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '主审会计事务所',
                        'En': 'ChiefAuditAccountingFirm',
                        'v':
                        './td[7]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '审计意见类型',
                        'En': 'TypeOfAuditOpinion',
                        'v':
                        './td[8]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '备注',
                        'En': 'ReMark',
                        'v':
                        './td[9]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
            
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_financial_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_subdebt_info(self, response):
        '''次级债信息'''
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComSubdebt',
                    'keys': ['DebtName', 'HTML_ID'],
                    'check': 'DebtName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '债务名称',
                        'En': 'DebtName',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '债务性质',
                        'En': 'DebtNature',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '债务规模',
                        'En': 'DebtScale',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '合同生效日',
                        'En': 'ContractDate',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '到期偿还日期',
                        'En': 'ReimbursementDate',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '备注',
                        'En': 'ReMark',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
            
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_subdebt_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req
        


def main():
    SinaspiderSpider.put_redis()

if __name__=='__main__':
    main()
