# -*- coding:utf-8 -*-

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
from functools import lru_cache

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
    name = 'RealEstate'
    start_urls = [
        'http://www.mohurd.gov.cn/'
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
                callback=self.mohurd_in)

    @SpiderHelp.check_response
    def mohurd_in(self, response):

        # # 一级资质房地产开发企业  836
        # yield self.request('http://219.142.101.72/showcorpinfo/showcorpinfo.aspx',
        #     headers=self.default_header,
        #     callback=self.mohurd_first_level_develop
        #     )

        # # 北京市 房地产开发企业  160*15
        # yield self.request('http://www.bjjs.gov.cn/eportal/ui?pageId=309058',
        #     headers=self.default_header,
        #     callback=self.bj_real_estate_developer
        #     )

        # # 上海市 房地产开发企业  5297
        # yield self.request('http://www.shfg.gov.cn/i/jydj/qy/s?pn=1&ps=10',
        #     headers=self.default_header,
        #     callback=self.sh_real_estate_developer
        #     )

        # # 重庆市 房地产开发企业  5297
        # yield self.request('http://www.cqkfb.com/cms/content/qysearch.htm',
        #     headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        #             'Referer': 'http://www.cqkfb.com/cms/content/qysearch.htm'},
        #     dont_filter=True,
        #     callback=self.cq_real_estate_developer
        #     )

        # # 山西 房地产开发企业  4275
        # yield self.request('http://jzsc.sxjs.gov.cn/Browse/EntQua_Fckf.aspx?page=1',
        #     headers=self.default_header,
        #     callback=self.shang1xi_real_estate_developer)

        # # 河北省 房地产开发企业  198  数据量少  换源
        # yield self.request('http://www.hebjs.gov.cn/was5/web/search?page=1&channelid=250932&perpage=200',
        #     headers=self.default_header,
        #     callback=self.hebei_real_estate_developer)

        # # 内蒙古 房地产开发企业   3958
        # yield self.request('http://www.imre.gov.cn/Inspire/creDevList.action?pageVO.pageSize=10&pageVO.startIndex=0',
        #     headers=self.default_header,
        #     callback=self.nmg_real_estate_developer)

        # # 辽宁 房地产开发企业 
        # yield self.request('http://www.fdc.lnjst.gov.cn/ApproveWeb/HouseEntWeb/PublicList.aspx?ftype=1&fcol=10001003&fnumber=1000100302',
        #     headers=self.default_header,
        #     callback=self.liaoning_real_estate_developer)

        # # 浙江 房地产开发企业   #3000
        # yield self.request('http://zf.zjjs.com.cn/xpzzsingle.jspx?categoryid=10009439&zzlx=3&zzdj=',
        #     headers=self.default_header,
        #     callback=self.zhejiang_real_estate_developer)

        # 江西省 房地产开发企业
        # yield self.request('http://59.52.254.78/jxjsw/webSite/appInfo/entcredit.aspx',
        #     headers=self.default_header,
        #     callback=self.jiangxi_real_estate_developer)

        # # 河南省 房地产开发企业
        # yield self.request('http://www.hnjs.net.cn/qualification%E6%88%BF%E5%9C%B0%E4%BA%A7%E5%BC%80%E5%8F%91%E4%BC%81%E4%B8%9A%E8%B5%84%E8%B4%A8.shtml?page=2',
        #     headers=self.default_header,
        #     callback=self.henan_real_estate_developer)

        # # 湖北省  房地产开发企业
        # yield self.request('http://59.175.169.110/Ewmwz/QyManage/QyzzSearch.aspx?ssl=111',
        #     headers=self.default_header,
        #     callback=self.hubei_real_estate_developer)


        # # IP 受限 增加访问间隔
        # # 湖南省 房地产开发企业
        # yield self.request('http://fcjg.hunanjs.gov.cn/qygs/kf/?pagenum=1&xydj=&parentid=&zzdj=&faren=&qymc=',
        #     headers=self.default_header,
        #     meta={'proxys':True},
        #     callback=self.hunan_real_estate_developer)

        # # 广东 房地产开发企业
        # yield self.request('http://www.gzcc.gov.cn/QueryService/Query.aspx?QueryID=11&page=1',
        #     headers=self.default_header,
        #     callback=self.guangdong_real_estate_developer)

        # 深圳 房地产开发企业
        # yield self.request('http://ris.szpl.gov.cn/ssj/reportlist.aspx?typeid=2048',
        #     headers=self.default_header,
        #     callback=self.guangdong2_real_estate_developer)

        # # 广西  房地产开发企业  -- 数据不完善  换数据源
        # yield self.request('http://221.7.246.44:8018/WebInfo/Enterprise/Enterprise.aspx',
        #     headers=self.default_header,
        #     callback=self.guangxi_real_estate_developer)

        # # 海南 房地产开发企业
        # yield self.request('http://www.hnsfx.com/credit/',
        #     headers=self.default_header,
        #     callback=self.hainan_real_estate_developer)

        # # 陕西 房地产开发企业
        # yield self.request('http://222.90.206.18:9010/SxApp/Share/Web/FcqyList.aspx',
        #     headers=self.default_header,
        #     callback=self.shang3xi_real_estate_developer)

        # # 四川 房地产开发企业
        # yield self.request('http://xxgx.scjst.gov.cn/Enterprise/eList.aspx',
        #     headers=self.default_header,
        #     callback=self.sichuang_real_estate_developer)
        pass


    def guangdong2_real_estate_developer(self, response):
        pass


    def zhejiang_real_estate_developer_data(self, page, response=None):
        return urllib.parse.urlencode(
            {'newpage':str(page),
            'applyname':'',
            'starttime':'',
            'endtime':''}
            )

    @SpiderHelp.check_response
    def zhejiang_real_estate_developer(self, response):
        # 翻页
        # logger.info(response.text)
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_re',
                        'v': '//a[text()="尾页"]/@onclick',
                        're': '(\d+)'
                        },
                callback=self.zhejiang_real_estate_developer,
                method='POST',
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://zf.zjjs.com.cn/xpzzsingle.jspx?categoryid=10009439&zzlx=3&zzdj=',
                bodyfunc=self.zhejiang_real_estate_developer_data,
                redis_conn=self.r,
                redis_flag=True,
                readpage=64,
                response_type='xpath')
        for req in reqs:
            yield req

        urls = (response.urljoin(url) for url in response.xpath('//a[text()="查看详情"]/@href').extract())
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                priority=3000,
                callback=self.zhejiang_real_estate_developer_info)

    @SpiderHelp.check_response
    def zhejiang_real_estate_developer_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="table_list"]',    
                't': 'xpath',
                'db': 'RealEstate.ZheJiang_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    'string(//td[@class="detailedye_t"])',
                    't': 'xpath_first'
                },{
                    'n': '单位地址',
                    'En': 'OfficeAddress',
                    'v':
                    'string(.//td[contains(text(),"单位地址")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'LegalMan',
                    'v':
                    'string(.//td[contains(text(),"法定代表人")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '企业类型',
                    'En': 'CompanyType',
                    'v':
                    'string(.//td[contains(text(),"企业类型")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质证书号',
                    'En': 'QualificationCertNo',
                    'v':
                    'string(.//td[contains(text(),"资质证书号")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v':
                    'string(.//td[contains(text(),"资质等级")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '批准日期',
                    'En': 'QualificationStartDate',
                    'v':
                    'string(.//td[contains(text(),"批准日期")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '证书有效期',
                    'En': 'QualificationPeriod',
                    'v':
                    'string(.//td[contains(text(),"证书有效期")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def shang1xi_real_estate_developer(self, response):
        # 翻页
        # logger.info(response.text)
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '共\s*?(\d+)\s*?条'
                        },
                callback=self.shang1xi_real_estate_developer,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://jzsc.sxjs.gov.cn/Browse/EntQua_Fckf.aspx?page=%s' % page,
                redis_conn=self.r,
                redis_flag=True,
                divmod=14,
                readpage=64,
                response_type='xpath')
        for req in reqs:
            yield req

        urls = (response.urljoin(url) for url in response.xpath('//a/@onclick').re("\'(.*?)\'"))
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                priority=3000,
                callback=self.shang1xi_real_estate_developer_info)

    @SpiderHelp.check_response
    def shang1xi_real_estate_developer_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@id="main8"]/ul[1]//table[@class="tab"]',    
                't': 'xpath',
                'db': 'RealEstate.Shang1Xi_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    'string(.//td[contains(text(),"企业名称")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '地    址',
                    'En': 'Address',
                    'v':
                    'string(.//td[contains(text(),"址")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'LegalMan',
                    'v':
                    'string(.//td[contains(text(),"法定代表人")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '企业类型',
                    'En': 'CompanyType',
                    'v':
                    'string(.//td[contains(text(),"企业类型")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '企业法人营业执照注册号',
                    'En': 'BusinssRegisterNum',
                    'v':
                    'string(.//td[contains(text(),"企业法人")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '批准从事房地产开发经营业务时间',
                    'En': 'BusinessBeginDate',
                    'v':
                    'string(.//td[contains(text(),"批准从事")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '注册资本',
                    'En': 'RegisteredCapital',
                    'v':
                    'string(.//td[contains(text(),"注册资本")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '实收资本',
                    'En': 'CapitalCollection',
                    'v':
                    'string(.//td[contains(text(),"实收资本")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v':
                    'string(.//td[contains(text(),"资质等级")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '证书编号',
                    'En': 'QualificationCertNo',
                    'v':
                    'string(.//td[contains(text(),"证书编号")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '发证日期',
                    'En': 'IssuingDate',
                    'v':
                    'string(.//td[contains(text(),"发证日期")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '有效期至',
                    'En': 'QualificationPeriod',
                    'v':
                    'string(.//td[contains(text(),"有效期至")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '发证机关',
                    'En': 'IssuingOrgan',
                    'v':
                    'string(.//td[contains(text(),"发证机关")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sichuang_real_estate_developer(self, response):
        pass

    def sichuang_real_estate_developer_data(self, response):
        return urllib.parse.urlencode(
            {'__VIEWSTATE':'',
            '__VIEWSTATEGENERATOR':'',
            '__EVENTVALIDATION':'',
            'qylx':'106', # 房地产对应类型编号
            'mc':'',
            'xydm':'',
            'fr':'',
            'zsbh':'',
            'ctl00$MainContent$Button1':'',
            'validate':''
            }
            )

    @SpiderHelp.check_response
    def shang3xi_real_estate_developer(self, response):
        # 翻页
        # logger.info(response.text)
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '共(\d+)页'
                        },
                callback=self.shang3xi_real_estate_developer,
                method='POST',
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://222.90.206.18:9010/SxApp/Share/Web/FcqyList.aspx',
                bodyfunc=self.shang3xi_real_estate_developer_data,
                redis_conn=self.r,
                redis_flag=True,
                readpage=64,
                response_type='xpath')
        for req in reqs:
            yield req

        urls = (response.urljoin(url) for url in response.xpath('//tr[@class="m_dg1_i"]//@href').extract())
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                priority=3000,
                callback=self.shang3xi_real_estate_developer_info)

    def shang3xi_real_estate_developer_data(self, page, response=None):
        return urllib.parse.urlencode(
            {'__EVENTTARGET':'Pager1$btn_Go',
            '__EVENTARGUMENT':'',
            '__LASTFOCUS':'',
            '__VIEWSTATE':response.xpath('//*[@id="__VIEWSTATE"]/@value').extract_first(),
            '__VIEWSTATEGENERATOR':response.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(),
            '__EVENTVALIDATION':response.xpath('//*[@id="__EVENTVALIDATION"]/@value').extract_first(),
            'txtFName':'',
            'txtFCertiNo':'',
            'Pager1$NavPage':str(page)}
            )

    @SpiderHelp.check_response
    def shang3xi_real_estate_developer_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'RealEstate.Shang3Xi_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    'string(.//td[contains(text(),"企业名称")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '证书编号',
                    'En': 'QualificationCertNo',
                    'v':
                    'string(.//td[contains(text(),"证书编号")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '发证日期',
                    'En': 'QualificationStartDate',
                    'v':
                    'string(.//td[contains(text(),"发证日期")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '有效期至',
                    'En': 'QualificationPeriod',
                    'v':
                    'string(.//td[contains(text(),"有效期至")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v':
                    'string(.//td[contains(text(),"资质等级")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '营业执照号',
                    'En': 'BusinssRegisterNum',
                    'v':
                    'string(.//td[contains(text(),"营业执照号")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '法人代表',
                    'En': 'LegalMan',
                    'v':
                    'string(.//td[contains(text(),"法人代表")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v':
                    'string(.//td[contains(text(),"注册地址")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def hainan_real_estate_developer(self, response):
        # 翻页
        # logger.info(response.text)
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//form[@action="index.asp"][p]/p/b[text()>1][1]/text()'
                        },
                callback=self.hainan_real_estate_developer,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://www.hnsfx.com/credit/index.asp?page=%s' % page,
                redis_conn=self.r,
                redis_flag=True,
                readpage=64,
                response_type='xpath')
        for req in reqs:
            yield req

        urls = (response.urljoin(url) for url in response.xpath('//tr[@class="tr4"]/td[1]//@href').extract())
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                priority=3000,
                callback=self.hainan_real_estate_developer_info)

    @SpiderHelp.check_response
    def hainan_real_estate_developer_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//td[@id="promenu0"]/table[1]',    
                't': 'xpath',
                'db': 'RealEstate.HaiNan_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    'string(.//td[contains(text(),"企业名称")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '企业类型',
                    'En': 'CompanyType',
                    'v': 'string(.//td[contains(text(),"企业类型")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'LegalMan',
                    'v':
                    'string(.//td[p[contains(text(),"法定代表人")]]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '注册资金',
                    'En': 'RegisteredCapital',
                    'v':
                    'string(.//td[p[contains(text(),"注册资金")]]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '实收资本',
                    'En': 'CapitalCollection',
                    'v':
                    'string(.//td[p[contains(text(),"实收资本")]]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '营业执照注册号',
                    'En': 'BusinssRegisterNum',
                    'v':
                    'string(.//td[p[contains(text(),"营业执照注册号")]]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v':
                    'string(.//td[p[contains(text(),"资质等级")]]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质证书编号',
                    'En': 'QualificationCertNo',
                    'v':
                    'string(.//td[p[contains(text(),"资质证书编号")]]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '批准从事房地产开发经营业务时间',
                    'En': 'BusinessBeginDate',
                    'v':
                    'string(.//td[p[contains(text(),"业务时间")]]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '发(换)证日期',
                    'En': 'QualificationStartDate',
                    'v':
                    'string(.//td[p[contains(text(),"证日期")]]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质证书有效期至',
                    'En': 'QualificationPeriod',
                    'v':
                    'string(.//td[p[contains(text(),"有效期")]]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '企业注册地址',
                    'En': 'RegisteredAddress',
                    'v':
                    'string(.//td[p[contains(text(),"注册地址")]]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '邮政编码',
                    'En': 'ZipCode',
                    'v':
                    'string(.//td[p[contains(text(),"邮政编码")]]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '企业网址',
                    'En': 'WebSite',
                    'v':
                    'string(.//td[p[contains(text(),"企业网址")]]/following-sibling::td[1][.//@href!="http://"])',
                    't': 'xpath_first'
                },{
                    'n': '企业简介',
                    'En': 'EnterpriseIntroduction',
                    'v':
                    'string(.//td[p[contains(text(),"企业简介")]]/following-sibling::td[1])',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def guangxi_real_estate_developer(self, response):
        pass


    def guangxi_real_estate_developer_data(self, page, response=None):
        pass

    @SpiderHelp.check_response
    def guangdong_real_estate_developer(self, response):
        # 翻页
        # logger.info(response.text)
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '共(\d+)页'
                        },
                callback=self.guangdong_real_estate_developer,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://www.gzcc.gov.cn/QueryService/Query.aspx?QueryID=11&page=%s' % page,
                redis_conn=self.r,
                redis_flag=True,
                readpage=64,
                response_type='xpath')
        for req in reqs:
            yield req

        urls = ('http://www.gzcc.gov.cn/'+ url.strip() for url in response.xpath('//table[@class="formTable"]//tr/td[1]//@href').extract())
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                priority=3000,
                callback=self.guangdong_real_estate_developer_info)

    @SpiderHelp.check_response
    def guangdong_real_estate_developer_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'RealEstate.GuanDong_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    'string(.//table[@id="table1"]//*[contains(text(),"企业名称")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '企业地址',
                    'En': 'OfficeAddress',
                    'v': 'string(.//table[@id="table1"]//*[contains(text(),"企业地址")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质证书编号',
                    'En': 'QualificationCertNo',
                    'v':
                    'string(.//table[@id="table1"]//*[contains(text(),"资质证书编号")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '成立时间',
                    'En': 'SetupDate',
                    'v':
                    'string(.//table[@id="table1"]//*[contains(text(),"成立时间")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '注册资金',
                    'En': 'RegisteredCapital',
                    'v':
                    'string(.//table[@id="table1"]//*[contains(text(),"注册资金")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '营业执照',
                    'En': 'BusinssRegisterNum',
                    'v':
                    'string(.//table[@id="table1"]//*[contains(text(),"营业执照")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '经济性质',
                    'En': 'CompanyType',
                    'v':
                    'string(.//table[@id="table1"]//*[contains(text(),"经济性质")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质名称',
                    'En': 'QualificationType',
                    'v':
                    '//table[@id="table1"]//tr[td[text()="资质名称"]]/following-sibling::tr[1]/td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v':
                    '//table[@id="table1"]//tr[td[text()="资质名称"]]/following-sibling::tr[1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '有效期限',
                    'En': 'QualificationPeriod',
                    'v':
                    '//table[@id="table1"]//tr[td[text()="资质名称"]]/following-sibling::tr[1]/td[3]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def hunan_real_estate_developer(self, response):
        # 翻页
        # logger.info(response.text)
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//center/table[@class="box"]//text()[string(.)="页/共"]/following-sibling::*[text()>0]/text()'
                        },
                callback=self.hunan_real_estate_developer,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://fcjg.hunanjs.gov.cn/qygs/kf/?pagenum=%s&xydj=&parentid=&zzdj=&faren=&qymc=' % page,
                redis_conn=self.r,
                redis_flag=True,
                readpage=64,
                meta={'proxys':True},
                response_type='xpath')
        for req in reqs:
            yield req

        urls = (response.urljoin(url) for url in response.xpath('//*[@id="table_list"]//tr[position()>2]//@href').extract())
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                priority=3000,
                meta={'proxys':True},
                callback=self.hunan_real_estate_developer_info)

    @SpiderHelp.check_response
    def hunan_real_estate_developer_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="white_title_big"]',    
                't': 'xpath',
                'db': 'RealEstate.HuNan_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    'string(.//td[contains(text(),"企业名称")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v': 'string(.//td[contains(text(),"组织机构代码")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '所在城市',
                    'En': 'CityName',
                    'v':
                    'string(.//td[contains(text(),"所在城市")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '所在区县',
                    'En': 'countyName',
                    'v':
                    'string(.//td[contains(text(),"所在区县")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '主管部门',
                    'En': 'Depat',
                    'v':
                    'string(.//td[contains(text(),"主管部门")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '企业详细地址',
                    'En': 'OfficeAddress',
                    'v':
                    'string(.//td[contains(text(),"企业详细地址")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '网址',
                    'En': 'WebSite',
                    'v':
                    'string(.//td[contains(text(),"网址")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '登记注册类型',
                    'En': 'RegisteredType',
                    'v':
                    'string(.//td[contains(text(),"登记注册类型")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfOperation',
                    'v':
                    'string(.//td[contains(text(),"经营范围")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '营业执照注册号',
                    'En': 'BusinssRegisterNum',
                    'v':
                    'string(.//td[contains(text(),"营业执照注册号)]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '工商注册日期',
                    'En': 'BusinessRegisterDate',
                    'v':
                    'string(.//td[contains(text(),"工商注册日期")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '营业执照到期日',
                    'En': 'BusinessEndDate',
                    'v':
                    'string(.//td[contains(text(),"营业执照到期日")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'LegalMan',
                    'v':
                    'string(.//td[contains(text(),"法定代表人")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v':
                    'string(.//td[contains(text(),"资质等级")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质证书编号',
                    'En': 'QualificationCertNo',
                    'v':
                    'string(.//td[contains(text(),"资质证书编号")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质证书发证机关',
                    'En': 'IssuingOrgan',
                    'v':
                    'string(.//td[contains(text(),"资质证书发证机关")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '资质证书发证日期',
                    'En': 'IssuingDate',
                    'v':
                    'string(.//td[contains(text(),"资质证书发证日期")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '证书有效期至',
                    'En': 'QualificationPeriod',
                    'v':
                    'string(.//td[contains(text(),"证书有效期至")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '批准从事房地产开发经营日期',
                    'En': 'BusinessBeginDate',
                    'v':
                    'string(.//td[contains(text(),"批准从事房地产开发经营日期")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '总经理',
                    'En': 'Manager',
                    'v':
                    'string(.//td[contains(text(),"总经理")]//following-sibling::td[1])',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def hubei_real_estate_developer(self, response):
        # 翻页
        # logger.info(response.text)
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//span[@id="labPageCount"]/text()'
                        },
                callback=self.hubei_real_estate_developer,
                method='POST',
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.url,
                bodyfunc=self.hunan_real_estate_developer_data,
                redis_conn=self.r,
                redis_flag=True,
                readpage=64,
                response_type='xpath')
        for req in reqs:
            yield req

        urls = (response.urljoin(url) for url in response.xpath('//table[@class="table"]//tr[position()>1 and position()<last()]//@href').extract())
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                priority=3000,
                callback=self.hubei_real_estate_developer_info)

    @SpiderHelp.check_response
    def hubei_real_estate_developer_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'RealEstate.HuBei_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    '//td[contains(text(),"企业名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v': '//td[contains(text(),"注册地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码(组织机构代码)',
                    'En': 'OrganizationCode',
                    'v':
                    '//td[contains(text(),"统一社会信用代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '营业执照注册号',
                    'En': 'BusinssRegisterNum',
                    'v':
                    '//td[contains(text(),"营业执照注册号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经济性质',
                    'En': 'CompanyType',
                    'v':
                    '//td[contains(text(),"经济性质")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资本(万元)',
                    'En': 'RegisteredCapital',
                    'v':
                    '//td[contains(text(),"注册资本")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'LegalMan',
                    'v':
                    '//td[contains(text(),"法定代表人")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '建立时间',
                    'En': 'SetupDate',
                    'v':
                    '//td[contains(text(),"建立时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人职务',
                    'En': 'LegalManPost',
                    'v':
                    '//td[contains(text(),"法定代表人职务")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人职称',
                    'En': 'LegalManTitle',
                    'v':
                    '//td[contains(text(),"法定代表人职称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '技术负责人',
                    'En': 'TechnicalLeader',
                    'v':
                    '//td[contains(text(),"技术负责人")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '技术负责人职务',
                    'En': 'TechnicalLeaderPost',
                    'v':
                    '//td[contains(text(),"技术负责人职务")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '行政许可号',
                    'En': 'LicensingNo',
                    'v':
                    '//td[contains(text(),"行政许可号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证书编号',
                    'En': 'QualificationCertNo',
                    'v':
                    '//td[contains(text(),"证书编号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证书有效期起',
                    'En': 'QualificationStartDate',
                    'v':
                    '//td[contains(text(),"证书有效期起")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '有效期(年)',
                    'En': 'QualificationPeriod',
                    'v':
                    '//td[contains(text(),"有效期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发证机关',
                    'En': 'LicensingAuthority',
                    'v':
                    '//td[contains(text(),"发证机关")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证书入库日期',
                    'En': 'QualificationAddTime',
                    'v':
                    '//td[contains(text(),"证书入库日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '备注',
                    'En': 'Remark',
                    'v':
                    '//td[contains(text(),"备注")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资质名称',
                    'En': 'QualificationGrade',
                    'v':
                    '//tr[td[contains(text(),"资质名称")]]/following-sibling::tr[1]/td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '有效开始日期',
                    'En': 'QualificationPassDate',
                    'v':
                    '//tr[td[contains(text(),"有效开始日期")]]/following-sibling::tr[1]/td[2]/text()',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def hunan_real_estate_developer_data(self,page='',response=None):
        return urllib.parse.urlencode({'__EVENTTARGET':'lbtnGo',
         '__EVENTARGUMENT':'',
         '__VIEWSTATE': response.xpath('//*[@id="__VIEWSTATE"]/@value').extract_first(),
         '__EVENTVALIDATION': response.xpath('//*[@id="__EVENTVALIDATION"]/@value').extract_first(),
         'txtSzdwmc':'',
         'txtZzjgdm':'',
         'txtPageIndex':str(page),
         'hSsl':'111'
         })

    @SpiderHelp.check_response
    def henan_real_estate_developer(self, response):
        # 翻页
        # logger.info(response.text)
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_re',
                        'v': '//a[text()="尾页"]/@href',
                        're': 'page=(\d+)'
                        },
                callback=self.henan_real_estate_developer,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://www.hnjs.net.cn/qualification%E6%88%BF%E5%9C%B0%E4%BA%A7%E5%BC%80%E5%8F%91%E4%BC%81%E4%B8%9A%E8%B5%84%E8%B4%A8.shtml?page={}'.format(page),
                redis_conn=self.r,
                redis_flag=True,
                readpage=64,
                response_type='xpath')
        for req in reqs:
            yield req

        urls = (response.urljoin(url) for url in response.xpath('//div[@class="zzTable"]//tr[position()>1]//@href').extract())
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                property=3000,
                callback=self.henan_real_estate_developer_info)

    @SpiderHelp.check_response
    def henan_real_estate_developer_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="jieguoMain"]//table',    
                't': 'xpath',
                'db': 'RealEstate.HeNan_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    './/*[contains(text(),"企业名称")]/following-sibling::*[local-name() ="th" or local-name()="td"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证书类别',
                    'En': 'QualificationType',
                    'v': './/*[contains(text(),"证书类别")]/following-sibling::*[local-name() ="th" or local-name()="td"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证书编号',
                    'En': 'QualificationCertNo',
                    'v': './/*[contains(text(),"证书编号")]/following-sibling::*[local-name() ="th" or local-name()="td"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v': './/*[contains(text(),"注册地址")]/following-sibling::*[local-name() ="th" or local-name()="td"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v': './/*[contains(text(),"资质等级")]/following-sibling::*[local-name() ="th" or local-name()="td"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'LegalMan',
                    'v': './/*[contains(text(),"法定代表人")]/following-sibling::*[local-name() ="th" or local-name()="td"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司类型',
                    'En': 'CompanyType',
                    'v': './/*[contains(text(),"公司类型")]/following-sibling::*[local-name() ="th" or local-name()="td"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '批准从事经营时间',
                    'En': 'BusinessBeginDate',
                    'v': './/*[contains(text(),"批准从事经营时间")]/following-sibling::*[local-name() ="th" or local-name()="td"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '营业执照注册号',
                    'En': 'BusinssRegisterNum',
                    'v': './/*[contains(text(),"营业执照注册号")]/following-sibling::*[local-name() ="th" or local-name()="td"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '实收资本',
                    'En': 'CapitalCollection',
                    'v': './/*[contains(text(),"实收资本")]/following-sibling::*[local-name() ="th" or local-name()="td"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '有效期开始时间',
                    'En': 'QualificationStartDate',
                    'v': './/*[contains(text(),"有效期开始时间")]/following-sibling::*[local-name() ="th" or local-name()="td"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '有效期结束时间',
                    'En': 'QualificationPeriod',
                    'v': 'string(.//*[contains(text(),"有效期结束时间")])',
                    't': 'xpath_re',
                    're': '：(.+)'
                },{
                    'n': '发证日期',
                    'En': 'IssuingDate',
                    'v': 'string(.//*[contains(text(),"发证日期")])',
                    't': 'xpath_re',
                    're': '：(.+)'
                },{
                    'n': '发证机构',
                    'En': 'LicensingAuthority',
                    'v': './/*[contains(text(),"发证机构")]/following-sibling::*[local-name() ="th" or local-name()="td"]/text()',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def jiangxi_real_estate_developer(self, response):
        body = self.jiangxi_real_estate_developer_data(response=response)
        yield self.request(response.url,
            method='POST',
            body=body,
            callback=self.jiangxi_real_estate_developer_list)


    def jiangxi_real_estate_developer_list(self, response):
        # 翻页
        # logger.info(response.text)
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//span[@id="_ctl0_ContentPlaceHolder1_Pager1_Pages"]/text()'
                        },
                callback=self.jiangxi_real_estate_developer_list,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: response.url,
                bodyfunc=self.jiangxi_real_estate_developer_data,
                redis_conn=self.r,
                redis_flag=True,
                readpage=64,
                response_type='xpath')
        for req in reqs:
            yield req

        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="News_List"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'RealEstate.Jiangxi_RealEstateDeveloperNameList',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    'string(./td[2])',
                    't': 'xpath_first'
                },{
                    'n': '证书等级',
                    'En': 'QualificationGrade',
                    'v': './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证书编号',
                    'En': 'QualificationCertNo',
                    'v': './td[3]/text()',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        urls = (response.urljoin(url) for url in response.xpath('//table[@class="News_List"]//tr[position()>1]/td[2]//@href').extract())
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                callback=self.jiangxi_real_estate_developer_info)

    def jiangxi_real_estate_developer_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="cTable"]',    
                't': 'xpath',
                'db': 'RealEstate.Jiangxi_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    'string(.//table[@class="cTable"]//tr[td[contains(text(),"企业名称")]]/td[2])',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'LegalMan',
                    'v': 'string(.//table[@class="cTable"]//tr[td[contains(text(),"法定代表人")]]/td[2])',
                    't': 'xpath_first'
                },{
                    'n': '企业地址',
                    'En': 'OfficeAddress',
                    'v': './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v': 'string(.//table[@class="cTable"]//tr[td[contains(text(),"资质等级")]]/td[2])',
                    't': 'xpath_first'
                },{
                    'n': '资质证书编号',
                    'En': 'QualificationCertNo',
                    'v': 'string(.//table[@class="cTable"]//tr[td[contains(text(),"资质证书编号")]]/td[2])',
                    't': 'xpath_first'
                },{
                    'n': '发证部门',
                    'En': 'LicensingAuthority',
                    'v': 'string(.//table[@class="cTable"]//tr[td[contains(text(),"发证部门")]]/td[2])',
                    't': 'xpath_first'
                },{
                    'n': '发证日期',
                    'En': 'DateOfIssuing',
                    'v': 'string(.//table[@class="cTable"]//tr[td[contains(text(),"发证日期")]]/td[2])',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def jiangxi_real_estate_developer_data(self, page='', response=None):
        return urllib.parse.urlencode({
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': response.xpath('//*[@name="__VIEWSTATE"]/@value').extract_first(),
        '__VIEWSTATEGENERATOR':response.xpath('//*[@name="__VIEWSTATEGENERATOR"]/@value').extract_first(),
        '_ctl0:ContentPlaceHolder1:txtFEntName':'',
        '_ctl0:ContentPlaceHolder1:dbFEntType':'130',  # 房地产开发企业
        '_ctl0:ContentPlaceHolder1:txtCertiNo':'',
        '_ctl0:ContentPlaceHolder1:btnQuery.x':random.randint(1,32),
        '_ctl0:ContentPlaceHolder1:btnQuery.y':random.randint(1,22),
        '_ctl0:ContentPlaceHolder1:Pager1:txtGoto':page,
        '_ctl0:UBottom1:dg1':'',
        '_ctl0:UBottom1:dg2':'',
        '_ctl0:UBottom1:dg3':'',
        '_ctl0:UBottom1:dg4':'',
        '_ctl0:UBottom1:dg5':'',
        '_ctl0:UBottom1:dg6':''
        })

    @SpiderHelp.check_response
    def liaoning_real_estate_developer(self, response):
        depts = response.xpath('//select[@id="ctl00_NewsList_dgDept2"]//@value').extract()
        # 各地区
        for dept in depts:
            body = self.liaoning_dept(dept, response)
            yield self.request(response.url,
                method='POST',
                body=body,
                meta={'dept': dept},
                headers=self.default_header,
                callback=self.liaoning_real_estate_developer_list)

    # @SpiderHelp.check_response
    def liaoning_real_estate_developer_list(self, response):
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '共(\d+)页'
                        },
                callback=self.liaoning_real_estate_developer_list,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://www.fdc.lnjst.gov.cn/ApproveWeb/HouseEntWeb/PublicList.aspx?ftype=1&fcol=10001003&fnumber=1000100302',
                bodyfunc=self.liaoning_page_go(response.meta['dept']),
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='xpath')
        for req in reqs:
            yield req

        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="cGrid1"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'RealEstate.LiaoNing_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v': './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '所在城市',
                    'En': 'CityName',
                    'v': '//*[@selected="selected"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '审批机关',
                    'En': 'LicensingAuthority',
                    'v': './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证书有效期至',
                    'En': 'QualificationPeriod',
                    'v': './td[5]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            # print(item)
            yield item

        


    def liaoning_page_go(self, dept):
        def data(page, response):
            return urllib.parse.urlencode({'__EVENTTARGET': 'ctl00$NewsList$Pager2$btn_Go',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS':'',
            '__VIEWSTATE':response.xpath('//*[@id="__VIEWSTATE"]/@value').extract_first(),
            'ctl00$NewsList$dgDept2': dept,
            'ctl00$NewsList$Pager2$NavPage': page})
        return data

    def liaoning_dept(self, dept, response):
        return urllib.parse.urlencode({'__EVENTTARGET': 'ctl00$NewsList$dgDept2',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS':'',
        '__VIEWSTATE':response.xpath('//*[@id="__VIEWSTATE"]/@value').extract_first(),
        'ctl00$NewsList$dgDept2': dept,
        'ctl00$NewsList$Pager2$NavPage': ''})

    @SpiderHelp.check_response
    def nmg_real_estate_developer(self, response):
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': 'hdl_totalCount\s*?=\s*?(\d+)'
                        },
                callback=self.nmg_real_estate_developer,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://www.imre.gov.cn/Inspire/creDevList.action?pageVO.pageSize=10&pageVO.startIndex=%s' % (page * 10 - 10),
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                divmod=10,
                response_type='xpath')
        for req in reqs:
            yield req

        urls = ('http://www.imre.gov.cn/Inspire/' + url 
            for url in response.xpath('//tr[td[11]]/td[1]//@href').extract())
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                callback=self.nmg_real_estate_developer_info)

    @SpiderHelp.check_response
    def nmg_real_estate_developer_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@id="lay0"]/table[@class="formdata"]',    
                't': 'xpath',
                'db': 'RealEstate.Nmg_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    'string(.//td[contains(text(),"企业名称")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '所在省(自治区、直辖市)',
                    'En': 'Province',
                    'v': './/td[contains(text(),"所在省")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码（法人代码）',
                    'En': 'LegalCode',
                    'v': './/td[contains(text(),"法人代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '所在城市',
                    'En': 'CityName',
                    'v': './/td[contains(text(),"所在城市")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '网址',
                    'En': 'WebSite',
                    'v': 'string(.//td[contains(text(),"网址")]/following-sibling::td[1])',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfOperation',
                    'v': '//td[contains(text(),"证书编号")]/following-sibling::td[1]/text()',
                    't': 'xpath_join'
                },{
                    'n': '法人统一社会信用代码(营业执照注册号)',
                    'En': 'BusinssRegisterNum',
                    'v': '//td[contains(text(),"营业执照注册号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '工商注册日期',
                    'En': 'BusinessRegisterDate',
                    'v': '//td[contains(text(),"工商注册日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '营业执照到期日',
                    'En': 'BusinessEndDate',
                    'v': '//td[contains(text(),"营业执照到期日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '批准从事房地产开发经营日期',
                    'En': 'BusinessBeginDate',
                    'v': '//td[contains(text(),"批准从事房地产开发经营日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'LegalMan',
                    'v': '//td[contains(text(),"法定代表人")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '总经理',
                    'En': 'Manager',
                    'v': '//td[contains(text(),"总经理")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v': '//td[contains(text(),"资质等级")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资质证书编号',
                    'En': 'QualificationCertNo',
                    'v': '//td[contains(text(),"资质证书编号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发证机关',
                    'En': 'IssuingOrgan',
                    'v': '//td[contains(text(),"发证机关")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发证日期',
                    'En': 'IssuingDate',
                    'v': '//td[contains(text(),"发证日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资质证书到期日',
                    'En': 'QualificationPeriod',
                    'v': '//td[contains(text(),"资质证书到期日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '银行信用等级',
                    'En': 'BankCreditLevel',
                    'v': '//td[contains(text(),"银行信用等级")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '银行信用等级证书号',
                    'En': 'BankCreditCertNo',
                    'v': '//td[contains(text(),"银行信用等级证书号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '银行信用等级评定机构',
                    'En': 'BankCredirPassOrgan',
                    'v': '//td[contains(text(),"银行信用等级评定机构")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '银行信用等级证书到期日',
                    'En': 'BankEffectEndDate',
                    'v': '//td[contains(text(),"银行信用等级证书到期日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '房地产开发企业简介',
                    'En': 'EnterpriseIntroduction',
                    'v': '//table[thead[contains(string(.),"房地产开发企业简介")]]//td/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            # print(item)
            yield item


    @SpiderHelp.check_response
    def hebei_real_estate_developer(self, response):
        urls = ('http://www.hebjs.gov.cn/was5/web/' + url 
            for url in response.xpath('//a[text()="基本信息"]/@href').extract())
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                callback=self.hebei_real_estate_developer_info)

    @SpiderHelp.check_response
    def hebei_real_estate_developer_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'RealEstate.HeBei_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    '//td[contains(text(),"企业名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '详细地址',
                    'En': 'OfficeAddress',
                    'v': '//td[contains(text(),"详细地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码/组织机构代码',
                    'En': 'OrganizationCode',
                    'v': '//td[contains(text(),"组织机构代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'LegalMan',
                    'v': '//td[contains(text(),"法定代表人")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资质资格',
                    'En': 'Qualification',
                    'v': '//td[contains(text(),"资质资格")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证书编号',
                    'En': 'QualificationCertNo',
                    'v': '//td[contains(text(),"证书编号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '剩余有效期',
                    'En': 'QualificationPeriod',
                    'v': '//td[contains(text(),"剩余有效期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资质类别及等级',
                    'En': 'QualificationGrade',
                    'v': '//td[contains(text(),"资质类别及等级")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发证机关',
                    'En': 'IssuingOrgan',
                    'v': '//td[contains(text(),"发证机关")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def cq_real_estate_developer(self, response):
        # if self.response_failed(response):
        #     return self.new_request(response)
        # 翻页
        totalpage = int(re.compile('总计\s*?(\d+)\s*?个记录').search(response.text).group(1)) / 15
        page = 1
        while page < totalpage:
            yield  scrapy.FormRequest('http://www.cqkfb.com/cms/content/qysearch.htm',
                method='POST',
                formdata={'pgno':[str(page),str(page-1)],
                        'qymc':'',
                        'ssqx':'',
                        'zzdj':''},
                headers=self.default_header,
                callback=self.cq_real_estate_developer_list)
            page += 1
            time.sleep(0.5)

    def cq_real_estate_developer_list(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        urls = ('http://www.cqkfb.com'+url for url in response.xpath('//a[text()="查看"]/@href').extract())
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                priority=3000,
                callback=self.cq_real_estate_developer_info)

    def cq_real_estate_developer_info(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'RealEstate.Cq_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    '//td[b[contains(text(),"企业名称")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '详细办公地址',
                    'En': 'OfficeAddress',
                    'v': '//td[b[contains(text(),"详细办公地址")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法人营业执照注册号',
                    'En': 'BusinssRegisterNum',
                    'v': '//td[b[contains(text(),"法人营业执照注册号")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '营业执照到期日',
                    'En': 'BusinessEndDate',
                    'v': '//td[b[contains(text(),"营业执照到期日")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '批准从事房地产开发经营日期',
                    'En': 'BusinessBeginDate',
                    'v': '//td[b[contains(text(),"批准从事房地产开发经营日期")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资本（万元）',
                    'En': 'RegisteredCapital',
                    'v': '//td[b[contains(text(),"注册资本")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v': '//td[b[contains(text(),"组织机构代码")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '登记注册类型',
                    'En': 'RegisteredType',
                    'v': '//td[b[contains(text(),"登记注册类型")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '企业成立时间',
                    'En': 'SetupDate',
                    'v': '//td[b[contains(text(),"企业成立时间")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '工商登记机关',
                    'En': 'LicensingAuthority',
                    'v': '//td[b[contains(text(),"工商登记机关")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'LegalMan',
                    'v': '//td[b[contains(text(),"法定代表人")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '实收资本（万元）',
                    'En': 'CapitalCollection',
                    'v': '//td[b[contains(text(),"实收资本")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '企业简介',
                    'En': 'EnterpriseIntroduction',
                    'v': 'string(.//div[@id="tagContent"]/div[1]//table)',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfOperation',
                    'v': 'string(.//div[@id="tagContent"]/div[2]//table//tr[2])',
                    't': 'xpath_first'
                },{
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v': '//div[@id="tagContent"]/div[3]//table//tr[2]/td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证书编号',
                    'En': 'QualificationCertNo',
                    'v': '//div[@id="tagContent"]/div[3]//table//tr[2]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发证时间',
                    'En': 'QualificationStartDate',
                    'v': '//div[@id="tagContent"]/div[3]//table//tr[2]/td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '有效期',
                    'En': 'QualificationPeriod',
                    'v': '//div[@id="tagContent"]/div[3]//table//tr[2]/td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '备注',
                    'En': 'Remark',
                    'v': '//div[@id="tagContent"]/div[3]//table//tr[2]/td[5]/text()',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item


    def sh_real_estate_developer(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'data/total'
                        },
                callback=self.sh_real_estate_developer,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://www.shfg.gov.cn/i/jydj/qy/s?pn=%s&ps=10' % page,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                divmod=10,
                response_type='json')
        for req in reqs:
            yield req

        JS = json.loads(response.text)
        for item in JS['data']['list']:
            url = 'http://www.shfg.gov.cn/i/jydj/kfqy/?id=%s&type=1' % item['kfp_number']
            yield self.request(url,
                headers=self.default_header,
                priority=2000,
                callback=self.sh_real_estate_developer_info)

    def sh_real_estate_developer_info(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'json',
                'db': 'RealEstate.Sh_RealEstateDeveloper',
                'keys': ['Company'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    'data/corpname',
                    't': 'json'
                },{
                    'n': '所在区县',
                    'En': 'CityName',
                    'v': 'data/cityname',
                    't': 'json'
                },{
                    'n': '登记注册类型',
                    'En': 'RegisteredType',
                    'v': 'data/registertype',
                    't': 'json'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfOperation',
                    'v': 'data/workscope',
                    't': 'json'
                },{
                    'n': '法人营业执照注册号',
                    'En': 'BusinssRegisterNum',
                    'v': 'data/businessregisternum',
                    't': 'json'
                },{
                    'n': '营业执照到期日期',
                    'En': 'BusinessEndDate',
                    'v': 'data/businessenddate',
                    't': 'json'
                },{
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v': 'data/aptitude',
                    't': 'json'
                },{
                    'n': '资质证书发证日期',
                    'En': 'QualificationPassDate',
                    'v': 'data/passdate',
                    't': 'json'
                },{
                    'n': '资质等级有效期限（结束）',
                    'En': 'QualificationPeriod',
                    'v': 'data/effectenddate',
                    't': 'json'
                },{
                    'n': '总经理',
                    'En': 'Manager',
                    'v': 'data/manager',
                    't': 'json'
                },{
                    'n': '银行信用等级证书',
                    'En': 'BankCreditCertNo',
                    'v': 'data/certificatenum',
                    't': 'json'
                },{
                    'n': '银行信用等级有效期限（开始）',
                    'En': 'BankEffectStartDate',
                    'v': 'data/bankeffectstartdate',
                    't': 'json'
                },{
                    'n': '质量管理体系认证日期',
                    'En': 'QualityPassDate',
                    'v': 'data/qualitypassdate',
                    't': 'json'
                },{
                    'n': '质量管理体系认证机构',
                    'En': 'QualityPassDept',
                    'v': 'data/qualitypassdept',
                    't': 'json'
                },{
                    'n': '质量管理体系认证证书有效期限（开始）',
                    'En': 'QEffectStartDate',
                    'v': 'data/qeffectstartdate',
                    't': 'json'
                },{
                    'n': '质量管理体系认证证书有效期限（结束）',
                    'En': 'QeffectEndDate',
                    'v': 'data/qeffectenddate',
                    't': 'json'
                },{
                    'n': '法人代码',
                    'En': 'LegalCode',
                    'v': 'data/legalcode',
                    't': 'json'
                },{
                    'n': '网址',
                    'En': 'WebSite',
                    'v': 'data/website',
                    't': 'json'
                },{
                    'n': '工商注册日期',
                    'En': 'BusinessRegisterDate',
                    'v': 'data/businessregisterdate',
                    't': 'json'
                },{
                    'n': '法定代表人',
                    'En': 'LegalMan',
                    'v': 'data/legalman',
                    't': 'json'
                },{
                    'n': '资质等级编号',
                    'En': 'QualificationLevelNo',
                    'v': 'data/aptitudenum',
                    't': 'json'
                },{
                    'n': '资质等级有效期限（开始）',
                    'En': 'QualificationLevelStartDate',
                    'v': 'data/effectstartdate',
                    't': 'json'
                },{
                    'n': '批准从事房地产开发经营日期',
                    'En': 'BusinessBeginDate',
                    'v': 'data/businessbegindate',
                    't': 'json'
                },{
                    'n': '银行信用等级',
                    'En': 'CreditLevel',
                    'v': 'data/creditlevel',
                    't': 'json'
                },{
                    'n': '银行信用等级评定机构',
                    'En': 'BnakPassDept',
                    'v': 'data/bankpassdept',
                    't': 'json'
                },{
                    'n': '银行信用等级有效期限（结束）',
                    'En': 'BankCreditEndDate',
                    'v': 'data/bankeffectenddate',
                    't': 'json'
                },{
                    'n': '质量管理体系认证证书号',
                    'En': 'QualificationCertNo',
                    'v': 'data/qualitycertificate',
                    't': 'json'
                },{
                    'n': '资质证书发证机关',
                    'En': 'PassDept',
                    'v': 'data/passdept',
                    't': 'json'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def bj_real_estate_developer_data(self, page, response):
        return urllib.parse.urlencode({'filter_LIKE_QYMC':'',
                                        'filter_LIKE_ZCDZSHI':'',
                                        'filter_LIKE_YZZZSBH':'',
                                        'filter_LIKE_YZZDJ':'',
                                        'currentPage':str(page),
                                        'pageSize':'15',
                                        'OrderByField':'',
                                        'OrderByDesc':''})

    def bj_real_estate_developer(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_re',
                        'v': '//a[text()="尾页"]/@onclick',
                        're': 'value=(\d+)'
                        },
                callback=self.bj_real_estate_developer,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://www.bjjs.gov.cn/eportal/ui?pageId=309058',
                bodyfunc=self.bj_real_estate_developer_data,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='xpath')
        for req in reqs:
            yield req

        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="gridview"]//td[@style]',    
                't': 'xpath',
                'db': 'RealEstate.Bj_RealEstateDeveloper',
                'keys': ['Company','CertificateNo','QualificationPeriod'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    './text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v': './following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '行政相对人代码',
                    'En': 'Code',
                    'v': './following-sibling::td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法人代表',
                    'En': 'LegalRepresentative',
                    'v': './following-sibling::td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证书编号',
                    'En': 'CertificateNo',
                    'v': './following-sibling::td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发证日期',
                    'En': 'DateOfIssuing',
                    'v': './following-sibling::td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '有效期截止',
                    'En': 'QualificationPeriod',
                    'v': './following-sibling::td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资质证书情况',
                    'En': 'QualificationGrade',
                    'v': './following-sibling::td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '许可机关',
                    'En': 'LicensingAuthority',
                    'v': './following-sibling::td[8]/text()',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def mohurd_first_level_develop_data(self, page, response=None):
        return urllib.parse.urlencode({
            '__VIEWSTATE':response.xpath('//*[@id="__VIEWSTATE"]/@value').extract_first(),
            '__EVENTTARGET':'',
            '__EVENTARGUMENT':'',
            '__EVENTVALIDATION':response.xpath('//*[@id="__EVENTVALIDATION"]/@value').extract_first(),
            'TextBox1':'',
            'TextBox2': '',
            'DropDownList1': '',
            'AspNetPager1_input':str(page),
            'AspNetPager1':'go'
                })

    # @SpiderHelp.check_response
    def mohurd_first_level_develop(self, response):
        if self.response_failed(response):
            return self.new_request(response)
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '分(\d+)页'
                        },
                callback=self.mohurd_first_level_develop,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://219.142.101.72/showcorpinfo/showcorpinfo.aspx',
                bodyfunc=self.mohurd_first_level_develop_data,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='xpath')
        for req in reqs:
            yield req

        # 中华人民共和国住房与城乡建设部   房地产开发一级资质企业 信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="DataGrid1"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'RealEstate.RealEstateDeveloper',
                'keys': ['Company','CertificateNo','QualificationPeriod'],
                'check': 'Company',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'Company',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '资质证书编号',
                    'En': 'CertificateNo',
                    'v': './td[3]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '资质有效期至',
                    'En': 'QualificationPeriod',
                    'v': './td[4]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '所在省',
                    'En': 'Province',
                    'v': './td[5]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '资质等级',
                    'En': 'QualificationGrade',
                    'v': '一级',
                    't': 'abs'
                },{
                    'n': '来源站',
                    'En': 'FromUrl',
                    'v': 'mohurd.gov.cn',
                    't': 'abs'
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
