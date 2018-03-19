# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 14:03:07 2017

@author: luopx
"""
data1 = {
        "filter_EQS_OTC_ID":"",
        "ORDERNAME":"AOI#AOI_NAME",
        "ORDER":"ASC",
        "sqlkey":"registration",
        "sqlval":"SELECT_LINE_PERSON"
        }
configs1 = {'list':{'v':'','t':'','keys':['CropRowID'],'db':'sac.SAC_ProfessionalQualificationCrop'},
           'data':[
            {'n':'机构ID','En':'CropRowID','t':'json','v':'AOI_ID','dt':''},
            {'n':'机构名称','En':'CorpFullName','t':'json','v':'AOI_NAME','dt':''},
            {'n':'从业人员数','En':'QualificationCount','t':'json','v':'PR_COUNT_PERSON','dt':''},
            {'n':'一般证券业务','En':'GeneralSecurities','t':'json','v':'PTI0PERSON','dt':''},
            {'n':'证券投资咨询业务(其他)','En':'InvestmentConsulting','t':'json','v':'PTI1PERSON','dt':''},
            {'n':'证券经纪业务营销','En':'BusinessMarketing','t':'json','v':'PTI2PERSON','dt':''},
            {'n':'证券经纪人','En':'SecuritiesBroker','t':'json','v':'PTI3PERSON','dt':''},
            {'n':'证券投资咨询业务(分析师)','En':'analyst','t':'json','v':'PTI4PERSON','dt':''},
            {'n':'证券投资咨询业务(投资顾问)','En':'InvestmentAdviser','t':'json','v':'PTI5PERSON','dt':''},
            {'n':'保荐代表人','En':'SponsorRepresentative','t':'json','v':'PTI6PERSON','dt':''},
            {'n':'投资主办人','En':'InvestmentSponsor','t':'json','v':'PTI7PERSON','dt':''},
            ]
           }

def asc_data(AOI_ID):
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
cctconfigs = {'list':{'v':'','t':'','keys':['EMPID'],'db':'sac.SAC_ProfessionalQualificationPerson'},
              'data':[
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
              }
Employee_ChangeConfigs = {'list':{'v':'','t':'','keys':['QualificationNo'],'db':'sac.SAC_Employee_Change'},
                   'data':[{'n':'','En':'CorpFullName','t':'json','v':'AOI_NAME','dt':''},
                          {'n':'','En':'QualificationStatus','t':'json','v':'CERTC_NAME','dt':''},
                          {'n':'','En':'QualificationNo','t':'json','v':'CER_NUM','dt':''},
                          {'n':'','En':'QualificationStartDate','t':'json','v':'OBTAIN_DATE','dt':''},
                          {'n':'','En':'QualificationType','t':'json','v':'PTI_NAME','dt':''},
                          {'n':'','En':'EmpID','t':'meta','v':'EmpID','dt':''},
                    ]
                   }

data2 = {
        'filter_EQS_O#otc_id':'01',
        'filter_EQS_O#sac_id':'',
        'filter_LIKES_aoi_name':'',
        'sqlkey':'publicity',
        'sqlval':'ORG_BY_TYPE_INFO'
        }
data3 = {
        'filter_EQS_sac_id':'',
        'filter_LIKES_aoi_name':'',
        'sqlkey':'publicity',
        'sqlval':'ORG_BY_TYPE_INFO_TZZX'}

data4 = {
        'filter_EQS_O#otc_id':'03',
        'filter_EQS_O#sac_id':'',
        'filter_LIKES_aoi_name':'',
        'sqlkey':'publicity',
        'sqlval':'ORG_BY_TYPE_INFO'}  

otcInfoBaseconfigs = {'list':{'v':'','t':''},
                       'data':[{'n':'机构ID','En':'orgid','t':'json','v':'AOI_ID','dt':''},
                               {'n':'会员ID','En':'MEMBER_NO','t':'json','v':'AOI_MEMBER_NO','dt':''},
                               {'n':'会员代码','En':'orgNo','t':'json','v':'AOI_NO','dt':''},
                               {'n':'组织机构代码','En':'ORG_CODE','t':'json','v':'AOI_ORG_NO','dt':''},
                               {'n':'会员属性','En':'OPC_NAME','t':'json','v':'OPC_NAME','dt':''}
                               ]
                       }

otcInfoBaseconfigs2 = {'list':{'v':'','t':'','db':'sac.SAC_otcInfo','keys':['orgid']},
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


otcInfoConfigs = {'list':{'v':'','t':'','keys':['orgid','NAME','PRACTICE_TIME'],'db':'sac.SAC_Practitioners'},
                   'data':[{'n':'性别','En':'Gender','t':'json','v':'GC_ID','dt':''},
                           {'n':'现任职务','En':'CURRENT_POSITION','t':'json','v':'MPTI_CURRENT_POSITION','dt':''},
                           {'n':'姓名','En':'NAME','t':'json','v':'MPTI_NAME','dt':''},
                           {'n':'执业时间','En':'PRACTICE_TIME','t':'json','v':'MPTI_PRACTICE_TIME','dt':''},
                           {'n':'从业资格','En':'QUALIFICATION_NO','t':'json','v':'MPTI_QUALIFICATION_NO','dt':''},
                           {'n':'备注','En':'REMARK','t':'json','v':'MPTI_REMARK','dt':''}
                           ]
                   }
BRANCH_OrgConfigs = {'list':{'v':'','t':'','keys':['orgid','BRANCH_FULL_NAME'],'db':'sac.SAC_BRANCH_Org'},
                   'data':[{'n':'分公司名称','En':'BRANCH_FULL_NAME','t':'json','v':'MBOI_BRANCH_FULL_NAME','dt':''},
                           {'n':'分公司经营范围','En':'BUSINESS_SCOPE','t':'json','v':'MBOI_BUSINESS_SCOPE','dt':''},
                           {'n':'分公司电话','En':'CS_TEL','t':'json','v':'MBOI_CS_TEL','dt':''},
                           {'n':'分公司办公地址','En':'OFF_ADDRESS','t':'json','v':'MBOI_OFF_ADDRESS','dt':''},
                           {'n':'分公司负责人','En':'PERSON_IN_CHARGE','t':'json','v':'MBOI_PERSON_IN_CHARGE','dt':''}
                           ]
                   }
orgInfoparse1configs = {'list':{'v':'','t':'','keys':['orgid'],'db':'sac.SAC_securitiesInfo'},
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
EQS_sacInfoParse2Configs = {'list':{'v':'','t':'','keys':['orgid'],'db':'sac.SAC_EQSInfo'},
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
SALES_DEPTParseConfigs = {'list':{'v':'','t':'','keys':['MSDI_NAME','orgid'],'db':'sac.SAC_BusinessDepartment'},
                   'data':[{'n':'营业部服务电话','En':'MSDI_CS_TEL','t':'json','v':'MSDI_CS_TEL','dt':''},
                           {'n':'邮箱#基本为NUll','En':'MSDI_EMAIL','t':'json','v':'MSDI_EMAIL','dt':''},
                           {'n':'营业部名称','En':'MSDI_NAME','t':'json','v':'MSDI_NAME','dt':''},
                           {'n':'注册地址','En':'REG_ADDRESS','t':'json','v':'MSDI_REG_ADDRESS','dt':''},
                           {'n':'办公地址','En':'MSDI_REG_PCC','t':'json','v':'MSDI_REG_PCC','dt':''},
                           {'n':'营业部负责人','En':'MSDI_SALES_MANAGER','t':'json','v':'MSDI_SALES_MANAGER','dt':''},
                           {'n':'所在地证监局投诉电话','En':'MSDI_ZJJ_COMPLAINTS_TEL','t':'json','v':'MSDI_ZJJ_COMPLAINTS_TEL','dt':''}
                           ]
                   }