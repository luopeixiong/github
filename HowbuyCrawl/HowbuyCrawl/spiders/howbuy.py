# -*- coding: utf-8 -*-
import scrapy
from .myselector import Selector as S
import re
from scrapy import Selector as S1
import time
from HowbuyCrawl.items import HowbuycrawlItem
from scrapy import Request,FormRequest
class HowbuySpider(scrapy.Spider):
    name = "howbuy"
    allowed_domains = ["howbuy.com"]
    start_urls = [
                  'https://www.howbuy.com/fund/company/',
                  'https://simu.howbuy.com/company/',
                  'https://simu.howbuy.com/mlboard.htm',
                  'https://www.howbuy.com/fund/manager/',
                  'https://simu.howbuy.com/manager/'
                  ]
    cookies = {"simu_qualified_v2": "5"}
    CompanyPage = 1
    compangperPage = 20
    FundPage = 1
    FundPerPage = 20
    ManagerPage = 1
    ManagerPerPage = 20
    _Request = 0
    _items = 0
    
    def foo(func):
        """
        装饰器函数,统计request总数,以及item返回总数
        """
        def foo2(self,*args,**kwargs):
            results = func(self,*args,**kwargs)
            for i in results.__iter__():
                if isinstance(i,Request) or isinstance(i,FormRequest):
                    self._Request+=1
                if isinstance(i,HowbuycrawlItem):
                    self._items+=1
                yield i
                
            
        return foo2
    def madecompanydata(self,page,perPage=20,allPage=''):
#        """构造howbuy 私募基金公司列表页post 表单"""
        data = {"orderType": "Desc",
                "sortField": "hb1nscclzyjj",
                "ejflsccl": "",
                "djbh": "",
                "skey": "",
                "page": str(page),
                "perPage": str(perPage),
                "allPage": str(allPage),
                "targetPage": ""}
        return data
    def madefundProdListdata(self,page,perPage=20,allPage=''):
#        """构造howbuy 私募基金产品列表页post 表单"""
        data = {"orderType": "Desc",
                "sortField": "hb1n",
                "ejfl": "",
                "sylx": "J",
                "gzkxd": "1",
                "jgxs": "",
                "skey": "",
                "page": str(page),
                "perPage": str(perPage),
                "allPage": str(allPage),
                "targetPage": ""}
        return data
    def madeManagerListdata(self,page,perPage=20,allPage=''):
#        """构造howbuy 私募基金经理列表页post 表单"""        
        data = {"cynxRang":"",
                "orderType":"Desc",
                "sortField":"hb1nscclzyjj",
                "ejflsccl":"",
                "jjjlly":"",
                "skey":"",
                "page":str(page),
                "perPage":str(perPage),
                "allPage":str(allPage),
                "targetPage":"",
                }
        return data
    @foo
    def start_requests(self):
        for url in self.start_urls:
            headers = S.headers()
            if url == 'https://simu.howbuy.com/company/':
                """公司列表"""
                data = self.madecompanydata(self.CompanyPage,self.compangperPage)
                yield scrapy.FormRequest(url,
                                     method = 'POST',
                                     formdata=data,
                                     cookies = self.cookies,
                                     headers = headers,
                                     priority = 1,
                                     callback = self.companyListParse
                                     )
            if url == 'https://simu.howbuy.com/mlboard.htm':
                """私募产品"""
                data = self.madefundProdListdata(self.FundPage,self.FundPerPage)
                yield scrapy.FormRequest(url,
                                         method = 'POST',
                                         formdata = data,
                                         cookies = self.cookies,
                                         headers = headers,
                                         priority = 1,
                                         callback = self.fundListParse)
            if url in ['https://simu.howbuy.com/manager/','https://www.howbuy.com/fund/manager/']:
                """私募经理"""
                data = self.madeManagerListdata(self.ManagerPage,self.ManagerPerPage)
                yield scrapy.FormRequest(url,
                                         method = 'POST',
                                         formdata = data,
                                         cookies = self.cookies,
                                         headers = headers,
                                         priority = 1,
                                         callback = self.ManagerListParse)
    def parse(self, response):
        print(response.text)
        pass
    @foo
    def companyListParse(self, response):
#        print(response.text)
        if self.CompanyPage == 1:
            self.CompanyTotalPages  = int(response.xpath('//input[@name="allPage"]/@value').extract_first())
        configs = [
                    {'n':'公司名称','En':'fund_company_name','t':'xpath_first','v':'td[2]/a[@target]/text()','dt':''},
                    {'n':'公司拼音(对应网站URLpath路径)','En':'fund_company_ID','t':'xpath_first','v':'td[2]/a[@target]/@href','dt':''},
                    {'n':'所在地区','En':'company_location','t':'xpath_first','v':'td[3]/text()','dt':''},
                    {'n':'成立时间','En':'setup_time','t':'xpath_first','v':'td[4]/text()','dt':''},
#                    {'n':'明星经理','En':'stars_manager_name','t':'xpath_first','v':'td[5]/a/text()','dt':''},
#                    {'n':'明星经理拼音(同公司)','En':'stars_manager_ID','t':'xpath_first','v':'td[5]/a/@href','dt':''},
                    {'n':'基金数量','En':'manage_fund_pro_nums','t':'xpath_first','v':'td[6]/table/td[1]/a/text()','dt':''},
                    {'n':'代表基金简称','En':'behalf_fund_name','t':'xpath_first','v':'td[6]/table/td[2]/a/text()','dt':''},
                    {'n':'代表基金拼音(同公司)','En':'behalf_fund_ID','t':'xpath_first','v':'td[6]/table/td[2]/a/@href','dt':''}
                    ]
        for info in response.xpath('//tr[@class="tr_normal"]'):
            result = dict()
            for config in configs:
                result[config['En']] = S.select_content(info, config)
                result[config['En']] = S.replace_all(result[config['En']]) if result[config['En']] else None
            result['fund_company_ID'] = result['fund_company_ID'].split('/')[-2] if result['fund_company_ID'] else None
#            result['stars_manager_ID'] = result['stars_manager_ID'].split('/')[-1][:-5] if result['stars_manager_ID'] else None
            result['behalf_fund_ID'] = result['behalf_fund_ID'].split('/')[-2]  if result['behalf_fund_ID'] else None
            companyID = result['fund_company_ID']
            if companyID:
                nexturl = 'https://simu.howbuy.com/{companyID}/'.format(companyID = companyID)
                headers = S.headers()
                yield scrapy.Request(nexturl,
                                     method='GET',
                                     cookies = self.cookies,
                                     headers = headers,
                                     meta = {'result':result},
                                     priority = 0,
                                     callback = self.companyInfoParse)
        if self.CompanyPage<self.CompanyTotalPages:
            self.CompanyPage+=1
            headers = S.headers()
            data = self.madecompanydata(self.CompanyPage,self.compangperPage,self.CompanyTotalPages)
            url = 'https://simu.howbuy.com/company/'
            yield scrapy.FormRequest(url,
                                 method = 'POST',
                                 formdata=data,
                                 cookies = self.cookies,
                                 headers = headers,
                                 priority = 100,
                                 callback = self.companyListParse
                                 )
    @foo
    def companyInfoParse(self, response):
        """
        this is company_members parse and company_info parse
        """
        item = HowbuycrawlItem()
        item2 = HowbuycrawlItem()
        result = response.meta['result']
        configs = [
                {'n':'备案证号','En':'record_number','t':'xpath_first','v':'//li[text()="备案证号："]/span/text()','dt':''},
#                {'n':'所在区域','En':'','t':'xpath_first','v':'','dt':''},
#                {'n':'成立日期','En':'','t':'xpath_first','v':'','dt':''},
#                {'n':'旗下经理','En':'','t':'xpath_first','v':'','dt':''},
                {'n':'公司类型','En':'fund_company_type','t':'xpath_first','v':'//li[contains(text(),"公司类型：")]/text()','dt':''},
#                {'n':'核心人物','En':'','t':'xpath_first','v':'','dt':''},
#                {'n':'旗下基金','En':'','t':'xpath_first','v':'','dt':''},
                {'n':'注册资本','En':'registered_capital','t':'xpath_first','v':'//li[contains(text(),"注册资本：")]/span/text()','dt':''},
#                {'n':'成立时间（年）','En':'','t':'xpath_first','v':'','dt':''},
#                {'n':'投研团队（人）','En':'','t':'xpath_first','v':'','dt':''},
#                {'n':'基金数量（只）','En':'','t':'xpath_first','v':'','dt':''},
                {'n':'投资理念','En':'Investment_philosophy','t':'xpath_first','v':'//div[@class="review_rt lt"]/text()','dt':''}
#                {'n':'','En':'','t':'xpath_first','v':'','dt':''},
                
                ]
        for config in configs:
            result[config['En']] = S.select_content(response, config)
            result[config['En']] = S.replace_all(result[config['En']])
        result['fund_company_type'] = result['fund_company_type'].replace('公司类型：','') if hasattr(result['fund_company_type'],'replace') else None
#        print(result)
        item2['result'] = result
        item['db'] = ''
        item['keys'] = []
        yield item
        
        configs2 = [{'n':'名称','En':'name','t':'xpath_first','v':'div[1]/img/@alt','dt':''},
                    {'n':'ID','En':'ID','t':'xpath_first','v':'div[2]/p[1]/a/@href','dt':''},
                    {'n':'职位','En':'position','t':'xpath_first','v':'div[2]/p[1]/text()[last()]','dt':''},
                    {'n':'简介','En':'introduction','t':'xpath_first','v':'div[2]/p[2]/text()[last()]','dt':''},
                    {'n':'标签','En':'label','t':'other','v':'','dt':''}
                    ]
                    
#        """获取公司成员信息"""
#        "截取基金经理response"
#        result = re.search('(?=<!--基金经理-->\s+)(.+?)(?=<!--.*?-->)',res.text,re.S).group()
        manager_response = re.search('(?=<!--基金经理-->\s+)(.+?)(?=<!--.*?-->)',response.text,re.S).group(0)
        
#        "截取其他核心人物 response"
#        result = re.search('(?=<!--其他团队成员-->\s+)(.+?)(?=<!--.*?-->)',res.text,re.S).group()
        other_import_emp_response = re.search('(?=<!--其他核心人物-->\s+)(.+?)(?=<!--.*?-->)',response.text,re.S).group(0)
#        "截取其他团队成员 response"
#        result = re.search('(?=<!--其他核心人物-->\s+)(.+?)(?=<!--.*?-->)',res.text,re.S).group()
        other_emp_response = re.search('(?=<!--其他核心人物-->\s+)(.+?)(?=<!--.*?-->)',response.text,re.S).group(0)
        response1 = S1(text = manager_response)
        response2 = S1(text = other_import_emp_response)
        response3 = S1(text = other_emp_response)
        for cont in [response1,response2,response3]:
            
            for info in cont.xpath("//div[@class='people_list clearfix']"):
#                print(info)
                result = dict()
                for config in configs2:
                    result[config['En']] = S.select_content(info,config)
                    result[config['En']] = S.replace_all(result[config['En']])
                result['label'] = S.select_content(cont,{'n':'标签','En':'label','t':'xpath_first','v':'//em/text()','dt':''})
                
                if result['name']:
                    item['result'] = result
                    item['db'] = ''
                    item['keys'] = []
                    yield item
#        print(manager_response)
    @foo
    def fundListParse(self, response):
#        print(response.text)
        if self.FundPage == 1:
            self.FundTotalPages = int(response.xpath('//input[@name="allPage"]/@value').extract_first())
            print(self.FundTotalPages)
        configs = [
                {'n':'基金简称','En':'fund_short_name','t':'xpath_first','v':'td[3]/a/text()','dt':''},
                {'n':'基金产品URL','En':'fund_prod_url','t':'xpath_first','v':'td[3]/a/@href','dt':''},
#                {'n':'基金类型','En':'fund_prod_type','t':'xpath_first','v':'td[4]/text()','dt':''},
#                {'n':'','En':'','t':'xpath_first','v':'','dt':''},
                    ]
                
        result = dict()
        for info in response.xpath('//table[@id="spreadDetails"]/tr'):        
            for config in configs:
                result[config['En']] = S.select_content(info, config)
                result[config['En']] = S.replace_all(result[config['En']])
            fundProdUrl = result['fund_prod_url']
            if fundProdUrl:
                headers = S.headers()
                fund_Prod_ID = fundProdUrl.split('/')[-2]
                yield scrapy.Request(fundProdUrl,
                                     headers = headers,
                                     cookies = self.cookies,
                                     callback = self.fundProdInfoParse,
                                     priority = 3,
                                     meta = {'fund_Prod_ID':fund_Prod_ID},
                                     )
#            return False
        if self.FundPage < self.FundTotalPages:
            self.FundPage+=1
            headers = S.headers()
            data = self.madefundProdListdata(self.FundPage,self.FundPerPage,self.FundTotalPages)
            url = 'https://simu.howbuy.com/mlboard.htm'
            yield scrapy.FormRequest(url,
                                 method = 'POST',
                                 formdata=data,
                                 cookies = self.cookies,
                                 headers = headers,
                                 priority = 100,
                                 callback = self.fundListParse
                                 )
    @foo       
    def fundProdInfoParse(self, response):
#        print(response.text)
        item = HowbuycrawlItem()
        configs = [
                     {'n':'基金简称','En':'fund_short_name','t':'xpath_first','v':'//h1[@class="fl"]/text()','dt':''},
                     {'n':'基金ID','En':'fund_Prod_ID','t':'meta','v':'fund_Prod_ID','dt':''},
#                    {'n':'累计净值','En':'','t':'xpath_first','v':'','dt':''},
#                    {'n':'成立日期','En':'','t':'xpath_first','v':'','dt':''},
                    {'n':'基金公司','En':'fund_company_name','t':'xpath_first','v':'//p[@class="p3" and text()="基金公司:"]/a/text()','dt':''},
                    {'n':'基金公司拼音','En':'fund_company_ID','t':'xpath_first','v':'//p[@class="p3" and text()="基金公司:"]/a/@href','dt':''},
#                    {'n':'基金类型','En':'','t':'xpath_first','v':'','dt':''},
#                    {'n':'备案号','En':'fund_record_number','t':'xpath_first','v':'//p[@class="p2" and text()="备案号:"]/span/text()','dt':''},
                    {'n':'基金经理','En':'manager_name','t':'xpath_first','v':'//p[@class="p3" and text()="基金经理:"]/span/a/text()','dt':''},
                    {'n':'基金经理拼音','En':'manager_ID','t':'xpath_first','v':'//p[@class="p3" and text()="基金经理:"]/span/a/@href','dt':''},
                    {'n':'基金全称','En':'fund_full_name','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="基金全称"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'基金类型','En':'fund_type','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="基金类型"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'组织形式','En':'fund_org_form','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="组织形式"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'托管银行','En':'trustee_bank','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="托管银行"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'开放日期','En':'open_date','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="开放日期"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'币种','En':'currency','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="币种"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'封闭期','En':'closed_date','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="封闭期"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'备案号','En':'fund_record_number','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="备案号"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'成立日期','En':'fund_setup_date','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="成立日期"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'结构形式','En':'structural_style','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="结构形式"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'基金发行人','En':'fund_issure','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="基金发行人"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'基金状态','En':'fund_status','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="基金状态"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'净值单位','En':'assert_uion','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="净值单位"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'准封闭期','En':'Quasi_closed_period','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="准封闭期"]/following-sibling::td[1]/text()','dt':''},
                    {'n':'风险等级','En':'risk_level','t':'xpath_first','v':'//td[contains(@class,"tdbg") and text()="风险等级"]/following-sibling::td[1]/text()','dt':''}
                    ]
        result = dict()
        for config in configs:
            result[config['En']] = S.select_content(response, config)
            result[config['En']] = S.replace_all(result[config['En']]) if S.replace_all(result[config['En']]) else None
        result['manager_ID'] = result['manager_ID'].split('/')[-1][:-5] if result['manager_ID'] else None
        result['fund_company_ID'] = result['fund_company_ID'].split('/')[-1] if result['fund_company_ID'] else None
        item['result'] = result
        item['db'] = ''
        item['keys'] = []
        yield item
        
        
#        """获取产品数据"""
        if result['fund_Prod_ID']:
            headers =S.headers()
            #"""本基金,沪深300,好买对冲指数"""
            js1 = 'https://static.howbuy.com/min/f=/upload/auto/script/fund/smhb_%s_v1039.js'%result['fund_Prod_ID']
            #"""单位净值,日涨幅，回撤"""
            js2 = 'https://static.howbuy.com/min/f=/upload/auto/script/fund/smrhc_%s_v%s.js'%(result['fund_Prod_ID'],int(100*time.time()))
            #"""月度回报"""
            js3 = 'https://static.howbuy.com/??/upload/auto/script/fund/smydhb_%s.js'%result['fund_Prod_ID']
            #2017,8,22,1.437,0.1799,0.0629,2.437,3837.7304,2491.8927
            
            yield scrapy.Request(js1,
                                 headers = headers,
                                 cookies = self.cookies,
                                 priority = 0,
                                 callback = self.Profit_dataParse)
            
            #2.437,-13.43,2017,09,22,2.437,2.437  
            yield scrapy.Request(js2,
                                 headers = headers,
                                 cookies = self.cookies,
                                 priority = 0,
                                 callback = self.retracementParse)
    @foo
    def Profit_dataParse(self, response):
        """
            this is fund Profit data parse
        
        """
        item = HowbuycrawlItem()
        datas = re.findall("navList:(\[.*?\])",response.text)[0]
        datas = eval(datas)
        def fo(x,y):
            try:
                a = round(float(x),y)
                return a
            except:
                pass
        for data in datas:
            result = dict()
            datalist = data.split(",")
#            print(datalist)
            datalist[1]=str(int(datalist[1])+1)
            result['date'] = "-".join(map(lambda x:"0"+x if len(x)==1 else x,datalist[0:3]))
            result['assert_value'] = fo(datalist[6],4)
            result['hs300'] = fo(datalist[7],4)
            result['howbuy'] = fo(datalist[8],4)
            result['up_rate1'] = fo(datalist[3],4)
            result['up_rate2'] = fo(datalist[4],4)
            result['up_rate3'] = fo(datalist[5],4)
#            print(result)
            item['result'] = result
            item['db'] = ''
            item['keys'] = []
            yield item
    @foo
    def retracementParse(self, response):
        """
            this is fund retracement data parse
        
        """
        item = HowbuycrawlItem()
        def fo(x,y):
            return round(float(x),y)
        datas = eval(re.findall("navList:(\[.*?\])",response.text)[0])
        for data in datas:
            result = dict()
            datalist = data.split(",")
#            print(datalist)
#            datalist[3]=str(int(datalist[3])+1)
            result['date'] = "-".join(map(lambda x:"0"+x if len(x)==1 else x,datalist[2:5]))
            result['assert_value'] = fo(datalist[5],4)
            result['Accumulated_Net'] = fo(datalist[6],4)
            result['Retracement_rate'] = fo(datalist[1],4)
            #result['up'] = datalist[0]
#            print("%s  %s-%s-%s,j:%s,l:%s,hc:%s,up:%s"%(jjdm,datalist[2],datalist[3],datalist[4],datalist[5],datalist[6],datalist[1],datalist[0]))
#            item['result']=result            
#            yield item
#            print(result)
            item['result'] = result
            item['db'] = ''
            item['keys'] = []
            yield item
    @foo
    def ManagerListParse(self, response):
#        print(response.text)

        if self.ManagerPage == 1:
            self.ManagerTotalPages = int(response.xpath('//input[@name="allPage"]/@value').extract_first())
            print(self.ManagerTotalPages)
        configs = [
                    {'n':'基金经理','En':'manager_name','t':'xpath_first','v':'td[3]/a/text()','dt':''},
                    {'n':'基金经理ID','En':'manager_id','t':'xpath_first','v':'td[3]/a/@href','dt':''},
#                    {'n':'从业年限','En':'','t':'xpath_first','v':'','dt':''},
#                    {'n':'履历背景','En':'','t':'xpath_first','v':'','dt':''},
                    ]
        for info in response.xpath('//div[@class="fund_list"]/table/tbody/tr'):
            result = dict()
            for config in configs:
                result[config['En']] = S.select_content(info, config)
            result['manager_id'] = result['manager_id'].split("/")[-1][:-5] if result['manager_id'] else None
            managerUrl = 'https://simu.howbuy.com/manager/{manager_id}.html'.format(manager_id=result['manager_id'])
            headers = S.headers()
            yield scrapy.Request(managerUrl,
                                 headers = headers,
                                 method = 'GET',
                                 cookies=self.cookies,
                                 priority = 3,
                                 callback = self.managerInfoParse
                                 )
        if self.ManagerPage < self.ManagerTotalPages:
            self.ManagerPage+=1
            headers = S.headers()
            data = self.madeManagerListdata(self.ManagerPage,self.ManagerPerPage)
            url = 'https://simu.howbuy.com/manager/'
            yield scrapy.FormRequest(url,
                                     method = 'POST',
                                     formdata = data,
                                     cookies = self.cookies,
                                     headers = headers,
                                     priority = 100,
                                     callback = self.ManagerListParse)
    @foo
    def managerInfoParse(self, response):
#        print(response.url)
        """
        this is manager parse
        """
        item = HowbuycrawlItem()
        configs = [
                     {'n':'基金经理姓名','En':'manager_name','t':'xpath_first','v':'//div[@class="manager_name"]/text()','dt':''},
                     {'n':'基金经理ID','En':'manager_ID','t':'url','v':'','dt':''},
                     {'n':'所在公司','En':'fund_company_name','t':'xpath_first','v':'//a[@id="szgs"]/text()','dt':''},
                     {'n':'所在公司ID','En':'fund_company_id','t':'xpath_first','v':'//a[@id="szgs"]/@href','dt':''},
                     {'n':'擅长类型','En':'Excel_type','t':'xpath_first','v':'//li[text()="擅长类型: "]/span/text()','dt':''},
                     {'n':'代表基金','En':'behalf_fund_name','t':'xpath_first','v':'//li[text()="代表基金: "]/a/text()','dt':''},
                     {'n':'代表基金ID','En':'behalf_fund_ID','t':'xpath_first','v':'//li[text()="代表基金: "]/a/@href','dt':''},
                     {'n':'所获奖项','En':'Awards','t':'xpath_first','v':'//li[text()="所获奖项: "]/span/text()','dt':''},
                     {'n':'简介','En':'introduction','t':'xpath_first','v':'//div[@class="des_con"]/text()','dt':''},
                     {'n':'从业年限','En':'employ_years','t':'xpath_first','v':'//td[text()="从业年限"]/following-sibling::td[1]/text()','dt':''},
                     {'n':'履历背景','En':'background','t':'xpath_first','v':'//td[text()="履历背景"]/following-sibling::td[1]/text()','dt':''},
                     {'n':'年均回报','En':'Annual_return','t':'xpath_first','v':'//td[text()="年均回报"]/following-sibling::td[1]/span/text()','dt':''},
                     {'n':'过往履历','En':'Past_experience','t':'xpath_first','v':'//ul[contains(text(),"过往履历")]/text()','dt':''},
                     {'n':'任职私募年限','En':'Tenure_of_private_equity','t':'xpath_first','v':'//td[text()="任职私募年限"]/following-sibling::td[1]/text()','dt':''},
                     {'n':'任职私募日期','En':'Private_placement_date','t':'xpath_first','v':'//td[text()="任职私募日期"]/following-sibling::td[1]/text()','dt':''},
                     {'n':'管理基金数量','En':'manage_fund_nums','t':'xpath_first','v':'//td[text()="管理基金数量"]/following-sibling::td[1]/text()','dt':''},
                     
                     ]
        result = dict()
        for config in configs:
            result[config['En']] = S.select_content(response, config)
            result[config['En']] = S.replace_all(result[config['En']]) if S.replace_all(result[config['En']]) else None
        result['manager_ID'] = result['manager_ID'].split("/")[-1][:-5]
        result['behalf_fund_ID'] = result['behalf_fund_ID'].split("/")[-2] if hasattr(result['behalf_fund_ID'],'split') else None
        result['fund_company_id'] = result['fund_company_id'].split("/")[-2]  if hasattr(result['fund_company_id'],'split') else None
        item['result'] = result
        item['db'] = ''
        item['keys'] = []
        yield item
        

    def close(self, spider, reason):
        print("At this project ,Total get Item %s,sucess Request %s"%(self._items, self._Request))
        closed = getattr(spider, 'closed', None)
        if callable(closed):
            return closed(reason)
        