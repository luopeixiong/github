# -*- coding: utf-8 -*-
import scrapy
import os
import sys
import urllib.parse
import re
import requests
import json
import time
import execjs
import math
import time
from user_agent import generate_user_agent
from scrapy.http.cookies import CookieJar 
import tabula

BASEDIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

sys.path.append(BASEDIR)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SpiderHelp import SpiderHelp
from RedisHelp import _Request,_RedisSpider,logger

conn_flag = False
REDISFLAG = True
TODAY = time.strftime('%Y-%m-%d')
Headers = {'User-Agent': generate_user_agent(os=('win',))}
Cookies = {'.ASPXANONYMOUS':'pdtC5gfC0wEkAAAAOWIzZDNiMGEtYjUzOS00YzYyLWEyZTctNWM2OTdmOGM2ZDcz0'}
from myselector import pdf_to_html
'''
redis数据库使用FOFI先进后出的规则 对url进行队列选择
'''



class SinaspiderSpider(_RedisSpider, SpiderHelp):  #,scrapy.Spider
    name = 'sinaspider'
    start_urls = [
                  # 'http://stock.finance.sina.com.cn/xintuo/view/vProdList.php?prodtype={}',  # 新浪信托
                 # 'http://finance.sina.com.cn/js/data/20140924/category.js',  # 新浪股票
                  # 'http://money.finance.sina.com.cn/bank/api/json_v2.php/Bank_FinanceService.searchFinaceProd?page=1&num=20', #  银行理财
                  # 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodes', # 债券
                  # 'http://vip.stock.finance.sina.com.cn/quotes_service/view/js/qihuohangqing.js?20170823', # 期货
                  # 'http://wwv.cyzone.cn', # 创业邦入口
                  # 'http://www.p2peye.com/platform/all/p1/', #网贷天眼
                  # 'http://xukezheng.cbrc.gov.cn/ilicence/licence/licenceQuery.jsp', #  金融许可
                  'https://www.chinawealth.com.cn/zzlc/jsp/lccp.jsp', #银行理财
                  # 'http://money.finance.sina.com.cn/fund_center/index.html'# 新浪-基金入口
                  # 'http://www.10jqka.com.cn/', # 同花顺入口
                  # 'http://www.circ.gov.cn/' # 保险机构
                  # 'http://beijing.circ.gov.cn'#
                  # 'http://www.cbrc.gov.cn/chinese/jrjg/index.html' #  银监会-国内银行业金融机构
                  # 'http://www.cbrc.gov.cn/chongqing/yqlj/xnyh/30.html' # 银监会-重庆银行业金融机构
                  # 'http://bond.sse.com.cn/disclosure/info/', # 上海证券交易所证券
                  # 'http://www.cwf.gov.cn/cgi/company/web_default_4.shtml', #重庆市小额贷款公司
                  # 'http://sjr.sh.gov.cn/ZhengWuDaTing/Index?categoryid=10&parentid=64&OgnTpPid=0',# 上海小贷
                  # 'http://www.bjjrj.gov.cn/tztg/c44-a989.html', # 北京小贷
                  # 'http://zdb.pedaily.cn/',#投资界
                  # 'http://www.neeq.com.cn/', # 全国中小企业股份转让系统
                  # 'http://www.sac.net.cn/', # 证券业协会
                  # 'http://www.cfachina.org/', # 期货业协会
                 ]
    state = {}
    redis_flag=True
    redis_key = 'chinawealth:starturls'
    signel = 1
    host = '10.1.18.35'
    website_possible_httpstatus_list = [404, 502, 500, 504, 407]
    custom_settings = {
        # 'DOWNLOADER_MIDDLEWARES': 
        # {
        #     # 启用UA中间件
        #     # 'CreditChina.middlewares.RotateUserAgentMiddleware': 401,
        #     # 启用代理
        #     'CreditChina.middlewares.ProxyMiddleware': 700,
        # },
        # 最大并发
         'CONCURRENT_REQUESTS': 16,
        # 单ip最大并发
        # 'CONCURRENT_REQUESTS_PER_IP': 8,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        #下载延迟
        # 'DOWNLOAD_DELAY': 3,
        # 爬虫策略
        'DEPTH_PRIORITY': 1,
        # 允许的status
        'HTTPERROR_ALLOWED_CODES': [404, 502, 500, 504],
    }

    def __init__(self, _job=None,**kwargs):
        # 获取本爬虫redis_key
        super(SinaspiderSpider,self).__init__(**kwargs)

    def __str__(self): 
        return 'SinaspiderSpider'
        

    def _start_requests(self):
        req = []
        logger.info('Start Crawl Spider %s at rediskey %s' % (self.name,self.redis_key))
        for url in self.start_urls:
            if url == 'http://stock.finance.sina.com.cn/xintuo/view/vProdList.php?prodtype={}':
                for i in range(1,5):
                    _url = url.format(i)
                    req.append(self.request(
                        _url,
                        meta={'formatter':_url+'&page={}'},
                        redis_flag=REDISFLAG,
                        callback=self.sina_trust))
            elif url == 'http://finance.sina.com.cn/js/data/20140924/category.js':
                req.append(self.request(
                        url,
                        redis_flag=REDISFLAG,
                        callback=self.sina_stock_in))
            elif url == 'http://money.finance.sina.com.cn/bank/api/json_v2.php/Bank_FinanceService.searchFinaceProd?page=1&num=20':
                req.append(self.request(
                        url,
                        redis_flag=REDISFLAG,
                        callback=self.sina_bank_finance))
            elif url == 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodes':
                req.append(self.request(
                        url,
                        redis_flag=REDISFLAG,
                        callback=self.sina_Capital))
            elif url == 'http://wwv.cyzone.cn':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        callback=self.cyzone_start))
            elif url == 'http://vip.stock.finance.sina.com.cn/quotes_service/view/js/qihuohangqing.js?20170823':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        callback=self.sina_futures))
            elif url == 'http://www.p2peye.com/platform/all/p1/':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        callback=self.p2peye_list))
            elif url == 'http://xukezheng.cbrc.gov.cn/ilicence/licence/licenceQuery.jsp':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        callback=self.cbrc_jumps))
            elif url == 'https://www.chinawealth.com.cn/zzlc/jsp/lccp.jsp':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        callback=self.chinawealth_jumps))
            elif url == 'http://money.finance.sina.com.cn/fund_center/index.html':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        callback=self.sina_funds_in))
            elif url == 'http://www.10jqka.com.cn/':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        callback=self.flush_in))
            elif url == 'http://www.circ.gov.cn/':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        callback=self.circ_jumps))
            elif url == 'http://beijing.circ.gov.cn':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        headers={'User-Agent':generate_user_agent(os=('win',))},
                        callback=self.all_circ_jumps))
            elif url == 'http://www.cbrc.gov.cn/chinese/jrjg/index.html':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        headers={'User-Agent':generate_user_agent(os=('win',))},
                        callback=self.all_bank_list))
            elif url == 'http://bond.sse.com.cn/disclosure/info/':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        headers=self.default_header,
                        callback=self.sse_bond_in))
            elif url == 'http://www.cwf.gov.cn/cgi/company/web_default_4.shtml':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        headers=self.default_header,
                        callback=self.cq_financial_institution_info))
            elif url == 'http://sjr.sh.gov.cn/ZhengWuDaTing/Index?categoryid=10&parentid=64&OgnTpPid=0':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        headers=self.default_header,
                        callback=self.sh_financial_institution_jumps))
            elif url == 'http://www.bjjrj.gov.cn/tztg/c44-a989.html':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        headers=self.default_header,
                        callback=self.bj_financial_institution))
            elif url == 'http://zdb.pedaily.cn/':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        headers=self.default_header,
                        callback=self.pedaily_in))
            elif url == 'http://www.neeq.com.cn/':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        headers=self.default_header,
                        callback=self.neeq_in))
            elif url == 'http://www.sac.net.cn/':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        headers=self.default_header,
                        callback=self.sac_in))
            elif url == 'http://www.cfachina.org/':
                req.append(self.request(
                    url,
                        redis_flag=REDISFLAG,
                        headers=self.default_header,
                        callback=self.cfa_in))

        return req

    @SpiderHelp.check_response
    def sina_trust(self, response):
        # size 
        '''
        新浪信托
        '''
        # 列表页
        # 信托产品
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[contains(text(),"查看")]/@href',
                                                   },
                                           callback=self.sina_truse_info,
                                           headers=self.default_header,
                                           method='POST',
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs2:
            yield req

        # 信托发行机构
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//div[@class="tab_blk"]/table//tr/td[3]/a/@href',
                                                   },
                                           callback=self.sina_truse_com_info,
                                           headers=self.default_header,
                                           method='POST',
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[text()="下一页"]/@onclick'
                        },
                callback=self.sina_trust,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(page),
                divmod=1,
                flag=True,
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        

    @SpiderHelp.check_response
    def sina_truse_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.SinaTrustData',
                'keys': ['TrustProdFullName','TrustProdShortName'],
                'check': 'TrustProdFullName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'prodid=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '信托产品全称',
                    'En': 'TrustProdFullName',
                    'v':
                    '//td[div[contains(text(),"信托产品全称")]]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '信托产品简称',
                    'En': 'TrustProdShortName',
                    'v':
                    '//td[contains(text(),"信托产品简称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '信托机构',
                    'En': 'Trusts',
                    'v': '//td[contains(text(),"信托机构")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '信托机构ID',
                    'En': 'TrustsID',
                    'v': '//td[contains(text(),"信托机构")]/following-sibling::td[1]/a/@href',
                    't': 'xpath_re',
                    're': 'comid=(.+)'
                },
                {
                    'n': '投资领域',
                    'En': 'InvestmentField',
                    'v': '//td[contains(text(),"投资领域")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '投资经理',
                    'En': 'InvestmentManager',
                    'v': '//td[contains(text(),"投资经理")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '产品大类',
                    'En': 'ProductCategory',
                    'v': '//td[contains(text(),"产品大类")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '是否结构化',
                    'En': 'Structured',
                    'v': '//td[contains(text(),"是否结构化")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '预计年化收益率(%)',
                    'En': 'YieldExcept',
                    'v': '//td[contains(text(),"预计年化收益率(%)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '到期年化收益率(%)',
                    'En': 'YieldToMaturity',
                    'v': '//td[contains(text(),"到期年化收益率(%)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '产品说明',
                    'En': 'ProdDescription',
                    'v': '//td[contains(text(),"产品说明")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '预期收益说明',
                    'En': 'YieldExceptDescription',
                    'v': '//td[contains(text(),"预期收益说明")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '到期收益说明',
                    'En': 'YieldToMaturityDescription',
                    'v': '//td[contains(text(),"到期收益说明")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '认购资金递增说明',
                    'En': 'ExplanationOfIncreasing',
                    'v': '//td[contains(text(),"认购资金递增说明")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '信用增级方式',
                    'En': 'CreditRating',
                    'v': '//td[contains(text(),"信用增级方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '推介起始日',
                    'En': 'RecommendStartDate',
                    'v': '//td[div[contains(text(),"推介起始日")]]/following-sibling::td[1]/div[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '推介截止日',
                    'En': 'RecommendEndDate',
                    'v': '//td[contains(text(),"推介截止日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '存续期(年)',
                    'En': 'SurvivalPeriod',
                    'v': '//td[contains(text(),"存续期(年)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//td[contains(text(),"成立日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '终止日期',
                    'En': 'EndTime',
                    'v': '//td[contains(text(),"终止日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '预计发行规模(万元)',
                    'En': 'ExpectedDistributionScale',
                    'v': '//td[contains(text(),"预计发行规模(万元)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '实际发行规模(万元)',
                    'En': 'ActualDistributionScale',
                    'v': '//td[contains(text(),"实际发行规模(万元)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行地',
                    'En': 'PlaceOfDistribution',
                    'v': '//td[contains(text(),"发行地")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最低认购资金(万元)',
                    'En': 'MinimumSubscribedFunds',
                    'v': '//td[contains(text(),"最低认购资金(万元)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_truse_com_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.SinaTrustComData',
                'keys': ['HTML_ID'],
                'check': 'HTML_ID',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'comid=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '机构名称',
                    'En': 'NameOfTrustAgency',
                    'v':
                    '//td[div[contains(text(),"机构名称")]]/following-sibling::td[1]/div[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法人代表',
                    'En': 'NameOfLegalRepresentative',
                    'v':
                    '//td[contains(text(),"法人代表")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '总经理',
                    'En': 'GeneralManager',
                    'v': '//td[contains(text(),"总经理")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '所属地区',
                    'En': 'AreaName',
                    'v': '//td[contains(text(),"所属地区")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v': '//td[contains(text(),"注册地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司电话',
                    'En': 'OfficePhoneNumber',
                    'v': '//td[contains(text(),"公司电话")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司电子邮箱',
                    'En': 'OfficeEmailAddress',
                    'v': '//td[contains(text(),"公司电子邮箱")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v': '//td[contains(text(),"经营范围")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司简介',
                    'En': 'CompanyProfile',
                    'v': '//td[contains(text(),"公司简介")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '英文名称',
                    'En': 'EnglishName',
                    'v': '//td[div[contains(text(),"英文名称")]]/following-sibling::td[1]/div[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '董事长',
                    'En': 'Chairman',
                    'v': '//td[contains(text(),"董事长")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//td[contains(text(),"成立日期")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资本(万元)',
                    'En': 'RegisteredCapital',
                    'v': '//td[contains(text(),"注册资本(万元)")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '办公地址',
                    'En': 'OfficeAddress',
                    'v': '//td[contains(text(),"办公地址")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司传真',
                    'En': 'OfficeFaxNumber',
                    'v': '//td[contains(text(),"公司传真")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司网址',
                    'En': 'OfficeWebsite',
                    'v': '//td[contains(text(),"公司网址")]/following-sibling::td[1]/div/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_stock_in(self,response):
        # 解析js获取param页面
        regex = re.compile('\{.*\}',re.S)
        result = regex.search(response.text).group(0)
        JS = json.loads(result)
        key_list = list(JS['stock']['category']['schq']['category']['hsgs']['category'].keys())
        # ['qbag', 'zxqy', 'cyb', 'xlhy', 'gnbk', 'dybk', 'zs', 'zscf', 'szzz', 'szcz', 'hs300']
        # 前3为全部A股,中小板,创业板key
        for key in key_list[0:3]:
            url = 'http://finance.sina.com.cn/data/blocks/stock_schq_hsgs_%s.txt' % key
            yield _Request(url,
                headers=self.default_header,
                priority=10000,
                redis_flag=True,
                redis_conn=self.r,
                callback=self.sina_stock_get_param)
    
    @SpiderHelp.check_response
    def sina_stock_get_param(self, response):
        # 正则提取param
        regex = re.compile('param:\"(.*?)\"')
        param = regex.search(response.text).group(1)
        # 拼接url
        formatter = "http://money.finance.sina.com.cn/d/api/openapi_proxy.php/?__s=["+param+"]"+"&callback=FDC_DC.theTableData"
        url = formatter.format(sort='', asc=0, page=1, num=40)
        yield scrapy.Request(url,
            headers=self.default_header,
            meta={'formatter':formatter,'proxys':True},
            priority=30000,
            callback=self.sina_stock_list)

    @SpiderHelp.check_response
    def sina_stock_list(self, response):
        response = response.replace(body=re.search('\{.*?\}',response.text,re.S).group(0))
        # size 
        '''
        新浪股票
        '''

        # #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'count'
                        },
                callback=self.sina_stock_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(sort='', asc=0, page=page, num=40),
                divmod=40,
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='json')
        for req in reqs:
            yield req

        #  排序相同
        # '"symbol","code","name","trade","pricechange","changepercent","buy","sell","settlement","open","high","low","volume","amount","ticktime","per","per_d","nta","pb","mktcap","nmc","turnoverratio","favor","guba"'
        # '"symbol","code","name","trade","pricechange","changepercent","buy","sell","settlement","open","high","low","volume","amount","ticktime","per","per_d","nta","pb","mktcap","nmc","turnoverratio","favor","guba"'
        # '"symbol","code","name","trade","pricechange","changepercent","buy","sell","settlement","open","high","low","volume","amount","ticktime","per","per_d","nta","pb","mktcap","nmc","turnoverratio","favor","guba"'

        # 列表页
        # 股票
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'items',
                                                   },
                                           callback=self.sina_stock_com,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://finance.sina.com.cn/realstock/company/%s/nc.shtml' % page[0],
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs2:
            yield req

    @SpiderHelp.check_response
    def sina_stock_com(self, response):
        #  公司简介
        reqs = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="公司简介"]/@href',
                                                   },
                                           callback=self.sina_stock_com_info,
                                           headers=self.default_header,
                                           priority=1000,
                                           meta={'proxys':True},
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs:
            yield req 

        # # 公司高管
        # reqs = self.scrapy_info_url_help( response,
        #                                    config={'t': 'xpath_first',
        #                                            'v': '//a[text()="公司高管"]/@href',
        #                                            },
        #                                    callback=self.sina_com_senior_executive_info,
        #                                    headers=self.default_header,
        #                                    priority=1000,
        #                                    meta={'proxys':True},
        #                                    urlfunc=
        #                                    lambda page, response: page,
        #                                    errback=self.errbackparse,
        #                                    response_type='xpath')
        # for req in reqs:
        #     yield req 

        #  所属行业,所属板块
        reqs = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="所属行业"]/@href',
                                                   },
                                           callback=self.sina_stock_com_industry_classification,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs:
            yield req 
        # #  股本结构
        # reqs2 = self.scrapy_info_url_help( response,
        #                                    config={'t': 'xpath_first',
        #                                            'v': '//a[text()="股本结构"]/@href',
        #                                            },
        #                                    callback=self.sina_stock_com_capital_structure,
        #                                    headers=self.default_header,
        #                                    urlfunc=
        #                                    lambda page, response: page,
        #                                    priority=1000,
        #                                    meta={'proxys':True},
        #                                    errback=self.errbackparse,
        #                                    response_type='xpath')
        # for req in reqs2:
        #     yield req

        # #  主要股东
        # reqs3 = self.scrapy_info_url_help( response,
        #                                    config={'t': 'xpath_re',
        #                                            'v': '//a[text()="主要股东"]/@href',
        #                                            're': '(https?:\/\/.*?)\/displaytype'
        #                                            },
        #                                    callback=self.sina_stock_com_major_shareholders,
        #                                    headers=self.default_header,
        #                                    urlfunc=
        #                                    lambda page, response: page + '.phtml',
        #                                    priority=1000,
        #                                    meta={'proxys':True},
        #                                    errback=self.errbackparse,
        #                                    response_type='xpath')
        # for req in reqs3:
        #     yield req

        # #  流通股东
        # reqs3 = self.scrapy_info_url_help( response,
        #                                    config={'t': 'xpath_re',
        #                                            'v': '//a[text()="流通股东"]/@href',
        #                                            're': '(https?:\/\/.*?)\/displaytype'
        #                                            },
        #                                    callback=self.sina_stock_com_circulating_shareholders,
        #                                    headers=self.default_header,
        #                                    urlfunc=
        #                                    lambda page, response: page + '.phtml',
        #                                    priority=1000,
        #                                    meta={'proxys':True},
        #                                    errback=self.errbackparse,
        #                                    response_type='xpath')
        # for req in reqs3:
        #     yield req
        # #  基金持股
        # reqs4 = self.scrapy_info_url_help( response,
        #                                    config={'t': 'xpath_re',
        #                                            'v': '//a[text()="基金持股"]/@href',
        #                                            're': '(https?:\/\/.*?)\/displaytype'
        #                                            },
        #                                    callback=self.sina_com_fund_shares,
        #                                    headers=self.default_header,
        #                                    urlfunc=
        #                                    lambda page, response: page + '.phtml',
        #                                    priority=1000,
        #                                    meta={'proxys':True},
        #                                    errback=self.errbackparse,
        #                                    response_type='xpath')
        # for req in reqs4:
        #     yield req

        # #  融资融券
        # reqs4 = self.scrapy_info_url_help( response,
        #                                    config={'t': 'xpath_re',
        #                                            'v': '//a[text()="融资融券"]/@href',
        #                                            're': '(https?:\/\/.*?)bdate'
        #                                            },
        #                                    callback=self.sina_com_margin_financing,
        #                                    headers=self.default_header,
        #                                    urlfunc=
        #                                    lambda page, response: page + 'bdate=2001-01-01&edate={}'.format(TODAY),
        #                                    priority=1000,
        #                                    meta={'proxys':True},
        #                                    errback=self.errbackparse,
        #                                    response_type='xpath')
        # for req in reqs4:
        #     yield req

        # #  内部交易
        # reqs4 = self.scrapy_info_url_help( response,
        #                                    config={'t': 'xpath_re',
        #                                            'v': '//a[text()="内部交易"]/@href',
        #                                            're': '(https?:\/\/.*?)bdate'
        #                                            },
        #                                    callback=self.sina_com_internal_transaction,
        #                                    headers=self.default_header,
        #                                    urlfunc=
        #                                    lambda page, response: page + 'bdate=2001-01-01&edate={}'.format(TODAY),
        #                                    priority=1000,
        #                                    meta={'proxys':True},
        #                                    errback=self.errbackparse,
        #                                    response_type='xpath')
        # for req in reqs4:
        #     yield req

        # #  大宗交易
        # reqs4 = self.scrapy_info_url_help( response,
        #                                    config={'t': 'xpath_re',
        #                                            'v': '//a[text()="大宗交易"]/@href',
        #                                            're': '(https?:\/\/.*?)bdate'
        #                                            },
        #                                    callback=self.sina_com_block_trade,
        #                                    headers=self.default_header,
        #                                    urlfunc=
        #                                    lambda page, response: page + 'bdate=2001-01-01&edate={}'.format(TODAY),
        #                                    priority=1000,
        #                                    meta={'proxys':True},
        #                                    errback=self.errbackparse,
        #                                    response_type='xpath')
        # for req in reqs4:
        #     yield req

        # #  历史交易 页面跳转 获取年份列表 详细页可跳转 每日交易明细
        # reqs4 = self.scrapy_info_url_help( response,
        #                                    config={'t': 'xpath_first',
        #                                            'v': '//a[text()="历史交易"]/@href',
        #                                            },
        #                                    callback=self.sina_com_historical_transaction,
        #                                    headers=self.default_header,
        #                                    urlfunc=
        #                                    lambda page, response: page,
        #                                    priority=1000,
        #                                    meta={'proxys':True},
        #                                    errback=self.errbackparse,
        #                                    response_type='xpath')
        # for req in reqs4:
        #     yield req



        # #  复权交易 页面跳转 获取年份列表
        # reqs4 = self.scrapy_info_url_help( response,
        #                                    config={'t': 'xpath_first',
        #                                            'v': '//a[text()="复权交易"]/@href',
        #                                            },
        #                                    callback=self.sina_com_right_transaction,
        #                                    headers=self.default_header,
        #                                    urlfunc=
        #                                    lambda page, response: page,
        #                                    priority=1000,
        #                                    meta={'proxys':True},
        #                                    errback=self.errbackparse,
        #                                    response_type='xpath')
        # for req in reqs4:
        #     yield req

        # 持仓明细 可以需要抓取交易明细数据后 聚合计算 买入 卖出 向量运算

        #  分红送配
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="分红送配"]/@href',
                                                   },
                                           callback=self.sina_com_dividends_and_allotment,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req

        #  新股发行
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="新股发行"]/@href',
                                                   },
                                           callback=self.sina_com_ipo,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req

        # #  限售解禁
        # reqs4 = self.scrapy_info_url_help( response,
        #                                    config={'t': 'xpath_first',
        #                                            'v': '//a[text()="限售解禁"]/@href',
        #                                            },
        #                                    callback=self.sina_com_lift_a_ban_on_sale,
        #                                    headers=self.default_header,
        #                                    urlfunc=
        #                                    lambda page, response: page + '&p=1',
        #                                    priority=1000,
        #                                    meta={'proxys':True},
        #                                    errback=self.errbackparse,
        #                                    response_type='xpath')
        # for req in reqs4:
        #     yield req

        #  增发
        reqs4 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_first',
                                                   'v': '//a[text()="增发"]/@href',
                                                   },
                                           callback=self.sina_com_seasoned_new_issue,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           priority=1000,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs4:
            yield req


        

    @SpiderHelp.check_response
    def sina_stock_com_info(self, response):
        # 新浪公司基本信息
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComInfoData',
                'keys': ['ComCode'],
                'check': 'ComCode',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },
                {
                    'n': '公司名称',
                    'En': 'ComFullName',
                    'v':
                    '//td[contains(text(),"公司名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//h1[@id="stockName"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司代码',
                    'En': 'ComCode',
                    'v':
                    '//h1[@id="stockName"]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司英文名称',
                    'En': 'ComEnglishName',
                    'v':
                    '//td[contains(text(),"公司英文名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '上市市场',
                    'En': 'ListedMarket',
                    'v': '//td[contains(text(),"上市市场")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '发行价格',
                    'En': 'IssuePrice',
                    'v': '//td[contains(text(),"发行价格")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//td[contains(text(),"成立日期")]/following-sibling::td[1]//text()',
                    't': 'xpath_first'
                },
                {
                    'n': '机构类型',
                    'En': 'OrganizationType',
                    'v': '//td[contains(text(),"机构类型")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '董事会秘书',
                    'En': 'SecretaryName',
                    'v': '//td[contains(text(),"董事会秘书")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '董秘电话',
                    'En': 'SecretaryPhoneNumber',
                    'v': '//td[contains(text(),"董秘电话")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '董秘传真',
                    'En': 'SecretaryFaxNumber',
                    'v': '//td[contains(text(),"董秘传真")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '董秘电子邮箱',
                    'En': 'SecretaryEmailAddress',
                    'v': '//td[contains(text(),"董秘电子邮箱")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '邮政编码',
                    'En': 'ZipCode',
                    'v': '//td[contains(text(),"邮政编码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证券简称更名历史',
                    'En': 'RenameHistory',
                    'v': '//td[contains(text(),"证券简称更名历史")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v': '//td[contains(text(),"注册地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '办公地址',
                    'En': 'OfficeAddress',
                    'v': '//td[contains(text(),"办公地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司简介',
                    'En': 'Companyprofile',
                    'v': '//td[contains(text(),"公司简介")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v': '//td[contains(text(),"经营范围")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市日期',
                    'En': 'ListedDate',
                    'v': '//td[contains(text(),"上市日期")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '主承销商',
                    'En': 'MainUnderwriter',
                    'v': '//td[contains(text(),"主承销商")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资本',
                    'En': 'RegisteredCapital',
                    'v': '//td[contains(text(),"注册资本")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '组织形式',
                    'En': 'OrganizationalForm',
                    'v': '//td[contains(text(),"组织形式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司电话',
                    'En': 'OfficePhoneNumber',
                    'v': '//td[contains(text(),"公司电话")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司传真',
                    'En': 'OfficeFaxNumber',
                    'v': '//td[contains(text(),"公司传真")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司电子邮箱',
                    'En': 'OfficeEmailAddress',
                    'v': '//td[contains(text(),"公司电子邮箱")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司网址',
                    'En': 'OfficeWebsite',
                    'v': '//td[contains(text(),"公司网址")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '信息披露网址',
                    'En': 'DisclosureWebsite',
                    'v': '//td[contains(text(),"信息披露网址")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_senior_executive_info(self, response):
        #//*[@id="comInfo1"]/tbody/tr[39]
        #
        _configs = [{
            'list': {
                'n': '',
                'v': '//*[@id="comInfo1"]//tr[td[last()=4] and td[@class="ccl"]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_SeniorExcutive',
                'keys': ['CompanyName','Name','Title','postion'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v':
                    '//h1[@id="stockName"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '任期',
                    'En': 'Capital',
                    'v':
                    '../..//tr/th/text()',
                    't': 'xpath_first'
                },{
                    'n': '标题',
                    'En': 'Title',
                    'v':
                    './preceding-sibling::tr[td[last()=1]][1]/td/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '高管姓名',
                    'En': 'Name',
                    'v':
                    './td[1]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '职务',
                    'En': 'postion',
                    'v':
                    './td[2]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '任期开始',
                    'En': 'StartTime',
                    'v':
                    './td[3]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '任期结束',
                    'En': 'EndTime',
                    'v':
                    './td[4]/div/text()',
                    't': 'xpath_first'
                },
                
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_stock_com_industry_classification(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComClassification',
                'keys': ['HTML_ID'],
                'check': 'ComShortName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\/',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//h1[@id="stockName"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '所属行业板块',
                    'En': 'IndustryPlate',
                    'v':
                    '//div[@class="tagmain"]/table[@class="comInfo1"][1]//tr[position()>2 and td[last()=2]]/td[1]/text()',
                    't': 'xpath_join,'
                },{
                    'n': '所属概念板块',
                    'En': 'ConceptualPlate',
                    'v':
                    '//div[@class="tagmain"]/table[@class="comInfo1"][2]//tr[position()>2 and td[last()=2]]/td[1]/text()',
                    't': 'xpath_join,'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_stock_com_capital_structure(self, response):
        # 最多五列
        # 竖向迭代
        for i in range(2,7):
            _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="tagmain"]/table',    
                    't': 'xpath',
                    'db': 'CreditDataBase.Sina_ListedComCapitalStructure',
                    'keys': ['HTML_ID','DateOfChange','CauseOfChange'],
                    'check': 'DateOfChange',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID',
                        'En': 'HTML_ID',
                        'v':
                        'stockid\/(.+?)\.phtml',
                        't': 'url_re'
                    },
                    {
                        'n': '公司简称',
                        'En': 'ComShortName',
                        'v':
                        '//div[@class="tbtb01"]/h1/a/text()',
                        't': 'xpath_first'
                    },{
                        'n': '变动日期',
                        'En': 'DateOfChange',
                        'v':
                        './/tr[td[contains(text(),"变动日期")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '公告日期',
                        'En': 'DateOfAnnouncement',
                        'v':
                        './/tr[td[contains(text(),"公告日期")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '变动原因',
                        'En': 'CauseOfChange',
                        'v':
                        './/tr[td[contains(text(),"变动原因")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '总股本',
                        'En': 'TotalCapitalStock',
                        'v':
                        './/tr[td[contains(text(),"总股本")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '流通A股',
                        'En': 'CirculationOfAshares',
                        'v':
                        './/tr[td[contains(text(),"流通A股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '高管股',
                        'En': 'ExecutiveStock',
                        'v':
                        './/tr[td[contains(text(),"高管股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '限售A股',
                        'En': 'LimitedSaleOfAshares',
                        'v':
                        './/tr[td[contains(text(),"限售A股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '流通B股',
                        'En': 'CirculationOfBshares',
                        'v':
                        './/tr[td[contains(text(),"流通B股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '限售B股',
                        'En': 'LimitedSaleOfBshares',
                        'v':
                        './/tr[td[contains(text(),"限售B股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '流通H股',
                        'En': 'CirculationOfHshares',
                        'v':
                        './/tr[td[contains(text(),"流通H股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '国家股',
                        'En': 'StateOwnedShare',
                        'v':
                        './/tr[td[contains(text(),"国家股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '国有法人股',
                        'En': 'StateOwnedCorporateShares',
                        'v':
                        './/tr[td[contains(text(),"国有法人股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '境内法人股',
                        'En': 'DomesticLegalPersonShares',
                        'v':
                        './/tr[td[contains(text(),"境内法人股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '境内发起人股',
                        'En': 'DomesticSponsorsStock',
                        'v':
                        './/tr[td[contains(text(),"境内发起人股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '募集法人股',
                        'En': 'RaisingCorporateShares',
                        'v':
                        './/tr[td[contains(text(),"募集法人股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '一般法人股',
                        'En': 'GeneralCorporateShares',
                        'v':
                        './/tr[td[contains(text(),"一般法人股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '战略投资者持股',
                        'En': 'ShareholdingOfStrategicInvestors',
                        'v':
                        './/tr[td[contains(text(),"战略投资者持股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '基金持股',
                        'En': 'FundShares',
                        'v':
                        './/tr[td[contains(text(),"基金持股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '转配股',
                        'En': 'AllotmentOfShares',
                        'v':
                        './/tr[td[contains(text(),"转配股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '内部职工股',
                        'En': 'InternalEmployeeStock',
                        'v':
                        './/tr[td[contains(text(),"内部职工股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },{
                        'n': '优先股',
                        'En': 'PreferredStock',
                        'v':
                        './/tr[td[contains(text(),"优先股")]]/td[%s]/text()' % i,
                        't': 'xpath_first'
                    },
                ]
            }]
            results = self.item_parse(_configs, response)
            for item in results:
                yield item

    @SpiderHelp.check_response
    def sina_stock_com_major_shareholders(self, response):
        # 主要股东
        _configs = [{
            'list': {
                'n': '',
                'v': '//tr[td[last()=5] and td[.//a]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComMajorShareHolders',
                'keys': ['HTML_ID','ShareholderName','Deadline'],
                'check': 'ShareholderName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '截至日期',
                    'En': 'Deadline',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="截至日期"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="公告日期"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股东说明',
                    'En': 'ShareHoldersExplanation',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="股东说明"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股东总数',
                    'En': 'TotalNumberOfShareholders',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="股东总数"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '平均持股数',
                    'En': 'AverageStockHoldingNumber',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="平均持股数"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股东名称',
                    'En': 'ShareholderName',
                    'v':
                    './td[2]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '排序',
                    'En': 'Rank',
                    'v':
                    './td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '持股数量(股)',
                    'En': 'StockHoldingNumber',
                    'v':
                    './td[3]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '持股比例(%)',
                    'En': 'ShareholdingRatio',
                    'v':
                    './td[4]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '股本性质',
                    'En': 'NatureOfCapitalStock',
                    'v':
                    './td[5]/div/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_stock_com_circulating_shareholders(self, response):
        # 流通股东
        _configs = [{
            'list': {
                'n': '',
                'v': '//tr[td[last()=5] and td[1][div[text()>0]]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComCirculatingShareholders',
                'keys': ['HTML_ID','ShareholderName','Deadline'],
                'check': 'ShareholderName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '截止日期',
                    'En': 'Deadline',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="截止日期"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="公告日期"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股东名称',
                    'En': 'ShareholderName',
                    'v':
                    './td[2]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '排序',
                    'En': 'Rank',
                    'v':
                    './td[1]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '持股数量(股)',
                    'En': 'StockHoldingNumber',
                    'v':
                    './td[3]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '占流通股比例(%)',
                    'En': 'ProportionOfCirculatingShares',
                    'v':
                    './td[4]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '股本性质',
                    'En': 'NatureOfCapitalStock',
                    'v':
                    './td[5]/div/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_fund_shares(self, response):
        # 基金持股
        _configs = [{
            'list': {
                'n': '',
                'v': '//tr[td[last()=6] and td[2][div[a[text()>0]]]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComFundShares',
                'keys': ['HTML_ID','FundCode','Deadline'],
                'check': 'FundCode',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '截止日期',
                    'En': 'Deadline',
                    'v':
                    './preceding-sibling::tr[.//strong[text()="截止日期"]][1]/td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '基金名称',
                    'En': 'NameOfFundProd',
                    'v':
                    './td[1]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '基金代码',
                    'En': 'FundCode',
                    'v':
                    './td[2]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '持仓数量(股)',
                    'En': 'HoldingNumber',
                    'v':
                    './td[3]/div/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '占流通股比例(%)',
                    'En': 'ProportionOfCirculatingShares',
                    'v':
                    './td[4]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '持股市值（元）',
                    'En': 'StockMarketValue',
                    'v':
                    './td[5]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '占净值比例（%）',
                    'En': 'ProportionOfNetValue',
                    'v':
                    './td[6]/div/a/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_margin_financing(self, response):
        # 融资融券字段提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="list_table"]//tr[td[1][text()>0]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComMarginFinancing',
                'keys': ['HTML_ID','DateOfTransaction'],
                'check': 'DateOfTransaction',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'symbol=[a-zA-Z]*(\d+?)&',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//table[@class="list_table"]//tr[1]/td/span/text()',
                    't': 'xpath_re',
                    're':'\s*(\S+)\s*融资融券交易明细'
                },{
                    'n': '日期',
                    'En': 'DateOfTransaction',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融资余额',
                    'En': 'FinancingBalance',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融资买入额',
                    'En': 'FinancingBuyingAmount',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融资偿还额',
                    'En': 'FinancingReimbursement',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融资余量金额',
                    'En': 'AmountOfFinancialRemainder',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融券余量',
                    'En': 'FinancingMargin',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融券卖出量',
                    'En': 'MarginSelling',
                    'v':
                    './td[8]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融券偿还量',
                    'En': 'MarginRepayment',
                    'v':
                    './td[9]/text()',
                    't': 'xpath_first'
                },{
                    'n': '融券余额',
                    'En': 'MarginBalance',
                    'v':
                    './td[10]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_internal_transaction(self, response):
        # 内部交易字段提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="list_table"]//tr[td[a[string-length(text())=6]]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComInternalTransaction',
                'keys': ['HTML_ID','ChangingPerson','ChangeDate','PostChangeStockHoldingNumber'],
                'check': 'ChangingPerson',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    './td[1]/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    './td[2]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '变动人',
                    'En': 'ChangingPerson',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '变动类型',
                    'En': 'ChangeType',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '变动股数',
                    'En': 'VariableNumberOfShares',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成交均价',
                    'En': 'AverageTransactionPrice',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '变动金额(万元)',
                    'En': 'AmountOfChange',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '变动后持股数',
                    'En': 'PostChangeStockHoldingNumber',
                    'v':
                    './td[8]/text()',
                    't': 'xpath_first'
                },{
                    'n': '变动原因',
                    'En': 'ChangeReason',
                    'v':
                    './td[9]/text()',
                    't': 'xpath_first'
                },{
                    'n': '变动日期',
                    'En': 'ChangeDate',
                    'v':
                    './td[10]/text()',
                    't': 'xpath_first'
                },{
                    'n': '持股种类',
                    'En': 'TypeOfStockOwnership',
                    'v':
                    './td[11]/text()',
                    't': 'xpath_first'
                },{
                    'n': '与董监高关系',
                    'En': 'RelationsWithDirector',
                    'v':
                    './td[12]/text()',
                    't': 'xpath_first'
                },{
                    'n': '董监高职务',
                    'En': 'DirectorPosition',
                    'v':
                    './td[13]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[text()="下一页"]/@onclick'
                        },
                callback=self.sina_com_internal_transaction,
                headers=self.default_header,
                urlfunc=
                lambda page, response: re.compile('(https?:\/\/.*?)bdate').search(response.url).group(1) + 'bdate=2001-01-01&edate={}'.format(TODAY) + '&p={}'.format(page),
                divmod=1,
                flag=True,
                redis_conn=self.r,
                redis_flag=True,
                readpage=5,
                response_type='xpath')
        for req in reqs:
            yield req

    def sina_com_block_trade(self, response):
        # 大宗交易字段提取
        # 字段可能会重复  -- 字段完全相同 
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="list_table"]//tr[td[a[string-length(text())=6]]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComBlockTrade',
                'keys': ['HTML_ID','DateOfTransaction','Buyer','Seller','TransactionAmount'],
                'check': 'DateOfTransaction',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '交易日期',
                    'En': 'DateOfTransaction',
                    'v':
                    './td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    './td[2]/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    './td[3]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '成交价格(元)',
                    'En': 'TransactionPrice',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成交量(万股)',
                    'En': 'TransactionVolume',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成交金额(万元)',
                    'En': 'TransactionAmount',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '买方营业部',
                    'En': 'Buyer',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '卖方营业部',
                    'En': 'Seller',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证券类型',
                    'En': 'TypeOfShares',
                    'v':
                    './td[8]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[text()="下一页"]/@onclick'
                        },
                callback=self.sina_com_block_trade,
                headers=self.default_header,
                urlfunc=
                lambda page, response: re.compile('(https?:\/\/.*?)bdate').search(response.url).group(1) + 'bdate=2001-01-01&edate={}'.format(TODAY) + '&p={}'.format(page),
                divmod=1,
                flag=True,
                redis_conn=self.r,
                redis_flag=True,
                readpage=5,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sina_com_historical_transaction(self, response):
        # 生成generotor对象 会多几个无效页面 忽略(无法验证--起始好像可以从日期伪造,略过)
        years = response.xpath('//select[@name="year"]/option/@value').extract()
        jidus = response.xpath('//select[@name="jidu"]/option/@value').extract()
        # 节省内存
        urls = ('%s?year=%s&jidu=%s' % (response.url,year,jidu) for year in years for jidu in jidus)
        for url in urls:
            yield scrapy.Request(url,
                headers=self.default_header,
                priority=1000,
                callback=self.sina_com_historical_transaction_info)

    @SpiderHelp.check_response
    def sina_com_historical_transaction_info(self, response):
        # 历史交易字段提取
        # 这里可以跳转历史交易详细... 数据量庞大 再考虑
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="FundHoldSharesTable"]//tr[td[1][div/a/@href]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComHistoricalTransaction',
                'keys': ['HTML_ID','DateOfTransaction'],
                'check': 'DateOfTransaction',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(\d+)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '交易日期',
                    'En': 'DateOfTransaction',
                    'v':
                    './td[1]/div/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '开盘价',
                    'En': 'OpenPrice',
                    'v':
                    './td[2]/div/text()',
                    't': 'xpath_first',
                },{
                    'n': '最高价',
                    'En': 'HighestPrice',
                    'v':
                    './td[3]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '收盘价',
                    'En': 'ClosingPrice',
                    'v':
                    './td[4]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '最低价',
                    'En': 'MinimumPrice',
                    'v':
                    './td[5]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易量(股)',
                    'En': 'VolumeOfTransaction',
                    'v':
                    './td[6]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易金额(元)',
                    'En': 'TransactionAmount',
                    'v':
                    './td[7]/div/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        # # 成交明细
        # # http://market.finance.sina.com.cn/transHis.php?date=2013-03-29&symbol=sh600010&page=1
        # # 数据量庞大 
        # urls_generator = ('http://market.finance.sina.com.cn/transHis.php?'+ url+'&page=1' for url in response.xpath('//table[@id="FundHoldSharesTable"]//tr[td[1][div/a/@href]]/td[1]/div/a/@href').re('(symbol=.+)'))
        # for url in urls_generator:
        #     yield scrapy.Request(
        #         url,
        #         headers=self.default_header,
        #         priority=3000,
        #         callback=self.sina_com_transaction_details)

    @SpiderHelp.check_response
    def sina_com_transaction_details(self, response):
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': "detailPages=.*?\[(\d+),'\d+:\d+:\d+','\d+:\d+:\d+']];;"
                        },
                callback=self.sina_com_transaction_details,
                headers=self.default_header,
                urlfunc=
                lambda page, response: re.compile('(https?:\/\/.*?&page=)').search(response.url).group(1) + str(page),
                divmod=1,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # 每日交易明细 时间序列
        _configs = [{
            'list': {
                'n': '',
                'v': '//table//tr[.//*[contains(text(),":")]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComTransactionDetails',
                'keys': ['HTML_ID','DateOfTransaction','TimeOfTransaction','VolumeOfTransaction','Nature'],
                'check': 'TimeOfTransaction',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'symbol=(.+?)&',
                    't': 'url_re'
                },
                {
                    'n': '交易日期',
                    'En': 'DateOfTransaction',
                    'v':
                    'date=(.+?)&',
                    't': 'url_re'
                },
                {
                    'n': '成交时间',
                    'En': 'TimeOfTransaction',
                    'v':
                    './*[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '成交价',
                    'En': 'TransactionPrice',
                    'v':
                    './*[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '价格变动',
                    'En': 'PriceChange',
                    'v':
                    './*[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成交量(手)',
                    'En': 'VolumeOfTransaction',
                    'v':
                    './*[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成交额(元)',
                    'En': 'Turnover',
                    'v':
                    './*[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '性质',
                    'En': 'Nature',
                    'v':
                    './*[6]/*[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_right_transaction(self, response):
        # 生成generotor对象 会多几个无效页面 忽略(无法验证--起始好像可以从日期伪造,略过)
        years = response.xpath('//select[@name="year"]/option/@value').extract()
        jidus = response.xpath('//select[@name="jidu"]/option/@value').extract()
        # 节省内存
        urls = ('%s?year=%s&jidu=%s' % (response.url,year,jidu) for year in years for jidu in jidus)
        for url in urls:
            yield self.request(url,
                headers=self.default_header,
                callback=self.sina_com_right_transaction_info)

    @SpiderHelp.check_response
    def sina_com_right_transaction_info(self, response):
        # 复权交易分列信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="FundHoldSharesTable"]//tr[td[1][div/a/@href]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComRightTransaction',
                'keys': ['HTML_ID','DateOfTransaction'],
                'check': 'DateOfTransaction',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(\d+)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '交易日期',
                    'En': 'DateOfTransaction',
                    'v':
                    './td[1]/div/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '开盘价',
                    'En': 'OpenPrice',
                    'v':
                    './td[2]/div/text()',
                    't': 'xpath_first',
                },{
                    'n': '最高价',
                    'En': 'HighestPrice',
                    'v':
                    './td[3]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '收盘价',
                    'En': 'ClosingPrice',
                    'v':
                    './td[4]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '最低价',
                    'En': 'MinimumPrice',
                    'v':
                    './td[5]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易量(股)',
                    'En': 'VolumeOfTransaction',
                    'v':
                    './td[6]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易金额(元)',
                    'En': 'TransactionAmount',
                    'v':
                    './td[7]/div/text()',
                    't': 'xpath_first'
                },{
                    'n': '复权因子',
                    'En': 'RightFactor',
                    'v':
                    './td[8]/div/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_dividends_and_allotment(self, response):
        # # 进详情页
        # sharebonus_1 = ('http://vip.stock.finance.sina.com.cn' + url for url in response.xpath('//table[@id="sharebonus_1"]//a[contains(text(),"查看")]/@href').extract())
        # sharebonus_2 = ('http://vip.stock.finance.sina.com.cn' + url for url in response.xpath('//table[@id="sharebonus_2"]//a[contains(text(),"查看")]/@href').extract())
        # # 股息
        # for url in sharebonus_1:
        #     yield scrapy.Request(url,
        #         headers=self.default_header,
        #         callback=self.sina_com_dividends)

        # # 配股
        # for url in sharebonus_2:
        #     yield scrapy.Request(url,
        #         headers=self.default_header,
        #         callback=self.sina_com_allotment)

        # 红利信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="sharebonus_1"]//tr[td[1][contains(text(),"-")]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComDividends',
                'keys': ['HTML_ID','DateOfAnnouncement'],
                'check': 'DateOfAnnouncement',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '送股(股)-每10股',
                    'En': 'BonusShares',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first',
                },{
                    'n': '转增(股)-每10股',
                    'En': 'TransferOfShares',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '派息(税前)(元)-每10股',
                    'En': 'PreTaxDividend',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '进度',
                    'En': 'Schedule',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '除权除息日',
                    'En': 'ExDividendDate',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股权登记日',
                    'En': 'ShareholdersOfRecordDate',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '红股上市日',
                    'En': 'BonusSharesListedDate',
                    'v':
                    './td[8]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        # 配股信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="sharebonus_2"]//tr[td[1][contains(text(),"-")]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComAllotment',
                'keys': ['HTML_ID','DateOfAnnouncement'],
                'check': 'DateOfAnnouncement',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '配股方案(每10股配股股数)',
                    'En': 'AllotmentOffering',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first',
                },{
                    'n': '配股价格(元)',
                    'En': 'AllotmentPrice',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '基准股本(万股)',
                    'En': 'BenchmarkShareCapital',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '除权日',
                    'En': 'ExRightDate',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股权登记日',
                    'En': 'ShareholdersOfRecordDate',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '缴款起始日',
                    'En': 'PaymentStartDate',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '缴款终止日',
                    'En': 'PaymentEndDate',
                    'v':
                    './td[8]/text()',
                    't': 'xpath_first'
                },{
                    'n': '配股上市日 ',
                    'En': 'AllotmentListedDate',
                    'v':
                    './td[9]/text()',
                    't': 'xpath_first'
                },{
                    'n': '募集资金合计(元)',
                    'En': 'CollectionOfCapital',
                    'v':
                    './td[10]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_ipo(self, response):
        # 上市信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="comInfo1"]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedComIpo',
                'keys': ['HTML_ID'],
                'check': 'StockExchange',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '上市地',
                    'En': 'StockExchange',
                    'v':
                    './/td[.//*[contains(text(),"上市地")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '主承销商',
                    'En': 'MainUnderwriter',
                    'v':
                    './/td[.//*[contains(text(),"主承销商")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '承销方式',
                    'En': 'AllotmentPrice',
                    'v':
                    './/td[.//*[contains(text(),"承销方式")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市推荐人',
                    'En': 'ListedRecommendation',
                    'v':
                    './/td[.//*[contains(text(),"上市推荐人")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '每股发行价(元)',
                    'En': 'PricePerShare',
                    'v':
                    './/td[.//*[contains(text(),"每股发行价")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行方式',
                    'En': 'DistributionMode',
                    'v':
                    './/td[.//*[contains(text(),"发行方式")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行市盈率（按发行后总股本）',
                    'En': 'IPO_PE_Ratio',
                    'v':
                    './/td[.//*[contains(text(),"发行市盈率")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '首发前总股本（万股）',
                    'En': 'PreStartTotalEquity',
                    'v':
                    './/td[.//*[contains(text(),"首发前总股本")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '首发后总股本（万股）',
                    'En': 'FirstPostTotalEquity',
                    'v':
                    './/td[.//*[contains(text(),"首发后总股本")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '实际发行量（万股）',
                    'En': 'ActualCirculation',
                    'v':
                    './/td[.//*[contains(text(),"实际发行量")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '预计募集资金（万元）',
                    'En': 'ExpectedFundRaising',
                    'v':
                    './/td[.//*[contains(text(),"预计募集资金")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '实际募集资金合计（万元）',
                    'En': 'ActualFundRaising',
                    'v':
                    './/td[.//*[contains(text(),"实际募集资金合计")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行费用总额（万元）',
                    'En': 'TotalIssueCost',
                    'v':
                    './/td[.//*[contains(text(),"发行费用总额")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '募集资金净额（万元）',
                    'En': 'NetRaisedFunds',
                    'v':
                    './/td[.//*[contains(text(),"募集资金净额")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '承销费用（万元）',
                    'En': 'UnderwritingFee',
                    'v':
                    './/td[.//*[contains(text(),"承销费用")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '招股公告日',
                    'En':'AnnouncementDate',
                    'v':
                    './/td[.//*[contains(text(),"招股公告日")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市日期',
                    'En': 'ListedDate',
                    'v':
                    './/td[.//*[contains(text(),"上市日期")]]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_com_lift_a_ban_on_sale(self, response):
        # 限售解禁提取  可能翻页
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="dataTable"]//tr[td[1]//a[string-length(text())=6]]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedUnBanOnSale',
                'keys': ['HTML_ID','DateOfUnBanDate'],
                'check': 'HTML_ID',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    './td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    './td[2]/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '解禁日期',
                    'En': 'DateOfUnBanDate',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '解禁数量(万股)',
                    'En': 'UnBanNumbers',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first',
                },{
                    'n': '解禁股流通市值(亿元)',
                    'En': 'UnbanStockCirculationMarketValue',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市批次',
                    'En': 'ListedBatch',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        # 翻页逻辑
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[text()="下一页" and @class="page"]'
                        },
                callback=self.sina_com_lift_a_ban_on_sale,
                headers=self.default_header,
                urlfunc=
                lambda page, response: re.compile('(https?:\/\/.*?&p=)').search(response.url).group(1) + str(page),
                divmod=1,
                flag=True,
                readpage=2,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sina_com_seasoned_new_issue(self, response):
        # 增发新股信息提取    不定序
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[contains(@id,"addStock")]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ListedSeasonedNewIssue',
                'keys': ['HTML_ID','DateOfAnnouncement','AdditionalType'],
                'check': 'AdditionalType',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'stockid\/(.+?)\.phtml',
                    't': 'url_re'
                },{
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="tbtb01"]/h1/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './/comment()[contains(string(),"公告日期")]',
                    't': 'xpath_re',
                    're':'(\d{4}-\d{2}-\d{2})'
                },
                {
                    'n': '增发类型',
                    'En': 'AdditionalType',
                    'v':
                    './/td[strong[contains(text(),"增发类型")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '发行价格',
                    'En': 'IssuePrice',
                    'v':
                    './/td[strong[contains(text(),"发行价格")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '货币名称',
                    'En': 'CurrencyEname',
                    'v':
                    './/td[strong[contains(text(),"货币名称")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '募集资金合计',
                    'En': 'CollectionOfFunds',
                    'v':
                    './/td[strong[contains(text(),"募集资金合计")]]/following-sibling::*[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行费用',
                    'En': 'DistributionCost',
                    'v':
                    './/td[strong[contains(text(),"发行费用")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行数量',
                    'En': 'IssueNumber',
                    'v':
                    './/td[strong[starts-with(text(),"发行数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上网发行数量',
                    'En': 'OnlineIssueNumber',
                    'v':
                    './/td[strong[contains(text(),"上网发行数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '向老股东配售数量',
                    'En': 'DistributionToOld',
                    'v':
                    './/td[strong[contains(text(),"向老股东配售数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '向其他公众投资者配售数量',
                    'En': 'DistributionToOhther',
                    'v':
                    './/td[strong[contains(text(),"向其他公众投资者配售数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '网下发行数量',
                    'En': 'DistributionToUnderLine',
                    'v':
                    './/td[strong[contains(text(),"网下发行数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '老股东配售有效申购数量',
                    'En': 'NumberOfEffectiveOld',
                    'v':
                    './/td[strong[contains(text(),"老股东配售有效申购数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '其他公众投资者有效申购户数',
                    'En': 'SubscriptionsOfEffectivePublic',
                    'v':
                    './/td[strong[contains(text(),"其他公众投资者有效申购户数")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '其他公众投资者有效申购数量',
                    'En': 'NumberOfEffectivePublic',
                    'v':
                    './/td[strong[contains(text(),"其他公众投资者有效申购数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '网下发行有效申购户数',
                    'En': 'SubscriptionsOfEffectiveUnderLine',
                    'v':
                    './/td[strong[contains(text(),"网下发行有效申购户数")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '网下机构投资者有效申购数量',
                    'En': 'NumberOfEffectiveUnderLine',
                    'v':
                    './/td[strong[contains(text(),"网下机构投资者有效申购数量")]]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_bank_finance(self, response):
        # 银行理财
        # 理财产品
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'id',
                                                   },
                                           callback=self.sina_bank_finance_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://money.finance.sina.com.cn/bank/mall/financingDetail.php?id=' + page,
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'abs',
                        'v': '4760'
                        },
                callback=self.sina_bank_finance,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://money.finance.sina.com.cn/bank/api/json_v2.php/Bank_FinanceService.searchFinaceProd?page=%s&num=20' % page,
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sina_bank_finance_info(self,response):
        # 增发新股信息提取    不定序
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="comp_tb prd_tb"]',    
                't': 'xpath',
                'db': 'CreditDataBase.SinaBankFinance',
                'keys': ['HTML_ID', 'FinancialProductName'],
                'check': 'FinancialProductName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'id=(.+)',
                    't': 'url_re'
                },{
                    'n': '产品名称',
                    'En': 'FinancialProductName',
                    'v':
                    './/*[contains(text(),"产品名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '所属银行',
                    'En': 'AffiliatedBank',
                    'v':
                    './/*[contains(text(),"所属银行")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '投资币种',
                    'En': 'InvestmentCurrency',
                    'v':
                    './/*[contains(text(),"投资币种")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '投资起始金额(元)',
                    'En': 'InitialAmountOfInvestment',
                    'v':
                    './/*[contains(text(),"投资起始金额(元)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '增加购买起始金额(元)',
                    'En': 'IncreaseInitialAmountOfInvestment',
                    'v':
                    './/*[contains(text(),"增加购买起始金额(元)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发售时间',
                    'En': 'SaleStartTime',
                    'v':
                    './/*[contains(text(),"发售时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '停售时间',
                    'En': 'SaleEndTime',
                    'v':
                    './/*[contains(text(),"停售时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '投资天数(天)',
                    'En': 'IssueNumber',
                    'v':
                    './/*[contains(text(),"投资天数(天)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '计息起始日',
                    'En': 'NumberOfInvestmentDays',
                    'v':
                    './/*[contains(text(),"计息起始日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '预期收益(%)',
                    'En': 'ExpectedYield',
                    'v':
                    './/*[contains(text(),"预期收益(%)")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '是否保本',
                    'En': 'CapitalPreservation',
                    'v':
                    './/*[contains(text(),"是否保本")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '产品规模',
                    'En': 'ProductScale',
                    'v':
                    './/*[contains(text(),"产品规模")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '到期收益',
                    'En': 'MaturityReturn',
                    'v':
                    './/*[contains(text(),"到期收益")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '同期存款利率差额（10万元）',
                    'En': 'InterestRateDifference',
                    'v':
                    './/*[contains(text(),"同期存款利率差额（10万元）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '预期实际收益计算（10万元）',
                    'En': 'RealIncome',
                    'v':
                    './/*[contains(text(),"预期实际收益计算（10万元）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '投资范围',
                    'En': 'ScopeOfInvestment',
                    'v':
                    './/*[contains(text(),"投资范围")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sina_Capital(self, response):
        JS = execjs.eval(response.text)
        # 0.沪深股市
        stock_key = JS[1][0]
        # 1.创业板
        cyb_key = JS[0][1]
        # 2.基金
        funds_key = JS[0][2]
        # 3.香港股市 
        HK_stock_key = JS[0][3]
        # 4.债券
        bouns_key = JS[1][4]
        # 5.美国股市
        # 6.外汇
        # 7.期货
        # 8.黄金
        # 9.环球股指
        # 10.板块汇总行情
        for key_list in bouns_key[1]:
            key = key_list[2]
            url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeStockCount?node=%s' % key
            yield scrapy.Request(url,
                headers=self.default_header,
                callback=self.sina_bonds_page_count)

    @SpiderHelp.check_response
    def sina_bonds_page_count(self, response):
        totalpage = math.ceil(int(re.compile('\"(\d+)\"').search(response.text).group(1)) / 40)
        symbol = re.compile('node=(.+)').search(response.url).group(1)
        formatter = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple?page={}&num=40&sort=symbol&asc=1&node=%s&_s_r_a=page' % symbol
        url = formatter.format(1)
        yield _Request(url,
            callback=self.sina_bonds_list,
            headers=self.default_header,
            meta={'page':1,'totalpage': totalpage,'formatter': formatter},
            priority=10000,
            redis_flag=True,
            redis_conn=self.r)

    @SpiderHelp.check_response
    def sina_bonds_list(self, response):
        # 新浪债券列表
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'symbol',
                                                   },
                                           callback=self.sina_bonds_jump,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://money.finance.sina.com.cn/bond/quotes/%s.html' % page,
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'abs',
                        'v': '4760'
                        },
                callback=self.sina_bonds_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

    def sina_bonds_jump(self, response):
        # 基本资料
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[text()="基本资料"]/@href',
                                                   },
                                           callback=self.sina_bonds_basic,
                                           headers=self.default_header,
                                           priority=2000,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req
        # # 发行信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[text()="发行信息"]/@href',
                                                   },
                                           callback=self.sina_bonds_issue,
                                           headers=self.default_header,
                                           priority=2000,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 发行人信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[text()="发行人信息"]/@href',
                                                   },
                                           callback=self.sina_bonds_issuer,
                                           headers=self.default_header,
                                           priority=2000,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 转股条款
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[text()="转股条款"]/@href',
                                                   },
                                           callback=self.sina_bonds_transfer_clause,
                                           headers=self.default_header,
                                           priority=2000,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 利率变动
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[text()="利率变动"]/@href',
                                                   },
                                           callback=self.sina_bonds_interest_rate_change,
                                           headers=self.default_header,
                                           priority=2000,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 转债行权
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[text()="转债行权"]/@href',
                                                   },
                                           callback=self.sina_bonds_transfer_of_debt,
                                           headers=self.default_header,
                                           priority=2000,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

    @SpiderHelp.check_response
    def sina_bonds_basic(self, response):
        # 债券基本信息提取    不定序
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[div[text()="基本资料"]]/table',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsBasic',
                'keys': ['BondsCode','BondsName'],
                'check': 'BondsName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'info\/(.+?)\.html',
                    't': 'url_re'
                },{
                    'n': '债券名称',
                    'En': 'BondsName',
                    'v':
                    './/*[contains(text(),"债券名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '债券简称',
                    'En': 'BondsShortName',
                    'v':
                    './/*[contains(text(),"债券简称")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '债券代码',
                    'En': 'BondsCode',
                    'v':
                    './/*[contains(text(),"债券代码")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '债券类型',
                    'En': 'BondsType',
                    'v':
                    './/*[contains(text(),"债券类型")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '债券面值（元）',
                    'En': 'BondsFacevalue',
                    'v':
                    './/*[contains(text(),"债券面值（元）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '债券年限（年）',
                    'En': 'BondAgeLimit',
                    'v':
                    './/*[contains(text(),"债券年限（年）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '票面利率（%）',
                    'En': 'ParInterestRate',
                    'v':
                    './/*[contains(text(),"票面利率（%）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '到期日',
                    'En': 'DueDate',
                    'v':
                    './/*[contains(text(),"到期日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '兑付日',
                    'En': 'HonourDate',
                    'v':
                    './/*[contains(text(),"兑付日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '摘牌日',
                    'En': 'DelistingDate',
                    'v':
                    './/*[contains(text(),"摘牌日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '计息方式',
                    'En': 'InterestRate',
                    'v':
                    './/*[contains(text(),"计息方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '利率说明',
                    'En': 'InterestRateDescription',
                    'v':
                    './/*[contains(text(),"利率说明")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '付息方式',
                    'En': 'ModeOfInterestPayment',
                    'v':
                    './/*[contains(text(),"付息方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '起息日期',
                    'En': 'DateOfInterestStart',
                    'v':
                    './/*[contains(text(),"起息日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '止息日期',
                    'En': 'DateOfInterestEnd',
                    'v':
                    './/*[contains(text(),"止息日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '付息日期',
                    'En': 'DateOfInterestPayment',
                    'v':
                    './/*[contains(text(),"付息日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '年付息次数',
                    'En': 'InterestPaymentTimesPerYear',
                    'v':
                    './/*[contains(text(),"年付息次数")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行价格（元）',
                    'En': 'IssuePrice',
                    'v':
                    './/*[contains(text(),"发行价格（元）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行规模（亿元）',
                    'En': 'Issuescale',
                    'v':
                    './/*[contains(text(),"发行规模（亿元）")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行日期',
                    'En': 'DateOfIssue',
                    'v':
                    './/*[contains(text(),"发行日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市日期',
                    'En': 'DateOfListing',
                    'v':
                    './/*[contains(text(),"上市日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市场所',
                    'En': 'Exchange',
                    'v':
                    './/*[contains(text(),"上市场所")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '信用等级',
                    'En': 'CredictLevel',
                    'v':
                    './/*[contains(text(),"信用等级")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '内部信用增级方式',
                    'En': 'InternalCreditEnhancement',
                    'v':
                    './/*[contains(text(),"内部信用增级方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '外部信用增级方式',
                    'En': 'ExternalCreditEnhancement',
                    'v':
                    './/*[contains(text(),"外部信用增级方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item


    @SpiderHelp.check_response
    def sina_bonds_issue(self, response):
        # 债券发行信息提取    不定序
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[div[text()="发行基本情况"]]/table',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsIssue',
                'keys': ['BondsShortName','HTML_ID'],
                'check': 'BondsShortName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'issue\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '债券简称',
                    'En': 'BondsShortName',
                    'v':
                    './/*[contains(text(),"债券简称及代码")]/following-sibling::td[1]/a[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '债券代码',
                    'En': 'BondsCode',
                    'v':
                    './/*[contains(text(),"债券简称及代码")]/following-sibling::td[1]/a[2]/text()',
                    't': 'xpath_first',
                },{
                    'n': '票面利率/发行参考利率（%）',
                    'En': 'ParInterestRate',
                    'v':
                    './/*[contains(text(),"票面利率")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '债券面值（元）',
                    'En': 'BondsFacevalue',
                    'v':
                    './/*[contains(text(),"债券面值")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '是否公开发行',
                    'En': 'PubliclyIssued',
                    'v':
                    './/*[contains(text(),"是否公开发行")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行价格（元）',
                    'En': 'IssuePrice',
                    'v':
                    './/*[contains(text(),"发行价格")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './/*[contains(text(),"公告日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '招标日期',
                    'En': 'DateOfBidding',
                    'v':
                    './/*[contains(text(),"招标日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '招标方式',
                    'En': 'BiddingMethod',
                    'v':
                    './/*[contains(text(),"招标方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '招标标的',
                    'En': 'BiddingTarget',
                    'v':
                    './/*[contains(text(),"招标标的")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '招标上线（元）',
                    'En': 'UpLineOfTender ',
                    'v':
                    './/*[contains(text(),"招标上线")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '招标下线（元）',
                    'En': 'DownLineOfTender',
                    'v':
                    './/*[contains(text(),"招标下线")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行起始日',
                    'En': 'IssueStartDate',
                    'v':
                    './/*[contains(text(),"发行起始日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行终止日',
                    'En': 'IssueEndDate',
                    'v':
                    './/*[contains(text(),"发行终止日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行方式',
                    'En': 'IssueMethod',
                    'v':
                    './/*[contains(text(),"发行方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '缴款日期',
                    'En': 'DateOfPayment',
                    'v':
                    './/*[contains(text(),"缴款日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '本次实际发行规模（亿元）',
                    'En': 'ActualIssueScale',
                    'v':
                    './/*[contains(text(),"本次实际发行规模")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '网上实际发行规模（亿元）',
                    'En': 'ActualscaleOnline',
                    'v':
                    './/following::td[contains(text(),"网上实际发行规模")][last()-1]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '本次计划发行规模（亿元）',
                    'En': 'ScaleOfPlanissue',
                    'v':
                    './/*[contains(text(),"本次计划发行规模")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '网上实际发行规模（亿元）',
                    'En': 'ActualscaleOnline2',
                    'v':
                    './/following::td[contains(text(),"网上实际发行规模")][last()]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '累计发行规模（亿元）',
                    'En': 'CumulativeIssueScale',
                    'v':
                    './/*[contains(text(),"累计发行规模")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最低申购金额（千元）',
                    'En': 'MinimumPurchaseAmount',
                    'v':
                    './/*[contains(text(),"最低申购金额")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行费用（百万元）',
                    'En': 'DistributionCost',
                    'v':
                    './/*[contains(text(),"发行费用")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发行对象',
                    'En': 'IssueObject',
                    'v':
                    './/*[contains(text(),"发行对象")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '主承销商',
                    'En': 'MainUnderwriter',
                    'v':
                    './/*[text()="主承销商"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '副主承销商',
                    'En': 'VicePrincipalUnderwriter',
                    'v':
                    './/*[text()="副主承销商"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '承销方式',
                    'En': 'UnderwriteManner',
                    'v':
                    './/*[contains(text(),"承销方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 


    @SpiderHelp.check_response
    def sina_bonds_issuer(self, response):
        # 债券发行人信息提取    不定序
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[div[contains(text(),"基本情况")]]/table',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsIssuer',
                'keys': ['HTML_ID','CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'issuer\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v':
                    './/*[contains(text(),"公司名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    './/*[contains(text(),"公司简称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '英文名称',
                    'En': 'ComEnglishName',
                    'v':
                    './/*[contains(text(),"英文名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '英文简称',
                    'En': 'ComEshortName',
                    'v':
                    './/*[contains(text(),"英文简称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法人代表',
                    'En': 'NameOfLegalRepresentative',
                    'v':
                    './/*[contains(text(),"法人代表")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '总经理',
                    'En': 'GeneralManager',
                    'v':
                    './/*[contains(text(),"总经理")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v':
                    './/*[contains(text(),"注册地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '办公邮编',
                    'En': 'ZipCode',
                    'v':
                    './/*[contains(text(),"办公邮编")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '办公地址',
                    'En': 'OfficeAddress',
                    'v':
                    './/*[contains(text(),"办公地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司电话',
                    'En': 'OfficePhoneNumber',
                    'v':
                    './/*[contains(text(),"公司电话")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司传真',
                    'En': 'OfficeFaxNumber',
                    'v':
                    './/*[contains(text(),"公司传真")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司电子邮箱',
                    'En': 'OfficeEmailAddress',
                    'v':
                    './/*[contains(text(),"公司电子邮箱")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司网址',
                    'En': 'OfficeWebsite',
                    'v':
                    './/*[contains(text(),"公司网址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v':
                    './/*[contains(text(),"成立日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资本（千万）',
                    'En': 'RegisteredCapital',
                    'v':
                    './/*[contains(text(),"注册资本")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市日期',
                    'En': 'DateOfListing',
                    'v':
                    './/*[contains(text(),"上市日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v':
                    './/*[contains(text(),"经营范围")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '主营业务',
                    'En': 'MainBusiness',
                    'v':
                    './/following::td[contains(text(),"主营业务")][last()-1]',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item  


    @SpiderHelp.check_response
    def sina_bonds_transfer_clause(self, response):
        # 债券转股条款信息提取    不定序
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[div[contains(text(),"转股条款")]]/table',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsTransferClause',
                'keys': ['HTML_ID','TransitionStartDate'],
                'check': 'TransitionStartDate',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'convertItem\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '转换起始日',
                    'En': 'TransitionStartDate',
                    'v':
                    './/*[contains(text(),"转换起始日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '初始转换比例（股/百元）',
                    'En': 'InitialTransitionRatio',
                    'v':
                    './/*[contains(text(),"初始转换比例")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '最新转换比例（股/百元）',
                    'En': 'NewestConversionRatio',
                    'v':
                    './/*[contains(text(),"最新转换比例")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '转换结束日',
                    'En': 'TransitionEndDate',
                    'v':
                    './/*[contains(text(),"转换结束日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '初始转换价格（元）',
                    'En': 'InitialTransitionPrice',
                    'v':
                    './/*[contains(text(),"初始转换价格")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最新转换价格（元）',
                    'En': 'NewestTransitionPrice',
                    'v':
                    './/*[contains(text(),"最新转换价格")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '换股价格调整标准',
                    'En': 'StandardOfTransitionPriceAdjustment',
                    'v':
                    './/*[contains(text(),"换股价格调整标准")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '转股价格确定标准',
                    'En': 'StandardOfTransitionPriceDetermining',
                    'v':
                    './/*[contains(text(),"转股价格确定标准")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '赎回条款',
                    'En': 'RedemptionClause',
                    'v':
                    './/*[contains(text(),"赎回条款")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '回售条款',
                    'En': 'ResaleClause',
                    'v':
                    './/*[contains(text(),"回售条款")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '强制性转股条款',
                    'En': 'MandatoryClause ',
                    'v':
                    './/*[contains(text(),"强制性转股条款")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '转换余股处理',
                    'En': 'ConversionOfSurplusStockTreatment',
                    'v':
                    './/*[contains(text(),"转换余股处理")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '转股价格修正',
                    'En': 'TransferPriceCorrection',
                    'v':
                    './/*[contains(text(),"转股价格修正")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },{
                    'n': '特别向下修正条款',
                    'En': 'SpecialDownwardClause',
                    'v':
                    './/*[contains(text(),"特别向下修正条款")]/following-sibling::td[1]/p/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 


    @SpiderHelp.check_response
    def sina_bonds_interest_rate_change(self, response):
        # 债券利率变动
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[div[contains(text(),"债券利率变动")]]/table//tr[position()>1]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsInterestRateChange',
                'keys': ['HTML_ID', 'InterestRateStartDate'],
                'check': 'InterestRateStartDate',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'rateChange\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '起息日期',
                    'En': 'InterestRateStartDate',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '止息日期',
                    'En': 'InterestRateEndDate',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first',
                },{
                    'n': '适用利率（%）',
                    'En': 'ApplicableInterestRate',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '利率变更原因',
                    'En': 'CauseOfInterestRatioChange',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '基本利差',
                    'En': 'BasicMargin',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '基准利率',
                    'En': 'BenchmarkInterestRate',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 


    @SpiderHelp.check_response
    def sina_bonds_transfer_of_debt(self, response):
        # 可转债行权
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[contains(text(),"可转债行权")]/following-sibling::table[1]//tr[position()>1]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsConvertibleBondRight',
                'keys': ['HTML_ID', 'DateOfAnnouncement'],
                'check': 'DateOfAnnouncement',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'conversion\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '行权类型',
                    'En': 'RightType',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first',
                },{
                    'n': '截止日期',
                    'En': 'ClosingDate',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '转股价格（元）',
                    'En': 'ConversionStocksPrice',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '本期转股数（万股）',
                    'En': 'NumbersOfThisPeriodConversionStocks',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '累计转股数（万股）',
                    'En': 'TotalNumbersOfConversionStocks',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '累计转股金额（万元）',
                    'En': 'TotalConversionStocksAmount',
                    'v':
                    './td[8]/text()',
                    't': 'xpath_first'
                },{
                    'n': '债券流通金额（万元）',
                    'En': 'BondCirculationAmount',
                    'v':
                    './td[9]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

        # 转股价变动
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[contains(text(),"转股价变动")]/following-sibling::table[1]//tr[position()>1]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_ConversionStocksPriceChange',
                'keys': ['HTML_ID', 'DateOfAnnouncement'],
                'check': 'DateOfAnnouncement',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'conversion\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '价格变动类型',
                    'En': 'PriceChangeType',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first',
                },{
                    'n': '转股价格生效日期',
                    'En': 'EffectiveDateOfConversionStocksPrice',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '执行日期',
                    'En': 'ExecutionDate',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '转股价格（元）',
                    'En': 'ConversionStocksPrice',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '转股比例（%）',
                    'En': 'RatioOfConversionStocks',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

        # 回售赎回结果
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[contains(text(),"回售赎回结果")]/following-sibling::table[1]//tr[position()>1]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_BondsRecoveryRedemptionResults',
                'keys': ['HTML_ID', 'DateOfAnnouncement'],
                'check': 'DateOfAnnouncement',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'conversion\/(.+?)\.html',
                    't': 'url_re'
                },
                {
                    'n': '事件类型',
                    'En': 'EventType',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '公告日期',
                    'En': 'DateOfAnnouncement',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first',
                },{
                    'n': '赎回金额（万元）',
                    'En': 'RedemptionAmount',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '赎回价格（元/张）',
                    'En': 'RedemptionPrice',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },{
                    'n': '回收金额（万元）',
                    'En': 'RecoveryAmount',
                    'v':
                    './td[6]/text()',
                    't': 'xpath_first'
                },{
                    'n': '回收价格（元/张）',
                    'En': 'RecoveryPrice',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },{
                    'n': '债券类型（万元）',
                    'En': 'BondsType',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

    @SpiderHelp.check_response
    def cyzone_start(self, response):
        yield self.request('http://wwv.cyzone.cn/vcompany/list-0-0-1-0-0/',
            redis_flag=True,
            meta={'formatter':'http://wwv.cyzone.cn/vcompany/list-0-0-{}-0-0/','proxys':True},
            callback=self.cyzone_vcompany
            )
        yield self.request('http://wwv.cyzone.cn/company/list-0-1-4/',
            redis_flag=True,
            meta={'formatter':'http://wwv.cyzone.cn/company/list-0-{}-4/','proxys':True},
            callback=self.cyzone_company
            )
        yield self.request('http://wwv.cyzone.cn/people/list-0-1-0-0/',
            redis_flag=True,
            meta={'formatter':'http://wwv.cyzone.cn/people/list-0-{}-0-0/','proxys':True},
            callback=self.cyzone_people
            )
        yield self.request('http://wwv.cyzone.cn/event/list-764-0-1-0-0-0-0/',
            redis_flag=True,
            meta={'formatter':'http://wwv.cyzone.cn/event/list-764-0-{}-0-0-0-0/','proxys':True},
            callback=self.cyzone_event
            )
        yield self.request('http://wwv.cyzone.cn/vpeople/list-0-1/',
            redis_flag=True,
            meta={'formatter':'http://wwv.cyzone.cn/vpeople/list-0-{}/','proxys':True},
            callback=self.cyzone_vpeople
            )

    @SpiderHelp.check_response
    def cyzone_vcompany(self, response):
        # 创业邦-创业公司
        # #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[@id="lastpage"]/preceding-sibling::a[1]/text()'
                        },
                callback=self.cyzone_vcompany,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                divmod=1,
                redis_conn=self.r,
                meta={'proxys':True},
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # 列表页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[span[@class="tit"]]/@href',
                                                   },
                                           callback=self.cyzone_vcompany_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           meta={'proxys':True},
                                           response_type='xpath')
        for req in reqs2:
            yield req

    @SpiderHelp.check_response
    def cyzone_vcompany_info(self, response):
        # 创业公司
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Cyzone_StartupsCompany',
                'keys': ['HTML_ID','StartsComShortName'],
                'check': 'StartsComShortName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'r\/(.+)\.html',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'StartsComShortName',
                    'v':
                    '//li[h1 and @class="name"]/h1/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司全称',
                    'En': 'StartsComName',
                    'v':
                    '//li[contains(text(),"公司全称")]/text()',
                    't': 'xpath_re',
                    're':'公司全称[:：](.+)'
                },{
                    'n': '公司官网',
                    'En': 'OfficeWebsite',
                    'v':
                    '//div[@class="com-url"]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立时间1',
                    'En': 'SetupTime1',
                    'v':
                    '//li[i[@class="i1"]]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '所属地区',
                    'En': 'AreaName',
                    'v':
                    '//li[i[@class="i2"]]/span/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '融资轮次',
                    'En': 'Turns',
                    'v':
                    '//li[i[@class="i3"]]/span/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '行业标签',
                    'En': 'Industry',
                    'v':
                    '//li[i[@class="i6"]]/span/a/text()',
                    't': 'xpath_join,'
                },{
                    'n': '公司简介',
                    'En': 'CompanyProfile',
                    'v':
                    '//h3[contains(text(),"简介")]/following-sibling::div[1]/p/text()',
                    't': 'xpath_join,'
                },{
                    'n': '注册号',
                    'En': 'RegistrationNumber',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"注册号")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营状态',
                    'En': 'OperatingState',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"注册号")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表',
                    'En': 'NameOfLegalRepresentative',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"法定代表")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '股东',
                    'En': 'Shareholder',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"股东")]]/span[2]/text()',
                    't': 'xpath_join,'
                },{
                    'n': '公司类型',
                    'En': 'CompanyType',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"公司类型")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"成立日期")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资本',
                    'En': 'RegisteredCapital',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"注册资本")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '住所',
                    'En': 'OfficeAddress',
                    'v':
                    '//div[@class="qcc"]/p[span[contains(text(),"住所")]]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

    @SpiderHelp.check_response
    def cyzone_company(self, response):
        # 创业邦-投资公司
        # '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[@id="lastpage"]/preceding-sibling::a[1]/text()'
                        },
                callback=self.cyzone_company,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                meta={'proxys':True},
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # # 列表页 -投资公司信息
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//td[@class="table-company2-tit"]/a/@href',
                                                   },
                                           callback=self.cyzone_company_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           meta={'proxys':True},
                                           response_type='xpath')
        for req in reqs2:
            yield req

        # # 列表页 -投资公司投资事件 
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//td[@class="table-company2-tit"]/a/@href',
                                                   're': '\/([^\/]+)\.html'
                                                   },
                                           callback=self.cyzone_company_investment_events,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://wwv.cyzone.cn/company/case-%s-0-0-1/' % page,
                                           errback=self.errbackparse,
                                           meta={'proxys':True,},
                                           response_type='xpath')
        for req in reqs2:
            yield req
            return

    @SpiderHelp.check_response
    def cyzone_company_investment_events(self, response):
        # 投资公司投资事件提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//tr[@class="table-plate3"]',    
                't': 'xpath',
                'db': 'CreditDataBase.Cyzone_InvestmentCompanyEvents',
                'keys': ['HTML_ID', 'ObtainInvestmentComShortName','ObtainInvestmentTime'],
                'check': 'ObtainInvestmentComShortName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'case-(\d+)-',
                    't': 'url_re'
                },
                {
                    'n': '投资公司',
                    'En': 'ComShortName',
                    'v':
                    '//li[@class="organize"]//h2/text()',
                    't': 'xpath_first'
                },{
                    'n': '投资公司ID',
                    'En': 'InvestmentCompanyID',
                    'v':
                    '//li[@class="organize"]/a[1]/@href',
                    't': 'xpath_re',
                    're': 'd\/(.+)\.html'
                },{
                    'n': '获投公司',
                    'En': 'ObtainInvestmentComShortName',
                    'v':
                    './/span[@class="tp2_tit"]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '获投公司ID',
                    'En': 'ObtainInvestmentComID',
                    'v':
                    './/span[@class="tp2_tit"]/a/@href',
                    't': 'xpath_re',
                    're': 'r\/(.+)\.html'
                },{
                    'n': '金额',
                    'En': 'Amount',
                    'v':
                    './/div[@class="money"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '轮次',
                    'En': 'Turns',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '投资方',
                    'En': 'InvestmentCompanys',
                    'v':
                    './td[5]/@title',
                    't': 'xpath_first'
                },{
                    'n': '获投时间',
                    'En': 'ObtainInvestmentTime',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first'
                },
                
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

        # '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[@id="lastpage"]/preceding-sibling::a[1]/text()'
                        },
                callback=self.cyzone_company_investment_events,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://wwv.cyzone.cn/company/case-{}-0-0-{}/'.format(re.compile('case-(\d+)-').search(response.url).group(1),page),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                meta={'proxys':True},
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cyzone_company_info(self, response):
        # 投资公司提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.CyZONE_InvestmentCompany',
                'keys': ['HTML_ID', 'ComShortName'],
                'check': 'ComShortName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'd\/(.+)\.html',
                    't': 'url_re'
                },
                {
                    'n': '公司简称',
                    'En': 'ComShortName',
                    'v':
                    '//li[h1 and @class="organize"]/h1/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '成立时间',
                    'En': 'SetupTime',
                    'v':
                    '//li[contains(text(),"成立时间")]/text()',
                    't': 'xpath_re',
                    're':'成立时间[:：](.+)'
                },{
                    'n': '投资偏好',
                    'En': 'Preference',
                    'v':
                    '//li[contains(text(),"投资偏好")]/text()',
                    't': 'xpath_re',
                    're':'投资偏好[:：](.+)'
                },{
                    'n': '机构官网',
                    'En': 'OfficialWebsite',
                    'v':
                    '//li[contains(text(),"机构官网")]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '简介',
                    'En': 'Introduction',
                    'v':
                    '//div[h2[text()="简介"]]/div[1]//p//text()',
                    't': 'xpath_join'
                },{
                    'n': '投资团队人数',
                    'En': 'NumbersOfTeam',
                    'v':
                    'count(//div[h2[text()="投资团队"]]//li)',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

    @SpiderHelp.check_response
    def cyzone_people(self, response):
        # 创业邦-投资人
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[@id="lastpage"]/preceding-sibling::a[1]/text()'
                        },
                callback=self.cyzone_people,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                divmod=1,
                redis_conn=self.r,
                meta={'proxys':True},
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # # 列表页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//td[contains(@class,"people-name")]/a[1]/@href',
                                                   },
                                           callback=self.cyzone_people_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           meta={'proxys':True},
                                           response_type='xpath')
        for req in reqs2:
            yield req

    @SpiderHelp.check_response
    def cyzone_people_info(self, response):
        # 投资人提取
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Cyzone_Investor',
                'keys': ['HTML_ID', 'Name'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'f\/(.+)\.html',
                    't': 'url_re'
                },
                {
                    'n': '姓名',
                    'En': 'Name',
                    'v':
                    '//li[@class="name" and h1]/h1/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '职务',
                    'En': 'Position',
                    'v':
                    '//li[@class="name" and h1]/following-sibling::li[last()]',
                    't': 'xpath_first'
                },{
                    'n': '所在机构',
                    'En': 'Institution',
                    'v':
                    '//div[@class="project-info"]/p[@class="name organize-name"]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构ID',
                    'En': 'InstitutionID',
                    'v':
                    '//div[@class="project-info"]/p[@class="name organize-name"]/a/@href',
                    't': 'xpath_re',
                    're': 'd\/(.+)\.html'
                },
                {
                    'n': '关注领域',
                    'En': 'AreasOfConcern',
                    'v':
                    '//span[contains(text(),"关注领域")]/following-sibling::span/text()',
                    't': 'xpath_join,',
                },{
                    'n': '投资阶段',
                    'En': 'InvestmentStage',
                    'v':
                    '//span[contains(text(),"投资阶段")]/following-sibling::span/text()',
                    't': 'xpath_first',
                },{
                    'n': '常驻城市',
                    'En': 'ResidentCity',
                    'v':
                    '//span[contains(text(),"常驻城市")]/following-sibling::span/text()',
                    't': 'xpath_first',
                },{
                    'n': '简介',
                    'En': 'Introduction',
                    'v':
                    '//div[h2[text()="简介"]]/h2/following-sibling::div[1]//p//text()',
                    't': 'xpath_join'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

        # 工作经历
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[h2[text()="工作经历"]]/div',    
                't': 'xpath',
                'db': 'CreditDataBase.Cyzone_InvestorWorkExperience',
                'keys': ['HTML_ID', 'Name','Position','ComName'],
                'check': 'ComName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'f\/(.+)\.html',
                    't': 'url_re'
                },
                {
                    'n': '姓名',
                    'En': 'Name',
                    'v':
                    '//li[@class="name" and h1]/h1/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司',
                    'En': 'ComName',
                    'v':
                    './/span[@class="com"]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '公司ID',
                    'En': 'ComNID',
                    'v':
                    './/span[@class="com"]/a/@href',
                    't': 'xpath_re',
                    're':'d\/(.+)\.html'
                },{
                    'n': '职务',
                    'En': 'Position',
                    'v':
                    './/span[@class="job"]/text()',
                    't': 'xpath_first',
                },{
                    'n': '时间',
                    'En': 'TimeInterval',
                    'v':
                    '//div[@class="time"]/text()',
                    't': 'xpath_first',
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

    @SpiderHelp.check_response
    def cyzone_vpeople(self, response):
        # 创业邦-创业者
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[@id="lastpage"]/preceding-sibling::a[1]/text()'
                        },
                callback=self.cyzone_vpeople,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                divmod=1,
                redis_conn=self.r,
                meta={'proxys':True},
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # # 列表页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//td[@class="people-name"]/a[1]/@href',
                                                   },
                                           callback=self.cyzone_vpeople_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs2:
            yield req

    @SpiderHelp.check_response
    def cyzone_vpeople_info(self, response):
        # 创业邦-创业者
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Cyzone_Entrepreneur',
                'keys': ['HTML_ID', 'Name'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    's\/(.+)\.html',
                    't': 'url_re'
                },
                {
                    'n': '姓名',
                    'En': 'Name',
                    'v':
                    '//li[@class="name"]/h1/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '所在公司',
                    'En': 'Com1',
                    'v':
                    '//li[@class="name"]/following-sibling::li[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '职务',
                    'En': 'Position',
                    'v':
                    '//li[@class="name"]/following-sibling::li[last()]/text()',
                    't': 'xpath_first',
                },{
                    'n': '简介',
                    'En': 'BriefIntroduction',
                    'v':
                    '//div[h2[text()="简介"]]/div[1]//p//text()',
                    't': 'xpath_join',
                },{
                    'n': '项目名称',
                    'En': 'ProjName',
                    'v':
                    '//div[@class="project-info"]/p[@class="name"]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '项目ID',
                    'En': 'ProjID',
                    'v':
                    '//div[@class="project-info"]/p[@class="name"]/a/@href',
                    't': 'xpath_re',
                    're': 'r\/(.+)\.html'
                },{
                    'n': '官网',
                    'En': 'OfficialWebsite',
                    'v':
                    '//div[@class="project-info"]/p[contains(text(),"公司官网")]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '轮次',
                    'En': 'Turns',
                    'v':
                    '//div[@class="project-info"]/p[contains(text(),"轮次")]/text()',
                    't': 'xpath_re',
                    're': '轮次[:：],{0,1}([\s\S]+?),?$'
                },{
                    'n': '行业',
                    'En': 'Industry',
                    'v':
                    '//div[@class="project-info"]/p[contains(text(),"行业")]/a/text()',
                    't': 'xpath_join,',
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item 

    @SpiderHelp.check_response
    def cyzone_event(self, response):
        # 创业邦-投资事件
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//a[@id="lastpage"]/preceding-sibling::a[1]/text()'
                        },
                callback=self.cyzone_event,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                meta={'proxys':True},
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

        # 投资事件
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="list-table3"]//tr[contains(@class,"table") and position()>1]',    
                't': 'xpath',
                'db': 'CreditDataBase.Cyzone_InvestmentEvents',
                'keys': ['HTML_ID'],
                'check': 'HTML_ID',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    './/a[text()="详情"]/@href',
                    't': 'xpath_re',
                    're': 'e\/(.+)\.html'
                },
                {
                    'n': '获投公司简称',
                    'En': 'ObtainInvestmentComShortName',
                    'v':
                    './/span[@class="tp2_tit"]/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '获投公司全称',
                    'En': 'ObtainInvestmentComName',
                    'v':
                    './/span[@class="tp2_com"]/text()',
                    't': 'xpath_first',
                },{
                    'n': '获投公司ID',
                    'En': 'ObtainInvestmentComID',
                    'v':
                    './/span[@class="tp2_tit"]/a/@href',
                    't': 'xpath_re',
                    're':'r\/(.+)\.html'
                },{
                    'n': '金额',
                    'En': 'Amount',
                    'v':
                    './td[3]/div[@class="money"]/text()',
                    't': 'xpath_first',
                },{
                    'n': '轮次',
                    'En': 'Turns',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first',
                },{
                    'n': '投资公司',
                    'En': 'InvestmentCompanys',
                    'v':
                    './td[5]/@title',
                    't': 'xpath_re',
                    're': ',([\s\S]+),'
                },{
                    'n': '行业',
                    'En': 'Industry',
                    'v':
                    './td[6]/a/text()',
                    't': 'xpath_first',
                },{
                    'n': '获投时间',
                    'En': 'ObtainInvestmentTime',
                    'v':
                    './td[7]/text()',
                    't': 'xpath_first',
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def parse(self, response):
        logger.info(response.text)
        pass

    @SpiderHelp.check_response
    def sina_futures(self, response):
        # 获取分类参数
        TotalUrl = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQFuturesCount?node=%s'
        nodes = re.compile("\['.+?', '(\w+?)', '\d+?'\]").findall(response.text)
        for node in nodes:
            url = TotalUrl % node
            yield _Request(
                url,
                redis_flag=True,
                redis_conn=self.r,
                callback=self.sina_futures_jumps)

    @SpiderHelp.check_response
    def sina_futures_jumps(self, response):
        # 页面跳转
        node = re.compile('node=(.+)').search(response.url).group(1)
        formater = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQFuturesData?page={}&num=5&sort=position&asc=0&node=%s&base=futures' % node
        match = re.compile('String\(\"(\d+)\"\)').search(response.text)
        url = formater.format(1)
        totalpage =  math.ceil(int(match.group(1)) / 5) if match else 1
        yield self.request(url,
            callback=self.sina_futures_list,
            priority=2000,
            meta={'formatter':formater,'totalpage':totalpage,'proxys':True},
            headers=self.default_header,
            redis_flag=True,
            redis_conn=self.r)

    @SpiderHelp.check_response
    def sina_futures_list(self, response):
        # 新浪 期货列表
        # logger.error(response)
        reqs = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'symbol',
                                                   },
                                           callback=self.sina_futures_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://finance.sina.com.cn/futures/quotes/%s.shtml' % page,
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'abs',
                        'v': '4760'
                        },
                callback=self.sina_futures_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='json')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sina_futures_info(self, response):
        # 新浪 期货信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="table-futures-basic-data"]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_FuturesBasic',
                'keys': ['Code'],
                'check': 'Code',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'quotes/(.+)\.shtml',
                    't': 'url_re'
                },{
                    'n': 'Code',
                    'En': 'Code',
                    'v':
                    '//span[@class="code"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '期货名称',
                    'En': 'FuritersName',
                    'v':
                    '//h1[@class="title"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '交易品种',
                    'En': 'ETradingVariety',
                    'v':
                    './/*[contains(text(),"交易品种")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '交易单位',
                    'En': 'TradingUnit',
                    'v':
                    './/*[contains(text(),"交易单位")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '报价单位',
                    'En': 'QuotationUnit',
                    'v':
                    './/*[contains(text(),"报价单位")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最小变动价位',
                    'En': 'MinimumPriceChange',
                    'v':
                    './/*[contains(text(),"最小变动价位")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '涨跌停板幅度',
                    'En': 'PriceLimits',
                    'v':
                    './/*[contains(text(),"涨跌停板幅度")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '合约交割月份',
                    'En': 'ContractMonth',
                    'v':
                    './/*[contains(text(),"合约交割月份")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易时间',
                    'En': 'TradingTime',
                    'v':
                    './/*[contains(text(),"交易时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最后交易日',
                    'En': 'LastTradingDate',
                    'v':
                    './/*[contains(text(),"最后交易日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最后交割日',
                    'En': 'FinalDeliveryDate',
                    'v':
                    './/*[contains(text(),"最后交割日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交割品级',
                    'En': 'DeliveryGrade',
                    'v':
                    './/*[contains(text(),"交割品级")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最低交易保证金',
                    'En': 'MinimumTransactionMargin',
                    'v':
                    './/*[contains(text(),"最低交易保证金")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易手续费',
                    'En': 'TransactionFee',
                    'v':
                    './/*[contains(text(),"交易手续费")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交割方式',
                    'En': 'DeliveryMethods',
                    'v':
                    './/*[contains(text(),"交割方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易代码',
                    'En': 'TransactionCode',
                    'v':
                    './/*[contains(text(),"交易代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市交易所',
                    'En': 'StockExchange',
                    'v':
                    './/*[contains(text(),"上市交易所")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def p2peye_list(self, response):
        # 新浪 期货列表
        # logger.error(response)
        reqs = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//li[@class="ui-result-item"]//a[@class="ui-result-pname"]/@href',
                                                   },
                                           callback=self.p2peye_company,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//div[@class="ui-total-num"]/strong/text()'
                        },
                callback=self.p2peye_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: 'http://www.p2peye.com/platform/all/p%s/' % page,
                redis_conn=self.r,
                redis_flag=True,
                readpage=16,
                response_type='xpath')
        for req in reqs:
            yield req

    def p2peye_company(self, response):
        # 新浪 期货信息提取
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@id="table-futures-basic-data"]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sina_FuturesBasic',
                'keys': ['Code'],
                'check': 'Code',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'quotes/(.+)\.shtml',
                    't': 'url_re'
                },{
                    'n': '平台名称',
                    'En': 'Code',
                    'v':
                    '//span[@class="code"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '状态标签',
                    'En': 'FuritersName',
                    'v':
                    '//div[@class="tags"]/*[1]/div[@class="tag_icon"]/following-sibling::text()',
                    't': 'xpath_first'
                },
                {
                    'n': '状态标签2',
                    'En': 'ETradingVariety',
                    'v':
                    '//div[@class="tags"]/*[2]//text()[last()]',
                    't': 'xpath_first',
                },
                {
                    'n': '交易单位',
                    'En': 'TradingUnit',
                    'v':
                    './/*[contains(text(),"交易单位")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '报价单位',
                    'En': 'QuotationUnit',
                    'v':
                    './/*[contains(text(),"报价单位")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最小变动价位',
                    'En': 'MinimumPriceChange',
                    'v':
                    './/*[contains(text(),"最小变动价位")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '涨跌停板幅度',
                    'En': 'PriceLimits',
                    'v':
                    './/*[contains(text(),"涨跌停板幅度")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '合约交割月份',
                    'En': 'ContractMonth',
                    'v':
                    './/*[contains(text(),"合约交割月份")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易时间',
                    'En': 'TradingTime',
                    'v':
                    './/*[contains(text(),"交易时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最后交易日',
                    'En': 'LastTradingDate',
                    'v':
                    './/*[contains(text(),"最后交易日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最后交割日',
                    'En': 'FinalDeliveryDate',
                    'v':
                    './/*[contains(text(),"最后交割日")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交割品级',
                    'En': 'DeliveryGrade',
                    'v':
                    './/*[contains(text(),"交割品级")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最低交易保证金',
                    'En': 'MinimumTransactionMargin',
                    'v':
                    './/*[contains(text(),"最低交易保证金")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易手续费',
                    'En': 'TransactionFee',
                    'v':
                    './/*[contains(text(),"交易手续费")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交割方式',
                    'En': 'DeliveryMethods',
                    'v':
                    './/*[contains(text(),"交割方式")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '交易代码',
                    'En': 'TransactionCode',
                    'v':
                    './/*[contains(text(),"交易代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '上市交易所',
                    'En': 'StockExchange',
                    'v':
                    './/*[contains(text(),"上市交易所")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def cbrc_jumps(self, response):
        # 机构持有列表
        limit = 100
        url = 'http://xukezheng.cbrc.gov.cn/ilicence/getLicence.do?useState=3'
        yield self.request(url,
            callback=self.cbrc_usestate3,
            priority=2000,
            method='POST',
            body=urllib.parse.urlencode({'start':'0','limit':'100'}),
            meta={'proxys':True},
            headers=self.default_header,
            redis_flag=True,
            redis_conn=self.r)
        # # 近期机构设立情况
        # url = 'http://xukezheng.cbrc.gov.cn/ilicence/getLicence.do?useState=1'
        # yield self.request(url,
        #     callback=self.cbrc_usestate1,
        #     priority=2000,
        #     method='POST',
        #     body=urllib.parse.urlencode({'start':'0','limit':'100'}),
        #     meta={'proxys':True},
        #     headers=self.default_header,
        #     redis_flag=True,
        #     redis_conn=self.r)
        # # 失控情况
        # url = 'http://xukezheng.cbrc.gov.cn/ilicence/getLicence.do?useState=9'
        # yield self.request(url,
        #     callback=self.cbrc_usestate9,
        #     priority=2000,
        #     method='POST',
        #     body=urllib.parse.urlencode({'start':'0','limit':'100'}),
        #     meta={'proxys':True},
        #     headers=self.default_header,
        #     redis_flag=True,
        #     redis_conn=self.r)
        # # 机构退出列表
        # url = 'http://xukezheng.cbrc.gov.cn/ilicence/getLicence.do?useState=7'
        # yield self.request(url,
        #     callback=self.cbrc_usestate7,
        #     priority=2000,
        #     method='POST',
        #     body=urllib.parse.urlencode({'start':'0','limit':'100'}),
        #     meta={'proxys':True},
        #     headers=self.default_header,
        #     redis_flag=True,
        #     redis_conn=self.r)

    @SpiderHelp.check_response
    def cbrc_usestate3(self, response):
        # 机构持有列表 金融许可
        reqs = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'root/flowNo',
                                                   },
                                           callback=self.cbrc_institution_info,
                                           headers=self.default_header,
                                           meta={'proxys':True},
                                           priority=1999,
                                           urlfunc=
                                           lambda page, response: 'http://xukezheng.cbrc.gov.cn/ilicence/showLicenceInfo.do?state=3&id=%s' % page,
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalProperty'
                        },
                callback=self.cbrc_usestate3,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://xukezheng.cbrc.gov.cn/ilicence/getLicence.do?useState=3',
                bodyfunc=lambda page,response=None:urllib.parse.urlencode({'start':str((page-1)*100),'limit':'100'}),
                redis_conn=self.r,
                meta={'proxys':True},
                divmod=100,
                redis_flag=True,
                readpage=16,
                response_type='json')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cbrc_institution_info(self, response):
        # cbrc 金融许可
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="trw-table-s1"]',    
                't': 'xpath',
                'db': 'CBRC.cbrc_institution',
                'keys': ['org_code','serial_number'],
                'check': 'org_code',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    '&id=(.+)',
                    't': 'url_re'
                },{
                    'n': '机构编码',
                    'En': 'org_code',
                    'v':
                    './/tr[position()<15 and @class="a0"]/td[contains(text(),"机构编码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构名称',
                    'En': 'org_name',
                    'v':
                    './/tr[position()<15 and @class="a0"]/td[contains(text(),"机构名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '机构简称',
                    'En': 'org_short_name',
                    'v':
                    './/tr[position()<15 and @class="a0"]/td[contains(text(),"机构简称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '机构地址',
                    'En': 'org_address',
                    'v':
                    './/tr[position()<15 and @class="a0"]/td[contains(text(),"机构地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },{
                    'n': '经度',
                    'En': 'longitude',
                    'v':
                    './/tr[position()<15 and @class="a0"]/td[contains(text(),"经度")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '纬度',
                    'En': 'latitude',
                    'v':
                    './/tr[position()<15 and @class="a0"]/td[contains(text(),"纬度")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构所在地',
                    'En': 'site_of_institution',
                    'v':
                    './/tr[position()<15 and @class="a0"]/td[contains(text(),"机构所在地")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '邮政编码',
                    'En': 'postal_code',
                    'v':
                    './/tr[position()<15 and @class="a0"]/td[contains(text(),"邮政编码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发证日期',
                    'En': 'date_of_issuing',
                    'v':
                    './/tr[position()<15 and @class="a0"]/td[contains(text(),"发证日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '批准成立日期',
                    'En': 'date_of_approval',
                    'v':
                    './/tr[position()<15 and @class="a0"]/td[contains(text(),"批准成立日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发证机关',
                    'En': 'certification_authority',
                    'v':
                    './/tr[position()<15 and @class="a0"]/td[contains(text(),"发证机关")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '流水号',
                    'En': 'serial_number',
                    'v':
                    './/tr[position()<15 and @class="a0"]/td[contains(text(),"流水号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="trw-table-s1"]',    
                't': 'xpath',
                'db': 'CBRC.cbrc_institution_change',
                'keys': ['serial_number','org_code'],
                'check': 'serial_number',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    '&id=(.+)',
                    't': 'url_re'
                },{
                    'n': '流水号',
                    'En': 'serial_number',
                    'v':
                    './/tr[position()>=15 and @class="a0"]/td[contains(text(),"流水号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构编码',
                    'En': 'org_code',
                    'v':
                    './/tr[position()>=15 and @class="a0"]/td[contains(text(),"机构编码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '机构名称',
                    'En': 'org_name',
                    'v':
                    './/tr[position()>=15 and @class="a0"]/td[contains(text(),"机构名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },
                {
                    'n': '机构地址',
                    'En': 'org_address',
                    'v':
                    './/tr[position()>=15 and @class="a0"]/td[contains(text(),"机构地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first',
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def chinawealth_jumps(self, response):
        url = 'https://www.chinawealth.com.cn/lccpAllProJzyServlet.go'
        for index in ['02', '03', '01', '04']:
            body = urllib.parse.urlencode({'tzzlxdm':index,
                        'cpdjbm':' ' ,
                        'cpmc':'',
                        'pagenum':'01',
                        'orderby':'',
                        'code':'',
                        'changeTableFlage':'0'})
            yield self.request(
                        url,
                        method='POST',
                        body=body,
                        meta={'index': index},
                        redis_flag=REDISFLAG,
                        callback=self.chinawealth_list)

    @SpiderHelp.check_response
    def chinawealth_list(self, response):
        # 中国理财网

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'Count'
                        },
                callback=self.chinawealth_list,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: 'https://www.chinawealth.com.cn/lccpAllProJzyServlet.go',
                bodyfunc=self.get_lxdm,
                redis_conn=self.r,
                divmod=500,
                redis_flag=True,
                readpage=128,
                response_type='json')
        for req in reqs:
            yield req

        reqs = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'List/cpid',
                                                   },
                                           callback=self.chinawealth_sales_area,
                                           headers=self.default_header,
                                           method='POST',
                                           priority=1999,
                                           urlfunc=
                                           lambda page, response: 'https://www.chinawealth.com.cn/cpxsqyQuery.go',
                                           bodyfunc=self.get_xsqy,
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs:
            yield req

        _configs = [{
            'list': {
                'n': '',
                'v': 'List',    
                't': 'json',
                'db': 'Chinawealth.ChinawealthProd',
                'keys': ['InvestorType', 'ProdID'],
                'check': 'HTML_ID',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '产品登记编码',
                    'En': 'HTML_ID',
                    'v':
                    'cpdjbm',
                    't': 'json'
                },{
                    'n': '产品名称',
                    'En': 'ProdName',
                    'v':
                    'cpms',
                    't': 'json'
                },{
                    'n': '产品代码',
                    'En': 'ProdCode',
                    'v':
                    'cpdm',
                    't': 'json'
                },{
                    'n': '产品类型',
                    'En': 'ProdType',
                    'v':
                    'cplxms',
                    't': 'json'
                },{
                    'n': '投资者类型',
                    'En': 'InvestorType',
                    'v':
                    'tzzlxms',
                    't': 'json'
                },
                {
                    'n': '产品状态',
                    'En': 'ProductStatus',
                    'v':
                    'cpztms',
                    't': 'json'
                },
                {
                    'n': '产品运作模式',
                    'En': 'ProdOperationMode',
                    'v':
                    'cpyzmsms',
                    't': 'json'
                },
                {
                    'n': '起始销售金额',
                    'En': 'InitialSalesAmount',
                    'v':
                    'qdxsje',
                    't': 'json'
                },
                {
                    'n': '募集起始日期',
                    'En': 'RaiseStartDate',
                    'v':
                    'mjqsrq',
                    't': 'json'
                },
                {
                    'n': '产品起始日期',
                    'En': 'ProdStartDate',
                    'v':
                    'cpqsrq',
                    't': 'json'
                },
                {
                    'n': '初始净值',
                    'En': 'InitialNetValue',
                    'v':
                    'csjz',
                    't': 'json'
                },
                {
                    'n': '本期净值',
                    'En': 'ThisPeriodNetValue',
                    'v':
                    'bqjz',
                    't': 'json'
                },
                {
                    'n': '预期最低收益率%',
                    'En': 'ExpectedLowestYields',
                    'v':
                    'yjkhzdnsyl',
                    't': 'json'
                },
                {
                    'n': '产品期限',
                    'En': 'ProdTerm',
                    'v':
                    'cpqx',
                    't': 'json'
                },
                {
                    'n': '产品收益类型',
                    'En': 'ProdIncomeType',
                    'v':
                    'cpsylxms',
                    't': 'json'
                },
                {
                    'n': '募集币种',
                    'En': 'RaiseCurrcy',
                    'v':
                    'mjbz',
                    't': 'json'
                },
                {
                    'n': '风险等级',
                    'En': 'RiskGrade',
                    'v':
                    'fxdjms',
                    't': 'json'
                },
                {
                    'n': '募集结束日期',
                    'En': 'RaiseEndDate',
                    'v':
                    'mjjsrq',
                    't': 'json'
                },
                {
                    'n': '产品终止日期',
                    'En': 'ProdEndDate',
                    'v':
                    'cpyjzzrq',
                    't': 'json'
                },
                {
                    'n': '产品净值',
                    'En': 'ProdNetValue',
                    'v':
                    'cpjz',
                    't': 'json'
                },
                {
                    'n': '到期实际收益率',
                    'En': 'ActualYields',
                    'v':
                    'dqsjsyl',
                    't': 'json'
                },
                {
                    'n': '业务起始日',
                    'En': 'BusinessStartDate',
                    'v':
                    'kfzqqsr',
                    't': 'json'
                },
                {
                    'n': '业务结束日',
                    'En': 'BusinessEndDate',
                    'v':
                    'kfzqjsr',
                    't': 'json'
                },
                {
                    'n': '投资资产类型',
                    'En': 'TypeOfInvestmentAssets',
                    'v':
                    'tzlxms',
                    't': 'json'
                },
                {
                    'n': '预计最高收益率',
                    'En': 'ExpectedHigestYields',
                    'v':
                    'yjkhzgnsyl',
                    't': 'json'
                },
                {
                    'n': '发行机构名称',
                    'En': 'IssuerName',
                    'v':
                    'fxjgms',
                    't': 'json'
                },
                {
                    'n': '发行机构代码',
                    'En': 'IssuerCode',
                    'v':
                    'fxjgdm',
                    't': 'json'
                },
                {
                    'n': '产品id',
                    'En': 'ProdID',
                    'v':
                    'cpid',
                    't': 'json'
                },
                {
                    'n': 'qxms',
                    'En': 'Term',
                    'v':
                    'qxms',
                    't': 'json'
                },

            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def chinawealth_sales_area(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'json',
                'db': 'Chinawealth.ChinawealthSalesArea',
                'keys': ['HTML_ID'],
                'check': 'SalesArea',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'cpid',
                    't': 'request_body'
                },{
                    'n': '销售区域',
                    'En': 'SalesArea',
                    'v':
                    'List/cpxsqy',
                    't': 'json_join,'
                },

            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        

    def get_xsqy(self, page,response=None):
        index = response.meta['index']
        return urllib.parse.urlencode({
                'tzzlxdm':index,
                'cpid':page,
                'cpjglb':'',
                'cpsylx':'',
                'cpyzms':'',
                'cpqx':'',
                'cpzt':'',
                'cpdjbm':'',
                'cpmc':'',
                'cpfxjg':'',
                'mjqsrq':'',
                'mjjsrq':'',
                'pagenum':1})

    def get_lxdm(self,page, response=None):
        index = response.meta['index']
        return urllib.parse.urlencode({
                                        'tzzlxdm':index,
                                        'cpdjbm':' ' ,
                                        'cpmc':'',
                                        'pagenum':str(page),
                                        'orderby':'cpms',
                                        'code':'',
                                        'changeTableFlage':'0'})

    @SpiderHelp.check_response
    def sina_funds_in(self, response):
        #
        for i in range(2):
            formatter = 'http://app.xincai.com/fund/api/jsonp.json//XinCaiOtherService.getManagerFundInfo?page={}&num=40&sort=NavRate&asc=0&ccode=&date=&type2=%s' % i
            url = formatter.format(1)
            yield self.request(
                        url,
                        meta={'formatter': formatter},
                        redis_flag=REDISFLAG,
                        callback=self.sina_fund_manager_list)

    @SpiderHelp.check_response
    def sina_fund_manager_list(self, response):
        response = response.replace(body=re.compile('(\{.+\})').search(response.text).group(1))
        _configs = [{
            'list': {
                'n': '',
                'v': 'data',    
                't': 'json',
                'db': 'Sina.Sina_Fund_ManagerState',
                'keys': ['ManagerId','State','Bdate'],
                'check': 'ManagerId',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '基金经理姓名',
                    'En': 'Name',
                    'v':
                    'Name',
                    't': 'json'
                },{
                    'n': '基金经理Id',
                    'En': 'ManagerId',
                    'v':
                    'ManagerId',
                    't': 'json'
                },
                {
                    'n': '任职日期', 
                    'En': 'Bdate',
                    'v':
                    'BDate',
                    't': 'json'
                },{
                    'n': '离职时间', # 若Edate 不等于1900-01-01 00:00:00 说明为离职状态
                    'En': 'Edate',
                    'v':
                    'EDate',
                    't': 'json'
                },
                {
                    'n': '是否在职', # 1 在任 2离任
                    'En': 'State',
                    'v':
                    'type2=(\d+)',
                    't': 'url_re'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'total_num'
                        },
                callback=self.sina_fund_manager_list,
                headers=self.default_header,
                urlfunc=
                lambda page, response=None: response.meta['formatter'].format(str(page)),
                divmod=40,
                redis_conn=self.r,
                meta={'proxys':True},
                redis_flag=True,
                readpage=16,
                response_type='json')
        for req in reqs:
            yield req

        # # 列表页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'data/ManagerId',
                                                   },
                                           callback=self.sina_fund_manager,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://stock.finance.sina.com.cn/manager/view/mInfo.php?mid=%s' % page,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs2:
            yield req

    @SpiderHelp.check_response
    def sina_fund_manager(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Sina.Sina_Fund_ManagerBasic',
                'keys': ['ManagerName','HTML_ID'],
                'check': 'ManagerName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'mid=(.+)',
                    't': 'url_re'
                },{
                    'n': '基金经理',
                    'En': 'ManagerName',
                    'v':
                    '//td[contains(text(),"基金经理")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '基金经理image',
                    'En': 'ImagePath',
                    'v':
                    '//td[@class="pic"]//@src',
                    't': 'xpath_first'
                },{
                    'n': '年龄', 
                    'En': 'Age',
                    'v':
                    '//td[contains(text(),"年龄")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '学历', 
                    'En': 'Education',
                    'v':
                    '//td[contains(text(),"学历")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '首次任职', 
                    'En': 'FirstTimesHoldThePost',
                    'v':
                    '//td[contains(text(),"首次任职")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '从业时间',
                    'En': 'EmploymentTime',
                    'v':
                    '//td[contains(text(),"从业时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '资历排名',
                    'En': 'SeniorityRank',
                    'v':
                    '//td[contains(text(),"资历排名")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '任职公司',
                    'En': 'Moodyhas',
                    'v':
                    '//td[contains(text(),"任职公司")]/following-sibling::td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '任职公司ID',
                    'En': 'MoodyhasId',
                    'v':
                    '//td[contains(text(),"任职公司")]/following-sibling::td[1]/a/@href',
                    't': 'xpath_re',
                    're': 'company\/(.+)\.shtml'
                },{
                    'n': '跳槽次数', 
                    'En': 'JobHopping',
                    'v':
                    '//td[contains(text(),"跳槽次数")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '职业资质', 
                    'En': 'VocationalQualifications',
                    'v':
                    '//td[contains(text(),"职业资质")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '简历', 
                    'En': 'Industry',
                    'v':
                    '//td[contains(text(),"简历")]/following-sibling::td[1]/p/text()|//span[@id="detail"]/text()',
                    't': 'xpath_join'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        _configs = [{
            'list': {
                'n': '',
                'v': '//h3[text()="历史业绩"]/following-sibling::table[1]//tr[position()>1]',    
                't': 'xpath',
                'db': 'Sina.Sina_Fund_ManagerPerformance',
                'keys': ['ProdName','HTML_ID'],
                'check': 'ProdName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'mid=(.+)',
                    't': 'url_re'
                },{
                    'n': '基金经理',
                    'En': 'ManagerName',
                    'v':
                    '//td[contains(text(),"基金经理")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '产品名称', 
                    'En': 'ProdName',
                    'v':
                    './td[1]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '产品ID', 
                    'En': 'ProdId',
                    'v':
                    './td[1]/a/@href',
                    't': 'xpath_re',
                    're': 'quotes\/(.+?)\/'
                },{
                    'n': '任职公司', 
                    'En': 'Moodyhas',
                    'v':
                    './td[2]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '任职公司ID', 
                    'En': 'MoodyhasId',
                    'v':
                    './td[2]/a/@href',
                    't': 'xpath_re',
                    're': 'company\/(.+)\.shtml'
                },{
                    'n': '管理类型', 
                    'En': 'ManagementType',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '任职时间', 
                    'En': 'TenureTime',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                },{
                    'n': '任期回报', 
                    'En': 'TermOfReturn',
                    'v':
                    './td[5]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def flush_in(self, response):

        keys = response.xpath('//li[@onclick]').re('\((.+?)\)')
        for key in keys:
            url = 'http://comment.10jqka.com.cn/rapi/main.php?callback=insuredetail&count=20000&else=0&endto=0&gyear=0&lyear=0&method=insure.search&skip=0&start={}&track=insureseach&type=%s' % key
            yield self.request(
                url, 
                redis_flag=REDISFLAG,
                callback=self.flush_insurance_list)

    @SpiderHelp.check_response
    def flush_insurance_list(self, response):
        pass

    @SpiderHelp.check_response
    def circ_jumps(self, response):
        # 备案机构
        yield self.request('http://www.circ.gov.cn/tabid/5254/Default.aspx',
            meta={'proxys':True},
            callback=self.circ_in
            )

        # 人身险产品
        yield self.request('http://www.circ.gov.cn/tabid/5253/ctl/ViewOrgList/mid/16658/OrgTypeID/1/Default.aspx?ctlmode=none',
            meta={'proxys':True,'category':'人身险产品'},
            callback=self.cicr_prod_info
            )

        # 财产险产品
        yield self.request('http://www.circ.gov.cn/tabid/5253/ctl/ViewOrgList/mid/16658/OrgTypeID/2/Default.aspx?ctlmode=none',
            meta={'proxys':True,'category':'财产险产品'},
            callback=self.circ_prod
            )


    def circ_prod(self, response):
        # # 列表页
        if response.xpath('//table[@class="orglist_table"]//@href'):
            reqs2 = self.scrapy_info_url_help( response,
                                               config={'t': 'xpath_extract',
                                                       'v': '//table[@class="orglist_table"]//@href',
                                                       },
                                               callback=self.cicr_prod_info,
                                               headers=self.default_header,
                                               urlfunc=
                                               lambda page, response: 'http://www.circ.gov.cn%s' % page,
                                               errback=self.errbackparse,
                                               response_type='xpath')
            for req in reqs2:
                yield req

    @SpiderHelp.check_response
    def cicr_prod_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="tableRecordProduct"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'Cicr.Circ_InsuranceProdRecord',
                'keys': ['InsuranceComName','ProdName','DateOfRecord','InstitutionalType'],
                'check': 'InsuranceComName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'ItemID\/(.+?)\/',
                    't': 'url_re'
                },{
                    'n': '机构名称',
                    'En': 'InsuranceComName',
                    'v':
                    '//comment()[contains(string(.),"Start")]/following-sibling::node()[1]',
                    't': 'xpath_first'
                },{
                    'n': '产品名称', 
                    'En': 'ProdName',
                    'v':
                    './td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '备案日期', 
                    'En': 'DateOfRecord',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '险种', 
                    'En': 'InstitutionalType',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def circ_in(self, response):
        #'''翻页逻辑'''
        if self.next_flag(response):
            body = self.dara_from_res(response)
            yield self.request(
                response.url,
                method='POST',
                body=body,
                meta={'proxys':True},
                callback=self.circ_in)
        # # 列表页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//div[@id="ess_mailrightpane"]//@onclick',
                                                   're': "OpenWin\(\'(.*?)\',"
                                                   },
                                           callback=self.cicr_insurance_agency,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://www.circ.gov.cn%s?ctlmode=none' % page,
                                           meta={'proxys':True},
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs2:
            yield req

    def cicr_insurance_agency(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Cicr.Circ_Insurance',
                'keys': ['InsuranceComName'],
                'check': 'InsuranceComName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'ItemID\/(.+?)\/',
                    't': 'url_re'
                },{
                    'n': '机构名称',
                    'En': 'InsuranceComName',
                    'v':
                    '//td[contains(text(),"机构名称")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构类别', 
                    'En': 'InstitutionalCategories',
                    'v':
                    '//td[contains(text(),"机构类别")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '设立时间', 
                    'En': 'SetupTime',
                    'v':
                    '//td[contains(text(),"设立时间")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构地址', 
                    'En': 'InstitutionalAddress',
                    'v':
                    '//td[contains(text(),"机构地址")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '联系电话', 
                    'En': 'ContactPhoneNumber',
                    'v':
                    '//td[contains(text(),"联系电话")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '负责人', 
                    'En': 'PersonInCharge',
                    'v':
                    '//td[contains(text(),"负责人")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '中资外资', 
                    'En': 'ChinaOrForeignCapital',
                    'v':
                    '//td[contains(text(),"中资外资")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地', 
                    'En': 'RegisteredAddress',
                    'v':
                    '//td[contains(text(),"注册地")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '状态', 
                    'En': 'State',
                    'v':
                    '//td[contains(text(),"状态")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def get_input(self, response, key):
        tag = '//input[@name="%s"]/@value' % key
        return response.xpath(tag).extract_first() or ''

    def dara_from_res(self, response):
        dic = {'__EVENTTARGET': self.get_input(response, '__EVENTTARGET'),
                '__EVENTARGUMENT': self.get_input(response, '__EVENTARGUMENT'),
                '__VIEWSTATE': self.get_input(response, '__VIEWSTATE'),
                '__VIEWSTATEGENERATOR': self.get_input(response, '__VIEWSTATEGENERATOR'),
                'ScrollTop': self.get_input(response, 'ScrollTop'),
                '__essVariable': self.get_input(response, '__essVariable'),
                'ess$ctr16712$OrganizationList$lblAtPageNum':'',
                'ess$ctr16713$OrganizationList$lblAtPageNum':'',
                'ess$ctr16714$OrganizationList$lblAtPageNum':'',
                'ess$ctr16715$OrganizationList$lblAtPageNum':'',
                'ess$ctr16716$OrganizationList$lblAtPageNum':'',
                'ess$ctr16720$OrganizationList$lblAtPageNum':'',
                'ess$ctr26624$OrganizationList$lblAtPageNum':'',
                
               }
        dic_up = self.get_next(response)
        dic.update(dic_up)
        return urllib.parse.urlencode(dic)

    def next_flag(self, response):
        return bool(response.xpath('//a[contains(text(),"下一页") and @href]'))

    def get_next(self, response):
        sel = response.xpath('//a[contains(text(),"下一页") and @href]/following-sibling::input')
        return {sel[0].xpath('./preceding-sibling::a[1]/@id').extract_first().replace('_','$'):sel[0].xpath('./@value').extract_first() or '',
                '__EVENTTARGET':sel[0].xpath('./@id').extract_first().replace('_','$')}

    @SpiderHelp.check_response
    def all_circ_jumps(self, response):
        # 获取各地区url__js处理后
        _url = re.compile('portals\[\"([^www].*?\.circ\.gov\.cn).*?\"\].*?DeployFolder:\"(.*?)\"').findall(response.text)
        urls = ('http://{}/web/{}/'.format(*i) for i in _url)
        for url in urls:
            yield self.request(url,
            redis_flag=True,
            callback=self.all_circ_jumps2)

    @SpiderHelp.check_response
    def all_circ_jumps2(self, response):
        # 跳转至搜索页
        # 保险机构搜索页
        _url = response.xpath('//table[@class="jgchaxun"]//td[a][1]/a/@href').extract_first()
        yield self.request(response.urljoin(_url),
            redis_flag=True,
            headers=self.default_header,
            callback=self.china_insurance_agency1)
        
    def china_insurance_agency_data(self,page,response=None):
        # if page==1:
        #     EVENTTARGET = 'ess$ctr16871$SearchOrganization$wuPager$lbtnFirstPage'
        if page==1:
            EVENTTARGET = 'ess$ctr16871$SearchOrganization$lkbSearch'
        else:
            EVENTTARGET = 'ess$ctr16871$SearchOrganization$wuPager$lbtnGoto'
        dic={sel.xpath('./@name').extract_first():sel.xpath('./@value').extract_first() if sel.xpath('./@value') else '' for sel in response.xpath('//input[@name]')}
        div['__EVENTTARGET'] = EVENTTARGET
        return urllib.parse.urlencode(dic)


    # @SpiderHelp.check_response
    # def china_insurance_agency1(self, response):
    #     body = self.china_insurance_agency_data(0,response)
    #     yield scrapy.Request(response.url,
    #             method='POST',
    #             body=body,
    #             # redis_flag=True,
    #             headers=self.default_header,
    #             meta={'page':0},
    #             callback=self.china_insurance_agency2)

    @SpiderHelp.check_response
    def china_insurance_agency1(self, response):
        body = self.china_insurance_agency_data(1,response)
        yield scrapy.Request(response.url,
                method='POST',
                body=body,
                # redis_flag=True,
                headers=self.default_header,
                meta={'page':1},
                callback=self.china_insurance_agency_list)

    @SpiderHelp.check_response
    def china_insurance_agency_list(self, response):
         # 保监会  保险机构 
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//tr[@class="datagrid-Header"]/following-sibling::tr//a/@onclick',
                                                   're':"\(\'(.*?)\'\)"
                                                   },
                                           callback=self.china_insurance_agency_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response: 'http://www.circ.gov.cn' + page + '?ctlmode=non',
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_re',
                        'v': '//span[@id="ess_ctr16871_SearchOrganization_wuPager_lblPageInfo"]/text()[1]',
                        're': "总数:(\d+)"
                        },
                callback=self.china_insurance_agency_list,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page, response=None: 'http://www.circ.gov.cn/tabid/3254/Default.aspx',
                bodyfunc=self.china_insurance_agency_data,
                divmod=50,
                redis_conn=self.r,
                redis_flag=True,
                flag=True,
                readpage=2,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def china_insurance_agency_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Cicr.Circ_Insurance_2',
                'keys': ['InsuranceComName','HTML_ID'],
                'check': 'InsuranceComName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'ItemID\/(.+?)\/',
                    't': 'url_re'
                },{
                    'n': '机构名称',
                    'En': 'InsuranceComName',
                    'v':
                    '//td[contains(text(),"机构名称")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构类别', 
                    'En': 'InstitutionalCategories',
                    'v':
                    '//td[contains(text(),"机构类别")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '设立时间', 
                    'En': 'SetupTime',
                    'v':
                    '//td[contains(text(),"设立时间")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构地址', 
                    'En': 'InstitutionalAddress',
                    'v':
                    '//td[contains(text(),"机构地址")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '联系电话', 
                    'En': 'ContactPhoneNumber',
                    'v':
                    '//td[contains(text(),"联系电话")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '负责人', 
                    'En': 'PersonInCharge',
                    'v':
                    '//td[contains(text(),"负责人")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '中资外资', 
                    'En': 'ChinaOrForeignCapital',
                    'v':
                    '//td[contains(text(),"中资外资")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地', 
                    'En': 'RegisteredAddress',
                    'v':
                    '//td[contains(text(),"注册地")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '状态', 
                    'En': 'State',
                    'v':
                    '//td[contains(text(),"状态")]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def all_bank_list(self,response):
        # reqs3 = self.scrapy_info_url_help( response,
        #                                    config={'t': 'xpath_extract',
        #                                            'v': '//div[@class="zong"]//div[@id>1]/ul/li/ul/li[a]/a/@href[string(.)!="http://"]',
        #                                            },
        #                                    callback=self.all_bank_info,
        #                                    headers=self.default_header,
        #                                    urlfunc=
        #                                    lambda page, response: 'http://www.circ.gov.cn' + page + '?ctlmode=non',
        #                                    errback=self.errbackparse,
        #                                    response_type='xpath')
        # for req in reqs3:
        #     yield req

        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="zong"]//div[@id>1]/ul/li/ul/li',    
                't': 'xpath',
                'db': 'Cbrc.Cbrc_Bank',
                'keys': ['BankName'],
                'check': 'BankName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '机构名称',
                    'En': 'BankName',
                    'v':
                    './self::li[a]/a/text()|./self::li[not(a)]/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构url', 
                    'En': 'BankWebSite',
                    'v':
                    './self::li[a]/a/@href[string(.)!="http://"]',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def all_bank_info(self,response):
        pass

    @SpiderHelp.check_response
    def sse_bond_in(self, response):
        yield scrapy.Request('http://bond.sse.com.cn/js/26left.js',
            headers=self.default_header,
            callback=self.sse_bond_jumps1
            )

    @SpiderHelp.check_response
    def sse_bond_jumps1(self, response):
        urls = (url[4] for url in execjs.eval(re.compile('LeftMenu_260301\s*=\s*(\[.*?\]);',re.S).search(response.text).group(1)))
        for url in urls:
            yield self.request('http://bond.sse.com.cn' + url,
                redis_flag=True,
                headers=self.default_header,
                callback=self.sse_bond_jumps)

    @SpiderHelp.check_response
    def sse_bond_jumps(self, response):
        url = 'http://query.sse.com.cn/commonQuery.do?'
        url = url + self.sse_bond_data(1,response)
        sqlId = re.compile("sqlId.*?:.*?\'(.+?)\'",re.S).search(response.text).group(1) 
        yield self.request(url,
            headers=self.header_update(self.default_header,Referer='http://bond.sse.com.cn'),
            meta={'sqlId':sqlId,'proxys':True},
            callback=self.sse_bond_list)

    @SpiderHelp.check_response
    def sse_bond_list(self, response):
        # 
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'json',
                                                   'v': 'result/BOND_CODE',
                                                   },
                                           callback=self.sse_bond_info,
                                           meta={'proxys':True},
                                           headers=self.header_update(self.default_header,Referer='http://bond.sse.com.cn'),
                                           urlfunc=
                                           lambda page, response=None: 'http://query.sse.com.cn/commonQuery.do?isPagination=false&sqlId=COMMON_BOND_BASIC_ZQJBYS_L&BONDCODE=%s' % page,
                                           errback=self.errbackparse,
                                           response_type='json')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'pageHelp/pageCount',
                        },
                callback=self.sse_bond_list,
                headers=self.header_update(self.default_header,Referer='http://bond.sse.com.cn'),
                urlfunc=self.sse_bond_data,
                divmod=5,
                meta={'proxys':True},
                redis_conn=self.r,
                redis_flag=True,
                readpage=20,
                response_type='json')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sse_bond_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': 'result',    
                't': 'json',
                'db': 'Sse.Sse_Bond',
                'keys': ['BondCode'],
                'check': 'BondCode',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'BONDCODE=(.+)',
                    't': 'url_re'
                },{
                    'n': '债券代码', 
                    'En': 'BondCode',
                    'v':
                    'BOND_CODE',
                    't': 'json'
                },{
                    'n': '债券简称', 
                    'En': 'BondShortName',
                    'v':
                    'BOND_ABBR',
                    't': 'json'
                },{
                    'n': '发行人', 
                    'En': 'IssuerName',
                    'v':
                    'ISSUE_OWNER',
                    't': 'json'
                },{
                    'n': '债券全称', 
                    'En': 'BondFullName',
                    'v':
                    'BOND_FULL',
                    't': 'json'
                },{
                    'n': '债券类型', 
                    'En': 'BondType',
                    'v':
                    'BOND_TYPE',
                    't': 'json'
                },{
                    'n': '发行量（亿元）', 
                    'En': 'Circulation',
                    'v':
                    'ISSUE_VALUE',
                    't': 'json'
                },{
                    'n': '上交所上市总量（亿元）', 
                    'En': 'SseTotalAmt',
                    'v':
                    'SSE_TOTAL_AMT',
                    't': 'json'
                },{
                    'n': '起息日期', 
                    'En': 'StartDate',
                    'v':
                    'START_DATE',
                    't': 'json'
                },{
                    'n': '到期日期', 
                    'En': 'EndDate',
                    'v':
                    'END_DATE',
                    't': 'json'
                },{
                    'n': '上市日期', 
                    'En': 'ListedDate',
                    'v':
                    'LISTING_DATE',
                    't': 'json'
                },{
                    'n': '银行间代码', 
                    'En': 'BankCode',
                    'v':
                    'BANK_CODE',
                    't': 'json'
                },{
                    'n': '计息方式', 
                    'En': 'InterestType',
                    'v':
                    'INTEREST_TYPE',
                    't': 'json'
                },{
                    'n': '付息方式', 
                    'En': 'PayType',
                    'v':
                    'PAY_TYPE',
                    't': 'json'
                },{
                    'n': '票面利率（%）', 
                    'En': 'FaceRate',
                    'v':
                    'FACE_RATE',
                    't': 'json'
                },{
                    'n': '债券期限（年）', 
                    'En': 'TermYear',
                    'v':
                    'TERM_YEAR',
                    't': 'json'
                },{
                    'n': '基准利率（%）', 
                    'En': 'BaseRate',
                    'v':
                    'BASE_RATE',
                    't': 'json'
                },{
                    'n': '浮动利差（%）', 
                    'En': 'FloatRate',
                    'v':
                    'FLOAT_RATE',
                    't': 'json'
                },{
                    'n': '标准券折算率', 
                    'En': 'Rate',
                    'v':
                    'RATE',
                    't': 'json'
                },{
                    'n': '债券估值（元）', 
                    'En': 'CleanPrice',
                    'v':
                    'CLEAN_PRICE',
                    't': 'json'
                },{
                    'n': '投资者适当性管理', 
                    'En': 'ManageType',
                    'v':
                    'MANAGE_TYPE',
                    't': 'json'
                },{
                    'n': '交易方式', 
                    'En': 'TradeType',
                    'v':
                    'TRADE_TYPE',
                    't': 'json'
                },{
                    'n': '发行起始日', 
                    'En': 'IssueStartDate',
                    'v':
                    'ISSUED_START_DAY',
                    't': 'json'
                },{
                    'n': '发行结束日', 
                    'En': 'IssueEndDate',
                    'v':
                    'ISSUED_END_DAY',
                    't': 'json'
                },{
                    'n': '银行内部代码', 
                    'En': 'InterBankCode',
                    'v':
                    'INTERBANK_CODE',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def sse_bond_data(self,page,response=None):
        match = re.compile('isPagination=(.+?)&sqlId=(.+?)&pageHelp.pageSize=(.+?)BONDTYPE=(.+?)&.+?').search(response.url)
        if match:
            isPagination,sqlId,pageSize,BONDTYPE=match.groups()
        else:
            params = execjs.eval(re.compile('params\s*?=\s*?(\{.+?\});',re.S).search(response.text).group(1))
            sqlId = params.get('sqlId')
            BONDTYPE = params.get('BONDTYPE')
            isPagination = params.get('isPagination')
            pageSize = params.get('pageHelp.pageSize')
        return 'http://query.sse.com.cn/commonQuery.do?isPagination=%s&sqlId=%s&pageHelp.pageSize=%s&BONDTYPE=%s&pageHelp.pageNo=%s&pageHelp.beginPage=%s&pageHelp.endPage=%s' % (isPagination,sqlId,pageSize,BONDTYPE,page,page//5 * 5 +1 ,page//5 * 5 + 5)

    def get_china_body(self, response):
        pass

    @SpiderHelp.check_response
    def cq_financial_institution_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="company"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'Cbrc.Microfinance',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '机构名称',
                    'En': 'CompanyName',
                    'v':
                    './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '联系电话', 
                    'En': 'OfficePhoneNumber',
                    'v':
                    './td[3]/text()',
                    't': 'xpath_first'
                },{
                    'n': '单位地址', 
                    'En': 'OfficeAddress',
                    'v':
                    './td[4]/text()',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sh_financial_institution_jumps(self, response):
        # 小贷
        url = 'http://sjr.sh.gov.cn/ZhengWuDaTing/Index?categoryid=10&parentid=64&OgnTpPid=553'
        yield scrapy.Request(
            url,
            headers=self.default_header,
            callback=self.sh_financial_institution_list)
        # # 担保 --暂留 --解析不出来
        # url = 'http://sjr.sh.gov.cn/ZhengWuDaTing/Index?categoryid=10&parentid=64&OgnTpPid=554'
        # yield scrapy.Request(
        #     url,
        #     headers=self.default_header,
        #     callback=self.sh_guarantee_institution_list)

    def sh_financial_institution_list(self, response):
        urls = response.xpath('//p[@class="pp"]//a')
        for url in urls:
            response = pdf_to_html('http://sjr.sh.gov.cn'+url.xpath('./@href').extract_first())
            title = url.xpath('./text()').extract_first()
            _configs = [{
                'list': {
                    'n': '',
                    'v': '//table//tr[position()>2]',    
                    't': 'xpath',
                    'db': 'Cbrc.Microfinance',
                    'keys': ['CompanyName','Title'],
                    'check': 'CompanyName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': '机构名称',
                        'En': 'CompanyName',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '联系电话', 
                        'En': 'OfficePhoneNumber',
                        'v':
                        './td[7]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '单位地址', 
                        'En': 'OfficeAddress',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '注册资本 (万元）', 
                        'En': 'RegisteredCapital',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '法定代表人', 
                        'En': 'NameOfLegalRepresentative',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '成立日期', 
                        'En': 'SetupTime',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '标题', 
                        'En': 'Title',
                        'v':title,
                        't': 'abs'
                    }
                ]
            }]
            results = self.item_parse(_configs, response)
            for item in results:
                yield item

    @SpiderHelp.check_response
    def bj_financial_institution(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[colgroup]//tr[position()>3]',    
                't': 'xpath',
                'db': 'Cbrc.Microfinance',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '机构名称',
                    'En': 'CompanyName',
                    'v':
                    './td[last()-2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '联系电话', 
                    'En': 'OfficePhoneNumber',
                    'v':
                    './td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '单位地址', 
                    'En': 'OfficeAddress',
                    'v':
                    './td[last()-1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '区域', 
                    'En': 'AreaName',
                    'v':
                    './self::tr[td[last()=5]]/td[2]/text()|./self::tr[td[last()=4]]/preceding::tr[td[5]][1]/td[2]/text()',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def pedaily_in(self, response):
        # #  清科投资机构
        # yield self.request('http://zdb.pedaily.cn/company/all/',
        #     redis_flag=True,
        #     callback=self.pedaily_Investment_list)

        # #  清科创业机构
        # yield self.request('http://zdb.pedaily.cn/enterprise/all/',
        #     redis_flag=True,
        #     callback=self.pedaily_startups_list)

        # #  清科投资人
        # yield self.request('http://zdb.pedaily.cn/people/all/',
        #     redis_flag=True,
        #     callback=self.pedaily_Inverstor_list)

        # #  清科募资事件
        # yield self.request('http://zdb.pedaily.cn/pe/all/',
        #     redis_flag=True,
        #     callback=self.pedaily_Collecting_list)

        # #  清科并购事件
        # yield self.request('http://zdb.pedaily.cn/ma/all/',
        #     redis_flag=True,
        #     callback=self.pedaily_Merger_list)

        # #  清科上市事件
        # yield self.request('http://zdb.pedaily.cn/ipo/all/',
        #     redis_flag=True,
        #     callback=self.pedaily_IPO_list)

        #  清科投资事件
        yield self.request('http://zdb.pedaily.cn/inv/all/',
            redis_flag=True,
            callback=self.pedaily_Investment_event_list)

    @SpiderHelp.check_response
    def pedaily_Investment_list(self, response):
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//ul[@id="company-list"]//li/div[@class="txt"]//h3/span[2]//@href',
                                                   },
                                           callback=self.pedaily_Investment_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://zdb.pedaily.cn%s' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//span[@class="total"]/text()',
                        },
                callback=self.pedaily_Investment_list,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://zdb.pedaily.cn/company/p%s/' % page,
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def pedaily_Investment_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Pedaily.Pedaily_InvestmentInstitution',
                'keys': ['ComName'],
                'check': 'ComName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'show(\d+)\/',
                    't': 'url_re'
                },{
                    'n': '机构名称',
                    'En': 'ComName',
                    'v':
                    '//div[@class="info"]/h1/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构简称', 
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="info"]/h1/em/text()',
                    't': 'xpath_first'
                },{
                    'n': '英文名称', 
                    'En': 'ComEnglishName',
                    'v':
                    '//div[@class="info"]/h2/text()',
                    't': 'xpath_first'
                },{
                    'n': 'logo', 
                    'En': 'Logo',
                    'v':
                    '//div[@class="zdb-top"]//div[@class="img"]//@src[not(contains(string(.),"noimage"))]',
                    't': 'xpath_first'
                },{
                    'n': '资本类型', 
                    'En': 'TypeOfCapital',
                    'v':
                    '//div[@class="info"]//li[span[contains(text(),"资本类型")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构性质', 
                    'En': 'InstitutionalNature',
                    'v':
                    '//div[@class="info"]//li[span[contains(text(),"机构性质")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地点', 
                    'En': 'RegisteredAddress',
                    'v':
                    '//div[@class="info"]//li[span[contains(text(),"注册地点")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立时间', 
                    'En': 'SetupTime',
                    'v':
                    '//div[@class="info"]//li[span[contains(text(),"成立时间")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构总部', 
                    'En': 'HeadQuarters',
                    'v':
                    '//div[@class="info"]//li[span[contains(text(),"机构总部")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '官方网站', 
                    'En': 'OfficeWebsite',
                    'v':
                    '//div[@class="info"]//li[span[contains(text(),"官方网站")]]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '投资阶段', 
                    'En': 'InvestmentStages',
                    'v':
                    '//div[@class="info"]//li[span[contains(text(),"投资阶段")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '简介', 
                    'En': 'Profile',
                    'v':
                    '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="desc"]//text()[not(contains(string(.),"document")) and not(../@title)]',
                    't': 'xpath_join'
                },{
                    'n': '联系电话', 
                    'En': 'OfficePhoneNumber',
                    'v':
                    '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="contact"]/*[span[contains(text(),"联系电话")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '传 真', 
                    'En': 'OfficeFaxNumber',
                    'v':
                    '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="contact"]/*[span[contains(text(),"传 真")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '地 址', 
                    'En': 'OfficeAddress',
                    'v':
                    '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="contact"]/*[span[contains(text(),"地 址")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '邮 编', 
                    'En': 'ZipCode',
                    'v':
                    '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="contact"]/*[span[contains(text(),"邮 编")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '团队人数', 
                    'En': 'TeamNumber',
                    'v':
                    'count(//ul[@class="list-pics"]/li)',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def pedaily_startups_list(self, response):
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//ul[@id="enterprise-list"]//li/div[@class="txt"]//h3/span[2]//@href',
                                                   },
                                           callback=self.pedaily_startups_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://zdb.pedaily.cn%s' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//span[@class="total"]/text()',
                        },
                callback=self.pedaily_startups_list,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://zdb.pedaily.cn/enterprise/p%s/' % page,
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def pedaily_startups_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Pedaily.Pedaily_StartupsCompany',
                'keys': ['ComName'],
                'check': 'ComName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID', #   http://zdb.pedaily.cn/enterprise/show{HTML_ID}/
                    'En': 'HTML_ID',
                    'v':
                    'show(\d+)\/',
                    't': 'url_re'
                },{
                    'n': '机构名称',
                    'En': 'ComName',
                    'v':
                    '//div[@class="info"]/h1/text()',
                    't': 'xpath_first'
                },{
                    'n': '机构简称', 
                    'En': 'ComShortName',
                    'v':
                    '//div[@class="info"]/h1/em/text()',
                    't': 'xpath_first'
                },{
                    'n': '英文名称', 
                    'En': 'ComEnglishName',
                    'v':
                    '//div[@class="info"]/h2/text()',
                    't': 'xpath_first'
                },{
                    'n': 'logo', 
                    'En': 'Logo',
                    'v':
                    '//div[@class="zdb-top"]//div[@class="img"]//@src[not(contains(string(.),"noimage"))]',
                    't': 'xpath_first'
                },{
                    'n': '机构总部', 
                    'En': 'HeadQuarters',
                    'v':
                    '//div[@class="info"]//li[span[contains(text(),"机构总部")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地点', 
                    'En': 'RegisteredAddress',
                    'v':
                    '//div[@class="info"]//li[span[contains(text(),"注册地点")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立时间', 
                    'En': 'SetupTime',
                    'v':
                    '//div[@class="info"]//li[span[contains(text(),"成立时间")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '所属行业', 
                    'En': 'Industry',
                    'v':
                    '//div[@class="info"]//li[span[contains(text(),"所属行业")]]/text()',
                    't': 'xpath_first'
                },{
                    'n': '官方网站', 
                    'En': 'OfficeWebsite',
                    'v':
                    '//div[@class="info"]//li[span[contains(text(),"官方网站")]]/a/text()',
                    't': 'xpath_first'
                },{
                    'n': '简介', 
                    'En': 'Profile',
                    'v':
                    '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="desc"]//text()[not(contains(string(.),"document")) and not(../@title)]',
                    't': 'xpath_join'
                },{
                    'n': '联系电话', 
                    'En': 'OfficePhoneNumber',
                    'v':
                    '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="contact"]//span[contains(text(),"联系电话")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },{
                    'n': '传 真', 
                    'En': 'OfficeFaxNumber',
                    'v':
                    '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="contact"]//span[contains(text(),"传 真")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },{
                    'n': '详细地址', 
                    'En': 'OfficeAddress',
                    'v':
                    '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="contact"]//span[contains(text(),"详细地址")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },{
                    'n': '邮政编码', 
                    'En': 'ZipCode',
                    'v':
                    '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="contact"]//span[contains(text(),"邮政编码")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def pedaily_Inverstor_list(self, response):
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//ul[@id="people-list"]//li/div[@class="txt"]//h3//@href',
                                                   },
                                           callback=self.pedaily_Inverstor_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//span[@class="total"]/text()',
                        },
                callback=self.pedaily_Inverstor_list,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://zdb.pedaily.cn/people/p%s/' % page,
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def pedaily_Inverstor_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'Pedaily.Pedaily_InverstorBasic',
                'keys': ['HTML_ID'],
                'check': 'Name',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID', #   http://zdb.pedaily.cn/people/show{HTML_ID}/
                    'En': 'HTML_ID',
                    'v':
                    'show(\d+)\/',
                    't': 'url_re'
                },{
                    'n': '姓名',
                    'En': 'Name',
                    'v':
                    '//div[@class="info"]/h1/text()',
                    't': 'xpath_first'
                },{
                    'n': 'image', 
                    'En': 'Image',
                    'v':
                    '//div[@class="zdb-top"]//div[@class="img"]//@src[not(contains(string(.),"nopeople"))]',
                    't': 'xpath_first'
                },{
                    'n': '所在公司', 
                    'En': 'ComName',
                    'v':
                    '//div[@class="com"]/span[not(@class="job")][1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '职务', 
                    'En': 'Positions',
                    'v':
                    '//div[@class="com"]/span[@class="job"][1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '职业信息', 
                    'En': 'Occupational',
                    'v':
                    '//li[span[contains(text(),"职业信息")]]/a/text()',
                    't': 'xpath_join,'
                },{
                    'n': '投资领域', 
                    'En': 'InvestmentField',
                    'v':
                    '//li[span[contains(text(),"投资领域")]]/a/text()',
                    't': 'xpath_join,'
                },{
                    'n': '简介', 
                    'En': 'Profile',
                    'v':
                    '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="desc"]//text()[not(contains(string(.),"document")) and not(../@title)]',
                    't': 'xpath_join'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="list-time list-zdb list-career"]//li[position()>1]',    
                    't': 'xpath',
                    'db': 'Pedaily.Pedaily_InverstorWorkEx',
                    'keys': ['HTML_ID','ComName','Position','TimeInterval'],
                    'check': 'ComName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/people/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'show(\d+)\/',
                        't': 'url_re'
                    },{
                        'n': '姓名',
                        'En': 'Name',
                        'v':
                        '//div[@class="info"]/h1/text()',
                        't': 'xpath_first'
                    },{
                        'n': '时间段', 
                        'En': 'TimeInterval',
                        'v':
                        './/span[@class="time"]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '所在公司', 
                        'En': 'ComName',
                        'v':
                        './/*[@class="company"]//text()',
                        't': 'xpath_first'
                    },{
                        'n': '职务', 
                        'En': 'Position',
                        'v':
                        './/*[@class="duty"]//text()',
                        't': 'xpath_first'
                    },{
                        'n': '职业状态', 
                        'En': 'State',
                        'v':
                        './/*[@class="state"]//text()',
                        't': 'xpath_first,'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def pedaily_Collecting_list(self, response):
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[contains(text(),"详情")]/@href',
                                                   },
                                           callback=self.pedaily_Collecting_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://zdb.pedaily.cn' + page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//span[@class="total"]/text()',
                        },
                callback=self.pedaily_Collecting_list,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://zdb.pedaily.cn/pe/p%s/' % page,
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def pedaily_Collecting_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'xpath',
                    'db': 'Pedaily.Pedaily_Collecting',
                    'keys': ['FundName', 'HTML_ID'],
                    'check': 'FundName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/pe/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'show(\d+)\/',
                        't': 'url_re'
                    },{
                        'n': '基金名称',
                        'En': 'FundName',
                        'v':
                        '//div[@class="info"]/h1/text()',
                        't': 'xpath_first'
                    },{
                        'n': '币 种',
                        'En': 'Currency',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"币 种")]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '成立时间', 
                        'En': 'SetupTime',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"成立时间")]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '募集状态', 
                        'En': 'CollectionType',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"募集状态")]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '管理机构', 
                        'En': 'ManagementAgency',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"管理机构")]]/a/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '目标规模', 
                        'En': 'TargetScale',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"目标规模")]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '资本类型', 
                        'En': 'CapitalType',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"资本类型")]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '募集金额', 
                        'En': 'CollectionAmount',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"募集金额")]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '简介', 
                        'En': 'Profile',
                        'v':
                        '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="desc"]//text()[not(contains(string(.),"document")) and not(../@*)]',
                        't': 'xpath_join'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def pedaily_Merger_list(self, response):
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[contains(text(),"详情")]/@href',
                                                   },
                                           callback=self.pedaily_Merger_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://zdb.pedaily.cn' + page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//span[@class="total"]/text()',
                        },
                callback=self.pedaily_Merger_list,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://zdb.pedaily.cn/ma/p%s/' % page,
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def pedaily_Merger_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'xpath',
                    'db': 'Pedaily.Pedaily_Merger',
                    'keys': ['Event', 'HTML_ID'],
                    'check': 'Event',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/ma/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'show(\d+)\/',
                        't': 'url_re'
                    },{
                        'n': '事件',
                        'En': 'Event',
                        'v':
                        '//div[@class="info"]/h1/text()',
                        't': 'xpath_first'
                    },{
                        'n': '并  购  方',
                        'En': 'Acquirer',
                        'v':
                        '//div[@class="info"]//li[span[re:test(text(),"并.*?购.*?方")]]/a/text()',
                        't': 'xpath_first'
                    },{
                        'n': '被并购方', 
                        'En': 'Merged',
                        'v':
                        '//div[@class="info"]//li[span[re:test(text(),"被并购方")]]/a/text()',
                        't': 'xpath_first'
                    },{
                        'n': '并购状态', 
                        'En': 'StateOfMerger',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"并购状态")]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '所属行业', 
                        'En': 'Industry',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"所属行业")]]/a/text()',
                        't': 'xpath_join>'
                    },
                    {
                        'n': '涉及股权', 
                        'En': 'InvolvingEquity',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"涉及股权")]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '并购开始时间', 
                        'En': 'StartTimeOfMA',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"并购开始时间")]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '并购结束时间', 
                        'En': 'EndTimeOfMA',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"并购结束时间")]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '是否VC/PE支持', 
                        'En': 'VC_PE_Support',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"是否VC/PE支持")]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '简介', 
                        'En': 'Profile',
                        'v':
                        '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="desc"]//text()[not(contains(string(.),"document")) and not(../@*)]',
                        't': 'xpath_join'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def pedaily_IPO_list(self, response):
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[contains(text(),"详情")]/@href',
                                                   },
                                           callback=self.pedaily_IPO_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://zdb.pedaily.cn' + page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//span[@class="total"]/text()',
                        },
                callback=self.pedaily_IPO_list,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://zdb.pedaily.cn/ipo/p%s/' % page,
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def pedaily_IPO_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'xpath',
                    'db': 'Pedaily.Pedaily_IPO',
                    'keys': ['Event', 'HTML_ID'],
                    'check': 'Event',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/ipo/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'show(\d+)\/',
                        't': 'url_re'
                    },{
                        'n': '事件',
                        'En': 'Event',
                        'v':
                        '//div[@class="info"]/h1/text()',
                        't': 'xpath_first'
                    },{
                        'n': '公司名称',
                        'En': 'ComName',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"公司名称")]]/a/text()',
                        't': 'xpath_first'
                    },{
                        'n': '所属行业', 
                        'En': 'Industry',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"所属行业")]]/a/text()',
                        't': 'xpath_join>'
                    },{
                        'n': '投  资  方', 
                        'En': 'InvestmentCompanys',
                        'v':
                        '//div[@class="info"]//li[span[re:test(text(),"投.*?资.*?方")]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '上市时间', 
                        'En': 'ListedDate',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"上市时间")]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '发  行  价', 
                        'En': 'IssuePrice',
                        'v':
                        '//div[@class="info"]//li[span[re:test(text(),"发.*?行.*?价")]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '上市地点', 
                        'En': 'StockExchange',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"上市地点")]]/a/text()',
                        't': 'xpath_first'
                    },{
                        'n': '发  行  量', 
                        'En': 'IssueScale',
                        'v':
                        '//div[@class="info"]//li[span[re:test(text(),"发.*?行.*?量")]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '股票代码', 
                        'En': 'StockCode',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"股票代码")]]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '是否VC/PE支持', 
                        'En': 'VC_PE_Support',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"是否VC/PE支持")]]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def pedaily_Investment_event_list(self, response):
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//a[contains(text(),"详情")]/@href',
                                                   },
                                           callback=self.pedaily_Investment_event_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://zdb.pedaily.cn' + page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//span[@class="total"]/text()',
                        },
                callback=self.pedaily_Investment_event_list,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://zdb.pedaily.cn/inv/p%s/' % page,
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def pedaily_Investment_event_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'xpath',
                    'db': 'Pedaily.Pedaily_InvestmentEvent',
                    'keys': ['Event', 'HTML_ID'],
                    'check': 'Event',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'show(\d+)\/',
                        't': 'url_re'
                    },{
                        'n': '事件',
                        'En': 'Event',
                        'v':
                        '//div[@class="info"]/h1/text()',
                        't': 'xpath_first'
                    },{
                        'n': '融  资  方',
                        'En': 'Financingers',
                        'v':
                        '//div[@class="info"]//li[span[re:test(text(),"融.*?资.*?方")]]/a/text()',
                        't': 'xpath_first'
                    },{
                        'n': '投  资  方', 
                        'En': 'Investor',
                        'v':
                        '//div[@class="info"]//li[span[re:test(text(),"投.*?资.*?方")]]/a/text()[string(.)!="不公开的投资者"]',
                        't': 'xpath_join>'
                    },{
                        'n': '金　　额', 
                        'En': 'Amount',
                        'v':
                        '//div[@class="info"]//li[span[re:test(text(),"金.*?额")]]/span/text()[string(.)!="金　　额："]',
                        't': 'xpath_join:'
                    },{
                        'n': '轮　　次', 
                        'En': 'Turns',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"轮　　次")]]//text()[string(.)!="轮　　次："]',
                        't': 'xpath_join'
                    },
                    {
                        'n': '融资时间', 
                        'En': 'FinancingTime',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"融资时间")]]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '所属行业', 
                        'En': 'Industry',
                        'v':
                        '//div[@class="info"]//li[span[contains(text(),"所属行业")]]/a/text()',
                        't': 'xpath_join>'
                    },{
                        'n': '简介', 
                        'En': 'Profile',
                        'v':
                        '//div[@class="main zdb-show"]/div[@class="box-fix-l"]/div[@id="desc"]//text()[not(contains(string(.),"document")) and not(../@*)]',
                        't': 'xpath_first'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def neeq_in(self, response):
        yield scrapy.Request('http://www.neeq.com.cn/nq/listedcompany.html',
            headers=self.default_header,
            callback=self.neeq_com_list)

    @SpiderHelp.check_response
    def neeq_com_list(self, response):
        pass

    @SpiderHelp.check_response
    def sac_in(self, response):
        # 从业资格
        yield scrapy.Request('http://person.sac.net.cn/pages/registration/train-line-register!orderSearch.action',
            method="POST",
            body=urllib.parse.urlencode({
                'filter_EQS_OTC_ID':'',
                'ORDERNAME':'AOI#AOI_NAME',
                'ORDER':'ASC',
                'sqlkey':'registration',
                'sqlval':'SELECT_LINE_PERSON',
                }),
            meta={'proxys':True},
            headers=self.default_header,
            callback=self.sac_com_Qualificatio_certificate_list1)

        # # 公司信息   http://jg.sac.net.cn/pages/publicity/securities-list.html
        # yield self.request('http://jg.sac.net.cn/pages/publicity/resource!search.action',
        #     method="POST",
        #     body=urllib.parse.urlencode({
        #         'filter_EQS_O#otc_id':'',
        #         'filter_EQS_O#sac_id':'',
        #         'filter_LIKES_aoi_name':'',
        #         'sqlkey':'publicity',
        #         'sqlval':'ORG_BY_TYPE_INFO',
        #         }),
        #     priority=1500,
        #     headers=self.default_header,
        #     callback=self.sac_com_list)

        # # 备案
        # yield self.request('http://www.sac.net.cn/cpbags/index.html',
        #     headers=self.default_header,
        #     callback=self.sac_prod_list)

    @SpiderHelp.check_response
    def sac_prod_list(self, response):
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//table[@class="mar_cen gl_list"]//@href',
                                                   },
                                           callback=self.sac_prod_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: response.urljoin(page),
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'abs',
                        'v': '50',
                        },
                callback=self.sac_prod_list,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://www.sac.net.cn/cpbags/index_%s.html' % (page-1),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sac_prod_info(self, response):
        # 备案产品信息提取
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'xpath',
                    'db': 'Sac.Sac_ComProd',
                    'keys': ['HTML_ID'],
                    'check': 'HTML_ID',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID',
                        'En': 'HTML_ID',
                        'v':
                        'cpbags\/\w+\/(.*?)\.html',
                        't': 'url_re'
                    },{
                        'n': '标题',
                        'En': 'Title',
                        'v':
                        '//div[@class="xl_h"]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '小标题',
                        'En': 'Title2',
                        'v':
                        'string(.//div[@class="hei14"])',
                        't': 'xpath_re',
                        're': '(.*?号)'
                    },{
                        'n': '正文',
                        'En': 'Content',
                        'v':
                        '//div[@class="hei14"]//p[contains(string(.),"根据")]//text()|//div[@class="hei14"]//p[contains(string(.),"你公司")]//text()',
                        't': 'xpath_join'
                    },{
                        'n': '产品名称',
                        'En': 'ProdName',
                        'v':
                        'string(.//div[@class="hei14"]/div[1])',
                        't': 'xpath_re',
                        're': '发起设立的(.*?)进行了审查'
                    },{
                        'n': '公司名称',
                        'En': 'ComName',
                        'v':
                        'string(.//div[@class="hei14"]//p[contains(string(.),"：") and local-name() ="p"][1])',
                        't': 'xpath_re',
                        're': '(.*?)：'
                    },{
                        'n': '准许机关',
                        'En': 'PermissionAuthority',
                        'v':
                        '//div[@class="hei14"]/div//*[@align="right"][last()-1]//text()',
                        't': 'xpath_join'
                    },{
                        'n': '准许日期',
                        'En': 'PermissionDate',
                        'v':
                        '//div[@class="hei14"]/div//*[@align="right"][last()]//text()',
                        't': 'xpath_join'
                    }
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sac_com_list(self, response):
        
        # _configs = [{
        #         'list': {
        #             'n': '',
        #             'v': '',    
        #             't': 'json',
        #             'db': 'Sac.Sac_ComIndex',
        #             'keys': ['ComName','Category'],
        #             'check': 'ComName',
        #             'conn': conn_flag
        #         },
        #         'response_type':
        #         'json',
        #         'data': [
        #             {
        #                 'n': '机构ID',
        #                 'En': 'HTML_ID',
        #                 'v':
        #                 'AOI_ID',
        #                 't': 'json'
        #             },{
        #                 'n': '中文全称',
        #                 'En': 'ComName',
        #                 'v':
        #                 'AOI_NAME',
        #                 't': 'json'
        #             },{
        #                 'n': '协会分类',
        #                 'En': 'Category',
        #                 'v':
        #                 'OTC_ID',
        #                 't': 'json'
        #             },{
        #                 'n': '地区代码',
        #                 'En': 'AreaCode',
        #                 'v':
        #                 'SAC_ID',
        #                 't': 'json'
        #             }
        #         ]
        #     }]
        # results = self.item_parse(_configs, response)
        # for item in results:
        #     yield item

        JS = execjs.eval(response.text)
        url = 'http://jg.sac.net.cn/pages/publicity/resource!search.action'
        for sel in JS:
            AOI_ID = sel['AOI_ID']
            # OTC_ID = sel['OTC_ID'] # 公司类型
            # 基础信息 
            # yield self.request(url,
            #     method='POST',
            #     body=urllib.parse.urlencode({'filter_EQS_aoi_id':AOI_ID,
            #                              'sqlkey':'publicity',
            #                              'sqlval':'SELECT_ZX_REG_INFO'}),
            #     priority=2000,
            #     headers=self.default_header,
            #     callback=self.sac_com_basic_info)

            # # 会员信息
            # yield self.request(url,
            #     method='POST',
            #     body=urllib.parse.urlencode({'filter_EQS_aoi_id':AOI_ID,
            #                          'sqlkey':'info',
            #                          'sqlval':'GET_ORG_INFO_AOIID'}),
            #     priority=2000,
            #     headers=self.default_header,
            #     callback=self.sac_com_member_info)

            # # 高管
            # yield self.request(url,
            #     method='POST',
            #     body=urllib.parse.urlencode({'filter_EQS_aoi_id':AOI_ID,
            #                              'sqlkey':'publicity',
            #                              'sqlval':'ZX_EXECUTIVE_LIST'}),
            #     priority=2000,
            #     headers=self.default_header,
            #     meta={'AOI_ID': AOI_ID},
            #     callback=self.sac_supervisor_info)

            # 分公司  
            yield self.request('http://jg.sac.net.cn/pages/publicity/resource!list.action',
                method='POST',
                body=urllib.parse.urlencode({'filter_LIKES_mboi_branch_full_name':'',
                                            'filter_LIKES_mboi_off_address':'',
                                            'filter_EQS_aoi_id':AOI_ID,
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_BRANCH_ORG',
                                            'page.sqlCKey':'SIZE_BRANCH_ORG',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':'1',
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'}),
                priority=2000,
                headers=self.default_header,
                meta={'AOI_ID': AOI_ID},
                callback=self.sac_branch_info)

            # 营业部  
            yield self.request('http://jg.sac.net.cn/pages/publicity/resource!list.action',
                method='POST',
                body=urllib.parse.urlencode({'filter_LIKES_msdi_name':'',
                                            'filter_LIKES_msdi_reg_address':'',
                                            'filter_EQS_aoi_id':AOI_ID,
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_SALES_DEPT',
                                            'page.sqlCKey':'SIZE_SALES_DEPT',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':'1',
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'}),
                priority=2000,
                headers=self.default_header,
                meta={'AOI_ID': AOI_ID},
                callback=self.sac_department_info)

            # # 执业人员
            # yield self.request('http://jg.sac.net.cn/pages/publicity/resource!list.action',
            #     method='POST',
            #     body=urllib.parse.urlencode({'filter_EQS_aoi_id':AOI_ID,
            #                                 'page.searchFileName':'publicity',
            #                                 'page.sqlKey':'PAG_PRACTITIONERS',
            #                                 'page.sqlCKey':'SIZE_PRACTITONERS',
            #                                 '_search':'false',
            #                                 'nd':str(int(time.time()*1000)),
            #                                 'page.pageSize':'15',
            #                                 'page.pageNo':'1',
            #                                 'page.orderBy':'MATO_UPDATE_DATE',
            #                                 'page.order':'desc'}),
            #     priority=2000,
            #     headers=self.default_header,
            #     meta={'AOI_ID': AOI_ID},
            #     callback=self.sac_Practitioners_info)

    @SpiderHelp.check_response
    def sac_branch_info(self, response):
        if '没有被赋值' in response.text:
            return
        _configs = [{   
                'list': {
                    'n': '',
                    'v': 'result',    
                    't': 'json',
                    'db': 'Sac.Sac_ComBranch',
                    'keys': ['HTML_ID','BranchName'],
                    'check': 'BranchName',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'meta'
                    },{
                        'n': '分公司名称',
                        'En': 'BranchName',
                        'v':
                        'MBOI_BRANCH_FULL_NAME',
                        't': 'json'
                    },{
                        'n': '办公地址',
                        'En': 'OfficeAddress',
                        'v':
                        'MBOI_OFF_ADDRESS',
                        't': 'json'
                    },{
                        'n': '业务范围',
                        'En': 'ScopeOfoperation',
                        'v':
                        'MBOI_BUSINESS_SCOPE',
                        't': 'json'
                    },{
                        'n': '负责人',
                        'En': 'PersonInCharge',
                        'v':
                        'MBOI_PERSON_IN_CHARGE',
                        't': 'json'
                    },{
                        'n': '客户投诉电话',
                        'En': 'CustomerServerTel',
                        'v':
                        'MBOI_CS_TEL',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages',
                        },
                method='POST',
                callback=self.sac_branch_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://jg.sac.net.cn/pages/publicity/resource!list.action',
                bodyfunc=lambda page,response=None:urllib.parse.urlencode({'filter_LIKES_mboi_branch_full_name':'',
                                            'filter_LIKES_mboi_off_address':'',
                                            'filter_EQS_aoi_id':response.meta['AOI_ID'],
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_BRANCH_ORG',
                                            'page.sqlCKey':'SIZE_BRANCH_ORG',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':str(page),
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'}),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='json')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sac_department_info(self, response):
        if '没有被赋值' in response.text:
            return
        _configs = [{   
                'list': {
                    'n': '',
                    'v': 'result',    
                    't': 'json',
                    'db': 'Sac.Sac_ComDepartment',
                    'keys': ['HTML_ID','DepartmentName'],
                    'check': 'DepartmentName',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'meta'
                    },{
                        'n': '营业部名称',
                        'En': 'DepartmentName',
                        'v':
                        'MSDI_NAME',
                        't': 'json'
                    },{
                        'n': '办公地址',
                        'En': 'OfficeAddress',
                        'v':
                        'MSDI_REG_PCC',
                        't': 'json'
                    },{
                        'n': '负责人',
                        'En': 'PersonInCharge',
                        'v':
                        'MSDI_SALES_MANAGER',
                        't': 'json'
                    },{
                        'n': '注册地址',
                        'En': 'RegisteredAddress',
                        'v':
                        'MSDI_REG_ADDRESS',
                        't': 'json'
                    },{
                        'n': '客户服务（投诉）电话',
                        'En': 'CustomerServerTel',
                        'v':
                        'MSDI_CS_TEL',
                        't': 'json'
                    },{
                        'n': '所在地证监局投诉电话',
                        'En': 'SFC_Tel',
                        'v':
                        'MSDI_ZJJ_COMPLAINTS_TEL',
                        't': 'json'
                    },{
                        'n': '营业部电邮',
                        'En': 'EmailAddress',
                        'v':
                        'MSDI_EMAIL',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'json',
                        'v': 'totalPages',
                        },
                method='POST',
                callback=self.sac_department_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:'http://jg.sac.net.cn/pages/publicity/resource!list.action',
                bodyfunc=lambda page,response=None:urllib.parse.urlencode({'filter_LIKES_msdi_name':'',
                                            'filter_LIKES_msdi_reg_address':'',
                                            'filter_EQS_aoi_id':response.meta['AOI_ID'],
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_SALES_DEPT',
                                            'page.sqlCKey':'SIZE_SALES_DEPT',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':str(page),
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'}),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='json')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sac_Practitioners_info(self, response):

        _configs = [{   
                'list': {
                    'n': '',
                    'v': 'result',    
                    't': 'json',
                    'db': 'Sac.Sac_ComPractitioners',
                    'keys': ['HTML_ID','Name','Position','PracticeTime','Gender'],
                    'check': 'HTML_ID',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'meta'
                    },{
                        'n': '姓名',
                        'En': 'Name',
                        'v':
                        'MPTI_NAME',
                        't': 'json'
                    },{
                        'n': '现任职务',
                        'En': 'Position',
                        'v':
                        'MPTI_CURRENT_POSITION',
                        't': 'json'
                    },{
                        'n': '性别',
                        'En': 'Gender',
                        'v':
                        'GC_ID',
                        't': 'json'
                    },{
                        'n': '执业时间',
                        'En': 'PracticeTime',
                        'v':
                        'MPTI_PRACTICE_TIME',
                        't': 'json'
                    },{
                        'n': '备注',
                        'En': 'Remark',
                        'v':
                        'MPTI_REMARK',
                        't': 'json'
                    },{
                        'n': '资格证书',
                        'En': 'CertNo',
                        'v':
                        'MPTI_QUALIFICATION_NO',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                method='POST',
                config={'t': 'json',
                        'v': 'totalPages',
                        },
                callback=self.sac_Practitioners_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:response.url,
                bodyfunc=lambda page,response=None:urllib.parse.urlencode({'filter_EQS_aoi_id':response.meta['AOI_ID'],
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_PRACTITIONERS',
                                            'page.sqlCKey':'SIZE_PRACTITONERS',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':str(page),
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'}),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='json')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sac_supervisor_info(self, response):
        _configs = [{   
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_ComSupervisor',
                    'keys': ['HTML_ID','Name','Position','StartDate'],
                    'check': 'HTML_ID',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'meta'
                    },{
                        'n': '姓名',
                        'En': 'Name',
                        'v':
                        'EI_NAME',
                        't': 'json'
                    },{
                        'n': '现任职务',
                        'En': 'Position',
                        'v':
                        'EI_CURRENT_POSITION',
                        't': 'json'
                    },{
                        'n': '性别',
                        'En': 'Gender',
                        'v':
                        'GC_ID',
                        't': 'json'
                    },{
                        'n': '中国注册会计师资格证书号码',
                        'En': 'AccountantCert',
                        'v':
                        'EI_ACCOUNTANTS_NO',
                        't': 'json'
                    },{
                        'n': '是否通过证券评级业务高级管理人员资质测试',
                        'En': 'ISPASS_SENIOR_MANAGEMENT',
                        'v':
                        'EI_ISPASS_SENIOR_MANAGEMENT',
                        't': 'json'
                    },{
                        'n': '任职起始时间',
                        'En': 'StartDate',
                        'v':
                        'EI_PRACTITIONERS_START_DATE',
                        't': 'json'
                    },{
                        'n': '证券从业人员证书号码',
                        'En': 'SECURITIES_PROFESSIONALS',
                        'v':
                        'EI_SECURITIES_PROFESSIONALS',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sac_com_member_info(self, response):
        _configs = [{   
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_ComMember',
                    'keys': ['HTML_ID'],
                    'check': 'HTML_ID',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'json'
                    },{
                        'n': '会员ID',
                        'En': 'MemberId',
                        'v':
                        'AOI_MEMBER_NO',
                        't': 'json'
                    },{
                        'n': '机构序号',
                        'En': 'ComNo',
                        'v':
                        'AOI_NO',
                        't': 'json'
                    },{
                        'n': '社会统一信用代码',
                        'En': 'UnifiedSocialCreditCode',
                        'v':
                        'AOI_ORG_NO',
                        't': 'json'
                    },{
                        'n': '会员类别',
                        'En': 'MemberCategory',
                        'v':
                        'OPC_NAME',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sac_com_basic_info(self, response):
        _configs = [{   
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_ComBasic',
                    'keys': ['HTML_ID'],
                    'check': 'HTML_ID',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'json'
                    },{
                        'n': 'ASC_ID',
                        'En': 'ASC_ID',
                        'v':
                        'ASC_ID',
                        't': 'json'
                    },{
                        'n': 'IS_CLOSED',
                        'En': 'IS_CLOSED',
                        'v':
                        'IS_CLOSED',
                        't': 'json'
                    },{
                        'n': '中文全称',
                        'En': 'ComName',
                        'v':
                        'MRI_CHINESE_NAME',
                        't': 'json'
                    },{
                        'n': '中文简称',
                        'En': 'ComShortName',
                        'v':
                        'MRI_CHINESE_ABBREVIATION',
                        't': 'json'
                    },{
                        'n': '注册地址',
                        'En': 'Address',
                        'v':
                        'MRI_INFO_REG',
                        't': 'json'
                    },{
                        'n': '投诉电话',
                        'En': 'COMPLAINTS_TEL',
                        'v':
                        'MRI_COMPLAINTS_TEL',
                        't': 'json'
                    },{
                        'n': '公司邮箱',
                        'En': 'OfficeEmailAddress',
                        'v':
                        'MRI_COM_EMAIL',
                        't': 'json'
                    },{
                        'n': '公司历史',
                        'En': 'ComHistory',
                        'v':
                        'MRI_COM_HISTORY',
                        't': 'json'
                    },{
                        'n': '法人代表',
                        'En': 'NameOfLegalRepresentative',
                        'v':
                        'MRI_LEGAL_REPRESENTATIVE',
                        't': 'json'
                    },{
                        'n': '公司网址',
                        'En': 'ComWebsite',
                        'v':
                        'MRI_COM_WEBSITE',
                        't': 'json'
                    },{
                        'n': '信用',
                        'En': 'MRI_CREDIT_EMP_NUM',
                        'v':
                        'MRI_CREDIT_EMP_NUML',
                        't': 'json'
                    },{
                        'n': '信用支付',
                        'En': 'MRI_CREDIT_PAID_IN_CAPITAL',
                        'v':
                        'MRI_CREDIT_PAID_IN_CAPITAL',
                        't': 'json'
                    },{
                        'n': '客户服务（投诉）电话',
                        'En': 'CustomerServerTel',
                        'v':
                        'MRI_CUSTOMER_SERVICE_TEL',
                        't': 'json'
                    },{
                        'n': '英文简称',
                        'En': 'ComEshortName',
                        'v':
                        'MRI_ENGLISH_ABBREVIATION',
                        't': 'json'
                    },{
                        'n': '英文名称',
                        'En': 'ComEnglishName',
                        'v':
                        'MRI_ENGLISH_NAME',
                        't': 'json'
                    },{
                        'n': '传真',
                        'En': 'OfficeFaxNumber',
                        'v':
                        'MRI_FAX',
                        't': 'json'
                    },{
                        'n': '成立日期',
                        'En': 'SetupTime',
                        'v':
                        'MRI_FOUND_DATE',
                        't': 'json'
                    },{
                        'n': '总经理',
                        'En': 'GeneralManager',
                        'v':
                        'MRI_GENERAL_MANAGER',
                        't': 'json'
                    },{
                        'n': '详细注册地址',
                        'En': 'RegisteredAddress',
                        'v':
                        'MRI_INFO_REG',
                        't': 'json'
                    },{
                        'n': '是否上市',
                        'En': 'IsListed',
                        'v':
                        'MRI_IS_LISTED',
                        't': 'json'
                    },{
                        'n': '业务资格许可证编号',
                        'En': 'LicenceNumber',
                        'v':
                        'MRI_LICENSE_CODE',
                        't': 'json'
                    },{
                        'n': '管理',
                        'En': 'Manager',
                        'v':
                        'MRI_MANAGER',
                        't': 'json'
                    },{
                        'n': '净资产',
                        'En': 'NetAssets',
                        'v':
                        'MRI_NET_ASSETS',
                        't': 'json'
                    },{
                        'n': '办公地址',
                        'En': 'OfficeAddress',
                        'v':
                        'MRI_OFFICE_ADDRESS',
                        't': 'json'
                    },{
                        'n': '公司邮箱',
                        'En': 'OfficeZipCode',
                        'v':
                        'MRI_OFFICE_ZIP_CODE',
                        't': 'json'
                    },{
                        'n': '社会统一信用代码',
                        'En': 'UnifiedSocialCreditCode',
                        'v':
                        'MRI_ORG_CODE',
                        't': 'json'
                    },{
                        'n': '组织结构',
                        'En': 'Organ',
                        'v':
                        'MRI_ORG_STUCTURE',
                        't': 'json'
                    },{
                        'n': '其他',
                        'En': 'Other',
                        'v':
                        'MRI_QI_TA',
                        't': 'json'
                    },{
                        'n': '注册资本',
                        'En': 'RegisteredCapital',
                        'v':
                        'MRI_REG_CAPITAL',
                        't': 'json'
                    },{
                        'n': '注册ID-对应证书ID',
                        'En': 'RegisteredID',
                        'v':
                        'MRI_REG_ID',
                        't': 'json'
                    },{
                        'n': 'MRI_REG_VER_ID',
                        'En': 'MRI_REG_VER_ID',
                        'v':
                        'MRI_REG_VER_ID',
                        't': 'json'
                    },{
                        'n': '注册地邮编',
                        'En': 'RegisteredZipCode',
                        'v':
                        'MRI_REG_ZIP_CODE',
                        't': 'json'
                    },{
                        'n': '备注',
                        'En': 'ReMark',
                        'v':
                        'MRI_REMARK',
                        't': 'json'
                    },{
                        'n': '销售部数量',
                        'En': 'SalseDeptNum',
                        'v':
                        'MRI_SALES_DEPT_NUM',
                        't': 'json'
                    },{
                        'n': '证券业务',
                        'En': 'SECURITIES_BUSINESS',
                        'v':
                        'MRI_SECURITIES_BUSINESS',
                        't': 'json'
                    },{
                        'n': '证券业务许可证',
                        'En': 'SECURITIES_LicenceNumber',
                        'v':
                        'MRI_SECURITIES_BUSINESS_CODE',
                        't': 'json'
                    },{
                        'n': '证券资格',
                        'En': 'SECURITIES_ELIGIBLE',
                        'v':
                        'MRI_SECURITIES_ELIGIBLE',
                        't': 'json'
                    },{
                        'n': '上市地代码',
                        'En': 'ListedAreaCode',
                        'v':
                        'MRI_SHANG_SHI_CODE',
                        't': 'json'
                    },{
                        'n': '上市地',
                        'En': 'ListedArea',
                        'v':
                        'MRI_SHANG_SHI_DI',
                        't': 'json'
                    },{
                        'n': '证监局监督电话',
                        'En': 'SFC_Tel',
                        'v':
                        'MRI_ZJJ_TEL',
                        't': 'json'
                    },{
                        'n': '地区代码',
                        'En': 'AreaCode',
                        'v':
                        'SAC_ID',
                        't': 'json'
                    },{
                        'n': '地区',
                        'En': 'AreaName',
                        'v':
                        'SAC_NAME',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item


    @SpiderHelp.check_response
    def sac_com_Qualificatio_certificate_list1(self,response):
        # 公司-概况
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_Com_Qualificatio',
                    'keys': ['HTML_ID'],
                    'check': 'HTML_ID',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': '机构ID',
                        'En': 'HTML_ID',
                        'v':
                        'AOI_ID',
                        't': 'json'
                    },{
                        'n': '机构名称',
                        'En': 'ComName',
                        'v':
                        'AOI_NAME',
                        't': 'json'
                    },{
                        'n': '从业人员数',
                        'En': 'EmployeeNumbers',
                        'v':
                        'PR_COUNT_PERSON',
                        't': 'json'
                    },{
                        'n': '一般证券业务资格数',
                        'En': 'GeneralQualification',
                        'v':
                        'PTI0PERSON',
                        't': 'json'
                    },{
                        'n': '证券投资咨询业务(其他)',
                        'En': 'Other',
                        'v':
                        'PTI1PERSON',
                        't': 'json'
                    },{
                        'n': '证券经纪业务营销',
                        'En': 'BusinessMarketing',
                        'v':
                        'PTI2PERSON',
                        't': 'json'
                    },{
                        'n': '证券经纪人',
                        'En': 'Financingers',
                        'v':
                        'PTI3PERSON',
                        't': 'json'
                    },{
                        'n': '证券投资咨询业务(分析师)',
                        'En': 'Analyst',
                        'v':
                        'PTI4PERSON',
                        't': 'json'
                    },{
                        'n': '证券投资咨询业务(投资顾问)',
                        'En': 'InvestmentAdvisor',
                        'v':
                        'PTI5PERSON',
                        't': 'json'
                    },{
                        'n': '保荐代表人',
                        'En': 'SponsorRepresentative',
                        'v':
                        'PTI6PERSON',
                        't': 'json'
                    },{
                        'n': '投资主办人',
                        'En': 'InvestmentSponsor',
                        'v':
                        'PTI7PERSON',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        # # 列表页
        JS = execjs.eval(response.text)
        for sel in JS:
            AOI_ID = sel['AOI_ID']
            totalpage = int(sel['PR_COUNT_PERSON'])//100 + 1
            yield scrapy.Request('http://person.sac.net.cn/pages/registration/train-line-register!gsUDDIsearch.action',
                headers=self.default_header,
                method='POST',
                priority=1000,
                body=urllib.parse.urlencode({'ORDER': 'ASC',
                                     'ORDERNAME': 'PP#PTI_ID,PP#PPP_NAME',
                                     'filter_EQS_AOI_ID': AOI_ID,
                                     'filter_GTS_RNUM': '0',
                                     'filter_LES_ROWNUM': '100',
                                     'filter_EQS_PTI_ID':'',
                                     'sqlkey': 'registration',
                                     'sqlval': 'SEARCH_FINISH_PUBLICITY'}),
                meta={'AOI_ID': AOI_ID,'totalpage': totalpage,'proxys':True},
                callback=self.sac_com_Qualificatio_certificate_list2)

    @SpiderHelp.check_response
    def sac_com_Qualificatio_certificate_list2(self, response):
        # 公司-个人从业资格列表
        # 从业基础信息
        url = 'http://person.sac.net.cn/pages/registration/train-line-register!gsUDDIsearch.action'
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_PersonQualificatioCertificate',
                    'keys': ['MD5'],
                    'check': 'MD5',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': 'MD5',
                        'En': 'MD5',
                        'v':
                        'PPP_ID',
                        't': 'json'
                    },{
                        'n': '注册变更记录',
                        'En': 'Change',
                        'v':
                        'COUNTCER',
                        't': 'json'
                    },{
                        'n': '诚信记录',
                        'En': 'Credit',
                        'v':
                        'COUNTCX',
                        't': 'json'
                    },{
                        'n': '证书类别',
                        'En': 'CeryCategory',
                        'v':
                        'CTI_NAME',#未知
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            _item = item.copy()
            yield scrapy.Request(url,
                method='POST',
                headers=self.default_header,
                body=urllib.parse.urlencode({'filter_EQS_PPP_ID':_item['result']['MD5'],
                    'sqlkey':'registration',
                    'sqlval':'SD_A02Leiirkmuexe_b9ID'}),
                priority=1500,
                meta={'item':_item,'proxys':True},
                callback=self.Sac_person_jumps,
                )



        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex0',
                        'v': 'RNUM\s*?:\s*?\d00',
                        },
                callback=self.pedaily_Investment_event_list,
                headers=self.default_header,
                method='POST',
                urlfunc=lambda page,response=None:'http://person.sac.net.cn/pages/registration/train-line-register!orderSearch.action',
                bodyfunc=lambda page, response=None:urllib.parse.urlencode({'ORDER': 'ASC',
                                     'ORDERNAME': 'PP#PTI_ID,PP#PPP_NAME',
                                     'filter_EQS_AOI_ID': response.meta['AOI_ID'],
                                     'filter_GTS_RNUM': page * 100 - 100,
                                     'filter_LES_ROWNUM': page * 100,
                                     'filter_EQS_PTI_ID':'',
                                     'sqlkey': 'registration',
                                     'sqlval': 'SEARCH_FINISH_PUBLICITY'}),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                readpage=20,
                meta={'proxys':True},
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def Sac_person_jumps(self, response):
        # 本页获取明文ID
        JS = execjs.eval(response.text)
        if JS:
            url = 'http://person.sac.net.cn/pages/registration/train-line-register!gsUDDIsearch.action'
            RPI_ID = JS[0]['RPI_ID']
            item = response.meta['item']['result']
            item['HTML_ID'] = RPI_ID
            item['proxys'] = True
            data1 = {'filter_EQS_RH#RPI_ID':RPI_ID,
                     'sqlkey':'registration',
                     'sqlval':'SEARCH_LIST_BY_PERSON'}
            data2 = {'filter_EQS_RPI_ID':RPI_ID,
                      'sqlkey':'registration',
                      'sqlval':'SELECT_PERSON_INFO'}
            # 从业信息
            yield scrapy.Request(url,
                headers=self.default_header,
                method='POST',
                meta={'proxys': True,**item},
                body=urllib.parse.urlencode(data2),
                priority=2000,
                callback=self.sac_person_Qualification)

            # 从业变更信息
            yield scrapy.Request(url,
                headers=self.default_header,
                method='POST',
                body=urllib.parse.urlencode(data1),
                priority=2000,
                meta={'proxys': True,**item},
                callback=self.sac_person_Qualification_change)

    @SpiderHelp.check_response
    def sac_person_Qualification(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_PersonQualificatioCertificate',
                    'keys': ['HTML_ID'],
                    'check': 'Name',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': 'HTML_ID',
                        'En': 'HTML_ID',
                        'v':
                        'HTML_ID',
                        't': 'meta'
                    },{
                        'n': '姓名',
                        'En': 'Name',
                        'v':
                        'RPI_NAME',
                        't': 'json'
                    },{
                        'n': '性别',
                        'En': 'Gender',
                        'v':
                        'SCO_NAME',
                        't': 'json'
                    },{
                        'n': 'image',
                        'En': 'Image',
                        'v':
                        'RPI_PHOTO_PATH',
                        't': 'json'
                    },{
                        'n': '执业岗位',
                        'En': 'Position',
                        'v':
                        'PTI_NAME',
                        't': 'json'
                    },{
                        'n': '执业机构',
                        'En': 'PractisingInstitution',
                        'v':
                        'AOI_NAME',
                        't': 'json'
                    },{
                        'n': '执业机构ID',
                        'En': 'ComID',
                        'v':
                        'AOI_ID',
                        't': 'json'
                    },{
                        'n': '证书编号',
                        'En': 'CertNo',
                        'v':
                        'CER_NUM',
                        't': 'json'
                    },{
                        'n': '所在部门',
                        'En': 'Department',
                        'v':
                        'ADI_NAME',
                        't': 'json'
                    },{
                        'n': '注册变更记录',
                        'En': 'Change',
                        'v':
                        'Change',
                        't': 'meta'
                    },{
                        'n': '诚信记录',
                        'En': 'Credit',
                        'v':
                        'Credit',
                        't': 'meta'
                    },{
                        'n': '证书类别',
                        'En': 'CeryCategory',
                        'v':
                        'CeryCategory',#未知
                        't': 'meta'
                    },{
                        'n': '学历',
                        'En': 'Education',
                        'v':
                        'ECO_NAME',
                        't': 'json'
                    },{
                        'n': '证书有效截止日期',
                        'En': 'CertEndDate',
                        'v':
                        'ARRIVE_DATE',
                        't': 'json'
                    },{
                        'n': '证书取得日期',
                        'En': 'CertGetDate',
                        'v':
                        'OBTAIN_DATE',
                        't': 'json'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def sac_person_Qualification_change(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '',    
                    't': 'json',
                    'db': 'Sac.Sac_PersonChangeRecord',
                    'keys': ['HTML_ID','CertGetDate'],
                    'check': 'PractisingInstitution',
                    'conn': conn_flag
                },
                'response_type':
                'json',
                'data': [
                    {
                        'n': 'HTML_ID',
                        'En': 'HTML_ID',
                        'v':
                        'HTML_ID',
                        't': 'meta'
                    },{
                        'n': '执业机构',
                        'En': 'PractisingInstitution',
                        'v':
                        'AOI_NAME',
                        't': 'json'
                    },{
                        'n': '证书状态',
                        'En': 'CertState',
                        'v':
                        'CERTC_NAME',
                        't': 'json'
                    },{
                        'n': '证书编号',
                        'En': 'CertNumber',
                        'v':
                        'CER_NUM',
                        't': 'json'
                    },{
                        'n': '取得日期',
                        'En': 'CertGetDate',
                        'v':
                        'OBTAIN_DATE',
                        't': 'json'
                    },{
                        'n': '执业岗位',
                        'En': 'Position',
                        'v':
                        'PTI_NAME',
                        't': 'json'
                    }
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item



    @SpiderHelp.check_response
    def cfa_in(self, response):
        # 期货信息入口列表页
        yield self.request('http://www.cfachina.org/cfainfo/organbaseinfoServlet',
            headers=self.default_header,
            method='POST',
            body=urllib.parse.urlencode({'currentPage':'1',
                'pageSize':'20',
                'all':'organbaseinfo'}),
            redis_flag=True,
            callback=self.cfa_com_list)

    @SpiderHelp.check_response
    def cfa_com_list(self, response):
        '''中国期货业协会--证券公司信息'''
        # 基本情况
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_base_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=organbaseinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 历史情况
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_his_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=organhisinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 分支机构
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_branch_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=organbranchinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 高管人员信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_supervisor_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=supervisorinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 从业人员信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_person_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=personinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 股东信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_shareholder_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=organshareholderinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 诚信记录信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_credit_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=organcreditinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 财务信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_financial_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=organfinancialinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # 次级债信息
        reqs3 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_res',
                                                   'v': '//table//table//tr[position()>1]/td[1]/text()',
                                                   're': '\S+'
                                                   },
                                           callback=self.cfa_com_subdebt_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page, response=None: 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=%s&currentPage=1&pageSize=20&selectType=subdebtmonthinfo' % page,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs3:
            yield req

        # '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_list,
                headers=self.default_header,
                method="POST",
                urlfunc=lambda page,response=None:'http://www.cfachina.org/cfainfo/organbaseinfoServlet',
                bodyfunc=lambda page,response=None:urllib.parse.urlencode({'currentPage':str(page),
                                                                            'pageSize':'20',
                                                                            'all':'organbaseinfo'}),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_base_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComBasic',
                    'keys': ['ComName'],
                    'check': 'ComName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '公司名称',
                        'En': 'ComName',
                        'v':
                        './/td[contains(text(),"公司名称")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '许可证号',
                        'En': 'LicenceNumber',
                        'v':
                        './/td[contains(text(),"许可证号")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '经营范围', 
                        'En': 'ScopeOfoperation',
                        'v':
                        './/td[contains(text(),"经营范围")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '金融期货业务资格类别', 
                        'En': 'QualificationCategory',
                        'v':
                        './/td[contains(text(),"资格类别")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '取得会员资格的期货交易所名称', 
                        'En': 'FuturesExchange',
                        'v':
                        './/td[contains(text(),"期货交易所名称")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '注册资本(元)', 
                        'En': 'RegisteredCapital',
                        'v':
                        './/td[contains(text(),"注册资本")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '公司住所', 
                        'En': 'Address',
                        'v':
                        './/td[contains(text(),"公司住所")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '法定代表人', 
                        'En': 'NameOfLegalRepresentative',
                        'v':
                        './/td[contains(text(),"法定代表人")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '办公地址和邮编', 
                        'En': 'OfficeAddress_ZipCode',
                        'v':
                        './/td[contains(text(),"办公地址和邮编")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '客户服务及投诉电话', 
                        'En': 'OfficePhoneNumber',
                        'v':
                        './/td[contains(text(),"客户服务及投诉电话")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '公司网址网址', 
                        'En': 'OfficeWebsite',
                        'v':
                        './/td[contains(text(),"公司网址")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },{
                        'n': '公司电子邮箱', 
                        'En': 'OfficeEmailAddress',
                        'v':
                        './/td[contains(text(),"电子邮箱")]/following-sibling::td/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def cfa_com_his_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComHis',
                    'keys': ['Date', 'HTML_ID','Event'],
                    'check': 'Date',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '时间',
                        'En': 'Date',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '事件简称',
                        'En': 'Event',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '事件内容(200字以内)',
                        'En': 'Content',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_his_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_branch_info(self, response):
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComBranch',
                    'keys': ['BranchName', 'HTML_ID'],
                    'check': 'BranchName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '序号',
                        'En': 'No',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '分支机构名称',
                        'En': 'BranchName',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '所在地',
                        'En': 'AreaName',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '许可证号',
                        'En': 'LicenceNumber',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '设立时间',
                        'En': 'SetTime',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '负责人',
                        'En': 'PersonInCharge',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '客户服务与投诉电话',
                        'En': 'OfficePhoneNumber',
                        'v':
                        './td[7]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '详细地址(邮编)',
                        'En': 'OfficeAddress_ZipCode',
                        'v':
                        './td[8]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '电子邮箱',
                        'En': 'OfficeEmailAddress',
                        'v':
                        './td[9]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_branch_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_supervisor_info(self, response):
        '''高管'''
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComSupervisor',
                    'keys': ['HTML_ID', 'Name','Position','PresentTime'],
                    'check': 'Name',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '姓名',
                        'En': 'Name',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '性别',
                        'En': 'Gender',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '现任职务',
                        'En': 'Position',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '高管资格批准文号',
                        'En': 'ApprovalNumber',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '任现职时间',
                        'En': 'PresentTime',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '其它任职经历(与期货相关)',
                        'En': 'PostExperience',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '备注',
                        'En': 'ReMark',
                        'v':
                        './td[7]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_supervisor_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_person_info(self, response):
        '''从业人员'''
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComPerson',
                    'keys': ['Name', 'HTML_ID','Position','PresentTime'],
                    'check': 'Name',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '姓名',
                        'En': 'Name',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '性别',
                        'En': 'Gender',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '从业资格号',
                        'En': 'QualificationNumber',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '投资咨询从业证书号',
                        'En': 'InvestmentConsultingCert',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '任职部门',
                        'En': 'Department',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '职务',
                        'En': 'Position',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '任现职时间',
                        'En': 'PresentTime',
                        'v':
                        './td[7]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_person_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_shareholder_info(self, response):
        '''股东信息'''
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComShareHolder',
                    'keys': ['ShareholderName', 'HTML_ID'],
                    'check': 'ShareholderName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '股东名称',
                        'En': 'ShareholderName',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '持股比例(%)',
                        'En': 'ShareholdingRatio',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '入股时间',
                        'En': 'ShareTime',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '法定代表人',
                        'En': 'NameOfLegalRepresentative',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '注册资本(元)',
                        'En': 'RegisteredCapital',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '办公地址',
                        'En': 'OfficeAddress',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '公司网址',
                        'En': 'OfficeWebsite',
                        'v':
                        './td[7]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '所属行业',
                        'En': 'Industry',
                        'v':
                        './td[8]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '经济类型',
                        'En': 'EconomicType',
                        'v':
                        './td[9]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '备注',
                        'En': 'ReMark',
                        'v':
                        './td[10]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]

        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_shareholder_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_credit_info(self, response):
        '''诚信记录信息'''
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComCredit',
                    'keys': ['DocumentNumber', 'HTML_ID'],
                    'check': 'Date',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '时间',
                        'En': 'Date',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '类别',
                        'En': 'Category',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '实施机关',
                        'En': 'ImplementationOrgan',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '文号',
                        'En': 'DocumentNumber',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '情况简介(200字以内)',
                        'En': 'BriefIntroduction',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    }
                ]
            }]
            
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_credit_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_financial_info(self, response):
        '''财务信息'''
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComFinancial',
                    'keys': ['Years', 'HTML_ID'],
                    'check': 'Years',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '年份',
                        'En': 'Years',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '净资本 (万元)',
                        'En': 'NetCapital',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '净资产 (万元)',
                        'En': 'NetAssets',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '权益总额 (万元)',
                        'En': 'TotalRights',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '手续费收入 (万元)',
                        'En': 'FeeIncome',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '净利润 (万元)',
                        'En': 'NetProfit',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '主审会计事务所',
                        'En': 'ChiefAuditAccountingFirm',
                        'v':
                        './td[7]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '审计意见类型',
                        'En': 'TypeOfAuditOpinion',
                        'v':
                        './td[8]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '备注',
                        'En': 'ReMark',
                        'v':
                        './td[9]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
            
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_financial_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def cfa_com_subdebt_info(self, response):
        '''次级债信息'''
        _configs = [{
                'list': {
                    'n': '',
                    'v': '//div[@class="gst_mcleib"]/table//tr[position()>1]',    
                    't': 'xpath',
                    'db': 'Cfa.Cfa_ComSubdebt',
                    'keys': ['DebtName', 'HTML_ID'],
                    'check': 'DebtName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': 'HTML_ID', #   http://zdb.pedaily.cn/inv/show{HTML_ID}/
                        'En': 'HTML_ID',
                        'v':
                        'organid=\W?(\w+)\w?',
                        't': 'url_re'
                    },{
                        'n': '债务名称',
                        'En': 'DebtName',
                        'v':
                        './td[1]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '债务性质',
                        'En': 'DebtNature',
                        'v':
                        './td[2]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '债务规模',
                        'En': 'DebtScale',
                        'v':
                        './td[3]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '合同生效日',
                        'En': 'ContractDate',
                        'v':
                        './td[4]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '到期偿还日期',
                        'En': 'ReimbursementDate',
                        'v':
                        './td[5]/text()',
                        't': 'xpath_first'
                    },{
                        'n': '备注',
                        'En': 'ReMark',
                        'v':
                        './td[6]/text()',
                        't': 'xpath_first'
                    },
                ]
            }]
            
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'xpath_first',
                        'v': '//ul[@class="yema"]/li[last()]/span/text()',
                        },
                callback=self.cfa_com_subdebt_info,
                headers=self.default_header,
                urlfunc=lambda page,response=None:re.sub('Page=(\d+)','Page=%s' % page,response.url),
                divmod=20,
                redis_conn=self.r,
                redis_flag=True,
                readpage=128,
                response_type='xpath')
        for req in reqs:
            yield req
        


if __name__ == '__main__':
    # put起始url到数据库
    SinaspiderSpider.put_redis()
