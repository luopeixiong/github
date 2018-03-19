# -*- coding: utf-8 -*-



import scrapy
from user_agent import generate_user_agent
import urllib.parse
#from myselector import Selector as S
import json
from scrapy.http.response.text import TextResponse
import re
import requests
from Help import other
from scrapy.http.response import Response
import logging

logger = logging.getLogger(__name__)

_PARTTERN = re.compile(':(\[.*?\])', re.S)
_ip = re.compile('\/\/(.*?):')
FAILED = 3
LIMIT = 10
aaa = 22222
MAX_TIMES = 3

# 删除不可用代理
def delete_proxy(response:Response):
    ip = _ip.search(response.meta['proxy']).group(1)
    requests.get("http://10.1.18.35:8000/delete?ip={}".format(ip), allow_redirects=False)
    requests.get("http://10.1.18.35:8000/delete?types=2", allow_redirects=False)


class _partern(object):
    def __init__(self):
        pass


def default_header() -> dict:
    return {
        'User_Agent':
        generate_user_agent(os=('win', )),
        'Referer':
        'http://xukezheng.cbrc.gov.cn/ilicence/licence/licenceQuery.jsp',
        'Content-Type':
        'application/x-www-form-urlencoded; charset=UTF-8'
    }


def cbrc_xuke_date(page: int = 1, limit: int = LIMIT) -> bytes:
    start = (page - 1) * LIMIT
    return urllib.parse.urlencode({'start': '%s' % start, 'limit': str(limit)})


class CbrcSpider(scrapy.Spider, other):
    name = "cbrc"
    allowed_domains = ["cbrc.gov.cn"]
    start_urls = [
        'http://xukezheng.cbrc.gov.cn/ilicence/getLicence.do?useState=3'
    ]
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'CBRC.middlewares.RotateUserAgentMiddleware': 401,
            'CBRC.middlewares.ProxyMiddleware': 700,
        },
        'CONCURRENT_REQUESTS': 32,
        'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOAD_DELAY': 0.1,
        'DEPTH_PRIORITY': 1,
        'HTTPERROR_ALLOWED_CODES': [404, 502, 504],
    }

    def request_try(self, response):
        try_times = response.meta.get('try_times', 0)
        if try_times < MAX_TIMES:
            meta = response.meta.copy()
            meta['try_times'] =  try_times + 1
            request = response.request.replace(dont_filter=True,meta=meta)
            return request

    def get_instance(self, args: tuple, cls):
        if args:
            for i in args:
                if isinstance(i, cls):
                    return i

    def _get_instance(self, kwargs: dict, cls):
        if kwargs:
            _list = list(kwargs.values())
            return self.get_instance(_list)

    def getfinstance(self, args, kwargs, cls):
        flag = self.get_instance(args, cls)
        return flag if flag else self._get_instance(kwargs, cls)

    def response_failed(self, response) -> bool:
        '''
        @output : Ture-->重新发送请求 False:为正确请求
        '''
        if response.status in [404, 502, 504]:
            if response.status in [404]:
                delete_proxy(response)
            return True
        elif 'setURL' in response.text:
            return True
        else:
            return False

    # 用于记录 页面访问时 代理返回的页面状态， 并排除错误页面
    def check_response(func: callable):
        def f(self, *args, **kwargs):
            if not callable(func):
                raise TypeError('<class %s is not a callback func>' %
                                (func.__class__))
            response = self.getfinstance(args, kwargs, TextResponse)
            logger.debug('<url:%s body:%s status:%s proxy:%s>' %
                  (response.url, response.request.body, response.status,
                   response.meta.get('proxy')))
            if self.response_failed(response):
                request = response.request.replace(dont_filter=True)
                return request
            else:
                result = func(self, *args, **kwargs)
                if result:
                    for i in result.__iter__():
                        yield i

        return f

    # 起始url
    def start_requests(self):
        for url in self.start_urls:
            page = 1
            if url == 'http://xukezheng.cbrc.gov.cn/ilicence/getLicence.do?useState=3':
                yield scrapy.Request(
                    url,
                    method='post',
                    headers=default_header(),
                    body=cbrc_xuke_date(page),
                    meta={'page': 1},
                    errback=self.error_back,
                    callback=self.list_parse)

    def parse(self, response):
        pass

    # 列表页重载为字典
    def load_json(self, response):
        JS = _PARTTERN.search(response.text).group(1)
        return json.loads(JS)

    def next_page(self, response):
        page = response.meta.get('page')
        _totalPage = response.meta.get('totalpage')
        if _totalPage:
            totalPage = _totalPage
        else:
            totalPage = re.compile('totalProperty\s*?:\s*?(\d+)').search(
                response.text)
            if totalPage:
                totalPage = int(totalPage.group(1)) / LIMIT
            else:
                totalPage = 1
        _request_ = []
        if page != 1:
            return
        while page < totalPage:
            page += 1
            request = response.request.replace(
                meta={'page': page,
                      'totalpage': totalPage},
                body=cbrc_xuke_date(page),
                headers=default_header(),
                dont_filter=True)
            _request_.append(request)
        return _request_

    @check_response
    def list_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return 
        JS = self.load_json(response)
        for info in JS:
            state = info['useState']
            flow_no = info['flowNo']
            url = 'http://xukezheng.cbrc.gov.cn/ilicence/showLicenceInfo.do?state=%s&id=%s' % (
                state, flow_no)
            yield scrapy.Request(
                url,
                meta=info,
                priority=1,
                headers=default_header(),
                errback=self.error_back,
                callback=self.cbrc_info_parse)
        requests_ = self.next_page(response)
        if requests_:
            for request in requests_:
                yield request

    @check_response
    def cbrc_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return 
        configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'cbrc_institution',
                'keys': ['org_code'],
                'check': 'org_code',
                'conn': False
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '机构编码',
                    'En': 'org_code',
                    'v':
                    '//table//tr[td[re:test(text(),"机构编码：")]]/td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '机构名称',
                    'En': 'org_name',
                    'v':
                    '//table//tr[td[re:test(text(),"机构名称：")]]/td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '机构简称',
                    'En': 'org_short_name',
                    'v':
                    '//table//tr[td[re:test(text(),"机构简称：")]]/td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '机构地址',
                    'En': 'org_address',
                    'v':
                    '//table//tr[td[re:test(text(),"机构地址：")]]/td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '经度',
                    'En': 'longitude',
                    'v': '//table//tr[td[re:test(text(),"经度：")]]/td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '纬度',
                    'En': 'latitude',
                    'v': '//table//tr[td[re:test(text(),"纬度：")]]/td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '机构所在地',
                    'En': 'site_of_institution',
                    'v':
                    '//table//tr[td[re:test(text(),"机构所在地：")]]/td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '邮政编码',
                    'En': 'postal_code',
                    'v':
                    '//table//tr[td[re:test(text(),"邮政编码：")]]/td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '发证日期',
                    'En': 'date_of_issuing',
                    'v':
                    '//table//tr[td[re:test(text(),"发证日期：")]]/td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n':
                    '批准成立日期',
                    'En':
                    'date_of_approval',
                    'v':
                    '//table//tr[td[re:test(text(),"批准成立日期：")]]/td[2]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n': '发证机关',
                    'En': 'certification_authority',
                    'v':
                    '//table//tr[td[re:test(text(),"发证机关：")]]/td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '流水号',
                    'En': 'serial_number',
                    'v':
                    '//table//tr[td[re:test(text(),"流水号：")]]/td[2]/text()',
                    't': 'xpath_first'
                },
            ]
        }, {
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'cbrc_institution_change',
                'keys': ['org_code'],
                'check': 'org_code',
                'conn': False
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n':
                    '流水号',
                    'En':
                    'serial_number',
                    'v':
                    '//tr[re:test(@id,"td\d")]/td[re:test(text(),"流水号：")]/../td[2]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '机构编码',
                    'En':
                    'org_code',
                    'v':
                    '//tr[re:test(@id,"td\d")]/td[re:test(text(),"机构编码：")]/../td[2]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '机构名称',
                    'En':
                    'org_name',
                    'v':
                    '//tr[re:test(@id,"td\d")]/td[re:test(text(),"机构名称：")]/../td[2]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '机构地址',
                    'En':
                    'org_address',
                    'v':
                    '//tr[re:test(@id,"td\d")]/td[re:test(text(),"机构地址：")]/../td[2]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        items = self.configParse(configs, response, response)
        for item in items.__iter__():
            item_ = item
            yield item_

    def error_back(self, response):
        request = response.request.replace(dont_filter=True)
        print('wrong HTTPERROR:%s' % response.status)
        yield request
