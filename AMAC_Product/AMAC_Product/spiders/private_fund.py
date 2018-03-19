# -*- coding: utf-8 -*-
import scrapy
import random
import urllib.parse
import json
from user_agent import generate_user_agent
from AMAC_Product.items import AmacProductItem
import time
import re
from scrapy import  Selector as S2
from .myselector import  Selector as S
import requests
from scrapy.cmdline import execute
import os
s = requests.Session()

class PrivateFundSpider(scrapy.Spider):
    name = "private_fund"
    allowed_domains = ["amac.org.cn"]
    custom_settings = {
                        "CONCURRENT_REQUESTS": 32 ,  #并发数
                        # "CONCURRENT_REQUESTS_PER_DOMAIN": 2 ,#网站并发数
                        # "CONCURRENT_REQUESTS_PER_IP": 2   ,#单IP并发数
                        # "DOWNLOAD_DELAY":1
                        }
    start_urls = ["http://fo.amac.org.cn/amac/allNotice.do-3",
                  "http://fo.amac.org.cn/amac/allNotice.do-2",
                  "http://fo.amac.org.cn/amac/allNotice.do-1",
                  "http://www.amac.org.cn/xxgs/cyjggs/hjsws/382718.shtml",
                  "http://www.amac.org.cn/xxgs/cyjggs/lssws/382717.shtml",
                  "http://www.amac.org.cn/xxgs/cyjggs/jjpjjg/382715.shtml",
                  "http://www.amac.org.cn/xxgs/zhgs/382728.shtml",
                  "http://www.amac.org.cn/xxgs/cyjggs/zfjsjg/382716.shtml",
                  "http://www.amac.org.cn/xxgs/cyjggs/jjxsjg/382714.shtml",
                  "http://person.amac.org.cn/pages/registration/train-line-register!list.action",
                  "http://ba.amac.org.cn/pages/amacWeb/user!list.action-2",
                  "http://ba.amac.org.cn/pages/amacWeb/ab-special-plan!list.action",
                  "http://gs.amac.org.cn/amac-infodisc/api/fund/account",
                  "http://gs.amac.org.cn/amac-infodisc/api/aoin/product",
                  "http://gs.amac.org.cn/amac-infodisc/api/pof/fund",
                  "http://ba.amac.org.cn/pages/amacWeb/user!list.action-1"]
    rand = "{:1<18}".format(str(random.random()))
    rand1 = "{:1<18}".format(str(random.random()))
    rand2 = "{:1<18}".format(str(random.random()))
    #私募基金管理人基金产品 爬虫post设置
    page = 0
    offset = 20
    #证券公司私募产品 爬虫post设置
    page1 = 1
    size1 = 50
    #证券公司直投基金 爬虫post设置
    page2 = 0
    offset2 = 20
    #基金专户产品  爬虫post设置
    page3 = 0
    offset3 = 20
    #资产支持专项计划 爬虫post设置
    page4 = 1
    size4 = 50
    #期货资产管理计划 爬虫POST设置
    page5 = 1
    size5 = 50
    #基金从业人员资格信息--机构基本信息页 爬虫post设置
    page6 = 1
    size6 = 10
    fundUrl = "http://gs.amac.org.cn/amac-infodisc/res/pof/fund/{fundID}.html"
    url = "http://gs.amac.org.cn/amac-infodisc/res/pof/fund/index.html"
    headers1 = {"User-Agent":generate_user_agent(),
               "Accept":"application/json, text/javascript, */*; q=0.01"}
    headers = {"User-Agent":generate_user_agent(),
               "Content-Type":"application/json",
               "Accept":"application/json, text/javascript, */*; q=0.01"}
    
    urlencodeheaders = {"User-Agent":generate_user_agent(),
                       "Content-Type":"application/json",
                       "Accept":"application/json, text/javascript, */*; q=0.01",
                       'content-type':'application/x-www-form-urlencoded',
                        "Referer":"http://person.amac.org.cn/pages/registration/amac-publicity-report.html"}
    @staticmethod
    def madedata(page,offset,rand):
        data = {"rand":rand,
                "page":page,
                "size":offset}
        urlencode = urllib.parse.urlencode(data)
        return "?"+urlencode
    @staticmethod
    def madedata2(page,offset):
        data = {
                "filter_LIKES_CPMC":"",
                "filter_LIKES_GLJG":"",
                "filter_LIKES_CPBM":"",
                "filter_GES_SLRQ":"",
                "filter_LES_SLRQ":"",
                "page.searchFileName":"publicity_web",
                "page.sqlKey":"PAGE_PUBLICITY_WEB",
                "page.sqlCKey":"SIZE_PUBLICITY_WEB",
                "_search":"false",
                "nd":str(int(time.time())*1000),
                "page.pageSize":str(offset),
                "page.pageNo":str(page),
                "page.orderBy":"SLRQ",
                "page.order":"desc"
                }
        
        return data

    @staticmethod
    def madedata3(page, offset):
        data = {
            'filter_LIKES_ASPI_NAME':'',
            'filter_GES_AT_AUDIT_DATE':'',
            'filter_LES_AT_AUDIT_DATE':'',
            'page.searchFileName':'publicity_abs_web',
            'page.sqlKey':'PAGE_ABS_PUBLICITY_WEB',
            'page.sqlCKey':'SIZE_ABS_PUBLICITY_WEB',
            '_search':'false',
            'nd':str(int(time.time())*1000),
            'page.pageSize':str(offset),
            'page.pageNo':str(page),
            'page.orderBy':'AT_AUDIT_DATE',
            'page.order':'desc'
                }

        return data

    @staticmethod
    def madedata4(page, offset):
        data = {'filter_LIKES_MPI_NAME':'',
                'filter_LIKES_AOI_NAME':'',
                'filter_LIKES_MPI_PRODUCT_CODE':'',
                'filter_GES_MPI_CREATE_DATE':'',
                'filter_LES_MPI_CREATE_DATE':'',
                'page.searchFileName':'publicity_web',
                'page.sqlKey':'PAGE_QH_PUBLICITY_WEB',
                'page.sqlCKey':'SIZE_QH_PUBLICITY_WEB',
                '_search':'false',
                'nd':str(int(time.time())*1000),
                'page.pageSize':str(offset),
                'page.pageNo':str(page),
                'page.orderBy':'MPI_CREATE_DATE',
                'page.order':'desc'}
        return data

    @staticmethod
    def madedata6(page, offset):
        data = {
                'filter_EQS_OTC_ID': '05',
                'filter_LIKES_AOI_NAME':'',
                'page.searchFileName':'registration',
                'page.sqlKey': 'SELECT_LINE_PERSON_LIST',
                'page.sqlCKey': 'SELECT_LINE_PERSON_SIZE',
                '_search': 'false',
                'nd': str(int(time.time())*1000),
                'page.pageSize': str(offset),
                'page.pageNo': str(page),
                'page.orderBy': 'AOI.AOI_NAME',
                'page.order': 'desc'
                }
        return data

    @staticmethod
    def madedata7(t,currentpage,gsid=''):
        data = {'currentPage':str(currentpage),
                'mname':'listNoticeForm',
                'GSJGMC':'',
                'GSFWLX':t,
                'GSID':gsid}
        return data

    @staticmethod
    def madedata8(t,currentpage,gsid):
        data = {'currentPage': str(currentpage),
                'mname': 'viewNoticeForm',
                'GSJGMC': '',
                'GSFWLX': t,
                'GSID': gsid}
        return data
    def start_requests(self):
        for url in self.start_urls:#[13:14]
            # print(url)
            if url == "http://gs.amac.org.cn/amac-infodisc/api/pof/fund":
                url = "http://gs.amac.org.cn/amac-infodisc/api/pof/fund"+self.madedata(self.page,self.offset,self.rand)
                data = {}
                yield scrapy.Request(url,
                                     method = "POST",
                                     body = json.dumps(data),
                                     headers = self.headers,
                                     callback=self.parse
                                     )
            if url == "http://ba.amac.org.cn/pages/amacWeb/user!list.action-1":
                data = self.madedata2(self.page1,self.size1)
                yield scrapy.FormRequest("http://ba.amac.org.cn/pages/amacWeb/user!list.action",
                                         headers = self.headers1,
                                         formdata = data,
                                         method = "POST",
                                         callback = self.parse2)
            elif url == "http://gs.amac.org.cn/amac-infodisc/api/aoin/product":
                url = url+self.madedata(self.page2,self.offset2,self.rand1)
                data = {}
                yield scrapy.Request(url,
                                     method = "POST",
                                     body = json.dumps(data),
                                     headers = self.headers,
                                     callback = self.parse3
                                     )
            elif url == "http://gs.amac.org.cn/amac-infodisc/api/fund/account":
                url = url+self.madedata(self.page3,self.offset3,self.rand2)
                data = {}
#                print(url,data)
                yield scrapy.Request(url,
                                     method = "POST",
                                     body = json.dumps(data),
                                     headers = self.headers,
                                     callback = self.parse4
                                     )
            elif url == "http://ba.amac.org.cn/pages/amacWeb/ab-special-plan!list.action":
                data = self.madedata3(self.page4, self.size4)
                yield scrapy.FormRequest("http://ba.amac.org.cn/pages/amacWeb/ab-special-plan!list.action",
                                         headers=self.headers1,
                                         formdata=data,
                                         method="POST",
                                         callback=self.parse5)
            elif url == "http://ba.amac.org.cn/pages/amacWeb/user!list.action-2":
                data = self.madedata4(self.page5, self.size5)
                yield scrapy.FormRequest("http://ba.amac.org.cn/pages/amacWeb/user!list.action",
                                         headers=self.headers1,
                                         formdata=data,
                                         method="POST",
                                         callback=self.parse6)
#            elif url == "http://person.amac.org.cn/pages/registration/train-line-register!list.action":
#                data = self.madedata6(self.page6,self.size6)
#                # data = urllib.parse.urlencode(data)
#                yield scrapy.FormRequest("http://person.amac.org.cn/pages/registration/train-line-register!list.action",
#                                         headers=self.urlencodeheaders,
#                                         formdata=data,
#                                         method="POST",
#                                         callback=self.parse7)
#            elif url  == 'http://www.amac.org.cn/xxgs/cyjggs/jjxsjg/382714.shtml':
#                yield scrapy.Request(url,
#                                     headers = self.headers1,
#                                     callback=self.amacSaleparse)
#            elif url == 'http://www.amac.org.cn/xxgs/cyjggs/zfjsjg/382716.shtml':
#                yield scrapy.Request(url,
#                                     headers = self.headers1,
#                                     callback=self.amacpayparse)
#            elif url =='http://www.amac.org.cn/xxgs/zhgs/382728.shtml':
#                yield scrapy.Request(url,
#                                     headers=self.headers1,
#                                     callback=self.amacaccountparse)
#            elif url == 'http://www.amac.org.cn/xxgs/cyjggs/jjpjjg/382715.shtml':
#                yield scrapy.Request(url,
#                                     headers=self.headers1,
#                                     callback=self.amacevaluationparse)
#            elif url == 'http://www.amac.org.cn/xxgs/cyjggs/lssws/382717.shtml':
#                yield scrapy.Request(url,
#                                     headers=self.headers1,
#                                     callback=self.amaclawparse)
#            elif url == 'http://www.amac.org.cn/xxgs/cyjggs/hjsws/382718.shtml':
#                yield scrapy.Request(url,
#                                     headers=self.headers1,
#                                     callback=self.amacaccounting_firm_parse)
#            elif url == 'http://fo.amac.org.cn/amac/allNotice.do-1':
#                t="2"
#                data=self.madedata7(t,1)
#                yield scrapy.FormRequest('http://fo.amac.org.cn/amac/allNotice.do',
#                                         formdata=data,
#                                         headers = self.headers1,
#                                         meta = {'page':1,'t':t},
#                                         callback = self.parse8)
#            elif url == 'http://fo.amac.org.cn/amac/allNotice.do-2':
#                t = "3"
#                data = self.madedata7(t, 1)
#                yield scrapy.FormRequest('http://fo.amac.org.cn/amac/allNotice.do',
#                                         formdata=data,
#                                         headers=self.headers1,
#                                         meta={'page': 1, 't': t},
#                                         callback=self.parse9)
#            elif url == "http://fo.amac.org.cn/amac/allNotice.do-3":
#                t = "4"
#                data = self.madedata7(t, 1)
#                yield scrapy.FormRequest('http://fo.amac.org.cn/amac/allNotice.do',
#                                         formdata=data,
#                                         headers=self.headers1,
#                                         meta={'page': 1, 't': t},
#                                         callback=self.parse10)
    def parse10(self, response):
        t =     ['t']
        thispage = response.meta['page']
        nextpage = response.xpath("//a[text()='后一页']")
        configs = [
            {'n': ' ', 'En': 'url_id', 't': 'xpath', 'v': 'td[2]/a/@href', 'dt': ''}
        ]
        for info in response.xpath("//tr[@class='tabhead_meeting_list']/following-sibling::tr"):
            result = dict()
            for config in configs:
                result[config['En']] = info.xpath(config['v']).extract_first()

            gsid = re.search('\"viewNoticeForm\", \"(\d*)\"', result['url_id']).group(1)
            infodata = self.madedata8(t, thispage, gsid)
            yield scrapy.FormRequest("http://fo.amac.org.cn/amac/allNotice.do",
                                     headers=self.headers1,
                                     formdata=infodata,
                                     meta={'gsid': gsid},
                                     callback=self.information_institution_parse)
        if nextpage:
            thispage += 1
            data = self.madedata7(t, thispage)
            yield scrapy.FormRequest('http://fo.amac.org.cn/amac/allNotice.do',
                                     formdata=data,
                                     headers=self.headers1,
                                     meta={'page': thispage, 't': t},
                                     callback=self.parse10)
    def information_institution_parse(self, response):
        item = AmacProductItem()
        result = dict()
        result['gsid'] = response.meta['gsid']
        configs = [
            {'n': '机构名称', 'En': 'org_name', 't': 'xpath',
             'v': '//b[text()="机构名称"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '机构代码', 'En': 'org_No', 't': 'xpath',
             'v': '//b[text()="机构代码"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '备案编号', 'En': 'record_number', 't': 'xpath',
             'v': '//b[text()="备案编号"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '机构类型', 'En': 'org_type', 't': 'xpath',
             'v': '//b[text()="机构类型"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '公司网址', 'En': 'website', 't': 'xpath',
             'v': '//b[text()="公司网址"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '注册地址', 'En': 'registered_address', 't': 'xpath',
             'v': '//b[text()="注册地址"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '办公地址 ', 'En': 'address', 't': 'xpath',
             'v': '//b[text()="办公地址"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '法定代表人/执行事务合伙人', 'En': 'legal_person', 't': 'xpath',
             'v': '//b[text()="法定代表人/执行事务合伙人"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '服务类型', 'En': 'server_type', 't': 'xpath',
             'v': '//b[text()="服务类型"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '本服务备案时间', 'En': 'record_date', 't': 'xpath',
             'v': '//b[text()="本服务备案时间"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '服务部门/团队人员数量', 'En': 'team_emp_numbers', 't': 'xpath',
             'v': '//b[text()="服务部门/团队人员数量"]/parent::td/following-sibling::td[1]/text()', 'dt': 'int'},
            {'n': '含基金从业人员数量', 'En': 'fund_emp_numbers', 't': 'xpath',
             'v': '//b[text()="含基金从业人员数量"]/parent::td/following-sibling::td[1]/text()', 'dt': 'int'},
            {'n': 'IT系统名称', 'En': 'IT_systeam_name', 't': 'xpath',
             'v': '//b[text()="IT系统名称"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '备注', 'En': 'remark', 't': 'xpath',
             'v': '//b[text()="备注"]/parent::td/following-sibling::td[1]/text()', 'dt': ''}
        ]
        for config in configs:
            result[config['En']] = response.xpath(config['v']).extract_first()
            if result[config['En']]:
                result[config['En']] = S.replace_all(result[config['En']])
                result[config['En']] = S.changdt(result[config['En']],config['dt'])

        item['keys'] = ['org_No']
        item['db'] = 'amac_information_org'
        item['result'] = result
        yield item
    def parse9(self, response):
        t = response.meta['t']
        thispage = response.meta['page']
        nextpage = response.xpath("//a[text()='后一页']")
        configs = [
            {'n': ' ', 'En': 'url_id', 't': 'xpath', 'v': 'td[2]/a/@href', 'dt': ''}
        ]
        for info in response.xpath("//tr[@class='tabhead_meeting_list']/following-sibling::tr"):
            result = dict()
            for config in configs:
                result[config['En']] = info.xpath(config['v']).extract_first()

            gsid = re.search('\"viewNoticeForm\", \"(\d*)\"', result['url_id']).group(1)
            infodata = self.madedata8(t, thispage, gsid)
            yield scrapy.FormRequest("http://fo.amac.org.cn/amac/allNotice.do",
                                     headers=self.headers1,
                                     formdata=infodata,
                                     meta={'gsid': gsid},
                                     callback=self.business_valution_parse)
        if nextpage:
            thispage+=1
            data = self.madedata7(t, thispage)
            yield scrapy.FormRequest('http://fo.amac.org.cn/amac/allNotice.do',
                                     formdata=data,
                                     headers=self.headers1,
                                     meta={'page': thispage, 't': t},
                                     callback=self.parse9)
    def business_valution_parse(self, response):
        item = AmacProductItem()
        result = dict()
        result['gsid'] = response.meta['gsid']
        configs = [
            {'n': '机构名称', 'En': 'org_name', 't': 'xpath',
             'v': '//b[text()="机构名称"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '机构代码', 'En': 'org_No', 't': 'xpath',
             'v': '//b[text()="机构代码"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '备案编号', 'En': 'record_number', 't': 'xpath',
             'v': '//b[text()="备案编号"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '机构类型', 'En': 'org_type', 't': 'xpath',
             'v': '//b[text()="机构类型"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '公司网址', 'En': 'website', 't': 'xpath',
             'v': '//b[text()="公司网址"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '注册地址', 'En': 'registered_address', 't': 'xpath',
             'v': '//b[text()="注册地址"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '办公地址 ', 'En': 'address', 't': 'xpath',
             'v': '//b[text()="办公地址"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '法定代表人/执行事务合伙人', 'En': 'legal_person', 't': 'xpath',
             'v': '//b[text()="法定代表人/执行事务合伙人"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '服务类型', 'En': 'server_type', 't': 'xpath',
             'v': '//b[text()="服务类型"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '本服务备案时间', 'En': 'record_date', 't': 'xpath',
             'v': '//b[text()="本服务备案时间"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '服务部门/团队人员数量', 'En': 'team_emp_numbers', 't': 'xpath',
             'v': '//b[text()="服务部门/团队人员数量"]/parent::td/following-sibling::td[1]/text()', 'dt': 'int'},
            {'n': '含基金从业人员数量', 'En': 'fund_emp_numbers', 't': 'xpath',
             'v': '//b[text()="含基金从业人员数量"]/parent::td/following-sibling::td[1]/text()', 'dt': 'int'},
            {'n': '备注', 'En': 'remark', 't': 'xpath',
             'v': '//b[text()="备注"]/parent::td/following-sibling::td[1]/text()', 'dt': ''}
        ]
        for config in configs:
            result[config['En']] = response.xpath(config['v']).extract_first()
            if result[config['En']]:
                result[config['En']] = S.replace_all(result[config['En']])
                if result[config['En']]:
                   result[config['En']] = S.replace_invalid_char(result[config['En']])
                   result[config['En']] = S.changdt(result[config['En']],config['dt'])
        item['keys'] = ['org_No']
        item['db'] = 'amac_Business_valuation_services'
        item['result'] = result
        yield item
    def parse8(self, response):
        t = response.meta['t']
        thispage = response.meta['page']
        nextpage = response.xpath("//a[text()='后一页']")
        configs = [
            {'n': ' ', 'En': 'url_id', 't': 'xpath', 'v': 'td[2]/a/@href', 'dt': ''}
        ]
        for info in response.xpath("//tr[@class='tabhead_meeting_list']/following-sibling::tr"):
            result = dict()
            for config in configs:
                result[config['En']] = info.xpath(config['v']).extract_first()

            gsid = re.search('\"viewNoticeForm\", \"(\d*)\"',result['url_id']).group(1)
            infodata = self.madedata8(t,thispage,gsid)
            yield scrapy.FormRequest("http://fo.amac.org.cn/amac/allNotice.do",
                                     headers=self.headers1,
                                     formdata=infodata,
                                     meta={'gsid':gsid},
                                     callback=self.registration_parse)
        if nextpage:
            thispage+=1
            data = self.madedata7(t, thispage)
            yield scrapy.FormRequest('http://fo.amac.org.cn/amac/allNotice.do',
                                     formdata=data,
                                     headers=self.headers1,
                                     meta={'page': thispage, 't': "2"},
                                     callback=self.parse8)

    def registration_parse(self, response):
        item = AmacProductItem()
        result = dict()
        result['gsid'] = response.meta['gsid']
        configs = [
            {'n': '机构名称', 'En': 'org_name', 't': 'xpath', 'v': '//b[text()="机构名称"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '机构代码', 'En': 'org_No', 't': 'xpath', 'v': '//b[text()="机构代码"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '备案编号', 'En': 'record_number', 't': 'xpath', 'v': '//b[text()="备案编号"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '机构类型', 'En': 'org_type', 't': 'xpath', 'v': '//b[text()="机构类型"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '公司网址', 'En': 'website', 't': 'xpath', 'v': '//b[text()="公司网址"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '注册地址', 'En': 'registered_address', 't': 'xpath', 'v': '//b[text()="注册地址"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '办公地址 ', 'En': 'address', 't': 'xpath', 'v': '//b[text()="办公地址"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '法定代表人/执行事务合伙人', 'En': 'legal_person', 't': 'xpath', 'v': '//b[text()="法定代表人/执行事务合伙人"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '服务类型', 'En': 'server_type', 't': 'xpath', 'v': '//b[text()="服务类型"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '本服务备案时间', 'En': 'record_date', 't': 'xpath', 'v': '//b[text()="本服务备案时间"]/parent::td/following-sibling::td[1]/text()', 'dt': ''},
            {'n': '服务部门/团队人员数量', 'En': 'team_emp_numbers', 't': 'xpath', 'v': '//b[text()="服务部门/团队人员数量"]/parent::td/following-sibling::td[1]/text()', 'dt': 'int'},
            {'n': '含基金从业人员数量', 'En': 'fund_emp_numbers', 't': 'xpath', 'v': '//b[text()="含基金从业人员数量"]/parent::td/following-sibling::td[1]/text()', 'dt': 'int'},
            {'n': '备注', 'En': 'remark', 't': 'xpath', 'v': '//b[text()="备注"]/parent::td/following-sibling::td[1]/text()', 'dt': ''}
        ]
        for config in configs:
            result[config['En']] = response.xpath(config['v']).extract_first()
            if result[config['En']]:
                result[config['En']] = S.replace_all(result[config['En']])
                if result[config['En']]:
                   result[config['En']] = S.replace_invalid_char(result[config['En']])
                   result[config['En']] = S.changdt(result[config['En']],config['dt'])
        item['keys'] = ['org_No']
        item['db'] = 'amac_registration_org'
        item['result'] = result
        yield item
    def amacaccounting_firm_parse(self, response):
        item = AmacProductItem()
        res = S.replace_invalid_html_char(response.text)
        response1 = S2(text=res)
        configs = [
            {'n': '会计师事务所名称 ', 'En': 'firm_name', 't': 'xpath', 'v': 'td[2]/text()', 'dt': ''},
            {'n': '成立时间', 'En': 'setup_time', 't': 'xpath', 'v': 'td[3]/text()', 'dt': ''},
            {'n': '网址', 'En': 'website', 't': 'xpath', 'v': 'td[4]/text()|td[4]/a/text()', 'dt': ''},
            {'n': '联系地址', 'En': 'address', 't': 'xpath', 'v': 'td[5]/text()|td[5]/p/text()', 'dt': ''},
            {'n': '电话', 'En': 'tel_num', 't': 'xpath', 'v': 'td[6]/text()', 'dt': ''},
            {'n': '协会会员', 'En': 'member', 't': 'xpath', 'v': 'td[7]/text()', 'dt': ''},
        ]
        for info in response1.xpath("//div[@class='ldContent']/div/table/tbody/tr[position()>1]"):
            # print(info)
            result = {}
            for config in configs:
                result[config['En']] = ' '.join(info.xpath(config['v']).extract()) if info.xpath(
                    config['v']).extract() else ''
                if result[config['En']]:
                   result[config['En']] = S.replace_invalid_char(result[config['En']])
                   result[config['En']] = S.changdt(result[config['En']],config['dt'])
            item['keys'] = ['firm_name']
            item['db'] = 'amac_accounting_firm'
            item['result'] = result
            yield item
    def amaclawparse(self, response):
        item = AmacProductItem()
        res = S.replace_invalid_html_char(response.text)
        response1 = S2(text=res)
        configs = [
            {'n': '律师事务所名称 ', 'En': 'org_name', 't': 'xpath', 'v': 'td[2]/text()', 'dt': ''},
            {'n': '成立时间', 'En': 'setup_time', 't': 'xpath', 'v': 'td[3]/text()', 'dt': ''},
            {'n': '网址', 'En': 'website', 't': 'xpath', 'v': 'td[4]/text()|td[4]/a/text()', 'dt': ''},
            {'n': '联系地址', 'En': 'address', 't': 'xpath', 'v': 'td[5]/text()|td[5]/p/text()', 'dt': ''},
            {'n': '电话', 'En': 'tel_num', 't': 'xpath', 'v': 'td[6]/text()', 'dt': ''},
            {'n': '协会会员', 'En': 'member', 't': 'xpath', 'v': 'td[7]/text()', 'dt': ''},
        ]
        for info in response1.xpath("//div[@class='ldContent']/div/table/tbody/tr[position()>1]"):
            # print(info)
            result = {}
            for config in configs:
                result[config['En']] = ' '.join(info.xpath(config['v']).extract()) if info.xpath(
                    config['v']).extract() else ''
                if result[config['En']]:
                   result[config['En']] = S.replace_invalid_char(result[config['En']])
                   result[config['En']] = S.changdt(result[config['En']],config['dt'])
            item['keys'] = ['org_name']
            item['db'] = 'amac_law_org'
            item['result'] = result
            yield item
    def amacevaluationparse(self, response):
        item = AmacProductItem()
        res = S.replace_invalid_html_char(response.text)
        response1 = S2(text=res)
        configs = [
            {'n': '基金销售机构名称', 'En': 'org_name', 't': 'xpath', 'v': 'td[2]/text()', 'dt': ''},
            {'n': '业务核准时间', 'En': 'Approval_date', 't': 'xpath', 'v': 'td[3]/text()', 'dt': ''},
            {'n': '网址', 'En': 'website', 't': 'xpath', 'v': 'td[4]/text()|td[4]/a/text()', 'dt': ''},
            {'n': '联系地址', 'En': 'address', 't': 'xpath', 'v': 'td[5]/text()|td[5]/p/text()', 'dt': ''},
            {'n': '电话', 'En': 'tel_num', 't': 'xpath', 'v': 'td[6]/text()', 'dt': ''},
            {'n': '协会会员', 'En': 'member', 't': 'xpath', 'v': 'td[7]/text()', 'dt': ''},
        ]
        for info in response1.xpath("//div[@class='ldContent']/div/table/tbody/tr[position()>1]"):
            # print(info)
            result = {}
            for config in configs:
                result[config['En']] = ' '.join(info.xpath(config['v']).extract()) if info.xpath(
                    config['v']).extract() else ''
                if result[config['En']]:
                   result[config['En']] = S.replace_invalid_char(result[config['En']])
                   result[config['En']] = S.changdt(result[config['En']],config['dt'])
            item['keys'] = ['org_name']
            item['db'] = 'amac_evaluation_org'
            item['result'] = result
            yield item

    def amacaccountparse(self, response):
        item = AmacProductItem()
        res = S.replace_invalid_html_char(response.text)
        response1 = S2(text=res)
        configs = [
            {'n': '公司名称', 'En': 'company_name', 't': 'xpath', 'v': 'td[1]/text()|td[1]/pre/text()', 'dt': ''},
            {'n': '账户名称', 'En': 'account_name', 't': 'xpath', 'v': 'td[2]/text()|td[2]/pre/text()', 'dt': ''},
            {'n': '开户行', 'En': 'open_bank', 't': 'xpath', 'v': 'td[3]/text()|td[3]/a/text()|td[3]/pre/text()', 'dt': ''},
            {'n': '账号', 'En': 'account_number', 't': 'xpath', 'v': 'td[4]/text()|td[4]/p/text()|td[4]/pre/text()', 'dt': ''},
            {'n': '公司网址', 'En': 'website', 't': 'xpath', 'v': 'td[5]/a/text()|td[5]/p/text()|td[5]/p/span/a/text()|td[5]/pre/text()', 'dt': ''},
            {'n': '公司地址', 'En': 'address', 't': 'xpath', 'v': 'td[6]/text()|td[6]/span/text()|td[6]/pre/text()', 'dt': ''},
            {'n': '联系电话', 'En': 'tel_num', 't': 'xpath', 'v': 'td[7]/text()|td[7]/span/text()|td[7]/p/text()|td[7]/pre/text()', 'dt': ''},
        ]
        configs2 = [{'n': '账户名称', 'En': 'account_name', 't': 'xpath', 'v': 'td[1]/text()', 'dt': ''},
                    {'n': '开户行', 'En': 'open_bank', 't': 'xpath', 'v': 'td[2]/text()|td[2]/a/text()', 'dt': ''},
                    {'n': '账号', 'En': 'account_number', 't': 'xpath', 'v': 'td[3]/text()|td[3]/p/text()', 'dt': ''}]
        configs3 = [{'n': '账号', 'En': 'account_number', 't': 'xpath', 'v': 'td[1]/text()|td[1]/p/text()', 'dt': ''}]
        result = {}
        for info in response1.xpath("//div[@class='ldContent']/div/table/tbody/tr[position()>2]"):
            # print(info)
            if info.xpath("td[position()=7]"):
                for config in configs:
                    result[config['En']] = ' '.join(info.xpath(config['v']).extract()) if info.xpath(
                        config['v']).extract() else ''
                    if result[config['En']]:
                        result[config['En']] = S.replace_all(result[config['En']])
            elif info.xpath("td[position()=3]"):
                for config in configs2:
                    result[config['En']] = ' '.join(info.xpath(config['v']).extract()) if info.xpath(
                        config['v']).extract() else ''
                    if result[config['En']]:
                        result[config['En']] = S.replace_all(result[config['En']])
            else:
                for config in configs3:
                    result[config['En']] = ' '.join(info.xpath(config['v']).extract()) if info.xpath(
                        config['v']).extract() else ''
                    if result[config['En']]:
                        result[config['En']] = S.replace_all(result[config['En']])

            item['keys'] = ['account_number']
            item['db'] = 'amc_account_number'
            item['result'] = result
            yield item
    def amacpayparse(self, response):
        item = AmacProductItem()
        res = S.replace_invalid_html_char(response.text)
        response1 = S2(text=res)
        configs = [
            {'n': '支付结算机构名称 ', 'En': 'org_name', 't': 'xpath', 'v': 'td[2]/text()', 'dt': ''},
            {'n': '首次在中国证监会备案时间', 'En': 'first_record_date', 't': 'xpath', 'v': 'td[3]/text()', 'dt': ''},
            {'n': '网址', 'En': 'website', 't': 'xpath', 'v': 'td[4]/text()|td[4]/a/text()', 'dt': ''},
            {'n': '联系地址', 'En': 'address', 't': 'xpath', 'v': 'td[5]/text()|td[5]/p/text()', 'dt': ''},
            {'n': '电话', 'En': 'tel_num', 't': 'xpath', 'v': 'td[6]/text()', 'dt': ''},
            {'n': '协会会员', 'En': 'member', 't': 'xpath', 'v': 'td[7]/text()', 'dt': ''},
        ]
        for info in response1.xpath("//div[@class='ldContent']/div/table/tbody/tr[position()>1]"):
            # print(info)
            result = {}
            for config in configs:
                result[config['En']] = ' '.join(info.xpath(config['v']).extract()) if info.xpath(config['v']).extract() else ''
                if result[config['En']]:
                   result[config['En']] = S.replace_invalid_char(result[config['En']])
                   result[config['En']] = S.changdt(result[config['En']],config['dt'])
            item['keys'] = ['org_name']
            item['db'] = 'amac_pay_org'
            item['result'] = result
            yield item
    def amacSaleparse(self, response):
        item = AmacProductItem()
        res = S.replace_invalid_html_char(response.text)
        response1 = S2(text=res)

        configs = [
            {'n': '基金销售机构', 'En': 'org_name', 't': 'xpath', 'v': 'td[2]/text()', 'dt': ''},
            {'n': '业务核准时间', 'En': 'Approval_date', 't': 'xpath', 'v': 'td[3]/text()', 'dt': ''},
            {'n': '网址', 'En': 'website', 't': 'xpath', 'v': 'td[4]/text()|td[4]/a/text()', 'dt': ''},
            {'n': '联系地址', 'En': 'address', 't': 'xpath', 'v': 'td[5]/text()|td[5]/p/text()', 'dt': ''},
            {'n': '电话', 'En': 'tel_num', 't': 'xpath', 'v': 'td[6]/text()', 'dt': ''},
            {'n': '协会会员', 'En': 'member', 't': 'xpath', 'v': 'td[7]/text()', 'dt': ''},
        ]

        for info in response1.xpath("//div[@class='ldContent']/table/tbody/tr[position()>1]"):
            # print(info)
            result = {}
            for config in configs:
                result[config['En']] = ' '.join(info.xpath(config['v']).extract()) if info.xpath(config['v']).extract() else ''
                if result[config['En']]:
                   result[config['En']] = S.replace_invalid_char(result[config['En']])
                   result[config['En']] = S.changdt(result[config['En']],config['dt'])
            item['keys'] = ['org_name']
            item['db'] = 'amac_sales_org'
            item['result'] = result
            yield item
    def parse7(self, response):
        '''
        私募基金从业人员信息表
        '''
        item = AmacProductItem()
        js = json.loads(response.text)
        if self.page6==1:
            self.totalPages6 = js['totalPages']
        configs = [
            {'n': '机构名称', 'En': 'CorpFullName', 't': 'json', 'v': 'AOI_NAME', 'dt': 'int'},
            {'n': '员工人数', 'En': 'EmployeeCount', 't': 'json', 'v': 'PR_COUNT_PERSON', 'dt': 'int'},
            {'n': '基金从业资格', 'En': 'FundQualificationCount', 't': 'json', 'v': 'PTI1PERSON', 'dt': 'int'},
            {'n': '基金销售从业资格', 'En': 'SaleQualificationCount', 't': 'json', 'v': 'PTI2PERSON', 'dt': 'int'},
            {'n': '其他从业资格', 'En': 'OtherQualificationCount', 't': 'json', 'v': 'PTI3PERSON', 'dt': 'int'},
            {'n': 'PE/VC从业资格', 'En': 'PEQualificationCount', 't': 'json', 'v': 'PTI4PERSON', 'dt': 'int'},
            {'n': '合规风控负责人', 'En': 'RiskEmployeeCount', 't': 'json', 'v': 'PTI6PERSON', 'dt': 'int'},
            {'n': '基金投资顾问', 'En': 'FundInvestAdviserCount', 't': 'json', 'v': 'PTI7PERSON', 'dt': 'int'},
            {'n': '基金经理', 'En': 'FundManagerCount', 't': 'json', 'v': 'PTI8PERSON', 'dt': 'int'},
            {'n': '投资经理', 'En': 'InvestManagerCount', 't': 'json', 'v': 'PTI9PERSON', 'dt': 'int'},
            {'n': '投资总监', 'En': 'InvestDirectorCount', 't': 'json', 'v': 'PTI10PERSON', 'dt': 'int'},
            {'n': '机构ID', 'En': 'CorpRawID', 't': 'json', 'v': 'AOI_ID', 'dt': 'int'}
        ]
        for json_ in js['result']:
            result = dict()
            for config in configs:
                result[config['En']] = json_[config['v']]
                if result[config['En']]:
                   result[config['En']] = S.replace_invalid_char(result[config['En']])
                   result[config['En']] = S.changdt(result[config['En']],config['dt'])
            item['keys'] = ['CorpRawID']
            item['db'] = 'Corp_Employee_Stat'
            item['result'] = result
            yield item
            personurl = "http://person.amac.org.cn/pages/registration/train-line-register!search.action"
            persondata = {'filter_EQS_PTI_ID':'',
                    'filter_EQS_AOI_ID':str(result['CorpRawID']),
                    'ORDERNAME':'PP#PTI_ID,PP#PPP_NAME',
                    'ORDER':'ASC',
                    'sqlkey':'registration',
                    'sqlval':'SEARCH_FINISH_PUBLICITY'}
            yield scrapy.FormRequest(personurl,
                                     formdata=persondata,
                                     headers = self.headers1,
                                     meta = {'CorpRawID':result['CorpRawID']},
                                     callback = self.personparse)
        if self.page6 < self.totalPages6:
            self.page6+=1
            data = self.madedata6(self.page6, self.size6)
            # data = urllib.parse.urlencode(data)
            yield scrapy.FormRequest("http://person.amac.org.cn/pages/registration/train-line-register!list.action",
                                     headers=self.urlencodeheaders,
                                     formdata=data,
                                     method="POST",
                                     callback=self.parse7)

    def personparse(self, response):
        item = AmacProductItem()
        result=dict()
        result['CorpRawID'] = response.meta['CorpRawID']
        js = json.loads(response.text)
        configs = [
            {'n': '机构ID', 'En': 'CorpRowID', 't': 'meta', 'v': 'CorpRawID', 'dt': 'int'},
            {'n':'人员ID', 'En': 'EmpID', 't': 'json', 'v': 'RPI_ID', 'dt': 'int'},
            {'n': '姓名', 'En': 'EmpFullName', 't': 'json', 'v': 'RPI_NAME', 'dt': ''},
            {'n': '机构全称', 'En': 'CorpFullName', 't': 'json', 'v': 'AOI_NAME', 'dt': ''},
            {'n': '性别', 'En': 'Gender', 't': 'json', 'v': 'SCO_NAME', 'dt': ''},
            {'n': '学历', 'En': 'Education', 't': 'json', 'v': 'ECO_NAME', 'dt': ''},
            {'n': '证书类型', 'En': 'QualificationType', 't': 'json', 'v': 'CTI_NAME', 'dt': ''},
            {'n': '证书编号', 'En': 'QualificationNo', 't': 'json', 'v': 'CER_NUM', 'dt': ''},
            {'n': '证书发布日期', 'En': 'QualificationStartDate', 't': 'json', 'v': 'PPP_GET_DATE', 'dt': ''},
            {'n': '证书截止有效日期', 'En': 'QualificationEndDate', 't': 'json', 'v': 'PPP_END_DATE', 'dt': ''},
            {'n': '变更信息', 'En': 'ChangeInformationCount', 't': 'json', 'v': 'COUNTCER', 'dt': 'int'},
            {'n': '诚信记录', 'En': 'CreditTip', 't': 'json', 'v': 'COUNTCX', 'dt': ''}
        ]
        for json_ in js:
            for config in configs:
                if config['t'] == 'json':
                    result[config['En']] = json_[config['v']]
                    if result[config['En']]:
                       result[config['En']] = S.replace_invalid_char(result[config['En']])
                       result[config['En']] = S.changdt(result[config['En']],config['dt'])
            result['Gender'] = 1 if result['Gender'] =="男" else 2 if result['Gender'] =="女" else 3
            item['keys'] = ['EmpID']
            item['db'] = 'Corp_Employee'
            item['result'] = result
            yield item
            changeurl = "http://person.amac.org.cn/pages/registration/train-line-register!search.action"
            changedata = {'filter_EQS_RH#RPI_ID':str(result['EmpID']),
                          'sqlkey':'registration',
                          'sqlval':'SEARCH_LIST_BY_PERSON'}
            yield scrapy.FormRequest(changeurl,
                                     formdata=changedata,
                                     headers = self.headers1,
                                     meta = {'Emp_id':result['EmpID']},
                                     callback = self.changeparse)
    def changeparse(self, response):
        item = AmacProductItem()
        result = dict()
        result['Emp_id'] = response.meta['Emp_id']
        js = json.loads(response.text)
        # print(js)
        configs = [
            {'n': '从业机构', 'En': 'CorpFullName', 't': 'json', 'v': 'AOI_NAME', 'dt': ''},
            {'n': '从业资格类型', 'En': 'QualificationType', 't': 'json', 'v': 'PTI_NAME', 'dt': ''},
            {'n': '证书编号', 'En': 'QualificationNo', 't': 'json', 'v': 'CER_NUM', 'dt': ''},
            {'n': '取得日期', 'En': 'QualificationStartDate', 't': 'json', 'v': 'OBTAIN_DATE', 'dt': ''},
            {'n': '证书状态', 'En': 'QualificationStatus', 't': 'json', 'v': 'CERTC_NAME', 'dt': ''},
            {'n': '人员ID', 'En': 'EmpID', 't': 'meta', 'v': 'COUNTCX', 'dt': 'int'}
        ]
        for json_ in js:
            for config in configs:
                if config['t'] == 'json':
                    result[config['En']] = json_[config['v']]
                    if result[config['En']]:
                       result[config['En']] = S.replace_invalid_char(result[config['En']])
                       result[config['En']] = S.changdt(result[config['En']],config['dt'])
            item['keys'] = ['EmpID']
            item['db'] = 'Corp_Employee_Change'
            item['result'] = result
            yield item
    def parse6(self, response):
#        print(response.text)
        js = json.loads(response.text)
        if self.page5 == 1:
            self.totalPages5 = js['totalPages']
        for json_ in js['result']:
            qhid = json_['MPI_ID']
            data = {
                    'filter_EQS_MPI_ID':str(qhid),
                    'sqlkey':'publicity_web',
                    'sqlval':'GET_QH_WEB_BY_MPI_ID'
            }
#            referer = "http://ba.amac.org.cn/pages/amacWeb/qh-web-list.html?id={qhid}".format(qhid=qhid)
#            headers = {"User-Agent": generate_user_agent()}
            yield scrapy.FormRequest("http://ba.amac.org.cn/pages/amacWeb/user!search.action",
                                     formdata = data,
                                     meta = {"MPI_ID":qhid},
                                     # headers = headers,
                                     callback = self.qhparse)
        if self.page5 < self.totalPages5:
            self.page5+=1
            data = self.madedata4(self.page5, self.size5)
            yield scrapy.FormRequest("http://ba.amac.org.cn/pages/amacWeb/user!list.action",
                                     headers=self.headers1,
                                     formdata=data,
                                     method="POST",
                                     callback=self.parse6)
    def parse5(self, response):
        '''
        基金业协会-资产支持专项计划
        '''
        item = AmacProductItem()
        js = json.loads(response.text)
        if self.page4 == 1:
            self.totalPages4 = js['totalPages']
        configs = [{'n': '专项计划全称', 'En': 'abs_name', 't': 'json', 'v':'ASPI_NAME', 'dt': ''},
                   {'n': '备案编号', 'En': 'abs_recode_No', 't': 'json', 'v': 'ASPI_BA_NUMBER', 'dt': ''},
                   {'n': '管理人', 'En': 'abs_manager', 't': 'json', 'v': 'ASPI_GL_NAME', 'dt': ''},
                   {'n': '托管人', 'En': 'abs_custofian', 't': 'json', 'v': 'AII_TGR', 'dt': ''},
                   {'n': '备案通过时间', 'En': 'adopt_date', 't': 'json', 'v': 'AT_AUDIT_DATE', 'dt': ''},
                   {'n': 'abs_id', 'En': 'abs_id', 't': 'json', 'v': 'ASPI_ID', 'dt': ''}
                   ]
        for json_ in js['result']:
            result = dict()
            for config in configs:
                result[config['En']] = json_[config['v']]
                if result[config['En']]:
                   result[config['En']] = S.replace_invalid_char(result[config['En']])
                   result[config['En']] = S.changdt(result[config['En']],config['dt'])
            item['keys'] = ['abs_recode_No']
            item['db'] = 'AMAC.ABS_Prod'
            item['result'] = result
            yield item
        if self.page4<self.totalPages4:
            self.page4+=1
            data = self.madedata3(self.page4, self.size4)
            yield scrapy.FormRequest("http://ba.amac.org.cn/pages/amacWeb/ab-special-plan!list.action",
                                     headers=self.headers1,
                                     formdata=data,
                                     method="POST",
                                     callback=self.parse5)

    def parse4(self, response):
        js = json.loads(response.text)
        if self.page3 == 0:
            self.totalPages3 = js['totalPages']
        # print(self.totalPages3)
        for account in js['content']:
            # print(account)
            url = "http://gs.amac.org.cn/amac-infodisc/res/fund/account/{account_id}.html".format(account_id=account['id'])
            yield scrapy.Request(url,
                                 callback=self.accountparse,
                                 method='GET',
                                 headers=self.headers1)
        if self.page3 < self.totalPages3:
            self.page3 += 1
            next_url = "http://gs.amac.org.cn/amac-infodisc/api/fund/account" + self.madedata(self.page3, self.offset3, self.rand2)
            data = {}
            yield scrapy.Request(next_url,
                                 method="POST",
                                 body=json.dumps(data),
                                 headers=self.headers,
                                 callback=self.parse4
                                 )
    def parse3(self, response):
        # print(response.text)
        js = json.loads(response.text)
        configs = [
            {'n': 'id', 'En': 'id', 't': 'json', 'v': 'id', 'dt': 'str'}

                ]
        if self.page2 == 0:
            self.totalPages2 = js['totalPages']
        result = {}
        for json_ in js['content']:
            for config in configs:
                result[config['En']]= json_[config['v']]
                url = "http://gs.amac.org.cn/amac-infodisc/res/aoin/product/{pid}.html".format(pid=result['id'])
                yield scrapy.Request(url,
                                     callback=self.directfundparse,
                                     method='GET',
                                     headers = self.headers1)
        if self.page2 <  self.totalPages2:
            self.page2+=1
            url = "http://gs.amac.org.cn/amac-infodisc/api/aoin/product"+ self.madedata(self.page2,self.offset2,self.rand1)
            data = {}
            yield scrapy.FormRequest(url,
                                     method='POST',
                                     body=json.dumps(data),
                                     headers=self.headers,
                                     callback=self.parse3)


    def parse2(self, response):
        '''
        基金业协会-证券公司私募产品
        '''
#        print(response.text)
        item = AmacProductItem()
        js = json.loads(response.text)
#        print(js)
        if self.page1 == 1:
            self.totalPages1 = js['totalPages']
        result = {}
        configs = [
                    {"n":"成立规模","En":"setup_scale","t":"json","v":"CLGM","dt":"float"},
                    {"n":"成立时参与户数","En":"setup_Nums","t":"json","v":"CLSCYHS","dt":"int"},
                    {"n":"产品编码","En":"pro_No","t":"json","v":"CPBM","dt":""},
                    {"n":"产品名称","En":"pro_name","t":"json","v":"CPMC","dt":""},
                    {"n":"到期日","En":"end_date","t":"json","v":"DQR","dt":""},
                    {"n":"份额登记机构","En":"share_register_org","t":"json","v":"FEDJJG","dt":""},
                    {"n":"管理方式","En":"manage_type","t":"json","v":"GLFS","dt":""},
                    {"n":"管理机构","En":"manage_org","t":"json","v":"GLJG","dt":""},
                    {"n":"产品ID","En":"pro_ID","t":"json","v":"MPI_ID","dt":""},
                    #{"n":"","En":"PW_ID","t":"json","v":"PW_ID","dt":""},
                    #{"n":"","En":"PW_STATES","t":"json","v":"PW_STATES","dt":""},
#                    {"n":"","En":"","t":"json","v":"RN","dt":""},
                    {"n":"是否分级","En":"is_graded","t":"json","v":"SFFJ","dt":""},
                    {"n":"设立日期","En":"setup_date","t":"json","v":"SLRQ","dt":""},
                    {"n":"托管机构","En":"Trusteeship_org","t":"json","v":"TGJG","dt":""},
                    {"n":"投资范围","En":"investment_scope","t":"json","v":"TZFW","dt":""},
                    {"n":"投资类型","En":"investment_type","t":"json","v":"TZLX","dt":""}
                    ]
        for info in js['result']:
            for config in configs:
                result[config['En']] = info[config['v']]
                if result[config['En']]:
                   result[config['En']] = S.replace_all(result[config['En']])
                   result[config['En']] = S.changdt(result[config['En']],config['dt'])
            item['result'] = result
            item['keys'] = ['pro_No']
            item['db'] = "AMAC.Securuties_Prod"
            yield item
        if self.page1 < self.totalPages1:
            self.page1+=1
            data = self.madedata2(self.page1,self.size1)
            yield scrapy.FormRequest("http://ba.amac.org.cn/pages/amacWeb/user!list.action",
                                     headers = self.headers1,
                                     formdata = data,
                                     method = "POST",
                                     callback = self.parse2)
#            print(item)
    def parse(self, response):
        js = json.loads(response.text)
#        print(js)
        if self.page==0:
            self.totalPages0 = int(js['totalPages'])
#            print(self.totalPages0)
        configs = [{"n":"基金备案号","En":"fundNo","t":"json","v":"fundNo","dt":""},
#                   {"n":"基金名称","En":"fundName","t":"json","v":"fundName","dt":""},
                   #{"n":"","En":"isDeputeManage","t":"json","v":"isDeputeManage","dt":""},
                   #{"n":"","En":"establishDate","t":"json","v":"establishDate","dt":""},
                   #{"n":"最近季度跟新","En":"lastQuarterUpdate","t":"json","v":"lastQuarterUpdate","dt":""},
#                   {"n":"基金管理公司","En":"managerName","t":"json","v":"managerName","dt":""},
#                   {"n":"管理类型","En":"managerType","t":"json","v":"managerType","dt":""},
                   {"n":"基金管理人ID","En":"managerID","t":"json","v":"managerUrl","dt":""},
#                   {"n":"托管人名称","En":"mandatorName","t":"json","v":"mandatorName","dt":""},
                   #{"n":"备案时间","En":"putOnRecordDate","t":"json","v":"putOnRecordDate","dt":""},
                   #{"n":"","En":"url","t":"json","v":"url","dt":""},
                   {"n":"基金ID","En":"fundID","t":"json","v":"id","dt":""},
#                   {"n":"基金ID","En":"special_note","t":"json","v":"id","dt":""}
                   ]
        result = {}
        for jsons in js['content']:
            for config in configs:
                result[config['En']] = jsons.get(config['v'])
            result['managerID'] = result['managerID'].split("/")[-1].replace(".html","")
            
            fund_pro_url = self.fundUrl.format(fundID=jsons.get("id"))
            headers1 = {"User-Agent":generate_user_agent()
                       }
            
            yield scrapy.Request(fund_pro_url,
                                 method = "GET",
#                                 meta = {'result':result},
                                 headers = headers1,
                                 callback = self.fund_pro_parse)
        if self.page<self.totalPages0:
            self.page+=1
            url = 'http://gs.amac.org.cn/amac-infodisc/api/pof/fund'+self.madedata(self.page,self.offset,self.rand)
            data = {}
            yield scrapy.Request(url,
                                 method = "POST",
                                 body = json.dumps(data),
                                 headers = self.headers,
                                 callback=self.parse
                                 )
        
    def fund_pro_parse(self, response):#
        '''
        基金业协会-私募基金管理人基金产品
        '''
#        print(response.url)
        item = AmacProductItem()
#        result = response.meta['result']
        configs = [{"n":"基金名称","v":"//td[contains(text(),'基金名称:')]/following-sibling::td/text()","t":"xpath","En":"fundName","dt":""},
                   {"n": "基金编号", "v": "//td[contains(text(),'基金编号:')]/following-sibling::td/text()", "t": "xpath",
                    "En": "fundNo", "dt": ""},
                   {"n":"成立时间","v":"//td[contains(text(),'成立时间:')]/following-sibling::td/text()","t":"xpath","En":"setup_date","dt":""},
                   {"n":"备案时间","v":"//td[contains(text(),'备案时间:')]/following-sibling::td/text()","t":"xpath","En":"record_date","dt":""},
                   {"n":"基金备案阶段","v":"//td[contains(text(),'基金备案阶段:')]/following-sibling::td/text()","t":"xpath","En":"record_stage","dt":""},
                   {"n":"基金类型","v":"//td[contains(text(),'基金类型:')]/following-sibling::td/text()","t":"xpath","En":"fund_type","dt":""},
                   #{"n": "币种", "v": "//td[contains(text(),'币种:')]/following-sibling::td/text()", "t": "xpath",
                   # "En": "money_type", "dt": ""},
                   {"n": "基金管理人名称", "v": "//td[contains(text(),'基金管理人名称:')]/following-sibling::td/a/text()", "t": "xpath",
                    "En": "managerName", "dt": ""},
                   {"n": "基金管理人ID", "v": "//td[contains(text(),'基金管理人名称:')]/following-sibling::td/a/@href", "t": "xpath",
                    "En": "managerID", "dt": ""},
                   {"n": "管理类型", "v": "//td[contains(text(),'管理类型:')]/following-sibling::td/text()", "t": "xpath",
                    "En": "managerType", "dt": ""},
                   {"n": "托管人名称", "v": "//td[contains(text(),'托管人名称:')]/following-sibling::td/text()", "t": "xpath",
                    "En": "mandatorName", "dt": ""},
                   {"n":"基金信息最后更新时间","v":"//td[contains(text(),'基金信息最后更新时间:')]/following-sibling::td/text()","t":"xpath","En":"lastupdateTime","dt":""},
                   {"n": "基金协会特别提示（针对基金）", "v": "//td[contains(text(),'基金协会特别提示（针对基金）:')]/following-sibling::td/text()", "t": "xpath",
                    "En": "special_note", "dt": ""},
                   {"n":"月报应披露","v":"//td[contains(text(),'月报:')]/following-sibling::td/text()","t":"xpath","En":"month_should_reveal","dt":"int"},
                   {"n":"月报按时披露","v":"//td[contains(text(),'月报:')]/following-sibling::td/text()","t":"xpath","En":"month_reveal_intime","dt":"int"},
                   {"n":"月报未披露","v":"//td[contains(text(),'月报:')]/following-sibling::td/text()","t":"xpath","En":"month_None_reveal","dt":"int"},
                   {"n":"半年报应披露","v":"//td[contains(text(),'半年报:')]/following-sibling::td/text()","t":"xpath","En":"halfYear_should_reveal","dt":"int"},
                   {"n":"半年报按时披露","v":"//td[contains(text(),'半年报:')]/following-sibling::td/text()","t":"xpath","En":"halfYear_reveal_intime","dt":"int"},
                   {"n":"半年报未披露","v":"//td[contains(text(),'半年报:')]/following-sibling::td/text()","t":"xpath","En":"halfYear_None_reveal","dt":"int"},
                   {"n":"年报应披露","v":"//td[contains(text(),'年报:')]/following-sibling::td/text()","t":"xpath","En":"Year_should_reveal","dt":"int"},
                   {"n":"年报按时披露","v":"//td[contains(text(),'年报:')]/following-sibling::td/text()","t":"xpath","En":"Year_reveal_intime","dt":"int"},
                   {"n":"年报未披露","v":"//td[contains(text(),'年报:')]/following-sibling::td/text()","t":"xpath","En":"Year_None_reveal","dt":"int"},
                   {"n":"季报应披露","v":"//td[contains(text(),'季报:')]/following-sibling::td/text()","t":"xpath","En":"quarter_should_reveal","dt":"int"},
                   {"n":"季报按时披露","v":"//td[contains(text(),'季报:')]/following-sibling::td/text()","t":"xpath","En":"quarter_reveal_intime","dt":"int"},
                   {"n":"季报未披露","v":"//td[contains(text(),'季报:')]/following-sibling::td/text()","t":"xpath","En":"quarter_None_reveal","dt":"int"}
                   ]
        result = dict()
        for config in configs:
            result[config['En']] = response.xpath(config['v']).extract_first()
            if result[config['En']]:
                result[config['En']] = S.replace_all(result[config['En']])
                
        print(result)
        if result['fundName']:
            pass
        else:
            yield scrapy.Request(response.url,
                                 method = "GET",
#                                 meta = {'result':result},
                                 headers = self.headers1,
                                 dont_filter=True,
                                 callback = self.fund_pro_parse)
            return False
        # print(re.findall("应披露(\d+)条，按时披露(\d+)条，未披露(\d+)条",result['month_None_reveal'])[0])
        print(re.findall("应披露(\d+)条，按时披露(\d+)条，未披露(\d+)条",result['month_None_reveal']))
        (result['month_should_reveal'],result['month_reveal_intime'],result['month_None_reveal'],) = re.findall("应披露(\d+)条，按时披露(\d+)条，未披露(\d+)条",result['month_None_reveal'])[0]
        (result['halfYear_should_reveal'],result['halfYear_reveal_intime'],result['halfYear_None_reveal'],)= re.findall("应披露(\d+)条，按时披露(\d+)条，未披露(\d+)条",result['halfYear_None_reveal'])[0]
        (result['quarter_should_reveal'],result['quarter_reveal_intime'],result['quarter_None_reveal'],)= re.findall("应披露(\d+)条，按时披露(\d+)条，未披露(\d+)条",result['quarter_None_reveal'])[0]
        (result['Year_should_reveal'],result['Year_reveal_intime'],result['Year_None_reveal'],) = re.findall("应披露(\d+)条，按时披露(\d+)条，未披露(\d+)条",result['Year_None_reveal'])[0]
        for config in configs:
            if result[config['En']]:
                   result[config['En']] = S.replace_invalid_char(result[config['En']])
                   result[config['En']] = S.changdt(result[config['En']],config['dt'])
        result['fundID'] = response.url.split("/")[-1][:-5] 
        result['managerID'] = result['managerID'].split("/")[-1][:-5] 
        item['result'] = result
        item['db'] = 'AMAC.Fund_Prod'
        item['keys'] = ['fundNo']
        
        yield item
    def directfundparse(self, response):
        '''
        基金业协会-证券公司直投基金
        '''
        # print(response.text)
        item = AmacProductItem()  
        configs = [{'n':'产品名称','En':'pro_name','t':'xpath','v':'//td[contains(text(),"产品名称") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()','dt':''},
                   {'n':'产品编码','En':'pro_No','t':'xpath','v':'//td[contains(text(),"产品编码") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()','dt':''},
                   {'n':'直投子公司名称','En':'dirct_ep_name','t':'xpath','v':'//td[contains(text(),"直投子公司名称") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()','dt':''},
                   {'n':'管理机构名称','En':'manager_name','t':'xpath','v':'//td[contains(text(),"管理机构名称") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()','dt':''},
                   {'n':'设立日期','En':'setup_date','t':'xpath','v':'//td[contains(text(),"设立日期") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()','dt':''},
                   {'n':'备案日期','En':'record_date','t':'xpath','v':'//td[contains(text(),"备案日期") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()','dt':''},
                   {'n':'基金类型','En':'fund_type','t':'xpath','v':'//td[contains(text(),"基金类型") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()','dt':''},
                   {'n':'组织形式','En':'party_form','t':'xpath','v':'//td[contains(text(),"组织形式") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()','dt':''},
                   {'n':'运作状态','En':'operation_status','t':'xpath','v':'//td[contains(text(),"运作状态") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()','dt':''},
                   {'n':'是否托管','En':'is_truesteeship','t':'xpath','v':'//td[contains(text(),"是否托管") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()','dt':''},
                   {'n':'托管人名称','En':'custodian','t':'xpath','v':'//td[contains(text(),"托管人名称") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()','dt':''},
                   {'n':'产品ID','En':'pro_id','t':'url_split','v':'','dt':''}
                   ]
        result = dict()
        for config in configs:
            if config['t'] == 'xpath':
                result[config['En']] = response.xpath(config['v']).extract_first()
                if result[config['En']]:
                   result[config['En']] = S.replace_invalid_char(result[config['En']])
                   result[config['En']] = S.changdt(result[config['En']],config['dt'])
        result['pro_id'] =  response.url.split('/')[-1][:-5]
        item['db'] = 'AMAC.Direct_Fund'
        item['keys'] = ['pro_No']
        item['result']=result
        yield item
        # print(item)

    def accountparse(self, response):
        '''
        基金业协会-基金专户产品公示
        '''
        item = AmacProductItem()
        configs = [
            {'n': '专户名称', 'En': 'account_name', 't': 'xpath', 'v': '//td[contains(text(),"专户名称") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()', 'dt': ''},
            {'n': '备案编码', 'En': 'record_No', 't': 'xpath', 'v': '//td[contains(text(),"备案编码") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()', 'dt': ''},
            {'n': '管理人名称', 'En': 'manager_name', 't': 'xpath', 'v': '//td[contains(text(),"管理人名称") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()', 'dt': ''},
            {'n': '托管人名称', 'En': 'custofian_name', 't': 'xpath', 'v': '//td[contains(text(),"托管人名称") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()', 'dt': ''},
            {'n': '备案日期', 'En': 'record_date', 't': 'xpath', 'v': '//td[contains(text(),"备案日期") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()', 'dt': ''},
            {'n': '合同期限（月）', 'En': 'contract_period', 't': 'xpath', 'v': '//td[contains(text(),"合同期限（月）") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()', 'dt': 'int'},
            {'n': '起始规模（亿元）', 'En': 'start_scale', 't': 'xpath', 'v': '//td[contains(text(),"起始规模（亿元）") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()', 'dt': 'float'},
            {'n': '是否分级', 'En': 'is_graded', 't': 'xpath', 'v': '//td[contains(text(),"是否分级") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()', 'dt': ''},
            {'n': '成立时投资者数量', 'En': 'investor_nums', 't': 'xpath', 'v': '//td[contains(text(),"成立时投资者数量") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()', 'dt': 'int'},
            {'n': '非专项资产管理计划产品类型', 'En': 'pro_type', 't': 'xpath', 'v': '//td[contains(text(),"非专项资产管理计划产品类型") and @class="td-title"]/following-sibling::td[@class="td-content"]/text()', 'dt': ''},
            {'n': '产品ID', 'En': 'pro_id', 't': 'url_split', 'v': '', 'dt': ''}
        ]
        result = dict()
        for config in configs:
            if config['t'] == 'xpath':
                result[config['En']] = response.xpath(config['v']).extract_first()
                if result[config['En']]:
                    result[config['En']] = S.replace_all(result[config['En']])
                    result[config['En']] = S.changdt(result[config['En']],config['dt'])
                
        result['pro_id'] = response.url.split("/")[-1][:-5]
        item['keys'] = ['account_name']
        item['db'] = 'AMAC.Account_Prod'
        item['result'] = result
        if result['account_name']:
            yield item
    def qhparse(self, response):
        '''
        基金业协会-期货资产管理计划
        '''
        item = AmacProductItem()
        js = json.loads(response.text)[0]
        # print(js)
        configs = [
            {'n': '产品名称', 'En': 'pro_name', 't': 'json', 'v': 'MPI_NAME', 'dt': ''},
            {'n': '产品编码', 'En': 'pro_No', 't': 'json', 'v': 'MPI_PRODUCT_CODE', 'dt': ''},
            {'n': '管理人', 'En': 'manager', 't': 'json', 'v': 'AOI_NAME', 'dt': ''},
            {'n': '托管人', 'En': 'custofian', 't': 'json', 'v': 'MPI_TRUSTEE', 'dt': ''},
            {'n': '成立日期', 'En': 'setup_date', 't': 'json', 'v': 'MPI_CREATE_DATE', 'dt': ''},
            {'n': '投资类型', 'En': 'investment_type', 't': 'json', 'v': 'TZLX', 'dt': ''},
            {'n': '募集规模（万元）', 'En': 'collection_scale', 't': 'json', 'v': 'MPI_TOTAL_MONEY', 'dt': 'int'},
            {'n': '是否结构化', 'En': 'is_structured', 't': 'json', 'v': 'SFJGH', 'dt': ''},
            {'n': '初始委托人数量', 'En': 'start_client_nums', 't': 'json', 'v': 'MPI_PARTICIPATION_USER', 'dt': 'int'},
            {'n': '投资范围', 'En': 'MPI_GROUP_RATIO', 't': 'json', 'v': 'MPI_GROUP_RATIO', 'dt': ''},
            {'n': '产品ID', 'En': 'pro_id', 't': 'meta', 'v': 'MPI_ID', 'dt': ''}
        ]
        result = dict()
        for config in configs:
            if config['t']=='json':
                result[config['En']] = js[config['v']]
                if result[config['En']]:
                    result[config['En']] = S.replace_all(result[config['En']])
                    result[config['En']] = S.changdt(result[config['En']],config['dt'])
        result['pro_id'] = response.meta['MPI_ID']
        item['keys'] = ['pro_No']
        item['db'] = 'AMAC.Futures_Prod'
        item['result'] = result
        yield item