# -*- coding: utf-8 -*-
import scrapy
import os
import sys
import urllib.parse
import re
import requests
import json
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
'''
redis数据库使用FOFI先进后出的规则 对url进行队列选择
'''

class CreditspiderSpider(_RedisSpider, SpiderHelp):  #,scrapy.Spider
    
    '''
    采用分布式,开启方式 调用_start_requests方法执行便可
    '''
    name = "fjcreditspider"
    state = {}
    redis_flag=True
    redis_key = 'beijing:starturls'
    signel = 1
    host = '10.1.18.35'
    custom_settings = {
        # 'DOWNLOADER_MIDDLEWARES': 
        # {
        #     # 启用中间件
        #     'CreditChina.middlewares.RotateUserAgentMiddleware': 401,
        #     # 启用代理
        #     'CreditChina.middlewares.ProxyMiddleware': 700,
        # },
        # 最大并发
        'CONCURRENT_REQUESTS': 32,
        # 单ip最大并发
        # 'CONCURRENT_REQUESTS_PER_IP': 16,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        #下载延迟
        'DOWNLOAD_DELAY': 0.1,
        # 爬虫策略
        'DEPTH_PRIORITY': 1,
        # 允许的status
        'HTTPERROR_ALLOWED_CODES': [404, 502, 500, 504],
    }
    进度 = ['福建','黑龙江','山东','江西','海南','江苏','海淀','河北','西藏','浙江','吉林','山西','广西','新疆','北京']
    进度2 = ['广州','惠州','郑州','','','1178345']
    start_urls = (
        # '''福建信用''', # 完成
        # # 福建失信被执行人
        # 'http://www.fjcredit.gov.cn/creditsearch.list.dhtml?source_id=100&kw=&page=1', # 不封IP
        # # 福建异常经营企业
        # 'http://www.fjcredit.gov.cn/creditsearch.list.dhtml?source_id=98&kw=&page=1', # 不封IP
        # # 福建 行政许可
        # 'http://www.fjcredit.gov.cn/creditsearch.permissionList.phtml?id=&keyword=&page=1', # 不封IP
        # # 福建行政处罚
        # 'http://www.fjcredit.gov.cn/creditsearch.punishmentList.phtml?id=&keyword=&page=1', # 不封IP
        # # 福建企业基础信息
        # 'http://www.fjcredit.gov.cn/creditsearch.list.dhtml?source_id=1&kw=&page=1', # 不封IP
        # '''黑龙江信用''',# 未跑
        # 黑龙江企业基本信息
        # 'http://www.hljcredit.gov.cn/WebCreditQueryService.do?doEntSearch',  # 会封IP  
        # # '''江西信用''' 
        # # 江西企业基础信息
        # 'http://www.creditjx.gov.cn/DataQuery/company/listNew.json',
        # # 江西重点人群信息  -- 暂且只跑律师信息
        # 'http://www.creditjx.gov.cn/DataQuery/website/zrr/queryZrrList.json',
        # '''信用新疆''',
        # # '''山东基本信息 
        # {http://www.creditsd.gov.cn/creditsearch.listcreditsd.dhtml?page=123029  先去社会统一码获取统一码，
        # # http://www.creditsd.gov.cn/creditsearch.corlistace.dhtml?kw=91370982MA3BXJHG3T 拿到验证码 查询基础页url
        # # 再获取企业基础信息
        # # http://www.creditsd.gov.cn/creditsearch.cordetailace.dhtml?id=151_b823940064686034ac2299a0eb1c5f76}'''
        # 'http://www.creditsd.gov.cn/creditsearch.listcreditsd.dhtml?page=1',
        #  失信被执行人
        # 'http://www.creditsd.gov.cn/creditsearch.list.dhtml?source_id=165&kw=&page=1',
        # '''海南信用''',
        # 海南基础信息
        # 页面需要replace
        # 'http://xyhn.hainan.gov.cn/JRBWeb/IntegratedManger/HnxykQyxxJbxxMainController.do?reqCode=VCreditquery&qymc=&pageNo=1&pageNumber=100', 
        # '信用海淀',
        # 'http://xinyong.bjhd.gov.cn/compan/companList!companList.action', # 运行缓慢
        # '''信用江苏''',
        # 'http://www.jscredit.gov.cn/credit/p/common/ucc/webPageList.do?pageSize=100&currPage=1',   
        # 失信被执行人
        # 'http://www.jscredit.gov.cn/credit/p/common/dishonesty/webPageList.do?pageSize=100&currPage=1',
        # 行政许可
        # 'http://www.jscredit.gov.cn/credit/p/two_publicity/webPageList.do?_type=al&webInvokeCondition=%7B%22queryCondition%22%3A%5B%7B%22name%22%3A%22XK_XDR%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22XK_XDR_SHXYM%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22XK_XDR_ZDM%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22XK_XDR_GSDJ%22%2C%22value%22%3A%22%22%7D%5D%7D&currPage=1&pageSize=100',
        # 行政处罚
        # 'http://www.jscredit.gov.cn/credit/p/two_publicity/webPageList.do?_type=ap&webInvokeCondition=%7B%22queryCondition%22%3A%5B%7B%22name%22%3A%22CF_XDR_MC%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22CF_XDR_SHXYM%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22CF_XDR_ZDM%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22CF_XDR_GSDJ%22%2C%22value%22%3A%22%22%7D%5D%7D&currPage=1&pageSize=100',
        # '''信用西藏''',
        # 西藏基础信息
        # 'http://www.creditxizang.gov.cn/xyxz/legalQuery/legalQuery.do?entName=&legalStatus=&legalType=',
        # '''信用河北'''
        # 基础信息
        # 'http://123.182.226.146:8082/was5/web/search?page=1&channelid=260465&orderby=RELEVANCE&perpage=100&outlinepage=10&searchscope=&timescope=&timescopecolumn=&orderby=RELEVANCE&andsen=&total=&orsen=&exclude=',
        # 行政许可
        # 'http://www.credithebei.gov.cn:8082/was5/web/search?page=1&channelid=284126&orderby=RELEVANCE&perpage=100',
        #行政处罚
        # 'http://www.credithebei.gov.cn:8082/was5/web/search?page=1&channelid=271661&orderby=RELEVANCE&perpage=100',
        # '''信用吉林'''
        # 基础信息
        # 'http://36.48.62.24:8704/DataQuery/company/list.json',  # 翻页有问题 多次重试 会封IP
        # '''信用浙江'''  #
        # 'http://www.zjcredit.gov.cn/page/corporation/enterpriseSearchProxy.jsp?startrecord=1&endrecord=100&perpage=100&totalRecord=1936006',
        # '''信用广西'''
        # 'http://www.gxcredit.gov.cn/getXyxxList.jspx?search_type=1&key_word=&page=1',
        # '''信用山西'''
        # 'http://www.creditsx.gov.cn/list-L.jspx',
        # '''广东信用'''
        # 广东律师资格证书 可以从广东信用网抓取
        #    '''广州'''
        # 'https://credit1.gz.gov.cn/creditPublic/creditCodeQuery',
        #   '''惠州'''  还有律所信息
        # 'http://xyhz.huizhou.gov.cn/html/dmgs_qyList.shtml?pageNo=1',
        # '''信用河北'''
        # 郑州基本信息
        # 'http://124.239.190.162:81/WebZhglSJZApp/a/xygs/xycx',
        # '''信用新疆'''
        # 'http://www.creditxj.gov.cn/legalQuery/findLegalList.do?regCode=&dataNumber=10&JGMC=&FDDBR=',
        # '''信用四川'''
        # 成都
        # 'https://www.cdcredit.gov.cn/dr/getCreditCodeList.do',
        #   '''信用北京'''
        'http://cxcj.creditbj.gov.cn/xyData/front/search/detail.shtml?typeId=2&catalog=xybj_data_bjfr_gs_ent&id=21568978',
                
        # '''信用重庆'''
        # 'http://www.xycq.gov.cn/html/query/code/list.html',
        # '''信用湖北'''
        # 'http://www.hbcredit.gov.cn/credithb/opensearch/index.html',
        # '''信用湖南'''
        #  这里通过搜索的方式 搜索公司名称带有公字的企业
        # 'http://www.credithunan.gov.cn/page/corporation/enterpriseList.jsp',
        # '''信用贵州'''
        # 'http://www.gzcredit.gov.cn/Service/CreditService.asmx/searchOrgWithPage',

        )
    
    def open_spider(self, spider):
        self.r = RedisHelp(self)

    def __init__(self, _job=None,**kwargs):
        # 获取本爬虫redis_key
        super(CreditspiderSpider,self).__init__(**kwargs)

    def __str__(self): 
        return 'CreditspiderSpider'

    

    def _start_requests(self):
        req = []
        for url in self.start_urls:
            if url == 'http://www.fjcredit.gov.cn/creditsearch.list.dhtml?source_id=100&kw=&page=1':
                req.append(self.request(
                    url,
                    redis_flag=REDISFLAG,
                    callback=self.fj_discredit))
            elif url == 'http://www.fjcredit.gov.cn/creditsearch.list.dhtml?source_id=98&kw=&page=1':
                req.append(self.request(
                    url,
                    redis_flag=REDISFLAG,
                    callback=self.fj_abnormal_operation))
            elif url == 'http://www.fjcredit.gov.cn/creditsearch.permissionList.phtml?id=&keyword=&page=1':
                req.append(self.request(url,
                    callback=self.fj_administrative_licensing))
            elif url == 'http://www.fjcredit.gov.cn/creditsearch.punishmentList.phtml?id=&keyword=&page=1':
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    callback=self.fj_administrative_sanction))
            elif url == 'http://www.fjcredit.gov.cn/creditsearch.list.dhtml?source_id=1&kw=&page=1':
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    callback=self.fj_basic_info)) 
            elif url == 'http://www.hljcredit.gov.cn/WebCreditQueryService.do?doEntSearch':
                data = urllib.parse.urlencode({'qymcGs':'',
                                                'uniscid':'',
                                                'frdbGs':'',
                                                'curPageNO':'1',
                                                'randD':''})
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    method='POST',
                    body=data,
                    callback=self.hlj_basic_info)) # 约400W数据

            elif url == 'http://www.creditjx.gov.cn/DataQuery/company/listNew.json':
                data = urllib.parse.urlencode(  {'page':'1',
                                                'pageSize':'1000',# 可修正
                                                'cxnr':'',
                                                'cxfs':'',})
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    method='POST',
                    body=data,
                    callback=self.jx_basic_info)) # 约400W数据
            elif url == 'http://www.creditjx.gov.cn/DataQuery/website/zrr/queryZrrList.json':
                data = urllib.parse.urlencode({'enTableName':'SFT_LSZYZGZXX_SFT',#执业类别  有11种类别
                        'searchContent':'',# 查询字段
                        'rownum':'10000',  # 限制数字
                        'page':'1',#页面
                        'pageSize':'10000'}) # 每页显示数量)
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    method='POST',
                    body=data,
                    callback=self.jx_lawyer_info)) # 约5000数据
            elif url == 'http://www.creditxj.gov.cn/legalQuery/legalQuery.do?entName=&legalStatus=&legalType=1&type=0&searchKey=&searchType=&':
                data = urllib.parse.urlencode({'pageNum':'1', #页面参数
                                                'numPerPage':'10', #每页查询限制
                                                'orderField':'',
                                                'orderDirection':'',
                                                'prePage':'1', #之前页面-1  伪造为page-2 大于等于1
                                                'nextPage':'3', #之前页面+1 伪造为page
                                                'ttPage':'64791'})
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    method='POST',
                    body=data,
                    callback=self.xz_basic_info)) # 约64W数据
            elif url == 'http://www.creditsd.gov.cn/creditsearch.listcreditsd.dhtml?page=1':
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    callback=self.sd_basic_info)) 
            elif url == 'http://xyhn.hainan.gov.cn/JRBWeb/IntegratedManger/HnxykQyxxJbxxMainController.do?reqCode=VCreditquery&qymc=&pageNo=1&pageNumber=100':
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    callback=self.hainan_basic_info)) 
            elif url == 'http://xinyong.bjhd.gov.cn/compan/companList!companList.action':
                data = urllib.parse.urlencode({'name':'请输入企业信息（如：名称、企业组织机构代码、工商注册码）',
                                    'types':'0',
                                    'page.total':'500000',
                                    'page.perPage':'500000',
                                    'page.index':'1'})
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    method='POST',
                    body=data,
                    headers=self.headers_update(self.default_header,{'X-Requested-With': 'XMLHttpRequest','Referer':'http://xinyong.bjhd.gov.cn/compan/companList!companIndex.action'}),
                    callback=self.haidian_basic_info)) 
            elif url == 'http://www.jscredit.gov.cn/credit/p/common/ucc/webPageList.do?pageSize=100&currPage=1':
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    callback=self.js_basic_info))
            elif url == 'http://www.jscredit.gov.cn/credit/p/common/dishonesty/webPageList.do?pageSize=100&currPage=1':
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    callback=self.js_discredit_executor))
            elif url == 'http://www.jscredit.gov.cn/credit/p/two_publicity/webPageList.do?_type=al&webInvokeCondition=%7B%22queryCondition%22%3A%5B%7B%22name%22%3A%22XK_XDR%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22XK_XDR_SHXYM%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22XK_XDR_ZDM%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22XK_XDR_GSDJ%22%2C%22value%22%3A%22%22%7D%5D%7D&currPage=1&pageSize=100':
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    callback=self.js_administrative_licensing))
            elif url == 'http://www.jscredit.gov.cn/credit/p/two_publicity/webPageList.do?_type=ap&webInvokeCondition=%7B%22queryCondition%22%3A%5B%7B%22name%22%3A%22CF_XDR_MC%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22CF_XDR_SHXYM%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22CF_XDR_ZDM%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22CF_XDR_GSDJ%22%2C%22value%22%3A%22%22%7D%5D%7D&currPage=1&pageSize=100':
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    callback=self.js_administrative_sanction))
            elif url == 'http://www.creditxizang.gov.cn/xyxz/legalQuery/legalQuery.do?entName=&legalStatus=&legalType=':
                data = urllib.parse.urlencode({'pageNum':'1',
                                                'numPerPage':'10',
                                                'orderField':'',
                                                'orderDirection':'',
                                                'prePage':'0',
                                                'nextPage':'1',
                                                'ttPage':'15575'})
                req.append(self.request(url,
                    method='POST',
                    body=data,
                    redis_flag=REDISFLAG,
                    callback=self.xz_basic_info))
            elif url == 'http://123.182.226.146:8082/was5/web/search?page=1&channelid=260465&orderby=RELEVANCE&perpage=100&outlinepage=10&searchscope=&timescope=&timescopecolumn=&orderby=RELEVANCE&andsen=&total=&orsen=&exclude=':
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    callback=self.hebei_basic_info))
            elif url == 'http://www.credithebei.gov.cn:8082/was5/web/search?page=1&channelid=284126&orderby=RELEVANCE&perpage=100':
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    callback=self.hebei_administrative_licensing))
            elif url == 'http://www.credithebei.gov.cn:8082/was5/web/search?page=1&channelid=271661&orderby=RELEVANCE&perpage=100':
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    callback=self.hebei_administrative_sanction))
            elif url == 'http://36.48.62.24:8704/DataQuery/company/list.json':
                data = urllib.parse.urlencode({'cxnr':'',
                                                'cxfw':'QYMC-',
                                                'fddbr':'',
                                                'szdq':'',
                                                'hylx':'',
                                                'ztlx':'',
                                                'ztfl':'qy',
                                                'page':'1',
                                                'pageSize':'15'})
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    method='POST',
                    body=data,
                    callback=self.jl_basci_info))
            elif url == 'http://www.zjcredit.gov.cn/page/corporation/enterpriseSearchProxy.jsp?startrecord=1&endrecord=100&perpage=100&totalRecord=1936006':
                       
                data = urllib.parse.urlencode({'id2': 'F043B82C71089F52480A95DA2E34A117A89CB9E41A36AA3FC75C79A0DF224AFD5862594A42006C5F'})
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    method='POST',
                    body=data,
                    callback=self.zj_basci_info))
            elif url == 'http://www.gxcredit.gov.cn/getXyxxList.jspx?search_type=1&key_word=&page=1':
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    method='POST',
                    callback=self.gx_basci_info))
            elif url == 'http://www.creditsx.gov.cn/list-L.jspx':
                data = urllib.parse.urlencode({'pageNo':'1',
                        'creditCorpusCode':'L',
                        'name':'',
                        'lcreditcode':'',
                        'sxly':'',
                        'isquery':'true'})
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    method='POST',
                    body=data,
                    callback=self.shanxi1_basci_info))
            elif url == 'https://credit1.gz.gov.cn/creditPublic/creditCodeQuery':
                data = urllib.parse.urlencode({'pageSize':'50',
                        'page':'1'})
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    method='POST',
                    body=data,
                    callback=self.gd_basci_info))
            elif url == 'http://124.239.190.162:81/WebZhglSJZApp/a/xygs/xycx':
                data = urllib.parse.urlencode({'dbType':'1',
                        'pageNo':'1',
                        'pageSize':'20'})
                req.append(self.request(url,
                    redis_flag=REDISFLAG,
                    method='POST',
                    body=data,
                    callback=self.heibei_zz_basci_info))
            elif url == 'http://xyhz.huizhou.gov.cn/html/dmgs_qyList.shtml?pageNo=1':
                req.append(self.request(url,
                        redis_flag=REDISFLAG,
                        callback=self.gd_huizhou_basci_info))
            elif url == 'http://www.creditxj.gov.cn/legalQuery/findLegalList.do?regCode=&dataNumber=10&JGMC=&FDDBR=':
                data = urllib.parse.urlencode({'pageNum':'1',
                                                'numPerPage':'10',
                                                'orderField':'',
                                                'orderDirection':'',
                                                'prePage':'1',
                                                'nextPage':'2',
                                                'ttPage':'64791'})
                req.append(self.request(url,
                        method='POST',
                        redis_flag=REDISFLAG,
                        body=data,
                        callback=self.xinjiang_basci_info))
            elif url == 'https://www.cdcredit.gov.cn/dr/getCreditCodeList.do':
                data = urllib.parse.urlencode({'type':'1',
                        'page':'1',
                        'pageSize':'10',
                        'keyWord':'',
                        'appType':'APP001'})
                req.append(self.request(url,
                        method='POST',
                        redis_flag=REDISFLAG,
                        body=data,
                        callback=self.sc_chengdu_basci_info))
            elif url == 'http://cxcj.creditbj.gov.cn/xyData/front/search/detail.shtml?typeId=2&catalog=xybj_data_bjfr_gs_ent&id=21568978':
                req.append(self.request(url,
                        redis_flag=REDISFLAG,
                        meta={'page':21568978},
                        callback=self.bj_basci_info))
            elif url == 'http://www.creditsd.gov.cn/creditsearch.list.dhtml?source_id=165&kw=&page=1':
                req.append(self.request(url,
                        redis_flag=REDISFLAG,
                        callback=self.sd_discredit_executor))
            elif url == 'http://www.hbcredit.gov.cn/credithb/opensearch/index.html':
                data = urllib.parse.urlencode({'pageIndex': '1'})
                req.append(self.request(url,
                                method='POST',
                                body=data,
                                redis_flag=REDISFLAG,
                                callback=self.hb_basic_info))
            elif url == 'http://www.credithunan.gov.cn/page/corporation/enterpriseList.jsp':
                data = urllib.parse.urlencode({'qymc':'公',
                                               'imageField3.x':'37',
                                               'imageField3.y':'10'},encoding="GBK")
                req.append(self.request(url,
                                        method='POST',
                                        body=data,
                                        redis_flag=REDISFLAG,
                                        callback=self.hunan_basic_info))
            elif url == 'http://www.gzcredit.gov.cn/Service/CreditService.asmx/searchOrgWithPage':
                data = json.dumps({"condition":{"qymc":"公司","cydw":""},"pageNo":"1","pageSize":"100","count":"2466182"})
                req.append(self.request(url,
                                        method='POST',
                                        headers=self.default_jheader,
                                        body=data,
                                        redis_flag=REDISFLAG,
                                        callback=self.guizhou_basic_info))
        return req
        ''' 
                        $(document).ready(
                            function(){var initData = ["J$中国邮政集团公司杭州市火车东站支局$$/corporation/eDetail.do?id=E4BAA0E899A08703","J$温州宜瑞实业发展有限公司$$/corporation/eDetail.do?id=98D5814BC9FABD72","J$余姚市宏亚电器电线厂$$/corporation/eDetail.do?id=1A8B9BA306612057","J$中国电信集团公司乐清分公司$$/corporation/eDetail.do?id=D9F839951C260047","J$浙江宝瑞典当有限责任公司$$/corporation/eDetail.do?id=1A1E990CA0478756","J$衢州市金胜房屋拆迁有限公司$$/corporation/eDetail.do?id=31E90E472E706542","J$绍兴柯桥新风粘合剂厂$$/corporation/eDetail.do?id=FE83F48193079BBF","J$绍兴和悦贸易有限公司$$/corporation/eDetail.do?id=C1430085C362E94B",];;$('#pagetest2').jpage({themeName:'default',openCookies:false,showMode:'full',totalRecord:1936006,dataStore:initData,dataAfter:"",groupSize:1,proxyUrl:'/page/corporation/enterpriseSearchProxy.jsp',perPage:8,barPosition:'bottom',ajaxParam:{id2:'F043B82C71089F52480A95DA2E34A117A89CB9E41A36AA3FC75C79A0DF224AFD5862594A42006C5F'}});}
                        )
                        
                            '''

    def headers_update(self,headers,update):
        if update:
            headers.update(update)
        return headers

    def start_requests(self):

        if hasattr(self, 'redis_key'):
            return _RedisSpider.start_requests(self)
        else:
            self.redis_flag==False
            reqs = self.start_requests()
            return reqs
        

    def parse(self, response):
        pass

    @SpiderHelp.check_response
    def fj_discredit(self, response):
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//*[@class="table table-bordered"]//tr[position()>1]/td[1]/a/@href'
                        },
                callback=self.fj_discredit_executor,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.fjcredit.gov.cn%s' % page,
                divmod=1,
                priority=100,
                redis_conn=self.r,
                redis_flag=True,
                response_type='xpath')
        for req in reqs2:
            yield req

        # '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共(\d+)页'
                    },
            callback=self.fj_discredit,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.fjcredit.gov.cn/creditsearch.list.dhtml?source_id=100&kw=&page=%s' % page,
            divmod=1,
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def fj_discredit_executor(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[contains(@class,"table")]',    
                't': 'xpath',
                'db': 'CreditDataBase.Fj_DiscreditExecutor',
                'keys': ['HTML_ID'],
                'check': 'ExecutorName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '案号',
                    'En': 'CaseNo',
                    'v':
                    './/tr[*[text()="案号"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'id=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '立案日期',
                    'En': 'DateOfFiling',
                    'v':
                    './/tr[*[text()="立案日期"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '名称',
                    'En': 'ExecutorName',
                    'v':
                    './/tr[*[text()="名称"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '年龄',
                    'En': 'Age',
                    'v': './/tr[*[text()="年龄"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执行法院',
                    'En': 'CourtOfExecution',
                    'v': './/tr[*[text()="执行法院"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执行依据文号',
                    'En': 'ExecutionBasis',
                    'v': './/tr[*[text()="执行依据文号"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执行依据制作单位',
                    'En': 'EnforcementBasis',
                    'v': './/tr[*[text()="执行依据制作单位"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '失信被执行人行为具体情况',
                    'En': 'SpecificCircumstances',
                    'v': './/tr[*[text()="失信被执行人行为具体情况"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法定代表人和负责人名称',
                    'En': 'LegalOrChargeName',
                    'v': './/tr[*[text()="法定代表人和负责人名称"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '发布时间',
                    'En': 'ReleaseTime',
                    'v': './/tr[*[text()="发布时间"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def fj_abnormal_operation(self, response):
        '''
        福建经营异常名录
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//*[@class="table table-bordered"]//tr[position()>1]/td[1]/a/@href'
                        },
                callback=self.fj_abnormal_operation_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.fjcredit.gov.cn%s' % page,
                divmod=1,
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共(\d+)页'
                    },
            callback=self.fj_abnormal_operation,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.fjcredit.gov.cn/creditsearch.list.dhtml?source_id=98&kw=&page=%s' % page,
            divmod=1,
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def fj_abnormal_operation_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[contains(@class,"table")]',    
                't': 'xpath',
                'db': 'CreditDataBase.Fj_AbnormalOperation',
                'keys': ['HTML_ID'],
                'check': 'MarketSubjectName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '市场主体名称',
                    'En': 'MarketSubjectName',
                    'v':
                    './/tr[*[text()="市场主体名称"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '工商注册号',
                    'En': 'RegistrationNumber',
                    'v':
                    './/tr[*[text()="工商注册号"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '状态',
                    'En': 'State',
                    'v':
                    './/tr[*[text()="状态"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '列入日期',
                    'En': 'IncludedDate',
                    'v': './/tr[*[text()="列入日期"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '列入事由',
                    'En': 'IncludedReason',
                    'v': './/tr[*[text()="列入事由"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '列入审批机关',
                    'En': 'IncludedApprovalAuthority',
                    'v': './/tr[*[text()="列入审批机关"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '移出日期',
                    'En': 'MoveOutDate',
                    'v': './/tr[*[text()="移出日期"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '移出事由',
                    'En': 'MoveOutReason',
                    'v': './/tr[*[text()="移出事由"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '移出审批机关',
                    'En': 'MoveOutrApprovalAuthority',
                    'v': './/tr[*[text()="移出审批机关"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v': '=(.+)',
                    't': 'url_re'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def fj_administrative_licensing(self, response):
        '''
        福建行政许可
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//*[@class="table table-hover table-condensed"]//tr[position()>1]/td[1]/a/@href'
                        },
                callback=self.fj_administrative_licensing_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.fjcredit.gov.cn%s' % page,
                divmod=1,
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共\d+条,(\d+)页'
                    },
            callback=self.fj_administrative_licensing,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.fjcredit.gov.cn/creditsearch.permissionList.phtml?id=&keyword=&page=%s' % page,
            divmod=1,
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def fj_administrative_licensing_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[contains(@class,"table")]',    
                't': 'xpath',
                'db': 'CreditDataBase.Fj_AdministrativeLicensing',
                'keys': ['HTML_ID'],
                'check': 'NameOfExecutive',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    '=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '行政相对人名称',
                    'En': 'NameOfExecutive',
                    'v':
                    './/tr[*[text()="行政相对人名称"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '项目名称',
                    'En': 'ObjectName',
                    'v':
                    './/tr[*[text()="项目名称"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '行政许可决定书文号',
                    'En': 'AdministrativeLicenseNumber',
                    'v': './/tr[*[text()="行政许可决定书文号"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '审批类别',
                    'En': 'ApprovalCategory',
                    'v': './/tr[*[text()="审批类别"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '许可内容',
                    'En': 'LicenseContent',
                    'v': './/tr[*[text()="许可内容"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': './/tr[*[text()="统一社会信用代码"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v': './/tr[*[text()="组织机构代码"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '工商登记码',
                    'En': 'BusinessRegistrationCode',
                    'v': './/tr[*[text()="工商登记码"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '税务登记号',
                    'En': 'TaxRegistrationNumber',
                    'v': './/tr[*[text()="税务登记号"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人姓名',
                    'En': 'NameOfLegalRepresentative',
                    'v': './/tr[*[text()="法定代表人姓名"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '许可决定日期',
                    'En': 'LicenseDecisionDate',
                    'v': './/tr[*[text()="许可决定日期"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '许可截止期',
                    'En': 'LicenseEndDate',
                    'v': './/tr[*[text()="许可截止期"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '许可机关',
                    'En': 'LicenseAuthority',
                    'v': './/tr[*[text()="许可机关"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def fj_administrative_sanction(self, response):
        '''
        福建行政处罚
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//*[@class="table table-hover table-condensed"]//tr[position()>1]/td[1]/a/@href'
                        },
                callback=self.fj_administrative_sanction_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.fjcredit.gov.cn%s' % page,
                priority=100,
                redis_conn=self.r,
                redis_flag=True,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共(\d+)条'
                    },
            callback=self.fj_administrative_sanction,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.fjcredit.gov.cn/creditsearch.punishmentList.phtml?id=&keyword=&page=%s' % page,
            divmod=15,
            response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def fj_administrative_sanction_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[contains(@class,"table")]',    
                't': 'xpath',
                'db': 'CreditDataBase.Fj_AdministrativeSanction',
                'keys': ['HTML_ID'],
                'check': 'NameOfExecutive',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    '=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '行政许可决定书文号',
                    'En': 'AdministrativeLicenseNumber',
                    'v': './/tr[*[text()="行政许可决定书文号"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '行政相对人名称',
                    'En': 'NameOfExecutive',
                    'v':
                    './/tr[*[text()="行政相对人名称"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '案件名称',
                    'En': 'CaseName',
                    'v':
                    './/tr[*[text()="案件名称"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '处罚类别',
                    'En': 'CategoryOfPunishment',
                    'v': './/tr[*[text()="处罚类别"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '处罚事由',
                    'En': 'CauseOfPunishment',
                    'v': './/tr[*[text()="处罚事由"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '处罚依据',
                    'En': 'PunishmentBasis',
                    'v': './/tr[*[text()="处罚依据"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': './/tr[*[text()="统一社会信用代码"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v': './/tr[*[text()="组织机构代码"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '工商登记码',
                    'En': 'BusinessRegistrationCode',
                    'v': './/tr[*[text()="工商登记码"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '税务登记号',
                    'En': 'TaxRegistrationNumber',
                    'v': './/tr[*[text()="税务登记号"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '居民身份证号',
                    'En': 'IdCardNumber',
                    'v': './/tr[*[text()="居民身份证号"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人姓名',
                    'En': 'NameOfLegalRepresentative',
                    'v': './/tr[*[text()="法定代表人姓名"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '处罚结果',
                    'En': 'PunishmentResult',
                    'v': './/tr[*[text()="处罚结果"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '处罚决定日期',# excel时间戳
                    'En': 'PunishmentDesisionTime',
                    'v': './/tr[*[text()="处罚决定日期"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '处罚截止期',
                    'En': 'PunishmentEndTime',
                    'v': './/tr[*[text()="处罚截止期"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '处罚机关',
                    'En': 'PunishmentAuthority',
                    'v': './/tr[*[text()="处罚机关"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def fj_basic_info(self, response):
        '''
        福建基础信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//*[contains(@class,"table")]//tr[position()>1]/td[1]/a/@href'
                        },
                callback=self.fj_basic_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.fjcredit.gov.cn%s' % page,
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共(\d+)页'
                    },
            callback=self.fj_basic_info,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.fjcredit.gov.cn/creditsearch.list.dhtml?source_id=1&kw=&page=%s' % page,
            divmod=1,
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def fj_basic_info_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[contains(@class,"table")]',    
                't': 'xpath',
                'db': 'CreditDataBase.Fj_BasicInfo',
                'keys': ['HTML_ID'],
                'check': 'OrganizationName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    '=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '机构名称',
                    'En': 'OrganizationName',
                    'v': './/tr[*[text()="机构名称"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '工商注册号',
                    'En': 'BusinessRegistrationCode',
                    'v':
                    './/tr[*[text()="工商注册号"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法定代表人',
                    'En': 'NameOfLegalRepresentative',
                    'v':
                    './/tr[*[text()="法定代表人"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '邮政编码',
                    'En': 'ZipCode',
                    'v': './/tr[*[text()="邮政编码"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '住所',
                    'En': 'Address',
                    'v': './/tr[*[text()="住所"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册资本',
                    'En': 'RegisteredCapital',
                    'v': './/tr[*[text()="注册资本"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v': './/tr[*[text()="经营范围"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '经营开始时间',
                    'En': 'OperateStarTime',
                    'v': './/tr[*[text()="经营开始时间"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': './/tr[*[text()="成立日期"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '企业类型',
                    'En': 'EnterpriseType',
                    'v': './/tr[*[text()="企业类型"]]/td[last()]/text()',
                    't': 'xpath_first'
                },{
                    'n': '登记机关',
                    'En': 'RegistrationAuthority',
                    'v': './/tr[*[text()="登记机关"]]/td[last()]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def hlj_basic_info(self, response):
        '''
        黑龙江基本信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//table[@class="list_2_tab"]//td[@class="t_cen_list2"]/a'
                        },
                callback=self.hlj_basic_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.hljcredit.gov.cn/%s' % page,
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共(\d+)条记录'
                    },
            callback=self.hlj_basic_info,
            headers=self.default_header,
            method='POST',
            urlfunc=
            lambda page,response=None: 'http://www.hljcredit.gov.cn/WebCreditQueryService.do?doEntSearch',
            bodyfunc=lambda page,response=None:urllib.parse.urlencode({'qymcGs':'',
                                            'uniscid':'',
                                            'frdbGs':'',
                                            'curPageNO':str(page),
                                            'randD':''}),
            divmod=10000, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def hlj_basic_info_info(self, response):
        print(response.url)
    
    @SpiderHelp.check_response
    def jx_basic_info(self, response):
        '''
        江西基本信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'json',
                        'v': 'list/xybsm'
                        },
                callback=self.jx_basic_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.creditjx.gov.cn/DataQuery/company/infoNew/%s/1' % page,
                priority=100,
                response_type='json')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json',
                    'v': 'pageCount'
                    },
            callback=self.jx_basic_info,
            headers=self.default_header,
            method='POST',
            urlfunc=
            lambda page,response=None: 'http://www.creditjx.gov.cn/DataQuery/company/listNew.json',
            bodyfunc=lambda page,response=None:urllib.parse.urlencode({'page':str(page),
                                                'pageSize':'100',# 可修正
                                                'cxnr':'',
                                                'cxfs':'',}),
            divmod=1, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='json')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def jx_basic_info_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Jx_BasicInfo',
                'keys': ['CompanyName'],
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
                    'infoNew\/(.+)',
                    't': 'url_re'
                },
                {
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v': '//div[@class="creditQueryDetailName"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v':
                    '//ul[@id="ulQyBaseInfo"]//span[contains(text(),"统一社会信用代码")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
                {
                    'n': '地址',
                    'En': 'Address',
                    'v':
                    '//ul[@id="ulQyBaseInfo"]//span[contains(text(),"地址")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
                {
                    'n': '法定代表人',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//div[@class="creditQueryTabSelection show"]//th[contains(text(),"法定代表人")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v': '//div[@class="creditQueryTabSelection show"]//th[contains(text(),"注册地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '状态',
                    'En': 'State',
                    'v': '//div[@class="creditQueryTabSelection show"]//th[contains(text(),"状态")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '纳税人识别号',
                    'En': 'TaxRegistrationNumber',
                    'v': '//div[@class="creditQueryTabSelection show"]//th[contains(text(),"纳税人识别号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '工商注册号',
                    'En': 'RegistrationNumber',
                    'v': '//div[@class="creditQueryTabSelection show"]//th[contains(text(),"工商注册号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v': '//div[@class="creditQueryTabSelection show"]//th[contains(text(),"组织机构代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//div[@class="creditQueryTabSelection show"]//th[contains(text(),"成立日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资本(万元)',
                    'En': 'RegisteredCapital',
                    'v': '//div[@class="creditQueryTabSelection show"]//th[contains(text(),"注册资本")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v': '//div[@class="creditQueryTabSelection show"]//th[contains(text(),"经营范围")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '登记注册备案数目',
                    'En': 'RegisteredRecordsNumbers',
                    'v': '//div[text()="登记注册备案"]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '资质认证许可数目',
                    'En': 'QualificationLicenseNumbers',
                    'v': '//div[text()="登记注册备案"]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '守信信息数目',
                    'En': 'TrustworthinessNumbers',
                    'v': '//div[text()="登记注册备案"]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '失信信息数目',
                    'En': 'DiscreditNumbers',
                    'v': '//div[text()="登记注册备案"]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '其他信息数目',
                    'En': 'OtherInfomationNumbers',
                    'v': '//div[text()="登记注册备案"]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '行政许可数目',
                    'En': 'AdministrativeLicensingNumbers',
                    'v': '//div[text()="登记注册备案"]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '行政处罚数目',
                    'En': 'AdministrativeSanctionNumbers',
                    'v': '//div[text()="登记注册备案"]/span/text()',
                    't': 'xpath_first'
                },
            ]
        },]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def jx_lawyer_info(self, response):
        '''
        江西律师信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'json',
                        'v': 'list/xybsm'
                        },
                callback=self.jx_basic_info_info,
                headers=self.default_header,
                # 需要修改
                urlfunc=
                lambda page,response=None: 'http://www.creditjx.gov.cn/DataQuery/company/infoNew/%s/1' % page,
                priority=100,
                response_type='json')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json',
                    'v': 'pageCount'
                    },
            callback=self.jx_lawyer_info,
            headers=self.default_header,
            method='POST',
            urlfunc=
            lambda page,response=None: 'http://www.creditjx.gov.cn/DataQuery/website/zrr/queryZrrList.json',
            bodyfunc=lambda page,response=None:urllib.parse.urlencode({'enTableName':'SFT_LSZYZGZXX_SFT',#执业类别  有11种类别
                        'searchContent':'',# 查询字段
                        'rownum':'10000',  # 限制数字
                        'page':str(page),#页面
                        'pageSize':'10000'} # 每页显示数量
                        ),
            divmod=1, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='json')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def xz_basic_info(self, res):
        '''
        新疆基本信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'json',
                        'v': 'list/xybsm'
                        },
                callback=self.jx_basic_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.creditjx.gov.cn/DataQuery/company/infoNew/%s/1' % page,
                priority=100,
                response_type='json')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json',
                    'v': 'pageCount'
                    },
            callback=self.jx_basic_info,
            headers=self.default_header,
            method='POST',
            urlfunc=
            lambda page,response=None: 'http://www.creditjx.gov.cn/DataQuery/company/listNew.json',
            bodyfunc=lambda page,response=None:urllib.parse.urlencode({'page':str(page),
                                                'pageSize':'100',# 可修正
                                                'cxnr':'',
                                                'cxfs':'0'}),
            divmod=1, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='json')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sd_basic_info(self, response):
        '''
        山东基础信息
        '''
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="table table-bordered"]//tr[position()>1]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sd_BasicData1',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v': './td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': './td[2]/text()',
                    't': 'xpath_first'
                },{
                    'n': '工商注册号/登记证号',
                    'En': 'RegistrationNumber',
                    'v': './td[3]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        # 搜索页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//table[@class="table table-bordered"]//tr[position()>1]/td[1]/text()'
                        },
                callback=self.sd_search_page,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.creditsd.gov.cn/creditsearch.corlistace.dhtml?kw=%s' % page,
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req



        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '条,(\d+)页'
                    },
            callback=self.sd_basic_info,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.creditsd.gov.cn/creditsearch.listcreditsd.dhtml?page=%s' % page,
            divmod=1, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req


    
    @SpiderHelp.check_response
    def sd_search_page(self, response):
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//a[@class="widget-title-nowrap"]/@href'
                        },
                callback=self.sd_basic_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.creditsd.gov.cn%s' % page,
                priority=1000,
                response_type='xpath')
        for req in reqs2:
            yield req

    @SpiderHelp.check_response
    def sd_basic_info_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="cate-boxcon cur"]//div[@class="overview"]',    
                't': 'xpath',
                'db': 'CreditDataBase.Sd_BasicData2',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v': 'id=(.+)',
                    't': 'url_re'
                },{
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v': '//div[@class="head-text"]/h1/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//i[@class="fa fa-user"]/following-sibling::text()',
                    't': 'xpath_re',
                    're':'[:：](\w+)'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//i[@class="fa fa-file-text"]/following-sibling::text()',
                    't': 'xpath_re',
                    're':'[:：](\w+)'
                },{
                    'n': '状态',
                    'En': 'State',
                    'v': '//div[@class="head-text"]/h1/em/text()',
                    't': 'xpath_first'
                },{
                    'n': '类型',
                    'En': 'CompanyType',
                    'v': './/*[contains(text(),"类型")]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资本',
                    'En': 'RegisteredCapital',
                    'v': './/*[contains(text(),"注册资本")]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': './/*[contains(text(),"成立日期")]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '营业期限自',
                    'En': 'BusinessStartTime',
                    'v': './/*[contains(text(),"营业期限自")]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '营业期限至',
                    'En': 'BusinessEndTime',
                    'v': './/*[contains(text(),"营业期限至")]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '登记机关',
                    'En': 'RegistrationAuthority',
                    'v': './/*[contains(text(),"登记机关")]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '核准日期',
                    'En': 'DateOfApproval',
                    'v': './/*[contains(text(),"核准日期")]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '登记状态',
                    'En': 'BusinessRegistrationState',
                    'v': './/*[contains(text(),"登记状态")]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '住所',
                    'En': 'Address',
                    'v': './/*[contains(text(),"住所")]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfOperation',
                    'v': './/*[contains(text(),"经营范围")]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def hainan_basic_info(self, response):
        response = response.replace(body=re.compile('\\\\(?:n|t)?').sub('',re.compile('list\":\"(.*?)\"\}',re.S).search(response.text).group(1) ))
        '''
        海南基本信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_res',
                        'v': '//a/@href',
                        're': 'key=(.+)'
                        },
                callback=self.hainan_basic_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://xyhn.hainan.gov.cn/JRBWeb/IntegratedManger/HnxykQyxxJbxxMainController.do?reqCode=showCredit&key=%s' % page,
                priority=100,
                redis_conn=self.r,
                redis_flag=True,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'abs',
                    'v': '416533'
                    },
            callback=self.hainan_basic_info,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://xyhn.hainan.gov.cn/JRBWeb/IntegratedManger/HnxykQyxxJbxxMainController.do?reqCode=VCreditquery&qymc=&pageNo=%s&pageNumber=100' % page,
            divmod=10, #
            redis_conn=self.r,
            redis_flag=True,
            offset=10,
            response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def hainan_basic_info_info(self, response):
        response = response.replace(body=re.compile('\\\\(?:n|t)?').sub('',re.compile('rightData1\":\"(.*?)\"\}',re.S).search(response.text).group(1) ))
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Hainan_BasicInfoData',
                'keys': ['HTML_ID'],
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
                    'key=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v': '//td[text()="企业名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '住所',
                    'En': 'Address',
                    'v': '//td[text()="住所"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v':
                    '//td[text()="注册号/统一社会信用代码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '联系电话',
                    'En': 'ContactNumber',
                    'v':
                    '//td[text()="联系电话"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '公司类型',
                    'En': 'CompanyType',
                    'v': '//td[text()="公司类型"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//td[text()="成立日期"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '登记机关',
                    'En': 'RegisteredOrgan',
                    'v': '//td[text()="登记机关"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '经营场所',
                    'En': 'OfficeAddress',
                    'v': '//td[text()="经营场所"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '一般经营项目',
                    'En': 'ScopeOfOperation',
                    'v': '//td[text()="一般经营项目"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def haidian_basic_info(self, response):
        '''
        海淀基础信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'json',
                        'v': 'resultJson/id'
                        },
                callback=self.haidian_basic_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://xinyong.bjhd.gov.cn/twogs/twogs!findqyxx.action?qyid=%s' % page,
                priority=100,
                redis_conn=self.r,
                redis_flag=True,
                response_type='json')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'abs',
                    'v': '500000'
                    },
            callback=self.haidian_basic_info,
            method='POST',
            headers=self.headers_update(self.default_header,{'X-Requested-With': 'XMLHttpRequest','Referer':'http://xinyong.bjhd.gov.cn/compan/companList!companIndex.action'}),
            urlfunc=
            lambda page,response=None: 'http://xinyong.bjhd.gov.cn/compan/companList!companList.action',
            divmod=500000, #
            bodyfunc=lambda page, response=None:urllib.parse.urlencode({'name':'请输入企业信息（如：名称、企业组织机构代码、工商注册码）',
                                    'types':'0',
                                    'page.total':'500000',
                                    'page.perPage':'100',
                                    'page.index':str(page)}),
            redis_conn=self.r,
            redis_flag=True,
            response_type='json')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def haidian_basic_info_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Bj_Haidian_BasicInfoData',
                'keys': ['HTML_ID'],
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
                    '=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v': '//tr[th[text()="企业名称"]]/td/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v':
                    '//tr[th[text()="统一社会信用代码"]]/td/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法人代表',
                    'En': 'NameOfLegalRepresentative',
                    'v':
                    '//tr[th[text()="法人代表"]]/td/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//tr[th[text()="成立日期"]]/td/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册资金',
                    'En': 'RegisteredCapital',
                    'v': '//tr[th[text()="注册资金"]]/td/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v': '//tr[th[text()="注册地址"]]/td/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '企业类型',
                    'En': 'CompanyType',
                    'v': '//tr[th[text()="企业类型"]]/td/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '主体状态',
                    'En': 'State',
                    'v': '//tr[th[text()="主体状态"]]/td/text()',
                    't': 'xpath_first'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def js_basic_info(self, response):
        #size  3676854
        '''
        江苏基础信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//table//tr/td[2]/text()'
                        },
                callback=self.js_search_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.jscredit.gov.cn/credit/enterprise/webFuzzySearch.do?keyword=%s' % page,
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'abs',
                    'v': '3676854'
                    },
            callback=self.js_basic_info,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.jscredit.gov.cn/credit/p/common/ucc/webPageList.do?pageSize=100&currPage=%s' % page,
            divmod=100, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def js_search_info(self, response):
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_re',
                        'v': '//tr[@onclick]/@onclick',
                        're':"detail\(\'(.*?)\'\)"
                        },
                callback=self.js_basic_infoinfo,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.jscredit.gov.cn/credit/enterprise/webDetail.do?ukValue=%s' % page,
                priority=1000,
                response_type='xpath')
        for req in reqs2:
            yield req
    
    @SpiderHelp.check_response
    def js_basic_infoinfo(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Js_BasicInfoData',
                'keys': ['HTML_ID'],
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
                    '=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v': '//th[text()="企业名称"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v':
                    '//th[text()="统一社会信用代码"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v':
                    '//th[text()="组织机构代码"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '企业类型',
                    'En': 'EnterpriseType',
                    'v':
                    '//th[text()="企业类型"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '所属行业',
                    'En': 'Industry',
                    'v':
                    '//th[text()="所属行业"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人证件种类',
                    'En': 'LegalIdCardType',
                    'v':
                    '//th[text()="法定代表人证件种类"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人证件号码',
                    'En': 'LegalIdCardNumber',
                    'v':
                    '//th[text()="法定代表人证件号码"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法定代表人姓名',
                    'En': 'NameOfLegalRepresentative',
                    'v':
                    '//th[text()="法定代表人姓名"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法定代表人职务',
                    'En': 'LegalPost',
                    'v': '//th[text()="法定代表人职务"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册资金单位万元',
                    'En': 'RegisteredCapital',
                    'v': '//th[text()="注册资金单位万元"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                }, {
                    'n': '币种',
                    'En': 'Currency',
                    'v': '//th[text()="币种"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                }, {
                    'n': '经营范围',
                    'En': 'ScopeOfOperation',
                    'v': '//th[text()="经营范围"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                }, {
                    'n': '注册地址',
                    'En': 'RegisteredAddress',
                    'v': '//th[text()="注册地址"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                }, {
                    'n': '邮政编码',
                    'En': 'ZipCode',
                    'v': '//th[text()="邮政编码"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                }, {
                    'n': '联系电话',
                    'En': 'ContactNumber',
                    'v': '//th[text()="联系电话"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                }, {
                    'n': '工商注册登记日期',
                    'En': 'BusinessRegistrationCode',
                    'v': '//th[text()="工商注册登记日期"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '工商注册登记机关全称',
                    'En': 'BusinessRegistrationOrgan',
                    'v': '//th[text()="工商注册登记机关全称"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '地税税务登记证号',
                    'En': 'TaxRegistrationNumber',
                    'v': '//th[text()="地税税务登记证号"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '地税税务登记日期',
                    'En': 'TaxRegistrationDate',
                    'v': '//th[text()="地税税务登记日期"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '地税税务登记机关全称',
                    'En': 'TaxRegistrationOrgan',
                    'v': '//th[text()="地税税务登记机关全称"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '国税税务登记证号',
                    'En': 'NationalTaxRegistrationNumber',
                    'v': '//th[text()="国税税务登记证号"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '国税税务登记日期',
                    'En': 'NationalTaxRegistrationDate',
                    'v': '//th[text()="国税税务登记日期"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '国税税务登记机关全称',
                    'En': 'NationalTaxRegistrationOrgan',
                    'v': '//th[text()="国税税务登记机关全称"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '参保证号',
                    'En': 'InsuranceCertificateNumber',
                    'v': '//th[text()="参保证号"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '参保状态',
                    'En': 'InsuranceCertificateState',
                    'v': '//th[text()="参保状态"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '参保日期',
                    'En': 'InsuranceCertificateDate',
                    'v': '//th[text()="参保日期"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '参保登记机关全称',
                    'En': 'InsuranceCertificateOrgan',
                    'v': '//th[text()="参保登记机关全称"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '海关登记证号',
                    'En': 'CustomsEntryNumber',
                    'v': '//th[text()="海关登记证号"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '海关登记日期',
                    'En': 'CustomsEntryDate',
                    'v': '//th[text()="海关登记日期"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '海关登记机关全称',
                    'En': 'CustomsEntryOrgan',
                    'v': '//th[text()="海关登记机关全称"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '企业状态',
                    'En': 'State',
                    'v': '//th[text()="企业状态"]/following-sibling::td[1]/span/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def js_discredit_executor(self, response):
        #size  134169
        '''
        江苏被执行人信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_res',
                        'v': '//table//tr[@onclick]/@onclick',
                        're':"detail\(\'(.*?)\'\)"
                        },
                callback=self.js_discredit_executor_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.jscredit.gov.cn/credit/p/common/dishonesty/webDetail.do?uk=%s' % page,
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'abs',
                    'v': '134169'
                    },
            callback=self.js_discredit_executor,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.jscredit.gov.cn/credit/p/common/dishonesty/webPageList.do?pageSize=100&currPage=%s' % page,
            divmod=100, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def js_discredit_executor_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Js_DiscreditExecutor',
                'keys': ['HTML_ID'],
                'check': 'ExecutorName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    '=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '被执行人名称',
                    'En': 'ExecutorName',
                    'v': '//th[text()="被执行人名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '证件号码',
                    'En': 'IdCardNumber',
                    'v':
                    '//th[text()="证件号码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '案号',
                    'En': 'CaseNo',
                    'v':
                    '//th[text()="案号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执行案由',
                    'En': 'CauseOfPunishment',
                    'v': '//th[text()="执行案由"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '案件标识',
                    'En': 'CaseID',
                    'v': '//th[text()="案件标识"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '性别名称',
                    'En': 'Gender',
                    'v': '//th[text()="性别名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '年龄',
                    'En': 'Age',
                    'v': '//th[text()="年龄"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '证件类型名称',
                    'En': 'IdCardType',
                    'v': '//th[text()="证件类型名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v': '//th[text()="组织机构代码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//th[text()="法定代表人"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '履行情况名称',
                    'En': 'Performance',
                    'v': '//th[text()="履行情况名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '执行法院名称',
                    'En': 'CourtOfExecution',
                    'v': '//th[text()="执行法院名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '执行依据文号',
                    'En': 'EnforcementbasisNumber',
                    'v': '//th[text()="执行依据文号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '立案时间',
                    'En': 'FilingTime',
                    'v': '//th[text()="立案时间"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '执行依据制作单位',
                    'En': 'EnforcementbasisProductor',
                    'v': '//th[text()="执行依据制作单位"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '失信行为情形名称',
                    'En': 'Dishonesty',
                    'v': '//th[text()="失信行为情形名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '裁判文书文号',
                    'En': 'AdjudicativeDocumentsNumber',
                    'v': '//th[text()="裁判文书文号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发布时间',
                    'En': 'ReleaseTime',
                    'v': '//th[text()="发布时间"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '最后更新时间',
                    'En': 'LastUpdateTime',
                    'v': '//th[text()="最后更新时间"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def js_administrative_licensing(self, response):
        #size  4840413
        '''
        江苏行政许可
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_res',
                        'v': '//table//tr[@onclick]/@onclick',
                        're':"detail\(\'(.*?)\'\)"
                        },
                callback=self.js_administrative_licensing_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.jscredit.gov.cn/credit/p/two_publicity/webDetail.do?_type=al&uk=%s' % page,
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'abs',
                    'v': '4840413'
                    },
            callback=self.js_administrative_licensing,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.jscredit.gov.cn/credit/p/two_publicity/webPageList.do?_type=al&webInvokeCondition=%7B%22queryCondition%22%3A%5B%7B%22name%22%3A%22XK_XDR%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22XK_XDR_SHXYM%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22XK_XDR_ZDM%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22XK_XDR_GSDJ%22%2C%22value%22%3A%22%22%7D%5D%7D&currPage={}&pageSize=100'.format(page),
            divmod=100, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def js_administrative_licensing_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Js_AdministrativeLicensing',
                'keys': ['HTML_ID'],
                'check': 'AdministrativeCounterpart',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'uk=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '行政许可决定书文号',
                    'En': 'LicenseDecisionNumber',
                    'v': '//th[text()="行政许可决定书文号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '审批类别',
                    'En': 'ApprovalCategory',
                    'v':
                    '//th[text()="审批类别"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '行政相对人名称',
                    'En': 'AdministrativeCounterpart',
                    'v':
                    '//th[text()="行政相对人名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '许可内容',
                    'En': 'LicenseContent',
                    'v': '//th[text()="许可内容"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//th[text()="统一社会信用代码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '项目名称',
                    'En': 'ProjectName',
                    'v': '//th[text()="项目名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v': '//th[text()="组织机构代码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '工商登记码',
                    'En': 'BusinessRegistrationCode',
                    'v': '//th[text()="工商登记码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '税务登记号',
                    'En': 'TaxRegistrationNumber',
                    'v': '//th[text()="税务登记号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '居民身份证号',
                    'En': 'IdCardNumber',
                    'v': '//th[text()="居民身份证号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人姓名',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//th[text()="法定代表人姓名"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '许可生效期',
                    'En': 'LicenseDecisionDate',
                    'v': '//th[text()="许可生效期"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '许可截止期',
                    'En': 'LicenseEndDate',
                    'v': '//th[text()="许可截止期"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '许可机关',
                    'En': 'LicensingAuthority',
                    'v': '//th[text()="许可机关"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '地方编码',
                    'En': 'AreaCode',
                    'v': '//th[text()="地方编码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '数据更新时间戳',
                    'En': 'LastUpdateTimeStamp',
                    'v': '//th[text()="数据更新时间戳"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '备注',
                    'En': 'Remark',
                    'v': '//th[text()="备注"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def js_administrative_sanction(self, response):
        #size  19840
        '''
        江苏处罚信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_res',
                        'v': '//table//tr[@onclick]/@onclick',
                        're':"detail\(\'(.*?)\'\)"
                        },
                callback=self.js_administrative_sanction_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.jscredit.gov.cn/credit/p/two_publicity/webDetail.do?_type=ap&uk=%s' % page,
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'abs',
                    'v': '19840'
                    },
            callback=self.js_administrative_sanction,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.jscredit.gov.cn/credit/p/two_publicity/webPageList.do?_type=ap&webInvokeCondition=%7B%22queryCondition%22%3A%5B%7B%22name%22%3A%22CF_XDR_MC%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22CF_XDR_SHXYM%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22CF_XDR_ZDM%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22CF_XDR_GSDJ%22%2C%22value%22%3A%22%22%7D%5D%7D&currPage={}&pageSize=100'.format(page),
            divmod=100, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def js_administrative_sanction_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Js_AdministrativeSanction',
                'keys': ['HTML_ID'],
                'check': 'AdministrativeCounterpart',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v':
                    'uk=(.+)',
                    't': 'url_re'
                },
                {
                    'n': '行政处罚决定书文号',
                    'En': 'SanctionDecisionNumber',
                    'v': '//th[text()="行政处罚决定书文号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '行政相对人名称',
                    'En': 'AdministrativeCounterpart',
                    'v':
                    '//th[text()="行政相对人名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '处罚种类',
                    'En': 'PunishmentType',
                    'v': '//th[text()="处罚种类"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '处罚类别2',
                    'En': 'PunishmentType2',
                    'v': '//th[text()="处罚类别2"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '处罚事由',
                    'En': 'CauseOfPunishment',
                    'v': '//th[text()="处罚事由"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '处罚依据', #字段较长
                    'En': 'PunishmentBasis',
                    'v': '//th[text()="处罚依据"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '案件名称',
                    'En': 'CaseName',
                    'v': '//th[text()="案件名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//th[text()="统一社会信用代码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v': '//th[text()="组织机构代码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '工商登记码',
                    'En': 'BusinessRegistrationCode',
                    'v': '//th[text()="工商登记码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '税务登记码',
                    'En': 'TaxRegistrationNumber',
                    'v': '//th[text()="税务登记码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '居民身份证号',
                    'En': 'IdCardNumber',
                    'v': '//th[text()="居民身份证号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人姓名',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//th[text()="法定代表人姓名"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '处罚结果',
                    'En': 'PunishmentResult',
                    'v': '//th[text()="处罚结果"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '处罚机关',
                    'En': 'PunishmentAuthority',
                    'v': '//th[text()="处罚机关"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '处罚生效期',
                    'En': 'TermOfPunishment',
                    'v': '//th[text()="处罚生效期"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '地方编码',
                    'En': 'AreaCode',
                    'v': '//th[text()="地方编码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '数据更新时间戳',
                    'En': 'LastUpdateTimeStamp',
                    'v': '//th[text()="数据更新时间戳"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '备注',
                    'En': 'Remark',
                    'v': '//th[text()="备注"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '公示截止期',
                    'En': 'PublicDeadline',
                    'v': '//th[text()="公示截止期"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
   
    @SpiderHelp.check_response
    def xz_basic_info(self, response):
        # size 155742
        '''
        江苏处罚信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 're_findall',
                        'v': "legalQueryInfo\(\'(\d+)\',\'(.+)\'",
                        },
                callback=self.xz_basic_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,kw,response=None: 'http://www.creditxizang.gov.cn/xyxz/legalQuery/legalQueryInfo.do?colId=2&id=%s&entName=%s&legalStatus=&legalType=' % (page,kw),
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共有(\d+)页'
                    },
            callback=self.xz_basic_info,
            method='POST',
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.creditxizang.gov.cn/xyxz/legalQuery/legalQuery.do?entName=&legalStatus=&legalType=',
            bodyfunc=lambda page,response=None:urllib.parse.urlencode({'pageNum':str(page),
                                                'numPerPage':'10',
                                                'orderField':'',
                                                'orderDirection':'',
                                                'prePage':str(abs(page)),
                                                'nextPage':str(page+2),
                                                'ttPage':'15575'}),
            divmod=1, #
            redis_conn=self.r,
            redis_flag=True,
            errback=self.errbackparse,
            response_type='xpath')
        for req in reqs:
            yield req

    
    def errbackparse(self, failure):
        logger.error(failure)
    
    @SpiderHelp.check_response
    def xz_basic_info_info(self, response):
        
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="qyfr_ny_2"]',    
                't': 'xpath',
                'db': 'CreditDataBase.Xz_BasicInfoData',
                'keys': ['HTML_ID'],
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
                    '&id=(\d+)&',
                    't': 'url_re'
                },
                {
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v': '//h4/text()',
                    't': 'xpath_first'
                },{
                    'n': '登记机关',
                    'En': 'RegistrationAuthority',
                    'v': '//*[contains(text(),"登记机关")]/text()',
                    't': 'xpath_re',
                    're':'：([\s\S]+)'
                },
                {
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//*[contains(text(),"登记号")]/text()',
                    't': 'xpath_re',
                    're':':([\s\S]+)'
                },
                {
                    'n': '法人代表',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//*[contains(text(),"法定代表人")]/text()',
                    't': 'xpath_re',
                    're':'：([\s\S]+)'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//*[contains(text(),"成立日期")]/text()',
                    't': 'xpath_re',
                    're':'：([\s\S]+)'
                },
                {
                    'n': '注册资金',
                    'En': 'RegisteredCapital',
                    'v': '//*[contains(text(),"注册资金")]/text()',
                    't': 'xpath_re',
                    're':'：([\s\S]+)'
                },
                {
                    'n': '地址',
                    'En': 'RegisteredAddress',
                    'v': './/*[contains(text(),"地址")]/text()',
                    't': 'xpath_re',
                    're':'：([\s\S]+)'
                },
                {
                    'n': '企业类型',
                    'En': 'CompanyType',
                    'v': '//*[contains(text(),"企业类型")]/text()',
                    't': 'xpath_re',
                    're':'：([\s\S]+)'
                },
                {
                    'n': '状态',
                    'En': 'State',
                    'v': '//*[contains(text(),"状态")]/text()',
                    't': 'xpath_re',
                    're':'：([\s\S]+)'
                }
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def hebei_basic_info(self, response):
        # size 63508 * 6
        '''
        河北基础信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//a[text()="查看"]/@href',
                        },
                callback=self.hebei_basic_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: '%s' % page,
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re',
                    'v': '//nobr/a[last()]/@href',
                    're': 'page=(\d+)'
                    },
            callback=self.hebei_basic_info,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://123.182.226.146:8082/was5/web/search?page=%s&channelid=260465&orderby=RELEVANCE&perpage=100&outlinepage=10&searchscope=&timescope=&timescopecolumn=&orderby=RELEVANCE&andsen=&total=&orsen=&exclude=' % page,
            divmod=1, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def hebei_basic_info_info(self,response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Hebei_BasicData',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v': '//span[@class="title"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//span[contains(text(),"统一社会信用代码:")]/following-sibling::span[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法人代表',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//div[@class="listDetail"]//td[contains(text(),"法人信息")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '税务登记号',
                    'En': 'TaxRegistrationNumber',
                    'v': '//div[@class="listDetail"]//td[contains(text(),"税务登记号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//div[@class="listDetail"]//td[contains(text(),"成立日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v': '//div[@class="listDetail"]//td[contains(text(),"经营范围")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v': '//div[@class="listDetail"]//td[contains(text(),"组织机构代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资金',
                    'En': 'RegisteredCapital',
                    'v': '//div[@class="listDetail"]//td[contains(text(),"注册资金")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '企业状态',
                    'En': 'State',
                    'v': '//div[@class="listDetail"]//td[contains(text(),"企业状态")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '经营期限',
                    'En': 'TermOfOperation',
                    'v': '//div[@class="listDetail"]//td[contains(text(),"经营期限")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '地址',
                    'En': 'Address',
                    'v': '//span[contains(text(),"地址")]/following-sibling::span[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def hebei_administrative_licensing(self, response):
        # size 7166 * 100
        '''
        河北许可信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//a[text()="行政许可"]/@href',
                        },
                callback=self.hebei_administrative_licensing_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.credithebei.gov.cn:8082/was5/web/%s' % page,
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re',
                    'v': '//nobr/a[last()]/@href',
                    're': 'page=(\d+)'
                    },
            callback=self.hebei_administrative_licensing,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.credithebei.gov.cn:8082/was5/web/search?page=%s&channelid=284126&orderby=RELEVANCE&perpage=100' % page,
            divmod=1, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def hebei_administrative_licensing_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Hebei_BasicInfoData',
                'keys': ['HTML_ID'],
                'check': 'AdministrativeCounterpart',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID', # 无id
                    'En': 'HTML_ID',
                    'v':
                    'record=(\d+)',
                    't': 'url_re'
                },
                {
                    'n': '行政许可决定书文号',
                    'En': 'LicenseDecisionNumber',
                    'v': '//td[text()="行政许可决定书文号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '项目名称',
                    'En': 'ProjectName',
                    'v': '//td[text()="项目名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '审批类别',
                    'En': 'ApprovalCategory',
                    'v': '//td[text()="审批类别"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '许可内容',
                    'En': 'LicenseContent',
                    'v': '//td[text()="许可内容"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '行政相对人名称',
                    'En': 'AdministrativeCounterpart',
                    'v': '//td[text()="行政相对人名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//td[text()="统一社会信用代码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v': '//td[text()="组织机构代码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '工商登记码',
                    'En': 'BusinessRegistrationCode',
                    'v': '//td[text()="工商登记码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '税务登记号',
                    'En': 'TaxRegistrationNumber',
                    'v': '//td[text()="税务登记号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '居民身份证号',
                    'En': 'IdCardNumber',
                    'v': '//td[text()="居民身份证号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法定代表人姓名',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//td[text()="法定代表人姓名"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '许可决定日期',
                    'En': 'LicenseDecisionDate',
                    'v': '//td[text()="许可决定日期"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '许可截止日期',
                    'En': 'LicenseEndDate',
                    'v': '//td[text()="许可截止日期"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '许可机关',
                    'En': 'LicenseAuthority',
                    'v': '//td[text()="许可机关"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '当前状态',
                    'En': 'State',
                    'v': '//td[text()="当前状态"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '数据更新时间戳',
                    'En': 'LastUpdateTimeStamp',
                    'v': '//td[text()="数据更新时间戳"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '备注',
                    'En': 'Remark',
                    'v': '//td[text()="备注"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def hebei_administrative_sanction(self, response):
        # size 424 * 100
        '''
        河北处罚信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//a[text()="行政处罚"]/@href',
                        },
                callback=self.hebei_administrative_sanction_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.credithebei.gov.cn:8082/was5/web/%s' % page,
                priority=100,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re',
                    'v': '//nobr/a[last()]/@href',
                    're': 'page=(\d+)'
                    },
            callback=self.hebei_administrative_sanction,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.credithebei.gov.cn:8082/was5/web/search?page=%s&channelid=271661&orderby=RELEVANCE&perpage=100' % page,
            divmod=1, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def hebei_administrative_sanction_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Hebei_BasicInfoData',
                'keys': ['HTML_ID'],
                'check': 'AdministrativeCounterpart',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID', # 无id
                    'En': 'HTML_ID',
                    'v':
                    'record=(\d+)',
                    't': 'url_re'
                },
                {
                    'n': '行政处罚决定文书号',
                    'En': 'SanctionDecisionNumber',
                    'v': '//td[text()="行政处罚决定文书号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//td[text()="统一社会信用代码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '处罚名称',
                    'En': 'NameOfPunishment',
                    'v': '//td[text()="处罚名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '处罚类型',
                    'En': 'CategoryOfPunishment',
                    'v': '//td[text()="处罚类型"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '处罚事由',
                    'En': 'CauseOfPunishment',
                    'v': '//td[text()="处罚事由"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '处罚依据',
                    'En': 'PunishmentBasis',
                    'v': '//td[text()="处罚依据"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '行政相对人名称',
                    'En': 'AdministrativeCounterpart',
                    'v': '//td[text()="行政相对人名称"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v': '//td[text()="组织机构代码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '工商登记码',
                    'En': 'BusinessRegistrationCode',
                    'v': '//td[text()="工商登记码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '税务登记号',
                    'En': 'TaxRegistrationNumber',
                    'v': '//td[text()="税务登记号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '居民身份证号',
                    'En': 'IdCardNumber',
                    'v': '//td[text()="居民身份证号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法定代表人姓名',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//td[text()="法定代表人姓名"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '处罚决定日期（处罚生效期）',
                    'En': 'SantionDecisionDate',
                    'v': '//td[text()="处罚决定日期（处罚生效期）"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '处罚机关',
                    'En': 'santionAuthority',
                    'v': '//td[text()="处罚机关"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '当前状态',
                    'En': 'State',
                    'v': '//td[text()="当前状态"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '数据更新时间戳',
                    'En': 'LastUpdateTimeStamp',
                    'v': '//td[text()="数据更新时间戳"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '备注',
                    'En': 'Remark',
                    'v': '//td[text()="备注"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def jl_basci_info(self, response):
        # size 424 * 100
        '''
        吉林基础信息
        '''
        _configs = [{
            'list': {
                'n': '',
                'v': 'list',    
                't': 'json',
                'db': 'CreditDataBase.Jl_BasciData',
                'keys': ['HTML_ID'],
                'check': 'HTML_ID',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': 'HTML_ID', # 无id
                    'En': 'HTML_ID',
                    'v':
                    'xybsm',
                    't': 'json'
                },{
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v': 'qymc',
                    't': 'json'
                }
                
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        # 详情页
        reqs3 = self.scrapy_info_url_help( response,
                config={'t': 'json',
                        'v': 'list/xybsm',
                        },
                callback=self.jl_basci_info_info2,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page,response=None: 'http://36.48.62.24:8704/DataQuery/company/company_info.json',
                bodyfunc = lambda page, response=None:{ 'xybsm':page,
                                                   'depID':'1E977A5FB90F57F9E050007F0100C45B',
                                                   'roleID':'1CEC3A826B2543649922F4FB1082B69A'
                                                   },
                priority=100,
                response_type='json')
        for req in reqs3:
            yield req

        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'json',
                        'v': 'list/xybsm',
                        },
                callback=self.jl_basci_info_info,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page,response=None: 'http://36.48.62.24:8704/DataQuery/company/company_info.json',
                bodyfunc = lambda page, response=None:{ 'xybsm':page,
                                                   'depID':'938DDF2F83B141A5B8035F3794AFF8FE',
                                                   'roleID':'1CEC3A826B2543649922F4FB1082B69A'
                                                   },
                priority=100,
                response_type='json')
        for req in reqs2:
            yield req

        

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json',
                    'v': 'pageCount',
                    },
            callback=self.jl_basci_info,
            method='POST',
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://36.48.62.24:8704/DataQuery/company/list.json',
            divmod=1, #
            bodyfunc=lambda page,response=None:urllib.parse.urlencode({'cxnr':'',
                                                'cxfw':'QYMC-',
                                                'fddbr':'',
                                                'szdq':'',
                                                'hylx':'',
                                                'ztlx':'',
                                                'ztfl':'qy',
                                                'page':str(page),
                                                'pageSize':'15'}),
            redis_conn=self.r,
            redis_flag=True,
            response_type='json')
        for req in reqs:
            yield req

        
             
    @SpiderHelp.check_response
    def jl_basci_info_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Jl_BasciData',
                'keys': ['HTML_ID'],
                'check': 'HTML_ID',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID', # 无id
                    'En': 'HTML_ID',
                    'v':
                    'xybsm',
                    't': 'request_body'
                },
                {
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '\"统一社会信用代码\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '注册号',
                    'En': 'RegistrationNumber',
                    'v': '\"注册号\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '市场主体类型（中文名称）',
                    'En': 'CompanyType',
                    'v': '\"市场主体类型（中文名称）\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '行业门类',
                    'En': 'IndustryCategory',
                    'v': '\"行业门类\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '\"成立日期\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '登记机关（中文名称）',
                    'En': 'RegisteredOrgan',
                    'v': '\"登记机关（中文名称）\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v': '\"经营范围\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '经营(驻在)期限自',
                    'En': 'TermOfOperation',
                    'v': '\"经营\(驻在\)期限自\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '登记状态（中文名称）',
                    'En': 'State',
                    'v': '\"登记状态（中文名称）\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '住所',
                    'En': 'Address',
                    'v': '\"住所\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '注册资本(金)',
                    'En': 'RegisteredCapital',
                    'v': '\"注册资本\(金\)\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '法定代表人',
                    'En': 'NameOfLegalRepresentative',
                    'v': '\"法定代表人\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '核准日期',
                    'En': 'DateOfApproval',
                    'v': '\"核准日期\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '机构代码',
                    'En': 'OrganizationCode',
                    'v': '\"机构代码\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def jl_basci_info_info2(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Jl_BasciData',
                'keys': ['HTML_ID'],
                'check': 'HTML_ID',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID', # 无id
                    'En': 'HTML_ID',
                    'v':
                    'xybsm',
                    't': 'request_body'
                },{
                    'n': '地址',
                    'En': 'OfficeAddress',
                    'v': '\"地址\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '法人',
                    'En': 'NameOfLegalRepresentative2',
                    'v': '\"法人\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '身份证号',
                    'En': 'IdCardNumber',
                    'v': '\"身份证号\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '注册资金',
                    'En': 'RegisteredOrgan2',
                    'v': '\"注册资金\",\"columnValue\":\"(.*?)\"',
                    't': 'regex1'
                },
                
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def zj_basci_info(self,response):
        # size 424 * 100
        '''
        浙江基本信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 're_findall',
                        'v': '\$\$([\s\S]+?)\"',
                        },
                callback=self.zj_basci_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.zjcredit.gov.cn%s' % page,
                priority=100,
                errback=self.errbackparse,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': 'totalRecord\s*?=\s*?(\d+)',
                    },
            callback=self.zj_basci_info,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.zjcredit.gov.cn/page/corporation/enterpriseSearchProxy.jsp?startrecord=%s&endrecord=%s&perpage=100&totalRecord=1936006' % (100 * page - 99, 100 * page),
            bodyfunc=
            lambda page, response=None:urllib.parse.urlencode({'id2': 'F043B82C71089F52480A95DA2E34A117A89CB9E41A36AA3FC75C79A0DF224AFD5862594A42006C5F'}),
            divmod=100, #
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def zj_basci_info_info(self, response):
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.ZjBasciData',
                'keys': ['HTML_ID'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID', # 无id
                    'En': 'HTML_ID',
                    'v':
                    'id=(\w+)',
                    't': 'url_re'
                },
                {
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v': '//td[@class="qyxx_1"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//td[text()="统一社会信用代码"]/following-sibling::td[@class]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '住所',
                    'En': 'Address',
                    'v': '//td[text()="住　　　　　　所"]/following-sibling::td[@class]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法人代表',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//td[text()="法人代表"]/following-sibling::td[@class]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册资本',
                    'En': 'RegisteredCapital',
                    'v': '//td[text()="注册资本"]/following-sibling::td[@class]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//td[text()="成立日期"]/following-sibling::td[@class]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '经营范围详细信息',
                    'En': 'ScopeOfoperation',
                    'v': '//tr[td[text()="经营范围详细信息"]]/following-sibling::tr//*[@class]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营状态',   # /html/images/0726001f.gif 存续
                    'En': 'State',
                    'v': '//td[@class="qyxx_1"]/img[last()]',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def gx_basci_info(self, response):
        #'http://www.gxcredit.gov.cn/getXyxxList.jspx?search_type=1&key_word=&page=1'
        # size 未知 --测试41278
        '''
        广西基本信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'json',
                        'v': 'ID',
                        },
                callback=self.gx_basci_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.gxcredit.gov.cn/toDetail.jspx?xyxx=%s' % page,
                priority=100,
                errback=self.errbackparse,
                response_type='json')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'abs',
                    'v': '41278',
                    },
            callback=self.gx_basci_info,
            headers=self.default_header,
            method='POST',
            urlfunc=
            lambda page,response=None: 'http://www.gxcredit.gov.cn/getXyxxList.jspx?search_type=1&key_word=&page=%s' % page,
            divmod=1, 
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def gx_basci_info_info(self,response):
        _configs = [
        {
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Gx_BasciData',
                'keys': ['HTML_ID'],
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
                    'xyxx=(\w+)',
                    't': 'url_re'
                },
                {
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v': '//h1/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//p[contains(text(),"统一社会信用代码")]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '地址',
                    'En': 'Address',
                    'v': '//p[contains(text(),"地址")]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '工商注册号',
                    'En': 'BusinessRegistrationCode',
                    'v': '//li[contains(text(),"工商注册号")]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '税务登记号',
                    'En': 'TaxRegistrationNumber',
                    'v': '//li[contains(text(),"税务登记号")]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '法人信息',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//li[contains(text(),"法人信息")]/span/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//li[contains(text(),"成立日期")]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',   
                    'En': 'ScopeOfoperation',
                    'v': '//li[contains(text(),"经营范围")]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '组织机构代码',   
                    'En': 'OrganizationCode',
                    'v': '//li[contains(text(),"组织机构代码")]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册资金',  
                    'En': 'RegisteredCapital',
                    'v': '//li[contains(text(),"注册资金")]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '审核/年检日期',   
                    'En': 'DateOfAudit',
                    'v': '//li[contains(text(),"审核/年检日期")]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营期限',  
                    'En': 'TermOfOperation',
                    'v': '//li[contains(text(),"经营期限")]/span/text()',
                    't': 'xpath_first'
                },
            ]
        },
        #{"XK_WSH":"(南)工商登记企核准字[2012]第10162号","XK_XDR_SWDJ":"","XK_FR":"钟明桂","XK_SSDW":"","XK_XDR_ZDM":"","XK_XZJG":"南宁市良庆区工商行政管理局","XK_ZT":"0","UUID":"5A3F4F4C2047AB69E053150D080A7BB6","XK_SXQ":"","XYPT_Q_DELETE_DXP":"2017-03-17 01:04:14","XK_SPLB":"设立","DML_FLAG":"0","BZ":"","XK_XDR_GSDJ":"450100000100303","XK_XDR_SFZ":"","XK_JZQ":"2099-12-31 00:00:00","XK_XDR_SHXYM":"91450108057532913H","DQ":"","XK_XMMC":"设立登记","XK_JDRQ":"2012-11-28 00:00:00","XK_NR":"设立登记","DFBM":"450000","XK_XDR":"南宁市桂之益投资有限公司"}
        {
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Gx_AdministrativeLicensing',
                'keys': ['UUID'],
                'check': 'AdministrativeCounterpart',# 为js写入
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID', # 无id
                    'En': 'HTML_ID',
                    'v':
                    'xyxx=(\w+)',
                    't': 'url_re'
                },{
                    'n': 'UUID', # 无id
                    'En': 'UUID',
                    'v': '\"UUID\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '行政许可决定书文号',
                    'En': 'LicenseDecisionNumber',
                    'v': '\"XK_WSH\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '项目名称',
                    'En': 'ProjectName',
                    'v': '\"XK_XXMC\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '审批类别',
                    'En': 'ApprovalCategory',
                    'v': '\"XK_SPLB\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '内容',
                    'En': 'LicenseContent',
                    'v': '\"XK_NR\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '行政相对人名称',
                    'En': 'AdministrativeCounterpart',
                    'v': '\"XK_XDR\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '\"XK_XDR_SHXYM\":\"(.*?)\"',
                    't': 'regex1'
                },
                {
                    'n': '组织机构代码',
                    'En': 'OrganizationCode',
                    'v': '\"XK_XDR_ZDM\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '工商登记码',   
                    'En': 'BusinessRegistrationCode',
                    'v': '\"XK_XDR_GSDJ\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '税务登记号',   
                    'En': 'TaxRegistrationNumber',
                    'v': '\"XK_XDR_SWDJ\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '法定代表人姓名',   
                    'En': 'NameOfLegalRepresentative',
                    'v': '\"XK_FR\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '地方编码', 
                    'En': 'AreaCode',
                    'v': '\"DFBM\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '数据更新时间戳',  
                    'En': 'LastUpdateTimeStamp',
                    'v': '\"XYPT_Q_DELETE_DXP\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '备注',  
                    'En': 'Remark',
                    'v': '\"BZ\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '状态',  
                    'En': 'State',
                    'v': '\"XK_ZT\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': '许可机关',  
                    'En': 'LicensingAuthority',
                    'v': '\"XK_XZJG\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': 'DML_FLAG',  
                    'En': 'DML_FLAG',
                    'v': '\"DML_FLAG\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': 'XK_SXQ',  
                    'En': 'XK_SXQ',
                    'v': '\"XK_SXQ\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': 'XK_SSDW',  
                    'En': 'XK_SSDW',
                    'v': '\"XK_SSDW\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': 'XK_JZQ',  
                    'En': 'XK_JZQ',
                    'v': '\"XK_JZQ\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': 'DQ',  
                    'En': 'DQ',
                    'v': '\"DQ\":\"(.*?)\"',
                    't': 'regex1'
                },{
                    'n': 'XK_JDRQ',  
                    'En': 'XK_JDRQ',
                    'v': '\"XK_JDRQ\":\"(.*?)\"',
                    't': 'regex1'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def shanxi1_basci_info(self, response):
        # size 228302 
        '''
        山西基本信息
        '''
        # 获取interfaceValue
        flag = response.xpath('//table[@class="table_list"]//tr[position()>1]/td[4]/a/@onclick').extract_first()
        if flag != None:
            pass
        else:
            request = response.request.replace(dont_filter=True)
            yield request
            return
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_res',
                        'v': '//table[@class="table_list"]//tr[position()>1]/td[4]/a/@onclick',
                        're': 'toview\(\'(.+)\'\)'
                        },
                callback=self.shanxi1_basci_info2,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page,response=None: 'http://www.creditsx.gov.cn/getSecurityInfo.jspx',
                bodyfunc=lambda page,response=None:urllib.parse.urlencode({'code':page,'creditCorpusCode':'L'}),
                priority=100,
                errback=self.errbackparse,
                response_type='xpath')
        for req in reqs2:
            yield req
        # logger.info(response.text)
        '''翻页逻辑'''
        # 未知原因 造成获取页面失败
        reqs = self.scrapy_page_help(
            response,
            # config={'t': 'xpath_first',
            #         'v': '//table[@class="table_list"]//tr[position()>1]/td[4]/a/@onclick',
            #         },
            config={'t': 'abs',
                    'v': '228302',
                    },
            callback=self.shanxi1_basci_info,
            headers=self.default_header,
            method='POST',
            # flag=True, # 逻辑翻页
            urlfunc=
            lambda page,response=None: 'http://www.creditsx.gov.cn/list-L.jspx',
            bodyfunc=
            lambda page,response=None:urllib.parse.urlencode({'pageNo':str(page),
                                'creditCorpusCode':'L',
                                'name':'',
                                'lcreditcode':'',
                                'sxly':'',
                                'isquery':'true'}),
            divmod=1, 
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def shanxi1_basci_info2(self, response):
        # 获取详情页

        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'json',
                        'v': 'interfaceValue',
                        },
                callback=self.shanxi1_basci_info_info,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page,response=None: 'http://www.creditsx.gov.cn/CreditMiddleService/a/dataQuery/validEnterprise',
                bodyfunc=lambda page,response=None:urllib.parse.urlencode({'interfaceValue':page.replace('\r\n','')}),
                priority=100,
                errback=self.errbackparse,
                response_type='json')
        for req in reqs2:
            yield req
    
    @SpiderHelp.check_response
    def shanxi1_basci_info_info(self, response):
        # 解析数据
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Shanxi1BasciData',
                'keys': ['BusinessRegistrationCode'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v': '//td[contains(text(),"主体名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//td[contains(text(),"统一社会信用代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '登记证号',
                    'En': 'BusinessRegistrationCode',
                    'v': '//td[contains(text(),"登记证号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '国税登记证号',
                    'En': 'NationalTaxRegistrationNumber',
                    'v': '//td[contains(text(),"国税登记证号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '组织机构代码证号',
                    'En': 'OrganizationCode',
                    'v': '//td[contains(text(),"组织机构代码证号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v': '//td[contains(text(),"经营范围")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '信用主体大类',
                    'En': 'BigClass',
                    'v': '//td[contains(text(),"信用主体大类")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '信用主体小类',  
                    'En': 'SmallClass',
                    'v': '//td[contains(text(),"信用主体小类")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人（负责人）姓名',   
                    'En': 'NameOfLegalRepresentative',
                    'v': '//td[contains(text(),"姓名")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人（负责人）身份证号',   
                    'En': 'LegalIdCardNumber',
                    'v': '//td[contains(text(),"身份证号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '住所',   
                    'En': 'Address',
                    'v': '//td[contains(text(),"住所")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '状态',  
                    'En': 'State',
                    'v': '//td[contains(text(),"状态")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营起始日期',  
                    'En': 'BusinessStartTime',
                    'v': '//td[contains(text(),"经营起始日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营截止日期',  
                    'En': 'BusinessEndTime',
                    'v': '//td[contains(text(),"经营截止日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '成立日期',  
                    'En': 'SetupTime',
                    'v': '//td[contains(text(),"成立日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '所属行业', 
                    'En': 'Industry',
                    'v': '//td[contains(text(),"所属行业")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def gd_basci_info(self, response):
        # pagesize is '17109'
        '''
        广州基本信息
        '''

        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'abs',
                    'v': '17109',
                    },
            callback=self.gd_basci_info,
            headers=self.default_header,
            method='POST',
            urlfunc=
            lambda page,response=None: 'https://credit1.gz.gov.cn/creditPublic/creditCodeQuery',
            divmod=1, 
            bodyfunc=lambda page, response=None:urllib.parse.urlencode({'pageSize':'50',
                        'page':str(page)}),
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req

        # 基本信息在列表页已经全部展示 无须进入
        _configs = [{
            'list': {
                'n': '',
                'v': 'rows',    
                't': 'json',
                'db': 'CreditDataBase.Gd_Gz_BasicData',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v': 'bm',
                    't': 'json'
                },{
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v': 'jgmc',
                    't': 'json'
                },{
                    'n': '主体名称',
                    'En': 'CompanyType',
                    'v': 'jglx',
                    't': 'json'
                },{
                    'n': '登记机关名称',
                    'En': 'RegistrationAuthority',
                    'v': 'djjgmc',
                    't': 'json'
                },
                {
                    'n': '登记注册号码',
                    'En': 'RegistrationNumber',
                    'v': 'djzchm',
                    't': 'json'
                },
                {
                    'n': '登记注册类型',
                    'En': 'RegistrationType',
                    'v': 'djzclx',
                    't': 'json'
                },
                {
                    'n': '登记注册时间',
                    'En': 'RegistrationDate',
                    'v': 'djzcsj',
                    't': 'json'
                },{
                    'n': '登记注册地址',
                    'En': 'RegistrationAddress',
                    'v': 'djzcxxdz',
                    't': 'json'
                },
                {
                    'n': '法定代表人',
                    'En': 'NameOfLegalRepresentative',
                    'v': 'fddbrmc',
                    't': 'json'
                },{
                    'n': '法定代表人证件号码',  
                    'En': 'IdCardNumber',
                    'v': 'fddbrsfzjhm',
                    't': 'json'
                },{
                    'n': '法定代表人证件类型',  
                    'En': 'IdCardType',
                    'v': 'fddbrsfzjlx',
                    't': 'json'
                },{
                    'n': '工商登记状态',   
                    'En': 'BusinessRegistrationState',
                    'v': 'gsdjzt',
                    't': 'json'
                },{
                    'n': '经营范围',   
                    'En': 'ScopeOfOperation',
                    'v': 'jyfw',
                    't': 'json'
                },{
                    'n': '社会统一信用代码',  
                    'En': 'UnifiedSocialCreditCode',
                    'v': 'tyshxydm',
                    't': 'json'
                },{
                    'n': '注册资金单位万元',  
                    'En': 'RegisteredCapital',
                    'v': 'zczj',
                    't': 'json'
                },{
                    'n': '注册资本币种',  
                    'En': 'Currency',
                    'v': 'zczbbz',
                    't': 'json'
                },{
                    'n': '组织机构代码', 
                    'En': 'OrganizationCode',
                    'v': 'zzjgdm',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def heibei_zz_basci_info(self, response):
        # size 未知 --测试41278
        '''
        郑州基本信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//*[@class="tablelistshow"]//tr[position()>1]/td[last()]/a/@href',
                        },
                callback=self.heibei_zz_basci_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://124.239.190.162:81%s' % page,
                priority=100,
                errback=self.errbackparse,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_first',
                    'v': '//*[@class="tablelistshow"]//tr[position()>1]/td[last()]/a/@href',
                    },
            callback=self.heibei_zz_basci_info,
            headers=self.default_header,
            method='POST',
            flag=True,
            urlfunc=
            lambda page,response=None: 'http://124.239.190.162:81/WebZhglSJZApp/a/xygs/xycx',
            bodyfunc=lambda page,response=None:urllib.parse.urlencode({'dbType':'1',
                        'pageNo':str(page),
                        'pageSize':'20'}),
            divmod=1, 
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def heibei_zz_basci_info_info(self, response):
        logger.info(response.text)
    
    @SpiderHelp.check_response
    def gd_huizhou_basci_info(self, response):
        # size 未知 --测试41278
        '''
        惠州基本信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//a[img[@title="详情"]]/@href',
                        },
                callback=self.gd_huizhou_basci_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://xyhz.huizhou.gov.cn/html/%s' % page,
                priority=100,
                errback=self.errbackparse,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_first',
                    'v': '//*[@class="pagination"]/div[2]/a[last()-1]/text()',
                    },
            callback=self.gd_huizhou_basci_info,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://xyhz.huizhou.gov.cn/html/dmgs_qyList.shtml?pageNo=%s' % page,
            divmod=1, 
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def gd_huizhou_basci_info_info(self, response):

        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Gd_Huizhou_BasicData',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v': 'guid=(.+)',
                    't': 'url_re'
                },{
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v': '//td[contains(text(),"企业名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//td[contains(text(),"统一信用代码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '工商注册登记日期',
                    'En': 'RegistrationDate',
                    'v': '//td[contains(text(),"工商注册登记日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '工商注册到期日期',
                    'En': 'RegistrationEndDate',
                    'v': '//td[contains(text(),"工商注册到期日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法定代表人姓名',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//td[contains(text(),"法定代表人姓名")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '证件类型',
                    'En': 'IdCardType',
                    'v': '//td[contains(text(),"证件类型")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证件号码',
                    'En': 'IdCardNumber',
                    'v': '//td[contains(text(),"证件号码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '企业类型',
                    'En': 'CompanyType',
                    'v': '//td[contains(text(),"企业类型")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '所属行业',  
                    'En': 'Industry',
                    'v': '//td[contains(text(),"所属行业")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册地址',  
                    'En': 'RegisteredAddress',
                    'v': '//td[contains(text(),"注册地址")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '邮政编码',   
                    'En': 'ZipCode',
                    'v': '//td[contains(text(),"邮政编码")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '联系电话',   
                    'En': 'ContactNumber',
                    'v': '//td[contains(text(),"联系电话")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '登记机关',  
                    'En': 'RegistrationAuthority',
                    'v': '//td[contains(text(),"登记机关")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def xinjiang_basci_info(self, response):
        # size 647910
        '''
        新疆基本信息
        '''
        # 详情页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//div[@id="content"]//table//tr[position()>1]/td[1]/a/@href',
                        },
                callback=self.xinjiang_basci_info_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.creditxj.gov.cn%s' % page,
                priority=100,
                errback=self.errbackparse,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_first',
                    'v': '//div[@class="gzdt_ny_page"]/input[@id="totalPage"]/@value',
                    },
            callback=self.xinjiang_basci_info,
            headers=self.default_header,
            method="POST",
            urlfunc=
            lambda page,response=None: 'http://www.creditxj.gov.cn/legalQuery/findLegalList.do?regCode=&dataNumber=10&JGMC=&FDDBR=',
            bodyfunc=lambda page,response=None:urllib.parse.urlencode({'pageNum':str(page),
                                                'numPerPage':'10',
                                                'orderField':'',
                                                'orderDirection':'',
                                                'prePage':str(page-2),
                                                'nextPage':str(page),
                                                'ttPage':'64791'}),
            divmod=1, 
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req
    
    @SpiderHelp.check_response
    def xinjiang_basci_info_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Xinjiang_BasicData',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v': 'id=(.+)',
                    't': 'url_re'
                },{
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v': '//td[div[strong[contains(text(),"企业名称")]]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '状态',
                    'En': 'State',
                    'v': '//td[div[strong[contains(text(),"状态")]]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//td[div[strong[contains(text(),"统一社会信用代码")]]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册登记时间',
                    'En': 'RegistrationDate',
                    'v': '//td[div[strong[contains(text(),"注册登记时间")]]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册登记号',
                    'En': 'RegistrationNumber',
                    'v': '//td[div[strong[contains(text(),"注册登记号")]]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法定代表人姓名',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//td[div[strong[contains(text(),"法定代表人姓名")]]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },{
                    'n': '登记管理机关',
                    'En': 'RegistrationAuthority',
                    'v': '//td[div[strong[contains(text(),"登记管理机关")]]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '企业地址',
                    'En': 'Address',
                    'v': '//td[div[strong[contains(text(),"企业地址")]]]/following-sibling::td/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def sc_chengdu_basci_info(self, response):
        # size 647910
        '''
        成都基本信息
        '''
        # 搜索页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'json',
                        'v': 'msg/rows/idno',
                        },
                callback=self.sc_chengdu_basci_search,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page,response=None: 'https://www.cdcredit.gov.cn/search/getRecommendation.do',
                bodyfunc=lambda page,response=None:urllib.parse.urlencode({'text':page,
                                                            'unit':'0',
                                                            'appType':'APP001'}),
                priority=100,
                errback=self.errbackparse,
                response_type='json')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json',
                    'v': 'msg/total',
                    },
            callback=self.sc_chengdu_basci_info,
            headers=self.default_header,
            method="POST",
            urlfunc=
            lambda page,response=None: 'https://www.cdcredit.gov.cn/dr/getCreditCodeList.do',
            bodyfunc=lambda page,response=None:urllib.parse.urlencode({'type':'1',
                        'page':str(page),
                        'pageSize':'10',
                        'keyWord':'',
                        'appType':'APP001'}),
            divmod=10, 
            redis_conn=self.r,
            redis_flag=True,
            response_type='json')
        for req in reqs:
            yield req

  
    def chengdu_data(self, page, response=None):
        JS = json.loads(response.text)['msg']['rows'][0]
        _id = JS['id']
        unit = JS['unit']
        accpNo = JS['accpNo']
        data = urllib.parse.urlencode({'id':_id,
                'unit':unit,
                'accpNo':accpNo,
                'appType':'APP001',
                'authorization':''})
        return data
    
    @SpiderHelp.check_response
    def sc_chengdu_basci_search(self, response):
        # 跳转工商信息页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'abs',
                        'v': 'accpNo',
                        },
                callback=self.sc_chengdu_basci_info_info,
                headers=self.default_header,
                method='POST',
                urlfunc=
                lambda page,response=None: 'https://www.cdcredit.gov.cn/EPBaseInfo/getGsjRegisterDetail.do',
                bodyfunc=self.chengdu_data,
                priority=1000,
                errback=self.errbackparse,
                response_type='xpath')
        for req in reqs2:
            yield req
    
    @SpiderHelp.check_response
    def sc_chengdu_basci_info_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Sc_chengd_BasicData',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v': 'id',
                    't': 'request_body'
                },{
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v': 'text\"s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"主体名称\"',
                    't': 'regex1'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': 'text\"s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"统一社会信用代码\"',
                    't': 'regex1'
                },{
                    'n': '住所（经营场所）',
                    'En': 'Address',
                    'v': 'text\"s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"住所（经营场所）\"',
                    't': 'regex1'
                },
                {
                    'n': '经营场所',
                    'En': 'OfficeAddress',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"经营场所\"',
                    't': 'regex1'
                },
                {
                    'n': '企业类型',
                    'En': 'CompanyType',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"企业类型\"',
                    't': 'regex1'
                },
                {
                    'n': '注册资本（金）',
                    'En': 'RegisteredCapital',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"注册资本（金）\"',
                    't': 'regex1'
                },{
                    'n': '注册资本币种',
                    'En': 'registeredCurrency',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"注册资本币种\"',
                    't': 'regex1'
                },
                {
                    'n': '实收资本',
                    'En': 'CapitalCollection',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"实收资本\"',
                    't': 'regex1'
                },{
                    'n': '实收资本币种',
                    'En': 'CapitalCurrency',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"实收资本币种\"',
                    't': 'regex1'
                },{
                    'n': '主营范围',
                    'En': 'MainScope',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"主营范围\"',
                    't': 'regex1'
                },{
                    'n': '兼营范围',
                    'En': 'ConcurrentlyScope',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"兼营范围\"',
                    't': 'regex1'
                },{
                    'n': '一般经营项目',
                    'En': 'GeneralBusinessProject',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"一般经营项目\"',
                    't': 'regex1'
                },{
                    'n': '许可经营项目',
                    'En': 'LicensedProject',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"许可经营项目\"',
                    't': 'regex1'
                },{
                    'n': '营业期限自',
                    'En': 'TimeLimitForBusiness',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"营业期限自\"',
                    't': 'regex1'
                },{
                    'n': '营业期限至',
                    'En': 'BusinessPeriodTo',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"营业期限至\"',
                    't': 'regex1'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"成立日期\"',
                    't': 'regex1'
                },{
                    'n': '核准日期',
                    'En': 'DateOfApproval',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"核准日期\"',
                    't': 'regex1'
                },{
                    'n': '行业门类',
                    'En': 'IndustryCategory',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"行业门类\"',
                    't': 'regex1'
                },{
                    'n': '邮政编码',
                    'En': 'ZipCode',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"邮政编码\"',
                    't': 'regex1'
                },{
                    'n': '状态',
                    'En': 'State',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"状态\"',
                    't': 'regex1'
                },{
                    'n': '经营方式',
                    'En': 'OperationMode',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"经营方式\"',
                    't': 'regex1'
                },{
                    'n': '经营类别',
                    'En': 'OperationCategory',
                    'v': 'text\"\s*?:\s*?\"?([^"]*?)\"?\s*?,\s*?\"title\"\s*?:\s*?\"经营类别\"',
                    't': 'regex1'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
    
    @SpiderHelp.check_response
    def bj_basci_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Bj_BasicData',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v': '&id=(\d+)',
                    't': 'url_re'
                },{
                    'n': '企业名称',
                    'En': 'CompanyName',
                    'v': '//strong[contains(text(),"主体名称")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },{
                    'n': '工商注册号',
                    'En': 'RegistrationNumber',
                    'v': '//strong[contains(text(),"工商注册号")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//strong[contains(text(),"统一社会信用代码")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },
                {
                    'n': '住所',
                    'En': 'Address',
                    'v': '//strong[contains(text(),"住所")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },
                {
                    'n': '法定代表人',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//strong[contains(text(),"法定代表人")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//strong[contains(text(),"成立日期")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },{
                    'n': '一般经营范围',
                    'En': 'GeneralScopeofoperation',
                    'v': '//strong[contains(text(),"一般经营范围")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },
                {
                    'n': '许可经营范围',
                    'En': 'ScopeOfLicensing',
                    'v': '//strong[contains(text(),"许可经营范围")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },{
                    'n': '经营范围项下标注',
                    'En': 'OperationScopeAnnotation',
                    'v': '//strong[contains(text(),"经营范围项下标注")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },{
                    'n': '企业历史变更名称',
                    'En': 'HistoryChangeName',
                    'v': '//strong[contains(text(),"企业历史变更名称")]/following-sibling::text()[1]',
                    't': 'xpath_first'
                },{
                    'n': '良好信息',
                    'En': 'GoodRecord',
                    'v': '//li[text()="红名单("]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '不良信息',
                    'En': 'BadRecord',
                    'v': '//li[text()="黑名单("]/span/text()',
                    't': 'xpath_first'
                },{
                    'n': '提示信息',
                    'En': 'WarningRecore',
                    'v': '//li[text()="提示信息("]/span/text()',
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
            config={'t': 'abs',
                    'v': '24633917',
                    },
            callback=self.bj_basci_info,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://cxcj.creditbj.gov.cn/xyData/front/search/detail.shtml?typeId=2&catalog=xybj_data_bjfr_gs_ent&id=%s' % page,
            divmod=1, 
            redis_conn=self.r,
            redis_flag=True,
            pagestart=21568978,
            response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sd_discredit_executor(self, response):
        # size 5768125
        '''
        山东失信被执行人信息
        '''
        # 搜索页
        reqs2 = self.scrapy_info_url_help( response,
                config={'t': 'xpath_extract',
                        'v': '//table[@class="table table-bordered"]//tr[position()>1]/td[1]/a/@href',
                        },
                callback=self.sd_discredit_executor_info,
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.creditsd.gov.cn%s' % page,
                priority=100,
                errback=self.errbackparse,
                response_type='xpath')
        for req in reqs2:
            yield req

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            # config={'t': 'regex1',
            #         'v': ',(\d+)页',
            #         },
            config={'t': 'abs',
                    'v': '5',
                    },
            callback=self.sd_discredit_executor,
            headers=self.default_header,
            urlfunc=
            lambda page,response=None: 'http://www.creditsd.gov.cn/creditsearch.list.dhtml?source_id=165&kw=&page=%s' % page,
            divmod=1, 
            redis_conn=self.r,
            redis_flag=True,
            response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def sd_discredit_executor_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'xpath',
                'db': 'CreditDataBase.Sd_DiscreditExecutorData',
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
                    'v': 'id=(.+)',
                    't': 'url_re'
                },{
                    'n': '失信被执行人名称',
                    'En': 'DiscreditExecutor',
                    'v': '//*[contains(text(),"失信被执行人名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '案号',
                    'En': 'CaseNo',
                    'v': '//*[contains(text(),"案号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '证件号',
                    'En': 'IdCardNumber',
                    'v': '//*[contains(text(),"证件号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执行法院',
                    'En': 'CourtOfExecution',
                    'v': '//*[contains(text(),"执行法院")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '地域名称',
                    'En': 'AreaName',
                    'v': '//*[contains(text(),"地域名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执行依据文号',
                    'En': 'ExecutionBasis',
                    'v': '//*[contains(text(),"执行依据文号")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '做出执行依据单位',
                    'En': 'MakeExecutionBasedUnit',
                    'v': '//*[contains(text(),"做出执行依据单位")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '被执行人的履行情况',
                    'En': 'Performance',
                    'v': '//*[contains(text(),"被执行人的履行情况")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '失信被执行人具体情形',
                    'En': 'SpecificCircumstances',
                    'v': '//*[contains(text(),"失信被执行人具体情形")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '发布时间',
                    'En': 'ReleaseTime',
                    'v': '//*[contains(text(),"发布时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '立案时间',
                    'En': 'FilingTime',
                    'v': '//*[contains(text(),"立案时间")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '已履行部分',
                    'En': 'FulfillingPart',
                    'v': '//*[contains(text(),"已履行部分")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '未履行部分',
                    'En': 'UnfulfilledPart',
                    'v': '//*[contains(text(),"未履行部分")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]

        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def hb_basic_info(self, response):
        # size 16147 * 20
        '''
        湖北基本信息
        '''
        # 搜索页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 'xpath_extract',
                                                   'v': '//div[@class="inquire_list"]//a/@href',
                                                   },
                                           callback=self.hb_basic_info_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page,response=None: 'http://www.hbcredit.gov.cn%s' % page,
                                           priority=100,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs2:
            yield req
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                # config={'t': 'regex1',
                #         'v': ',(\d+)页',
                #         },
                config={'t': 'xpath_re',
                        'v': '//div[@class="page"]/a[last()]/@onclick',
                        're': '\((\d+)\)'
                        },
                callback=self.hb_basic_info,
                method='POST',
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.hbcredit.gov.cn/credithb/opensearch/index.html',
                bodyfunc=lambda page, response :urllib.parse.urlencode({'pageIndex': str(page)}),
                divmod=1,
                redis_conn=self.r,
                redis_flag=True,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def hb_basic_info_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'CreditDataBase.Hubei_BasicData',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
                'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v': 's=(.+)',
                    't': 'url_re'
                },{
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v': '//*[contains(text(),"企业名称")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//*[contains(text(),"统一社会信用代码")]/following-sibling::*[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '法定代表人',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//td[contains(text(),"法定代表人")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//td[contains(text(),"成立日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册资本（万元）',
                    'En': 'RegisteredCapital',
                    'v': '//td[contains(text(),"注册资本")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '登记状态',
                    'En': 'BusinessRegistrationState',
                    'v': '//td[contains(text(),"登记状态")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '核准日期',
                    'En': 'DateOfApproval',
                    'v': '//td[contains(text(),"核准日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '登记机关',
                    'En': 'RegistrationAuthority',
                    'v': '//td[contains(text(),"登记机关")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营场所',
                    'En': 'OfficeAddress',
                    'v': '//td[contains(text(),"经营场所")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '工商注册号码',
                    'En': 'RegistrationNumber',
                    'v': 'gsdjm\"\s*?[:：]\s*?\'(.*?)\'',
                    't': 'regex1'
                },
            ]
        }]

        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def hunan_basic_info(self, response):
        # 跳转页面 获取id2管家参数
        url = 'http://www.credithunan.gov.cn/page/corporation/enterpriseSearchProxy.jsp?startrecord=0&endrecord=100&perpage=100&totalRecord=607221'
        result = re.compile("id2:\'(.*?)\'").search(response.text)
        if result:
            id2 = result.group(1)
        else:
            # 备用地址
            id2 = 'F043B82C71089F526ACBAFB6EBED264C624EF9F2B3BFF80BBDCA944B5023F1B80FB93CC84163E532'
        data = urllib.parse.urlencode({'id2':id2})
        yield self.request(url,
                           method='POST',
                           body=data,
                           meta={'page':1},
                           callback=self.hunan_basic_info2)

    def hunan_basic_info2(self, response):
        # size 607221
        '''
        湖南基本信息
        '''
        # 搜索页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 're_findall',
                                                   'v': '\$\$\.\.(.*?)\"',
                                                   },
                                           callback=self.hunan_basic_info_info,
                                           headers=self.default_header,
                                           urlfunc=
                                           lambda page,response=None: 'http://www.credithunan.gov.cn/page%s' % page,
                                           priority=100,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs2:
            yield req
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'abs',
                        'v': '607221'
                        },
                callback=self.hunan_basic_info2,
                method='POST',
                headers=self.default_header,
                urlfunc=
                lambda page,response=None: 'http://www.credithunan.gov.cn/page/corporation/enterpriseSearchProxy.jsp?startrecord=%s&endrecord=%s&perpage=100&totalRecord=607221' % ((page-1)*100, page*100),
                bodyfunc=
                lambda page, response=None: response.request.body.decode('utf-8'),
                divmod=100,
                redis_conn=self.r,
                redis_flag=True,
                response_type='xpath')
        for req in reqs:
            yield req

    @SpiderHelp.check_response
    def hunan_basic_info_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'CreditDataBase.Hunan_BasicData',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
                'xpath',
            'data': [
                {
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v': '\?id=(.+)&',
                    't': 'url_re'
                },{
                    'n': 'HTML_ID2',
                    'En': 'HTML_ID2',
                    'v': 'etpsId=(.+)',
                    't': 'url_re'
                },{
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v': '//td[@class="title"]/text()',
                    't': 'xpath_first'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': '//td[text()="统一社会信用代码"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '注册号',
                    'En': 'RegistrationNumber',
                    'v': '//td[text()="注册号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '法定代表人',
                    'En': 'NameOfLegalRepresentative',
                    'v': '//td[text()="法定代表人"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '类型',
                    'En': 'CompanyType',
                    'v': '//td[text()="类型"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': '//td[text()="成立日期"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '核准日期',
                    'En': 'DateOfApproval',
                    'v': '//td[contains(text(),"核准日期")]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注册资本（万元）',
                    'En': 'RegisteredCapital',
                    'v': '//td[text()="注册资本(万元)"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '所在行政区划',
                    'En': 'AreaName',
                    'v': '//td[text()="所在行政区划"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营状态',
                    'En': 'State',
                    'v': '//td[text()="经营状态"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '营业期限自',
                    'En': 'BusinessStartTime',
                    'v': '//td[text()="营业期限自"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '营业期限至',
                    'En': 'BusinessEndTime',
                    'v': '//td[text()="营业期限至"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '住所',
                    'En': 'Address',
                    'v': '//td[text()="住所"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },{
                    'n': '经营范围',
                    'En': 'ScopeOfoperation',
                    'v': '//tr[td[text()="经营范围"]]/following-sibling::tr[1]/td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]

        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @SpiderHelp.check_response
    def guizhou_basic_info(self, response):
        # size 2197950
        '''
        贵州基本信息 
        '''
        # 搜索页
        reqs2 = self.scrapy_info_url_help( response,
                                           config={'t': 're_findall',
                                                    #正则匹配公司 个体名称
                                                   'v': '"mc[^\"]*?\":[^\"]*?\"[\x00-\xff]*(.+?)[\x00-\xff]*?\"',
                                                   },
                                           callback=self.guizhou_basic_info_info,
                                           headers=self.default_jheader,
                                           method='POST',
                                           urlfunc=
                                           lambda page,response=None: 'http://www.gzcredit.gov.cn/Service/CreditService.asmx/searchDetail',
                                           bodyfunc=lambda page,response=None:json.dumps({"condition":{"qymc":page,"cydw":""}}),
                                           priority=100,
                                           errback=self.errbackparse,
                                           response_type='xpath')
        for req in reqs2:
            yield req
        #'''翻页逻辑'''
        reqs = self.scrapy_page_help(
                response,
                config={'t': 'regex1',
                        'v': '"count\\\\\":(\d+)'
                        },
                callback=self.guizhou_basic_info,
                method='POST',
                headers=self.default_jheader,
                urlfunc=
                lambda page,response=None: 'http://www.gzcredit.gov.cn/Service/CreditService.asmx/searchOrgWithPage',
                bodyfunc=
                lambda page, response=None: json.dumps({"condition":{"qymc":"公司","cydw":""},"pageNo":str(page),"pageSize":"100","count":"2466182"}),
                divmod=100,
                redis_conn=self.r,
                redis_flag=True,
                response_type='xpath')
        for req in reqs:
            yield req


    @SpiderHelp.check_response
    def guizhou_basic_info_info(self, response):
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'regex1',
                'db': 'CreditDataBase.Guizhou_BasicData',
                'keys': ['CompanyName'],
                'check': 'CompanyName',
                'conn': conn_flag
            },
            'response_type':
                'xpath',
            'data': [
                {
                    'n': '公司名称',
                    'En': 'CompanyName',
                    'v': 'gs_jbxxdata.*?\\"mc\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': 'HTML_ID',
                    'En': 'HTML_ID',
                    'v': 'gs_jbxxdata.*?\\"nbxh\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '统一社会信用代码',
                    'En': 'UnifiedSocialCreditCode',
                    'v': 'gs_jbxxdata.*?\\"gszch\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '住所',
                    'En': 'Address',
                    'v': 'gs_jbxxdata.*?\\"zs\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },
                {
                    'n': '法定代表人',
                    'En': 'NameOfLegalRepresentative',
                    'v': 'gs_jbxxdata.*?\\"fddbr\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },
                {
                    'n': '经济类型',
                    'En': 'SubjectType',
                    'v': 'gs_jbxxdata.*?\\"jjxz\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },
                {
                    'n': '经营范围',
                    'En': 'ScopeOfOperation',
                    'v': 'gs_jbxxdata.*?\\"jyfw\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },
                {
                    'n': '行业代码',
                    'En': 'IndustryCode',
                    'v': 'gs_jbxxdata.*?\\"hydm\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '成立日期',
                    'En': 'SetupTime',
                    'v': 'gs_jbxxdata.*?\\"clrq\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '登记机关',
                    'En': 'RegistrationAuthority',
                    'v': 'gs_jbxxdata.*?\\"djjg\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '状态',
                    'En': 'State',
                    'v': 'gs_jbxxdata.*?\\"ztzt\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '注销日期',
                    'En': 'LogoutDate',
                    'v': 'gs_jbxxdata.*?\\"zxrq\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '吊销日期',
                    'En': 'RevocationDate',
                    'v': 'gs_jbxxdata.*?\\"dxrq\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '公司类型',
                    'En': 'CompanyType',
                    'v': 'gs_jbxxdata.*?\\"ztlx\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '经营范围代码',
                    'En': 'ScopeOfOperationCode',
                    'v': 'gs_jbxxdata.*?\\"jyfwdm\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '注册资本',
                    'En': 'RegisteredCapital',
                    'v': 'gs_jbxxdata.*?\\"zczb\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '实收资本',
                    'En': 'CapitalCollection',
                    'v': 'gs_jbxxdata.*?\\"sszb\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '联系电话',
                    'En': 'ContactNumber',
                    'v': 'gs_jbxxdata.*?\\"lxdh\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '区划',
                    'En': 'AreaName',
                    'v': 'gs_jbxxdata.*?\\"zsxzqh\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },{
                    'n': '币种',
                    'En': 'Currency',
                    'v': 'gs_jbxxdata.*?\\"bz\\\\\":\\\\\"(.*?)\\\\\"',
                    't': 'regex1'
                },
            ]
        }]

        results = self.item_parse(_configs, response)
        for item in results:
            yield item

# if __name__ == '__main__':
#     Run = CreditspiderSpider()
#     reqs = Run._start_requests()
#     for req in reqs:
#         pass