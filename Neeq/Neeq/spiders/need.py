# -*- coding: utf-8 -*-
import scrapy
import time
from user_agent import generate_user_agent
import json
import re
from .myselector import Selector as S
from Neeq.items import NeeqItem
from .configs import Configs as C


class NeedSpider(scrapy.Spider):
    name = "need"
    allowed_domains = ["www.neeq.com.cn"]
    start_urls = ['http://www.neeq.com.cn/nqxxController/nqxx.do']
    page = 0
    def made_data(self,page):
        data = {'page':str(page),
                'typejb':'T',
                'xxzqdm':'',
                'xxzrlx':'',
                'xxhyzl':'',
                'xxssdq':'',
                'sortfield':'xxzqdm',
                'sorttype':'asc',
                'dicXxzbqs':'',
                'xxfcbj':'',
                '_':str(int(time.time()*1000))}
        return data
    def start_requests(self):
        for url in self.start_urls:
            headers = {'User-Agent':generate_user_agent()}
            if url == 'http://www.neeq.com.cn/nqxxController/nqxx.do':
                data = self.made_data(self.page)
                yield scrapy.FormRequest(url,
                                         formdata = data,
                                         headers = headers,
                                         callback = self.ListedCompanyParse
                                         )
    def parse(self, response):
        pass
    
    def ListedCompanyParse(self, response):
        JS = json.loads(re.search("{.*}",response.text,re.M).group(0))
        headers = {'User-Agent':generate_user_agent()}
        if self.page == 0:
            self.TotalPages = JS['totalPages']
            print(self.TotalPages)
        configs = C().configs
        for json_ in JS[configs['list']['v']]:
            result = dict()
            for config in configs['data']:
                result[config['En']] = json_[config['v']]
            data = {'zqdm':result['Company_code'],
                    '_':str(int(time.time()*1000))}
            yield scrapy.FormRequest('http://www.neeq.com.cn/nqhqController/detailCompany.do',
                                     formdata = data,
                                     headers = headers,
                                     callback = self.ListedCompanyInfoParse)
        if self.page<=self.TotalPages:
            self.page+=1
            nextdata = self.made_data(self.page)
            url = 'http://www.neeq.com.cn/nqxxController/nqxx.do'
            yield scrapy.FormRequest(url,
                                     formdata = nextdata,
                                     headers = headers,
                                     callback = self.ListedCompanyParse,
                                     
                                     )
    def ListedCompanyInfoParse(self, response):
        """
        挂牌公司parse
        """
        JS = json.loads(re.search("{.*}",response.text,re.M).group(0))
#        print(JS)
        item = NeeqItem()
        configs1 = C().configs1
        configs2 = C().configs2
        configs3 = C().configs3
        configs4 = C().configs4
        json_ = JS[configs1['list']['v']]
        result = dict()
        for config in configs1['data']:
            result[config['En']] = S.select_content(json_, config)
#        print(result)
        item['result'] = result
        item['db'] = 'baseinfo'
        item['keys'] = []
        code = result['code']
        yield item
        json_ = JS[configs4['list']['v']]
        result = dict()
        for config in configs4['data']:
            result[config['En']] = S.select_content(json_, config)
#            print(result)
        result['code'] = code
        item['result'] = result
        item['db'] = 'finance'
        item['keys'] = []
        yield item
        for json_ in JS[configs2['list']['v']]:
            result = dict()
            for config in configs2['data']:
                result[config['En']] = S.select_content(json_, config)
#            print(result)
            result['code'] = code
            item['result'] = result
            item['db'] = 'executives'
            item['keys'] = []
            yield item
        
        for json_ in JS[configs3['list']['v']]:
            result = dict()
            for config in configs3['data']:
                result[config['En']] = S.select_content(json_, config)
#            print(result)
            result['code'] = code
            item['result'] = result
            item['db'] = 'topTenHolders'
            item['keys'] = []
            yield item        