# -*- coding: utf-8 -*-
import scrapy
from myselector import Selector as S
import json
from user_agent import generate_user_agent
import urllib.parse
from Help import *
from .localConfigs import *
import re
#构造页面检查方法,用于页面的重试
def trytime_(response):
    if response.meta.get('maxtrys'):
        response.meta['maxtrys'] += 1
    else:
        response.meta['maxtrys'] = 1
def gettrytime(response,maxtry=3):
    trytime_(response)
    if response.meta['maxtrys']<maxtry:
        return True
def checkTimeError(response,maxtry=3):
    flag = gettrytime(response,maxtry)
    if flag and 'setURL' in response.text or response.status in [403]:
        request = response.request.replace(dont_filter = True)
        return request
    
class P2peyeSpider(scrapy.Spider, other):
    name = "p2peye"
#    allowed_domains = ["p2peye.com"]
    start_urls = ['http://www.p2peye.com/?ajax=1']
    custom_settings = {
#                        'DOWNLOADER_MIDDLEWARES': {
#                        'P2peye.middlewares.RotateUserAgentMiddleware':401,
#                        'P2peye.middlewares.ProxyMiddleware':700,
#                        },
                        'CONCURRENT_REQUESTS_PER_IP' :10,
                        'DOWNLOAD_DELAY':0.5,
                        'DEPTH_PRIORITY' : -1,
                        }
    def parse(self, response):
#        print(response.text)
        JS = json.loads(response.text)
        for _json in JS['data']:
            domain = _json['domain_body']
            pid = _json['pid']
            n = 1
            if domain:
                url = 'http://%s.p2peye.com/beian/'%domain
                Origin = 'http://%s.p2peye.com'%domain
                referer = 'http://%s.p2peye.com/beian/'%domain
                headers = hdr()
                headers.update({'referer':referer,'Origin':Origin})
                yield scrapy.Request(url,
                                     callback = self.infoParse,
                                     meta = {'pid':pid,'domain':domain},
                                     headers=headers,
                                     priority=2
                                     )
                format_ = 'http://%s.p2peye.com/gdajax/?pid=%s&pn={pn}'%(domain,pid)
                url_ = format_.format(pn=1)
                yield scrapy.Request(url_,
                                     callback = self.ShareholderinfoParse,
                                     meta = {'pid':pid,'domain':domain,'page':1,'format_':format_,'headers':headers},
                                     headers=headers,
                                     encoding='latin-1',
                                     priority=2)
                format__ = 'http://%s.p2peye.com/comchanajax/?pid=%s&pn={pn}'%(domain,pid)
                url__ = format__.format(pn=1)
                yield scrapy.Request(url__,
                                     callback = self.ChangeRecordParse,
                                     meta = {'pid':pid,'domain':domain,'page':1,'format_':format__,'headers':headers},
                                     headers=headers,
                                     encoding='latin-1',
                                     priority=2)
#                return False
    def ShareholderinfoParse(self,response):
#        print(response.text)
        request = checkTimeError(response)
        if request:return request
        JS = json.loads(response.text)
        items = self.configParse(ShareholderinfoConfigs,JS,response)
        for _item in items.__iter__():
            yield _item  
        if "下一页" in JS['data']['pagedom']:
            print('_'*100)
            format_ = response.meta['format_']
            page = response.meta['page']+1
            pid = response.meta['pid']
            headers = response.meta['headers']
            domain = response.meta['domain']
            nextPage = format_.format(pn=page)
            yield scrapy.Request(nextPage,
                                     callback = self.ShareholderinfoParse,
                                     meta = {'pid':pid,'domain':domain,'page':1,'format_':format_,'headers':headers},
                                     headers=headers,
                                     encoding='latin-1',
                                     priority=3)
    def ChangeRecordParse(self, response):
        request = checkTimeError(response)
        if request:return request
        JS = json.loads(response.text)
        items = self.configParse(ChangeRecordConfigs,JS,response)
        for _item in items.__iter__():
            item = _item
            item['result']['contentAfter'] = re.sub('(?:<[^>]*?>|（注：标有\*标志的为法定代表人）)','',item['result']['contentAfter'])
            item['result']['contentBefore'] = re.sub('(?:<[^>]*?>|（注：标有\*标志的为法定代表人）)','',item['result']['contentBefore'])
            yield item  
        if "下一页" in JS['data']['pagedom']:
            print('_'*100)
            format_ = response.meta['format_']
            pid = response.meta['pid']
            page = response.meta['page']+1
            headers = response.meta['headers']
            nextPage = format_.format(pn=page)
            domain = response.meta['domain']
            yield scrapy.Request(nextPage,
                                 callback = self.ChangeRecordParse,
                                 meta = {'pid':pid,'domain':domain,'page':page,'format_':format_,'headers':headers},
                                 headers=headers,
                                 encoding='latin-1',
                                 priority=3)
    def infoParse(self,response):
        request = checkTimeError(response)
        if request:return request
#        print(response.text)
        items = self.configParse(BaseInfoConfigs,response,response)
        for _item in items.__iter__():
            yield _item
        items1 = self.configParse(seniorExecutiveConfigs,response,response)
        for __item in items1.__iter__():
            yield __item