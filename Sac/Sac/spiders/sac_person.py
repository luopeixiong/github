# -*- coding: utf-8 -*-

import scrapy
from .myselector import Selector as S
import json
from user_agent import generate_user_agent
from Sac.items import SacItem
import time
import urllib.parse
from spiders.localConfigs import *
maxtry = 3


#构造页面检查方法,用于页面的重试
def trytime_(response):
    if response.meta.get('maxtrys'):
        response.meta['maxtrys'] += 1
    else:
        response.meta['maxtrys'] = 1
def gettrytime(response,maxtry=10):
    trytime_(response)
    if response.meta['maxtrys']<maxtry:
        return True
def checkTimeError(response,maxtry=3):
    flag = gettrytime(response,maxtry)
    if flag and 'setTimeout' in response.text:
        request = response.request.replace(dont_filter = True)
        return request
class SacPersonSpider(scrapy.Spider):
    """Spider Explain:this is for sac,
it has crawl person_info,
com_info,
inver_com_info，
Securities_info
爬虫说明如下：
该爬虫定向爬取sac证监会网站信息,
目前已完成部分为证券业从业资格信息，
1:证券公司基本信息，
2:以及证券投资咨询机构的基本信息，
3:证券评级机构基本信息
"""
    name = "sac"
    allowed_domains = ["sac.net.cn"]
    start_urls = [
                  'http://person.sac.net.cn/pages/registration/train-line-register!orderSearch.action',
                  'http://jg.sac.net.cn/pages/publicity/resource!search.action']
    custom_settings = {
                       'CONCURRENT_REQUESTS':8,
                       'DOWNLOAD_DELAY':0.2}
    def start_requests(self):
        print('Start Crawl  Object : %s'%self.__class__.__name__)
        print('the Object docment:%s'%self.__doc__)
        for url in self.start_urls:
            if url == 'http://person.sac.net.cn/pages/registration/train-line-register!orderSearch.action':
                
                '''从业资格证书列表页入口'''
                yield scrapy.FormRequest(url,
                                         formdata=data1,
                                         headers = {'User-Agent':generate_user_agent(os=('win',))},
                                         priority=1000)
#             if url == 'http://jg.sac.net.cn/pages/publicity/resource!search.action':
#                 '''证券公司信息列表页入口'''
#                 yield scrapy.FormRequest(url,
#                                          formdata=data2,
#                                          priority=True,
#                                          callback = self.orgListParse,
#                                          headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},)
#                 '''证券投资咨询公司信息列表页入口'''
#                 yield scrapy.FormRequest(url,
#                                          formdata=data3,
#                                          priority=True,
#                                          callback = self.EQS_sacListParse,
#                                          headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},)
# #                
#                 '''证券评级机构信息列表页入口'''
#                 yield scrapy.FormRequest(url,
#                                          formdata=data4,
#                                          priority=True,
#                                          callback = self.otcListParse,
#                                          headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},)
                
    def otcListParse(self, response):
        request = checkTimeError(response)
        if request:return request
        js = json.loads(response.text)
        for js_ in js:
            otcid = js_['AOI_ID']
            page = 1
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!search.action',
                                     formdata = {
                                                 'filter_EQS_aoi_id':str(otcid),
                                                'sqlkey':'info',
                                                'sqlval':'GET_ORG_INFO_AOIID'},
                                     callback = self.otcInfoParse1,
                                     meta = {'otcid':otcid},
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux')),
                                                'Connection':'keep-alive'},
                                     )
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!search.action',
                                    formdata={
                                            'filter_EQS_aoi_id':str(otcid),
                                            'sqlkey':'publicity',
                                            'sqlval':'ZX_EXECUTIVE_LIST'},
                                    callback = self.otcInfoParse4,
                                    meta = {'otcid':otcid},
                                    headers = {'User-Agent':generate_user_agent(os=('win','mac','linux')),
                                                'Connection':'keep-alive'},
                                     )
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!list.action',
                                    formdata={
                                            'filter_EQS_aoi_id':str(otcid),
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_PRACTITIONERS',
                                            'page.sqlCKey':'SIZE_PRACTITONERS',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':str(page),
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'},
                                    callback = self.otcInfoParse5,
                                    meta = {'otcid':otcid,'page':page},
                                    headers = {'User-Agent':generate_user_agent(os=('win','mac','linux')),
                                                'Connection':'keep-alive'},)
            
    def otcInfoParse5(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券评级机构--执业人员信息'''
        item = SacItem()
        page = response.meta['page']
        orgid = response.meta['otcid']
        js = json.loads(response.text)
        if page==1:
            totalPage = js['totalPages']
        else:
            totalPage = response.meta['totalPage']
        configs = otcInfoConfigs
        for js_ in js['result']:
            result = dict()
            result['orgid'] = orgid
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
                result[k] = S.replace_invalid_char(result[k])
            item['result'] = result
            item['keys'] = configs['list']['keys']
            item['db'] = configs['list']['db']
            yield item
        if page<totalPage:
            page+=1
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!list.action',
                                    formdata={
                                            'filter_EQS_aoi_id':str(orgid),
                                            'page.searchFileName':'publicity',
                                            'page.sqlKey':'PAG_PRACTITIONERS',
                                            'page.sqlCKey':'SIZE_PRACTITONERS',
                                            '_search':'false',
                                            'nd':str(int(time.time()*1000)),
                                            'page.pageSize':'15',
                                            'page.pageNo':str(page),
                                            'page.orderBy':'MATO_UPDATE_DATE',
                                            'page.order':'desc'},
                                    callback = self.otcInfoParse5,
                                    meta = {'otcid':orgid,'page':page,'totalPage':totalPage},
                                    headers = {'User-Agent':generate_user_agent(os=('win','mac','linux')),
                                                'Connection':'keep-alive'},)
    def otcInfoParse1(self, response):
        '''证券评级机构--基本信息1'''
        request = checkTimeError(response)
        if request:return request
        js = json.loads(response.text)
#        otcid = response.meta['otcid']
        
        configs = otcInfoBaseconfigs
        for js_ in js:
            result=dict()
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
                result[k] = S.replace_invalid_char(result[k])
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!search.action',
                                     formdata = {
                                                 'filter_EQS_aoi_id':str(result['orgid']),
                                                 'sqlkey':'publicity',
                                                 'sqlval':'SELECT_ZX_REG_INFO',
                                                 'Connection':'keep-alive'},
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},
                                     callback = self.otcInfoParse2,
                                     meta = {'result':result}
                                     )
        
    def otcInfoParse2(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券评级机构--基本信息2'''
        item = SacItem()
        js = json.loads(response.text)
        configs = otcInfoBaseconfigs2
        for js_ in js:
            result = response.meta['result']
            for config in configs['data']:
                k = config['En']  
                result[k] = S.select_content(js_, config)
                result[k] = S.replace_invalid_char(result[k])
            item['result'] = result
            item['keys'] = configs['list']['keys']
            item['db'] = configs['list']['db']
            yield item
            
            
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!search.action',
                                         formdata = {
                                                     'filter_EQS_mri_reg_id':str(result['REG_ID']),
                                                     'sqlkey':'info',
                                                     'sqlval':'GET_FILES_BY_REG_ID'},
                                         callback = self.otcInfoParse3,
                                         meta = {'orgid':result['orgid']},
                                         headers = {'User-Agent':generate_user_agent(os=('win','mac','linux')),
                                                    'Referer': 'http://jg.sac.net.cn/pages/publicity/credit_rating_reg.html?aoi_id={orgid}&is_org_search=no'.format(orgid=result['orgid']),
                                                    'Content-Type': 'application/x-www-form-urlencoded',
                                                    'Connection':'keep-alive'},
                                     )
    def otcInfoParse3(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券评级机构--执照图片'''
        item = SacItem()
        orgid = response.meta['orgid']
        js = json.loads(response.text)
        configs = {'list':{'v':'','t':'','keys':['REG_ID','ZRNI_NAME'],'db':'dbo.SAC_otclicenseCopy'},
                   'data':[{'n':'REGID','En':'REG_ID','t':'json','v':'MRI_REG_ID','dt':''},
                           {'n':'证书ID','En':'ZRNI_ID','t':'json','v':'ZRNI_ID','dt':''},
                           {'n':'证书name','En':'ZRNI_NAME','t':'json','v':'ZRNI_NAME','dt':''},
                           {'n':'证书path','En':'ZRNI_PATH','t':'json','v':'ZRNI_PATH','dt':''},
                           {'n':'证书类型','En':'ZRNI_TYPE','t':'json','v':'ZRNI_TYPE','dt':''},
                           ]
                   }
        for js_ in js:
            result = dict()
            result['orgid'] = orgid
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
                result[k] = S.replace_invalid_char(result[k])
            formtxt = 'http://jg.sac.net.cn/pages/publicity/train-line-register!writeFile.action?inputPath={path}&fileName={filename}'
            filename = urllib.parse.quote(urllib.parse.quote(result['ZRNI_NAME'].encode('utf-8')).encode('utf-8'))
            result['url'] = formtxt.format(path=result['ZRNI_PATH'],filename = filename)
            item['result'] = result
            item['keys'] = configs['list']['keys']
            item['db'] = configs['list']['db']
            yield item
    def otcInfoParse4(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券评级机构--高管人员信息'''
        item = SacItem()
        orgid = response.meta['otcid']
        js = json.loads(response.text)
        configs = {'list':{'v':'','t':'','keys':['NAME','orgid','PRACTITIONERS_START_DATE'],'db':'dbo.SAC_otcseniorExecutive'},
                   'data':[{'n':'中国注册会计师资格证书号码','En':'ACCOUNTANTS_NO','t':'json','v':'EI_ACCOUNTANTS_NO','dt':''},
                           {'n':'现任职务','En':'CURRENT_POSITION','t':'json','v':'EI_CURRENT_POSITION','dt':''},
                           {'n':'是否通过证券评级业务高级管理人员资质测试','En':'ISPASS_SENIOR_MANAGEMENT','t':'json','v':'EI_ISPASS_SENIOR_MANAGEMENT','dt':''},
                           {'n':'姓名','En':'NAME','t':'json','v':'EI_NAME','dt':''},
                           {'n':'任职起始时间','En':'PRACTITIONERS_START_DATE','t':'json','v':'EI_PRACTITIONERS_START_DATE','dt':''},
                           {'n':'证券从业人员证书号码','En':'SECURITIES_PROFESSIONALS','t':'json','v':'EI_SECURITIES_PROFESSIONALS','dt':''},
                           {'n':'性别','En':'Gender','t':'json','v':'GC_ID','dt':''}
                           ]
                   }
        for js_ in js:
            result = dict()
            result['orgid'] = orgid
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
                result[k] = S.replace_invalid_char(result[k])
            item['result'] = result
            item['keys'] = configs['list']['keys']
            item['db'] = configs['list']['db']
            yield item
    def EQS_sacListParse(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券投资咨询机构--列表页parse'''
        js = json.loads(response.text)
        for js_ in js:
            orgid = js_['AOI_ID']
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!search.action',
                                     callback = self.EQS_sacInfoParse,
                                     formdata = {
                                                'filter_EQS_aoi_id':str(orgid),
                                                'sqlkey':'info',
                                                'sqlval':'GET_ORG_INFO_AOIID'
                                                },
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},
                                     )
    def EQS_sacInfoParse(self, response):
        '''证券投资咨询机构--基本信息1'''
#        orgid = response.meta['orgid']
        js = json.loads(response.text)
        configs =  {'list':{'v':'','t':'','keys':'','db':''},
                   'data':[{'n':'机构ID','En':'orgid','t':'json','v':'AOI_ID','dt':''},
                           {'n':'会员编号','En':'MEMBER_NO','t':'json','v':'AOI_MEMBER_NO','dt':''},
                           {'n':'会员代码','En':'menber_code','t':'json','v':'AOI_NO','dt':''},
                           {'n':'机构代码','En':'org_No','t':'json','v':'AOI_ORG_NO','dt':''},
                           {'n':'会员级别','En':'OPC_NAME','t':'json','v':'OPC_NAME','dt':''},
                           ]
                   } 
        for js_ in js:
            result=dict()
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
                result[k] = S.replace_invalid_char(result[k])
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!search.action',
                                     formdata = {'filter_EQS_aoi_id':str(result['orgid']),
                                                'sqlkey':'publicity',
                                                'sqlval':'SELECT_TZ_REG_INFO'},
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},
                                     callback = self.EQS_sacInfoParse2,
                                     meta = {'result':result})
    def EQS_sacInfoParse2(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券投资咨询机构--基本信息2'''
        js = json.loads(response.text)
        item = SacItem()
        configs = EQS_sacInfoParse2Configs
        for js_ in js:
            result = response.meta['result']
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
                result[k] = S.replace_invalid_char(result[k])
            item['result'] = result
            item['keys'] = configs['list']['keys']
            item['db'] = configs['list']['db']
            yield item
    def orgListParse(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券公司--列表页parse'''
        js = json.loads(response.text)
        for orgid_ in js:
            orgid = orgid_['AOI_ID']
            page=1
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!search.action',
                                     formdata = {'filter_EQS_aoi_id':str(orgid),
                                                'sqlkey':'publicity',
                                                'sqlval':'SELECT_ZQ_REG_INFO'},
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},
                                     callback = self.orgInfoParse1,
                                     meta = {'orgid':orgid},
                                     )
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!list.action',
                                     formdata = {'filter_LIKES_mboi_branch_full_name':'',
                                                'filter_LIKES_mboi_off_address':'',
                                                'filter_EQS_aoi_id':str(orgid),
                                                'page.searchFileName':'publicity',
                                                'page.sqlKey':'PAG_BRANCH_ORG',
                                                'page.sqlCKey':'SIZE_BRANCH_ORG',
                                                '_search':'false',
                                                'nd':str(int(time.time()*1000)),
                                                'page.pageSize':'15',
                                                'page.pageNo':str(page),
                                                'page.orderBy':'MATO_UPDATE_DATE',
                                                'page.order':'desc'},
                                     meta = {'orgid':orgid,'page':1},
                                     callback = self.BRANCH_OrgParse,
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},)
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!list.action',
                                     formdata = {'filter_LIKES_msdi_name':'',
                                                'filter_LIKES_msdi_reg_address':'',
                                                'filter_EQS_aoi_id':str(orgid),
                                                'page.searchFileName':'publicity',
                                                'page.sqlKey':'PAG_SALES_DEPT',
                                                'page.sqlCKey':'SIZE_SALES_DEPT',
                                                '_search':'false',
                                                'nd':str(int(time.time()*1000)),
                                                'page.pageSize':'15',
                                                'page.pageNo':str(page),
                                                'page.orderBy':'MATO_UPDATE_DATE',
                                                'page.order':'desc'},
                                     meta = {'orgid':orgid,'page':1},
                                     callback = self.SALES_DEPTParse,
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},)
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!search.action',
                                     formdata = {'filter_EQS_aoi_id':str(orgid),
                                                'sqlkey':'publicity',
                                                'sqlval':'EXECUTIVE_LIST'},
                                     meta = {'orgid':orgid},
                                     callback = self.senior_executiveParse,
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},)
    def senior_executiveParse(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券公司--高管信息'''
        item = SacItem()
        orgid = response.meta['orgid']
        js = json.loads(response.text)
        configs = {'list':{'v':'','t':'','keys':['orgid','name','OFFICE_DATE','OFFICE_DATE'],'db':'dbo.SAC_executive'},
                   'data':[{'n':'现任职务','En':'CURRENT_POSITION','t':'json','v':'EI_CURRENT_POSITION','dt':''},
                           {'n':'姓名','En':'name','t':'json','v':'EI_NAME','dt':''},
                           {'n':'任职起始时间','En':'OFFICE_DATE','t':'json','v':'EI_OFFICE_DATE','dt':''},
                           {'n':'性别','En':'gender','t':'json','v':'GC_ID','dt':''},
                           ]
                   }
        for js_ in js:
            result=dict()
            result['orgid'] = orgid
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
                result[k] = S.replace_invalid_char(result[k])
            item['result'] = result
            item['keys'] = configs['list']['keys']
            item['db'] = configs['list']['db']
            yield item
        
    def SALES_DEPTParse(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券公司--营业部信息'''
        item = SacItem()
        orgid = response.meta['orgid']
        page = response.meta['page']
        js = json.loads(response.text)
        if page == 1:
            totalPage = js['totalPages']
        else:
            totalPage = response.meta['totalPage']
        configs = SALES_DEPTParseConfigs
        for js_ in js['result']:
            result = dict()
            result['orgid'] = orgid
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
                result[k] = S.replace_invalid_char(result[k])
            item['result'] = result
            item['keys'] = configs['list']['keys']
            item['db'] = configs['list']['db']
            yield item
        if page< totalPage:
            page+=1
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!list.action',
                                     formdata = {'filter_LIKES_msdi_name':'',
                                                'filter_LIKES_msdi_reg_address':'',
                                                'filter_EQS_aoi_id':str(orgid),
                                                'page.searchFileName':'publicity',
                                                'page.sqlKey':'PAG_SALES_DEPT',
                                                'page.sqlCKey':'SIZE_SALES_DEPT',
                                                '_search':'false',
                                                'nd':str(int(time.time()*1000)),
                                                'page.pageSize':'15',
                                                'page.pageNo':str(page),
                                                'page.orderBy':'MATO_UPDATE_DATE',
                                                'page.order':'desc'},
                                     meta = {'orgid':orgid,'page':page,'totalPage':totalPage},
                                     callback = self.SALES_DEPTParse,
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},)
    def BRANCH_OrgParse(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券公司--分公司信息'''
        item = SacItem()
        orgid = response.meta['orgid']
        page = response.meta['page']
        js = json.loads(response.text)
        if page == 1:
            totalPage = js['totalPages']
        else:
            totalPage = response.meta['totalPage']
        configs = BRANCH_OrgConfigs
        for js_ in js['result']:
            result=dict()
            result['orgid'] = orgid
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
                result[k] = S.replace_invalid_char(result[k])
            item['result'] = result
            item['keys'] = configs['list']['keys']
            item['db'] = configs['list']['db']
            yield item
        if page<=totalPage:
            page+=1
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!list.action',
                                     formdata = {'filter_LIKES_mboi_branch_full_name':'',
                                                'filter_LIKES_mboi_off_address':'',
                                                'filter_EQS_aoi_id':str(orgid),
                                                'page.searchFileName':'publicity',
                                                'page.sqlKey':'PAG_BRANCH_ORG',
                                                'page.sqlCKey':'SIZE_BRANCH_ORG',
                                                '_search':'false',
                                                'nd':str(int(time.time()*1000)),
                                                'page.pageSize':'15',
                                                'page.pageNo':str(page),
                                                'page.orderBy':'MATO_UPDATE_DATE',
                                                'page.order':'desc'},
                                     meta = {'orgid':orgid,'page':page,'totalPage':totalPage},
                                     callback = self.BRANCH_OrgParse,
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},)
    def orgInfoParse1(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券公司信息基本信息--result传入orgInfoParse2'''
        item = SacItem()
        orgid = response.meta['orgid']
        js = json.loads(response.text)
        configs = orgInfoparse1configs
        result = dict()
        for js_ in js:
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_    , config,response)
                result[k] = S.replace_invalid_char(result[k])
            data = {'filter_EQS_aoi_id':str(orgid),
                        'sqlkey':'publicity',
                        'sqlval':'SEARCH_ZQGS_QUALIFATION'}
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!search.action',
                                     formdata = data,
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},
                                     callback = self.orgInfoParse2,
                                     meta = {'orgid':orgid,'result':result},
                                     )
    def orgInfoParse2(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券公司信息获取经营范围'''
        item = SacItem()
        result = response.meta['result']
        result['orgid'] = response.meta['orgid']
        js = json.loads(response.text)
        PTSC_NAME = []
        for i in js:
            PTSC_NAME.append(i['PTSC_NAME'])
        result['ptsc'] = ','.join(PTSC_NAME)
        result['ptsc'] = S.replace_invalid_char(result['ptsc'])
        item['result'] = result
        item['keys'] = ['orgid']
        item['db'] = 'dbo.SAC_securitiesInfo'
        yield item

    def parse(self, response):
        request = checkTimeError(response)
        if request:return request
        '''从业资格证书--公司基本信息'''
        item = SacItem()
        js = json.loads(response.text)
        configs = configs1
        
        for json_ in js:
            result = dict()
            for config in configs['data']:
                result[config['En']] = json_[config['v']]
                result[config['En']] = S.replace_invalid_char(result[config['En']])
            item['result'] = result
            item['keys'] = configs['list']['keys']
            item['db'] = configs['list']['db']
            CropRowID = result['CropRowID']
            datas = asc_data(CropRowID)
            headers = {'User-Agent':generate_user_agent()}
            yield scrapy.FormRequest("http://person.sac.net.cn/pages/registration/train-line-register!search.action",
                                     formdata=datas[0],
                                     headers = headers,
                                     meta = {'CropRowID':CropRowID},
                                     priority=0,
                                     callback = self.cctparse)
            yield scrapy.FormRequest("http://person.sac.net.cn/pages/registration/train-line-register!search.action",
                                     formdata=datas[1],
                                     headers = headers,
                                     meta = {'CropRowID':CropRowID},
                                     priority=0,
                                     callback = self.cctparse)
            yield item
    def cctparse(self, response):
        request = checkTimeError(response)
        if request:return request
        '''个人证券从业信息列表页PARSE'''
        js = json.loads(response.text)
        configs = cctconfigs
        for json_ in js:
#            print(json_)
            headers  = {'User-Agent':generate_user_agent()}
            result = dict()
            for config in configs['data']:
                result[config['En']] = S.select_content(json_, config,response)
                result[config['En']] = S.replace_invalid_char(result[config['En']])
            EmpHashID = result['EmpHashID']
            data = {'filter_EQS_PPP_ID':EmpHashID,
                    'sqlkey':'registration',
                    'sqlval':'SD_A02Leiirkmuexe_b9ID'}
            yield scrapy.FormRequest('http://person.sac.net.cn/pages/registration/train-line-register!search.action',
                                     formdata = data,
                                     headers = headers,
                                     callback = self.getEmpIDparse,
                                     priority=2,
                                     meta = {'result':result}
                                     )
    def getEmpIDparse(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券从业资格-个人信息'''
        js = json.loads(response.text)
        headers  = {'User-Agent':generate_user_agent()}
        result = response.meta['result']
        if js:
            result['EmpID']  = js[0]['RPI_ID']
            data = {
                    'filter_EQS_RH#RPI_ID':result['EmpID'],
                    'sqlkey':'registration',
                    'sqlval':'SEARCH_LIST_BY_PERSON'}
            yield scrapy.FormRequest('http://person.sac.net.cn/pages/registration/train-line-register!search.action',
                                    formdata = data,
                                    headers = headers,
                                    callback = self.Employee_Change,
                                    priority=3,
                                    meta={'EmpID':result['EmpID']}
                                    )
            yield scrapy.Request('http://person.sac.net.cn/pages/registration/train-line-register!search.action?filter_EQS_RPI_ID={EMPID}&sqlkey=registration&sqlval=SELECT_PERSON_INFO'.format(EMPID=result['EmpID']),
                                 headers = headers,
                                 callback = self.Employee_InFo,
                                 priority=3,
                                 meta={'result':result}
                                 )
    def Employee_InFo(self, response):
        request = checkTimeError(response)
        if request:return request
        item = SacItem()
        try:
            js = json.loads(response.text)
            result = response.meta['result']
            for json_ in js:
                result['image'] = 'http://photo.sac.net.cn/sacmp/images/'+json_['RPI_PHOTO_PATH']
                result['ADI_NAME'] = json_['ADI_NAME']
                result['ADI_ID'] = json_['ADI_ID']
                item['result'] = result
                item['keys'] = cctconfigs['list']['keys']
                item['db'] = cctconfigs['list']['db']
                yield item
        except:
            msg = '%s%s'%(response.url,response.text)
            scrapy.log.msg(msg)
    def Employee_Change(self, response):
        request = checkTimeError(response)
        if request:return request
        '''证券从业资格-个人变更信息'''
        item = SacItem()
        js = json.loads(response.text)
        result = dict()
        configs = Employee_ChangeConfigs 
        for json_ in js:
            for config in configs['data']:
                result[config['En']] = S.select_content(json_, config,response)
                result[config['En']] = S.replace_invalid_char(result[config['En']])
            item['result'] = result
            item['keys'] = configs['list']['keys']
            item['db'] = configs['list']['db']
            yield item