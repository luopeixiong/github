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


def get_area():
    res = requests.get('http://js.51jobcdn.com/in/js/2016/layer/area_array_c.js?20171103')
    RESULT = json.loads(re.compile('area=(\{.*?\})',re.S).search(res.text).group(1))
    return RESULT



class SinaspiderSpider(_RedisSpider, SpiderHelp):  #,scrapy.Spider
    name = '51job_test'
    start_urls = get_area()
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

        # 51job全站
        for _url,name in self.start_urls.items():
            url = 'http://search.51job.com/list/%s,000000,0000,00,9,{0:{1}2d},%%2520,2,{2}.html' % _url
            for i in range(1,13):
                start_url = url.format(i, '0', 1)
                formater = url.format(i, '0', '{}')
                yield self.request(start_url,
                    headers=self.default_header,
                    redis_flag=True,
                    meta={'formater': formater,'money':i},
                    callback=self.job_in)
                
        # 智联全站
        yield self.request('http://company.zhaopin.com/beijing/',
            headers=self.default_header,
            callback=self.zhilian_in)

        # 猎聘全站
        yield self.request('https://www.liepin.com/company/',
            headers=self.default_header,
            callback=self.liepin_in)

    def liepin_in(url):
        citys = ["010","020","030","040","050020","050040","050050","050090","050140","060020","060040","060080","060100","070020","070030","070040","080020","090020","090040","100020","110020","120020","130020","140020","150020","160020","170020","180020","190020","200020","210020","210040","220020","230020","240020","250020","250070","260020","270020","280020","290020","300020","310020","320","340"]
        industrys = ['040', '420', '010', '030', '050', '060', '020', '080', '100', '090', '130', '140', '150', '430', '500', '190', '240', '200', '210', '220', '460', '470', '350', '360', '180', '370', '340', '120', '110', '440', '450', '230', '260', '510', '070', '170', '380', '250', '160', '480', '270', '280', '290', '330', '310', '320', '300', '490', '390', '410', '400']
        natures = ["010","020","030","040","050","060","070","999",]
        # 分地区,分行业,分公司性质 遍历
        for city in citys:
            for industry in industrys:
                for nature in natures:
                    url = 'https://www.liepin.com/company/{city}-{industry}-{nature}/'.format(city=city,industry=industry,nature=nature)
                    fmt = url + 'pn%s/'
                    yield self.request(url,
                        headers=self.default_header,
                        meta={'fmt': fmt},
                        callback=self.liepin_company_list)

    def liepin_company_list(self, response):
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '共(\d+)页'
                        },
                callback=self.liepin_company_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['fmt'] % page,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='xpath')
        for req in reqs:
            yield req

        urls = response.xpath('//*[@class="company-name"]/a/@href').extract()
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                meta={'page':1},
                callback=self.liepin_com_homepage)

    def liepin_com_homepage(self, response):
        if response.meta['page'] == 1:
            _configs = [{
                'list': {
                        'n': '',
                        'v': '',
                        't': 'xpath',
                        'db': 'JobSpider.LiePin_Job',
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
                            'job\/(.*?).s?htm',
                            't': 'url_re',
                        }, {
                            'n': '标题',
                            'En': 'Title',
                            'v':
                            '//h1/text()',
                            't': 'xpath_first'
                        }, {
                            'n': '工作地点',
                            'En': 'City_Area',
                            'v':
                            'string(//*[@class="basic-infor"]/span[1])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '职位月薪',
                            'En': 'Money',
                            'v':
                            '//*[@class="job-item-title"]/text()',
                            't': 'xpath_join'
                        },
                        {
                            'n': '公司名称',
                            'En': 'CompanyName',
                            'v':
                            'string(//div[@class="title-info"]/h3)',
                            't': 'xpath_first'
                        },
                        {
                            'n': '工作经验',
                            'En': 'WorkExperience',
                            'v':
                            'string(//div[@class="job-qualifications"]/span[2])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '最低学历',
                            'En': 'Eduction',
                            'v':
                            'string(//div[@class="job-qualifications"]/span[1])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '语言要求',
                            'En': 'Language',
                            'v':
                            'string(//div[@class="job-qualifications"]/span[3])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '年龄要求',
                            'En': 'Age',
                            'v':
                            'string(//div[@class="job-qualifications"]/span[4])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '发布日期',
                            'En': 'PushDate',
                            'v':
                            '//time/@title',
                            't': 'xpath_first'
                        },
                        {
                            'n': '职位描述',
                            'En': 'JobDescription',
                            'v':
                            'string(//*[@class="job-item main-message job-description"]/div[@class="content content-word"])',
                            't': 'xpath_first'
                        },
                        {
                            'n': 'keywords',
                            'En': 'keywords',
                            'v':
                            'manager',
                            't': 'meta'
                        },

                ]
            }]
            results = self.item_parse(_configs, response)
            for item in results:
                yield item
                # print(item)
         # 翻页
        
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共(\d+)个'
                    },
            callback=self.liepin_com_homepage,
            headers=self.default_header,
            urlfunc=lambda page, response=None: response.meta['fmt'] % page,
            redis_conn=self.r,
            redis_flag=True,
            divmod=15,
            readpage=32,
            response_type='xpath')
        for req in reqs:
            yield req

        job_urls = (url.split('?')[0] for url in response.xpath('//*[@class="job-info"]/a/@href').extract())
        for job_url in job_urls:
            yield self.request(job_url,
                headers=self.default_header,
                callback=self.liepin_job)

    def liepin_job(self, response):
        _configs = [{
            'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'JobSpider.LiePin_Job',
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
                        'job\/(.*?).s?htm',
                        't': 'url_re',
                    }, {
                        'n': '标题',
                        'En': 'Title',
                        'v':
                        '//h1/text()',
                        't': 'xpath_first'
                    }, {
                        'n': '工作地点',
                        'En': 'City_Area',
                        'v':
                        'string(//*[@class="basic-infor"]/span[1])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '职位月薪',
                        'En': 'Money',
                        'v':
                        '//*[@class="job-item-title"]/text()',
                        't': 'xpath_join'
                    },
                    {
                        'n': '公司名称',
                        'En': 'CompanyName',
                        'v':
                        'string(//div[@class="title-info"]/h3)',
                        't': 'xpath_first'
                    },
                    {
                        'n': '工作经验',
                        'En': 'WorkExperience',
                        'v':
                        'string(//div[@class="job-qualifications"]/span[2])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '最低学历',
                        'En': 'Eduction',
                        'v':
                        'string(//div[@class="job-qualifications"]/span[1])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '语言要求',
                        'En': 'Language',
                        'v':
                        'string(//div[@class="job-qualifications"]/span[3])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '年龄要求',
                        'En': 'Age',
                        'v':
                        'string(//div[@class="job-qualifications"]/span[4])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '发布日期',
                        'En': 'PushDate',
                        'v':
                        '//time/@title',
                        't': 'xpath_first'
                    },
                    {
                        'n': '职位描述',
                        'En': 'JobDescription',
                        'v':
                        'string(//*[@class="job-item main-message job-description"]/div[@class="content content-word"])',
                        't': 'xpath_first'
                    },
                    {
                        'n': 'keywords',
                        'En': 'keywords',
                        'v':
                        'manager',
                        't': 'meta'
                    },

            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            # yield item
            print(item)

    def zhilian_in(self, response):
        citys = response.xpath('//div[@id="city"]//a/@id').extract()
        industrys = response.xpath('//div[@id="industry"]//a/@id').extract()
        for city in citys:
            for industry in industrys:
                fmt = 'http://company.zhaopin.com/{city}/{industry}/p%s/'.format(city=city,industry=industry)
                url = fmt % 1
                yield self.request(url,
                    headers=self.default_header,
                    meta={'fmt':fmt},
                    callback=self.zhilian_com_list)

    def zhilian_com_list(self, response):
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '共(\d+)页'
                        },
                callback=self.zhilian_com_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['fmt'] % page,
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='xpath')
        for req in reqs:
            yield req

        urls = response.xpath('//div[@class="jobs-list-box"]/div[a]//@href').extract()
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                meta={'page':1},
                callback=self.zhilian_com_homepage)


    def zhilian_com_homepage(self, response):

        if 'window.location.href' in response.url:
            url = re.compile("window\.location\.href=\'(.*?)\'").search(response.text).group(1)
            yield self.request(url,
                headers=self.default_header,
                callback=self.zhilian_com_info)
        elif 'm.zhaopin.com' in response.url:
            _configs = [{
                'list': {
                        'n': '',
                        'v': '',
                        't': 'xpath',
                        'db': 'JobSpider.Zhilian_Com',
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
                            'v': 'company\/([^\/]+)',
                            't': 'url_re',
                        }, {
                            'n': '公司名称',
                            'En': 'ComName',
                            'v': '//h1[@class="name"]/text()',
                            't': 'xpath_first'
                        }, {
                            'n': '公司性质',
                            'En': 'ComType',
                            'v': '//*[@class="prop"]/text()',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司规模',
                            'En': 'Scale',
                            'v': '//*[@class="scale"]/text()',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司行业',
                            'En': 'Capital',
                            'v':
                            '//*[@class="ind"]/text()',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司简介',
                            'En': 'ComProfile',
                            'v':
                            'string(//*[@class="about-main"])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司网站',
                            'En': 'WebSite',
                            'v':
                            '//div[@class="about-main"]//text()[re:test(string(.),"(?:网\s*?站地?址?)?.{0,10}\s*?[:：]\s*?[A-Za-z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+")]',
                            't': 'xpath_re',
                            're': "([A-Za-z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+)"
                        },
                        {
                            'n': '公司地址',
                            'En': 'Address',
                            'v':
                            'string(//*[@class="add"])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司电话',
                            'En': 'ComConcat',
                            'v':
                            '//div[@class="about-main"]//text()[re:test(string(.),"(?:电\s*?话|热\s*?线).{0,10}\s*?[:：]\s*?[0-9 -]{7,}")]',
                            't': 'xpath_re',
                            're': "(?:电\s*?话).{0,10}\s*?[:：]\s*?([0-9 -]{7,})"
                        },
                        {
                            'n': 'Email',
                            'En': 'Email',
                            'v':
                            '//div[@class="about-main"]//text()[re:test(string(.),"[A-Za-z0-9_-]+@[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+")]',
                            't': 'xpath_re',
                            're': "([A-Za-z0-9_-]+@[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+)"
                        },{
                            'n': 'Logo',
                            'En': 'Logo',
                            'v':
                            '//*[@class="companyLogo"]/img[@class="logo-icon"]/@src',
                            't': 'xpath_first',
                        },{
                            'n': 'keywords',
                            'En': 'keywords',
                            'v':
                            'manager',
                            't': 'meta'
                        },
                       
                ]
            }]
            results = self.item_parse(_configs, response)
            for item in results:
                # yield item
                print(item)

        elif 'http://special.zhaopin.com' in response.url:
            pass
            # TODO
        else:
            _configs = [{
                'list': {
                        'n': '',
                        'v': '',
                        't': 'xpath',
                        'db': 'JobSpider.Zhilian_Com',
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
                            '//*[@id="companyNumber"]/@value',
                            't': 'xpath_first',
                        }, {
                            'n': '公司名称',
                            'En': 'ComName',
                            'v':
                            'string(//div[@class="mainLeft"]//h1)',
                            't': 'xpath_first'
                        }, {
                            'n': '公司性质',
                            'En': 'ComType',
                            'v':
                            'string(//td[span[text()="公司性质："]]/following-sibling::*[1])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司规模',
                            'En': 'Scale',
                            'v':
                            'string(//td[span[text()="公司规模："]]/following-sibling::*[1])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司行业',
                            'En': 'Capital',
                            'v':
                            'string(//td[span[text()="公司行业："]]/following-sibling::*[1])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司简介',
                            'En': 'ComProfile',
                            'v':
                            'string(//div[@class="company-content"])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司网站',
                            'En': 'WebSite',
                            'v':
                            'string(//td[span[text()="公司网站："]]/following-sibling::*[1][not(contains(string(.)," http://null"))])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司地址',
                            'En': 'Address',
                            'v':
                            'string(//td[span[text()="公司地址："]]/following-sibling::*[1]/span[1])',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司电话',
                            'En': 'ComConcat',
                            'v':
                            '//div[@class="company-content"]//text()[re:test(string(.),"(?:电\s*?话).{0,10}\s*?[:：]\s*?[0-9 -]{7,}")]',
                            't': 'xpath_re',
                            're': "(?:电\s*?话).{0,10}\s*?[:：]\s*?([0-9 -]{7,})"
                        },
                        {
                            'n': 'Email',
                            'En': 'Email',
                            'v':
                            '//div[@class="company-content"]//text()[re:test(string(.),"[A-Za-z0-9_-]+@[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+")]',
                            't': 'xpath_re',
                            're': "([A-Za-z0-9_-]+@[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+)"
                        },
                        {
                            'n': 'Logo',
                            'En': 'LogoImages',
                            'v':
                            '//*[@class="companyLogo"]/@src',
                            't': 'xpath_first',
                        },{
                            'n': 'keywords',
                            'En': 'keywords',
                            'v':
                            'manager',
                            't': 'meta'
                        },
                       
                ]
            }]
            results = self.item_parse(_configs, response)
            for item in results:
                # yield item
                print(item)

        # 判断是否有职位在招聘
        jobs_url = response.xpath('//*[@class="moreJobs"]/@href').extract_first()
        fmt = job_urls + '&p=%s'
        if jobs_url:
            yield self.request(jobs_url,
                headers=self.default_header,
                meta={'fmt':fmt},
                callback=self.zhilian_job_list)

    def zhilian_job_list(self, response):
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//span[@class="search_yx_tj"]/em[text()>1]/text()'
                        },
                callback=self.zhilian_job_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['fmt'] % page,
                redis_conn=self.r,
                redis_flag=True,
                divmod=60,
                readpage=32,
                response_type='xpath')
        for req in reqs:
            yield req
        job_urls = (response.urljoin(url) for url in response.xpath('//td[@class="zwmc"]/div/a/@href').extract())
        for job_url in job_urls:
            yield self.request(job_url,
                headers=self.default_header,
                callback=self.zhilian_job_info)

    def zhilian_job_info(self, response):
        _configs = [{
            'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'JobSpider.Job51_com',
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
                        '//input[@id="hidCOID"]/@value',
                        't': 'xpath_first',
                    }, {
                        'n': '公司名称',
                        'En': 'ComName',
                        'v':
                        '//h1/@title',
                        't': 'xpath_first'
                    }, {
                        'n': '公司类型',
                        'En': 'ComType',
                        'v':
                        '//p[@class="ltype"]/text()',
                        't': 'xpath_re',
                        're': '^([\s\S]+?)\|[\s\S]+?\|[\s\S]+$'
                    },
                    {
                        'n': '人数规模',
                        'En': 'Scale',
                        'v':
                        '//p[@class="ltype"]/text()',
                        't': 'xpath_re',
                        're': '^[\s\S]+?\|([\s\S]+?)\|[\s\S]+$'
                    },
                    {
                        'n': '行业分类',
                        'En': 'Capital',
                        'v':
                        '//p[@class="ltype"]/text()',
                        't': 'xpath_re',
                        're': '^[\s\S]+?\|[\s\S]+?\|([\s\S]+)$'
                    },
                    {
                        'n': '公司简介',
                        'En': 'ComProfile',
                        'v':
                        'string(//div[contains(@class,"con_msg")]/div[@class="in"])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '公司电话',
                        'En': 'ComConcat',
                        'v':
                        '//text()[re:test(string(.),"(?:电\s*?话).{0,10}\s*?[:：]\s*?[0-9 -]{7,}")]',
                        't': 'xpath_re',
                        're': "(?:电\s*?话).{0,10}\s*?[:：]\s*?([0-9 -]{7,})"
                    },
                    {
                        'n': '邮政编码',
                        'En': 'ZipCode',
                        'v':
                        'string(//span[text()="公司地址："]/following-sibling::node()[1])',
                        't': 'xpath_re',
                        're': '邮编\s*?[:：]\s*?(\d+)'
                    },
                    {
                        'n': '公司网址',
                        'En': 'WebSite',
                        'v':
                        '//div[@class="tCompany_full"]//text()[re:test(string(.),"(?:https?:\/\/)[a-zA-Z0-9]+(?:\.[a-zA-Z0-9_-]+)+")]',
                        't': 'xpath_re',
                        're': '((?:https?:\/\/)[a-zA-Z0-9]+(?:\.[a-zA-Z0-9_-]+)+)'
                    },
                    {
                        'n': '公司地址',
                        'En': 'Address',
                        'v':
                        'string(//span[text()="公司地址："]/following-sibling::node()[1])',
                        't': 'xpath_re',
                        're': '(.+)(?:\(邮编){1,}?'
                    },
                    {
                        'n': 'Email',
                        'En': 'Email',
                        'v':
                        '//div[@class="tCompany_full"]//text()[re:test(string(.),"[A-Za-z0-9]+@[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+") and string(.)!="club@51job.com" and string(.)!="hr@51job.com"]',
                        't': 'xpath_re',
                        're': "([A-Za-z0-9_-]+@[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+)"
                    },{
                        'n': 'keywords',
                        'En': 'keywords',
                        'v':
                        'manager',
                        't': 'meta'
                    },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
            # print(item)

    def job_in(self, response):
        # 翻页
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '共(\d+)页'
                        },
                callback=self.job_in,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formater'].format(page),
                redis_conn=self.r,
                redis_flag=True,
                readpage=32,
                response_type='xpath')
        for req in reqs:
            yield req

        urls = (response.urljoin(url) for url in response.xpath('//div[@class="dw_table"]/div[@class="el"]/p[1]//@href').extract())
        for url in urls:    
            yield self.request(url,
                headers=self.default_header,
                meta={'money': response.meta['money']},
                callback=self.job_info)

        urls = (response.urljoin(url) for url in response.xpath('//div[@class="dw_table"]/div[@class="el"]/span[1]//@href').extract())
        for url in urls:    
            yield self.request(url,
                headers=self.default_header,
                callback=self.com_info)

    def com_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'xpath',
                    'db': 'Job51.ComPany',
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
                        '//input[@id="hidCOID"]/@value',
                        't': 'xpath_first',
                    },{
                        'n': '公司名称',
                        'En': 'ComName',
                        'v':
                        '//h1/@title',
                        't': 'xpath_first'
                    },{
                        'n': '公司类型',
                        'En': 'ComType',
                        'v':
                        '//p[@class="ltype"]/text()',
                        't': 'xpath_re',
                        're': '^([\s\S]+?)\|[\s\S]+?\|[\s\S]+$'
                    },
                    {
                        'n': '人数规模',
                        'En': 'Scale',
                        'v':
                        '//p[@class="ltype"]/text()',
                        't': 'xpath_re',
                        're': '^[\s\S]+?\|([\s\S]+?)\|[\s\S]+$'
                    },
                    {
                        'n': '行业分类',
                        'En': 'Capital',
                        'v':
                        '//p[@class="ltype"]/text()',
                        't': 'xpath_re',
                        're': '^[\s\S]+?\|[\s\S]+?\|([\s\S]+)$'
                    },
                    {
                        'n': '公司简介',
                        'En': 'ComProfile',
                        'v':
                        'string(//div[contains(@class,"con_msg")]/div[@class="in"])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '公司电话',
                        'En': 'ComConcat',
                        'v':
                        '//text()[re:test(string(.),"(?:电\s*?话)\s*?[:：]\s*?[0-9 -]{7,}")]',
                        't': 'xpath_re',
                        're': "(?:电\s*?话)\s*?[:：]\s*?([0-9 -]{7,})"
                    },
                    {
                        'n': '邮政编码',
                        'En': 'ZipCode',
                        'v':
                        'string(//span[text()="公司地址："]/following-sibling::node()[1])',
                        't': 'xpath_re',
                        're': '邮编\s*?[:：]\s*?(\d+)'
                    },
                    {
                        'n': '公司网址',
                        'En': 'WebSite',
                        'v':
                        '//div[@class="tCompany_full"]//text()[re:test(string(.),"(?:https?:\/\/)[a-zA-Z0-9]+(?:\.[a-zA-Z0-9_-]+)+")]',
                        't': 'xpath_re',
                        're': '((?:https?:\/\/)[a-zA-Z0-9]+(?:\.[a-zA-Z0-9_-]+)+)'
                    },
                    {
                        'n': '公司地址',
                        'En': 'Address',
                        'v':
                        'string(//span[text()="公司地址："]/following-sibling::node()[1])',
                        't': 'xpath_re',
                        're': '(.+)(?:\(邮编){1,}?'
                    },
                    {
                        'n': 'Email',
                        'En': 'Email',
                        'v':
                        '//div[@class="tCompany_full"]//text()[re:test(string(.),"[A-Za-z0-9]+@[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+") and string(.)!="club@51job.com" and string(.)!="hr@51job.com"]',
                        't': 'xpath_re',
                        're': "([A-Za-z0-9]+@[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+)"
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
            # print(item)

    def job_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'xpath',
                    'db': 'Job51.Job',
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
                        '//input[@id="hidJobID"]/@value',
                        't': 'xpath_first',
                    },{
                        'n': '标题',
                        'En': 'Title',
                        'v':
                        '//h1/@title',
                        't': 'xpath_first'
                    },{
                        'n': '地区',
                        'En': 'City_Area',
                        'v':
                        '//h1/following-sibling::*[@class="lname"]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '月薪',
                        'En': 'Money',
                        'v':
                        '//h1/following-sibling::strong[1]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': 'MoneyLevel',
                        'En': 'MoneyLevel',
                        'v':
                        'money',
                        't': 'meta'
                    },
                    {
                        'n': '公司名称',
                        'En': 'CompanyName',
                        'v':
                        '//p[@class="cname"]/a/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '公司ID',
                        'En': 'ComID',
                        'v':
                        '//p[@class="cname"]/a/@href',
                        't': 'xpath_re',
                        're': '\/co(.+?)\.html'
                    },
                    {
                        'n': '工作经验要求',
                        'En': 'WorkExperience',
                        'v':
                        '//span[@class="sp4"][em[@class="i1"]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '学历要求',
                        'En': 'Eduction',
                        'v':
                        '//span[@class="sp4"][em[@class="i2"]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '招聘人数',
                        'En': 'RecruitNums',
                        'v':
                        '//span[@class="sp4"][em[@class="i3"]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '发布日期',
                        'En': 'PushDate',
                        'v':
                        '//span[@class="sp4"][em[@class="i4"]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '外语要求',
                        'En': 'English',
                        'v':
                        '//span[em[@class="i5"]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '专业要求',
                        'En': 'Professional',
                        'v':
                        '//span[em[@class="i6"]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '福利待遇',
                        'En': 'FringeBenefits',
                        'v':
                        '//p[@class="t2"]/span/text()',
                        't': 'xpath_join,'
                    },
                    {
                        'n': '职位要求',
                        'En': 'JobDescription',
                        'v':
                        'string(//div[@class="bmsg job_msg inbox"])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '职能类别',
                        'En': 'FunctionalCategories',
                        'v':
                        '//span[text()="职能类别："]/following-sibling::span[1]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '上班地址',
                        'En': 'WorkAddress',
                        'v':
                        'string(//span[text()="上班地址："]/following-sibling::node()[1])',
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