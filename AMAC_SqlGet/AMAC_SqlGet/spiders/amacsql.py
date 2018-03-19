# -*- coding: utf-8 -*-
import scrapy
import urllib.parse
import random
import json
import time
from user_agent import generate_user_agent as ua
from myselector import Selector as S
from Help import *


def hdr1():
    headers = {
        'User-Agent': ua(os=('win', )),
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    return headers


def hdr2():
    headers = {
        'User-Agent': ua(os=('win', )),
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/json'
    }
    return headers


class AmacsqlSpider(scrapy.Spider, other):
    '''次爬虫的逻辑为列表页一次性获取,可能会失效'''
    name = "amacsql"
    allowed_domains = ["amac.org.cn"]
    start_urls = [
        'http://person.amac.org.cn/pages/registration/train-line-register!search.action',
        'http://ba.amac.org.cn/pages/amacWeb/ab-special-plan!list.action',
        'http://ba.amac.org.cn/pages/amacWeb/user!search.action',  ###finshed
        'http://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand={rand}&page=0&size=100000',
        'http://gs.amac.org.cn/amac-infodisc/api/aoin/product?rand={rand}&page=0&size=100000',
        'http://gs.amac.org.cn/amac-infodisc/api/fund/account?rand={rand}&page=0&size=100000',
        'http://person.amac.org.cn/pages/registration/train-line-register!list.action',
        'http://gs.amac.org.cn/amac-infodisc/api/pof/manager?rand={rand}&page=0&size=100000'
    ]
    custom_settings = {
        'DEPTH_PRIORITY': -1,
    }

    def start_requests(self):
        for url in self.start_urls:
            ###基金从业资格  从业资格证书信息  个人列表页
            #            if url == 'http://person.amac.org.cn/pages/registration/train-line-register!search.action':
            #                ##公司资格证书  公司类型
            #                data2 = {'filter_EQS_AOI_ID':'',#699085
            #                        'sqlkey':'registration',
            #                        'sqlval':'SERAOI_TYPE'}
            #                yield scrapy.Request(url,
            #                                     body = urllib.parse.urlencode(data2),
            #                                     headers= hdr1(),
            #                                     method = 'POST',
            #                                     dont_filter=True,
            #                                     callback = self.Corp_Employee_Stat2InfoParse
            #                                     )

            if url == 'http://ba.amac.org.cn/pages/amacWeb/ab-special-plan!list.action':  ####
                '''√'''
                ####资产支持专项计划 列表页一次性获取 无详情页
                data1 = {
                    'filter_LIKES_ASPI_NAME': '',
                    'filter_GES_AT_AUDIT_DATE': '',
                    'filter_LES_AT_AUDIT_DATE': '',
                    'page.searchFileName': 'publicity_abs_web',
                    'page.sqlKey': 'PAGE_ABS_PUBLICITY_WEB',
                    'page.sqlCKey': 'SIZE_ABS_PUBLICITY_WEB',
                    '_search': 'false',
                    'nd': '1510028433413',
                    'page.pageSize': '10000',
                    'page.pageNo': '1',
                    'page.orderBy': 'AT_AUDIT_DATE',
                    'page.order': 'desc'
                }
                yield scrapy.Request(
                    url,
                    body=urllib.parse.urlencode(data1),
                    headers=hdr1(),
                    method='POST',
                    dont_filter=True,
                    callback=self.amac_abs_proInfoParse)

            if url == 'http://ba.amac.org.cn/pages/amacWeb/user!search.action':
                '''√'''
                ###证券公司私募产品详情页 一次性获取
                data1 = {
                    'filter_EQS_MPI_ID': '',  #86766
                    'sqlkey': 'publicity_web',
                    'sqlval': 'GET_PUBLICITY_WEB_BY_MPI_ID'
                }
                yield scrapy.Request(
                    url,
                    body=urllib.parse.urlencode(data1),
                    headers=hdr1(),
                    method='POST',
                    dont_filter=True,
                    callback=self.amac_securities_proInfoParse)

                ##期货资产管理计划详细信息详情页  一次性获取
                data2 = {
                    'filter_EQS_MPI_ID': '',  #86766
                    'sqlkey': 'publicity_web',
                    'sqlval': 'GET_QH_WEB_BY_MPI_ID'
                }
                yield scrapy.Request(
                    url,
                    body=urllib.parse.urlencode(data2),
                    headers=hdr1(),
                    method='POST',
                    dont_filter=True,
                    callback=self.amac_Futures_manageInfoParse)

            if url == 'http://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand={rand}&page=0&size=100000':
                data1 = json.dumps({})
                #私募基金管理人基金产品 列表页  一次性获取
                #详情页未找到捷径   ------------------------------------------------------------------------
                yield scrapy.Request(
                    url.format(rand=random.random()),
                    body=data1,
                    headers=hdr2(),
                    method='POST',
                    dont_filter=True,
                    callback=self.amac_fund_proListParse)

            if url == 'http://gs.amac.org.cn/amac-infodisc/api/aoin/product?rand={rand}&page=0&size=100000':
                data1 = json.dumps({})
                #证券公司直投基金 列表页一次性获取
                #详情页未找到捷径   ------------------------------------------------------------------------
                yield scrapy.Request(
                    url.format(rand=random.random()),
                    body=data1,
                    headers=hdr2(),
                    method='POST',
                    dont_filter=True,
                    callback=self.amac_direct_fundListParse)

            if url == 'http://gs.amac.org.cn/amac-infodisc/api/fund/account?rand={rand}&page=0&size=100000':
                data1 = json.dumps({})
                #基金专户产品 列表页一次性获取
                #详情页未找到捷径   ------------------------------------------------------------------------
                yield scrapy.Request(
                    url.format(rand=random.random()),
                    body=data1,
                    headers=hdr2(),
                    method='POST',
                    dont_filter=True,
                    callback=self.amac_account_proListParse)

            if url == 'http://person.amac.org.cn/pages/registration/train-line-register!list.action':
                ###基金从业人员   公司概览列表页 ---所有机构
                data1 = {
                    'filter_EQS_OTC_ID': '',  #01
                    'filter_LIKES_AOI_NAME': '',
                    'page.searchFileName': 'registration',
                    'page.sqlKey': 'SELECT_LINE_PERSON_LIST',
                    'page.sqlCKey': 'SELECT_LINE_PERSON_SIZE',
                    '_search': 'false',
                    'nd': str(int(time.time() * 1000)),
                    'page.pageSize': '100000',
                    'page.pageNo': '1',
                    'page.orderBy': 'AOI.AOI_NAME',
                    'page.order': 'desc'
                }
                yield scrapy.Request(
                    url,
                    body=urllib.parse.urlencode(data1),
                    headers=hdr1(),
                    method='POST',
                    dont_filter=True,
                    callback=self.Corp_Employee_StatListParse)

            if url == 'http://gs.amac.org.cn/amac-infodisc/api/pof/manager?rand={rand}&page=0&size=100000':
                ####私募基金管理人    列表页 一次性获取   ###详情页暂无方案
                data1 = json.dumps({})
                yield scrapy.Request(
                    url.format(rand=random.random()),
                    body=data1,
                    headers=hdr2(),
                    method='POST',
                    dont_filter=True,
                    callback=self.ManagerListParse)

    def parse(self, response):
        pass

    def amac_fund_proListParse(self, response):
        request = checkTimeError(response, txt='setTime')
        if request:
            yield request
            return False
        JS = json.loads(response.text)
        #url地址在content/url下
        for json_ in JS['content']:
            url = urllib.parse.urljoin(
                'http://gs.amac.org.cn/amac-infodisc/res/pof/fund/index.html',
                json_['url'])

            yield scrapy.Request(
                url,
                headers=hdr1(),
                method='GET',
                callback=self.amac_fund_proInfoParse,
                priority=10)

    def amac_fund_proInfoParse(self, response):
        request = checkTimeError(response, txt='setTime')
        if request:
            yield request
            return False
        configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'amac_fund_pro',
                'keys': ['fundName', 'fundNo', 'managerName'],
                'check': 'fundName'
            },
            'data': [
                {
                    'n':
                    '基金备案号',
                    'En':
                    'fundNo',
                    'v':
                    '//tr[td[contains(text(),"基金编号")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金名称',
                    'En':
                    'fundName',
                    'v':
                    '//tr[td[contains(text(),"基金名称")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金管理公司',
                    'En':
                    'managerName',
                    'v':
                    '//tr[td[contains(text(),"基金管理人")]]/td[@class="td-content"]/a/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '管理类型',
                    'En':
                    'managerType',
                    'v':
                    '//tr[td[contains(text(),"管理类型")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n': '基金管理人ID',
                    'En': 'managerID',
                    'v': '基金管理人名称.*?manager\/(\d+?)\.',
                    't': 'regex1'
                },
                {
                    'n':
                    '托管人名称',
                    'En':
                    'mandatorName',
                    'v':
                    '//tr[td[contains(text(),"托管人名称")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n': '基金ID',
                    'En': 'fundID',
                    'v': 'fund\/(\d+)\.',
                    't': 'url_re'
                },
                {
                    'n':
                    '成立时间',
                    'En':
                    'setup_date',
                    'v':
                    '//tr[td[contains(text(),"成立时间")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '备案时间',
                    'En':
                    'record_date',
                    'v':
                    '//tr[td[contains(text(),"备案时间")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金备案阶段',
                    'En':
                    'record_stage',
                    'v':
                    '//tr[td[contains(text(),"基金备案阶段")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金类型',
                    'En':
                    'fund_type',
                    'v':
                    '//tr[td[contains(text(),"基金类型")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '运作状态',
                    'En':
                    'status',
                    'v':
                    '//tr[td[contains(text(),"运作状态")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '币种',
                    'En':
                    'currency',
                    'v':
                    '//tr[td[contains(text(),"币种")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金信息最后更新时间',
                    'En':
                    'lastupdateTime',
                    'v':
                    '//tr[td[contains(text(),"基金信息最后更新时间")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金协会特别提示',
                    'En':
                    'special_note',
                    'v':
                    '//tr[td[contains(text(),"基金协会特别提示")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n': '月报应披露',
                    'En': 'month_should_reveal',
                    'v': '>月报.*?应披露(\d+)条',
                    't': 'regex1'
                },
                {
                    'n': '月报按时披露',
                    'En': 'month_reveal_intime',
                    'v': '>月报.*?按时披露(\d+)条',
                    't': 'regex1'
                },
                {
                    'n': '月报未披露',
                    'En': 'month_None_reveal',
                    'v': '>月报.*?未披露(\d+)条',
                    't': 'regex1'
                },
                {
                    'n': '半年报应披露',
                    'En': 'halfYear_should_reveal',
                    'v': '>半年报.*?应披露(\d+)条',
                    't': 'regex1'
                },
                {
                    'n': '半年报按时披露',
                    'En': 'halfYear_reveal_intime',
                    'v': '>半年报.*?按时披露(\d+)条',
                    't': 'regex1'
                },
                {
                    'n': '半年报未披露',
                    'En': 'halfYear_None_reveal',
                    'v': '>半年报.*?未披露(\d+)条',
                    't': 'regex1'
                },
                {
                    'n': '年报应披露',
                    'En': 'Year_should_reveal',
                    'v': '>年报.*?应披露(\d+)条',
                    't': 'regex1'
                },
                {
                    'n': '年报按时披露',
                    'En': 'Year_reveal_intime',
                    'v': '>年报.*?按时披露(\d+)条',
                    't': 'regex1'
                },
                {
                    'n': '年报未披露',
                    'En': 'Year_None_reveal',
                    'v': '>年报.*?未披露(\d+)条',
                    't': 'regex1'
                },
                {
                    'n': '季报应披露',
                    'En': 'quarter_should_reveal',
                    'v': '>季报.*?应披露(\d+)条',
                    't': 'regex1'
                },
                {
                    'n': '季报按时披露',
                    'En': 'quarter_reveal_intime',
                    'v': '>季报.*?按时披露(\d+)条',
                    't': 'regex1'
                },
                {
                    'n': '季报未披露',
                    'En': 'quarter_None_reveal',
                    'v': '>季报.*?未披露(\d+)条',
                    't': 'regex1'
                },
            ]
        }]
        items = self.configParse(configs, response, response)
        for item in items.__iter__():
            item_ = item
            yield item_

    def amac_direct_fundListParse(self, response):
        request = checkTimeError(response, txt='setTime')
        if request:
            yield request
            return False
        JS = json.loads(response.text)
        for json_ in JS['content']:
            id_ = json_['id']
            url = 'http://gs.amac.org.cn/amac-infodisc/res/aoin/product/%s.html' % id_
            yield scrapy.Request(
                url,
                headers=hdr1(),
                method='GET',
                callback=self.amac_direct_fundInfoParse,
                priority=10)

    def amac_direct_fundInfoParse(self, response):
        request = checkTimeError(response, txt='setTime')
        if request:
            yield request
            return False
        configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'amac_direct_fund',
                'keys': ['pro_name', 'pro_No', 'manager_name'],
                'check': 'pro_name'
            },
            'data': [
                {
                    'n':
                    '产品名称',
                    'En':
                    'pro_name',
                    'v':
                    '//tr[td[contains(text(),"产品名称")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n': '产品ID',
                    'En': 'pro_id',
                    'v': 'product\/(\d+)\.html',
                    't': 'url_re'
                },
                {
                    'n':
                    '产品编码',
                    'En':
                    'pro_No',
                    'v':
                    '//tr[td[contains(text(),"产品编码")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '直投子公司名称',
                    'En':
                    'dirct_ep_name',
                    'v':
                    '//tr[td[contains(text(),"直投子公司名称")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '管理机构名称',
                    'En':
                    'manager_name',
                    'v':
                    '//tr[td[contains(text(),"管理机构名称")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '设立日期',
                    'En':
                    'setup_date',
                    'v':
                    '//tr[td[contains(text(),"设立日期")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '备案日期',
                    'En':
                    'record_date',
                    'v':
                    '//tr[td[contains(text(),"备案日期")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '基金类型',
                    'En':
                    'fund_type',
                    'v':
                    '//tr[td[contains(text(),"基金类型")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '组织形式',
                    'En':
                    'party_form',
                    'v':
                    '//tr[td[contains(text(),"组织形式")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '运作状态',
                    'En':
                    'operation_status',
                    'v':
                    '//tr[td[contains(text(),"运作状态")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '是否托管',
                    'En':
                    'is_truesteeship',
                    'v':
                    '//tr[td[contains(text(),"是否托管")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '托管人名称',
                    'En':
                    'custodian',
                    'v':
                    '//tr[td[contains(text(),"托管人名称")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        items = self.configParse(configs, response, response)
        for item in items.__iter__():
            item_ = item
            yield item_

    def amac_account_proListParse(self, response):
        request = checkTimeError(response, txt='setTime')
        if request:
            yield request
            return False
        JS = json.loads(response.text)
        for json_ in JS['content']:
            id_ = json_['id']
            type_ = json_['type']
            url = 'http://gs.amac.org.cn/amac-infodisc/res/fund/account/%s.html' % id_
            yield scrapy.Request(
                url,
                headers=hdr1(),
                method='GET',
                callback=self.amac_account_proInfoParse,
                meta={'type_': type_},
                priority=10)

    def amac_account_proInfoParse(self, response):
        request = checkTimeError(response, txt='setTime')
        if request:
            yield request
            return False
        configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'amac_account_pro',
                'keys': ['account_name', 'record_No', 'manager_name'],
                'check': 'account_name'
            },
            'data': [
                {
                    'n':
                    '专户名称',
                    'En':
                    'account_name',
                    'v':
                    '//tr[td[contains(text(),"专户名称")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '备案编码',
                    'En':
                    'record_No',
                    'v':
                    '//tr[td[contains(text(),"备案编码")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '管理人名称',
                    'En':
                    'manager_name',
                    'v':
                    '//tr[td[contains(text(),"管理人名称")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '托管人名称',
                    'En':
                    'custofian_name',
                    'v':
                    '//tr[td[contains(text(),"托管人名称")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '备案日期',
                    'En':
                    'record_date',
                    'v':
                    '//tr[td[contains(text(),"备案日期")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '合同期限（月）',
                    'En':
                    'contract_period',
                    'v':
                    '//tr[td[contains(text(),"合同期限")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '起始规模（亿元）',
                    'En':
                    'start_scale',
                    'v':
                    '//tr[td[contains(text(),"起始规模")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '是否分级',
                    'En':
                    'is_graded',
                    'v':
                    '//tr[td[contains(text(),"是否分级")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '成立时投资者数量',
                    'En':
                    'investor_nums',
                    'v':
                    '//tr[td[contains(text(),"成立时投资者数量")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '非专项资产管理计划产品类型',
                    'En':
                    'pro_type',
                    'v':
                    '//tr[td[contains(text(),"非专项资产管理计划产品类型")]]/td[@class="td-content"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n': '投资范围及比例',
                    'En': 'fields',
                    'v': '投资范围及比例<\/td>[^<]*?<td[^<]*?>(.*?)<',
                    't': 'regex1'
                },
                {
                    'n': '类型',
                    'En': 'type_',
                    'v': 'type_',
                    't': 'meta'
                },
                {
                    'n': 'pro_id',
                    'En': 'pro_id',
                    'v': 'account\/(.*?)\.html',
                    't': 'url_re'
                },
            ]
        }]
        items = self.configParse(configs, response, response)
        for item in items.__iter__():
            item_ = item
            yield item_

    def Corp_Employee_StatListParse(self, response):
        request = checkTimeError(response, txt='setTime')
        if request:
            yield request
            return False
        JS = json.loads(response.text)
        configs = [{
            'list': {
                'n': '',
                'v': 'result',
                't': 'json',
                'db': 'Corp_Employee_Stat',
                'keys': ['CorpRawID'],
                'check': 'CorpFullName'
            },
            'data': [
                {
                    'n': '机构ID',
                    'En': 'CorpRawID',
                    'v': 'AOI_ID',
                    't': 'json'
                },
                {
                    'n': '机构名称',
                    'En': 'CorpFullName',
                    'v': 'AOI_NAME',
                    't': 'json'
                },
                {
                    'n': '人员数量',
                    'En': 'EmployeeCount',
                    'v': 'PR_COUNT_PERSON',
                    't': 'json'
                },
                {
                    'n': '基金从业人员数量',
                    'En': 'FundQualificationCount',
                    'v': 'PTI0PERSON',
                    't': 'json'
                },
                {
                    'n': '基金销售资格人数',
                    'En': 'SaleQualificationCount',
                    'v': 'PTI2PERSON',
                    't': 'json'
                },
                {
                    'n': '其他从业资格人数',
                    'En': 'OtherQualificationCount',
                    'v': 'PTI3PERSON',
                    't': 'json'
                },
                {
                    'n': 'PE/VC从业资格人数',
                    'En': 'PEQualificationCount',
                    'v': 'PTI4PERSON',
                    't': 'json'
                },
                {
                    'n': '合规风控负责人人数',
                    'En': 'RiskEmployeeCount',
                    'v': 'PTI6PERSON',
                    't': 'json'
                },
                {
                    'n': '基金投资顾问人数',
                    'En': 'FundInvestAdviserCount',
                    'v': 'PTI7PERSON',
                    't': 'json'
                },
                {
                    'n': '基金经理人数',
                    'En': 'FundManagerCount',
                    'v': 'PTI8PERSON',
                    't': 'json'
                },
                {
                    'n': '投资经理人数',
                    'En': 'InvestManagerCount',
                    'v': 'PTI9PERSON',
                    't': 'json'
                },
                {
                    'n': '投资总监人数',
                    'En': 'InvestDirectorCount',
                    'v': 'PTI10PERSON',
                    't': 'json'
                },
            ]
        }]

        items = self.configParse(configs, JS, response)
        for item in items.__iter__():
            item_ = item
            #            yield item_
            url = 'http://person.amac.org.cn/pages/registration/train-line-register!search.action'
            data = {
                'filter_EQS_PTI_ID': '',
                'filter_EQS_AOI_ID': item_['result']['CorpRawID'],
                'ORDERNAME': 'PP#PTI_ID,PP#PPP_NAME',
                'ORDER': 'ASC',
                'sqlkey': 'registration',
                'sqlval': 'SEARCH_FINISH_PUBLICITY'
            }
            yield scrapy.Request(
                url,
                body=urllib.parse.urlencode(data),
                headers=hdr1(),
                method='POST',
                callback=self.ManagerPerListParse,
                priority=10)

    def ManagerPerListParse(self, response):
        request = checkTimeError(response, txt='setTime')
        if request:
            yield request
            return False
        JS = json.loads(response.text)
        for json_ in JS:
            ##个人ID参数在 RPI_ID 里
            EmpID = json_['RPI_ID']  #str
            ###注册变更记录
            ChangeInformationCount = json_['COUNTCER']  #str
            CreditTip = json_['COUNTCX']
            url = 'http://person.amac.org.cn/pages/registration/train-line-register!search.action'
            data = {
                'filter_EQS_RPI_ID': EmpID,
                'sqlkey': 'registration',
                'sqlval': 'SELECT_PERSON_INFO'
            }
            yield scrapy.Request(
                url,
                body=urllib.parse.urlencode(data),
                headers=hdr1(),
                method='POST',
                meta={
                    'EmpID': EmpID,
                    'ChangeInformationCount': ChangeInformationCount
                },
                callback=self.Corp_EmployeeInfoParse,
                priority=20)
            data_ = {
                'filter_EQS_RH#RPI_ID': EmpID,
                'sqlkey': 'registration',
                'sqlval': 'SEARCH_LIST_BY_PERSON'
            }
            yield scrapy.Request(
                url,
                body=urllib.parse.urlencode(data_),
                headers=hdr1(),
                method='POST',
                meta={'EmpID': EmpID},
                callback=self.Corp_Employee_ChangeInfoParse,
                priority=20)

    def Corp_Employee_ChangeInfoParse(self, response):
        request = checkTimeError(response, txt='setTime')
        if request:
            yield request
            return False
        JS = json.loads(response.text)
        configs = [{
            'list': {
                'n': '',
                'v': '',
                't': '',
                'db': 'Corp_Employee_Change',
                'keys': ['EmpID', 'QualificationNo'],
                'check': 'CorpFullName'
            },
            'data': [
                {
                    'n': '人员ID',
                    'En': 'EmpID',
                    'v': 'EmpID',
                    't': 'meta'
                },
                {
                    'n': '从业机构',
                    'En': 'CorpFullName',
                    'v': 'AOI_NAME',
                    't': 'json'
                },
                {
                    'n': '从业资格类别',
                    'En': 'QualificationType',
                    'v': 'PTI_NAME',
                    't': 'json'
                },
                {
                    'n': '证书编号',
                    'En': 'QualificationNo',
                    'v': 'CER_NUM',
                    't': 'json'
                },
                {
                    'n': '取得日期',
                    'En': 'QualificationStartDate',
                    'v': 'OBTAIN_DATE',
                    't': 'json'
                },
                {
                    'n': '证书状态',
                    'En': 'QualificationStatus',
                    'v': 'CERTC_NAME',
                    't': 'json'
                },
            ]
        }]

        items = self.configParse(configs, JS, response)
        for item in items.__iter__():
            item_ = item
            yield item_

    def Corp_EmployeeInfoParse(self, response):
        request = checkTimeError(response, txt='setTime')
        if request:
            yield request
            return False
        JS = json.loads(response.text)
        configs = [{
            'list': {
                'n': '',
                'v': '',
                't': '',
                'db': 'Corp_Employee',
                'keys': ['EmpID'],
                'check': 'EmpFullName'
            },
            'data': [
                {
                    'n': '人员ID',
                    'En': 'EmpID',
                    'v': 'EmpID',
                    't': 'meta'
                },
                {
                    'n': '人员全称',
                    'En': 'EmpFullName',
                    'v': 'RPI_NAME',
                    't': 'json'
                },
                {
                    'n': '机构全称',
                    'En': 'CorpFullName',
                    'v': 'AOI_NAME',
                    't': 'json'
                },
                {
                    'n': '机构ID',
                    'En': 'CorpRawID',
                    'v': 'AOI_ID',
                    't': 'json'
                },
                {
                    'n': '部门名称',
                    'En': 'ADI_NAME',
                    'v': 'ADI_NAME',
                    't': 'json'
                },
                {
                    'n': '部门ID',
                    'En': 'ADI_ID',
                    'v': 'ADI_ID',
                    't': 'json'
                },
                {
                    'n': '性别',
                    'En': 'Gender',
                    'v': 'SCO_NAME',
                    't': 'json'
                },
                {
                    'n': '学历',
                    'En': 'Education',
                    'v': 'ECO_NAME',
                    't': 'json'
                },
                {
                    'n': '证书类型',
                    'En': 'QualificationType',
                    'v': 'PTI_NAME',
                    't': 'json'
                },
                {
                    'n': '证书编号',
                    'En': 'QualificationNo',
                    'v': 'CER_NUM',
                    't': 'json'
                },
                {
                    'n': '证书发布日期',
                    'En': 'QualificationStartDate',
                    'v': 'OBTAIN_DATE',
                    't': 'json'
                },
                {
                    'n': '证书截至有效日期',
                    'En': 'QualificationEndDate',
                    'v': 'ARRIVE_DATE',
                    't': 'json'
                },
                {
                    'n': '变更信息',
                    'En': 'ChangeInformationCount',
                    'v': 'ChangeInformationCount',
                    't': 'meta'
                },
                {
                    'n': '诚信记录',
                    'En': 'CreditTip',
                    'v': 'CreditTip',
                    't': 'meta'
                },
            ]
        }]

        items = self.configParse(configs, JS, response)
        for item in items.__iter__():
            item_ = item
            yield item_

    def ManagerListParse(self, response):
        request = checkTimeError(response, txt='setTime')
        if request:
            yield request
            return False
        JS = json.loads(response.text)
        for json_ in JS['content']:
            result = json_
            url = 'http://gs.amac.org.cn/amac-infodisc/res/pof/manager/%s.html' % result[
                'id']
            yield scrapy.Request(
                url,
                headers=hdr1(),
                method='GET',
                callback=self.ManagerInfoParse,
                meta=result,
                priority=10)

    def ManagerInfoParse(self, response):
        request = checkTimeError(response, txt='setTime')
        if request:
            yield request
            return False
        ##替换   html 特有 字符集
        __ = S.replace_invalid_html_char(response.text)
        response = response.replace(body=__)
        configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'dbo.AMAC_fundManager',
                'keys': ['fundManagerName', 'RegistrationNumber'],
                'check': 'fundManagerName'
            },
            'data': [{
                'n': '管理人webID',
                'En': 'webID',
                'v': 'manager\/(\d+)\.html',
                't': 'url_re'
            }, {
                'n':
                '基金管理人全称(中文)',
                'En':
                'fundManagerName',
                'v':
                '//tr[td[contains(text(),"基金管理人全称(中文)")]]/td[@class="td-content"]/div[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '基金管理人全称(英文)',
                'En':
                'fundManagerEname',
                'v':
                '//tr[td[contains(text(),"基金管理人全称(英文)")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '登记编号',
                'En':
                'RegistrationNumber',
                'v':
                '//tr[td[contains(text(),"登记编号")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '组织机构代码',
                'En':
                'OrganizationCode',
                'v':
                '//tr[td[contains(text(),"组织机构代码")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '登记时间',
                'En':
                'RegistrationDate',
                'v':
                '//tr[td[contains(text(),"登记时间")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '成立时间',
                'En':
                'setup_date',
                'v':
                '//tr[td[contains(text(),"成立时间")]]/td[@class="td-content"][2]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '注册地址',
                'En':
                'RegisteredAddress',
                'v':
                '//tr[td[contains(text(),"注册地址")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '办公地址',
                'En':
                'OfficeAddress',
                'v':
                '//tr[td[contains(text(),"办公地址")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '注册资本(万元)(人民币)',
                'En':
                'RegisteredCapital',
                'v':
                '//tr[td[contains(text(),"注册资本(万元)(人民币)")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '实缴资本(万元)(人民币)',
                'En':
                'PaidInCapital1',
                'v':
                '//tr[td[contains(text(),"实缴资本(万元)(人民币)")]]/td[@class="td-content"][2]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '企业性质',
                'En':
                'EnterpriseNature',
                'v':
                '//tr[td[contains(text(),"企业性质")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '注册资本实缴比例',
                'En':
                'PaidInProportion',
                'v':
                '//tr[td[contains(text(),"注册资本实缴比例")]]/td[@class="td-content"][2]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '机构类型',
                'En':
                'MechanismType',
                'v':
                '//tr[td[contains(text(),"机构类型")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '业务类型',
                'En':
                'BusinessType',
                'v':
                '//tr[td[contains(text(),"业务类型")]]/td[@class="td-content"][2]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '员工人数',
                'En':
                'EmployeesNumber',
                'v':
                '//tr[td[contains(text(),"员工人数")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n': '机构网址',
                'En': 'InstitutionalWebsite',
                'v': "机构网址.*?gotoWebsite\(\'(.*?)\'\)",
                't': 'regex1'
            }, {
                'n':
                '是否为会员',
                'En':
                'IsMember',
                'v':
                '//tr[td[contains(text(),"是否为会员")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '当前会员类型',
                'En':
                'MemberType',
                'v':
                '//tr[td[contains(text(),"当前会员类型")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '入会时间',
                'En':
                'InitiationDate',
                'v':
                '//tr[td[contains(text(),"入会时间")]]/td[@class="td-content"][2]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '法律意见书状态',
                'En':
                'LegalOpinionsStatus',
                'v':
                '//tr[td[contains(text(),"法律意见书状态")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '法定代表人/执行事务合伙人(委派代表)姓名',
                'En':
                'LegalRepresentative',
                'v':
                '//tr[td[contains(text(),"法定代表人/执行事务合伙人(委派代表)姓名")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '是否有从业资格',
                'En':
                'IsQualification',
                'v':
                '//tr[td[contains(text(),"是否有从业资格")]]/td[@class="td-content"][1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '资格取得方式',
                'En':
                'QualificationMethod',
                'v':
                '//tr[td[contains(text(),"资格取得方式")]]/td[@class="td-content"][2]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '机构信息最后更新时间',
                'En':
                'LastUpdateDate',
                'v':
                '//tr[td[contains(text(),"机构信息最后更新时间")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '特别提示信息',
                'En':
                'SpecialInformation',
                'v':
                '//tr[td[contains(text(),"特别提示信息")]]/td[@class="td-content"]/text()',
                't':
                'xpath_first'
            }, {
                'n': '失联机构',
                'En': 'LostContactMechanism',
                'v': '//td[span[text()="失联机构"]]//text()',
                't': 'xpath'
            }, {
                'n': '异常机构',
                'En': 'AbnormalMechanism',
                'v': '//td[span[text()="异常机构"]]//text()',
                't': 'xpath'
            }, {
                'n': '重大遗漏',
                'En': 'MajorOmission',
                'v': '//td[span[text()="重大遗漏"]]//text()',
                't': 'xpath'
            }, {
                'n': '虚假填报',
                'En': 'FalseFilling',
                'v': '//td[span[text()="虚假填报"]]//text()',
                't': 'xpath'
            }, {
                'n': '违反八条底线',
                'En': 'Violation8Baseline',
                'v': '//td[span[text()="违反八条底线"]]//text()',
                't': 'xpath'
            }, {
                'n': '不良诚信',
                'En': 'BadFaith',
                't': 'xpath',
                'v': '//td[span[text()="不良诚信"]]//text()'
            }, {
                'n': '基金数量',
                'En': 'fundCount',
                't': 'meta',
                'v': 'fundCount'
            }, {
                'n': '基金规模',
                'En': 'fundScale',
                't': 'meta',
                'v': 'fundScale'
            }, {
                'n': '是否有信用提示',
                'En': 'hasCreditTips',
                't': 'meta',
                'v': 'hasCreditTips'
            }, {
                'n': '是否有特别提示',
                'En': 'hasSpecialTips',
                't': 'meta',
                'v': 'hasSpecialTips'
            }, {
                'n': '登记省',
                'En': 'registerProvince',
                't': 'meta',
                'v': 'registerProvince'
            }, {
                'n': '是否在黑名单',
                'En': 'inBlacklist',
                't': 'meta',
                'v': 'inBlacklist'
            }, {
                'n': '管理人是否有产品',
                'En': 'managerHasProduct',
                't': 'meta',
                'v': 'managerHasProduct'
            }, {
                'n': '办公所在城市',
                'En': 'officeCity',
                't': 'meta',
                'v': 'officeCity'
            }, {
                'n': '办公点坐标',
                'En': 'officeCoordinate',
                't': 'meta',
                'v': 'officeCoordinate'
            }, {
                'n': '办公省份',
                'En': 'officeProvince',
                't': 'meta',
                'v': 'officeProvince'
            }, {
                'n': '实收资本',
                'En': 'paidInCapital',
                't': 'meta',
                'v': 'paidInCapital'
            }, {
                'n': '注册地址坐标',
                'En': 'regCoordinate',
                't': 'meta',
                'v': 'regCoordinate'
            }, {
                'n': '注册所在城市',
                'En': 'registerCity',
                't': 'meta',
                'v': 'registerCity'
            }, {
                'n': '认缴资本',
                'En': 'subscribedCapital',
                't': 'meta',
                'v': 'subscribedCapital'
            }]
        }]
        items = self.configParse(configs, response, response)
        for item in items.__iter__():
            item_ = item
            for k in [
                    'LostContactMechanism', 'AbnormalMechanism',
                    'MajorOmission', 'FalseFilling', 'Violation8Baseline',
                    'BadFaith'
            ]:
                item_['result'][k] = ''.join(item_['result'][k].re(
                    '[^\r|\t|\n]+')) if item_['result'][k] else '正常'
            yield item_

    def Corp_Employee_StatInfoParse(self, response):
        pass

    def amac_abs_proInfoParse(self, response):
        request = checkTimeError(response, txt='setTime')
        JS = json.loads(response.text)
        if request:
            yield request
            return False
        configs = [{
            'list': {
                'n': '',
                'v': 'result',
                't': 'json',
                'db': 'dbo.amac_abs_pro',
                'keys': ['abs_recode_No', 'abs_id', 'abs_manager'],
                'check': 'abs_name'
            },
            'data': [
                {
                    'n': 'abs_id',
                    'En': 'abs_id',
                    'v': 'ASPI_ID',
                    't': 'json'
                },
                {
                    'n': '专项计划全称',
                    'En': 'abs_name',
                    'v': 'ASPI_NAME',
                    't': 'json'
                },
                {
                    'n': '备案编号',
                    'En': 'abs_recode_No',
                    'v': 'ASPI_BA_NUMBER',
                    't': 'json'
                },
                {
                    'n': '管理人',
                    'En': 'abs_manager',
                    'v': 'ASPI_GL_NAME',
                    't': 'json'
                },
                {
                    'n': '托管人',
                    'En': 'abs_custofian',
                    'v': 'AII_TGR',
                    't': 'json'
                },
                {
                    'n': '备案通过时间',
                    'En': 'adopt_date',
                    'v': 'AT_AUDIT_DATE',
                    't': 'json'
                },
            ]
        }]

        items = self.configParse(configs, JS, response)
        for item in items.__iter__():
            yield item

    def amac_securities_proInfoParse(self, response):
        request = checkTimeError(response, txt='setTime')
        JS = json.loads(response.text)
        if request:
            yield request
            return False
        configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'json',
                'db': 'amac_securities_pro',
                'keys': ['pro_name', 'pro_No', 'manage_org'],
                'check': 'pro_name'
            },
            'data': [{
                'n': '产品ID',
                'En': 'pro_ID',
                'v': 'MPI_ID',
                't': 'json'
            }, {
                'n': '产品编码',
                'En': 'pro_No',
                'v': 'CPBM',
                't': 'json'
            }, {
                'n': '产品名称',
                'En': 'pro_name',
                'v': 'CPMC',
                't': 'json'
            }, {
                'n': '管理机构',
                'En': 'manage_org',
                'v': 'GLJG',
                't': 'json'
            }, {
                'n': '设立日期',
                'En': 'setup_date',
                'v': 'SLRQ',
                't': 'json'
            }, {
                'n': '到期日',
                'En': 'end_date',
                'v': 'DQR',
                't': 'json'
            }, {
                'n': '投资类型',
                'En': 'investment_type',
                'v': 'TZLX',
                't': 'json'
            }, {
                'n': '是否分级',
                'En': 'is_graded',
                'v': 'SFFJ',
                't': 'json'
            }, {
                'n': '管理方式',
                'En': 'manage_type',
                'v': 'GLFS',
                't': 'json'
            }, {
                'n': '成立规模',
                'En': 'setup_scale',
                'v': 'CLGM',
                't': 'json'
            }, {
                'n': '成立时参与户数',
                'En': 'setup_Nums',
                'v': 'CLSCYHS',
                't': 'json'
            }, {
                'n': '托管机构',
                'En': 'Trusteeship_org',
                'v': 'TGJG',
                't': 'json'
            }, {
                'n': '份额登记机构',
                'En': 'share_register_org',
                'v': 'FEDJJG',
                't': 'json'
            }, {
                'n': '投资范围',
                'En': 'investment_scope',
                'v': 'TZFW',
                't': 'json'
            }, {
                'n': 'PW_ID',
                'En': 'PW_ID',
                'v': 'PW_ID',
                't': 'json'
            }, {
                'n': 'PW_STATES',
                'En': 'PW_STATES',
                'v': 'PW_STATES',
                't': 'json'
            }]
        }]

        items = self.configParse(configs, JS, response)
        for item in items.__iter__():
            yield item

    def amac_Futures_manageInfoParse(self, response):
        request = checkTimeError(response, txt='setTime')
        JS = json.loads(response.text)
        if request:
            yield request
            return False
        configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'json',
                'db': 'dbo.amac_Futures_manage',
                'keys': ['pro_name', 'pro_No', 'manager'],
                'check': 'pro_name'
            },
            'data': [
                {
                    'n': '产品ID',
                    'En': 'pro_ID',
                    'v': 'MPI_ID',
                    't': 'json'
                },
                {
                    'n': '产品编码',
                    'En': 'pro_No',
                    'v': 'MPI_PRODUCT_CODE',
                    't': 'json'
                },
                {
                    'n': '产品名称',
                    'En': 'pro_name',
                    'v': 'MPI_NAME',
                    't': 'json'
                },
                {
                    'n': '管理人',
                    'En': 'manager',
                    'v': 'AOI_NAME',
                    't': 'json'
                },
                {
                    'n': '托管人',
                    'En': 'custofian',
                    'v': 'MPI_TRUSTEE',
                    't': 'json'
                },
                {
                    'n': '成立日期',
                    'En': 'setup_date',
                    'v': 'MPI_CREATE_DATE',
                    't': 'json'
                },
                {
                    'n': '投资类型',
                    'En': 'investment_type',
                    'v': 'TZLX',
                    't': 'json'
                },
                {
                    'n': '募集规模（万元）',
                    'En': 'collection_scale',
                    'v': 'MPI_TOTAL_MONEY',
                    't': 'json'
                },
                {
                    'n': '是否结构化',
                    'En': 'is_structured',
                    'v': 'SFJGH',
                    't': 'json'
                },
                {
                    'n': '初始委托人数量',
                    'En': 'start_client_nums',
                    'v': 'MPI_PARTICIPATION_USER',
                    't': 'json'
                },
                {
                    'n': '投资范围',
                    'En': 'investment_fields',
                    'v': 'MPI_GROUP_RATIO',
                    't': 'json'
                },
            ]
        }]

        items = self.configParse(configs, JS, response)
        for item in items.__iter__():
            yield item


if __name__ == '__main__':
    from yapf.yapflib.yapf_api import FormatFile  # reformat a file
    path = r'F:\gitwork\AMAC_SqlGet\AMAC_SqlGet\spiders\amacsql.py'
    FormatFile(path, in_place=True)