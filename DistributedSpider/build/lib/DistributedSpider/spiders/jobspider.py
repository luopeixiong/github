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
import pymssql

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


from SpiderHelp import SpiderHelp
from RedisHelp import _Request, _RedisSpider, logger


conn_flag = False
REDISFLAG = True
TODAY = time.strftime('%Y-%m-%d')
Headers = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
           'Upgrade-Insecure-Requests':'1',
           'Accept': 'text/html, application/xhtml+xml, */*; q=0.01',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           'Cache-Control': 'max-age=0',
           'Host': 'www.lagou.com',
           'Cookie': 'JSESSIONID=ABAAABAABEEAAJAE66398E0C70D0A240C71734513B0A4FC; user_trace_token=20180228151555-39367b68-c15d-4d39-be8c-3418f70bab2d; PRE_UTM=; PRE_HOST=; PRE_SITE=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_%25E5%25A5%25BD%25E7%25A7%259F%3Fpx%3Ddefault%26city%3D%25E5%2585%25A8%25E5%259B%25BD; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fgongsi%2F126021.html; LGUID=20180228151615-43ca7310-1c57-11e8-96e8-525400f775ce; SEARCH_ID=1246ee42374d463eb81fc33836f1626d; _gid=GA1.2.408872113.1519802170; _gat=1; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1519802170; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1519803456; _ga=GA1.2.666080348.1519802170; LGSID=20180228151615-43ca7139-1c57-11e8-96e8-525400f775ce; LGRID=20180228153741-420ede3e-1c5a-11e8-b106-5254005c3644',
           'Connection': 'keep-alive'}

MAX = 2**15


def get_manager():
    
    conn = pymssql.connect('10.1.18.35', user="sa",
                           password="8927968", database="Haifeng.CrawlerData")
    cursor = conn.cursor()
    sql = "select fundManagerName from AMAC.Amac_privateFundManager"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return (i[0] for i in result)


res = requests.get(
    'http://js.51jobcdn.com/in/js/2016/layer/area_array_c.js?20171103')
RESULT = json.loads(re.compile(
    'area=(\{.*?\})', re.S).search(res.text).group(1))

Cookies = {"user_trace_token": "20180227171023-13c4ff22-32a7-4279-95fa-1569da2fd0dc",
            "LGUID": "20180227171023-0aeeef7b-1b9e-11e8-93dd-525400f775ce",
            "TG-TRACK-CODE": "search_code",
            "JSESSIONID": "ABAAABAAAIAACBI095C5CFEC9B75F6AEC7BFA4F6E934BA4",
            "X_HTTP_TOKEN": "dca46ba3b037acb292a4fe2d69459213",
            "SEARCH_ID": "b74be4ad873349cda617c9ca2d69a20f",
            "_gid": "GA1.2.1815094150.1519722620",
            "_gat": "1",
            "Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6": "1519722620",
            "Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6": "1519785973",
            "_ga": "GA1.2.854555534.1519722620",
            "LGSID": "20180228095833-e1e978c3-1c2a-11e8-b0fe-5254005c3644",
            "LGRID": "20180228104617-8cf88a57-1c31-11e8-95e6-525400f775ce",}

Headers2 = {'Host': 'www.lagou.com',
'Connection': 'keep-alive',
'Cache-Control': 'max-age=0',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Referer': 'https://www.lagou.com/jobs/list_java?px=new&city=%E5%8C%97%E4%BA%AC',
'Cookie': 'JSESSIONID=ABAAABAABEEAAJAE66398E0C70D0A240C71734513B0A4FC; user_trace_token=20180228151555-39367b68-c15d-4d39-be8c-3418f70bab2d; PRE_UTM=; PRE_HOST=; PRE_SITE=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_%25E5%25A5%25BD%25E7%25A7%259F%3Fpx%3Ddefault%26city%3D%25E5%2585%25A8%25E5%259B%25BD; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fgongsi%2F126021.html; LGUID=20180228151615-43ca7310-1c57-11e8-96e8-525400f775ce; SEARCH_ID=1246ee42374d463eb81fc33836f1626d; _gid=GA1.2.408872113.1519802170; _gat=1; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1519802170; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1519803456; _ga=GA1.2.666080348.1519802170; LGSID=20180228151615-43ca7139-1c57-11e8-96e8-525400f775ce; LGRID=20180228153741-420ede3e-1c5a-11e8-b106-5254005c3644',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-CN,zh;q=0.8'
}

Headers3 = {'Host': 'www.lagou.com',
'Connection': 'keep-alive',
'Cache-Control': 'max-age=0',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Referer': 'https://www.lagou.com/gongsi/j222021.html',
'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
'Cookie': 'JSESSIONID=ABAAABAABEEAAJAE66398E0C70D0A240C71734513B0A4FC; user_trace_token=20180228151555-39367b68-c15d-4d39-be8c-3418f70bab2d; PRE_UTM=; PRE_HOST=; PRE_SITE=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_%25E5%25A5%25BD%25E7%25A7%259F%3Fpx%3Ddefault%26city%3D%25E5%2585%25A8%25E5%259B%25BD; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fgongsi%2F126021.html; LGUID=20180228151615-43ca7310-1c57-11e8-96e8-525400f775ce; SEARCH_ID=1246ee42374d463eb81fc33836f1626d; _gid=GA1.2.408872113.1519802170; _gat=1; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1519802170; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1519803456; _ga=GA1.2.666080348.1519802170; LGSID=20180228151615-43ca7139-1c57-11e8-96e8-525400f775ce; LGRID=20180228153741-420ede3e-1c5a-11e8-b106-5254005c3644',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-CN,zh;q=0.8'
}
# Cookies2 = {'Cookie': 'JSESSIONID=ABAAABAABEEAAJAE66398E0C70D0A240C71734513B0A4FC; user_trace_token=20180228151555-39367b68-c15d-4d39-be8c-3418f70bab2d; LGUID=20180228151615-43ca7310-1c57-11e8-96e8-525400f775ce; SEARCH_ID=1246ee42374d463eb81fc33836f1626d; _gid=GA1.2.408872113.1519802170; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1519802170; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1519806409; _ga=GA1.2.666080348.1519802170; LGSID=20180228151615-43ca7139-1c57-11e8-96e8-525400f775ce; LGRID=20180228162654-223e4252-1c61-11e8-b106-5254005c3644'}

Cookies2 = {'JSESSIONID':'ABAAABAABEEAAJAE66398E0C70D0A240C71734513B0A4FC',
            'user_trace_token':'20180228151555-39367b68-c15d-4d39-be8c-3418f70bab2d',
            'LGUID':'20180228151615-43ca7310-1c57-11e8-96e8-525400f775ce',
            'X_HTTP_TOKEN':'83cc1a88ad261dba2cf6ed161fdc22e3',
            '_putrc':'3E8B7C9608CF6DEF',
            'login':'true',
            'unick':'%E7%BD%97%E5%9F%B9%E9%9B%84',
            'showExpriedIndex':'1',
            'showExpriedCompanyHome':'1',
            'showExpriedMyPublish':'1',
            'hasDeliver':'61',
            'gate_login_token':'fad94f1e4944b8024e303fc9f8260e4b5c91769ab9b32165',
            '_gat':'1',
            'SEARCH_ID':'3004c962e6554ddd995d1b3aa931c0e7',
            'index_location_city':'%E5%8C%97%E4%BA%AC',
            '_gid':'GA1.2.408872113.1519802170',
            'Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6':'1519802170',
            'Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6':'1519809835',
            '_ga':'GA1.2.666080348.1519802170',
            'LGSID':'20180228151615-43ca7139-1c57-11e8-96e8-525400f775ce',
            'LGRID':'20180228172400-1c463d4b-1c69-11e8-9709-525400f775ce'}

class SinaspiderSpider(_RedisSpider, SpiderHelp):  # ,scrapy.Spider
    name = 'job_spider'
    start_urls = list(get_manager())
    state = {}
    redis_flag = True
    redis_key = '%s:starturls' % name
    signel = 1
    host = '10.1.18.35'
    website_possible_httpstatus_list = [302, 404, 502, 500, 504, 407]
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
        # 下载延迟
        'DOWNLOAD_DELAY': 1,
        # 爬虫策略
        'DEPTH_PRIORITY': 1,
        # 允许的status
        'HTTPERROR_ALLOWED_CODES': [404, 502, 500, 504],
    }

    def __init__(self, _job=None, **kwargs):
        # 获取本爬虫redis_key
        super(SinaspiderSpider, self).__init__(**kwargs)

    @property
    def ctime(self):
        return '%.13s' % (time.time()*1000)

    def __str__(self):
        return 'SinaspiderSpider'

    def _start_requests(self):
        regex = re.compile('[(（].*?[)）]').sub
        req = []
        logger.info('Start Crawl Spider %s at rediskey %s' %
                    (self.name, self.redis_key))
        _cityjson = ['北京', '上海', '广东', '湖北', '陕西', '四川', '辽宁',
                    '吉林', '江苏', '山东', '浙江', '广西', '安徽', '河北',
                    '山西', '内蒙', '黑龙江', '福建', '江西', '河南', '湖南',
                    '海南', '贵州', '云南', '西藏', '甘肃', '青海', '宁夏',
                    '新疆', '香港', '澳门', '台湾省', '天津', '重庆']
        for manager in self.start_urls:
            _manager = manager  #regex('',manager)
            # 51Job
            job51 = 'http://search.51job.com/list/000000,000000,0000,00,9,99,%s,1,{}.html' % urllib.parse.quote(urllib.parse.quote(_manager))
            job51_url = job51.format(1)
            yield self.request(job51_url,
                headers=self.default_header,
                redis_flag=True,
                meta={'formater': job51, 'manager': manager},
                callback=self.job51_in)

            # 智联招聘
            # 需要锁定地区搜索
            cityjson = _cityjson.copy()
            while cityjson:
                # 分地区搜索
                areas = '+'.join(cityjson[:5])
                cityjson = cityjson[5:]
                zhilian = 'http://sou.zhaopin.com/jobs/searchresult.ashx?jl=%s&kw=%s&p={}' % (
                    urllib.parse.quote(areas), urllib.parse.quote(_manager))
                zhilian_url = zhilian.format(1)
                yield self.request(zhilian_url,
                                   headers=self.default_header,
                                   redis_flag=True,
                                   meta={'formater': zhilian, 'manager': manager},
                                   callback=self.zhilian_in)


            # 猎聘   公司页面--> 招聘列表
            liepin = 'https://www.liepin.com/company/so/?keywords=%s' % urllib.parse.quote(
                manager)
            yield self.request(liepin,
                               headers=self.default_header,
                               meta={'manager': manager},
                               redis_flag=True,
                               callback=self.liepin_in)

            # # BOSS直聘   - 公司主页  天眼查接口确认信息  
            # # 会封禁ip
            # zhipin = 'https://www.zhipin.com/job_detail/?scity=100010000&query=%s' % urllib.parse.quote(_manager)
            # fmt = zhipin+'&page={}'
            # '''搜索为模糊匹配'''  #进入主页  对比公司名称  不符合pass
            # yield self.request(zhipin,
            #     headers=self.default_header,
            #     meta={'manager': manager, 'fmt': fmt},
            #     redis_flag=True,
            #     callback=self.zhipin_in)

            # 中国金融人才网
            jinrong = 'http://www.51jrjob.com/jobseeker/stage/findjob.html?kv=%s' % urllib.parse.quote(_manager)
            yield self.request(jinrong,
                headers=self.default_header,
                redis_flag=True,
                meta={'manager': manager},
                callback=self.jinrong_in)

        # # 拉钩  搜索结果为模糊匹配--较为精准 需要迭代cookie cookie会失效  
        # search_keys = self.start_urls
        
        # yield self.request('https://www.lagou.com',
        #     headers=self.default_header,
        #     cookies=Cookies,
        #     meta={'search_keys': search_keys, 'cookiejar': 1},
        #     redis_flag=True,
        #     callback=self.lagou_jump
        #     )
    
    def lagou_jump(self, response):
        search_keys = response.meta['search_keys']
        search_key = search_keys.copy()
        yield self.request('https://www.lagou.com/jobs/companyAjax.json?px=default&needAddtionalResult=false&isSchoolJob=0',
            method='POST',
            headers=self.default_header,
            body=urllib.parse.urlencode({'first':'true',
                                        'pn':'1',
                                        'kd':search_key}),
            
            meta={'search_keys': search_keys, 'cookiejar': response.meta['cookiejar'], 'manager': search_key},
            callback=self.lagou_in)


    def lagou_in(self, response):
        search_keys = response.meta['search_keys']
        if search_keys:
            search_key = search_keys.pop()
            print(len(search_keys),search_key)
        else:
            return
        yield self.request('https://www.lagou.com/jobs/companyAjax.json?px=default&needAddtionalResult=false&isSchoolJob=0',
            headers=self.default_header,
            method='POST',
            dont_filter=True,
            body=urllib.parse.urlencode({'first':'true',
                                        'pn':'1',
                                        'kd':search_key}),
            meta={'manager': search_key,'cookiejar': response.meta['cookiejar'], 'search_keys': search_keys,'dont_redirect': False},
            callback=self.lagou_in)
        data = json.loads(response.text)
        data = data['content']['result']
        headers = Headers.copy()
        for url in data:
            # 这里的cookie为手动输入 需要修改为自动
            if url['companyFullName']  in response.meta['manager'] or response.meta['manager'] in url['companyFullName']:
                print('Got com: %s --> %s' % (url['companyFullName'],response.meta['manager']))
                yield self.request('https://www.lagou.com/gongsi/%s.html' % url['companyId'],
                    headers=Headers2,
                    cookies=Cookies2,
                    meta={'manager': response.meta['manager']},
                    callback=self.lagou_com)
                headers = Headers3
                headers['Referer'] = 'https://www.lagou.com/gongsi/j%s.html' % url['companyId']
                yield self.request('https://www.lagou.com/gongsi/searchPosition.json',
                    method='POST',
                    priority=1000,
                    body=urllib.parse.urlencode({'companyId': url['companyId'],
                                                'positionFirstType':'全部',
                                                'schoolJob':'false',
                                                'pageNo':'1',
                                                'pageSize':'10'}),
                    headers=headers,
                    cookies=Cookies2,
                    meta={'manager': response.meta['manager'],'companyId':url['companyId']},
                    callback=self.lagou_job_in)
            else:
                print('pass com: %s --!> %s' % (url['companyFullName'],response.meta['manager']))

     
    def lagou_data(self,com_id):

        def data(page=1, response=None):
            return urllib.parse.urlencode({
                'companyId': com_id,
                'positionFirstType': '全部',
                'schoolJob': 'false',
                'pageNo': str(page),
                'pageSize':'10'
                })
        return data           

    def lagou_com(self, response):
        response = response.replace(body = response.xpath('//*[@id="companyInfoData"]/text()').extract_first())
        _configs = [{
                'list': {
                        'n': '',
                        'v': '',
                        't': 'json',
                        'db': 'JobSpider.Lagou_Com',
                        'keys': ['HTML_ID'],
                        'check': 'ComName',
                        'conn': conn_flag
                        },
                'response_type':
                    'json',
                    'data': [
                        {
                            'n': 'HTML_ID',
                            'En': 'HTML_ID',
                            'v': 'companyId',
                            't': 'json',
                        }, {
                            'n': '公司名称',
                            'En': 'ComName',
                            'v': 'coreInfo/companyName',
                            't': 'json',
                        }, 
                        {
                            'n': '公司规模',
                            'En': 'Scale',
                            'v': 'baseInfo/companySize',
                            't': 'json',
                        },
                        {
                            'n': '公司行业',
                            'En': 'Category',
                            'v': 'baseInfo/industryField',
                            't': 'json',
                        },
                        {
                            'n': '公司简介',
                            'En': 'ComProfile',
                            'v':
                            'introduction/companyProfile',
                            't': 'json',
                        },
                        {
                            'n': '公司地址',
                            'En': 'Address',
                            'v':
                            'addressList/detailAddress',
                            't': 'json_join|',
                        },{
                            'n': 'Logo',
                            'En': 'LogoImages',
                            'v':
                            'coreInfo/logo',
                            't': 'json',
                        },{
                            'n': '所在城市',
                            'En': 'City_Area',
                            'v':
                            'baseInfo/city',
                            't': 'meta'
                        },{
                            'n': 'turns',
                            'En': 'Turns',
                            'v':
                            'baseInfo/financeStage',
                            't': 'json'
                        },{
                            'n': 'companyUrl',
                            'En': 'WebSite',
                            'v':
                            'coreInfo/companyUrl',
                            't': 'json'
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

    def lagou_job_in(self, response):
        # 翻页
        # print(response.text)
        JS = json.loads(response.text)
        if JS['content']['data']['page']['totalCount'] != '0':
            reqs = self.scrapy_page_help(
                response,
                method='POST',
                config={'t': 'json',
                        'v': 'content/data/page/totalCount',
                        },
                callback=self.lagou_job_in,
                urlfunc=lambda page, response=None: response.url,
                bodyfunc=lambda page, response=None: urllib.parse.urlencode({'companyId':response.meta['companyId'],
                                                    'positionFirstType':'全部',
                                                    'schoolJob':'false',
                                                    'pageNo':str(page),
                                                    'pageSize':'10'}),
                redis_conn=self.r,
                redis_flag=True,
                headers=Headers3,
                cookies=Cookies2,
                divmod=10,
                readpage=32,
                response_type='json')
            for req in reqs:
                yield req
        urls  = JS['content']['data']['page']['result']
        if not urls:
            return
        for url in urls:
            url['manager'] = response.meta['manager']
            job_url = 'https://www.lagou.com/jobs/%s.html' % url['positionId']
            headers = Headers3.copy()
            headers['Referer'] = job_url
            yield self.request(job_url,
                priority=1000,
                headers=headers,
                cookies=Cookies2,
                meta=url,
                callback=self.lagou_job)
        

    def lagou_job(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'JobSpider.Lagou_Job',
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
                        'v': 'jobs\/([^\/]+)\.htm',
                        't': 'url_re',
                    }, {
                        'n': '标题',
                        'En': 'Title',
                        'v':
                        '//div[@class="job-name"]/@title',
                        't': 'xpath_first'
                    }, {
                        'n': '工作地点',
                        'En': 'WorkAddress',
                        'v':
                        '//h3[@class="address"]/following-sibling::div[1]//text()[contains(string(.),"-") or parent::a and string(.)!="查看地图"]',
                        't': 'xpath_join'
                    },
                    {
                        'n': '发布日期',
                        'En': 'PushDate',
                        'v':
                        '//*[@class="publish_time"]/text()',
                        't': 'xpath_re',
                        're': '(\d{4}-\d{2}-\d{2})'
                    },
                    {
                        'n': '职位月薪',
                        'En': 'Money',
                        'v':
                        '//*[@class="job_request"]//span[1]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '公司名称',
                        'En': 'CompanyName',
                        'v':
                        'companyFullName',
                        't': 'meta'
                    },
                    {
                        'n': '工作经验',
                        'En': 'WorkExperience',
                        'v':
                        '//*[@class="job_request"]//span[3]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '最低学历',
                        'En': 'Eduction',
                        'v':
                        '//*[@class="job_request"]//span[4]/text()',
                        't': 'xpath_first'
                    },
                    # {
                    #     'n': '要求行业',
                    #     'En': 'industry',
                    #     'v':
                    #     '//li[span[text()="要求行业："]]/text()',
                    #     't': 'xpath_first'
                    # },
                    # {
                    #     'n': '年龄要求',
                    #     'En': 'Age',
                    #     'v':
                    #     '//li[span[text()="年龄要求："]]/text()',
                    #     't': 'xpath_first'
                    # },
                    {
                        'n': '职位描述',
                        'En': 'JobDescription',
                        'v':
                        'string(//h3[@class="description"]/following-sibling::div[1])',
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
            print(item)

    def zhipin_in(self, response):
        # 翻页
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'abs',
                    'v': '10'
                    },
            callback=self.zhipin_in,
            headers=self.default_header,
            urlfunc=lambda page, response=None: response.meta['fmt'].format(
                page),
            redis_conn=self.r,
            redis_flag=True,
            divmod=1,
            readpage=32,
            response_type='xpath')
        for req in reqs:
            yield req
        urls = (response.urljoin(url) for url in set(response.xpath('//div[@class="company-text"]//@href').extract()))
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                meta={'manager': response.meta['manager']},
                callback=self.zhipin_com_in,
                dont_filter=True)


    def zhipin_com_in(self, response):
        manager = response.meta['manager']
        if manager in response.text or \
            response.xpath('//h3[text()="工商信息"]/following-sibling::h4[1]/text()').extract_first('None') in manager: 
            # 招聘列表
            # url = response.urljoin(response.xpath('//*[starts-with(text(),"招聘职位")]/@href').extract_first())
            # yield self.request(url,
            #     headers=self.default_header,
            #     callback=self.zhipin_job_in)
            _configs = [{
            'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'JobSpider.Jinrong_Com',
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
                        'v': 'gongsi\/([^\/]+?)\.htm',
                        't': 'url_re',
                    },{
                        'n': '公司名称',
                        'En': 'ComName',
                        'v': '//h3[text()="工商信息"]/following-sibling::h4[1]/text()',
                        't': 'xpath_first',
                    }, 
                    {
                        'n': '公司规模',
                        'En': 'Scale',
                        'v': '//div[@class="info-primary"]/p[em]/text()[2]',
                        't': 'xpath_first',
                    },
                    {
                        'n': '公司行业',
                        'En': 'Capital',  # Category
                        'v': '//div[@class="info-primary"]/p[em]/text()[3]',
                        't': 'xpath_first',
                    },{
                        'n': '轮次',
                        'En': 'Turns',
                        'v': '//div[@class="info-primary"]/p[em]/text()[1]',
                        't': 'xpath_first',
                    },{
                        'n': '公司网址',
                        'En': 'WebSite',
                        'v': '//*[@class="job-sec company-products"]//@href',
                        't': 'xpath_first'
                    },
                    {
                        'n': '公司简介',
                        'En': 'ComProfile',
                        'v':
                        'string(//*[@class="text fold-text"])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '公司地址',
                        'En': 'Address',
                        'v':
                        '//div[@class="location-address"]//text()',
                        't': 'xpath_join|'
                    },{
                        'n': 'Logo',
                        'En': 'LogoImages',
                        'v':
                        '//*[@class="slider-main"]//li[@class="cur"]//@src',
                        't': 'xpath_first',
                    },{
                        'n': '法人代表',
                        'En': 'LegalMan',
                        'v':
                        '//li[span[text()="法人代表"]]/text()',
                        't': 'xpath_first',
                    },{
                        'n': '注册资本',
                        'En': 'RegisteredCapital',
                        'v':
                        '//li[span[text()="注册资本"]]/text()',
                        't': 'xpath_first',
                    },{
                        'n': '成立时间',
                        'En': 'SetupTime',
                        'v':
                        '//li[span[text()="成立时间"]]/text()',
                        't': 'xpath_first',
                    },{
                        'n': '企业类型',
                        'En': 'CompanyType',
                        'v':
                        '//li[span[text()="企业类型"]]/text()',
                        't': 'xpath_first',
                    },{
                        'n': '经营状态',
                        'En': 'OperatingState',
                        'v':
                        '//li[span[text()="经营状态"]]/text()',
                        't': 'xpath_first',
                    },{
                        'n': '注册地址',
                        'En': 'RegisteredAddress',
                        'v':
                        '//li[span[text()="注册地址"]]/text()',
                        't': 'xpath_first',
                    },{
                        'n': '统一信用代码',
                        'En': 'UnifiedCreditCode',
                        'v':
                        '//li[span[text()="统一信用代码"]]/text()',
                        't': 'xpath_first',
                    },{
                        'n': '经营范围',
                        'En': 'ScopeOfOperation',
                        'v': '//li[span[text()="经营范围"]]/text()',
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
        else:
            print('pass %s <> %s' % (manager, response.xpath('//h3[text()="工商信息"]/following-sibling::h4[1]/text()').extract_first('None')))

    def zhipin_job_in(self, response):
        pass


    def jinrong_in(self, response):

        # 翻页
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re',
                    'v': '//a[text()="尾页"]/@href',
                    're': 'page=(\d+)'
                    },
            callback=self.liepin_com,
            headers=self.default_header,
            urlfunc=lambda page, response=None: response.meta['formater'].format(
                page),
            redis_conn=self.r,
            redis_flag=True,
            divmod=1,
            readpage=32,
            response_type='xpath')
        for req in reqs:
            yield req

        manager = response.meta['manager']

        # 岗位
        urls = response.xpath('//div[@class="job"]//a[@class="pos-detail2"]//@href').extract()
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                meta={'manager':manager},
                callback=self.jinrong_job)

        com_url = response.xpath('//div[@class="subp2"]//a/@href').extract_first()
        if com_url:
            yield self.request(com_url,
                headers=self.default_header,
                meta={'manager':manager},
                callback=self.jinrong_com)

    def jinrong_job(self, response):
        _configs = [{
            'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'JobSpider.Jinrong_Job',
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
                        'v': 'Position\/([^\/]+)\.htm',
                        't': 'url_re',
                    }, {
                        'n': '标题',
                        'En': 'Title',
                        'v':
                        '//*[@class="titleInfo"]/h1/text()',
                        't': 'xpath_first'
                    }, {
                        'n': '工作地点',
                        'En': 'WorkPlace',
                        'v':
                        '//li[span[text()="工作地点："]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '招聘人数',
                        'En': 'RecruitNums',
                        'v':
                        '//li[span[text()="招聘人数："]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '职位月薪',
                        'En': 'Money',
                        'v':
                        '//span[@id="xinshui"]/i/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '公司名称',
                        'En': 'CompanyName',
                        'v':
                        '//*[@class="titleInfo"]//h3/a/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '工作经验',
                        'En': 'WorkExperience',
                        'v':
                        '//li[span[text()="工作经验："]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '最低学历',
                        'En': 'Eduction',
                        'v':
                        '//li[span[text()="要求学历："]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '要求行业',
                        'En': 'industry',
                        'v':
                        '//li[span[text()="要求行业："]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '年龄要求',
                        'En': 'Age',
                        'v':
                        '//li[span[text()="年龄要求："]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '职位描述',
                        'En': 'JobDescription',
                        'v':
                        'string(//div[@class="zwm"])',
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

    def jinrong_com(self, response):
        _configs = [{
            'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'JobSpider.Jinrong_Com',
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
                        'v': 'Company\/([^\/]+)\.htm',
                        't': 'url_re',
                    },{
                        'n': '公司名称',
                        'En': 'ComName',
                        'v': 'string(//*[@class="cnameBox"])',
                        't': 'xpath_re',
                        're': '(.*?)百度一下'
                    }, 
                    {
                        'n': '公司规模',
                        'En': 'Scale',
                        'v': '//div[@class="cnameBoxDetail" and contains(text(), "公司规模：")]/text()',
                        't': 'xpath_re',
                        're': '公司规模：(.+)'
                    },{
                        'n': '公司网址',
                        'En': 'WebSite',
                        'v': '//*[text()="网址："]/following-sibling::*[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '福利待遇',
                        'En': 'FringeBenefits',
                        'v': '//*[@class="ctagBox"]/span/text()',
                        't': 'xpath_join,'
                    },
                    {
                        'n': '公司简介',
                        'En': 'ComProfile',
                        'v':
                        'string(//*[@class="cyjj"])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '公司地址',
                        'En': 'Address',
                        'v':
                        '//*[@class="cnameBoxDetail" and contains(text(), "公司地址：")]/text()',
                        't': 'xpath_re',
                        're': '公司地址：\s*?(.+?)\s'
                    },{
                        'n': 'Logo',
                        'En': 'LogoImages',
                        'v':
                        '//*[@class="clogoBox"]//@src',
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
            yield item
            # print(item)

    def liepin_in(self, response):
        # 取第一个
        url = response.urljoin(response.xpath('//dl[@data-id]/dt//@href').extract_first())
        if not url:
            return
        fmt = url + '/pn%s/'
        yield self.request(url,
            headers=self.default_header,
            meta={'page':1,'formater':fmt,'manager': response.meta['manager']},
            callback=self.liepin_com)
    
    def liepin_com(self, response):

        # 翻页
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共\s*?6(\d+)\s*?个'
                    },
            callback=self.liepin_com,
            headers=self.default_header,
            urlfunc=lambda page, response=None: response.meta['formater'].format(
                page),
            redis_conn=self.r,
            redis_flag=True,
            divmod=15,
            readpage=32,
            response_type='xpath')
        for req in reqs:
            yield req

        urls = response.xpath('//*[@class="job-info"]/a/@href').re('https?:\/\/www\.liepin\.com\/job\/.*?\.shtml')
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                meta={'manager': response.meta['manager']},
                callback=self.liepin_job)

        if response.meta['page'] == 1:
            _configs = [{
                'list': {
                        'n': '',
                        'v': '',
                        't': 'xpath',
                        'db': 'JobSpider.LiePin_Com',
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
                            'v': '//h1/text()',
                            't': 'xpath_first'
                        }, 
                        {
                            'n': '公司规模',
                            'En': 'Scale',
                            'v': '//li[span[text()="公司规模："]]/text()',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司行业',
                            'En': 'Category',
                            'v':
                            '//li[span[text()="行业："]]/@title|//li[span[text()="行业："]]/a/text()',
                            't': 'xpath_first'
                        },
                        {
                            'n': '公司简介',
                            'En': 'ComProfile',
                            'v':
                            '//*[@class="profile"]/text()',
                            't': 'xpath_join'
                        },
                        {
                            'n': '公司地址',
                            'En': 'Address',
                            'v':
                            '//li[span[text()="公司地址："]]/text()',
                            't': 'xpath_first'
                        },{
                            'n': 'Logo',
                            'En': 'LogoImages',
                            'v':
                            '//*[@class="bigELogo"]/@src',
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
                yield item
                # print(item)

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
                        'En': 'WorkPlace',
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

    def zhilian_in(self, response):
        # 翻页
        
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_first',
                    'v': '//span[@class="search_yx_tj"]/em/text()[string(.)!="0"]'
                    },
            callback=self.zhilian_in,
            headers=self.default_header,
            urlfunc=lambda page, response=None: response.meta['formater'].format(
                page),
            redis_conn=self.r,
            redis_flag=True,
            divmod=60,
            readpage=32,
            response_type='xpath')
        for req in reqs:
            yield req
        # jobs
        urls = ('http://jobs.zhaopin.com/%s.htm' %
                url for url in response.xpath('//td[@class="zwmc"]//@href').re('com\/(.*?)\.htm'))
        for url in urls:
            yield self.request(url,
                               headers=self.default_header,
                               meta={'manager': response.meta['manager']},
                               callback=self.zhilian_job_info)
        # coms
        urls = (response.urljoin(url) for url in response.xpath('//td[@class="gsmc"]/a[1]/@href').extract())
        for url in urls:
            yield self.request(url,
                               headers=self.default_header,
                               meta={'manager': response.meta['manager']},
                               callback=self.zhilian_com_info)

    def zhilian_job_info(self, response):
        _configs = [{
            'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'JobSpider.Zhilian_Job',
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
                        '\/([^\/]+?)\.htm',
                        't': 'url_re',
                    }, {
                        'n': '标题',
                        'En': 'Title',
                        'v':
                        'string(//div[@class="inner-left fl"]/h1)',
                        't': 'xpath_first'
                    }, {
                        'n': '工作地点',
                        'En': 'WorkPlace',
                        'v':
                        'string(//*[text()="工作地点："]/following-sibling::*[1])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '职位月薪',
                        'En': 'Money',
                        'v':
                        'string(//*[text()="职位月薪："]/following-sibling::*[1])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '公司名称',
                        'En': 'CompanyName',
                        'v':
                        'string(//div[@class="inner-left fl"]/h2/a)',
                        't': 'xpath_first'
                    },
                    {
                        'n': '工作经验',
                        'En': 'WorkExperience',
                        'v':
                        'string(//*[text()="工作经验："]/following-sibling::*[1])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '最低学历',
                        'En': 'Eduction',
                        'v':
                        'string(//*[text()="最低学历："]/following-sibling::*[1])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '招聘人数',
                        'En': 'RecruitNums',
                        'v':
                        'string(//*[text()="招聘人数："]/following-sibling::*[1])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '职位类别',
                        'En': 'FunctionalCategories',
                        'v':
                        'string(//*[text()="职位类别："]/following-sibling::*[1])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '发布日期',
                        'En': 'PushDate',
                        'v':
                        'string(//*[text()="发布日期："]/following-sibling::*[1])',
                        't': 'xpath_first'
                    },
                    {
                        'n': '福利待遇',
                        'En': 'FringeBenefits',
                        'v':
                        '//div[@class="welfare-tab-box"]/span/text()',
                        't': 'xpath_join,'
                    },
                    {
                        'n': '职位描述',
                        'En': 'JobDescription',
                        'v':
                        '//div[@class="tab-cont-box"]/div[1]/p[text()]/text()',
                        't': 'xpath_join'
                    },
                    {
                        'n': '工作地址',
                        'En': 'WorkAddress',
                        'v':
                        '//*[text()="工作地址："]/following-sibling::*[1]/text()',
                        't': 'xpath_join'
                    },{
                        'n': '工作性质',
                        'En': 'WorkType',
                        'v':
                        'string(//span[text()="工作性质："]/following-sibling::node()[1])',
                        't': 'xpath_first'
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

    def zhilian_com_info(self, response):
        # 解析 主要解析2种页面  一个为手机端的  一个为普通端的   特殊页面正则  分3块写
        # 暂时不做special页面
        # 加载跳转页面
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
                            'En': 'Category',
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
                yield item
                # print(item)

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
                yield item
                # print(item)

    def job51_in(self, response):
        # 翻页
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共(\d+)页'
                    },
            callback=self.job51_in,
            headers=self.default_header,
            urlfunc=lambda page, response=None: response.meta['formater'].format(
                page),
            redis_conn=self.r,
            redis_flag=True,
            readpage=32,
            response_type='xpath')
        for req in reqs:
            yield req
        # jobs
        urls = (response.urljoin(url) for url in response.xpath(
            '//div[@class="dw_table"]/div[@class="el"]/p[1]//@href').extract())
        for url in urls:
            yield self.request(url,
                               headers=self.default_header,
                               meta={'manager': response.meta['manager']},
                               callback=self.job51_job_info)
        # coms
        urls = (response.urljoin(url) for url in response.xpath(
            '//div[@class="dw_table"]/div[@class="el"]/span[1]//@href').extract())
        for url in urls:
            yield self.request(url,
                               headers=self.default_header,
                               meta={'manager': response.meta['manager']},
                               callback=self.job51_com_info)

    def job51_com_info(self, response):
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
                        'En': 'Category',
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

    def job51_job_info(self, response):
        _configs = [{
            'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'JobSpider.Job51_Job',
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
                        '//input[@id="hidJobID"]/@value',
                        't': 'xpath_first',
                    }, {
                        'n': '标题',
                        'En': 'Title',
                        'v':
                        '//h1/@title',
                        't': 'xpath_first'
                    }, {
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
                        'n': '公司名称',
                        'En': 'ComName',
                        'v':
                        '//p[@class="cname"]/a/text()',
                        't': 'xpath_first'
                    },
                    # {
                    #     'n': '公司ID',
                    #     'En': 'ComID',
                    #     'v':
                    #     '//p[@class="cname"]/a/@href',
                    #     't': 'xpath_re',
                    #     're': '\/co(.+?)\.html'
                    # },
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
                    }, {
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


def main():
    SinaspiderSpider.put_redis()


if __name__ == '__main__':
    main()
