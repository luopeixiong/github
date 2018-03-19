# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy import Request
import json
import redis
import re
import socket
import urllib.parse
from user_agent import generate_user_agent
import logging

logger = logging.getLogger(__name__)
regex = re.compile('_')


class RedisHelp(object):
    def __init__(self,cls,host=socket.gethostbyname(socket.gethostname()),redis_key=None,port=6379,db=0):
        self.host = host if not getattr(cls,'host',False) else getattr(cls,'host')
        self.redis_key = redis_key if not getattr(cls,'redis_key',False) else getattr(cls,'redis_key')
        self.port = port if not getattr(cls,'port',False) else getattr(cls,'port')
        self.db = db if not getattr(cls,'db',False) else getattr(cls,'db')
        self.r = self.__connect_redis()

    def __connect_redis(self):
        return redis.Redis(host=self.host,port=self.port, db=self.db)

    #改为先进先出
    def lpush(self,value):
        self.r.rpush(self.redis_key, value)



class _Request(Request):
    def __init__(self,url, callback=None, method='GET', headers=None, body=None,
                 cookies=None, meta=None, encoding='utf-8', priority=0,
                 dont_filter=False, errback=None, flags=None,redis_flag=False,redis_conn=None):
        Request.__init__(self, url, callback=callback, method=method, headers=headers, body=body,
                 cookies=cookies, meta=meta, encoding=encoding, priority=priority,
                 dont_filter=dont_filter, errback=errback)
        self.redis_flag = redis_flag
        self.redis_conn = redis_conn
        self._headers = headers
        self._send_to_redis()
        
    
    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        if kwargs.get('redis_flag'):
            obj.__init__(*args,**kwargs)
        else:
            return obj

    def to_json_str(func):
        def f(self,*args,**kwargs):
            _kwargs = kwargs.copy()
            data = {}
            for k,v in _kwargs.items():
                if k not in  ['callback','errback']:
                    if k.startswith('_'):
                         regex.sub('', k ,1)
                    data[k] = self.to_str(v)
                else:
                    if callable(v):
                        v = 'self.' + v.__name__
                    data[k] = v
            return json.dumps(data)
        return f

    def to_str(self, val):
        if isinstance(val, bytes):
            val = val.decode('utf-8')
        return val

    @to_json_str
    def _redis_json_data(*args, **kwargs):
        pass

    @property
    def make_redis_data(self):
        return self._redis_json_data(url=self._url,meta=self._meta,encoding=self._encoding,
                method=self.method,body=self._body,callback=self.callback,cookies=self.cookies,
                errback=self.errback,headers=self._headers,dont_filter=self.dont_filter)

    def _send_to_redis(self):
        if self.redis_flag:
            self.redis_conn.lpush(self.make_redis_data)
            



class _RedisSpider(RedisSpider):
    name = "test"
    # allowed_domains = ["www.baidu.com"]
    start_urls = ['http://www.baidu.com/']
    redis_key = 'test:starturls'
    signel = 1
    host = '10.1.18.35'
    redis_flag=True


    def __init__(self, **kwargs):
        self.r = RedisHelp(self)

    def make_requests_from_url(self, url):
        request = self.__redis_url_parse(url)
        return request



    # def start_requests(self):
    #     if hasattr(self, 'redis_key'):
    #         return RedisSpider.start_requests(self)
    #     else:
    #         self.redis_flag=False
    #         # 正常写
    #         yield _Request('http://www.baidu.com')

    def __redis_url_parse(self, url):
        if url.startswith('{'):
            kw = json.loads(url)
            try:
                kw['callback']=eval(kw.get('callback')) if kw.get('callback') else self.parse
            except Exception as e:
                logger.error(e)
            return scrapy.Request(**kw)
        else:
            return scrapy.Request(url)

    def parse(self, response=None):
        if hasattr(response,'text'):
            print(response.text)
        page=response.meta.get('page', 0) if response else 0
        page +=1
        url = 'http://www.sd12348.gov.cn/sftIDC/select/search.do'
        data = urllib.parse.urlencode({
            'page': str(page),
            'areacode': '37',
            'order': '',
            'pageSize': '10',
            'type': 'lawyer',
            'flag': '0',
            'status': '1'
        })
        yield scrapy.Request(
            url,
            body=data,
            method='POST',
            dont_filter=True,
            meta={'page': page},
            priority=100,
            headers=self.default_header(),
            # redis_flag=self.redis_flag,
            # redis_conn=self.r,
            callback=self.parse)
 
if __name__ == '__main__':
    pass
    # A = _Request('http://www.baidu.com',encoding='GBK')
    # q = TestSpider()
    # result = q.parse()
    # for i in result:
    #     pass
