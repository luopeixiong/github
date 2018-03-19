# -*- coding: utf-8 -*-
import scrapy
from user_agent import generate_user_agent as ua
from .myselector import Selector as S
from . import config  as Con
import re

class HowbuySpider(scrapy.Spider):
    name = "howbuy_"
    allowed_domains = ["howbuy.com"]
    start_urls = [
                'https://www.howbuy.com/fund/fundranking/',
                'https://www.howbuy.com/fund/company/',
                'https://www.howbuy.com/fund/manager/',
                'https://simu.howbuy.com/mlboard.htm',
                'https://simu.howbuy.com/manager/',
                'https://simu.howbuy.com/company/'
                ]
    cookies = {"simu_qualified_v2": "5"}
    def start_requests(self):
        page = 1
        for url in self.start_urls:
            #Get页面
            if url in [
                'https://www.howbuy.com/fund/fundranking/',
                'https://www.howbuy.com/fund/company/',
                'https://www.howbuy.com/fund/manager/']:
                yield scrapy.Request(url,
                                     method='GET',
                                     headers={'User-Agent':ua(os=('win','mac','linux'))},
                                     cookies = self.cookies,
                                     priority=1,
                                     meta={'page':page},
                                     )
            #post页面
            if url in ['https://simu.howbuy.com/mlboard.htm',
                        'https://simu.howbuy.com/manager/',
                        'https://simu.howbuy.com/company/'
                        ]:
                page = 1
                data = Con.changeData(url,page)
                yield scrapy.FormRequest(url,
                                      method='POST',
                                     headers={'User-Agent':ua(os=('win','mac','linux'))},
                                     cookies = self.cookies,
                                     formdata = data,
                                     priority=1,
                                     meta={'page':page},
                                     )
    def parse(self, response):
        page = response.meta['page']
        configs = Con.parseChioce(response.url)
        if page == 1:
            #构造allpage
            allPage = re.search('共(\d+)页',response.text)
            if allPage:
                allPage = int(allPage.group(1)) if allPage.group(1).isdigit() else 1
            else:
                allPage = 1
        else:
            allPage = response.meta['allPage']
        if configs['htmlreplace']:
            #改造html
            strs = Con.replaceHtml(response.text, configs['htmlreplace'])
            response_ = scrapy.Selector(text = strs)
        else:
            response_ = response
        kw = S.select_content(response_, configs['geturl'], response)
        kw = set(kw)
#        
#        print(kw)
        if kw:
            if configs['method'] == 'get':
                for url in kw:
                    url = configs['format'].format(url)
                    yield scrapy.Request(url,
                                        headers={'User-Agent':ua(os=('win','mac','linux'))},
                                        cookies = self.cookies,
                                        priority=1,
                                        callback = eval(configs['callback'])
                                        )
        #下一页
        if page<allPage:
            page+=1
            
            data = Con.changeData(response.url,*eval('page,20,allPage'))
            yield scrapy.FormRequest(response.url,
                               formdata=data,
                               headers={'User-Agent':ua(os=('win','mac','linux'))},
                               cookies = self.cookies,
                               priority=1,
                               meta={'page':page,'allPage':allPage},
                               
                               )
    def infoParse(self, response):
#        print(response.text)
        _configs = Con.configIngochange(response.url)
        for configs in _configs:
            if configs['list']['v']:
                res = S.select_content(response, configs['list'],response)
            else:
                res = [response]
            for _ in res:
                result = dict()
                for config in configs['data']:
                    k = config['En']
                    result[k] = S.select_content(_ , config, response)
                    result[k] = S.replace_invalid_char(result[k])
                print(result)