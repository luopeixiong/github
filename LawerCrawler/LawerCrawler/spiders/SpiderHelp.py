# -*- coding:utf-8 -*-
import os
import sys
BASEDIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# 加入环境变量  临时性非全局
sys.path.append(BASEDIR)
sys.path.append('../')
import scrapy
import re
import requests
from scrapy.http.response.text import TextResponse
from scrapy.http.response import Response
import urllib.parse
from user_agent import generate_user_agent
from myselector import Selector as S
import json
import logging
from math import ceil
import time

conn_flag = False   # False使用本地数据库 True 使用公司数据库
start_time = time.time()
proxy_flag = True

'_configs 统一为页面抓取信息配置'

# 睡眠函数  可放入check_response内
def sleep_flag():
    if (time.time() - start_time) % (20 * 60) > (15 * 60):
        print('start_sleep')
        time.sleep(5)
        print('continue')
    else:
        print('pass')


# 日志handler
logger = logging.getLogger(__name__)

# 代理去http/https
_ip = re.compile('\/\/(.*?):')
# 一些页面的pagesize全局变量
PAGESIZE = 100
# 处理json
true = 'true'
# 处理json
false = 'false'
# 最大重试次数
MAX_TIMES = 3




# 删除proxy
def delete_proxy(response: Response):  # 删除不可用代理
    ip = _ip.search(response.meta['proxy']).group(1)
    requests.get(
        "http://10.1.18.35:8000/delete?ip={}".format(ip),
        allow_redirects=False)
    requests.get(
        "http://10.1.18.35:8000/delete?types=2", allow_redirects=False)


# 实例化Item
class Item(scrapy.Item):
    # define the fields for your item here like:
    result = scrapy.Field()  # 封装结果
    keys = scrapy.Field()
    db = scrapy.Field()
    conn = scrapy.Field()


class SpiderHelp(object):
    def __init__(self):
        pass

    @property
    def default_header(self) -> dict:

        return {
            'User_Agent': generate_user_agent(os=('win', )),
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

    # 默认的表头
    @property
    def default_jheader(self) -> dict:
        return {
            'User_Agent': generate_user_agent(os=('win', )),
            'Content-Type': 'application/json'
        }

    # 删除 绑定在response内的代理
    def delete_proxy(self, response: Response):
        '''
        @params response
        @目标 删除response proxy
        @output None
        '''
        if response.meta.get('proxy'):
            ip = _ip.search(response.meta['proxy']).group(1)
            requests.get("http://10.1.18.35:8000/delete?ip={}".format(ip))

    # 类判断
    def get_instance(self, args: tuple or list, cls):
        '''
        @params  args:参数列表
        @params cls:类
        @output i  -> if ininstance(i,cls) == True
        '''
        if args:
            for i in args:
                if isinstance(i, cls):
                    return i

    def _get_instance(self, kwargs: dict, cls):
        '''
        @params  args:参数字典
        @params cls:类
        @output i.values()  -> if ininstance(i.values(),cls) == True
        '''
        if kwargs:
            _list = list(kwargs.values())
            return self.get_instance(_list)

    def getfinstance(self, args, kwargs, cls):
        '''
        @params cls -->type or tuple of types
        '''
        flag = self.get_instance(args, cls)
        return flag if flag else self._get_instance(kwargs, cls)

    # 判断失败页面逻辑
    def response_failed(self, response: Response) -> bool:
        '''
        @output Ture-->重新发送请求 False:为正确请求
        @output False-->正确请求，参数传递给 parse
        '''
        if response.status in [404,  407]:
            if response.status in [404, 407]:
                self.delete_proxy(response)
            return True
        elif re.compile('seturl|没有查询到相关结果[\s\S]*没有查询到相关结果', re.I|re.S).search(response.text):
            return True
        else:
            return False

    # logger 日志
    def check_response(func: callable):
        '''
        @parsms:func  装饰函数
        '''

        def decorate(self, *args, **kwargs):
            if not callable(func):
                raise TypeError('<class %s is not a callback func>' %
                                (func.__class__))
            response = self.getfinstance(args, kwargs,
                                         (TextResponse, Response))
            logger.debug('<url:%s body:%s status:%s proxy:%s>' %
                         (response.url, response.request.body, response.status,
                          response.meta.get('proxy')))
            result = func(self, *args, **kwargs)
            if self.response_failed(response):
                request = response.request.replace(dont_filter=True)
                yield request
            else:
                if result:
                    for i in result.__iter__():
                        yield i

        return decorate

    def item_parse(self, _configs: list, response, response1=None) -> dict:
        '''
        @parsma _configs->字段抓取设置  list
        @params response->Response
        @output -->result  字段-值 的字典
        '''
        if hasattr(response,'url'):
            response1 = response
        for configs in _configs:
            response_change = self.change_response_f_type(configs, response)
            if configs['list']['v']:
                _response_copy = S.select_content(response_change,
                                                  configs['list'], response1)
            else:
                if isinstance(response_change, list):
                    _response_copy = response_change
                else:
                    _response_copy = [response_change]
            for _response in _response_copy:
                result = dict()
                for config in configs['data']:
                    result[config['En']] = S.select_content(
                        _response, config, response1)
                    result[config['En']] = S.replace_all(result[config['En']])
                item = self.item_db_parse(configs, result)
                if item:
                    # 持久化记录item
                    self.state['items_count'] = self.state.get(
                        'items_count', 0) + 1
                    yield item

    def item_db_parse(self, configs, result):
        '''
        @params configs 字典 里面有keys,db,check3个参数 check在result里有对应key
        @params result 字典 解析字段的返回值
        '''
        check = configs['list']['check']
        if not result[check]:  # 非空字段检索 为None ''  return
            return
        item = Item()
        item['result'] = result
        item['db'] = configs['list']['db']
        item['keys'] = configs['list']['keys']
        item['conn'] = configs['list'].get('conn',False)
        return item

    def change_response_f_type(self, configs, response):
        if configs.get('response_type') == 'json':
            return json.loads(response.text)
        else:
            return response

    def scrapy_page_help(self,
                         response: Response,
                         config: dict = None,
                         callback: callable = None,
                         headers: dict = None,
                         urlfunc: callable = None,
                         bodyfunc: callable = None,
                         divmod: int = 1,
                         response_type: 'xpath' or 'json' = 'xpath',
                         method: 'GET' or 'POST' = 'GET',
                         flag=False,  # True为下一页翻页，False为生成所有页面
                         pagestart=1,  # 其实页说明
                         connect_type: 'urlencode'
                         or 'json' = 'urlencode') -> scrapy.Request:
        '''
        @ params response  parse的response形参
        @ params config  获取total方法参数  调用S.select_content
        @ callback  回调函数
        @ headers 默认为urlencode
        @ urlfunc  常用lambda函数 
        @ connect_type 决定body的encode方法
        @ response_type 决定参数获取方式
        @ method Request method
        @ divmod 获取到total 后计算totalpage的除数
        @ bodyfunc 常用lambda表达式
        return [Requests]
        '''
        page = response.meta.get('page', 1)
        if page != pagestart or flag:
            return []
        dataencode = urllib.parse.urlencode if connect_type == 'urlencode' else json.loads
        if response_type.lower() == 'json':
            JS_response = json.loads(response.text)
        else:
            JS_response = response
        totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
            ceil(int(S.select_content(JS_response, config)) / divmod) if S.select_content(JS_response, config)\
            else 1
        reqs = set()
        logger.info('totalpage is %s' % totalpage)
        # 直接获取最大页码 生成request
        if page < totalpage and not flag:
            for page in range(page + 1, totalpage + 1):
                if callable(bodyfunc):
                    body = bodyfunc(page, response=response)
                    if isinstance(body, str):
                        pass
                    else:
                        body = dataencode(body)
                else:
                    body = None
                if callable(urlfunc):
                    url = urlfunc(page)
                else:
                    url = response.url
                req = scrapy.Request(
                    url,
                    method=method,
                    body=body,
                    headers=headers,
                    meta={'page': page,
                          'totalpage': totalpage},
                    callback=callback)
                reqs.add(req)
        # 下一页判断翻页 
        elif page < totalpage and flag:
            if S.select_content(JS_response, config):
                page += 1
                req = scrapy.Request(
                    url,
                    method=method,
                    body=body,
                    headers=headers,
                    meta={'page': page,
                          'totalpage': totalpage},
                    callback=callback)
                reqs.add(req)
        return reqs


