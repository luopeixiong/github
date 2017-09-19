# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

#import time
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from user_agent import generate_user_agent
import requests
#from twisted.web._newclient  import ResponseNeverReceived
#from twisted.internet.error import TimeoutError, ConnectError, ConnectionRefusedError
#import random
#import json
s = requests.Session()

class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self,user_agent=''):
        self.user_agent = user_agent
        
    def process_request(self, request ,spider):
        ua = generate_user_agent()
        request.headers.setdefault('User-agent',ua)
        request.headers.setdefault('Accept','*.*')
        request.headers.setdefault('Accept-Encodeing','gzip,deflat')
        request.headers.setdefault('Accept-Language','en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4')
        request.headers.setdefault('Content-Type','text/html;charset=UTF-8')


class AmacProductSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
