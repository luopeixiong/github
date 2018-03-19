# -*- coding: utf-8 -*-
import scrapy
from Help import *
from spiders.localConfigs import *
from myselector import Selector as S
import time
import re

headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
           'host':'zdb.pedaily.cn',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Encoding':'gzip,deflate',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           'Referer':'http://zdb.pedaily.cn',
           'Upgrade-Insecure-Requests': '1',
           }
print(headers)
class PedailySpider(scrapy.Spider, other):
    name = "pedaily"
    allowed_domains = ["pedaily.cn"]
    start_urls = ['http://pedaily.cn/']
    start_configs = [
#                      'http://zdb.pedaily.cn/inv/p{page}/',
#                     'http://zdb.pedaily.cn/company/all-p{page}/',
#                     'http://zdb.pedaily.cn/ipo/p{page}/',
#                     'http://zdb.pedaily.cn/ma/p{page}/',
                     'http://zdb.pedaily.cn/pe/p{page}/',
#                     'http://zdb.pedaily.cn/enterprise/p{page}/',
#                     'http://zdb.pedaily.cn/people/index.shtml-p{page}/',
                     
                     ]
    custom_settings = {'ROBOTSTXT_OBEY':False,
                       'DOWNLOAD_DELAY':1,
                       'CONCURRENT_REQUESTS':1}
    def start_requests(self):
        page = 1
        for format_ in self.start_configs:
            url = format_.format(page=page)
            headers['Referer'] = url
            request = scrapy.Request(url,
                                 headers = headers)
            print(request.cookies)
            yield scrapy.Request(url,
                                 headers = headers)
    def parse(self, response):
        request = checkTimeError(response)
        if request:
            yield request 
            return False
        followConfigs = choice(response.url,urlconfigs) 
        try:
            urls = S.select_content(response,followConfigs,response)
            for url in urls:
                url = response.urljoin(url)
                headers['Referer'] = url
                yield scrapy.Request(url,
                                     headers=headers,
                                     callback = self.infoParse)
        except Exception as e:
            print(response.text,e)
        nextPageConfigs = choice(response.url,pageConfigs) 
        try:
            urls = S.select_content(response,nextPageConfigs,response)
            for url in urls:
                print(url)
                url = response.urljoin(url)
                headers['Referer'] = url
                yield scrapy.Request(url,
                                     headers = headers)
        except Exception as e:
            print(response.text,e)
    def infoParse(self,response):
        request = checkTimeError(response)
        if request:
            yield request 
            return False
        __ = S.replace_invalid_html_char(response.text)
        response = response.replace(body = __)
#        print(re.findall('(?=投[^>]*?资[^>]*?方).*?<a\s*?href=\".*?show(\d+)\/',response.text,re.S))
        InfoConfigs = choice(response.url,contentsConfigs)
        items = self.configParse(InfoConfigs,response,response)
        for item in items.__iter__():
#            yield item
            print(item)
