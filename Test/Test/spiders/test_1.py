# -*- coding: utf-8 -*-
import scrapy
from Test.items import TestItem
import urllib.parse
import requests
from user_agent import generate_user_agent
def cookieJar(url):
    res = requests.get(url)
    return res.cookies.get_dict()

headers = {
            'User-Agent':generate_user_agent(os=('win',)),
            'Referer':'https://www.lagou.com/gongsi/'}
class Test1Spider(scrapy.Spider):
    name = "test_1"
    start_urls = ['https://www.lagou.com/gongsi/0-0-0.json']
    def start_requests(self):
        for url in self.start_urls:
            data = {'first':'false',
                    'pn':'1',
                    'sortField':'0',
                    'havemark':'0',
                    }
            yield scrapy.FormRequest(url,
                dont_filter=True,
                formdata=data,
                callback=self.parse1,
                headers=headers)

    def parse(self, response):
        item = TestItem()
        item['result']  = 111
        yield item
    def parse1(self, response):
        print(response.text)

a = [1,2,3]

def func(a:'列表对象')->'输出list':
    '''
    @ params a '列表对象'
    return '输出list'
    '''
    a.append(4)
    return a
print(func.__doc__)

func(a)
print(a)