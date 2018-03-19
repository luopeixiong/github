# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from user_agent import generate_user_agent
from twisted.web._newclient  import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectError, ConnectionRefusedError ,TCPTimedOutError
import random
import json
import time
import requests
s = requests
class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self,user_agent=''):
        self.user_agent = user_agent
        
    def process_request(self, request ,spider):
        ua = generate_user_agent(os=('mac','win'))
        request.headers.setdefault('User-agent',ua)
        request.headers.setdefault('Accept','*.*')
        request.headers.setdefault('Accept-Encodeing','gzip,deflat')
        request.headers.setdefault('Accept-Language','en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4')
        request.headers.setdefault('Content-Type','text/html;charset=UTF-8')

class ProxyMiddleware(object):
    def __init__(self):
        self.proxys = []
        self.tagurl = "http://www.cyzone.cn"
        self.DONT_RETRY_ERRORS = (TimeoutError, ConnectError, ConnectionRefusedError, ValueError, ResponseNeverReceived, TCPTimedOutError)
        self.start = time.time()
        self.disallow = []
        self.proxy = ""
    def getproxy(self):
        #获取10个代理 并去掉不可用
        self.proxys = []
        if self.proxys is []:
            self.disallow = []
        url = "http://www.xdaili.cn/ipagent//freeip/getFreeIps"
        res = json.loads(s.get(url).text)['RESULT']['rows']
        proxy = ["http://"+i["ip"]+":"+i['port'] for i in res]
        
#        print(proxy)
        self.proxys.extend(proxy)
        #http://115.226.136.183:42859
        self.proxys = [i for i in self.proxys if i not in self.disallow]
#            print("目前可用代理ip为%s"%(self.proxys))
        print("目前可用代理数为%s"%(len(self.proxys)))
        return self.proxys
    def process_request(self, request, spider):
        now = time.time()
        last = now - self.start
        print("目前可用代理数为%s"%(len(self.proxys)))
        try:
            if self.proxys and last<150:
                proxy = random.choice(self.proxys)
                request.meta['proxy'] = proxy
            else:
                self.getproxy()
                if self.proxys == []:
                    time.sleep(30)
                self.start = time.time()
                proxy = random.choice(self.proxys)
                request.meta['proxy']  = proxy
        except Exception as e:
            print(e)
    def process_exception(self, request, exception, spider):
        """
            处理由于使用代理导致的链接一次,则重新换个代理继续请求
        """
        print("错误类型",exception)
        if isinstance(exception, self.DONT_RETRY_ERRORS):
            #不可用proxy加入disallow
            self.disallow.append(request.meta['proxy'])
            #生成self.proxys 与disallow的补
            self.proxys = [i for i in self.proxys if i not in self.disallow]
            new_request = request.copy()
            try:
                proxy = random.choice(self.proxys)
            except IndexError:
                self.getproxy()
                proxy = random.choice(self.proxys)
            new_request.meta['proxy'] = proxy
            print("正在使用代理为%s"%proxy)
            return new_request
        


class P2PeyeSpiderMiddleware(object):
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
