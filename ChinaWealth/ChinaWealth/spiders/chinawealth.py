# -*- coding: utf-8 -*-
import scrapy
from user_agent import generate_user_agent
import json
from .myselector import Selector as S
import time 
from ChinaWealth.items import ChinawealthItem


class ChinawealthSpider(scrapy.Spider):
    name = "chinawealth"
    allowed_domains = ["chinawealth.com.cn"]
    start_urls = ['http://chinawealth.com.cn/']
    page1 = 1
    page2 = 1
    page3 = 1
    page4 = 1
    configs = [ #{'n':'','En':'','t':'json','v':'bqjz','dt':''},
                {'n':'产品登记编码','En':'prod_code','t':'json','v':'cpdjbm','dt':''},
                {'n':'产品名称','En':'prod_name','t':'json','v':'cpms','dt':''},
                {'n':'产品代码','En':'prod_No','t':'json','v':'cpdm','dt':''},
                {'n':'投资者类型','En':'investor_type','t':'json','v':'tzzlxms','dt':''},
                {'n':'产品状态','En':'prod_status','t':'json','v':'cpztms','dt':''},
                {'n':'产品运作模式','En':'run_modle','t':'json','v':'cpyzmsms','dt':''},
                {'n':'起始销售金额','En':'start_sale_money','t':'json','v':'qdxsje','dt':'int'},
                {'n':'募集起始日期','En':'Raise_start_date','t':'json','v':'mjqsrq','dt':'date'},
                {'n':'产品起始日期','En':'prod_start_date','t':'json','v':'cpqsrq','dt':'date'},
                {'n':'初始净值','En':'initial_net_value','t':'json','v':'csjz','dt':''},
                {'n':'预期最低收益率','En':'EX_yield_MINrate','t':'json','v':'yjkhzdnsyl','dt':'float'},
                {'n':'产品期限','En':'prod_days_limit','t':'json','v':'cpqx','dt':'int'},
                {'n':'产品收益类型','En':'yieldType','t':'json','v':'cpsylxms','dt':''},
                {'n':'募集币种','En':'Raise_currency','t':'json','v':'mjbz','dt':''},
                {'n':'风险等级','En':'risk_level','t':'json','v':'cpfxdj','dt':''},
                {'n':'募集结束日期','En':'Raise_end_date','t':'json','v':'mjjsrq','dt':'date'},
                {'n':'产品终止日期','En':'prod_end_date','t':'json','v':'cpyjzzrq','dt':'date'},
                # {'n':'','En':'','t':'json','v':'fxdjms','dt':''},
                {'n':'产品净值','En':'prod_net_value','t':'json','v':'cpjz','dt':'float'},
                #{'n':'产品类型_code','En':'','t':'json','v':'cplx','dt':''},
               {'n':'产品类型','En':'','t':'json','v':'cplxms','dt':''},
                #{'n':'产品收益类型','En':'','t':'json','v':'cpsylx','dt':''},
                #{'n':'','En':'','t':'json','v':'cpxsqy','dt':''},
                {'n':'到期实际收益率','En':'Actual_yield_rate','t':'json','v':'dqsjsyl','dt':'float'},
                {'n':'业务起始日','En':'business_start_date','t':'json','v':'kfzqjsr','dt':'date'},
                {'n':'业务结束日','En':'business_end_date','t':'json','v':'kfzqqsr','dt':'date'},
                #{'n':'','En':'','t':'json','v':'qxdm','dt':''},
                #{'n':'期限类型','En':'','t':'json','v':'qxms','dt':''},
                {'n':'投资资产类型','En':'Investment_type','t':'json','v':'tzlxms','dt':''},
                #{'n':'','En':'','t':'json','v':'xsqy','dt':''},
                {'n':'预期最高收益率','En':'EX_yield_MAXrate','t':'json','v':'yjkhzgnsyl','dt':'float'},
                {'n':'发行机构名称','En':'publishOrg_name','t':'json','v':'fxjgms','dt':''},
                {'n':'发行机构代码','En':'publishOrg_code','t':'json','v':'fxjgdm','dt':''},
                {'n':'产品id','En':'prod_id','t':'json','v':'cpid','dt':''},
                ]
    configs2 = {}
    @staticmethod
    def madedata(tz,cpid):
         data = {"tzzlxdm":tz,
                "cpid":str(cpid),
                "cpjglb":"",
                "cpsylx":"",
                "cpyzms":"",
                "cpqx":"",
                "cpzt":"",
                "cpdjbm":"",
                "cpmc":"",
                "cpfxjg":"",
                "mjqsrq":"",
                "mjjsrq":"",
                "pagenum":"1"
                    }
         return data
    @staticmethod
    def madedata_start(tz,page):
         data = {
            'cpjglb':'',
            'cpsylx':'',
            'cpyzms':'',
            'cpfxdj':'',
            'cpqx':'',
            'cpzt':'',
            'cpdjbm': ' ',
            'cpmc':'',
            'cpfxjg':'',
            'mjqsrq':'',
            'mjjsrq':'',
            'areacode':'',
            'tzzlxdm':tz,
            'pagenum':str(page),
            'orderby':'',
            'code':'',
                }
         return data
    @staticmethod
    def madedata_after(tz,page):
        data = {
            'cpjglb':'',
            'cpsylx':'',
            'cpyzms':'',
            'cpfxdj':'',
            'cpqx':'',
            'cpzt':'',
            'cpdjbm': ' ',
            'cpmc':'',
            'cpfxjg':'',
            'mjqsrq':'',
            'mjjsrq':'',
            'areacode':'',
            'tzzlxdm':tz,
            'pagenum':str(page),
            'orderby':'',
            'code':'',
            'changeTableFlage':'0'
                }
        return data
    def start_requests(self):
        
        for tz in ["04","02","01","03"]:
            time.sleep(1)
            if tz == '01':
                data = self.madedata_start(tz,1)
                yield scrapy.FormRequest('http://www.chinawealth.com.cn/lccpAllProJzyServlet.go',
                                         formdata = data,
                                         headers = {'User-Agent':generate_user_agent()},
                                         callback=self.parse1)
            if tz == '02':
                data = self.madedata_start(tz,1)
                yield scrapy.FormRequest('http://www.chinawealth.com.cn/lccpAllProJzyServlet.go',
                                         formdata = data,
                                         headers = {'User-Agent':generate_user_agent()},
                                         callback=self.parse2)
            if tz == '03':
                data = self.madedata_start(tz,1)
                yield scrapy.FormRequest('http://www.chinawealth.com.cn/lccpAllProJzyServlet.go',
                                         formdata = data,
                                         headers = {'User-Agent':generate_user_agent()},
                                         callback=self.parse3)
            if tz == '04':
                data = self.madedata_start(tz,1)
                yield scrapy.FormRequest('http://www.chinawealth.com.cn/lccpAllProJzyServlet.go',
                                         formdata = data,
                                         headers = {'User-Agent':generate_user_agent()},
                                         callback=self.parse4)
    def parse1(self, response):
        js = json.loads(response.text)
        if self.page1 == 1:
            self.totalPages1 = js['Count']/500
#        print(js)
        for json_ in js['List']:

            result = dict()
            for config in self.configs:
                result[config['En']] = S.select_content(json_, config)
                if result[config['En']]:
                    result[config['En']] = S.replace_all(result[config['En']])
                    result[config['En']] = S.changdt(result[config['En']], config['dt'])
                else:
                    result[config['En']] = None
#            print(result)
            infodata = self.madedata("01",result['prod_id'])
            yield scrapy.FormRequest('http://www.chinawealth.com.cn/cpxsqyQuery.go',
                                     formdata = infodata,
                                     headers = {'User-Agent':generate_user_agent()},
                                     callback=self.infoparse,
                                     meta={'result':result})
        if self.page1<self.totalPages1:
            self.page1+=1
            nextdata = self.madedata_after("01",self.page1)
            yield scrapy.FormRequest('http://www.chinawealth.com.cn/lccpAllProJzyServlet.go',
                                         formdata = nextdata,
                                         headers = {'User-Agent':generate_user_agent()},
                                         callback=self.parse1,
                                         priority=1)
            
                        
    def parse2(self, response):
        js = json.loads(response.text)
        if self.page2 == 1:
            self.totalPages2 = js['Count']/500
        for json_ in js['List']:

            result = dict()
            for config in self.configs:
                result[config['En']] = S.select_content(json_, config)
                if result[config['En']]:
                    result[config['En']] = S.replace_all(result[config['En']])
                    result[config['En']] = S.changdt(result[config['En']], config['dt'])
                else:
                    result[config['En']] = None
#            print(result)
            infodata = self.madedata("02",result['prod_id'])
            yield scrapy.FormRequest('http://www.chinawealth.com.cn/cpxsqyQuery.go',
                                     formdata = infodata,
                                     headers = {'User-Agent':generate_user_agent()},
                                     callback=self.infoparse,
                                     meta={'result':result})
        if self.page2<self.totalPages2:
            self.page2+=1
            nextdata = self.madedata_after("01",self.page2)
            yield scrapy.FormRequest('http://www.chinawealth.com.cn/lccpAllProJzyServlet.go',
                                         formdata = nextdata,
                                         headers = {'User-Agent':generate_user_agent()},
                                         callback=self.parse2,
                                         priority=1)
    def parse3(self, response):
        js = json.loads(response.text)
        if self.page3 == 1:
            self.totalPages3 = js['Count']/500
        for json_ in js['List']:

            result = dict()
            for config in self.configs:
                result[config['En']] = S.select_content(json_, config)
                if result[config['En']]:
                    result[config['En']] = S.replace_all(result[config['En']])
                    result[config['En']] = S.changdt(result[config['En']], config['dt'])
                else:
                    result[config['En']] = None
#            print(result)
            infodata = self.madedata("03",result['prod_id'])
            yield scrapy.FormRequest('http://www.chinawealth.com.cn/cpxsqyQuery.go',
                                     formdata = infodata,
                                     headers = {'User-Agent':generate_user_agent()},
                                     callback=self.infoparse,
                                     meta={'result':result},
                                     )
        if self.page3<self.totalPages3:
            self.page3+=1
            nextdata = self.madedata_after("03",self.page3)
            yield scrapy.FormRequest('http://www.chinawealth.com.cn/lccpAllProJzyServlet.go',
                                         formdata = nextdata,
                                         headers = {'User-Agent':generate_user_agent()},
                                         callback=self.parse3,
                                         priority=1)
    def parse4(self, response):
        js = json.loads(response.text)
        if self.page4 == 1:
            self.totalPages4 = js['Count']/500
        for json_ in js['List']:

            result = dict()
            for config in self.configs:
                result[config['En']] = S.select_content(json_, config)
                if result[config['En']]:
                    result[config['En']] = S.replace_all(result[config['En']])
                    result[config['En']] = S.changdt(result[config['En']], config['dt'])
                    
                else:
                    result[config['En']] = None
#            print(result)
            infodata = self.madedata("04",result['prod_id'])
            yield scrapy.FormRequest('http://www.chinawealth.com.cn/cpxsqyQuery.go',
                                     formdata = infodata,
                                     headers = {'User-Agent':generate_user_agent()},
                                     callback=self.infoparse,
                                     meta={'result':result}
                                     )
        if self.page4<self.totalPages4:
            self.page4+=1
            nextdata = self.madedata_after("01",self.page4)
            yield scrapy.FormRequest('http://www.chinawealth.com.cn/lccpAllProJzyServlet.go',
                                         formdata = nextdata,
                                         headers = {'User-Agent':generate_user_agent()},
                                         callback=self.parse4,
                                         priority=1)
    def infoparse(self, response):
        item = ChinawealthItem()
        result = response.meta['result']
        js = json.loads(response.text)
        qy = list()
#        print(js)
        try:
            print('%s/%s,%s/%s,%s/%s,%s/%s'%(self.page1,self.totalPages1,self.page2,self.totalPages2,self.page3,self.totalPages3,self.page4,self.totalPages4))
        except:
            pass
        for json_ in js['List']:
            if json_ and json_['cpxsqy']:
                qy.append(json_['cpxsqy'])
        if qy:
            result['saleAreas'] = ",".join(qy)
        item['result'] = result
        item['db'] = 'China_Wealth_product'
        item['keys'] = ['prod_code']
        yield item