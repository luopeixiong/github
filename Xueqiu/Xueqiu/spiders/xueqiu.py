# -*- coding: utf-8 -*-
import scrapy
from user_agent import generate_user_agent as ua
import requests
import json
import time
from .myselector import Selector as S
import csv
import re

def _time():
    return int(time.time()*1000)
def getcookie():
    res = requests.get('https://xueqiu.com/',headers={'User-Agent':ua()},cookies = {})
    return res.cookies.get_dict()
def _headers():
    return {'User-Agent':ua(os=('win','linux','mac')),
            'Host':'xueqiu.com'}
def _json(response):
    return json.loads(response.text)
class XueqiuSpider(scrapy.Spider):
    name = "xueqiu"
    allowed_domains = ["xueqiu.com","hkex.com.hk"]
    start_urls = ['https://xueqiu.com/stock/cata/stocklist.json?page={0}&size=90&order=desc&orderby=percent&type=11%2C12&_={1}',
                  'https://xueqiu.com/stock/cata/stocklist.json?page={0}&size=90&order=desc&orderby=percent&type=30&isdelay=1&_={1}']
    cookies = getcookie()
    csvfile = open('雪球公司资料.csv', 'w',newline = "")
    csvfile1 = open('雪球公司资料-香港.csv', 'w',newline = "")
    writer = csv.writer(csvfile)
    writer1 = csv.writer(csvfile1)
    writeFlag = 0
    writeFlag1 = 0
    def start_requests(self):
        
        page = 1
        for _url in self.start_urls:
            if _url in [
                        'https://xueqiu.com/stock/cata/stocklist.json?page={0}&size=90&order=desc&orderby=percent&type=11%2C12&_={1}',
#                        'https://xueqiu.com/stock/cata/stocklist.json?page={0}&size=90&order=desc&orderby=percent&type=30&isdelay=1&_={1}'
                        ]:
                url = _url.format(page,_time())
                yield scrapy.Request(url,
                                     callback = self.parse,
                                     headers = _headers(),
                                     cookies = self.cookies,
                                     method='get',
                                     meta = {'page':page,'formurl':_url}
                                     )
                
            
    def parse(self, response):
        page = response.meta['page']
        js = _json(response)
        _url = response.meta['formurl']
        if page == 1:
            totalPage = int(js['count']['count'])
        else:
            totalPage = response.meta['totalPage']
        
        for __js in js['stocks']:
            code = __js['symbol']
            #上市公司简介
            page = 1
            if _url == 'https://xueqiu.com/stock/cata/stocklist.json?page={0}&size=90&order=desc&orderby=percent&type=11%2C12&_={1}':
#                https://xueqiu.com/stock/f10/compinfo.json?symbol=SH601858&page=1&size=4&_=1508408200126
                urlform_info = 'https://xueqiu.com/stock/f10/compinfo.json?symbol={0}&page=1&size=4&_={1}'.format(code,_time())
                yield scrapy.Request(urlform_info,
                                     callback = self.infoParse,
                                     headers = _headers(),
                                     method = 'get',
                                     meta = {'code':code},
                                     cookies = self.cookies
                                     )
#                urlform_info = 'https://xueqiu.com/stock/f10/shareschg.json?symbol={}&page={}&size=4&_={}'.format(code,page,_time())
#                yield scrapy.Request(urlform_info,
#                                     callback = self.infoParse,
#                                     headers = _headers(),
#                                     method = 'get',
#                                     meta = {'code':code},
#                                     cookies = self.cookies
#                                     )
            elif _url == 'https://xueqiu.com/stock/cata/stocklist.json?page={0}&size=90&order=desc&orderby=percent&type=30&isdelay=1&_={1}':
                urlform_info = 'http://www.hkex.com.hk/chi/invest/company/profile_page_c.asp?WidCoID={0}'.format(code)
#                print(urlform_info)
                yield scrapy.Request(urlform_info,
                                     callback = self.HKinfoParse,
                                     headers = _headers(),
                                     method = 'get',
                                     meta = {'code':code},
                                     cookies = self.cookies
                                     )
            
        if page<totalPage/90:
            page+=1
            url = _url.format(page,_time())
            yield scrapy.Request(url,
                                 callback = self.parse,
                                 headers = _headers(),
                                 cookies = self.cookies,
                                 method='get',
                                 meta = {'page':page,'formurl':_url,'totalPage':totalPage}
                                 )
    def HKinfoParse(self, response):
        _response = response
        configs = {'list':{'n':'','t':'','v':''},
                   'data':[{'n':'股票代码','En':'stock-code','v':'code','t':'meta','dt':''},
                           {'n':'公司名称','En':'compname','v':'//td[font[contains(text(),"公司/證券名稱:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
#                           {'n':'','En':'','v':'','t':'//td[font[contains(text(),"公司/證券名稱:")]]/following-sibling::td/font/text()','dt':''},
                           {'n':'主要业务','En':'','v':'//td[font[contains(text(),"主要業務:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'成立日期','En':'','v':'//td[font[contains(text(),"成立日期:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'上市日期','En':'','v':'//td[font[contains(text(),"上市日期:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'信託基金經理人','En':'','v':'//td[font[contains(text(),"信託基金經理人:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'主席','En':'','v':'//td[font[contains(text(),"主席:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'公司地址','En':'','v':'//td[font[contains(text(),"公司地址:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'注册地址','En':'','v':'//td[font[contains(text(),"註冊地點:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'上市类别','En':'','v':'//td[font[contains(text(),"上市類別:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'行业分类','En':'','v':'//td[font[contains(text(),"行業分類:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'过户数','En':'','v':'//td[font[contains(text(),"過戶處:")]]/following-sibling::td/font/a/text()','t':'xpath_join','dt':''},
                           {'n':'交易货币','En':'','v':'//td[font[contains(text(),"交易貨幣:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'法定股本','En':'','v':'//td[font[contains(text(),"法定股本:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'发行股数','En':'','v':'//td[font[contains(text(),"發行股數:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'最初议价','En':'','v':'//td[font[contains(text(),"最初議價:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'票面值','En':'','v':'//td[font[contains(text(),"票面值:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'已發行基金單位數目','En':'','v':'//td[font[contains(text(),"已發行基金單位數目:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'买卖单位','En':'','v':'//td[font[contains(text(),"買賣單位:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           {'n':'市值','En':'','v':'//td[font[contains(text(),"市值:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
#                           {'':'','En':'','v':'//td[font[contains(text(),"公司/證券名稱:")]]/following-sibling::td/font/text()','t':'xpath_join','dt':''},
                           
                           
                           ],
                    'clear':[]
                    }
        if configs['list']['v']:
            res = S.select_content(_response,configs['list'],response)
        else:
            res = _response
        result = dict()
        for config in configs['data']:
            k = config['n']
            result[k] = S.select_content(res,config,response)
            result[k] = S.replace_invalid_char(result[k])
        if configs['clear']:
            for config in configs['clear']:
                k = config['n']
                result[k] = S.select_content(result[k],config,response)
        if result['公司名称']:
            print(result)
            if self.writeFlag1 == 0:
                self.writer1.writerow(tuple(map(lambda x:str(x),result.keys())))
                self.writeFlag1+=1
            self.writer1.writerow(tuple(map(lambda x:str(x),result.values())))
#        print(list(map(lambda x:str(x),result.values())))
    def infoParse(self, response):
        _response = _json(response)
        print(_response)
        configs = {'list':{'n':'','t':'json','v':'tqCompInfo'},
                   'data':[{'n':'股票代码','En':'stock-code','v':'code','t':'meta','dt':''},
                           {'n':'公司名称','En':'compname','v':'compname','t':'json','dt':''},
                           {'n':'公司英文名称','En':'engname','v':'engname','t':'json','dt':''},
                           {'n':'comptype1','En':'comptype1','v':'comptype1','t':'json','dt':''},
                           {'n':'comptype2','En':'comptype2','v':'comptype2','t':'json','dt':''},
                           {'n':'成立日期','En':'founddate','v':'founddate','t':'json','dt':''},
                           {'n':'组织形式','En':'orgtype','v':'orgtype','t':'json','dt':''},
                           {'n':'注册资本（万元）','En':'regcapital','v':'regcapital','t':'json','dt':''},
                           {'n':'法定股本','En':'authcapsk','v':'authcapsk','t':'json','dt':''},
                           {'n':'董事长','En':'chairman','v':'chairman','t':'json','dt':''},
                           {'n':'总经理','En':'manager','v':'manager','t':'json','dt':''},
                           {'n':'法人代表','En':'legrep','v':'legrep','t':'json','dt':''},
                           {'n':'董秘','En':'bsecretary','v':'bsecretary','t':'json','dt':''},
                           {'n':'董秘电话','En':'bsecretarytel','v':'bsecretarytel','t':'json','dt':''},
                           {'n':'董秘传真','En':'bsecretaryfax','v':'bsecretaryfax','t':'json','dt':''},
                           {'n':'证券/股证事务代表','En':'seaffrepr','v':'seaffrepr','t':'json','dt':''},
                           {'n':'证券代表电话','En':'seagttel','v':'seagttel','t':'json','dt':''},
                           {'n':'证券代表传真','En':'seagtfax','v':'seagtfax','t':'json','dt':''},
                           {'n':'证券代表电子邮箱','En':'seagtemail','v':'seagtemail','t':'json','dt':''},
                           {'n':'董秘授权代表','En':'authreprsbd','v':'authreprsbd','t':'json','dt':''},
                           {'n':'法律顾问','En':'leconstant','v':'leconstant','t':'json','dt':''},
                           {'n':'会计师事务所','En':'accfirm','v':'accfirm','t':'json','dt':''},
                           {'n':'注册地址','En':'regaddr','v':'regaddr','t':'json','dt':''},
                           {'n':'办公地址','En':'officeaddr','v':'officeaddr','t':'json','dt':''},
                           {'n':'办公地址邮编','En':'officezipcode','v':'officezipcode','t':'json','dt':''},
                           {'n':'公司电话','En':'comptel','v':'comptel','t':'json','dt':''},
                           {'n':'公司传真','En':'compfax','v':'compfax','t':'json','dt':''},
                           {'n':'公司电子邮箱','En':'compemail','v':'compemail','t':'json','dt':''},
                           {'n':'公司网址','En':'compurl','v':'compurl','t':'json','dt':''},
                           {'n':'客服电话','En':'servicetel','v':'servicetel','t':'json','dt':''},
                           {'n':'客服传真','En':'servicefax','v':'servicefax','t':'json','dt':''},
                           {'n':'公司简介','En':'compintro','v':'compintro','t':'json','dt':''},
                           {'n':'经营范围','En':'bizscope','v':'bizscope','t':'json','dt':''},
                           {'n':'主营业务','En':'majorbiz','v':'majorbiz','t':'json','dt':''},
                           {'n':'业务规模','En':'bizscale','v':'bizscale','t':'json','dt':''},
                           {'n':'公司代码','En':'compcode','v':'compcode','t':'json','dt':''},
                           {'n':'公司简称','En':'compsname','v':'compsname','t':'json','dt':''},
                           {'n':'地区代码','En':'region','v':'region','t':'json','dt':''},
                           {'n':'邮编','En':'regptcode','v':'regptcode','t':'json','dt':''},
                           {'n':'公示日期(时间戳)','En':'listdate','v':'listdate','t':'json','dt':''},
                           {'n':'发行价','En':'issprice','v':'issprice','t':'json','dt':''},
                           {'n':'onlactissqty','En':'onlactissqty','v':'onlactissqty','t':'json','dt':''},
                           {'n':'actissqty','En':'actissqty','v':'actissqty','t':'json','dt':''},
                           {'n':'省区','En':'tqCompBoardmapList_1','v':'tqCompBoardmapList[-2]/keyname','t':'json','dt':''},
                           {'n':'市区','En':'tqCompBoardmapList_2','v':'tqCompBoardmapList[-1]/keyname','t':'json','dt':''},
                           {'n':'所属行业','En':'tqCompIndustryList','v':'tqCompIndustryList','t':'json','dt':''}
                           ],
                   'clear':[{'n':'所属行业','En':'tqCompIndustryList','v':'level2name','t':'jsonjoin','dt':''}
                           ]
                   }
        if configs['list']['v']:
            res = S.select_content(_response,configs['list'],response)
        else:
            res = _response
        result = dict()
        for config in configs['data']:
            k = config['En']
            result[k] = S.select_content(res,config,response)
            result[k] = S.replace_invalid_char(result[k])
        if configs['clear']:
            for config in configs['clear']:
                k = config['En']
                result[k] = S.select_content(result[k],config,response)
        print(result)
#        print(list(map(lambda x:str(x),result.values())))
        if result['compname']:
            if self.writeFlag == 0:
                self.writer.writerow(tuple(map(lambda x:str(x),result.keys())))
                self.writeFlag+=1
            self.writer.writerow(tuple(map(lambda x:str(x),result.values())))
        
    @classmethod
    def close(self,spider, reason):
        self.csvfile.close()
        self.csvfile1.close()
        closed = getattr(spider, 'closed', None)
        if callable(closed):
            return closed(reason) 
        