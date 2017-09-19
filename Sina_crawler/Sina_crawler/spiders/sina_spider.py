# -*- coding: utf-8 -*-
import scrapy
#from urllib.parse import urlencode
import requests
s = requests.Session()
from user_agent import generate_user_agent
import json
import re
from Sina_crawler.items import SinaCrawlerItem
#from scrapy import log
from myselector import Selector as S
import time


class SinaSpiderSpider(scrapy.Spider):
    name = "sina_spider"
    allowed_domains = ["sina.com.cn"]
    Boardsdict = {"hs_a":"全部A股","zxqy":"中小板","cyb":"创业板"}
    Boards = ["hs_a","zxqy","cyb"]   
    base_headers = {"user-agent":generate_user_agent()}
    stockcodes = []
    custom_settings = {
            "CONCURRENT_REQUESTS_PER_IP":1,
            "CONCURRENT_REQUESTS_PER_DOMAIN":1,
            "DOWNLOAD_DELAY":2,
#            'ITEM_PIPELINES':{'Sina_crawler.pipelines.SinaSpidersPipeline': 300}
            }
    
    start_urls = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php/?__s=[[%22hq%22,%22{board}%22,%22%22,0,{page},40]]"
    def start_requests(self):
        for Board in self.Boards[2:]:
            url = self.start_urls.format(board=Board,page=1)
            yield scrapy.Request(url,
                                 method = 'GET',
                                 meta = {"board":Board,"page":1,'total':None},
                                 dont_filter = True,
                                 headers = self.base_headers,
                                )
    def parse(self, response):
        item = SinaCrawlerItem()
        Board = response.meta['board']
        BoardName = self.Boardsdict[Board]
        page = response.meta["page"]
        totalcount = response.meta['total']
        try:
            items = json.loads(response.text)[0]
        except:
            pass
        try:
            totalcount = items['count']/40
        except:
            pass
        try:
            items = json.loads(response.text)[0]
        except:
            print("None item")
        result={}
        try:
            print(BoardName,page,totalcount)
            for item_ in items['items']:
                result['StockCode']=item_[1]
                result['StockName']=item_[2]
                result['BoardName']=BoardName
                item['result'] = result
                if result['StockCode'] not in self.stockcodes:
                    self.stockcodes.append(result['StockCode'])
                    for url in ["http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/{code}.phtml",#上市公司基本信息
                            "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockStructure/stockid/{code}.phtml",#股权变动
                            "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockHolder/stockid/{code}.phtml",#主要股东
                            "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CirculateStockHolder/stockid/{code}.phtml",#流动股东
                            "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpManager/stockid/{code}.phtml",#基金高管
                            "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_FundStockHolder/stockid/{code}.phtml"#基金持有人
                            ]:
                        nexturl = url.format(code=result['StockCode'])
#                        print(nexturl)
                        headers = {"User-Agent":generate_user_agent()}
                        if "vCI_CorpInfo" in url:
                            yield scrapy.Request(nexturl,
                                                 callback=self.CorpInfoParse,
                                                 headers = headers,
                                                 meta={"code":result['StockCode']})
                        if "vCI_StockStructure" in url:
                            yield scrapy.Request(nexturl,
                                                 callback=self.StockStructureParse,
                                                 headers = headers,
                                                 meta={"code":result['StockCode']})
                        if "vCI_StockHolder" in url:
                            yield scrapy.Request(nexturl,
                                                 callback=self.StockHolderParse,
                                                 headers = headers,
                                                 meta={"code":result['StockCode']})
                        if "vCI_CirculateStockHolder" in url:
                            yield scrapy.Request(nexturl,
                                                 callback=self.CirculateStockHolderParse,
                                                 headers = headers,
                                                 meta={"code":result['StockCode']})
                        if "vCI_CorpManager" in url:
                            yield scrapy.Request(nexturl,
                                                 callback=self.CorpManagerParse,
                                                 headers = headers,
                                                 meta={"code":result['StockCode']})
                        if "vCI_FundStockHolder" in url:
                            yield scrapy.Request(nexturl,
                                                 callback=self.FundStockHolderParse,
                                                 headers = headers,
                                                 meta={"code":result['StockCode']})
                item['keys'] = []
                item['db'] = ''
                yield item
                
            if page<totalcount:
                page += 1
                url = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php/?__s=[[%22hq%22,%22{board}%22,%22%22,0,{page},40]]".format(board=Board,page=page)
                yield scrapy.Request(url,
                                     meta = {"board":Board,"page":page,"total":totalcount},
                                     headers = self.base_headers,
                                     dont_filter = True,
                                     callback = self.parse)
                
        except:
            url = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php/?__s=[[%22hq%22,%22{board}%22,%22%22,0,{page},40]]".format(board=Board,page=page)
            yield scrapy.Request(url,
                                 meta = {"board":Board,"page":page,"total":totalcount},
                                 headers = self.base_headers,
                                 dont_filter = True,
                                 callback = self.parse)
      
    def CorpInfoParse(self, response):
        item = SinaCrawlerItem()
        configs = [{"name":"公司名称","ename":"company_name","type":"xpath","value":"//td[text()='公司名称：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"股票代码","ename":"stock_name","type":"xpath","value":"//h1[@id='stockName']/text()[1]",'data_type':""},                                                                 
                  {"name":"公司代码","ename":"stock_code","type":"","value":"",'data_type':""},
                  {"name":"公司英文名称","ename":"stock_ename","type":"xpath","value":"//td[text()='公司英文名称：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"上市市场","ename":"Listed_market","type":"xpath","value":"//td[text()='上市市场：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"发行价格","ename":"Issue_price","type":"xpath","value":"//td[text()='发行价格：']/following-sibling::*[1]/text()",'data_type':"float"},
                  {"name":"成立日期","ename":"set_up_time","type":"xpath","value":"//td[text()='成立日期：']/following-sibling::*[1]/a/text()",'data_type':""},
                  {"name":"机构类型","ename":"institution_type","type":"xpath","value":"//td[text()='机构类型：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"董事会秘书","ename":"Board_Secretary","type":"xpath","value":"//td[text()='董事会秘书：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"董秘电话","ename":"Secretary_tel_numbers","type":"xpath","value":"//td[text()='董秘电话：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"董秘传真","ename":"Secretary_fax","type":"xpath","value":"//td[text()='董秘传真：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"董秘电子邮箱","ename":"Secretary_email","type":"xpath","value":"//td[text()='董秘电子邮箱：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"邮政编码","ename":"Postal_Code","type":"xpath","value":"//td[text()='邮政编码：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"证券简称更名历史","ename":"history_change_name","type":"xpath","value":"//td[text()='证券简称更名历史：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"注册地址","ename":"Registered_address","type":"xpath","value":"//td[text()='注册地址：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"办公地址","ename":"Office_address","type":"xpath","value":"//td[text()='办公地址：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"公司简介","ename":"Company_profile","type":"xpath","value":"//td[text()='公司简介：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"经营范围","ename":"business_Scope","type":"xpath","value":"//td[text()='经营范围：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"上市日期","ename":"Listing_date","type":"xpath","value":"//td[text()='上市日期：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"主承销商","ename":"Lead_underwriter","type":"xpath","value":"//td[text()='主承销商：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"注册资本","ename":"registered_capital","type":"xpath","value":"//td[text()='注册资本：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"组织形式","ename":"Organization_form","type":"xpath","value":"//td[text()='组织形式：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"公司电话","ename":"tel_number","type":"xpath","value":"//td[text()='公司电话：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"公司传真","ename":"fax","type":"xpath","value":"//td[text()='公司传真：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"公司电子邮箱","ename":"fax","type":"xpath","value":"//td[text()='公司电子邮箱：']/following-sibling::*[1]/a/@href",'data_type':""},
                  {"name":"公司网址","ename":"website","type":"xpath","value":"//td[text()='公司网址：']/following-sibling::*[1]/a/@href",'data_type':""},
                  {"name":"信息披露网址","ename":"Information_disclosure","type":"xpath","value":"//td[text()='信息披露网址：']/following-sibling::*[1]/a/@href",'data_type':""}
                 ]
        result = {}
        for config in configs:
            if config['type'] == "xpath":
                result[config['ename']]=response.xpath(config['value']).extract()
                if result[config['ename']]:
                    result[config['ename']]=result[config['ename']][0]
                    result[config['ename']] = S.replace_invalid_char(result[config['ename']])
                    if config['data_type'] =='float':
                        result[config['ename']] = float(result[config['ename']])
                else:
                    result[config['ename']]=None
        result['stock_code']=response.url.split("/")[-1][:-6]
        item['result'] = result
        item['keys'] = []
        item['db'] = ''
        yield item
    def StockStructureParse(self, response):
        if "拒绝访问" in response.text:
            print("拒绝访问")
            time.sleep(30*60)
            headers = {"User-Agent":generate_user_agent()}
            return scrapy.Request(response.url,
                                 dont_filter=True,
                                 headers = headers,
                                 callback=self.StockStructureParse) 
#        print(response.xpath("//title/text()"))
        item = SinaCrawlerItem()
        configs = {"list":{"type":"xpath","value":"//table[contains(@id,'StockStructureNewTable')]"},
                   "data":[
                            {"name":"股票代码","ename":"stock_code","type":"","value":"",'data_type':""},
                            {"name":"变动日期","ename":"change_date","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':""},
                            {"name":"公告日期","ename":"publish_date","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"tr[1]/td[{index}]/text()"},
                            #{"name":"股本结构图","ename":"Capital_structure","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':""},
                            {"name":"变动原因","ename":"change_reason","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':""},
                            {"name":"总股本","ename":"total_Capital","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"流通A股","ename":"Circulation_A_shares","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"高管股","ename":"Executives_shares","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"限售A股","ename":"Restricted_A_shares","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"流通B股","ename":"Circulation_B_shares","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"限售B股","ename":"Restricted_B_shares","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"流通H股","ename":"Circulation_H_shares","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"国家股","ename":"country_shares","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"国有法人股","ename":"National_corporate_share","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"境内法人股","ename":"domestic_corporate_share","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"境内发起人股","ename":"domestic_originator_shares","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"募集法人股","ename":"Corporate_shares_raised","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"一般法人股","ename":"Ordinary_corporate_shares","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"战略投资者持股","ename":"Strategic_investor_holding","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"基金持股","ename":"Fund_holding","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"转配股","ename":"Transfer_stock","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"内部职工股","ename":"employee_stock","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"优先股","ename":"preferred_stock","type":"xpath","value":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            
                           ]}
        if configs['list']:
            trees = response.xpath(configs['list']['value'])
        for tree in trees:
            for index in range(1,6):
                result={}
                for config in configs['data']:
                    if config['type']=='xpath':
                        result[config['ename']] = tree.xpath(config['value'].format(text=config['name'],index=index)).extract()
                        if result[config['ename']]:
                            result[config['ename']]=result[config['ename']][0]
                            if result[config['ename']]=='--':
                                result[config['ename']]=None
                            elif config['data_type'] == "int" or config['data_type'] == "float":
                                 c = re.findall("\d*\.?\d*",result[config['ename']])
                                 if c:
                                     result[config['ename']] = int(float(c[0])*10000)
                                 else:
                                     result[config['ename']] =None
                        else:
                            result[config['ename']]=None
                result['stock_code']=response.url.split("/")[-1][:-6]
                item['result'] = result
                item['keys'] = []
                item['db'] = ''
                if result['change_date']:
                    yield item
    def process_data(self,result,c):
        if result[c['ename']]:
#                        print(result[c['ename']])
            result[c['ename']] = result[c['ename']][0]
            if c['data_type'] =='int':
                q = re.findall("\d+",result[c['ename']])
                if q:
#                                print(q[0])
                    result[c['ename']]=int(q[0])
                else:
                    result[c['ename']]=None
            if c['data_type'] == 'float':
                q = re.findall("\d*\.?\d*",result[c['ename']])
                if q:
                    result[c['ename']] = float(q[0])
                else:
                    result[c['ename']] = None
        else:
            result[c['ename']]=None
        return result
    def StockHolderParse(self, response):
        if "拒绝访问" in response.text:
            print("拒绝访问")
            time.sleep(30*60)
            headers = {"User-Agent":generate_user_agent()}
            return scrapy.Request(response.url,
                                 dont_filter=True,
                                 headers = headers,
                                 callback=self.StockHolderParse) 
        item = SinaCrawlerItem()
#        print(response.xpath("//title/text()"))
        configs = {"list":{"type":"xpath","value":"//strong[text()='截至日期']/parent::div/parent::td/parent::tr"},
                   "data":[
                            {"name":"股票代码","ename":"stock_code","type":"","value":"",'data_type':""},
                            {"name":"截至日期","ename":"stop_date","type":"xpath","value":"td[2]/text()",'data_type':""},
                            {"name":"公告日期","ename":"pubilish_date","type":"xpath","value":"following-sibling::*[1]/td[2]/text()",'data_type':""},
                            {"name":"股东说明","ename":"Shareholder_notes","type":"xpath","value":"following-sibling::*[2]/td[2]/text()",'data_type':""},
                            {"name":"股东总数","ename":"Total_shareholder","type":"xpath","value":"following-sibling::*[3]/td[2]/text()",'data_type':"int"},
                            {"name":"平均持股数","ename":"ave_shares_held","type":"xpath","value":"following-sibling::*[4]/td[2]/text()",'data_type':"int"},
                            {"name":"股东名称","ename":"shareholder_name","type":"xpath","value":"following-sibling::*[{index}]/td[2]/div/a/text()",'data_type':""},
                            #{"name":"股东ID","ename":"shareholde_ID","type":"xpath","value":"following-sibling::*[{index}]/td[2]/div/a/href()",'data_type':""},
                            {"name":"持股数量(股)","ename":"shareholder_numbers","type":"xpath","value":"following-sibling::*[{index}]/td[3]/div/a/text()",'data_type':"int"},
                            {"name":"持股比例(%)","ename":"shares_held_rate","type":"xpath","value":"following-sibling::*[{index}]/td[4]/div/a/text()",'data_type':"float"},
                            {"name":"股本性质","ename":"capital_nature","type":"xpath","value":"following-sibling::*[{index}]/td[5]/div/text()",'data_type':""}
                           ]}
        if configs['list']:
            trees = response.xpath(configs['list']['value'])
        result = {}
        for tree in trees:
            config = configs['data']
            for config1 in config[1:6]:
                result[config1['ename']]=tree.xpath(config1['value']).extract()
                
                flag = True
            for c in config[1:6]:
                result.update(self.process_data(result,c))
            index = 6
            while flag:
                for config2 in config[6:]:
                    try:
                        result[config2['ename']]=tree.xpath(config2['value'].format(index=index)).extract()
                    except Exception as e:
                        print(e)
                        flag=False
                        break
                for c in config[6:]:
                    result.update(self.process_data(result,c))
                result['stock_code'] = response.url.split("/")[-1][:-6]
                #result['shareholde_ID'] = result['shareholde_ID'][-8:]
                if result['shareholder_name'] is None:
                    flag = False
                else:
                    item['result'] = result
                    item['keys'] = []
                    item['db'] = ''
                    yield item

                if flag:
                    index+=1
                else:
                    break
    def CirculateStockHolderParse(self, response):
        if "拒绝访问" in response.text:
            print("拒绝访问")
            time.sleep(30*60)
            headers = {"User-Agent":generate_user_agent()}
            return scrapy.Request(response.url,
                                 dont_filter=True,
                                 headers = headers,
                                 callback=self.CirculateStockHolderParse) 
        item = SinaCrawlerItem()
#        print(response.xpath("//title/text()"))
#        print(response.text)
        configs = {"list":{"type":"xpath","value":"//strong[text()='截止日期']/parent::div/parent::td/parent::tr"},
                   "data":[
                            {"name":"股票代码","ename":"stock_code","type":"","value":"",'data_type':""},
                            {"name":"截至日期","ename":"stop_date","type":"xpath","value":"td[2]/text()",'data_type':""},
                            {"name":"公告日期","ename":"pubilish_date","type":"xpath","value":"following-sibling::tr[1]/td[2]/text()",'data_type':""},
                            {"name":"股东名称","ename":"shareholder_name","type":"xpath","value":"following-sibling::tr[{index}]/td[2]/div/text()",'data_type':""},
                            {"name":"持股数量(股)","ename":"shareholder_numbers","type":"xpath","value":"following-sibling::tr[{index}]/td[3]/div/text()",'data_type':"int"},
                            {"name":"持股比例(%)","ename":"shares_held_rate","type":"xpath","value":"following-sibling::tr[{index}]/td[4]/div/text()",'data_type':"float"},
                            {"name":"股本性质","ename":"capital_nature","type":"xpath","value":"following-sibling::tr[{index}]/td[5]/div/text()",'data_type':""}
                           ]}
        if configs['list']:
            trees = response.xpath(configs['list']['value'])
        result = {}
        for tree in trees:
            config = configs['data']
            for config1 in config[1:3]:
                result[config1['ename']]=tree.xpath(config1['value']).extract()
                index = 3
                flag = True
            for c in config[1:3]:
                result.update(self.process_data(result,c))
            while flag:
                for config2 in config[3:]:
                    try:
                        result[config2['ename']]=tree.xpath(config2['value'].format(index=index)).extract()
                    except Exception as e:
                        print(e)
                        flag=False
                        break
                for c in config[3:]:
                    result.update(self.process_data(result,c))
                result['stock_code'] = response.url.split("/")[-1][:-6]
                if result['shareholder_name'] is None:
                    flag = False
                else:
                    item['result'] = result
                    item['result'] = result
                    item['keys'] = []
                    item['db'] = ''
                    yield item

                if flag:
                    index+=1
                else:
                    break
    def CorpManagerParse(self, response):
        if "拒绝访问" in response.text:
            print("拒绝访问")
            time.sleep(30*60)
            headers = {"User-Agent":generate_user_agent()}
            return scrapy.Request(response.url,
                                 dont_filter=True,
                                 headers = headers,
                                 callback=self.CirculateStockHolderParse) 
        item = SinaCrawlerItem()
        configs = {"list":{"type":"xpath","value":"//a[contains(@href,'/corp/view/vCI_CorpManagerInfo.php?stockid=')]/parent::div/parent::td/parent::tr"},
                   "data":[{"name":"标题","ename":"title","type":"xpath","value":"preceding-sibling::tr/td[@colspan=4]/div/text()","data_type":""},
                           {"name":"人员姓名","ename":"emp_name","type":"xpath","value":"td[1]/div/a/text()","data_type":""},
                           {"name":"职务","ename":"position","type":"xpath","value":"td[2]/div/text()","data_type":""},
                           {"name":"起始日期","ename":"start_time","type":"xpath","value":"td[3]/div/text()","data_type":""},
                           {"name":"终止日期","ename":"stop_time","type":"xpath","value":"td[4]/div/text()","data_type":""},
                           
                           ]
                   }
        for tree in response.xpath(configs['list']['value']):
            result={}
            for config in configs['data']:
                result[config['ename']] = tree.xpath(config['value']).extract()
                if result[config['ename']]:
                    result[config['ename']] = result[config['ename']][-1]
                else:
                    result[config['ename']]=None
                if result['title'] is None:
                    result['title']="历届高管成员"
            title = result['title']
            result['title'] = re.search("\S*[(董事会)|(高管成员)|(监事会)]",title).group(0)
            if result['title'] == "历届高管成员":
                result['title_start'] = None
                result['title_end'] = None
            else:
                result['title_start'] = re.findall("起始日期:(\d{4}-\d{2}-\d{2})",title)[0] if re.findall("起始日期:(\d{4}-\d{2}-\d{2})",title) else None
                result['title_end'] = re.findall("终止日期:(\d{4}-\d{2}-\d{2})",title)[0] if re.findall("终止日期:(\d{4}-\d{2}-\d{2})",title) else None
            for i in result:
                if result[i] == "--":
                    result[i] = None
            result["code"]=response.url.split("/")[-1][:-6]
            item['result'] = result
            item['keys'] = []
            item['db'] = ''
            yield item
    def FundStockHolderParse(self, response):
        if "拒绝访问" in response.text:
            print("拒绝访问")
            time.sleep(30*60)
            headers = {"User-Agent":generate_user_agent()}
            return scrapy.Request(response.url,
                                 dont_filter=True,
                                 headers = headers,
                                 callback=self.CirculateStockHolderParse) 
        item = SinaCrawlerItem()
        configs = {"list":{"type":"xpath","value":"//strong[text()='截止日期']/parent::*/parent::*/parent::*"},
                   "data":[{"name":"截止日期","ename":"stop_time","type":"xpath","value":"td[2]/text()","data_type":""},
                           {"name":"基金名称","ename":"fund_name","type":"xpath","value":"following-sibling::tr[{index}]/td[1]/div/a/text()","data_type":""},
                           {"name":"基金code","ename":"fund_code","type":"xpath","value":"following-sibling::tr[{index}]/td[2]/div/a/text()","data_type":""},
                           {"name":"持仓数量(股)","ename":"holder_numbers","type":"xpath","value":"following-sibling::tr[{index}]/td[3]/div/a/text()","data_type":"int"},
                           {"name":"占流通股比例(%)","ename":"rate_of_Tradable","type":"xpath","value":"following-sibling::tr[{index}]/td[4]/div/text()","data_type":"float"},
                           {"name":"持股市值（元）","ename":"holder_values","type":"xpath","value":"following-sibling::tr[{index}]/td[5]/div/text()","data_type":"int"},
                           {"name":"占净值比例（%）","ename":"assert_rate","type":"xpath","value":"following-sibling::tr[{index}]/td[6]/div/a/text()","data_type":"float"},
                           {"name":"股票代码","ename":"stock_code","type":"url_cut","value":-1,"data_type":""}
                           ]
                   }
        
        for tree in response.xpath(configs['list']['value']):
            index = 2
            result = {}
            while True:
                flag= True
                for config in configs['data']:
                    if config['type'] != "xpath":
                        continue
                    result[config['ename']] = tree.xpath(config['value'].format(index=index)).extract()
                    if result[config['ename']]:
                        result[config['ename']] = result[config['ename']][0]
                        if config['data_type'] in ["float","int"]:
                            result[config['ename']] = float(result[config['ename']])
                    else:
                        result[config['ename']]=None
                    
                    
                if result['fund_name']:
                    pass
                else:
                    flag = False
                if flag:
                    index+=1
                else:
                    break
                result['stock_code'] = response.url.split("/")[-1][:-6]
                item['result'] = result
                item['keys'] = []
                item['db'] = ''
                yield item