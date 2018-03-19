# -*- coding: utf-8 -*-

import scrapy
from .myselector import Selector as S
import json
from user_agent import generate_user_agent
from Sac.items import SacItem
import time
import urllib.parse

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
    name = "sac_person"
    allowed_domains = ["sac.net.cn"]
    start_urls = [
                  'http://person.sac.net.cn/pages/registration/train-line-register!orderSearch.action',
                  'http://jg.sac.net.cn/pages/publicity/resource!search.action']
    def start_requests(self):
        print('Start Crawl  Object : %s'%self.__class__.__name__)
        print('the Object docment:%s'%self.__doc__)
        for url in self.start_urls:
            if url == 'http://person.sac.net.cn/pages/registration/train-line-register!orderSearch.action':
                data={
                        "filter_EQS_OTC_ID":"10",
                        "ORDERNAME":"AOI#AOI_NAME",
                        "ORDER":"ASC",
                        "sqlkey":"registration",
                        "sqlval":"SELECT_LINE_PERSON"
                        }
                '''从业资格证书列表页入口'''
                yield scrapy.FormRequest(url,
                                         formdata=data,
                                         headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},
                                         dont_filter=True)
            if url == 'http://jg.sac.net.cn/pages/publicity/resource!search.action':
                '''证券公司信息列表页入口'''
                data={
                    'filter_EQS_O#otc_id':'01',
                    'filter_EQS_O#sac_id':'',
                    'filter_LIKES_aoi_name':'',
                    'sqlkey':'publicity',
                    'sqlval':'ORG_BY_TYPE_INFO'
                    }
                yield scrapy.FormRequest(url,
                                         formdata=data,
                                         dont_filter=True,
                                         callback = self.orgListParse,
                                         headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},)

                data_ = {
                        'filter_EQS_sac_id':'',
                        'filter_LIKES_aoi_name':'',
                        'sqlkey':'publicity',
                        'sqlval':'ORG_BY_TYPE_INFO_TZZX'}
                '''证券投资咨询公司信息列表页入口'''
                yield scrapy.FormRequest(url,
                                         formdata=data_,
                                         dont_filter=True,
                                         callback = self.EQS_sacListParse,
                                         headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},)
                
                data_1 = {
                        'filter_EQS_O#otc_id':'03',
                        'filter_EQS_O#sac_id':'',
                        'filter_LIKES_aoi_name':'',
                        'sqlkey':'publicity',
                        'sqlval':'ORG_BY_TYPE_INFO'}    
                '''证券评级机构信息列表页入口'''
                yield scrapy.FormRequest(url,
                                         formdata=data_1,
                                         dont_filter=True,
                                         callback = self.otcListParse,
                                         headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},)
                
    def otcListParse(self, response):
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
        '''证券评级机构--执业人员信息'''
        page = response.meta['page']
        orgid = response.meta['otcid']
        js = json.loads(response.text)
        if page==1:
            totalPage = js['totalPages']
        else:
            totalPage = response.meta['totalPage']
        configs = {'list':{'v':'','t':''},
                   'data':[{'n':'性别','En':'Gender','t':'json','v':'GC_ID','dt':''},
                           {'n':'现任职务','En':'CURRENT_POSITION','t':'json','v':'MPTI_CURRENT_POSITION','dt':''},
                           {'n':'姓名','En':'NAME','t':'json','v':'MPTI_NAME','dt':''},
                           {'n':'执业时间','En':'PRACTICE_TIME','t':'json','v':'MPTI_PRACTICE_TIME','dt':''},
                           {'n':'从业资格','En':'QUALIFICATION_NO','t':'json','v':'MPTI_QUALIFICATION_NO','dt':''},
                           {'n':'备注','En':'REMARK','t':'json','v':'MPTI_REMARK','dt':''}
                           ]
                   }
        for js_ in js['result']:
            result = dict()
            result['orgid'] = orgid
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
            print(result)
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
        js = json.loads(response.text)
#        otcid = response.meta['otcid']
        configs = {'list':{'v':'','t':''},
                   'data':[{'n':'机构ID','En':'orgid','t':'json','v':'AOI_ID','dt':''},
                           {'n':'会员ID','En':'MEMBER_NO','t':'json','v':'AOI_MEMBER_NO','dt':''},
                           {'n':'会员代码','En':'orgNo','t':'json','v':'AOI_NO','dt':''},
                           {'n':'组织机构代码','En':'ORG_CODE','t':'json','v':'AOI_ORG_NO','dt':''},
                           {'n':'会员属性','En':'OPC_NAME','t':'json','v':'OPC_NAME','dt':''}
                           ]
                   }
        
        for js_ in js:
            result=dict()
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
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
        '''证券评级机构--基本信息2'''
        js = json.loads(response.text)
        print(js)
        configs = {'list':{'v':'','t':''},
                   'data':[{'n':'机构ID','En':'orgid','t':'json','v':'AOI_ID','dt':''},
                           {'n':'asc_id','En':'asc_id','t':'json','v':'ASC_ID','dt':''},
                           {'n':'是否关闭','En':'is_closed','t':'json','v':'IS_CLOSED','dt':''},
                           {'n':'入库时间','En':'ADD_DATE','t':'json','v':'MRI_ADD_DATE','dt':''},
                           {'n':'入库user','En':'ADD_USER','t':'json','v':'MRI_ADD_USER','dt':''},
                           {'n':'主席','En':'CHAIRMAN','t':'json','v':'MRI_CHAIRMAN','dt':''},
                           {'n':'中文简称','En':'CHINESE_ABBREVIATION','t':'json','v':'MRI_CHINESE_ABBREVIATION','dt':''},
                           {'n':'中文全称','En':'CHINESE_NAME','t':'json','v':'MRI_CHINESE_NAME','dt':''},
                           {'n':'投诉电话','En':'COMPLAINTS_TEL','t':'json','v':'MRI_COMPLAINTS_TEL','dt':''},
                           {'n':'公司Email1','En':'COM_EMAIL','t':'json','v':'MRI_COM_EMAIL','dt':''},
                           {'n':'公司历史？','En':'COM_HISTORY','t':'json','v':'MRI_COM_HISTORY','dt':''},
                           {'n':'公司网址','En':'COM_WEBSITE','t':'json','v':'MRI_COM_WEBSITE','dt':''},
                           {'n':'联系电话','En':'CONTACT_TEL','t':'json','v':'MRI_CONTACT_TEL','dt':''},
                           {'n':'员工人数','En':'CREDIT_EMP_NUM','t':'json','v':'MRI_CREDIT_EMP_NUM','dt':''},
                           {'n':'实收资本（万元）','En':'CREDIT_PAID_IN_CAPITAL','t':'json','v':'MRI_CREDIT_PAID_IN_CAPITAL','dt':''},
                           {'n':'客户服务电话','En':'CUSTOMER_SERVICE_TEL','t':'json','v':'MRI_CUSTOMER_SERVICE_TEL','dt':''},
                           {'n':'公司邮箱','En':'EMAIL','t':'json','v':'MRI_EMAIL','dt':''},
                           {'n':'英文缩写','En':'ENGLISH_ABBREVIATION','t':'json','v':'MRI_ENGLISH_ABBREVIATION','dt':''},
                           {'n':'英文名','En':'ENGLISH_NAME','t':'json','v':'MRI_ENGLISH_NAME','dt':''},
                           {'n':'传真','En':'FAX','t':'json','v':'MRI_FAX','dt':''},
                           {'n':'成立时间','En':'FOUND_DATE','t':'json','v':'MRI_FOUND_DATE','dt':''},
                           {'n':'主管部门','En':'GA_COMPETENT_DEPT','t':'json','v':'MRI_GA_COMPETENT_DEPT','dt':''},
                           {'n':'远程教育人员人数','En':'GA_FULLTIME_STAFF_NUM','t':'json','v':'MRI_GA_FULLTIME_STAFF_NUM','dt':''},
                           {'n':'成员数','En':'GA_MEM_NUM','t':'json','v':'MRI_GA_MEM_NUM','dt':''},
                           {'n':'权威注册','En':'GA_REG_AUTHORITY','t':'json','v':'MRI_GA_REG_AUTHORITY','dt':''},
                           {'n':'秘书长','En':'GA_SECRETARY_GENERAL','t':'json','v':'MRI_GA_SECRETARY_GENERAL','dt':''},
                           {'n':'(总裁)总经理','En':'GENERAL_MANAGER','t':'json','v':'MRI_GENERAL_MANAGER','dt':''},
                           {'n':'详细注册地址','En':'INFO_REG','t':'json','v':'MRI_INFO_REG','dt':''},
                           {'n':'是否上市','En':'IS_LISTED','t':'json','v':'MRI_IS_LISTED','dt':''},
                           {'n':'法定代表人','En':'LEGAL_REPRESENTATIVE','t':'json','v':'MRI_LEGAL_REPRESENTATIVE','dt':''},
                           {'n':'业务资格许可证编号','En':'LICENSE_CODE','t':'json','v':'MRI_LICENSE_CODE','dt':''},
                           {'n':'管理人','En':'MANAGER','t':'json','v':'MRI_MANAGER','dt':''},
                           {'n':'净资产','En':'NET_ASSETS','t':'json','v':'MRI_NET_ASSETS','dt':''},
                           {'n':'办公地址','En':'OFFICE_ADDRESS','t':'json','v':'MRI_OFFICE_ADDRESS','dt':''},
                           {'n':'办公地址邮编','En':'OFFICE_ZIP_CODE','t':'json','v':'MRI_OFFICE_ZIP_CODE','dt':''},
                           {'n':'组织机构代码','En':'ORG_CODE','t':'json','v':'MRI_ORG_CODE','dt':''},
                           {'n':'机构','En':'ORG_STUCTURE','t':'json','v':'MRI_ORG_STUCTURE','dt':''},
                           {'n':'QI_TA','En':'QI_TA','t':'json','v':'MRI_QI_TA','dt':''},
                           {'n':'注册资本','En':'REG_CAPITAL','t':'json','v':'MRI_REG_CAPITAL','dt':''},
                           {'n':'注册ID','En':'REG_ID','t':'json','v':'MRI_REG_ID','dt':''},
                           {'n':'注册版本ID','En':'REG_VER_ID','t':'json','v':'MRI_REG_VER_ID','dt':''},
                           {'n':'注册地邮编','En':'REG_ZIP_CODE','t':'json','v':'MRI_REG_ZIP_CODE','dt':''},
                           {'n':'备注','En':'REMARK','t':'json','v':'MRI_REMARK','dt':''},
                           {'n':'销售部数量','En':'SALES_DEPT_NUM','t':'json','v':'MRI_SALES_DEPT_NUM','dt':''},
                           {'n':'证券业务','En':'SECURITIES_BUSINESS','t':'json','v':'MRI_SECURITIES_BUSINESS','dt':''},
                           {'n':'证券业务代码','En':'SECURITIES_BUSINESS_CODE','t':'json','v':'MRI_SECURITIES_BUSINESS_CODE','dt':''},
                           {'n':'证券资格','En':'SECURITIES_ELIGIBLE','t':'json','v':'MRI_SECURITIES_ELIGIBLE','dt':''},
                           {'n':'上市编码','En':'SHANG_SHI_CODE','t':'json','v':'MRI_SHANG_SHI_CODE','dt':''},
                           {'n':'上市DI','En':'SHANG_SHI_DI','t':'json','v':'MRI_SHANG_SHI_DI','dt':''},
                           {'n':'更新日期','En':'UPDATE_DATE','t':'json','v':'MRI_UPDATE_DATE','dt':''},
                           {'n':'更新user','En':'UPDATE_USER','t':'json','v':'MRI_UPDATE_USER','dt':''},
                           {'n':'ZJJ投诉电话','En':'ZJJ_TEL','t':'json','v':'MRI_ZJJ_TEL','dt':''},
                           {'n':'SAC_ID','En':'SAC_ID','t':'json','v':'SAC_ID','dt':''},
                           {'n':'注册省市','En':'SAC_NAME','t':'json','v':'SAC_NAME','dt':''},
                           {'n':'应用id','En':'SSGC_ID','t':'json','v':'SSGC_ID','dt':''}
                           ]
                   }
        for js_ in js:
            result = response.meta['result']
            for config in configs['data']:
                k = config['En']  
                result[k] = S.select_content(js_, config)
            print(result) 
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
        '''证券评级机构--执照图片'''
        orgid = response.meta['orgid']
        print(response.meta)
        js = json.loads(response.text)
        print(response.text)
        configs = {'list':{'v':'','t':''},
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
            formtxt = 'http://jg.sac.net.cn/pages/publicity/train-line-register!writeFile.action?inputPath={path}&fileName={filename}'
            filename = urllib.parse.quote(urllib.parse.quote(result['ZRNI_NAME'].encode('utf-8')).encode('utf-8'))
            result['url'] = formtxt.format(path=result['ZRNI_PATH'],filename = filename)
            print(result)
    def otcInfoParse4(self, response):
        '''证券评级机构--高管人员信息'''
        orgid = response.meta['otcid']
        js = json.loads(response.text)
        configs = {'list':{'v':'','t':''},
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
            print(result)
    def EQS_sacListParse(self, response):
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
        configs =  {'list':{'v':'','t':''},
                   'data':[{'n':'机构ID','En':'orgid','t':'json','v':'AOI_ID','dt':''},
                           {'n':'会员编号','En':'MEMBER_NO','t':'json','v':'AOI_MEMBER_NO','dt':''},
                           {'n':'会员代码','En':'org_NO','t':'json','v':'AOI_NO','dt':''},
                           {'n':'机构代码','En':'org_No','t':'json','v':'AOI_ORG_NO','dt':''},
                           {'n':'会员级别','En':'OPC_NAME','t':'json','v':'OPC_NAME','dt':''},
                           ]
                   } 
        for js_ in js:
            result=dict()
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
            yield scrapy.FormRequest('http://jg.sac.net.cn/pages/publicity/resource!search.action',
                                     formdata = {'filter_EQS_aoi_id':str(result['orgid']),
                                                'sqlkey':'publicity',
                                                'sqlval':'SELECT_TZ_REG_INFO'},
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},
                                     callback = self.EQS_sacInfoParse2,
                                     meta = {'result':result})
    def EQS_sacInfoParse2(self, response):
        '''证券投资咨询机构--基本信息2'''
        js = json.loads(response.text)
        configs = {'list':{'v':'','t':''},
                   'data':[
                           {'n':'中文名称','En':'CHINESE_NAME','t':'json','v':'MRI_CHINESE_NAME','dt':''},
                           {'n':'公司邮箱','En':'EMAIL','t':'json','v':'MRI_EMAIL','dt':''},
                           {'n':'传真','En':'FAX','t':'json','v':'MRI_FAX','dt':''},
                           {'n':'总经理','En':'GENERAL_MANAGER','t':'json','v':'MRI_GENERAL_MANAGER','dt':''},
                           {'n':'详细注册地址','En':'INFO_REG','t':'json','v':'MRI_INFO_REG','dt':''},
                           {'n':'法人代表','En':'LEGAL_REPRESENTATIVE','t':'json','v':'MRI_LEGAL_REPRESENTATIVE','dt':''},
                           {'n':'业务资格许可证编号','En':'LICENSE_CODE','t':'json','v':'MRI_LICENSE_CODE','dt':''},
                           {'n':'办公地址','En':'OFFICE_ADDRESS','t':'json','v':'MRI_OFFICE_ADDRESS','dt':''},
                           {'n':'办公地邮政编码','En':'OFFICE_ZIP_CODE','t':'json','v':'MRI_OFFICE_ZIP_CODE','dt':''},
                           {'n':'注册资本（万元）','En':'REG_CAPITAL','t':'json','v':'MRI_REG_CAPITAL','dt':''},
                           {'n':'备注','En':'REMARK','t':'json','v':'MRI_REMARK','dt':''},
                           {'n':'所在地证监局投诉电话','En':'ZJJ_TEL','t':'json','v':'MRI_ZJJ_TEL','dt':''},
                           ]
                   }
        for js_ in js:
            result = response.meta['result']
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
            print(result)
    def orgListParse(self, response):
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
        '''证券公司--高管信息'''
        orgid = response.meta['orgid']
        js = json.loads(response.text)
        configs = {'list':{'v':'','t':''},
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
            print(result)
        
    def SALES_DEPTParse(self, response):
        '''证券公司--营业部信息'''
        orgid = response.meta['orgid']
        page = response.meta['page']
        js = json.loads(response.text)
        if page == 1:
            totalPage = js['totalPages']
        else:
            totalPage = response.meta['totalPage']
        configs = {'list':{'v':'','t':''},
                   'data':[{'n':'营业部服务电话','En':'MSDI_CS_TEL','t':'json','v':'MSDI_CS_TEL','dt':''},
                           {'n':'邮箱#基本为NUll','En':'MSDI_EMAIL','t':'json','v':'MSDI_EMAIL','dt':''},
                           {'n':'营业部名称','En':'MSDI_NAME','t':'json','v':'MSDI_NAME','dt':''},
                           {'n':'注册地址','En':'REG_ADDRESS','t':'json','v':'MSDI_REG_ADDRESS','dt':''},
                           {'n':'办公地址','En':'MSDI_REG_PCC','t':'json','v':'MSDI_REG_PCC','dt':''},
                           {'n':'营业部负责人','En':'MSDI_SALES_MANAGER','t':'json','v':'MSDI_SALES_MANAGER','dt':''},
                           {'n':'所在地证监局投诉电话','En':'MSDI_ZJJ_COMPLAINTS_TEL','t':'json','v':'MSDI_ZJJ_COMPLAINTS_TEL','dt':''}
                           ]
                   }
        
        for js_ in js['result']:
            result = dict()
            result['orgid'] = orgid
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
            print(result)
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
        '''证券公司--分公司信息'''
        orgid = response.meta['orgid']
        page = response.meta['page']
        js = json.loads(response.text)
        if page == 1:
            totalPage = js['totalPages']
        else:
            totalPage = response.meta['totalPage']
        configs = {'list':{'v':'','t':''},
                   'data':[{'n':'分公司名称','En':'BRANCH_FULL_NAME','t':'json','v':'MBOI_BRANCH_FULL_NAME','dt':''},
                           {'n':'分公司经营范围','En':'BUSINESS_SCOPE','t':'json','v':'MBOI_BUSINESS_SCOPE','dt':''},
                           {'n':'分公司电话','En':'CS_TEL','t':'json','v':'MBOI_CS_TEL','dt':''},
                           {'n':'分公司办公地址','En':'OFF_ADDRESS','t':'json','v':'MBOI_OFF_ADDRESS','dt':''},
                           {'n':'分公司负责人','En':'PERSON_IN_CHARGE','t':'json','v':'MBOI_PERSON_IN_CHARGE','dt':''}
                           ]
                   }
        for js_ in js['result']:
            result=dict()
            result['orgid'] = orgid
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_, config)
            print(result)
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
        '''证券公司信息基本信息--result传入orgInfoParse2'''
        orgid = response.meta['orgid']
        js = json.loads(response.text)
        print(js)
        configs = {'list':{'v':'','t':''},
                   'data':[{'n':'中文全称','En':'org_FullName','t':'json','v':'MRI_CHINESE_NAME','dt':''},
                           {'n':'公司网址','En':'COM_WEBSITE','t':'json','v':'MRI_COM_WEBSITE','dt':''},
                           {'n':'客户服务（投诉）电话','En':'SERVICE_TEL','t':'json','v':'MRI_CUSTOMER_SERVICE_TEL','dt':''},
                           {'n':'公司邮箱','En':'Email','t':'json','v':'MRI_EMAIL','dt':''},
                           {'n':'注册地址','En':'reg_address','t':'json','v':'MRI_INFO_REG','dt':''},
                           {'n':'法人代表	','En':'LEGAL_REPRESENTATIVE','t':'json','v':'MRI_LEGAL_REPRESENTATIVE','dt':''},
                           {'n':'经营证券业务许可证编号','En':'LICENSE_CODE','t':'json','v':'MRI_LICENSE_CODE','dt':''},
                           {'n':'办公地址','En':'OFFICE_ADDRESS','t':'json','v':'MRI_OFFICE_ADDRESS','dt':''},
                           {'n':'办公地邮编','En':'OFFICE_ZIP_CODE','t':'json','v':'MRI_OFFICE_ZIP_CODE','dt':''},
                           {'n':'注册资本（万元）','En':'REG_CAPITAL','t':'json','v':'MRI_REG_CAPITAL','dt':''}
                           ]
                   }
        result = dict()
        for js_ in js:
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(js_    , config)
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
        '''证券公司信息获取经营范围'''
        result = response.meta['result']
        result['org_id'] = response.meta['orgid']
        js = json.loads(response.text)
        PTSC_NAME = []
        for i in js:
            PTSC_NAME.append(i['PTSC_NAME'])
        result['ptsc'] = ','.join(PTSC_NAME)
        print(result)
    def parse(self, response):
        '''从业资格证书--公司基本信息'''
        item = SacItem()
        js = json.loads(response.text)
        configs = [
                    {'n':'机构ID','En':'CropRowID','t':'json','v':'AOI_ID','dt':''},
                    {'n':'机构名称','En':'CorpFullName','t':'json','v':'AOI_NAME','dt':''},
                    {'n':'从业人员数','En':'QualificationCount','t':'json','v':'PR_COUNT_PERSON','dt':''},
                    {'n':'一般证券业务','En':'a','t':'json','v':'PTI0PERSON','dt':''},
                    {'n':'证券投资咨询业务(其他)','En':'b','t':'json','v':'PTI1PERSON','dt':''},
                    {'n':'证券经纪业务营销','En':'c','t':'json','v':'PTI2PERSON','dt':''},
                    {'n':'证券经纪人','En':'d','t':'json','v':'PTI3PERSON','dt':''},
                    {'n':'证券投资咨询业务(分析师)','En':'e','t':'json','v':'PTI4PERSON','dt':''},
                    {'n':'证券投资咨询业务(投资顾问)','En':'f','t':'json','v':'PTI5PERSON','dt':''},
                    {'n':'保荐代表人','En':'g','t':'json','v':'PTI6PERSON','dt':''},
                    {'n':'投资主办人','En':'h','t':'json','v':'PTI7PERSON','dt':''},
                    ]
        
        for json_ in js:
            result = dict()
            for config in configs:
                result[config['En']] = json_[config['v']]
#            print(result)
            item['result'] = result
            item['keys'] = []
            item['db'] = ''
            yield item
            CropRowID = result['CropRowID']
            datas = self.asc_data(CropRowID)
            headers = {'User-Agent':generate_user_agent()}
            yield scrapy.FormRequest("http://person.sac.net.cn/pages/registration/train-line-register!search.action",
                                     formdata=datas[0],
                                     headers = headers,
                                     meta = {'CropRowID':CropRowID},
                                     callback = self.cctparse)
            yield scrapy.FormRequest("http://person.sac.net.cn/pages/registration/train-line-register!search.action",
                                     formdata=datas[1],
                                     headers = headers,
                                     meta = {'CropRowID':CropRowID},
                                     callback = self.cctparse)
            
    def asc_data(self,AOI_ID):
        '''处理个人证券从业信息data'''
        data1 = {'filter_LES_ROWNUM':'8000',
                 'filter_GTS_RNUM':'0',
                 'filter_EQS_PTI_ID':'',
                 'filter_EQS_AOI_ID':AOI_ID,
                 'ORDERNAME':'PP#PTI_ID,PP#PPP_NAME',
                 'ORDER':'ASC',
                 'sqlkey':'registration'
                 ,'sqlval':'SEARCH_FINISH_PUBLICITY'}
        data2 = {'filter_LES_ROWNUM':'8000',
                 'filter_GTS_RNUM':'0',
                 'filter_EQS_PTI_ID':'',
                 'filter_EQS_AOI_ID':AOI_ID,
                 'ORDERNAME':'PP#PTI_ID,PP#PPP_NAME',
                 'ORDER':'ASC',
                 'sqlkey':'registration'
                 ,'sqlval':'SEARCH_FINISH_OTHER_PUBLICITY'}
        return (data1,data2,)

    def cctparse(self, response):
        '''个人证券从业信息列表页PARSE'''
        js = json.loads(response.text)
        configs= [
                {'n':'','En':'EmpHashID','t':'json','v':'PPP_ID','dt':''},
                {'n':'','En':'EmpFullName','t':'json','v':'RPI_NAME','dt':''},
                {'n':'','En':'Gender','t':'json','v':'SCO_NAME','dt':''},
                {'n':'','En':'Education','t':'json','v':'ECO_NAME','dt':''},
                {'n':'','En':'CorpFullName','t':'json','v':'AOI_NAME','dt':''},
                {'n':'','En':'QualificationType','t':'json','v':'PTI_NAME','dt':''},
                {'n':'','En':'QualificationName','t':'json','v':'CTI_NAME','dt':''},
                {'n':'','En':'QualificationNo','t':'json','v':'CER_NUM','dt':''},
                {'n':'','En':'QualificationStartDate','t':'json','v':'PPP_GET_DATE','dt':''},
                {'n':'','En':'QualificationEndDate','t':'json','v':'PPP_END_DATE','dt':''},
                {'n':'','En':'ChangeInformationCount','t':'json','v':'COUNTCER','dt':''},
                {'n':'','En':'CreditTip','t':'json','v':'COUNTCX','dt':''},
                {'n':'机构ID','En':'CropRowID','t':'meta','v':'CropRowID','dt':''},
                        ]
        for json_ in js:
#            print(json_)
            headers  = {'User-Agent':generate_user_agent()}
            result = dict()
            for config in configs:
                if config['t'] != 'meta':
                    result[config['En']] = S.select_content(json_, config)
                else:
                    result[config['En']] = S.select_content(response, config)
            
            EmpHashID = result['EmpHashID']
            data = {'filter_EQS_PPP_ID':EmpHashID,
                    'sqlkey':'registration',
                    'sqlval':'SD_A02Leiirkmuexe_b9ID'}
            yield scrapy.FormRequest('http://person.sac.net.cn/pages/registration/train-line-register!search.action',
                                     formdata = data,
                                     headers = headers,
                                     callback = self.getEmpIDparse,
                                     meta = {'result':result}
                                     )
    def getEmpIDparse(self, response):
        '''证券从业资格-个人信息'''
        item = SacItem()
        js = json.loads(response.text)
        headers  = {'User-Agent':generate_user_agent()}
        result = response.meta['result']
        if js:
            result['EmpID']  = js[0]['RPI_ID']
#            print(result)
            item['result'] = result
            item['keys'] = []
            item['db'] = ''
            yield item
            data = {
                    'filter_EQS_RH#RPI_ID':result['EmpID'],
                    'sqlkey':'registration',
                    'sqlval':'SEARCH_LIST_BY_PERSON'}
            yield scrapy.FormRequest('http://person.sac.net.cn/pages/registration/train-line-register!search.action',
                                    formdata = data,
                                    headers = headers,
                                    callback = self.Employee_Change,
                                    meta={'EmpID':result['EmpID']}
                                    )
    def Employee_Change(self, response):
        '''证券从业资格-个人变更信息'''
        item = SacItem()
        js = json.loads(response.text)
        result = dict()
        result['EmpID'] = response.meta['EmpID']
        configs = [
                    {'n':'','En':'CorpFullName','t':'json','v':'AOI_NAME','dt':''},
                    {'n':'','En':'QualificationStatus','t':'json','v':'CERTC_NAME','dt':''},
                    {'n':'','En':'QualificationNo','t':'json','v':'CER_NUM','dt':''},
                    {'n':'','En':'QualificationStartDate','t':'json','v':'OBTAIN_DATE','dt':''},
                    {'n':'','En':'QualificationType','t':'json','v':'PTI_NAME','dt':''}
                    ]
        for json_ in js:
            for config in configs:
                result[config['En']] = S.select_content(json_, config)
#            print(result)
            item['result'] = result
            item['keys'] = []
            item['db'] = ''
            yield item
if __name__=="__main__":
#    a = SacPersonSpider()
#    print(a.start_requests())
    pass