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
    name = 'sac'
    start_urls = [
                'http://www.sac.net.cn/', # 证券业协会
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
        'DOWNLOAD_DELAY': 10,
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

    def _start_requests(self):
        req = []
        logger.info('Start Crawl Spider %s at rediskey %s' % (self.name,self.redis_key))
        for url in self.start_urls:
            req.append(self.request(
                url,
                    redis_flag=REDISFLAG,
                    headers=self.default_header,
                    callback=self.sac_in))
        return req

    # @SpiderHelp.check_response
    def sac_in(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        # # 从业资格
        yield scrapy.Request('http://person.sac.net.cn/pages/registration/train-line-register!orderSearch.action',
            method="POST",
            body=urllib.parse.urlencode({
                'filter_EQS_OTC_ID':'', # 略 获取所有机构类别数据
                'ORDERNAME':'AOI#AOI_NAME',  # 排序
                'ORDER':'ASC',  # 降序
                'sqlkey':'registration', # 估计是存储过程
                'sqlval':'SELECT_LINE_PERSON', # 估计是存储过程
                }),
            meta={'proxys':True},
            headers=self.default_header,
            callback=self.sac_com_Qualificatio_certificate_list1)

        # # 公司信息   http://jg.sac.net.cn/pages/publicity/securities-list.html
        # yield self.request('http://jg.sac.net.cn/pages/publicity/resource!search.action',
        #     method="POST",
        #     body=urllib.parse.urlencode({
        #         'filter_EQS_O#otc_id':'',
        #         'filter_EQS_O#sac_id':'',
        #         'filter_LIKES_aoi_name':'',
        #         'sqlkey':'publicity',
        #         'sqlval':'ORG_BY_TYPE_INFO',
        #         }),
        #     priority=1500,
        #     headers=self.default_header,
        #     callback=self.sac_com_list)

        # # 备案
        # yield self.request('http://www.sac.net.cn/cpbags/index.html',
        #     headers=self.default_header,
        #     callback=self.sac_prod_list)

    # @SpiderHelp.check_response
    def sac_prod_list(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//table[@class="mar_cen gl_list"]//@href',
                                                   },
                                           callback=self.sac_prod_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: response.urljoin(page),
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'abs',
                        'v': '50',
                        },
                callback=self.sac_prod_list,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://www.sac.net.cn/cpbags/index_%s.html' % (page-1),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    # @SpiderHelp.check_response
    def sac_prod_info(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        # 备案产品信息提取
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'xpath',
                    'db': 'Sac.Sac_ComProd',
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
                        'cpbags\/\w+\/(.*?)\.html',
                        't': 'url_re'
                    },{
                        'n': '标题',
                        'En': 'Title',
                        'v':
                        '//div[@class="xl_h"]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '小标题',
                        'En': 'Title2',
                        'v':
                        'string(.//div[@class="hei14"])',
                        't': 'xpath_re',
                        're': '(.*?号)'
                    },{
                        'n': '正文',
                        'En': 'Content',
                        'v':
                        '//div[@class="hei14"]//p[contains(string(.),"根据")]//text()|//div[@class="hei14"]//p[contains(string(.),"你公司")]//text()',
                        't': 'xpath_join'
                    },{
                        'n': '产品名称',
                        'En': 'ProdName',
                        'v':
                        'string(.//div[@class="hei14"]/div[1])',
                        't': 'xpath_re',
                        're': '发起设立的(.*?)进行了审查'
                    },{
                        'n': '公司名称',
                        'En': 'ComName',
                        'v':
                        'string(.//div[@class="hei14"]//p[contains(string(.),"：") and local-name() ="p"][1])',
                        't': 'xpath_re',
                        're': '(.*?)：'
                    },{
                        'n': '准许机关',
                        'En': 'PermissionAuthority',
                        'v':
                        '//div[@class="hei14"]/div//*[@align="right"][last()-1]//text()',
                        't': 'xpath_join'
                    },{
                        'n': '准许日期',
                        'En': 'PermissionDate',
                        'v':
                        '//div[@class="hei14"]/div//*[@align="right"][last()]//text()',
                        't': 'xpath_join'
                    }
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def sac_com_list(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_ComIndex',
                    'keys': ['ComName','Category'],
                    'check': 'ComName',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'json'
                    },{
                        'n': '中文全称',
                        'En': 'ComName',
                        'v':
                        'AOI_NAME',
                        't': 'json'
                    },{
                        'n': '协会分类',
                        'En': 'Category',
                        'v':
                        'OTC_ID',
                        't': 'json'
                    },{
                        'n': '地区代码',
                        'En': 'AreaCode',
                        'v':
                        'SAC_ID',
                        't': 'json'
                    }
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        JS = json.loads(response.text)
        url = 'http://jg.sac.net.cn/pages/publicity/resource!search.action'
        for sel in JS:
            AOI_ID = sel['AOI_ID']
            # OTC_ID = sel['OTC_ID'] # 公司类型
            # 基础信息 
            yield self.request(url,
                method='POST',
                body=urllib.parse.urlencode({'filter_EQS_aoi_id':AOI_ID,
                                         'sqlkey':'publicity',
                                         'sqlval':'SELECT_ZX_REG_INFO'}),
                priority=2000,
                headers=self.default_header,
                callback=self.sac_com_basic_info)

            # 会员信息
            yield self.request(url,
                method='POST',
                body=urllib.parse.urlencode({'filter_EQS_aoi_id':AOI_ID,
                                     'sqlkey':'info',
                                     'sqlval':'GET_ORG_INFO_AOIID'}),
                priority=2000,
                headers=self.default_header,
                callback=self.sac_com_member_info)

            # 高管
            yield self.request(url,
                method='POST',
                body=urllib.parse.urlencode({'filter_EQS_aoi_id':AOI_ID,
                                         'sqlkey':'publicity',
                                         'sqlval':'ZX_EXECUTIVE_LIST'}),
                priority=2000,
                headers=self.default_header,
                meta={'AOI_ID': AOI_ID},
                callback=self.sac_supervisor_info)

            # 分公司  
            yield self.request('http://jg.sac.net.cn/pages/publicity/resource!list.action',
                method='POST',
                body=urllib.parse.urlencode({'filter_LIKES_mboi_branch_full_name':'',
                                            'filter_LIKES_mboi_off_address':'',
                                            'filter_EQS_aoi_id':AOI_ID,
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_BRANCH_ORG',
                                            'page.sqlCKey':'SIZE_BRANCH_ORG',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':'1',
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'}),
                priority=2000,
                headers=self.default_header,
                meta={'AOI_ID': AOI_ID},
                callback=self.sac_branch_info)

            # 营业部  
            yield self.request('http://jg.sac.net.cn/pages/publicity/resource!list.action',
                method='POST',
                body=urllib.parse.urlencode({'filter_LIKES_msdi_name':'',
                                            'filter_LIKES_msdi_reg_address':'',
                                            'filter_EQS_aoi_id':AOI_ID,
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_SALES_DEPT',
                                            'page.sqlCKey':'SIZE_SALES_DEPT',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':'1',
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'}),
                priority=2000,
                headers=self.default_header,
                meta={'AOI_ID': AOI_ID},
                callback=self.sac_department_info)

            # 执业人员
            yield self.request('http://jg.sac.net.cn/pages/publicity/resource!list.action',
                method='POST',
                body=urllib.parse.urlencode({'filter_EQS_aoi_id':AOI_ID,
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_PRACTITIONERS',
                                            'page.sqlCKey':'SIZE_PRACTITONERS',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':'1',
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'}),
                priority=2000,
                headers=self.default_header,
                meta={'AOI_ID': AOI_ID},
                callback=self.sac_Practitioners_info)

    # @SpiderHelp.check_response
    def sac_branch_info(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        _configs = [{   
                'list': {
                    'n': '',
                    'v': 'result',    
                    't': 'json',
                    'db': 'Sac.Sac_ComBranch',
                    'keys': ['HTML_ID','BranchName'],
                    'check': 'BranchName',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'meta'
                    },{
                        'n': '分公司名称',
                        'En': 'BranchName',
                        'v':
                        'MBOI_BRANCH_FULL_NAME',
                        't': 'json'
                    },{
                        'n': '办公地址',
                        'En': 'OfficeAddress',
                        'v':
                        'MBOI_OFF_ADDRESS',
                        't': 'json'
                    },{
                        'n': '业务范围',
                        'En': 'ScopeOfoperation',
                        'v':
                        'MBOI_BUSINESS_SCOPE',
                        't': 'json'
                    },{
                        'n': '负责人',
                        'En': 'PersonInCharge',
                        'v':
                        'MBOI_PERSON_IN_CHARGE',
                        't': 'json'
                    },{
                        'n': '客户投诉电话',
                        'En': 'CustomerServerTel',
                        'v':
                        'MBOI_CS_TEL',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages',
                        },
                method='POST',
                callback=self.sac_branch_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://jg.sac.net.cn/pages/publicity/resource!list.action',
                bodyfunc=lambda page,response=None:urllib.parse.urlencode({'filter_LIKES_mboi_branch_full_name':'',
                                            'filter_LIKES_mboi_off_address':'',
                                            'filter_EQS_aoi_id':response.meta['AOI_ID'],
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_BRANCH_ORG',
                                            'page.sqlCKey':'SIZE_BRANCH_ORG',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':str(page),
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'}),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='json')
        for req in reqs:
            yield req

    # @SpiderHelp.check_response
    def sac_department_info(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        _configs = [{   
                'list': {
                    'n': '',
                    'v': 'result',    
                    't': 'json',
                    'db': 'Sac.Sac_ComDepartment',
                    'keys': ['HTML_ID','DepartmentName'],
                    'check': 'DepartmentName',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'meta'
                    },{
                        'n': '营业部名称',
                        'En': 'DepartmentName',
                        'v':
                        'MSDI_NAME',
                        't': 'json'
                    },{
                        'n': '办公地址',
                        'En': 'OfficeAddress',
                        'v':
                        'MSDI_REG_PCC',
                        't': 'json'
                    },{
                        'n': '负责人',
                        'En': 'PersonInCharge',
                        'v':
                        'MSDI_SALES_MANAGER',
                        't': 'json'
                    },{
                        'n': '注册地址',
                        'En': 'RegisteredAddress',
                        'v':
                        'MSDI_REG_ADDRESS',
                        't': 'json'
                    },{
                        'n': '客户服务（投诉）电话',
                        'En': 'CustomerServerTel',
                        'v':
                        'MSDI_CS_TEL',
                        't': 'json'
                    },{
                        'n': '所在地证监局投诉电话',
                        'En': 'SFC_Tel',
                        'v':
                        'MSDI_ZJJ_COMPLAINTS_TEL',
                        't': 'json'
                    },{
                        'n': '营业部电邮',
                        'En': 'EmailAddress',
                        'v':
                        'MSDI_EMAIL',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages',
                        },
                method='POST',
                callback=self.sac_department_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://jg.sac.net.cn/pages/publicity/resource!list.action',
                bodyfunc=lambda page,response=None:urllib.parse.urlencode({'filter_LIKES_msdi_name':'',
                                            'filter_LIKES_msdi_reg_address':'',
                                            'filter_EQS_aoi_id':response.meta['AOI_ID'],
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_SALES_DEPT',
                                            'page.sqlCKey':'SIZE_SALES_DEPT',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':str(page),
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'}),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='json')
        for req in reqs:
            yield req

    # @SpiderHelp.check_response
    def sac_Practitioners_info(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        _configs = [{   
                'list': {
                    'n': '',
                    'v': 'result',    
                    't': 'json',
                    'db': 'Sac.Sac_ComPractitioners',
                    'keys': ['HTML_ID','Name','Position','PracticeTime','Gender'],
                    'check': 'HTML_ID',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'meta'
                    },{
                        'n': '姓名',
                        'En': 'Name',
                        'v':
                        'MPTI_NAME',
                        't': 'json'
                    },{
                        'n': '现任职务',
                        'En': 'Position',
                        'v':
                        'MPTI_CURRENT_POSITION',
                        't': 'json'
                    },{
                        'n': '性别',
                        'En': 'Gender',
                        'v':
                        'GC_ID',
                        't': 'json'
                    },{
                        'n': '执业时间',
                        'En': 'PracticeTime',
                        'v':
                        'MPTI_PRACTICE_TIME',
                        't': 'json'
                    },{
                        'n': '备注',
                        'En': 'Remark',
                        'v':
                        'MPTI_REMARK',
                        't': 'json'
                    },{
                        'n': '资格证书',
                        'En': 'CertNo',
                        'v':
                        'MPTI_QUALIFICATION_NO',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                method='POST',
                config={'t': 'json',
                        'v': 'totalPages',
                        },
                callback=self.sac_Practitioners_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:response.url,
                bodyfunc=lambda page,response=None:urllib.parse.urlencode({'filter_EQS_aoi_id':response.meta['AOI_ID'],
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_PRACTITIONERS',
                                            'page.sqlCKey':'SIZE_PRACTITONERS',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':str(page),
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'}),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='json')
        for req in reqs:
            yield req

    # @SpiderHelp.check_response
    def sac_supervisor_info(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        _configs = [{   
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_ComSupervisor',
                    'keys': ['HTML_ID','Name','Position','StartDate'],
                    'check': 'HTML_ID',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'meta'
                    },{
                        'n': '姓名',
                        'En': 'Name',
                        'v':
                        'EI_NAME',
                        't': 'json'
                    },{
                        'n': '现任职务',
                        'En': 'Position',
                        'v':
                        'EI_CURRENT_POSITION',
                        't': 'json'
                    },{
                        'n': '性别',
                        'En': 'Gender',
                        'v':
                        'GC_ID',
                        't': 'json'
                    },{
                        'n': '中国注册会计师资格证书号码',
                        'En': 'AccountantCert',
                        'v':
                        'EI_ACCOUNTANTS_NO',
                        't': 'json'
                    },{
                        'n': '是否通过证券评级业务高级管理人员资质测试',
                        'En': 'ISPASS_SENIOR_MANAGEMENT',
                        'v':
                        'EI_ISPASS_SENIOR_MANAGEMENT',
                        't': 'json'
                    },{
                        'n': '任职起始时间',
                        'En': 'StartDate',
                        'v':
                        'EI_PRACTITIONERS_START_DATE',
                        't': 'json'
                    },{
                        'n': '证券从业人员证书号码',
                        'En': 'SECURITIES_PROFESSIONALS',
                        'v':
                        'EI_SECURITIES_PROFESSIONALS',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def sac_com_member_info(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        _configs = [{   
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_ComMember',
                    'keys': ['HTML_ID'],
                    'check': 'HTML_ID',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'json'
                    },{
                        'n': '会员ID',
                        'En': 'MemberId',
                        'v':
                        'AOI_MEMBER_NO',
                        't': 'json'
                    },{
                        'n': '机构序号',
                        'En': 'ComNo',
                        'v':
                        'AOI_NO',
                        't': 'json'
                    },{
                        'n': '社会统一信用代码',
                        'En': 'UnifiedSocialCreditCode',
                        'v':
                        'AOI_ORG_NO',
                        't': 'json'
                    },{
                        'n': '会员类别',
                        'En': 'MemberCategory',
                        'v':
                        'OPC_NAME',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def sac_com_basic_info(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        _configs = [{   
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_ComBasic',
                    'keys': ['HTML_ID'],
                    'check': 'HTML_ID',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'json'
                    },{
                        'n': 'ASC_ID',
                        'En': 'ASC_ID',
                        'v':
                        'ASC_ID',
                        't': 'json'
                    },{
                        'n': 'IS_CLOSED',
                        'En': 'IS_CLOSED',
                        'v':
                        'IS_CLOSED',
                        't': 'json'
                    },{
                        'n': '中文全称',
                        'En': 'ComName',
                        'v':
                        'MRI_CHINESE_NAME',
                        't': 'json'
                    },{
                        'n': '中文简称',
                        'En': 'ComShortName',
                        'v':
                        'MRI_CHINESE_ABBREVIATION',
                        't': 'json'
                    },{
                        'n': '注册地址',
                        'En': 'Address',
                        'v':
                        'MRI_INFO_REG',
                        't': 'json'
                    },{
                        'n': '投诉电话',
                        'En': 'COMPLAINTS_TEL',
                        'v':
                        'MRI_COMPLAINTS_TEL',
                        't': 'json'
                    },{
                        'n': '公司邮箱',
                        'En': 'OfficeEmailAddress',
                        'v':
                        'MRI_COM_EMAIL',
                        't': 'json'
                    },{
                        'n': '公司历史',
                        'En': 'ComHistory',
                        'v':
                        'MRI_COM_HISTORY',
                        't': 'json'
                    },{
                        'n': '法人代表',
                        'En': 'NameOfLegalRepresentative',
                        'v':
                        'MRI_LEGAL_REPRESENTATIVE',
                        't': 'json'
                    },{
                        'n': '公司网址',
                        'En': 'ComWebsite',
                        'v':
                        'MRI_COM_WEBSITE',
                        't': 'json'
                    },{
                        'n': '信用',
                        'En': 'MRI_CREDIT_EMP_NUM',
                        'v':
                        'MRI_CREDIT_EMP_NUML',
                        't': 'json'
                    },{
                        'n': '信用支付',
                        'En': 'MRI_CREDIT_PAID_IN_CAPITAL',
                        'v':
                        'MRI_CREDIT_PAID_IN_CAPITAL',
                        't': 'json'
                    },{
                        'n': '客户服务（投诉）电话',
                        'En': 'CustomerServerTel',
                        'v':
                        'MRI_CUSTOMER_SERVICE_TEL',
                        't': 'json'
                    },{
                        'n': '英文简称',
                        'En': 'ComEshortName',
                        'v':
                        'MRI_ENGLISH_ABBREVIATION',
                        't': 'json'
                    },{
                        'n': '英文名称',
                        'En': 'ComEnglishName',
                        'v':
                        'MRI_ENGLISH_NAME',
                        't': 'json'
                    },{
                        'n': '传真',
                        'En': 'OfficeFaxNumber',
                        'v':
                        'MRI_FAX',
                        't': 'json'
                    },{
                        'n': '成立日期',
                        'En': 'SetupTime',
                        'v':
                        'MRI_FOUND_DATE',
                        't': 'json'
                    },{
                        'n': '总经理',
                        'En': 'GeneralManager',
                        'v':
                        'MRI_GENERAL_MANAGER',
                        't': 'json'
                    },{
                        'n': '详细注册地址',
                        'En': 'RegisteredAddress',
                        'v':
                        'MRI_INFO_REG',
                        't': 'json'
                    },{
                        'n': '是否上市',
                        'En': 'IsListed',
                        'v':
                        'MRI_IS_LISTED',
                        't': 'json'
                    },{
                        'n': '业务资格许可证编号',
                        'En': 'LicenceNumber',
                        'v':
                        'MRI_LICENSE_CODE',
                        't': 'json'
                    },{
                        'n': '管理',
                        'En': 'Manager',
                        'v':
                        'MRI_MANAGER',
                        't': 'json'
                    },{
                        'n': '净资产',
                        'En': 'NetAssets',
                        'v':
                        'MRI_NET_ASSETS',
                        't': 'json'
                    },{
                        'n': '办公地址',
                        'En': 'OfficeAddress',
                        'v':
                        'MRI_OFFICE_ADDRESS',
                        't': 'json'
                    },{
                        'n': '公司邮箱',
                        'En': 'OfficeZipCode',
                        'v':
                        'MRI_OFFICE_ZIP_CODE',
                        't': 'json'
                    },{
                        'n': '社会统一信用代码',
                        'En': 'UnifiedSocialCreditCode',
                        'v':
                        'MRI_ORG_CODE',
                        't': 'json'
                    },{
                        'n': '组织结构',
                        'En': 'Organ',
                        'v':
                        'MRI_ORG_STUCTURE',
                        't': 'json'
                    },{
                        'n': '其他',
                        'En': 'Other',
                        'v':
                        'MRI_QI_TA',
                        't': 'json'
                    },{
                        'n': '注册资本',
                        'En': 'RegisteredCapital',
                        'v':
                        'MRI_REG_CAPITAL',
                        't': 'json'
                    },{
                        'n': '注册ID-对应证书ID',
                        'En': 'RegisteredID',
                        'v':
                        'MRI_REG_ID',
                        't': 'json'
                    },{
                        'n': 'MRI_REG_VER_ID',
                        'En': 'MRI_REG_VER_ID',
                        'v':
                        'MRI_REG_VER_ID',
                        't': 'json'
                    },{
                        'n': '注册地邮编',
                        'En': 'RegisteredZipCode',
                        'v':
                        'MRI_REG_ZIP_CODE',
                        't': 'json'
                    },{
                        'n': '备注',
                        'En': 'ReMark',
                        'v':
                        'MRI_REMARK',
                        't': 'json'
                    },{
                        'n': '销售部数量',
                        'En': 'SalseDeptNum',
                        'v':
                        'MRI_SALES_DEPT_NUM',
                        't': 'json'
                    },{
                        'n': '证券业务',
                        'En': 'SECURITIES_BUSINESS',
                        'v':
                        'MRI_SECURITIES_BUSINESS',
                        't': 'json'
                    },{
                        'n': '证券业务许可证',
                        'En': 'SECURITIES_LicenceNumber',
                        'v':
                        'MRI_SECURITIES_BUSINESS_CODE',
                        't': 'json'
                    },{
                        'n': '证券资格',
                        'En': 'SECURITIES_ELIGIBLE',
                        'v':
                        'MRI_SECURITIES_ELIGIBLE',
                        't': 'json'
                    },{
                        'n': '上市地代码',
                        'En': 'ListedAreaCode',
                        'v':
                        'MRI_SHANG_SHI_CODE',
                        't': 'json'
                    },{
                        'n': '上市地',
                        'En': 'ListedArea',
                        'v':
                        'MRI_SHANG_SHI_DI',
                        't': 'json'
                    },{
                        'n': '证监局监督电话',
                        'En': 'SFC_Tel',
                        'v':
                        'MRI_ZJJ_TEL',
                        't': 'json'
                    },{
                        'n': '地区代码',
                        'En': 'AreaCode',
                        'v':
                        'SAC_ID',
                        't': 'json'
                    },{
                        'n': '地区',
                        'En': 'AreaName',
                        'v':
                        'SAC_NAME',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item


    # @SpiderHelp.check_response
    def sac_com_Qualificatio_certificate_list1(self,response):
        if self.response_failed(response):
            return self.new_request(response)
        # logger.info(response.text)
        # 公司-概况
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_Com_Qualificatio',
                    'keys': ['HTML_ID'],
                    'check': 'HTML_ID',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'json'
                    },{
                        'n': '机构名称',
                        'En': 'ComName',
                        'v':
                        'AOI_NAME',
                        't': 'json'
                    },{
                        'n': '从业人员数',
                        'En': 'EmployeeNumbers',
                        'v':
                        'PR_COUNT_PERSON',
                        't': 'json'
                    },{
                        'n': '一般证券业务资格数',
                        'En': 'GeneralQualification',
                        'v':
                        'PTI0PERSON',
                        't': 'json'
                    },{
                        'n': '证券投资咨询业务(其他)',
                        'En': 'Other',
                        'v':
                        'PTI1PERSON',
                        't': 'json'
                    },{
                        'n': '证券经纪业务营销',
                        'En': 'BusinessMarketing',
                        'v':
                        'PTI2PERSON',
                        't': 'json'
                    },{
                        'n': '证券经纪人',
                        'En': 'Financingers',
                        'v':
                        'PTI3PERSON',
                        't': 'json'
                    },{
                        'n': '证券投资咨询业务(分析师)',
                        'En': 'Analyst',
                        'v':
                        'PTI4PERSON',
                        't': 'json'
                    },{
                        'n': '证券投资咨询业务(投资顾问)',
                        'En': 'InvestmentAdvisor',
                        'v':
                        'PTI5PERSON',
                        't': 'json'
                    },{
                        'n': '保荐代表人',
                        'En': 'SponsorRepresentative',
                        'v':
                        'PTI6PERSON',
                        't': 'json'
                    },{
                        'n': '投资主办人',
                        'En': 'InvestmentSponsor',
                        'v':
                        'PTI7PERSON',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for items in results:
            yield items
        # # 列表页
        JS = json.loads(response.text)
        for item in JS:
            AOI_ID = item['AOI_ID']
            totalpage = int(item['PR_COUNT_PERSON'])//100 + 1
            yield self.request('http://person.sac.net.cn/pages/registration/train-line-register!gsUDDIsearch.action',
                headers=self.default_header,
                method='POST',
                priority=2000,
                body=urllib.parse.urlencode({'ORDER': 'ASC',
                                     'ORDERNAME': 'PP#PTI_ID,PP#PPP_NAME',
                                     'filter_EQS_AOI_ID': AOI_ID,
                                     'filter_GTS_RNUM': '0',
                                     'filter_LES_ROWNUM': '100',
                                     'filter_EQS_PTI_ID':'',
                                     'sqlkey': 'registration',
                                     'sqlval': 'SEARCH_FINISH_PUBLICITY'}),
                meta={'AOI_ID': AOI_ID,'totalpage': totalpage,'proxys':True},
                callback=self.sac_com_Qualificatio_certificate_list2)

    # @SpiderHelp.check_response
    def sac_com_Qualificatio_certificate_list2(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        # logger.info(response.text)
        # 公司-个人从业资格列表
        # 从业基础信息
        AOI_ID = response.meta['AOI_ID']
        JS = json.loads(response.text)
        for item in JS:
            # 转换加密参数  
            yield self.request('http://person.sac.net.cn/pages/registration/train-line-register!gsUDDIsearch.action',
                method='POST',
                headers=self.default_header,
                body=urllib.parse.urlencode({'filter_EQS_PPP_ID':str(item['PPP_ID']),
                    'sqlkey':'registration',
                    'sqlval':'SD_A02Leiirkmuexe_b9ID'}),
                priority=3000,
                meta={'item': item, 'proxys': True},
                callback=self.Sac_person_jumps,
                )



        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'meta',
                        'v': 'totalpage',
                        },
                callback=self.sac_com_Qualificatio_certificate_list2,
                headers=self.default_header,
                method='POST',
                urlfunc=lambda page,response=None:'http://person.sac.net.cn/pages/registration/train-line-register!orderSearch.action',
                bodyfunc=lambda page, response=None:urllib.parse.urlencode({'ORDER': 'ASC',
                                     'ORDERNAME': 'PP#PTI_ID,PP#PPP_NAME',
                                     'filter_EQS_AOI_ID': AOI_ID,
                                     'filter_GTS_RNUM': page * 100 - 100,
                                     'filter_LES_ROWNUM': page * 100,
                                     'filter_EQS_PTI_ID':'',
                                     'sqlkey': 'registration',
                                     'sqlval': 'SEARCH_FINISH_PUBLICITY'}),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=20,
                meta={'proxys':True,'AOI_ID':AOI_ID},
                response_type='json')
        for req in reqs:
            yield req

    # @SpiderHelp.check_response
    def Sac_person_jumps(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        # 本页获取明文ID
        JS = json.loads(response.text)
        if JS:
            url = 'http://person.sac.net.cn/pages/registration/train-line-register!gsUDDIsearch.action'
            RPI_ID = JS[0]['RPI_ID']
            item = response.meta['item']
            item['HTML_ID'] = RPI_ID
            item['proxys'] = True
            data1 = {'filter_EQS_RH#RPI_ID':RPI_ID,
                     'sqlkey':'registration',
                     'sqlval':'SEARCH_LIST_BY_PERSON'}
            data2 = {'filter_EQS_RPI_ID':RPI_ID,
                      'sqlkey':'registration',
                      'sqlval':'SELECT_PERSON_INFO'}
            # 从业信息
            yield scrapy.Request(url,
                headers=self.default_header,
                method='POST',
                meta={**item},
                body=urllib.parse.urlencode(data2),
                priority=4000,
                callback=self.sac_person_Qualification)

            # 从业变更信息
            yield scrapy.Request(url,
                headers=self.default_header,
                method='POST',
                body=urllib.parse.urlencode(data1),
                priority=4000,
                meta={**item},
                callback=self.sac_person_Qualification_change)

    # @SpiderHelp.check_response
    def sac_person_Qualification(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_PersonQualificatioCertificate',
                    'keys': ['HTML_ID'],
                    'check': 'Name',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': 'HTML_ID',
                        'En': 'HTML_ID',
                        'v':
                        'HTML_ID',
                        't': 'meta'
                    },{
                        'n': '姓名',
                        'En': 'Name',
                        'v':
                        'RPI_NAME',
                        't': 'json'
                    },{
                        'n': '性别',
                        'En': 'Gender',
                        'v':
                        'SCO_NAME',
                        't': 'json'
                    },{
                        'n': 'image',
                        'En': 'Image',
                        'v':
                        'RPI_PHOTO_PATH',
                        't': 'json'
                    },{
                        'n': '执业岗位',
                        'En': 'Position',
                        'v':
                        'PTI_NAME',
                        't': 'json'
                    },{
                        'n': '执业机构',
                        'En': 'PractisingInstitution',
                        'v':
                        'AOI_NAME',
                        't': 'json'
                    },{
                        'n': '执业机构ID',
                        'En': 'ComID',
                        'v':
                        'AOI_ID',
                        't': 'json'
                    },{
                        'n': '证书编号',
                        'En': 'CertNo',
                        'v':
                        'CER_NUM',
                        't': 'json'
                    },{
                        'n': '所在部门',
                        'En': 'Department',
                        'v':
                        'ADI_NAME',
                        't': 'json'
                    },{
                        'n': '注册变更记录',
                        'En': 'Change',
                        'v':
                        'COUNTCER',
                        't': 'meta'
                    },{
                        'n': '诚信记录',
                        'En': 'Credit',
                        'v':
                        'COUNTCX',
                        't': 'meta'
                    },{
                        'n': '证书类别',
                        'En': 'CeryCategory',
                        'v':
                        'CTI_NAME',#未知
                        't': 'meta'
                    },{
                        'n': '学历',
                        'En': 'Education',
                        'v':
                        'ECO_NAME',
                        't': 'json'
                    },{
                        'n': '证书有效截止日期',
                        'En': 'CertEndDate',
                        'v':
                        'ARRIVE_DATE',
                        't': 'json'
                    },{
                        'n': '证书取得日期',
                        'En': 'CertGetDate',
                        'v':
                        'OBTAIN_DATE',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @SpiderHelp.check_response
    def sac_person_Qualification_change(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_PersonChangeRecord',
                    'keys': ['HTML_ID','CertGetDate'],
                    'check': 'PractisingInstitution',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': 'HTML_ID',
                        'En': 'HTML_ID',
                        'v':
                        'HTML_ID',
                        't': 'meta'
                    },{
                        'n': '执业机构',
                        'En': 'PractisingInstitution',
                        'v':
                        'AOI_NAME',
                        't': 'json'
                    },{
                        'n': '证书状态',
                        'En': 'CertState',
                        'v':
                        'CERTC_NAME',
                        't': 'json'
                    },{
                        'n': '证书编号',
                        'En': 'CertNumber',
                        'v':
                        'CER_NUM',
                        't': 'json'
                    },{
                        'n': '取得日期',
                        'En': 'CertGetDate',
                        'v':
                        'OBTAIN_DATE',
                        't': 'json'
                    },{
                        'n': '执业岗位',
                        'En': 'Position',
                        'v':
                        'PTI_NAME',
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