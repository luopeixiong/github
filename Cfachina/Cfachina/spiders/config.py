#/usr/bin/env python 
#! -*- coding:utf-8 -*-

import re


class Configs(object):
    def __init__(self):
        ####从业资格配置###
        self.configs_person = {'list':{'n':'从业人员信息-config','v':'//table//tr[position()>1]','t':'xpath','db':'person','keys':[]},
                          'data':[{'n':'姓名','En':'name','t':'xpath_first','v':'td[1]/text()','dt':''},
                               {'n':'性别','En':'Gender','t':'xpath_first','v':'td[2]/text()','dt':''},
                               {'n':'从业资格号','En':'QualificationNo','t':'xpath_first','v':'td[3]/text()','dt':''},
                               {'n':'投资咨询从业证书号','En':'inviderQualificationNo','t':'xpath_first','v':'td[4]/text()','dt':''},
                               {'n':'任职部门','En':'department','t':'xpath_first','v':'td[5]/text()','dt':''},
                               {'n':'职务','En':'position','t':'xpath_first','v':'td[6]/text()','dt':''},
                               {'n':'任现职时间','En':'Appointment_time','t':'xpath_first','v':'td[7]/text()','dt':''},
                               {'n':'公司名称','En':'org_name','t':'xpath_first','v':'//div[@class="gst_title"]/a[3]/text()','dt':''},
                               {'n':'公司id','En':'organid','t':'xpath_first','v':'//input[@name="organid"]/@value','dt':''},
                               ]
                          }
        ###基础信息配置###
        self.configs_baseinfo = {'list':{'n':'基本信息','v':'','t':'','db':'baseinfo','keys':[]},
                            'data':[{'n':'公司名称','En':'orgName','v':'//div[@class="gst_mcleib"]//td[@align!="left" and contains(text(),"公司名称")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'许可证号','En':'license_No','v':'//div[@class="gst_mcleib"]//td[@align!="left" and contains(text(),"许可证号")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'经营范围','En':'Business_scope','v':'//div[@class="gst_mcleib"]//td[@align!="left" and contains(text(),"经营范围")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'金融期货业务资格类别','En':'Qualification','v':'//div[@class="gst_mcleib"]//td[@align!="left" and contains(text(),"金融期货业务资格类别")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'取得会员资格的期货交易所名称','En':'futures_exchange','v':'//div[@class="gst_mcleib"]//td[@align!="left" and contains(text(),"取得会员资格的期货交易所名称")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'注册资本(元)','En':'reg_capital','v':'//div[@class="gst_mcleib"]//td[@align!="left" and contains(text(),"注册资本(元)")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'公司住所','En':'company_address','v':'//div[@class="gst_mcleib"]//td[@align!="left" and contains(text(),"公司住所")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'法定代表人','En':'legal_representative','v':'//div[@class="gst_mcleib"]//td[@align!="left" and contains(text(),"法定代表人")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'办公地址和邮编','En':'reg_address','v':'//div[@class="gst_mcleib"]//td[@align!="left" and contains(text(),"办公地址和邮编")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'客户服务及投诉电话','En':'Tel','v':'//div[@class="gst_mcleib"]//td[@align!="left" and contains(text(),"客户服务及投诉电话")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'公司网址网址','En':'webSite','v':'//div[@class="gst_mcleib"]//td[@align!="left" and contains(text(),"公司网址网址")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'公司电子邮箱','En':'Email','v':'//div[@class="gst_mcleib"]//td[@align!="left" and contains(text(),"公司电子邮箱")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                                    ]
                            }
        ###历史情况配置###
        self.configs_hisinfo = {'list':{'n':'','v':'//table//tr[position()>1]','t':'xpath','db':'hisinfo','keys':[]},
                            'data':[{'n':'时间','En':'','v':'td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'事件简称','En':'','v':'td[2]/text()','t':'xpath_first','dt':''},
                                    {'n':'事件内容(200字以内)','En':'','v':'td[3]/text()','t':'xpath_first','dt':''}
                                    ]
                            }
        ###分支机构配置###
        self.configs_branchinfo = {'list':{'n':'分支机构','v':'//table//tr[position()>1]','t':'xpath','db':'branchinfo','keys':[]},
                            'data':[{'n':'分支机构名称','En':'branch_name','v':'td[2]/text()','t':'xpath_first','dt':''},
                                    {'n':'所在地','En':'loaction','v':'td[3]/text()','t':'xpath_first','dt':''},
                                    {'n':'许可证号','En':'license_No','v':'td[4]/text()','t':'xpath_first','dt':''},
                                    {'n':'设立时间','En':'setup_date','v':'td[5]/text()','t':'xpath_first','dt':''},
                                    {'n':'负责人','En':'charge','v':'td[6]/text()','t':'xpath_first','dt':''},
                                    {'n':'客户服务与投诉电话','En':'Tel','v':'td[7]/text()','t':'xpath_first','dt':''},
                                    {'n':'详细地址(邮编)','En':'address','v':'td[8]/text()','t':'xpath_first','dt':''},
                                    {'n':'电子邮箱','En':'Email','v':'td[9]/text()','t':'xpath_first','dt':''},
                                    ]
                            }
        ###高管人员信息配置###
        self.configs_supervisorinfo = {'list':{'n':'高管人员信息','v':'//table//tr[position()>1]','t':'xpath','db':'supervisorinfo','keys':[]},
                            'data':[{'n':'姓名','En':'Name','v':'td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'性别','En':'Gender','v':'td[2]/text()','t':'xpath_first','dt':''},
                                    {'n':'现任职务','En':'current_position','v':'td[3]/text()','t':'xpath_first','dt':''},
                                    {'n':'高管资格批准文号','En':'Approval_number','v':'td[4]/text()','t':'xpath_first','dt':''},
                                    {'n':'任现职时间','En':'Appointment_time','v':'td[5]/text()','t':'xpath_first','dt':''},
                                    {'n':'其它任职经历(与期货相关)','En':'Other_job_experience','v':'td[6]/text()','t':'xpath_first','dt':''},
                                    {'n':'备注','En':'remark','v':'td[7]/text()','t':'xpath_first','dt':''}
                                    ]
                            }
        ###股东信息配置###
        self.configs_shareholderinfo = {'list':{'n':'股东信息','v':'//table//tr[position()>1]','t':'xpath','db':'shareholderinfo','keys':[]},
                            'data':[{'n':'股东名称','En':'Shareholder_name','v':'td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'持股比例(%)','En':'Shareholding_ratio','v':'td[2]/text()','t':'xpath_first','dt':''},
                                    {'n':'入股时间','En':'Share_date','v':'td[3]/text()','t':'xpath_first','dt':''},
                                    {'n':'法定代表人','En':'Legal_representative','v':'td[4]/text()','t':'xpath_first','dt':''},
                                    {'n':'注册资本(元)','En':'reg_capital','v':'td[5]/text()','t':'xpath_first','dt':''},
                                    {'n':'办公地址','En':'office_address','v':'td[6]/text()','t':'xpath_first','dt':''},
                                    {'n':'公司网址','En':'website','v':'td[7]/text()','t':'xpath_first','dt':''},
                                    {'n':'所属行业','En':'profession','v':'td[8]/text()','t':'xpath_first','dt':''},
                                    {'n':'经济类型','En':'Economic_type','v':'td[9]/text()','t':'xpath_first','dt':''},
                                    {'n':'备注','En':'remark','v':'td[10]/text()','t':'xpath_first','dt':''}
                                    ]
                            }
        ###诚信记录配置###
        self.configs_creditinfo ={'list':{'n':'','v':'//table//tr[position()>1]','t':'xpath','db':'creditinfo','keys':[]},
                            'data':[{'n':'时间','En':'date','v':'td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'类别','En':'type','v':'td[2]/text()','t':'xpath_first','dt':''},
                                    {'n':'实施机关','En':'Implementing_organ','v':'td[3]/text()','t':'xpath_first','dt':''},
                                    {'n':'文号','En':'Document_number','v':'td[4]/text()','t':'xpath_first','dt':''},
                                    {'n':'情况简介(200字以内)','En':'introduction','v':'td[5]/text()','t':'xpath_first','dt':''}
                                    ]
                            }
        ###财务情况配置###
        self.configs_financialinfo = {'list':{'n':'','v':'//table//tr[position()>1]','t':'xpath','db':'financialinfo','keys':[]},
                            'data':[{'n':'年份','En':'year','v':'td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'净资本 (万元)','En':'Net_capital','v':'td[2]/text()','t':'xpath_first','dt':''},
                                    {'n':'净资产 (万元)','En':'Net_assets','v':'td[3]/text()','t':'xpath_first','dt':''},
                                    {'n':'权益总额 (万元)','En':'Total_equity','v':'td[4]/text()','t':'xpath_first','dt':''},
                                    {'n':'手续费收入 (万元)','En':'Service_Charge','v':'td[5]/text()','t':'xpath_first','dt':''},
                                    {'n':'净利润 (万元)','En':'Net_profit','v':'td[6]/text()','t':'xpath_first','dt':''},
                                    {'n':'主审会计事务所','En':'Chief_accounting_firm','v':'td[7]/text()','t':'xpath_first','dt':''},
                                    {'n':'审计意见类型','En':'opinions','v':'td[8]/text()','t':'xpath_first','dt':''},
                                    {'n':'备注','En':'remark','v':'td[9]/text()','t':'xpath_first','dt':''}
                                    ]
                            }
        ###次级债务信息配置###
        self.configs_subdebtmonthinfo = {'list':{'n':'','v':'//table//tr[position()>1]','t':'xpath','db':'subdebtmonthinfo','keys':[]},
                            'data':[{'n':'债务名称','En':'Debt_name','v':'td[1]/text()','t':'xpath_first','dt':''},
                                    {'n':'债务性质','En':'Debt_nature','v':'td[2]/text()','t':'xpath_first','dt':''},
                                    {'n':'债务规模','En':'Debt_scale','v':'td[3]/text()','t':'xpath_first','dt':''},
                                    {'n':'合同生效日','En':'Effective_date','v':'td[4]/text()','t':'xpath_first','dt':''},
                                    {'n':'到期偿还日期','En':'repayment_date','v':'td[5]/text()','t':'xpath_first','dt':''},
                                    {'n':'备注','En':'remark','v':'td[6]/text()','t':'xpath_first','dt':''}
                                    ]
                            }
    def main(self,url):
        ###根据url提取配置###
        flagdict = [
                {'regex':'selectType=personinfo','configs':'self.configs_person'},
                {'regex':'selectType=organhisinfo','configs':'self.configs_hisinfo'},
                {'regex':'selectType=organbaseinfo','configs':'self.configs_baseinfo'},
                {'regex':'selectType=organbranchinfo','configs':'self.configs_branchinfo'},
                {'regex':'selectType=supervisorinfo','configs':'self.configs_supervisorinfo'},
                {'regex':'selectType=organshareholderinfo','configs':'self.configs_shareholderinfo'},
                {'regex':'selectType=organcreditinfo','configs':'self.configs_creditinfo'},
                {'regex':'selectType=organfinancialinfo','configs':'self.configs_financialinfo'},
                {'regex':'selectType=subdebtmonthinfo','configs':'self.configs_subdebtmonthinfo'}
                ]
        for flag in flagdict:
            if re.search(flag['regex'],url):
                configs = flag['configs']
                return eval(configs)
if __name__ == '__main__':
    pass