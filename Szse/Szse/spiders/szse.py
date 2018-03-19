# -*- coding: utf-8 -*-
import scrapy
import urllib.parse
import sys
from user_agent import generate_user_agent as ua
import re
from myselector import Selector as S
import datetime
from Help import *
from ownerconfigs import *
import random
from Szse.items import SzseItem
import json




def getTotalPage(response):
    page = response.meta['page']    
    if page == 1:
        totalpage = int(re.search("naviboxid\'\s*?,\s*?(\d+)\s*?,",response.text).group(1)) if re.search("naviboxid\'\s*?,\s*?(\d+)\s*?,",response.text) else 1
        counts = int(re.search("gotoReportPageNoByTextBox\([^\)]*?,(\d+?)\)",response.text).group(1)) if re.search("gotoReportPageNoByTextBox\([^\)]*?,(\d+?)\)",response.text) else 1
    else:
        totalpage = response.meta['totalpage']
        counts = response.meta['counts']
    return page,totalpage,counts
class SzseSpider(scrapy.Spider, other):
    name = "szse"
#    allowed_domains = ["szse.cn"]
    start_urls = [
                ###股票，基金，证券
                 'http://www.szse.cn/szseWeb/FrontController.szse',
#                  ##融资融券信息 --表较大，后续修改为每次爬取近1个月数据
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1837_xxpl&TABKEY=tab1&txtDate={date}&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate',
                  ##在任董事信息 --表较小
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1900&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate',
                 ###在任董秘信息 --表较小
                  'http://www.szse1.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1901&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate',
                  ##董秘资格培训信息 --表较小
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1901&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate',
                  ##董事人才库信息 --表较小
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1900&TABKEY=tab3&tab3PAGENO={page}&tab3PAGECOUNT=&tab3RECORDCOUNT=&REPORT_ACTION=navigate',
                  ##处罚信息 --表较小
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1759_cxda&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate',
                  ##中介机构处罚与处分信息  --表较小
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1903_detail&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate',
                  ##解除限售总体情况 --表较小
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1902&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate',
                  ##持有股份占总股本1%以上股东解除限售情况 --表较小
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1902&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate',
                  ##持有解除限售存量股份占总股本5%以上股东减持1% --表较小
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1902&TABKEY=tab3&tab3PAGENO={page}&tab3PAGECOUNT=&tab3RECORDCOUNT=&REPORT_ACTION=navigate',
                  ##基金申购回购信息 -- 需要插入数据量大--第一次使用全站爬取,后续修改为每次爬取前几页
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=sgshqd&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate',
                  ##资产计划份额转让成交信息 -- 表较小
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1931_zcjhcjxx&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&report_action=navigate',
                  ##资产计划份额转让产品信息 -- 表较小
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1839_zcjhcpxx&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate',
                  ##停复牌信息
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1798&TABKEY=tab1&txtKsrq=2000-01-01&txtZzrq=%s&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate'%datetime.datetime.now().strftime("%Y-%m-%d"),
                  ###上市公司全称变更
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=SSGSGMXX&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate',
                  ###上市公司简称变更
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=SSGSGMXX&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate',
                  ###暂停上市公司
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1793_ssgs&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate',
                  ###终止上市公司
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1793_ssgs&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate',
                  #项目进度信息
                  'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=xmjdxx&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate',
                  ]
    custom_settings = {'CONCURRENT_REQUESTS':16,
                       'LOG_LEVEL':'INFO'}
    
    def start_requests(self):
        self.Start = {
                    '1110':self.colistparse,
                    '1105':self.fundlistparse,
                    '1273':self.zqparse,
                      }

        for _url in self.start_urls:
            page=1
            if _url == 'http://www.szse.cn/szseWeb/FrontController.szse':
                for CATALOGID,callback in self.Start.items():
                   postdata = szse_data(page,CATALOGID)
                   meta = {'CATALOGID':CATALOGID,'page':page,'_url':_url}
                   yield scrapy.Request(_url,callback=callback,method='POST',headers=hdr(),meta=meta,body=postdata)
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1837_xxpl&TABKEY=tab1&txtDate={date}&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate':
                dateformat = "%Y-%m-%d"
                today = datetime.datetime.now().strftime("%Y%m%d")
                datelist = S.datelist('20100101',today,dateformat)
                datelist.reverse()
                
                for date in datelist:
                    url = _url.format(page=page,date=date)
                    yield scrapy.Request(url,
                                         headers = hdr(),
                                         meta = {'page':page,'date':date},
                                         callback = self.rzrqparse,
                                         )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1900&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate':
                url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1900&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate'.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.zrdsparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1901&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.zrdmparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1901&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.dmzgpxdaparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1900&TABKEY=tab3&tab3PAGENO={page}&tab3PAGECOUNT=&tab3RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.dsrckparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1759_cxda&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.chufaparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1903_detail&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.zhongjiechufaparse,
                                     )
            
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1902&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.jiechuxianshoufaparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1902&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.jiechuxianshou1perfaparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1902&TABKEY=tab3&tab3PAGENO={page}&tab3PAGECOUNT=&tab3RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.jiechuxianshou5perfaparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=sgshqd&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.sghgqdparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1931_zcjhcjxx&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&report_action=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.zcjhcjxxparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1839_zcjhcpxx&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.zcjhcpxxparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1798&TABKEY=tab1&txtKsrq=2000-01-01&txtZzrq=%s&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate'%datetime.datetime.now().strftime("%Y-%m-%d"):
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.tfpxxparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=SSGSGMXX&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.fullnamechangeparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=SSGSGMXX&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.shortnamechangeparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1793_ssgs&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.suspendListingparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1793_ssgs&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT=&tab2RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.StopListingparse,
                                     )
            elif _url == 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=xmjdxx&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT=&tab1RECORDCOUNT=&REPORT_ACTION=navigate':
                url = _url.format(page=page)
                yield scrapy.Request(url,
                                     headers = hdr(),
                                     meta = {'page':page},
                                     callback = self.projparse,
                                     )

                    

    def projparse(self, response):
        urls = response.xpath('//table[@id="REPORTID_tab1"]//@onclick').extract()
        for url in urls:
            url_ = 'http://www.szse.cn'+re.search("\'(.*?)\'",url).group(1)
            yield scrapy.Request(url_,
                                 headers = hdr(),
                                 callback = self.projInfoparse,
                                 priority=1)
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=xmjdxx&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'
            url = url.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.projparse,
                                 priority=0) 
    def projInfoparse(self, response):
        items = self.configParse(projInfoConfigs,response,response)
        for item in items.__iter__():
            _item = item
            _item['result']['ProspectusUrl'] = re.search("\((.*?)\)",_item['result']['ProspectusUrl']).group(1).replace('+encodeURIComponent(','') if _item['result']['ProspectusUrl'] and hasattr(re.search("\((.*?)\)",_item['result']['ProspectusUrl']),'group') else None
            _item['result']['FeedbackUrl'] = re.search("\((.*?)\)",_item['result']['FeedbackUrl']).group(1).replace('+encodeURIComponent(','') if _item['result']['FeedbackUrl'] and hasattr(re.search("\((.*?)\)",_item['result']['FeedbackUrl']),'group') else None
#           文本太大 一篇10几万字。。。
#            _item['result']['ProspectusContent'] = S._txtparse('http://www.szse.cn'+_item['result']['ProspectusUrl']) if _item['result']['ProspectusUrl'] else None
#            _item['result']['FeedbackContent'] = S._txtparse('http://www.szse.cn'+_item['result']['FeedbackUrl']) if _item['result']['FeedbackUrl']  else None
            yield _item
    def StopListingparse(self, response):
        items = self.configParse(StopListingConfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1793_ssgs&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT={totalpage}&tab2RECORDCOUNT={counts}&REPORT_ACTION=navigate'
            url = url.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.suspendListingparse,
                                 priority=1) 
    def suspendListingparse(self, response):
        items = self.configParse(suspendListingConfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1793_ssgs&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'
            url = url.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.suspendListingparse,
                                 priority=1) 
    def shortnamechangeparse(self, response):
        items = self.configParse(shortnamechangeConfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=SSGSGMXX&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT={totalpage}&tab2RECORDCOUNT={counts}&REPORT_ACTION=navigate'
            url = url.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.shortnamechangeparse,
                                 priority=1) 
    def fullnamechangeparse(self,response):
        items = self.configParse(fullnamechangeConfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=SSGSGMXX&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'
            url = url.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.fullnamechangeparse,
                                 priority=1) 
    def tfpxxparse(self, response):
        items = self.configParse(tfpxxConfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1798&TABKEY=tab1&txtKsrq=2000-01-01&txtZzrq=%s&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'%datetime.datetime.now().strftime("%Y-%m-%d")
            url = url.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.tfpxxparse,
                                 priority=1) 
    def zcjhcpxxparse(self, response):
        items = self.configParse(zcjhcpxxConfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1839_zcjhcpxx&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.zcjhcpxxparse,
                                 priority=1) 
    def zcjhcjxxparse(self, response):
        items = self.configParse(zcjhcjxxConfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1931_zcjhcjxx&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&report_action=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.zcjhcjxxparse,
                                 priority=1) 
    def sghgqdparse(self, response):
        filenames = re.findall("html\?filename=(\w+)\'",response.text)
        for filename in filenames:
            _url = 'http://www.szse.cn/szseWeb/common/szse/files/text/etf/{filename}.txt'.format(filename=filename)
            yield scrapy.Request(_url,
                                 headers = hdr(),
                                 callback = self.sghgqdInfoParse,
                                 priority=1) 
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=sgshqd&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.sghgqdparse,
                                 priority=1) 
    def sghgqdInfoParse(self, response):
#        print(response.text)
        items = self.configParse(sghgqdInfoConfigs,response,response)
        for item in items.__iter__():
            yield item
        results = re.compile("(?P<code>\d{6})\s{5,10}(?P<name>\S+)\s{5,13}?(?P<shares>\S+)\s{9,14}(?P<label>\S+)\s{11,21}(?P<Ritio>(?:[0-9\.%]{6}|\s*?))\s*(?P<shendai>(?:[0-9\.,]*?|\s*?))\s*(?P<shuhui>(?:[0-9\.,]*?|\s*?))\s*(?P<market>\w+)\r").finditer(response.text)
        regDate = item['result']['regDate']
        regcode = item['result']['fundCode']
        for _result in results:
            _result = _result.groupdict()
            _result['regDate'] = regDate
            _result['regcode'] = regcode
            items = self.configParse(sghgqdInfo2Configs,_result,response)
            for item in items.__iter__():
                yield item
                
    def jiechuxianshou5perfaparse(self, response):
        items = self.configParse(jiechuxianshou5perConfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1902&TABKEY=tab3&tab3PAGENO={page}&tab3PAGECOUNT={totalpage}&tab3RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.jiechuxianshou5perfaparse,
                                 priority=1) 
    def jiechuxianshou1perfaparse(self, response):
        items = self.configParse(jiechuxianshou1perConfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1902&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT={totalpage}&tab2RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.jiechuxianshou1perfaparse,
                                 priority=1)   
    def jiechuxianshoufaparse(self, response):
        items = self.configParse(jiechuxianshouConfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1902&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.jiechuxianshoufaparse,
                                 priority=1)   
    def zhongjiechufaparse(self, response):
        items = self.configParse(zhongjiechufaConfigs,response,response)
        for item in items.__iter__():
            _item = item
            url = re.search("\((.*?)\)",_item['result']['contents']).group(1).strip()
            url = response.urljoin(url)
            try:
                content = S._txtparse(url)
                content = S.replace_invalid_char(content)
            except:
                content = None
            _item['result']['contents'] = content
            _item['result']['url'] = url
            yield _item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1903_detail&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.zhongjiechufaparse,
                                 priority=1)
    def chufaparse(self, response):
        items = self.configParse(chufaConfigs,response,response)
        for item in items.__iter__():
            _item = item
            url = re.search("\((.*?)\)",_item['result']['contents']).group(1).strip()
            url = response.urljoin(url)
            try:
                content = S._txtparse(url)
                content = S.replace_invalid_char(content)
            except:
                content = None
            _item['result']['contents'] = content
            _item['result']['url'] = url
            yield _item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1759_cxda&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.chufaparse,
                                 priority=1)
    def dsrckparse(self, response):
        
        pids = re.compile('tab1&id=(\d+)').findall(response.text)
        for pid in pids:
            _url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&SOURCEURL=/szseWeb/FrontController.szse*_QUESTION_*ACTIONID=7*_AND_*AJAX=AJAX-TRUE*_AND_*CATALOGID=1900*_AND_*TABKEY=tab3*_AND_*tab3PAGENO=*_AND_*tab3PAGECOUNT=*_AND_*tab3RECORDCOUNT=&SOURCECATALOGID=1900&CATALOGID=1900_detail&TABKEY=tab1&id={pid}'.format(pid=pid)
            yield scrapy.Request(_url,
                                 headers = hdr(),
                                 callback = self.dsrckInfoparse,
                                 priority=1)    
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1900&TABKEY=tab3&tab3PAGENO={page}&tab3PAGECOUNT=&tab3RECORDCOUNT=&REPORT_ACTION=navigate'.format(page=page)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.dsrckparse,
                                 priority=1)
    def dsrckInfoparse(self, response):
        items = self.configParse(dsrckInfoConfigs,response,response)
        for item in items.__iter__():
            yield item
    def dmzgpxdaparse(self , response):
        items = self.configParse(dmzgpxdaconfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1901&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT={totalpage}&tab2RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.dmzgpxdaparse,
                                 priority=1)    
    def zrdmparse(self, response):
        items = self.configParse(zrdmConfigs,response,response)
        for item in items.__iter__():
                yield item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1901&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.zrdmparse,
                                 priority=1)    
    def zrdsparse(self, response):
        items = self.configParse(zrdsConfigs,response,response)
        for item in items.__iter__():
            _item = item
            result = _item['result']
            try:
                sy = re.search("sy=(\d+)",result['ins']).group(1)
                GSDM = re.search("GSDM=(\d+)",result['ins']).group(1)
                url = 'http://www.szse.cn//szseWeb/common/szse/report/ViewResume.jsp?sy={sy}&GSDM={GSDM}'.format(sy=sy,GSDM=GSDM)
                headers=hdr()
                yield scrapy.Request(url,callback=self.zrdsinfoparse,headers=headers,meta={'result':result,'db':_item['db'],'keys':_item['keys']})
            except Exception as e:
                yield _item
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1900&TABKEY=tab2&tab2PAGENO={page}&tab2PAGECOUNT={totalpage}&tab2RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.zrdsparse,
                                 priority=1)    
    def zrdsinfoparse(self, response):
        item = SzseItem()
        result = response.meta['result']
        result['ins'] = "".join(response.xpath('//span[@id="ViewResume1_lblContent"]/text()').extract())
        result['ins'] = S.replace_invalid_char(result['ins'])
        item['result'] = result
        item['db'] = response.meta['db']
        item['keys'] = response.meta['keys']
        yield item
    
    def rzrqparse(self, response):
        items = self.configParse(rzrqConfigs,response,response)
        for item in items.__iter__():
            yield item
        date = response.meta['date']
        page,totalpage,counts = getTotalPage(response)
        if page<=totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1837_xxpl&TABKEY=tab1&txtDate={date}&tab2PAGENO={page}&tab2PAGECOUNT={totalpage}&tab2RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts,date=date)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'date':date,'totalpage':totalpage,'counts':counts
                                        },
                                 callback = self.rzrqparse,
                                 priority=1)
    def colistparse(self, response):
        for code in response.xpath('//table[@class="cls-data-table-common cls-data-table"]//tr/td[1]/a/u/text()').extract():
            url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&SOURCEURL=/szseWeb/FrontController.szse*_QUESTION_*ACTIONID=7*_AND_*AJAX=AJAX-TRUE*_AND_*CATALOGID=1110*_AND_*TABKEY=tab1*_AND_*tab1PAGENO=2*_AND_*tab1PAGECOUNT=206*_AND_*tab1RECORDCOUNT=2056&SOURCECATALOGID=1110&CATALOGID=1743_detail_sme&TABKEY=tab1&DM=%s&site=main'%code
            yield scrapy.Request(url,callback = self.stockinfoParse,meta={'code':code})
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            _url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1110&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(_url,
                                 callback=self.colistparse,
                                 method='GET',
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 headers=hdr()
                                 )
    def stockinfoParse(self, response):
       items = self.configParse(stockinfoParse_configs,response,response)
       for item in items.__iter__():
           yield item
    
    def fundlistparse(self,response):
        items = self.configParse(fundConfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<=totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1105&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.fundlistparse,
                                 priority=1)
    def zqparse(self,response):
        items = self.configParse(zqConfigs,response,response)
        for item in items.__iter__():
            yield item
        page,totalpage,counts = getTotalPage(response)
        if page<=totalpage:
            page+=1
            url= 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-TRUE&CATALOGID=1273&TABKEY=tab1&tab1PAGENO={page}&tab1PAGECOUNT={totalpage}&tab1RECORDCOUNT={counts}&REPORT_ACTION=navigate'.format(page=page,totalpage=totalpage,counts=counts)
            yield scrapy.Request(url,
                                 headers = hdr(),
                                 meta = {'page':page,'totalpage':totalpage,'counts':counts},
                                 callback = self.zqparse,
                                 priority=1)
    ###需要分日期        
    def kzzparse(self,response):
        CATALOGID = response.meta['CATALOGID']
        _url = response.meta['_url']
        page,totalpage,counts = getTotalPage(response)
        if page<totalpage:
            page+=1
            postdata = szse_data(page,CATALOGID)
            meta = {'CATALOGID':CATALOGID,'page':page,'_url':_url,'totalpage':totalpage,'counts':counts}
            callback = self.Start[CATALOGID]
            yield scrapy.Request(_url,callback=callback,method='POST',headers=hdr(),meta=meta,body=postdata)