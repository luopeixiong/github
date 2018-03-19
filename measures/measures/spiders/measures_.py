# -*- coding: utf-8 -*-
import scrapy
import random
from user_agent import generate_user_agent
from .myselector import Selector as S
import re
import time
import urllib.parse
import json
import requests
from scrapy import Selector as S1
from measures.items import MeasuresItem
s = requests.Session()

class MeasuresSpider(scrapy.Spider):
    name = "measures_"
    allowed_domains = ["szse.cn","sse.com"]
    start_urls = ["http://www.szse.cn/szseWeb/FrontController.szse?randnum={randnum}",
                  "http://query.sse.com.cn"
                  ]
    szse_page = 1
    sse_page = 1
    def start_requests(self):
        for url in self.start_urls:
            if url == "http://www.szse.cn/szseWeb/FrontController.szse?randnum={randnum}":
                randnum = random.random()
                url = "http://www.szse.cn/szseWeb/FrontController.szse?randnum={randnum}".format(randnum=randnum)
                data = {
                    'ACTIONID':'7',
                    'AJAX':'AJAX-TRUE',
                    'CATALOGID':'1759_cxda',
                    'TABKEY':'tab1',
                    'tab1PAGENO':str(self.szse_page),
#                    'tab1PAGECOUNT':'1',
#                    'tab1RECORDCOUNT':'532',
                    'REPORT_ACTION':'navigate',
                    }
                yield scrapy.FormRequest(url,
                                         formdata=data,
                                         headers={'User-Agent':generate_user_agent()},
                                         callback = self.szseparse)
            if url == "http://query.sse.com.cn":
                url = self.ssedata(self.sse_page)
                print(url)
                headers = {"Referer":"http://www.sse.com.cn/disclosure/credibility/supervision/measures/"
                           ,"user-agent":generate_user_agent()}
                yield scrapy.Request(url,
                                     headers=headers,
                                     method='GET',
                                     dont_filter = True,
                                     callback=self.sseparse)

    def ssedata(self,page):
        data = {
                "jsonCallBack":"jsonpCallback%s"%random.randint(10000,99999),
                "extTeacher":"",
                "extWTFL":"",
                "stockcode":"",
                "siteId":"28",
                "sqlId":"BS_GGLL",
                "extGGLX":"",
                "channelId":"10007,10008,10009,10010",
                "createTime":"",
                "createTimeEnd":"",
                "extGGDL":"",
                "order":"createTime|desc,stockcode|asc",
                "isPagination":"true",
                "pageHelp.pageSize":"15",
                "pageHelp.pageNo":str(page),
                "pageHelp.beginPage":str(page),
                "pageHelp.cacheSize":"1",
                "pageHelp.endPage":str(page*10+1),
                "_":str(int(time.time()*1000))
                }
        data = urllib.parse.urlencode(data)
        url = 'http://query.sse.com.cn/commonSoaQuery.do?'+data
        return url
    def szseparse(self, response):
        item = MeasuresItem()
        configs = [{'n':'股票代码','En':'stock_code','t':'xpath_first','v':'td[1]/text()','dt':''},
                   {'n':'股票名称','En':'stock_name','t':'xpath_first','v':'td[2]/text()','dt':''},
                   {'n':'处分日期','En':'Punish_date','t':'xpath_first','v':'td[3]/text()','dt':''},
                   {'n':'处分类别','En':'Punish_label','t':'xpath_first','v':'td[4]/text()','dt':''},
                   {'n':'当事人','En':'clients','t':'xpath_first','v':'td[5]/text()','dt':''},
                   {'n':'标题','En':'title','t':'xpath_first','v':'td[6]/text()','dt':''},
                   {'n':'内容','En':'contents','t':'other','v':'','dt':''},
                   {'n':'文章地址','En':'doc_website','t':'xpath_first','v':'td[7]/image/@onclick','dt':''},
                   ]
#        print(response.text)
        if self.szse_page == 1:
            self.szse_totalPages = int(re.findall("共(\d*)页",response.text)[0])
            print(self.szse_totalPages)
        for info in response.xpath("//table[@id='REPORTID_tab1']/tr[position()>1]"):
            result=dict()
            for config in configs:
                result[config['En']] = S.select_content(info, config)
            if result['doc_website']:
                result['doc_website'] = response.urljoin(re.search("open\(\'(\S*)\s?\'\)",result['doc_website']).group(1))
                name = result['doc_website'].split("/")[-1]
                if "pdf" in name:
                    result['contents'] = S.pdfparse(url = result['doc_website'])
                    if result['contents']:
                        result['contents'] = S.replace_all(result['contents'])
                elif "doc" in name:
                    result['contents'] = S.docparse(url = result['doc_website'])
                    if result['contents']:
                        result['contents'] = S.replace_all(result['contents'])
#            print(result)
            result['form'] = 'szse'
            item['result'] = result
            item['db'] = 'dbo.sse_szse_measures'
            item['keys'] = ['stock_code','Punish_date','doc_website','Punish_label']
            yield item
        if self.szse_page <self.szse_totalPages:
            self.szse_page+=1
            randnum = random.random()
            url = "http://www.szse.cn/szseWeb/FrontController.szse?randnum={randnum}".format(randnum=randnum)
            data = {
                    'ACTIONID':'7',
                    'AJAX':'AJAX-TRUE',
                    'CATALOGID':'1759_cxda',
                    'TABKEY':'tab1',
                    'tab1PAGENO':str(self.szse_page),
#                    'tab1PAGECOUNT':'1',
#                    'tab1RECORDCOUNT':'532',
                    'REPORT_ACTION':'navigate',
                    }
            yield scrapy.FormRequest(url,
                                     formdata=data,
                                     headers={'User-Agent':generate_user_agent()},
                                     callback = self.szseparse)
            
    def sseparse(self, response):
#        print(response.text)
        item = MeasuresItem()
        headers = {"Referer":"http://www.sse.com.cn/disclosure/credibility/supervision/measures/"
                           ,"user-agent":generate_user_agent()}
        Flag = True
        if "setTimeout" in response.text:
            print("try again")
            yield scrapy.Request(response.url,
                                 headers=headers,
                                 method='GET',
                                 dont_filter = True,
                                 callback=self.sseparse)
            Flag = False
        if Flag is False:
            return None
        js = json.loads(re.findall("{.*}",response.text)[0])
#        print(js)
        if self.sse_page == 1:
            self.sse_totalPages = int(js['pageHelp']['pageCount'])
        configs = [{'n':'股票代码','En':'stock_code','t':'json','v':'extSECURITY_CODE','dt':''},
                   {'n':'股票名称','En':'stock_name','t':'json','v':'extGSJC','dt':''},
                   {'n':'处分日期','En':'Punish_date','t':'json','v':'createTime','dt':''},
                   {'n':'处分类别','En':'Punish_label','t':'json','v':'extTYPE','dt':''},
                   {'n':'当事人','En':'clients','t':'json','v':'extTeacher','dt':''},
                   {'n':'标题','En':'title','t':'json','v':'docTitle','dt':''},
                   {'n':'内容','En':'contents','t':'other','v':'','dt':''},
                   {'n':'文章地址','En':'doc_website','t':'json','v':'docURL','dt':''}
                   ]
        for json_ in js['result']:
            result = dict()
#            print(json_)
            for config in configs:
                result[config['En']] = S.select_content(json_,config)
            if result['doc_website']:
                result['doc_website'] = "http://"+result['doc_website']
                
#                name = result['doc_website'].split("/")[-1]
#                print(result['doc_website'],name)
                if "pdf" in result['doc_website']:
                    result['contents'] = S.pdfparse(url=result['doc_website'])
                    if result['contents']:
                        result['contents'] = S.replace_all(result['contents'])
                elif 'doc' in result['doc_website']:
                    result['contents'] = S.docparse(url=result['doc_website'])
                    if result['contents']:
                        result['contents'] = S.replace_all(result['contents'])
                elif 'shtml' in result['doc_website']:
                    res = s.get(result['doc_website'],headers = headers)
                    res.encoding = res.apparent_encoding 
                    response_ = S1(text = res.text)
                    conf = {'n':'文本','t':'xpath_join','v':"//div[@class='allZoom']/p/text()"}
                    result['contents'] = S.select_content(response_,conf)
            if result['contents']:
                result['contents'] = S.replace_all(result['contents'])
            if hasattr(result['Punish_date'],'split'):
                result['Punish_date'] = result['Punish_date'][:10]
#            print(result)
            result['form'] = 'sse'
            item['result'] = result
            item['db'] = 'dbo.sse_szse_measures'
            item['keys'] = ['stock_code','Punish_date','doc_website','Punish_label']
            yield item
        if self.sse_page<self.sse_totalPages:
            self.sse_page+=1
            url = self.ssedata(self.sse_page)
            yield scrapy.Request(url,
                                 headers=headers,
                                 method='GET',
                                 dont_filter = True,
                                 callback=self.sseparse)