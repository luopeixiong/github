# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
sys.path.append('./')

import scrapy
import urllib.parse
from user_agent import generate_user_agent as ua
from myselector import Selector as S
import re
import json
from items import SseItem
import datetime
from functools import wraps
import time

def hdr():
    return {'User-Agent':ua(os=('win','linux','mac'))}
def sse_data_fund(page,class_,pagesize=25):
    data = {'isPagination':'true',
            'pageHelp.pageSize':str(pagesize),
            'pageHelp.pageNo':str(page),
            'pageHelp.beginPage':str(page),
            'pageHelp.cacheSize':'1',
            'pageHelp.endPage':str(page+1),
            'sqlId':class_}
    url = 'http://query.sse.com.cn/commonQuery.do?jsonCallBack=&'+urllib.parse.urlencode(data)
    return url
def sse_data_gphg(page,pagesize = 25):
    data = {'isPagination':'true',
            'sqlId':'COMMON_SSE_SCSJ_CJGK_ZQZYSHG_JYSLMX_L',
            'beginDate':'',
            'endDate':'',
            'securityCode':'',
            'pageHelp.pageNo':str(page),
            'pageHelp.beginPage':str(page),
            'pageHelp.cacheSize':'1',
            'pageHelp.endPage':str(page+1),
            'pageHelp.pageSize':str(pagesize)}
    url = 'http://query.sse.com.cn/commonQuery.do?jsonCallBack=&'+urllib.parse.urlencode(data)
    return url
def sse_data_zcgljh(page,pagesize = 25):
    data = {
        'isPagination':'true',
        'beginDate':'',
        'endDate':'',
        'SECURITY_CODE':'',
        'SECURITY_ABBR':'',
        'sqlId':'SSE_SCSJ_CJGK_GPZYSHG_ZCGLJH_CJXX_CX_L',
        'pageHelp.pageSize':str(pagesize),
        'pageHelp.pageNo':str(page),
        'pageHelp.beginPage':str(page),
        'pageHelp.cacheSize':'1',
        'pageHelp.endPage':'5',
        }
    url = 'http://query.sse.com.cn/commonQuery.do?jsonCallBack=&'+urllib.parse.urlencode(data)
    return url
def sse_data_zrt(date):
    data = {'isPagination':'false',
            'sqlId':'COMMON_SSE_GYBS_CXYW_RZRQ_JYXX_ZRTJYGK_SEARCH_L',
            'fileDate':date,
            }
    url = 'http://query.sse.com.cn/commonQuery.do?jsonCallBack=&'+urllib.parse.urlencode(data)
    return url
def sse_data_bond(page,pagesize = 25):
    data = {
        'isPagination':'true',
        'sqlId':'COMMON_BOND_XXPL_ZQXX_L',
        'BONDTYPE':'',
        'pageHelp.pageSize':str(pagesize),
        'pageHelp.pageNo':str(page),
        'pageHelp.beginPage':str(page),
        'pageHelp.cacheSize':'1',
        'pageHelp.endPage':'5'
        }
    url = 'http://query.sse.com.cn/commonQuery.do?jsonCallBack=&'+urllib.parse.urlencode(data)
    return url
def sse_data_rzrq(date,page,pagesize = 25):
    data = {'isPagination':'true',
            'tabType':	'mxtype',
            'detailsDate':	date,
            'stockCode':'',
            'beginDate':'',
            'endDate':'',
            'pageHelp.pageSize':	str(pagesize),
            'pageHelp.pageCount':	'50',
            'pageHelp.pageNo':	str(page),
            'pageHelp.beginPage':	str(page),
            'pageHelp.cacheSize':'1',
            'pageHelp.endPage':'5'
            }
    url ='http://query.sse.com.cn/marketdata/tradedata/queryMargin.do?jsonCallBack=&'+urllib.parse.urlencode(data)
    return url
def sse_data_stock(page,stockType,pagesize = 25):
    data = {
        'isPagination':'true',
        'stockCode':'',
        'csrcCode':'',
        'areaName':'',
        'stockType':str(stockType),
        'pageHelp.cacheSize':'1',
        'pageHelp.beginPage':str(page),
        'pageHelp.pageSize':str(pagesize),
        'pageHelp.pageNo':str(page),
        'pageHelp.endPage':'5'
        }
    url = 'http://query.sse.com.cn/security/stock/getStockListData2.do?jsonCallBack=&'+urllib.parse.urlencode(data)
    return url
def sse_headers_rzrq():
    _headers = hdr()
    _headers['Host'] = 'query.sse.com.cn'
    return _headers

def tryFlag(response):
    if 'setTimeout' in response.text:
        return True
class SseSpider(scrapy.Spider):
    """
    爬虫说明: 目前已完成
    爬虫设置为 线程数{1} 下载延迟{0}秒
    1：融资融券明细信息 http://www.sse.com.cn/market/othersdata/margin/detail/ 逻辑为分日期获取
    #2: 上证股票信息 http://www.sse.com.cn/assortment/stock/list/delisting/
    
    """
    
    name = "sse"
#    allowed_domains = ["sse.com"]
    start_urls = ['http://www.sse.com.cn/assortment/fund/list/',#基金入口
                  'http://www.sse.com.cn/market/othersdata/asset/',#资产管理计划份额转让成交信息
                  'http://www.sse.com.cn/market/othersdata/refinancing/',#转融通证券出借交易概况
                  'http://www.sse.com.cn/market/bonddata/data/',#债券入口
                  'http://www.sse.com.cn/market/othersdata/margin/detail/',#融资融券入口
                  'http://www.sse.com.cn/market/othersdata/repurchase/',#股票质押回购交易明细
#                  'http://www.sse.com.cn/assortment/stock/list/delisting/',#股票列表  
                  ]
    custom_settings = {'DOWNLOAD_DELAY':2,
                       'CONCURRENT_REQUESTS':8,
                       }
    def start_requests(self):
        self.__doc__ = self.__doc__.format(self.custom_settings['DOWNLOAD_DELAY'],self.custom_settings['CONCURRENT_REQUESTS'])
        print(self.__doc__)
        print(self.custom_settings)
        page = 1
        for _url in self.start_urls:
            time.sleep(1)
            if _url == 'http://www.sse.com.cn/market/othersdata/margin/detail/':
                dateformat = "%Y%m%d"
                today = datetime.datetime.now().strftime(dateformat)
                datelist = S.datelist("20000101",today,dateformat)
                datelist.reverse()
                for date in datelist:  
                    url = sse_data_rzrq(date,page)
                    _headers = sse_headers_rzrq()
                    _headers['Referer'] = 'http://www.sse.com.cn/market/othersdata/margin/detail/'
                    yield scrapy.Request(url,
                                         headers=_headers,
                                         method="GET",
                                         meta = {'page':page,'date':date},
                                         callback = self.rzrqParse)
            elif _url == 'http://www.sse.com.cn/assortment/stock/list/delisting/':
                for stockType in range(1,6):
                    #1 上A
                    #2 上B
                    #3 首次发行待上市
                    #4 暂停上市
                    #5 终止上市
                    url = sse_data_stock(page, stockType)
                    _headers = sse_headers_rzrq()
                    _headers['Referer'] = 'http://www.sse.com.cn/assortment/stock/list/delisting/'
                    yield scrapy.Request(url,
                                         headers=_headers,
                                         method="GET",
                                         meta = {'page':page,'stockType':stockType},
                                         callback = self.stockListParse,
                                         priority=1)
            elif _url == 'http://www.sse.com.cn/market/bonddata/data/':
                url = sse_data_bond(page)
                _headers = sse_headers_rzrq()
                _headers['Referer'] = 'http://www.sse.com.cn/market/bonddata/data/tb/'
                #不明原因翻页终止,更改pagesize至最大,一次性获取全部数据,获取2次
                yield scrapy.Request(url,
                                         headers=_headers,
                                         method="GET",
                                         meta = {'page':page},
                                         callback = self.bondListParse)
                yield scrapy.Request(url,
                                         headers=_headers,
                                         method="GET",
                                         meta = {'page':page},
                                         callback = self.bondListParse,
                                         dont_filter=True)
            elif _url == 'http://www.sse.com.cn/market/othersdata/refinancing/':
                dateformat = "%Y%m%d"
                today = datetime.datetime.now().strftime(dateformat)
                datelist = S.datelist("20000101",today,dateformat)
                datelist.reverse()
                for date in datelist:  
                    url = sse_data_zcgljh(page)
                    _headers = sse_headers_rzrq()
                    _headers['Referer'] = 'http://www.sse.com.cn/market/othersdata/refinancing/'
                    yield scrapy.Request(url,
                                         headers=_headers,
                                         method="GET",
                                         meta = {'page':page,'date':date},
                                         callback = self.zrtParse)
            elif _url == 'http://www.sse.com.cn/market/othersdata/asset/':
                 url = sse_data_zcgljh(page)
                 _headers = sse_headers_rzrq()
                 _headers['Referer'] = 'http://www.sse.com.cn/market/othersdata/asset/'
                 yield scrapy.Request(url,
                                     headers=_headers,
                                     method="GET",
                                     meta = {'page':page},
                                     callback = self.zcgljhParse)
            elif _url == 'http://www.sse.com.cn/market/othersdata/repurchase/':
                 url = sse_data_gphg(page)
                 _headers = sse_headers_rzrq()
                 _headers['Referer'] = 'http://www.sse.com.cn/market/othersdata/repurchase/'
                 yield scrapy.Request(url,
                                     headers=_headers,
                                     method="GET",
                                     meta = {'page':page},
                                     callback = self.gphgParse)
            elif _url == 'http://www.sse.com.cn/assortment/fund/list/':
                classList=['COMMON_SSE_ZQPZ_JYXHBJJLB_L_NEW',
                           'COMMON_SSE_ZQPZ_LOFLB_L_NEW_F',
                           'COMMON_SSE_ZQPZ_FJLOFLB_L_NEW',
                           'COMMON_SSE_ZQPZ_JJLB_L_NEW',
                           'COMMON_SSE_ZQPZ_ETFLB_L_NEW']
                for class_ in classList:
                     url = sse_data_fund(page,class_)
                     _headers = sse_headers_rzrq()
                     _headers['Referer'] = 'http://www.sse.com.cn/assortment/fund/list/'
                     yield scrapy.Request(url,
                                         headers=_headers,
                                         method="GET",
                                         meta = {'page':page,'class_':class_},
                                         callback = self.fundParse)
    def fundParse(self, response):
#        print(response.meta)
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        _response = json.loads(response.text)
        for i in _response['result']:
            fundID = i.get('FUND_ID') if i.get('FUND_ID') else i.get('FUND_CODE') 
            FUND_MANAGER = i.get('FUND_MANAGER') if i.get('FUND_MANAGER')  else i.get('MANAGER_NAME') 
            _headers = sse_headers_rzrq()
            _headers['Referer'] = 'http://www.sse.com.cn/assortment/fund/list/etfinfo/basic/index.shtml?FUNDID='+fundID
            #基金基本信息
            yield scrapy.Request('http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_JJLB_JJ_L&FUNDID={code}&ABBR=random'.format(code=fundID),
                                 headers=_headers,
                                 callback = self.fundInfoParse
                                 )
            _headers = sse_headers_rzrq()
            _headers['Referer'] = 'http://www.sse.com.cn/assortment/fund/fundcompany/list/detail.shtml?COMPANYNAME='+urllib.parse.quote(FUND_MANAGER.encode('utf-8'))
            #
            yield scrapy.Request('http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_JJGSLB_JJGLGSGK_GSJBXX_C&COMPANYNAME={name}'.format(name=urllib.parse.quote(FUND_MANAGER)),
                                 headers=_headers,
                                 callback = self.ManagerInfoParse
                                 )
        page = response.meta['page']
        class_ = response.meta['class_']
        if  page== 1: 
            page+=1
            #第一次进入页面 获取页面总数，后续直接继承页数
            pageCount = _response['pageHelp']['pageCount']
            pageCount = pageCount if isinstance(pageCount,int) else 1
            #进入下一页
    
            for page in range(page,pageCount+1):
                url = sse_data_fund(page,class_)
                _headers = sse_headers_rzrq()
                _headers['Referer'] = 'http://www.sse.com.cn/assortment/fund/list/'
                yield scrapy.Request(url,
                                     headers=_headers,
                                     method="GET",
                                     meta = {'page':page,'pageCount':pageCount,'class_':class_},
                                     callback = self.fundParse)
    def fundInfoParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result','check':'FUNDID','db':'SSE_FundBaseInfo','keys':['FUNDID']},
                    'data':[
                            {'n':'基金简称','En':'ABBR','v':'ABBR','t':'json','dt':''},
                            {'n':'基金类别','En':'CLASS','v':'CLASS','t':'json','dt':''},
                            {'n':'基金公司名称','En':'COMPANYNAME','v':'COMPANYNAME','t':'json','dt':''},
                            {'n':'ETF_URL','En':'ETF_URL','v':'ETF_URL','t':'json','dt':''},
                            {'n':'传真','En':'FAX','v':'FAX','t':'json','dt':''},
                            {'n':'基金公司ID','En':'FDCOMANPYID','v':'FDCOMANPYID','t':'json','dt':''},
                            {'n':'基金ID','En':'FUNDID','v':'FUNDID','t':'json','dt':''},
                            {'n':'基金管理人','En':'FUND_MANAGER','v':'FUND_MANAGER','t':'json','dt':''},
                            {'n':'基金托管人','En':'FUND_TRUSTEE','v':'FUND_TRUSTEE','t':'json','dt':''},
                            {'n':'INDEX_CODE','En':'INDEX_CODE','v':'INDEX_CODE','t':'json','dt':''},
                            {'n':'INDEX_NAME','En':'INDEX_NAME','v':'INDEX_NAME','t':'json','dt':''},
                            {'n':'INDEX_URL','En':'INDEX_URL','v':'INDEX_URL','t':'json','dt':''},
                            {'n':'发行价格','En':'ISSUE_PRICE','v':'ISSUE_PRICE','t':'json','dt':''},
                            {'n':'律师事务所','En':'LAWYER_AFFAIR','v':'LAWYER_AFFAIR','t':'json','dt':''},
                            {'n':'上市日期','En':'LISTING_DATE','v':'LISTING_DATE','t':'json','dt':''},
                            {'n':'基金经理','En':'MANAGE_REPE','v':'MANAGE_REPE','t':'json','dt':''},
                            {'n':'电话','En':'PHONE','v':'PHONE','t':'json','dt':''},
                            {'n':'基金续存期','En':'SAVE_DATE','v':'SAVE_DATE','t':'json','dt':''}
                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
#                print(item)
                yield item
    def ManagerInfoParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result','check':'COMPANYNAME','db':'SSE_ManagerInfo','keys':['FDCOMPANYID']},
                    'data':[
                            {'n':'公司地址','En':'COMPANYADDR','v':'COMPANYADDR','t':'json','dt':''},
                            {'n':'基金公司名称','En':'COMPANYNAME','v':'COMPANYNAME','t':'json','dt':''},
                            {'n':'传真','En':'CONTACTFAX','v':'CONTACTFAX','t':'json','dt':''},
                            {'n':'联系人','En':'CONTACTNAME','v':'CONTACTNAME','t':'json','dt':''},
                            {'n':'联系电话','En':'CONTACTPHONE','v':'CONTACTPHONE','t':'json','dt':''},
                            {'n':'成立日期','En':'DATESETUP','v':'DATESETUP','t':'json','dt':''},
                            {'n':'总经理','En':'GMNAME','v':'GMNAME','t':'json','dt':''},
                            {'n':'公司ID','En':'FDCOMPANYID','v':'TO_CHAR(FDCOMPANYID)','t':'json','dt':''}
                            ]
                    }
                    ]
        _response = json.loads(response.text)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
#                 print(item)
                yield item

    def gphgParse(self, response):
        
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result','check':'SECURITY_CODE','db':'SSE_gphg','keys':['SECURITY_CODE','TRADE_DATE']},
                    'data':[
                            {'n':'待购回余量（股/份/张）','En':'BUY_BACK_MARGIN','v':'BUY_BACK_MARGIN','t':'json','dt':''},
                            {'n':'初始交易数量（股/份/张）','En':'INITIAL_TRANSACTIONS_NUMBER','v':'INITIAL_TRANSACTIONS_NUMBER','t':'json','dt':''},
                            {'n':'购回交易数量（股/份/张）','En':'REPURCHASE_TRANSACTIONS_NUMBER','v':'REPURCHASE_TRANSACTIONS_NUMBER','t':'json','dt':''},
                            {'n':'证劵简称','En':'SECURITY_ABBR','v':'SECURITY_ABBR','t':'json','dt':''},
                            {'n':'证劵代码','En':'SECURITY_CODE','v':'SECURITY_CODE','t':'json','dt':''},
                            {'n':'交易日期','En':'TRADE_DATE','v':'TRADE_DATE','t':'json','dt':''}
                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        page = response.meta['page']
        if  page== 1: 
            page+=1
            #第一次进入页面 获取页面总数，后续直接继承页数
            pageCount = _response['pageHelp']['pageCount']
            pageCount = pageCount if isinstance(pageCount,int) else 1
        #进入下一页

            for page in range(page,pageCount+1):
                url = sse_data_gphg(page)
                _headers = sse_headers_rzrq()
                _headers['Referer'] = 'http://www.sse.com.cn/market/othersdata/repurchase/'
                yield scrapy.Request(url,
                                     headers=_headers,
                                     method="GET",
                                     meta = {'page':page,'pageCount':pageCount},
                                     callback = self.gphgParse)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    
    def zcgljhParse(self, response):
        
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result','check':'SECURITY_CODE','db':'SSE_zcgljh','keys':['SECURITY_CODE','TRADE_DATE','AMOUNT']},
                    'data':[
                            {'n':'成交金额（元）','En':'AMOUNT','v':'AMOUNT','t':'json','dt':''},
                            {'n':'成交价格（元/百元面值）','En':'PRICE','v':'PRICE','t':'json','dt':''},
                            {'n':'证券全称','En':'SECURITY_ABBR','v':'SECURITY_ABBR','t':'json','dt':''},
                            {'n':'证券代码','En':'SECURITY_CODE','v':'SECURITY_CODE','t':'json','dt':''},
                            {'n':'全称','En':'SECURITY_FULL','v':'SECURITY_FULL','t':'json','dt':''},
                            {'n':'成交日期','En':'TRADE_DATE','v':'TRADE_DATE','t':'json','dt':''},
                            {'n':'成交数量（份）','En':'VOLUME','v':'VOLUME','t':'json','dt':''},
                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        page = response.meta['page']
        if  page== 1: 
            page+=1
            #第一次进入页面 获取页面总数，后续直接继承页数
            pageCount = _response['pageHelp']['pageCount']
            pageCount = pageCount if isinstance(pageCount,int) else 1
        #进入下一页

            for page in range(page,pageCount+1):
                url = sse_data_zcgljh(page)
                _headers = sse_headers_rzrq()
                _headers['Referer'] = 'http://www.sse.com.cn/market/othersdata/asset/'
                yield scrapy.Request(url,
                                     headers=_headers,
                                     method="GET",
                                     meta = {'page':page,'pageCount':pageCount},
                                     callback = self.zcgljhParse)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
                code = item['result']['SECURITY_CODE']
                _headers = sse_headers_rzrq()
                _headers['Referer'] = 'http://www.sse.com.cn/market/othersdata/asset/detail.shtml?SECURITY_CODE={code}'.format(code=code)
                yield scrapy.Request('http://query.sse.com.cn/commonQuery.do?&jsonCallBack=&isPagination=false&sqlId=SSE_GYBS_CXYW_ZCGLJH_CPGTXX_L&FUNDID={code}'.format(code=code),
                                     headers=_headers,
                                     meta={'code':code},
                                     callback = self.zcgljhInfoParse)
    def zcgljhInfoParse(self,response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result','check':'SECURITY_CODE','db':'SSE_zcgljhInfo','keys':['SECURITY_CODE']},
                    'data':[
                            {'n':'成立日期','En':'CREATE_DATE','v':'CREATE_DATE','t':'json','dt':''},
                            {'n':'到期日期','En':'END_DATE','v':'END_DATE','t':'json','dt':''},
                            {'n':'是否可提前结束','En':'FINISH_TYPE','v':'FINISH_TYPE','t':'json','dt':''},
                            {'n':'投资者范围','En':'INVESTOR_SCOPE','v':'INVESTOR_SCOPE','t':'json','dt':''},
                            {'n':'资产管理机构','En':'ORG_NAME','v':'ORG_NAME','t':'json','dt':''},
                            {'n':'证券简称','En':'SECURITY_ABBR','v':'SECURITY_ABBR','t':'json','dt':''},
                            {'n':'证券代码','En':'SECURITY_CODE','v':'SECURITY_CODE','t':'json','dt':''},
                            {'n':'证券全称','En':'SECURITY_FULL','v':'SECURITY_FULL','t':'json','dt':''},
                            {'n':'网址','En':'WWW_ADDR','v':'WWW_ADDR','t':'json','dt':''},
                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def zrtParse(self,response):
        
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result','check':'STOCK_CODE','db':'SSE_zrt','keys':['STOCK_CODE','FILE_DATE','REPORT_TYPE']},
                    'data':[
                            {'n':'证券简称','En':'COMPANY_ABBR','v':'COMPANY_ABBR','t':'json','dt':''},
                            {'n':'费率（%）','En':'FEE_RATE','v':'FEE_RATE','t':'json','dt':''},
                            {'n':'申报日期','En':'FILE_DATE','v':'FILE_DATE','t':'json','dt':''},
                            {'n':'期限（天）','En':'LIMITED_DAY','v':'LIMITED_DAY','t':'json','dt':''},
                            {'n':'申报类型','En':'REPORT_TYPE','v':'REPORT_TYPE','t':'json','dt':''},
                            {'n':'证券代码','En':'STOCK_CODE','v':'STOCK_CODE','t':'json','dt':''},
                            {'n':'成交总量','En':'TRADE_VALUME','v':'TRADE_VALUME','t':'json','dt':''},
                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
        
    def bondListParse(self, response):
        
        configs = [{'list':{'n':'','t':'json','v':'result','db':'SSE_bond','keys':['BOND_CODE','BOND_FULL'],'check':'BOND_FULL'},
                    'data':[{'n':'债券简称','En':'BOND_ABBR','v':'BOND_ABBR','t':'json','dt':''},
                            {'n':'债券代码','En':'BOND_CODE','v':'BOND_CODE','t':'json','dt':''},
                            {'n':'债券全称','En':'BOND_FULL','v':'BOND_FULL','t':'json','dt':''},
#                            {'n':'CALL_DATE','En':'CALL_DATE','v':'CALL_DATE','t':'json','dt':''},
                            {'n':'信用水平','En':'CREDIT_LEVEL','v':'CREDIT_LEVEL','t':'json','dt':''},
                            {'n':'到期日','En':'END_DATE','v':'END_DATE','t':'json','dt':''},
#                            {'n':'ESTIMATE_UNIT','En':'ESTIMATE_UNIT','v':'ESTIMATE_UNIT','t':'json','dt':''},
                            {'n':'票面利率','En':'FACE_RATE','v':'FACE_RATE','t':'json','dt':''},
                            {'n':'票面价值','En':'FACE_VALUE','v':'FACE_VALUE','t':'json','dt':''},
#                            {'n':'FILE_DATE','En':'FILE_DATE','v':'FILE_DATE','t':'json','dt':''},
                            {'n':'浮动费率','En':'FLOAT_RATE','v':'FLOAT_RATE','t':'json','dt':''},
                            {'n':'计息方式','En':'INTEREST_TYPE','v':'INTEREST_TYPE','t':'json','dt':''},
                            {'n':'发行人','En':'ISSUE_OWNER','v':'ISSUE_OWNER','t':'json','dt':''},
                            {'n':'发行价格','En':'ISSUE_PRICE','v':'ISSUE_PRICE','t':'json','dt':''},
                            {'n':'发行量(亿元)','En':'ISSUE_VALUE','v':'ISSUE_VALUE','t':'json','dt':''},
                            {'n':'上市日期','En':'LISTING_DATE','v':'LISTING_DATE','t':'json','dt':''},
                            {'n':'主要经销商','En':'MAIN_DEALER','v':'MAIN_DEALER','t':'json','dt':''},
#                            {'n':'网上结束日期','En':'ONLINE_END_DATE','v':'ONLINE_END_DATE','t':'json','dt':''},
#                            {'n':'网上发行简称','En':'ONLINE_ISSUE_ABBR','v':'ONLINE_ISSUE_ABBR','t':'json','dt':''},
#                            {'n':'网上发行代码','En':'ONLINE_ISSUE_CODE','v':'ONLINE_ISSUE_CODE','t':'json','dt':''},
#                            {'n':'网上发行起始日','En':'ONLINE_START_DATE','v':'ONLINE_START_DATE','t':'json','dt':''},
#                            {'n':'下次付息日','En':'PAY_DATE','v':'PAY_DATE','t':'json','dt':''},
                            {'n':'付息方式','En':'PAY_TYPE','v':'PAY_TYPE','t':'json','dt':''},
#                            {'n':'开始日期','En':'START_DATE','v':'START_DATE','t':'json','dt':''},
                            {'n':'质押券代码','En':'PLEDGE_CODE','v':'PLEDGE_CODE','t':'json','dt':''},
#                            {'n':'STOP_END_DATE','En':'STOP_END_DATE','v':'STOP_END_DATE','t':'json','dt':''},
#                            {'n':'STOP_START_DATE','En':'STOP_START_DATE','v':'STOP_START_DATE','t':'json','dt':''},
                            {'n':'期限(年)','En':'TERM_YEAR','v':'TERM_YEAR','t':'json','dt':''},
                            {'n':'交易日','En':'TRADE_DATE','v':'TRADE_DATE','t':'json','dt':''},]
                    }
                    ]
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        _response = json.loads(response.text)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
        page = response.meta['page']
        if  page== 1: 
            page+=1
            #第一次进入页面 获取页面总数，后续直接继承页数
            pageCount = _response['pageHelp']['pageCount']
            pageCount = pageCount if isinstance(pageCount,int) else 1
        #进入下一页

            for page in range(page,pageCount+1):
                url = sse_data_bond(page)
                _headers = sse_headers_rzrq()
                _headers['Referer'] = 'http://www.sse.com.cn/market/bonddata/data/tb/'
                yield scrapy.Request(url,
                                     headers=_headers,
                                     method="GET",
                                     meta = {'page':page,'pageCount':pageCount},
                                     callback = self.bondListParse)
    def bondInfoParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
#        print(response.text)
       
    def stockListParse(self, response):
        
        ###错误页面处理
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        _meta = response.meta
        _response = json.loads(response.text)
        for _js in _response['result']:
            code = _js['COMPANY_CODE']
#            print(code)
            referer = 'http://www.sse.com.cn/assortment/stock/list/info/company/index.shtml?COMPANY_CODE={code}'.format(code=code)
            _headers = sse_headers_rzrq()
            _headers['Referer'] = referer
            #公司概况
            #http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GP_GPLB_C&productid={code}  
            yield scrapy.Request('http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GP_GPLB_C&productid={code}'.format(code=code),
                                 headers=_headers,
                                 method="GET",
                                 meta = {'code':code},
                                 callback = self.stockInfoParse)
            #A股上市时间
            #http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GP_GPLB_AGSSR_C&productid={code}
            yield scrapy.Request('http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GP_GPLB_AGSSR_C&productid={code}'.format(code=code),
                                 headers=_headers,
                                 method="GET",
                                 meta = {'code':code},
                                 callback = self.AlistDateParse)
            #B股上市时间
            #http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GP_GPLB_BGSSR_C&productid={code}  
            yield scrapy.Request('http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GP_GPLB_BGSSR_C&productid={code}'.format(code=code),
                                 headers=_headers,
                                 method="GET",
                                 meta = {'code':code},
                                 callback = self.BlistDateParse)
            #董秘电话
            #http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GP_GPLB_MSXX_C&productid={code}   
            yield scrapy.Request('http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GP_GPLB_MSXX_C&productid={code}'.format(code=code),
                                 headers=_headers,
                                 method="GET",
                                 meta = {'code':code},
                                 callback = self.dongmiParse)
            #股本结构
            #http://query.sse.com.cn/security/stock/queryCompanyStockStruct.do?jsonCallBack=&isPagination=false&companyCode={code}   
            #股本变化
            #http://query.sse.com.cn/security/stock/queryEquityChangeAndReason.do?jsonCallBack=&isPagination=true&companyCode=600000&pageHelp.pageSize=25&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5
            yield scrapy.Request('http://query.sse.com.cn/security/stock/queryEquityChangeAndReason.do?jsonCallBack=&isPagination=true&companyCode={code}&pageHelp.pageSize=200&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5'.format(code=code),
                                  headers=_headers,
                                  method="GET",
                                  meta = {'code':code},
                                  callback = self.EquityChangeParse)
                                 
            #首次增发
            #http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GPLB_CZQK_AGSCFX_S&productid=600000
            yield scrapy.Request('http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GPLB_CZQK_AGSCFX_S&productid={code}'.format(code=code),
                                  headers=_headers,
                                  method="GET",
                                  meta = {'code':code},
                                  callback = self.InitialSEOParse)            
            #增发
            #http://query.sse.com.cn/commonQuery.do?jsonCallBack=3&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GPLB_CZQK_AGZF_S&productid=600000
            yield scrapy.Request('http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GPLB_CZQK_AGZF_S&productid={code}'.format(code=code),
                                  headers=_headers,
                                  method="GET",
                                  meta = {'code':code},
                                  callback = self.SEOParse)              
            #特殊时间首日表现
            #http://query.sse.com.cn/marketdata/tradedata/queryStockSpecialQuat.do?jsonCallBack=&isPagination=true&startDate=&endDate=&product=600000&_=1508824404531
            yield scrapy.Request('http://query.sse.com.cn/marketdata/tradedata/queryStockSpecialQuat.do?jsonCallBack=&isPagination=true&startDate=&endDate=&product={code}'.format(code=code),
                                  headers=_headers,
                                  method="GET",
                                  meta = {'code':code},
                                  callback = self.SpecialEventsParse)                
            #分红
            #http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GG_LYFP_AGFH_L&productid=600000
            yield scrapy.Request('http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GG_LYFP_AGFH_L&productid={code}'.format(code=code),
                                  headers=_headers,
                                  method="GET",
                                  meta = {'code':code},
                                  callback = self.AbonusParse)     
            #送股
            #http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GG_LYFP_AGSG_L&productid=600000
            yield scrapy.Request('http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=false&sqlId=COMMON_SSE_ZQPZ_GG_LYFP_AGSG_L&productid={code}'.format(code=code),
                                  headers=_headers,
                                  method="GET",
                                  meta = {'code':code},
                                  callback = self.BonusParse)  
            #成交概况
            #先忽略
            #http://query.sse.com.cn/security/fund/queryAllQuatAbelNew.do?jsonCallBack=&FUNDID=600000&inMonth=201709&inYear=2016&searchDate=2017-10-23
            yield scrapy.Request('http://query.sse.com.cn/security/fund/queryAllQuatAbelNew.do?jsonCallBack=&FUNDID={code}&inMonth=201709&inYear=2016&searchDate=2017-10-23'.format(code=code),
                                  headers=_headers,
                                  method="GET",
                                  meta = {'code':code},
                                  callback = self.SpecialEventsParse)  
            #高管人员
            #http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=true&productid=600000&sqlId=COMMON_SSE_ZQPZ_GG_GGRYLB_L&pageHelp.pageSize=25&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5
            yield scrapy.Request('http://query.sse.com.cn/commonQuery.do?jsonCallBack=&isPagination=true&productid={code}&sqlId=COMMON_SSE_ZQPZ_GG_GGRYLB_L&pageHelp.pageSize=200&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5'.format(code=code),
                                  headers=_headers,
                                  method="GET",
                                  meta = {'code':code},
                                  callback = self.SeniorExecutivesParse)  
            #股东大会资料
            #http://query.sse.com.cn/security/stock/queryStockholderMeetingInformationNew.do?jsonCallBack=&isPagination=true&productId=600000&beginDate=1900-01-01&endDate=2017-10-24&reportType=%E8%82%A1%E4%B8%9C%E5%A4%A7%E4%BC%9A%E4%BC%9A%E8%AE%AE%E8%B5%84%E6%96%99&reportType2=%E8%82%A1%E4%B8%9C%E5%A4%A7%E4%BC%9A%E4%BC%9A%E8%AE%AE%E8%B5%84%E6%96%99&pageHelp.pageSize=25&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5
            yield scrapy.Request('http://query.sse.com.cn/security/stock/queryStockholderMeetingInformationNew.do?jsonCallBack=&isPagination=true&productId={code}&beginDate=1900-01-01&endDate=2017-10-24&reportType=%E8%82%A1%E4%B8%9C%E5%A4%A7%E4%BC%9A%E4%BC%9A%E8%AE%AE%E8%B5%84%E6%96%99&reportType2=%E8%82%A1%E4%B8%9C%E5%A4%A7%E4%BC%9A%E4%BC%9A%E8%AE%AE%E8%B5%84%E6%96%99&pageHelp.pageSize=25&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5'.format(code=code),
                                  headers=_headers,
                                  method="GET",
                                  meta = {'code':code},
                                  callback = self.MeetingInformationParse)  
            #治理细则
#            http://query.sse.com.cn/security/stock/queryArticleAssociationNew.do?jsonCallBack=&isPagination=true&companyCode=600000&reportType=ZLXZ&pageHelp.pageSize=25&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5
            yield scrapy.Request('http://query.sse.com.cn/security/stock/queryArticleAssociationNew.do?jsonCallBack=&isPagination=true&companyCode={code}&reportType=ZLXZ&pageHelp.pageSize=200&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5'.format(code=code),
                                  headers=_headers,
                                  method="GET",
                                  meta = {'code':code},
                                  callback = self.GoverningDetailsParse)  
            #公司章程
#            http://query.sse.com.cn/security/stock/queryArticleAssociationNew.do?jsonCallBack=&isPagination=true&companyCode=600000&reportType=GSZC&pageHelp.pageSize=25&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5
            yield scrapy.Request('http://query.sse.com.cn/security/stock/queryArticleAssociationNew.do?jsonCallBack=&isPagination=true&companyCode={code}&reportType=GSZC&pageHelp.pageSize=200&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5'.format(code=code),
                                  headers=_headers,
                                  method="GET",
                                  meta = {'code':code},
                                  callback = self.ConstitutionParse)  
            #公司摘要
#            http://query.sse.com.cn/security/stock/queryStockBulletinSummary.do?jsonCallBack=&isPagination=true&inputCond=600000&gg=&pageHelp.pageSize=25&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5
            yield scrapy.Request('http://query.sse.com.cn/security/stock/queryStockBulletinSummary.do?jsonCallBack=&isPagination=true&inputCond={code}&gg=&pageHelp.pageSize=200&pageHelp.pageCount=50&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5'.format(code=code),
                                  headers=_headers,
                                  method="GET",
                                  meta = {'code':code},
                                  callback = self.abstractParse)  
            #公司公告
            #暂时忽略
            #http://www.sse.com.cn/js/common/stocks/new/600000.js
#            yield scrapy.Request('http://www.sse.com.cn/js/common/stocks/new/{code}.js'.format(code=code),
##                                  headers=_headers,
#                                  method="GET",
#                                  meta = {'code':code},
#                                  callback = self.NoticeParse)  
            #
        page = _meta['page']
        if  page== 1: 
            page+=1
            #第一次进入页面 获取页面总数，后续直接继承页数
            pageCount = _response['pageHelp']['pageCount']
            pageCount = pageCount if isinstance(pageCount,int) else 1
        #进入下一页
            for page in range(page,pageCount+1):
                url = sse_data_stock(page,_meta['stockType'])
                _headers = sse_headers_rzrq()
                _headers['Referer'] = 'http://www.sse.com.cn/assortment/stock/list/delisting/'
                yield scrapy.Request(url,
                                     headers=_headers,
                                     method="GET",
                                     meta = _meta,
                                     callback = self.stockListParse)
    def NoticeParse(self, response):
        
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'re_findall','v':re.compile('\{stock_code.*?\}',re.S)},
                    'data':[
                            {'n':'标题','En':'bulletin_title','v':'bulletin_title\s?:\s?\"(.*?)\"','t':'re_first','dt':''},
                            {'n':'文档地址','En':'bulletin_file_url','v':'bulletin_file_url\s?:\s?\"(.*?)\"','t':'re_first','dt':''},
                            {'n':'代码','En':'stock_code','v':'stock_code\s?:\s?\"(.*?)\"','t':'re_first','dt':''},
                            {'n':'公告日','En':'bulletin_date','v':'bulletin_date\s?:\s?\"(.*?)\"','t':'re_first','dt':''},
                            {'n':'资料类型','En':'bulletin_large_type','v':'bulletin_large_type\s?:\s?\"(.*?)\"','t':'re_first','dt':''},
#                            {'n':'code','En':'code','v':'code','t':'meta','dt':''},
#                            {'n':'公司名称','En':'productshortname','v':'productshortname','t':'json','dt':''},
#                            {'n':'摘要ID','En':'seq','v':'seq','t':'json','dt':''},
#                            {'n':'资料内容','En':'content','v':'URL','t':'json','dt':''},
                            ],
#                    'clear':[{'n':'资料内容','En':'content','v':'http://www.sse.com.cn','t':'url2txt','dt':''},]
                    }
                    ]
        _response = response.text
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def abstractParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[
                            {'n':'标题','En':'bulletintitle','v':'bulletintitle','t':'json','dt':''},
                            {'n':'代码','En':'product','v':'product','t':'json','dt':''},
                            {'n':'公告日','En':'DATEDECLARE','v':'DATEDECLARE','t':'json','dt':''},
                            {'n':'公司名称','En':'productshortname','v':'productshortname','t':'json','dt':''},
                            {'n':'摘要ID','En':'seq','v':'seq','t':'json','dt':''},
#                            {'n':'资料内容','En':'content','v':'URL','t':'json','dt':''},
                            ],
#                    'clear':[{'n':'资料内容','En':'content','v':'http://www.sse.com.cn','t':'url2txt','dt':''},]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def ConstitutionParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[
                            {'n':'标题','En':'title','v':'title','t':'json','dt':''},
                            {'n':'代码','En':'security_Code','v':'security_Code','t':'json','dt':''},
                            {'n':'资料登记日','En':'SSEDate','v':'SSEDate','t':'json','dt':''},
                            {'n':'资料链接','En':'URL','v':'URL','t':'json','dt':''},
                            {'n':'资料类型','En':'bulletin_Type','v':'bulletin_Type','t':'json','dt':''},
#                            {'n':'资料内容','En':'content','v':'URL','t':'json','dt':''},
                            ],
#                    'clear':[{'n':'资料内容','En':'content','v':'http://www.sse.com.cn','t':'url2txt','dt':''},]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def GoverningDetailsParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[
                            {'n':'标题','En':'title','v':'title','t':'json','dt':''},
                            {'n':'代码','En':'security_Code','v':'security_Code','t':'json','dt':''},
                            {'n':'资料登记日','En':'SSEDate','v':'SSEDate','t':'json','dt':''},
                            {'n':'资料链接','En':'URL','v':'URL','t':'json','dt':''},
                            {'n':'资料类型','En':'bulletin_Type','v':'bulletin_Type','t':'json','dt':''},
#                            {'n':'资料内容','En':'content','v':'URL','t':'json','dt':''},
                            ],
#                    'clear':[{'n':'资料内容','En':'content','v':'http://www.sse.com.cn','t':'url2txt','dt':''},]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def MeetingInformationParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[
                            {'n':'标题','En':'title','v':'title','t':'json','dt':''},
                            {'n':'代码','En':'security_Code','v':'security_Code','t':'json','dt':''},
                            {'n':'资料登记日','En':'SSEDate','v':'SSEDate','t':'json','dt':''},
                            {'n':'资料链接','En':'URL','v':'URL','t':'json','dt':''},
                            {'n':'资料类型','En':'bulletin_Type','v':'bulletin_Type','t':'json','dt':''},
#                            {'n':'资料内容','En':'content','v':'URL','t':'json','dt':''},
                            ],
#                    'clear':[{'n':'资料内容','En':'content','v':'http://www.sse.com.cn','t':'url2txt','dt':''},]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def SeniorExecutivesParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[
                            {'n':'职务','En':'BUSINESS','v':'BUSINESS','t':'json','dt':''},
                            {'n':'姓名','En':'NAME','v':'NAME','t':'json','dt':''},
                            {'n':'任职开始时间','En':'START_TIME','v':'START_TIME','t':'json','dt':''},
                            {'n':'股票代码','En':'code','v':'code','t':'meta','dt':''},

                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def BonusParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[
#                            {'n':'收盘价(元)','En':'A_SHARES','v':'A_SHARES','t':'json','dt':''},
                            {'n':'公告刊登日','En':'ANNOUNCE_DATE','v':'ANNOUNCE_DATE','t':'json','dt':''},
#                            {'n':'每股红利-除税','En':'ANNOUNCE_DESTINATION','v':'ANNOUNCE_DESTINATION','t':'json','dt':''},
                            {'n':'送股比例(10:?)','En':'BONUS_RATE','v':'BONUS_RATE','t':'json','dt':''},
#                            {'n':'股权登记日','En':'CHANGE_RATE','v':'CHANGE_RATE','t':'json','dt':''},
                            {'n':'公司名称','En':'COMPANY_CODE','v':'COMPANY_CODE','t':'json','dt':''},
                            {'n':'全称','En':'COMPANY_NAME','v':'COMPANY_NAME','t':'json','dt':''},
                            {'n':'除权基准日','En':'EX_RIGHT_DATE_A','v':'EX_RIGHT_DATE_A','t':'json','dt':''},
                            {'n':'股权登记日总股本(万股)','En':'ISS_VOL','v':'ISS_VOL','t':'json','dt':''},
                            {'n':'股权登记日','En':'RECORD_DATE_A','v':'RECORD_DATE_A','t':'json','dt':''},
                            {'n':'A股代码','En':'SECURITY_CODE_A','v':'SECURITY_CODE_A','t':'json','dt':''},
                            {'n':'A股简称','En':'SECURITY_NAME_A','v':'SECURITY_NAME_A','t':'json','dt':''},
                            {'n':'红股上市日','En':'TRADE_DATE_A','v':'TRADE_DATE_A','t':'json','dt':''},

                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def AbonusParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[
#                            {'n':'收盘价(元)','En':'A_SHARES','v':'A_SHARES','t':'json','dt':''},
                            {'n':'股票代码','En':'COMPANY_CODE','v':'COMPANY_CODE','t':'json','dt':''},
                            {'n':'每股红利-除税','En':'DIVIDEND_PER_SHARE1_A','v':'DIVIDEND_PER_SHARE1_A','t':'json','dt':''},
                            {'n':'每股红利-含税','En':'DIVIDEND_PER_SHARE2_A','v':'DIVIDEND_PER_SHARE2_A','t':'json','dt':''},
                            {'n':'股权登记日','En':'EX_DIVIDEND_DATE_A','v':'EX_DIVIDEND_DATE_A','t':'json','dt':''},
                            {'n':'全称','En':'FULL_NAME','v':'FULL_NAME','t':'json','dt':''},
                            {'n':'股权登记日总股本(万股)','En':'ISS_VOL','v':'ISS_VOL','t':'json','dt':''},
                            {'n':'除息前日收盘价','En':'LAST_CLOSE_PRICE_A','v':'LAST_CLOSE_PRICE_A','t':'json','dt':''},
                            {'n':'除息报价','En':'OPEN_PRICE_A','v':'OPEN_PRICE_A','t':'json','dt':''},
                            {'n':'登记日','En':'RECORD_DATE_A','v':'RECORD_DATE_A','t':'json','dt':''},
                            {'n':'A股代码','En':'SECURITY_CODE_A','v':'SECURITY_CODE_A','t':'json','dt':''},
                            {'n':'A股简称','En':'SECURITY_NAME_A','v':'SECURITY_NAME_A','t':'json','dt':''},
#                            {'n':'成交量(万股)','En':'TOTAL_DIVIDEND_A','v':'TOTAL_DIVIDEND_A','t':'json','dt':''},

                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def SpecialEventsParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[{'n':'收盘价(元)','En':'closeprice','v':'closeprice','t':'json','dt':''},
                            {'n':'代码','En':'companyCode','v':'companyCode','t':'json','dt':''},
                            {'n':'当日流通股本(万股)','En':'curBonus','v':'curBonus','t':'json','dt':''},
                            {'n':'换手率(%)','En':'exchangerate','v':'exchangerate','t':'json','dt':''},
                            {'n':'最高价(元)','En':'highprice','v':'highprice','t':'json','dt':''},
                            {'n':'日期','En':'listingDate','v':'listingDate','t':'json','dt':''},
                            {'n':'事件','En':'listingMark','v':'listingMark','t':'json','dt':''},
                            {'n':'最低价(元)','En':'lowprice','v':'lowprice','t':'json','dt':''},
                            {'n':'开盘价(元)','En':'openprice','v':'openprice','t':'json','dt':''},
#                            {'n':'募集资金总额(万元)','En':'productName','v':'productName','t':'json','dt':''},
                            {'n':'成交额(万元)','En':'tradingamt','v':'tradingamt','t':'json','dt':''},
                            {'n':'成交量(万股)','En':'tradingvol','v':'tradingvol','t':'json','dt':''},

                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def InitialSEOParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[{'n':'代码','En':'COMPANY_CODE','v':'COMPANY_CODE','t':'json','dt':''},
                            {'n':'中签率%','En':'GOT_RATE_A','v':'GOT_RATE_A','t':'json','dt':''},
                            {'n':'发行日期','En':'ISSUED_BEGIN_DATE_A','v':'ISSUED_BEGIN_DATE_A','t':'json','dt':''},
                            {'n':'发行方式','En':'ISSUED_MODE_CODE_A','v':'ISSUED_MODE_CODE_A','t':'json','dt':''},
                            {'n':'发行价格','En':'ISSUED_PRICE_A','v':'ISSUED_PRICE_A','t':'json','dt':''},
                            {'n':'发行市盈率(%)-加权法','En':'ISSUED_PROFIT_RATE_A1','v':'ISSUED_PROFIT_RATE_A1','t':'json','dt':''},
                            {'n':'发行市盈率(%)-摊薄法','En':'ISSUED_PROFIT_RATE_A2','v':'ISSUED_PROFIT_RATE_A2','t':'json','dt':''},
                            {'n':'发行数量(万股)','En':'ISSUED_VOLUME_A','v':'MAIN_UNDERWRITER_NAME_A','t':'json','dt':''},
                            {'n':'主承销商','En':'MAIN_UNDERWRITER_NAME_A','v':'MAIN_UNDERWRITER_NAME_A','t':'json','dt':''},
                            {'n':'募集资金总额(万元)','En':'RAISED_MONEY_A','v':'RAISED_MONEY_A','t':'json','dt':''},
#                            {'n':'code','En':'SECURITY_ABBR_A','v':'SECURITY_ABBR_A','t':'json','dt':''},
#                            {'n':'code','En':'SECURITY_CODE_A','v':'SECURITY_CODE_A','t':'json','dt':''},

                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def SEOParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[{'n':'代码','En':'COMPANY_CODE','v':'COMPANY_CODE','t':'json','dt':''},
                            {'n':'中签率%','En':'GOT_RATE_A','v':'GOT_RATE_A','t':'json','dt':''},
                            {'n':'发行日期','En':'ISSUED_BEGIN_DATE_A','v':'ISSUED_BEGIN_DATE_A','t':'json','dt':''},
                            {'n':'发行方式','En':'ISSUED_MODE_CODE_A','v':'ISSUED_MODE_CODE_A','t':'json','dt':''},
                            {'n':'发行价格','En':'ISSUED_PRICE_A','v':'ISSUED_PRICE_A','t':'json','dt':''},
                            {'n':'发行市盈率(%)-加权法','En':'ISSUED_PROFIT_RATE_A1','v':'ISSUED_PROFIT_RATE_A1','t':'json','dt':''},
                            {'n':'发行市盈率(%)-摊薄法','En':'ISSUED_PROFIT_RATE_A2','v':'ISSUED_PROFIT_RATE_A2','t':'json','dt':''},
                            {'n':'发行数量(万股)','En':'ISSUED_VOLUME_A','v':'MAIN_UNDERWRITER_NAME_A','t':'json','dt':''},
                            {'n':'主承销商','En':'MAIN_UNDERWRITER_NAME_A','v':'MAIN_UNDERWRITER_NAME_A','t':'json','dt':''},
                            {'n':'募集资金总额(万元)','En':'RAISED_MONEY_A','v':'RAISED_MONEY_A','t':'json','dt':''},
                            {'n':'上市推荐人','En':'RECOMMEND_NAME_A','v':'RECOMMEND_NAME_A','t':'json','dt':''},
                            {'n':'老股东配售比例(10：?)','En':'SHARE_HOLDER_RATE_A','v':'SHARE_HOLDER_RATE_A','t':'json','dt':''},

                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def EquityChangeParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[{'n':'A股','En':'AShares','v':'AShares','t':'json','dt':''},
                            {'n':'B股','En':'BShares','v':'BShares','t':'json','dt':''},
                            {'n':'变动原因代码','En':'changeReason','v':'changeReason','t':'json','dt':''},
                            {'n':'变动原因','En':'changeReasonDesc','v':'changeReasonDesc','t':'json','dt':''},
                            {'n':'变动日期','En':'realDate','v':'realDate','t':'json','dt':''},
                            {'n':'变动ID','En':'seq','v':'seq','t':'json','dt':''},
                            {'n':'变动后股数(万股)','En':'totalShares','v':'totalShares','t':'json','dt':''},
                            {'n':'code','En':'code','v':'code','t':'meta','dt':''},

                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def dongmiParse(self, response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[{'n':'代码','En':'COMPANY_CODE','v':'COMPANY_CODE','t':'json','dt':''},
                            {'n':'ID_CODE','En':'ID_CODE','v':'ID_CODE','t':'json','dt':''},
                            {'n':'PHONE','En':'PHONE','v':'PHONE','t':'json','dt':''},
                            {'n':'董事会秘书','En':'SECURITY_OF_THE_BOARD_OF_DIRE','v':'SECURITY_OF_THE_BOARD_OF_DIRE','t':'json','dt':''},

                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def AlistDateParse(self,response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[{'n':'代码','En':'COMPANYCODE','v':'COMPANYCODE','t':'json','dt':''},
                            {'n':'上市时间-A','En':'LISTINGDATEA','v':'LISTINGDATEA','t':'json','dt':''},

                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def BlistDateParse(self,response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[{'n':'代码','En':'COMPANYCODE','v':'COMPANYCODE','t':'json','dt':''},
                            {'n':'上市时间-B','En':'LISTINGDATEA','v':'LISTINGDATEA','t':'json','dt':''},

                            ]
                    }
                    ]
        _response = json.loads(response.text)
#        print(_response)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def stockInfoParse(self,response):
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        
        configs = [{'list':{'n':'','t':'json','v':'result'},
                    'data':[{'n':'所属省/直辖市','En':'AREA_NAME_DESC','v':'AREA_NAME_DESC','t':'json','dt':''},
                            {'n':'历史名称','En':'CHANGEABLE_BOND_ABBR','v':'CHANGEABLE_BOND_ABBR','t':'json','dt':''},
                            {'n':'历史代码','En':'CHANGEABLE_BOND_CODE','v':'CHANGEABLE_BOND_CODE','t':'json','dt':''},
                            {'n':'公司简称','En':'COMPANY_ABBR','v':'COMPANY_ABBR','t':'json','dt':''},
                            {'n':'注册地址','En':'COMPANY_ADDRESS','v':'COMPANY_ADDRESS','t':'json','dt':''},
                            {'n':'公司代码','En':'COMPANY_CODE','v':'COMPANY_CODE','t':'json','dt':''},
                            {'n':'CSRC行业(门类)','En':'CSRC_CODE_DESC','v':'CSRC_CODE_DESC','t':'json','dt':''},
                            {'n':'CSRC行业(大类)','En':'CSRC_GREAT_CODE_DESC','v':'CSRC_GREAT_CODE_DESC','t':'json','dt':''},
                            {'n':'CSRC行业(中类)','En':'CSRC_MIDDLE_CODE_DESC','v':'CSRC_MIDDLE_CODE_DESC','t':'json','dt':''},
                            {'n':'公司简称(英)','En':'ENGLISH_ABBR','v':'ENGLISH_ABBR','t':'json','dt':''},
                            {'n':'E-mail','En':'E_MAIL_ADDRESS','v':'E_MAIL_ADDRESS','t':'json','dt':''},
                            {'n':'境外上市地','En':'FOREIGN_LISTING_ADDRESS','v':'FOREIGN_LISTING_ADDRESS','t':'json','dt':''},
                            {'n':'是否境外上市','En':'FOREIGN_LISTING_DESC','v':'FOREIGN_LISTING_DESC','t':'json','dt':''},
                            {'n':'公司全称(中)','En':'FULLNAME','v':'FULLNAME','t':'json','dt':''},
                            {'n':'公司全称(英)','En':'FULL_NAME_IN_ENGLISH','v':'FULL_NAME_IN_ENGLISH','t':'json','dt':''},
                            {'n':'法定代表人','En':'LEGAL_REPRESENTATIVE','v':'LEGAL_REPRESENTATIVE','t':'json','dt':''},
                            {'n':'通讯地址','En':'OFFICE_ADDRESS','v':'OFFICE_ADDRESS','t':'json','dt':''},
                            {'n':'邮编','En':'OFFICE_ZIP','v':'OFFICE_ZIP','t':'json','dt':''},
                            {'n':'联系电话','En':'REPR_PHONE','v':'REPR_PHONE','t':'json','dt':''},
                            {'n':'是否上证180样本股','En':'SECURITY_30_DESC','v':'SECURITY_30_DESC','t':'json','dt':''},
                            {'n':'SECURITY_ABBR_A','En':'SECURITY_ABBR_A','v':'SECURITY_ABBR_A','t':'json','dt':''},
                            {'n':'SECURITY_CODE_A','En':'SECURITY_CODE_A','v':'SECURITY_CODE_A','t':'json','dt':''},
                            {'n':'SECURITY_CODE_A_SZ','En':'SECURITY_CODE_A_SZ','v':'SECURITY_CODE_A_SZ','t':'json','dt':''},
                            {'n':'SECURITY_CODE_A_SZ','En':'SECURITY_CODE_B','v':'SECURITY_CODE_B','t':'json','dt':''},
                            {'n':'SSE行业','En':'SSE_CODE_DESC','v':'SSE_CODE_DESC','t':'json','dt':''},
                            {'n':'A股状态','En':'STATE_CODE_A_DESC','v':'STATE_CODE_A_DESC','t':'json','dt':''},
                            {'n':'B股状态','En':'STATE_CODE_B_DESC','v':'STATE_CODE_B_DESC','t':'json','dt':''},
                            {'n':'网址','En':'WWW_ADDRESS','v':'WWW_ADDRESS','t':'json','dt':''}
                            ]
                    }
                    ]
        _response = json.loads(response.text)
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    #错误页面判断方法
    def tryFlag(self,response):
        if 'setTimeout' in response.text:
            return True
         
    def rzrqParse(self, response):
        ###错误页面处理
        
        flag = self.tryFlag(response)
        if flag:
            request = response.request.replace(dont_filter=True)
            return request
        _response = json.loads(response.text)
#        print(_response)
        configs = [{'list':{'n':'','t':'json','v':'result','keys':['stockCode','opDate'],'db':'SSE_rzrq','check':'stockCode'},
                    'data':[{'n':'信用交易日期','En':'opDate','v':'opDate','t':'json','dt':''},
                            {'n':'标的证券代码','En':'stockCode','v':'stockCode','t':'json','dt':''},
                            {'n':'标的证券简称','En':'securityAbbr','v':'securityAbbr','t':'json','dt':''},
                            {'n':'融资余额(元)','En':'rzye','v':'rzye','t':'json','dt':''},
                            {'n':'融资买入额(元)','En':'rzmre','v':'rzmre','t':'json','dt':''},
                            {'n':'融资偿还额(元)','En':'rzche','v':'rzche','t':'json','dt':''},
                            {'n':'融券余量','En':'rqyl','v':'rqyl','t':'json','dt':''},
                            {'n':'融券卖出量','En':'rqmcl','v':'rqmcl','t':'json','dt':''},
                            {'n':'融券偿还量','En':'rqchl','v':'rqchl','t':'json','dt':''},]
                    }
                    ]
        #获取总页数
        page = response.meta['page']
        date = response.meta['date']
        if page == 1: 
            page+=1
            #第一次进入页面 获取页面总数，后续直接继承页数
            pageCount = _response['pageHelp']['pageCount']
            pageCount = pageCount if isinstance(pageCount,int) else 1
        #进入下一页
            for page in range(page,pageCount+1):
                url = sse_data_rzrq(date,page)
                _headers = sse_headers_rzrq()
                _headers['Referer'] = 'http://www.sse.com.cn/market/othersdata/margin/detail/'
                yield scrapy.Request(url,
                                     headers=_headers,
                                     method="GET",
                                     meta = {'date':date,'page':page,'pageCount':pageCount},
                                     callback = self.rzrqParse)
        #调用公共parse处理Item 返回Generator对象
        items = self.configPaese(configs,_response,response)
        if items:
            #__iter__()返回迭代器本身
            for item in items.__iter__():
                yield item
    def parse(self, response):
        print(response.text)
    def configPaese(self, configs,_response,response=None):
        #实例化item
        item = SseItem()
        #迭代可能多个的configs
        for _configs in configs:
            #根据key v 修改response为列表
            if _configs['list']['v']:
                res = S.select_content(_response,_configs['list'])
                
            else:
                #list(response)   ----让response可迭代
                res = [_response]
            #避免select[]列表
            if res:
                for _res in res:
                    #初始化result
                    result = dict()
                    #遍历每个字段提取
                    for config in _configs['data']:
                        k = config['En']
#                        print(k)
                        result[k] = S.select_content(_res, config, response)
                        result[k] = S.replace_invalid_char(result[k])
                    if _configs.get('clear'):
                        for config in _configs['clear']:
                            k = config['En']
                            result[k] = S.select_content(result[k],config,response)
                    item['result'] = result
                    item['keys'] = _configs['list']['keys']
                    item['db'] = _configs['list']['db']
                    
                    #传递pipelin处理item字段
                    if result[_configs['list']['check']]:
                        yield item   