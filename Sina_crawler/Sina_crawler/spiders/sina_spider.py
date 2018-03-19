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
from .myselector import Selector as S
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
        for Board in self.Boards:
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
                if True:
#                if result['StockCode'] not in self.stockcodes:
#                    self.stockcodes.append(result['StockCode'])
                    for url in ["http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/{code}.phtml",#上市公司基本信息
                            "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockStructure/stockid/{code}.phtml",#股权变动
                            "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockHolder/stockid/{code}.phtml",#主要股东
                            "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CirculateStockHolder/stockid/{code}.phtml",#流动股东
                            "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpManager/stockid/{code}.phtml",#基金高管
                            "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_FundStockHolder/stockid/{code}.phtml"#基金持有人
                            ]:
                        time.sleep
                        nexturl = url.format(code=result['StockCode'])
                        headers = {"User-Agent":generate_user_agent()}
                        if "vCI_CorpInfo" in nexturl:
                            pass
                            yield scrapy.Request(nexturl,
                                                 callback=self.CorpInfoParse,
                                                 headers = headers,
                                                 meta={"code":result['StockCode']})
                        elif "vCI_StockStructure" in nexturl:
                            pass
                            yield scrapy.Request(nexturl,
                                                 callback=self.StockStructureParse,
                                                 headers = headers,
                                                 meta={"code":result['StockCode']})
                        elif "vCI_StockHolder" in nexturl:
                            pass
                            yield scrapy.Request(nexturl,
                                                 callback=self.StockHolderParse,
                                                 headers = headers,
                                                 meta={"code":result['StockCode']})
                        if "vCI_CirculateStockHolder" in nexturl:
                            pass
                            yield scrapy.Request(nexturl,
                                                 callback=self.CirculateStockHolderParse,
                                                 headers = headers,
                                                 meta={"code":result['StockCode']})
                        elif "vCI_CorpManager" in nexturl:
                            pass
                            yield scrapy.Request(nexturl,
                                                 callback=self.CorpManagerParse,
                                                 headers = headers,
                                                 meta={"code":result['StockCode']})
                        elif "vCI_FundStockHolder" in nexturl:
                            pass
                            yield scrapy.Request(nexturl,
                                                 callback=self.FundStockHolderParse,
                                                 headers = headers,
                                                 meta={"code":result['StockCode']})
                item['keys'] = ['BoardName','StockCode']
                item['db'] = 'sina_StockList'
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
#        print(response.text)
        item = SinaCrawlerItem()
        configs = [{"name":"公司名称","En":"company_name","t":"xpath_first","v":"//td[text()='公司名称：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"股票代码","En":"stock_name","t":"xpath_first","v":"//h1[@id='stockName']/text()[1]",'data_type':""},                                                                 
                  {"name":"公司代码","En":"stock_code","t":"url_split","v":"",'data_type':""},
                  {"name":"公司英文名称","En":"stock_ename","t":"xpath_first","v":"//td[text()='公司英文名称：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"上市市场","En":"Listed_market","t":"xpath_first","v":"//td[text()='上市市场：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"发行价格","En":"Issue_price","t":"xpath_first","v":"//td[text()='发行价格：']/following-sibling::*[1]/text()",'data_type':"float"},
                  {"name":"成立日期","En":"set_up_time","t":"xpath_first","v":"//td[text()='成立日期：']/following-sibling::*[1]/a/text()",'data_type':""},
                  {"name":"机构类型","En":"institution_type","t":"xpath_first","v":"//td[text()='机构类型：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"董事会秘书","En":"Board_Secretary","t":"xpath_first","v":"//td[text()='董事会秘书：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"董秘电话","En":"Secretary_tel_numbers","t":"xpath_first","v":"//td[text()='董秘电话：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"董秘传真","En":"Secretary_fax","t":"xpath_first","v":"//td[text()='董秘传真：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"董秘电子邮箱","En":"Secretary_email","t":"xpath_first","v":"//td[text()='董秘电子邮箱：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"邮政编码","En":"Postal_Code","t":"xpath_first","v":"//td[text()='邮政编码：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"证券简称更名历史","En":"history_change_name","t":"xpath_first","v":"//td[text()='证券简称更名历史：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"注册地址","En":"Registered_address","t":"xpath_first","v":"//td[text()='注册地址：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"办公地址","En":"Office_address","t":"xpath_first","v":"//td[text()='办公地址：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"公司简介","En":"Company_profile","t":"xpath_first","v":"//td[text()='公司简介：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"经营范围","En":"business_Scope","t":"xpath_first","v":"//td[text()='经营范围：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"上市日期","En":"Listing_date","t":"xpath_first","v":"//td[text()='上市日期：']/following-sibling::td[1]/a/text()",'data_type':""},
                  {"name":"主承销商","En":"Lead_underwriter","t":"xpath_first","v":"//td[text()='主承销商：']/following-sibling::td[1]/a/text()",'data_type':""},
                  {"name":"注册资本","En":"registered_capital","t":"xpath_first","v":"//td[text()='注册资本：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"组织形式","En":"Organization_form","t":"xpath_first","v":"//td[text()='组织形式：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"公司电话","En":"tel_number","t":"xpath_first","v":"//td[text()='公司电话：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"公司传真","En":"fax","t":"xpath_first","v":"//td[text()='公司传真：']/following-sibling::*[1]/text()",'data_type':""},
                  {"name":"公司电子邮箱","En":"fax","t":"xpath_first","v":"//td[text()='公司电子邮箱：']/following-sibling::*[1]/a/@href",'data_type':""},
                  {"name":"公司网址","En":"website","t":"xpath_first","v":"//td[text()='公司网址：']/following-sibling::*[1]/a/@href",'data_type':""},
                  {"name":"信息披露网址","En":"Information_disclosure","t":"xpath_first","v":"//td[text()='信息披露网址：']/following-sibling::*[1]/a/@href",'data_type':""}
                 ]
        result = {}
        for config in configs:
            if config["t"]:
                result[config["En"]]=S.select_content(response,config)
                if result[config["En"]]:
                    result[config["En"]] = S.replace_all(result[config["En"]])
                    result[config["En"]] = S.changdt(result[config["En"]],config['data_type'])
                else:
                    result[config["En"]]=None
        result['stock_code']=response.url.split("/")[-1][:-6]
        item['result'] = result
        item['keys'] = ['stock_code']
        item['db'] = 'sina_ListedCompany'
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
        configs = {"list":{"t":"xpath","v":"//table[contains(@id,'StockStructureNewTable')]"},
                   "data":[
                            {"name":"股票代码","En":"stock_code","t":"","v":"",'data_type':""},
                            {"name":"变动日期","En":"change_date","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':""},
                            {"name":"公告日期","En":"publish_date","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"tr[1]/td[{index}]/text()"},
                            #{"name":"股本结构图","En":"Capital_structure","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':""},
                            {"name":"变动原因","En":"change_reason","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':""},
                            {"name":"总股本","En":"total_Capital","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"流通A股","En":"Circulation_A_shares","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"高管股","En":"Executives_shares","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"限售A股","En":"Restricted_A_shares","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"流通B股","En":"Circulation_B_shares","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"限售B股","En":"Restricted_B_shares","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"流通H股","En":"Circulation_H_shares","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"国家股","En":"country_shares","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"国有法人股","En":"National_corporate_share","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"境内法人股","En":"domestic_corporate_share","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"境内发起人股","En":"domestic_originator_shares","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"募集法人股","En":"Corporate_shares_raised","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"一般法人股","En":"Ordinary_corporate_shares","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"战略投资者持股","En":"Strategic_investor_holding","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"基金持股","En":"Fund_holding","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"转配股","En":"Transfer_stock","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"内部职工股","En":"employee_stock","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            {"name":"优先股","En":"preferred_stock","t":"xpath","v":"tbody/node()/td[contains(text(),'{text}')]/following-sibling::*[{index}]/text()",'data_type':"float"},
                            
                           ]}
        if configs['list']:
            trees = response.xpath(configs['list']["v"])
        for tree in trees:
            for index in range(1,6):
                result={}
                for config in configs['data']:
                    if config["t"]=='xpath':
                        result[config["En"]] = tree.xpath(config["v"].format(text=config['name'],index=index)).extract()
                        if result[config["En"]]:
                            result[config["En"]]=result[config["En"]][0]
                            if result[config["En"]]=='--':
                                result[config["En"]]=None
                            elif config['data_type'] == "int" or config['data_type'] == "float":
                                 c = re.findall("\d*\.?\d*",result[config["En"]])
                                 if c:
                                     result[config["En"]] = int(float(c[0])*10000)
                                 else:
                                     result[config["En"]] =None
                        else:
                            result[config["En"]]=None
                result['stock_code']=response.url.split("/")[-1][:-6]
                item['result'] = result
                item['keys'] = ['stock_code','change_date']
                item['db'] = 'sina_Equity_change'
                if result['change_date']:
                    yield item
    def process_data(self,result,c):
        if result[c["En"]]:
#                        print(result[c["En"]])
            result[c["En"]] = result[c["En"]][0]
            if c['data_type'] =='int':
                q = re.findall("\d+",result[c["En"]])
                if q:
#                                print(q[0])
                    result[c["En"]]=int(q[0])
                else:
                    result[c["En"]]=None
            if c['data_type'] == 'float':
                q = re.findall("\d*\.?\d*",result[c["En"]])
                if q:
                    result[c["En"]] = float(q[0])
                else:
                    result[c["En"]] = None
        else:
            result[c["En"]]=None
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
        configs = {"list":{"t":"xpath","v":"//strong[text()='截至日期']/parent::div/parent::td/parent::tr"},
                   "data":[
                            {"name":"股票代码","En":"stock_code","t":"","v":"",'data_type':""},
                            {"name":"截至日期","En":"stop_date","t":"xpath","v":"td[2]/text()",'data_type':""},
                            {"name":"公告日期","En":"pubilish_date","t":"xpath","v":"following-sibling::*[1]/td[2]/text()",'data_type':""},
                            {"name":"股东说明","En":"Shareholder_notes","t":"xpath","v":"following-sibling::*[2]/td[2]/text()",'data_type':""},
                            {"name":"股东总数","En":"Total_shareholder","t":"xpath","v":"following-sibling::*[3]/td[2]/text()",'data_type':"int"},
                            {"name":"平均持股数","En":"ave_shares_held","t":"xpath","v":"following-sibling::*[4]/td[2]/text()",'data_type':"int"},
                            {"name":"股东名称","En":"shareholder_name","t":"xpath","v":"following-sibling::*[{index}]/td[2]/div/a/text()",'data_type':""},
                            #{"name":"股东ID","En":"shareholde_ID","t":"xpath","v":"following-sibling::*[{index}]/td[2]/div/a/href()",'data_type':""},
                            {"name":"持股数量(股)","En":"shareholder_numbers","t":"xpath","v":"following-sibling::*[{index}]/td[3]/div/a/text()",'data_type':"int"},
                            {"name":"持股比例(%)","En":"shares_held_rate","t":"xpath","v":"following-sibling::*[{index}]/td[4]/div/a/text()",'data_type':"float"},
                            {"name":"股本性质","En":"capital_nature","t":"xpath","v":"following-sibling::*[{index}]/td[5]/div/text()",'data_type':""}
                           ]}
        if configs['list']:
            trees = response.xpath(configs['list']["v"])
        result = {}
        for tree in trees:
            config = configs['data']
            for config1 in config[1:6]:
                result[config1["En"]]=tree.xpath(config1["v"]).extract()
                
                flag = True
            for c in config[1:6]:
                result.update(self.process_data(result,c))
            index = 6
            while flag:
                for config2 in config[6:]:
                    try:
                        result[config2["En"]]=tree.xpath(config2["v"].format(index=index)).extract()
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
                    item['keys'] = ['stock_code','stop_date']
                    item['db'] = 'sina_Major_shareholder'
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
        configs = {"list":{"t":"xpath","v":"//strong[text()='截止日期']/parent::div/parent::td/parent::tr"},
                   "data":[
                            {"name":"股票代码","En":"stock_code","t":"","v":"",'data_type':""},
                            {"name":"截至日期","En":"stop_date","t":"xpath","v":"td[2]/text()",'data_type':""},
                            {"name":"公告日期","En":"pubilish_date","t":"xpath","v":"following-sibling::tr[1]/td[2]/text()",'data_type':""},
                            {"name":"股东名称","En":"shareholder_name","t":"xpath","v":"following-sibling::tr[{index}]/td[2]/div/text()",'data_type':""},
                            {"name":"持股数量(股)","En":"shareholder_numbers","t":"xpath","v":"following-sibling::tr[{index}]/td[3]/div/text()",'data_type':"int"},
                            {"name":"持股比例(%)","En":"shares_held_rate","t":"xpath","v":"following-sibling::tr[{index}]/td[4]/div/text()",'data_type':"float"},
                            {"name":"股本性质","En":"capital_nature","t":"xpath","v":"following-sibling::tr[{index}]/td[5]/div/text()",'data_type':""}
                           ]}
        if configs['list']:
            trees = response.xpath(configs['list']["v"])
        result = {}
        for tree in trees:
            config = configs['data']
            for config1 in config[1:3]:
                result[config1["En"]]=tree.xpath(config1["v"]).extract()
                index = 3
                flag = True
            for c in config[1:3]:
                result.update(self.process_data(result,c))
            while flag:
                for config2 in config[3:]:
                    try:
                        result[config2["En"]]=tree.xpath(config2["v"].format(index=index)).extract()
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
                    item['keys'] = ['stock_code','stop_date']
                    item['db'] = 'sina_Tradable_shareholders'
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
        configs = {"list":{"t":"xpath","v":"//a[contains(@href,'/corp/view/vCI_CorpManagerInfo.php?stockid=')]/parent::div/parent::td/parent::tr"},
                   "data":[{"name":"标题","En":"title","t":"xpath","v":"preceding-sibling::tr/td[@colspan=4]/div/text()","data_type":""},
                           {"name":"人员姓名","En":"emp_name","t":"xpath","v":"td[1]/div/a/text()","data_type":""},
                           {"name":"职务","En":"position","t":"xpath","v":"td[2]/div/text()","data_type":""},
                           {"name":"起始日期","En":"start_date","t":"xpath","v":"td[3]/div/text()","data_type":""},
                           {"name":"终止日期","En":"stop_date","t":"xpath","v":"td[4]/div/text()","data_type":""},
                           
                           ]
                   }
        for tree in response.xpath(configs['list']["v"]):
            result={}
            for config in configs['data']:
                result[config["En"]] = tree.xpath(config["v"]).extract()
                if result[config["En"]]:
                    result[config["En"]] = result[config["En"]][-1]
                else:
                    result[config["En"]]=None
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
            result["stock_code"]=response.url.split("/")[-1][:-6]
            item['result'] = result
            item['keys'] = ["stock_code","stop_date","emp_name",'position']
            item['db'] = 'sina_company_executives'
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
        configs = {"list":{"t":"xpath","v":"//strong[text()='截止日期']/parent::*/parent::*/parent::*"},
                   "data":[{"name":"截止日期","En":"stop_time","t":"xpath","v":"td[2]/text()","data_type":""},
                           {"name":"基金名称","En":"fund_name","t":"xpath","v":"following-sibling::tr[{index}]/td[1]/div/a/text()","data_type":""},
                           {"name":"基金code","En":"fund_code","t":"xpath","v":"following-sibling::tr[{index}]/td[2]/div/a/text()","data_type":""},
                           {"name":"持仓数量(股)","En":"holder_numbers","t":"xpath","v":"following-sibling::tr[{index}]/td[3]/div/a/text()","data_type":"int"},
                           {"name":"占流通股比例(%)","En":"rate_of_Tradable","t":"xpath","v":"following-sibling::tr[{index}]/td[4]/div/text()","data_type":"float"},
                           {"name":"持股市值（元）","En":"holder_values","t":"xpath","v":"following-sibling::tr[{index}]/td[5]/div/text()","data_type":"int"},
                           {"name":"占净值比例（%）","En":"assert_rate","t":"xpath","v":"following-sibling::tr[{index}]/td[6]/div/a/text()","data_type":"float"},
                           {"name":"股票代码","En":"stock_code","t":"url_cut","v":-1,"data_type":""}
                           ]
                   }
        
        for tree in response.xpath(configs['list']["v"]):
            index = 2
            result = {}
            while True:
                flag= True
                for config in configs['data']:
                    if config["t"] != "xpath":
                        continue
                    result[config["En"]] = tree.xpath(config["v"].format(index=index)).extract()
                    if result[config["En"]]:
                        result[config["En"]] = result[config["En"]][0]
                        if config['data_type'] in ["float","int"]:
                            result[config["En"]] = float(result[config["En"]])
                    else:
                        result[config["En"]]=None
                    
                    
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
                item['keys'] = ['stock_code','fund_code','stop_time']
                item['db'] = 'sina_fund_holder'
                yield item
