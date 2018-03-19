# -*- coding:utf-8 -*-

import time,random,json,re,os,sys,time
import scrapy,xlrd
from numbers import Real
from user_agent import generate_user_agent
from SpiderHelp import SpiderHelp
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


class Headers(object):
    def __init__(self,os=('win',),content_type=1):
        self.os = os
        self.content_type = 'application/x-www-form-urlencoded' if content_type else 'application/json'

    @property
    def choice(self):
        return {'User-Agent':generate_user_agent(os=self.os),
                'Content-Type': self.content_type,
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Accept-Encoding': 'gzip, deflate', 
                'Connection': 'keep-alive',
                'Accept': '*/*'}

headers = Headers()

class Item(scrapy.Item):
    result = scrapy.Field()

class TrcSpider(scrapy.Spider):
    name = 'trc'
    start_urls = ['http://www.chinatrc.com.cn/zhongxindeng-web/product/index/t-c-x-f-g-rs-re-ps-pe-p%s']
    custom_settings = {'ITEM_PIPELINES':{'DistributedSpider.pipelines.CsvPipeline': 300},}

    def start_requests(self):
        for url in self.start_urls:
            fmt = url
            url %= 1
            yield scrapy.Request(url,
                headers=headers.choice,
                meta={'fmt':fmt},
                callback=self.parse)

    def parse(self, response):
        JS = json.loads(response.text)
        total = JS['count']
        for page in range(1,int(total/10)+1):
            yield scrapy.Request(response.meta['fmt'] % page,
                headers=headers.choice,
                dont_filter=True,
                callback=self.get_json)

    def ctime_to_date(self, timestamp):
        time_local = time.localtime(timestamp)
        dt = time.strftime("%Y-%m-%d",time_local)
        return dt

    def get_json(self, response):
        if 'publicityList' in response.text:
            JS = json.loads(response.text)
            for content in JS['publicityList']:
                result = {}
                result['projectId'] = content['projectId']
                result['isOn'] = content['isOn']
                result['trustProductName'] = content['trustProductName']
                result['proectIssueCode'] = content['proectIssueCode']
                result['trustCompanyName'] = content['trustCompanyName']
                result['trustCompanyShortName'] = content['trustCompanyShortName']
                result['trustTremType'] = content['trustTremType']
                result['trustPropertyApplicationDesc'] = content['trustPropertyApplicationDesc']
                result['trustPropertyManagementDesc'] = content['trustPropertyManagementDesc']
                result['issueCodeDate'] = self.ctime_to_date(int(content['issueCodeDate']['time']/1000))
                result['publicityTime'] = self.ctime_to_date(int(content['publicityTime']['time']/1000))
                result['registrationTime'] = self.ctime_to_date(int(content['registrationTime']['time']/1000))
                item = Item()
                item['result'] = result
                yield item
        else:
            yield response.request



