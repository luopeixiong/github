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
MAX = 2**15
from myselector import pdf_to_html


SEARCH_WORD = '国家主席习近平'
BASEPATH = 'F:\\BAIDU'

#redis数据库使用FOFI先进后出的规则 对url进行队列选择
class SinaspiderSpider(_RedisSpider, SpiderHelp):  #,scrapy.Spider
    name = 'baidu_image'
    start_urls = [
        'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=%s&pn=00' % SEARCH_WORD
    ]
    fmt = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word={}&pn=%s'.format(SEARCH_WORD)
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
                callback=self.baidu_image_in)

    def baidu_image_in(self, response):
        result = re.compile('"data":\s*?(\[\{.*?\}\])',re.S).search(response.text).group(1)
        JS = json.loads(result)
        for item in JS:
            url = item.get('thumbURL')
            if url:
                yield self.request(url,
                    meta=item,
                    headers=self.default_header,
                    callback=self.image_download)

        flag = response.xpath('//a[text()="下一页"]/@href').extract_first()
        if flag:
            next_url = response.urljoin(flag)
            yield self.request(next_url,
                headers=self.default_header,
                callback=self.baidu_image_in)

    def image_download(self, response):
        content = response.body
        item = response.meta
        filename = item['cs']
        filetype = response.url.split('.')[-1]
        path = filename+'.'+filetype
        _path = os.path.join(BASEPATH,path)
        with open(_path,'wb') as f:
            f.write(content)

def main():
    SinaspiderSpider.put_redis()

if __name__=='__main__':
    main()