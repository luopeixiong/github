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
import time
import re
import requests
#import re
s = requests
import json
import logging

logger = logging.getLogger(__name__)
_ip = re.compile('\/\/(.*?):')
def get_proxy():
    res = requests.get("http://10.1.18.35:8000/?types=0&count=30&country=国内")
    JS = json.loads(res.text)
    proxies = ['http://'+proxy[0]+':'+str(proxy[1]) for proxy in JS]
    return proxies

def delete_proxy(proxy):
    ip = _ip.search(proxy).group(1)
    requests.get("http://10.1.18.35:8000/delete?ip={}".format(ip))

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
        #http://115.226.136.183:42859
        self.proxys = get_proxy()
#            print("目前可用代理ip为%s"%(self.proxys))
        print("目前可用代理数为%s"%(len(self.proxys)))
        return self.proxys
    def process_request(self, request, spider):
        now = time.time()
        last = now - self.start
        print("目前可用代理数为%s"%(len(self.proxys)))
        try:
            if self.proxys and last<300:
                proxy = random.choice(self.proxys)
                request.meta['proxy'] = proxy
            else:
                self.getproxy()
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
            delete_proxy(request.meta['proxy'])
            #生成self.proxys 与disallow的补
            self.proxys = [i for i in self.proxys if i not in self.disallow]
            new_request = request.copy()
            try:
                proxy = random.choice(self.proxys)
            except IndexError:
                self.getproxy()
                proxy = random.choice(self.proxys)
            new_request.meta['proxy'] = proxy
            new_request = new_request.replace(dont_filter=True)
            print("正在使用代理为%s"%proxy)
            return new_request

    def process_response(self, request, response, spider):
        """
        检查response.status, 根据status是否在允许的状态码中决定是否切换到下一个proxy, 或者禁用proxy
        """
        if "proxy" in request.meta.keys():
            logger.debug("%s %s %s" % (request.meta["proxy"], response.status, request.url))
        else:
            logger.debug("None %s %s" % (response.status, request.url))

        # status不是正常的200而且不在spider声明的正常爬取过程中可能出现的
        # status列表中, 则认为代理无效, 切换代理
        if response.status != 200 \
                and (not hasattr(spider, "website_possible_httpstatus_list") \
                             or response.status not in spider.website_possible_httpstatus_list):
            logger.info("response status not in spider.website_possible_httpstatus_list")
            try:
                proxy = random.choice(self.proxys)
            except IndexError:
                self.getproxy()
                proxy = random.choice(self.proxys)
            new_request = request.copy()
            new_request.meta['proxy'] = proxy
            new_request.dont_filter = True
            return new_request
        else:
            return response


class PedataSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
