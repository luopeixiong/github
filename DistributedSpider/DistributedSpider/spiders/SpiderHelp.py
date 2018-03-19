# -*- coding:utf-8 -*-
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
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
from RedisHelp import _Request
from functools import wraps
from json import JSONDecodeError
import execjs

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
MAX_TIMES = 10




# 删除proxy
def delete_proxy(response: Response):  # 删除不可用代理
    try:
        ip = _ip.search(response.meta['proxy']).group(1) 
    except:
        ip = ''
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
    state = {}
    faile_respon = '(?:seturl|^$|没有查询到相关结果[\s\S]*没有查询到相关结果|The proxy server received an invalid|UncategorizedSQLException|访问过于频繁)'

    def __init__(self,**kwargs):
        pass

    @property
    def default_header(self)->dict:
        return {
            'User-Agent': generate_user_agent(os=('win',),navigator=('chrome', 'firefox',),device_type=("desktop",),),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate', 
            'Accept': '*/*'
        }

    def header_update(self,headers,**kwargs):
        headers.update(kwargs)
        return headers  

    # 默认的表头
    @property
    def default_jheader(self)->dict:
        return {
            'User-Agent': generate_user_agent(os=('win',),navigator=('chrome', 'firefox',),device_type=("desktop",),),
            'Content-Type': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate', 
            'Accept': '*/*'
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
        if response.status in [301, 404, 403, 502, 500, 504, 407]:
            if response.status in [301, 403, 404, 502, 500, 504, 407]:
                self.delete_proxy(response)
            return True
        elif re.compile(self.faile_respon, re.I|re.S).findall(response.text):
            return True
        else:
            return False

    
    def set_faile_reason(self, value = 'seturl|^$|没有查询到相关结果[\s\S]*没有查询到相关结果|The proxy server received an invalid|UncategorizedSQLException|访问过于频繁'):
        self.faile_respon = value


    def new_request(self, response):
        __meta = response.meta.copy()
        try_time = __meta.get('try_time', 0) + 1
        if try_time > MAX_TIMES:
            logger.warning('TRY MORE THAN %s TIMES ON %s' % (MAX_TIMES,response.url))
        else:
            __meta['try_time'] = try_time
            logger.debug('RESPONSE IS INVALID,TRY %s TIME ON %s' % (try_time,response.url))
            return response.request.replace(dont_filter=True, meta=__meta)

    def response_try(self, response):
        if self.response_failed(response):
            return self.new_request(response)

    # logger 日志
    @staticmethod
    def check_response(func: callable):
        '''
        @parsms:func  装饰函数
        '''
        @wraps(func)
        def decorate(self, *args, **kwargs):
            if not callable(func):
                raise TypeError('<class %s is not a callback func>' %
                                (func.__class__))
            response = self.getfinstance(args, kwargs,
                                         (TextResponse, Response))
            logger.info('<url:%s body:%s status:%s proxy:%s>' %
                         (response.url, response.request.body, response.status,
                          response.meta.get('proxy')))
            if self.response_failed(response):
                request = self.new_request(response)
                if request:
                    yield request
                    return
            result = func(self, *args, **kwargs)
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
                                                  configs['list'], response1) or []
            else:
                if isinstance(response_change, list):
                    _response_copy = response_change
                else:
                    _response_copy = [response_change]
            for _response in _response_copy:
                if not _response:
                    return
                result = dict()
                for config in configs['data']:
                    result[config['En']] = S.select_content(
                        _response, config, response1)
                    result[config['En']] = S.replace_all(result[config['En']])
                print(result)
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
            try:
                try:
                    v = json.loads(response.text)
                except:
                    v = execjs.eval(response.text)
                return v
            except BaseException as e:
                logger.info('jsonDecoder error %r' % e)
        else:
            return response

    # 翻页函数
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
                         redis_flag=False,
                         redis_conn=None,
                         errback=None,
                         cookies=None,
                         offset=1,
                         meta={},
                         readpage=128, # 每次余数 生成nextpages数
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
        _pagestart = response.meta.get('pagestart') or pagestart
        _offset = response.meta.get('offset') or offset
        page = response.meta.get('page') or 1
        dataencode = urllib.parse.urlencode if connect_type == 'urlencode' else json.dumps
        if not response.meta.get('totalpage'):
            if response_type.lower() == 'json':
                try:
                    JS_response = json.loads(response.text)
                except:
                    JS_response = execjs.eval(response.text) if hasattr(response,'text') else response if isinstance(response,(dict,list)) else {}
            else:
                JS_response = response
        else:
            JS_response = response

        reqs = set()
        
        # 直接获取最大页码 生成request 更新逻辑为一次生成默认32页,优化内存
        if not flag:
            totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
                ceil(int(S.select_content(JS_response, config, response)) / divmod) if S.select_content(JS_response, config, response)\
                else 1
            if page < totalpage and not flag:
                _readpage = readpage * _offset
                pagestart = _pagestart % _readpage
                if page % _readpage == pagestart:
                    minpage = min(page + _readpage,totalpage)
                    logger.info('from %s to %s,totalpage is %s' % (page+1,minpage,totalpage))
                    for page in range(page + _offset, minpage + _offset, _offset):
                        if callable(bodyfunc):
                            body = bodyfunc(page, response=response)
                            if isinstance(body, str):
                                pass
                            else:
                                body = dataencode(body)
                        else:
                            body = None
                        if callable(urlfunc):
                            url = urlfunc(page,response=response)
                        else:
                            url = response.url
                        _meta = response.meta.copy()
                        _meta.update({'page': page,
                                  'pagestart':_pagestart,
                                  'totalpage': totalpage,
                                  'offset':_offset})
                        req = _Request(
                            url,
                            method=method,
                            body=body,
                            headers=headers,
                            redis_flag=redis_flag,
                            redis_conn=redis_conn,
                            errback=errback,
                            cookies=cookies,
                            meta=_meta,
                            callback=callback)
                        reqs.add(req)
            elif page > totalpage and not flag:
                _readpage = readpage * _offset
                pagestart = _pagestart % _readpage
                if page % _readpage == pagestart:
                    minpage = max(page-_readpage,totalpage)
                    logger.info('from %s to %s,totalpage is %s' % (page,minpage,totalpage))
                    for page in range(minpage, page):
                        if callable(bodyfunc):
                            body = bodyfunc(page, response=response)
                            if isinstance(body, str):
                                pass
                            else:
                                body = dataencode(body)
                        else:
                            body = None
                        if callable(urlfunc):
                            url = urlfunc(page,response=response)
                        else:
                            url = response.url
                        _meta = response.meta.copy()
                        _meta.update({'page': page,
                                  'pagestart':_pagestart,
                                  'totalpage': totalpage,
                                  'offset':_offset})
                        req = _Request(
                            url,
                            method=method,
                            body=body,
                            headers=headers,
                            redis_flag=redis_flag,
                            redis_conn=redis_conn,
                            errback=errback,
                            cookies=cookies,
                            meta=_meta,
                            callback=callback)
                        reqs.add(req)
        # 下一页判断 默认生成32页 翻页 
        elif flag:
            if S.select_content(JS_response, config):
                _readpage = readpage * _offset
                pagestart = _pagestart % _readpage
                if page % _readpage == pagestart:
                    logger.info('from %s to %s,totalpage is undefind' % (page+1,page+readpage))
                    for _page in range(page + 1, page+_readpage+1):
                        if callable(urlfunc):
                            url = urlfunc(_page,response=response)
                        else:
                            url = response.url
                        if callable(bodyfunc):
                            body = bodyfunc(_page, response=response)
                            if isinstance(body, str):
                                pass
                            else:
                                body = dataencode(body)
                        else:
                                body = None
                        _meta = response.meta.copy()
                        _meta.update({'page': _page,
                                  'pagestart':_pagestart,
                                  'offset':_offset})
                        req = _Request(
                            url,
                            method=method,
                            body=body,
                            headers=headers,
                            meta=_meta,
                            redis_flag=redis_flag,
                            redis_conn=redis_conn,
                            callback=callback,
                            errback=errback)
                        reqs.add(req)
            else:
                # logger.error(response.text)
                with open('1.html','wb') as f:
                    f.write(response.body)
        return reqs

    # return config生成的url
    def scrapy_info_url_help(self,
                         response: Response,
                         config: dict = None,
                         callback: callable = None,
                         errback=None,
                         headers: dict = None,
                         urlfunc: callable = None,
                         bodyfunc: callable = None,
                         divmod: int = 1,
                         meta=None,
                         priority=100,
                         cookies=None,
                         redis_flag=False,
                         redis_conn=None,
                         dont_filter=False,
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
        dataencode = urllib.parse.urlencode if connect_type == 'urlencode' else json.dumps
        if response_type.lower() == 'json':
            try:
                JS_response = json.loads(response.text)
            except:
                JS_response = execjs.eval(response.text)
        else:
            JS_response = response
        reqs = set()
        urls = S.select_content(JS_response, config, response)
        if isinstance(urls, list):
            pass
        else:
            urls = [urls]
        for page in urls:
            if not page:
                return []
            if callable(bodyfunc):
                    body = bodyfunc(page, response=response)
                    if isinstance(body, str):
                        pass
                    else:
                        body = dataencode(body)
            else:
                body = None
            if callable(urlfunc):
                if isinstance(page,tuple):
                    url = urlfunc(*page,response=response)
                else:
                    url = urlfunc(page,response=response)
            else:
                url = response.url
            _meta = response.meta.copy()
            meta = meta if meta else {}
            _meta.update(meta)
            req = _Request(
                url,
                method=method,
                body=body,
                headers=headers,
                meta=_meta,
                priority=priority,
                cookies=cookies,
                redis_flag=False,
                redis_conn=None,
                dont_filter=dont_filter,
                callback=callback,
                errback=errback)
            reqs.add(req)
        return reqs

    def request(self,url,callback=None,dont_filter=False,
        method='GET',cookies=None,
        headers=None,priority=0,meta=None,encoding='utf-8',body=None,
        redis_flag=False,redis_conn=None):
        callback = callback if callback else self.parse
        headers=headers if headers else self.default_header
        if redis_flag:
            return _Request(url,callback=callback,dont_filter=dont_filter,body=body,method=method,cookies=cookies,
                headers=headers,priority=priority,meta=meta,encoding=encoding,redis_flag=redis_flag,redis_conn=self.r)
        else:
            return _Request(url,callback=callback,dont_filter=dont_filter,body=body,method=method,cookies=cookies,
                headers=headers,priority=priority,meta=meta,encoding=encoding)

    @classmethod
    def put_redis(cls,*args,**kwargs):
        if hasattr(cls,'_start_requests'):
            reqs = cls(*args,**kwargs)._start_requests()
            for req in reqs:
                pass
        else:
            raise AttributeError('<class object %s> has not attribute _start_requests' % cls.__name__)

    def errbackparse(self, failure):
        logger.error(failure)