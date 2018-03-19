#/usr/bin/env python
#! -*- coding:utf-8 -*-


class Config(object):
    def __init__(self):
        pass
    
    @staticmethod
    def config_s():
        data = {'list':{'n':'','v':'','t':'','keys':['EntrepreneursID'],'db':'dbo.cyzone_entrepreneurs','check':'Entrepreneurs'},
                'data':[
                       {'n':'创业者名称','En':'Entrepreneurs','v':'//h1/text()','t':'xpath_join,','dt':''}, 
                       {'n':'创业者ID','En':'EntrepreneursID','v':'\/(\d+?)\.html','t':'url_re','dt':''}, 
                       {'n':'url','En':'url','v':'','t':'response.url','dt':''}, 
                       {'n':'所在机构','En':'Organization','v':'//ul[li[@class="time company"]]/li[@class="time company"][1]','t':'xpath_join,','dt':''}, 
                       {'n':'所在机构ID','En':'OrganizationID','v':'http://www.cyzone.cn/r/\d+?/(\d+?).html','t':'regex1','dt':''}, 
                       {'n':'职务','En':'post','v':'//ul[li[@class="time company"]]/li[@class="time company"][2]','t':'xpath_join,','dt':''}, 
                       {'n':'简介','En':'introduction','v':'//div[@class="people-info-box"]/p//text()','t':'xpath_join,','dt':''}, 
                       {'n':'从业项目','En':'EmploymentProject','v':'//div[@class="project-info"]/p[@class="name"]/a/text()','t':'xpath_join,','dt':''}, 
                       {'n':'公司官网','En':'OfficialWebsite','v':'//div[@class="project-info"]/p[contains(text(),"公司官网：")]/a/@href','t':'xpath_join,','dt':''}, 
                       {'n':'轮次','En':'Turns','v':'//div[@class="project-info"]/p[contains(text(),"轮次：")]/text()[last()]','t':'xpath_join,','dt':''}, 
                       {'n':'行业','En':'industry','v':'//div[@class="project-info"]/p[contains(text(),"行业：")]/a/text()','t':'xpath_join,','dt':''}, 
                       ]
                        
                }
        return data
    @staticmethod
    def config_f():
        data = {'list':{'n':'','v':'','t':'','keys':['InvestorID'],'db':'dbo.Cyzone_Investor','check':'Organization'},
                'data':[
                       {'n':'投资人名称','En':'Investor','v':'//h1/text()','t':'xpath_join,','dt':''}, 
                       {'n':'投资人名称ID','En':'InvestorID','v':'\/(\d+?)\.html','t':'url_re','dt':''}, 
                       {'n':'所在机构','En':'Organization','v':'//ul[li[@class="time company"]]/li[@class="time company"][1]','t':'xpath_join,','dt':''}, 
                       {'n':'所在机构ID','En':'OrganizationID','v':'http://www.cyzone.cn/d/\d+?/(\d+?).html','t':'regex1','dt':''}, 
                       {'n':'职务','En':'post','v':'//ul[li[@class="time company"]]/li[@class="time company"][2]','t':'xpath_join,','dt':''}, 
                       {'n':'简介','En':'introduction','v':'//div[@class="people-info-box"]/p//text()','t':'xpath_join,','dt':''}, 
                       {'n':'关注领域','En':'FocusField','v':'//div[@class="info" and span[text()="关注领域："]]/span[@class!="tit"]/text()','t':'xpath_join,','dt':''}, 
                       {'n':'投资阶段','En':'InvestmentStage','v':'//div[@class="info" and span[text()="投资阶段："]]/span[@class!="tit"]/text()','t':'xpath_join,','dt':''}, 
                       {'n':'常住城市','En':'CityResident','v':'//div[@class="info" and span[text()="常驻城市："]]/span[@class!="tit"]/text()','t':'xpath_join,','dt':''}, 
                       {'n':'工作经历','En':'WorkExperience','v':'//span[@class="com" or @class="job"]//text()','t':'xpath_join|','dt':''}, 
                       ]
                        
                }
        return data
    @staticmethod
    def config_d():
        data = {'list':{'n':'','v':'','t':'','keys':['InvestmentInstitutionsID'],'db':'dbo.Cyzone_InvestmentInstitutions','check':'InvestmentInstitutions'},
                'data':[
                       {'n':'投资机构名称','En':'InvestmentInstitutions','v':'//h1/text()','t':'xpath_join,','dt':''}, 
                       {'n':'投资机构名称ID','En':'InvestmentInstitutionsID','v':'\/(\d+?)\.html','t':'url_re','dt':''}, 
                       {'n':'成立时间','En':'SetupTime','v':'//li[starts-with(text(),"成立时间：")]/text()','t':'xpath_join,','dt':''}, 
                       {'n':'投资偏好','En':'InvestmentPreference','v':'//li[starts-with(text(),"投资偏好：")]/text()','t':'xpath_join,','dt':''}, 
                       {'n':'机构官网','En':'OfficialWebsite','v':'//li[starts-with(text(),"机构官网：")]/a/@href','t':'xpath_join,','dt':''}, 
                       {'n':'简介','En':'introduction','v':'//div[@class="people-info-box"]/p//text()','t':'xpath_join,','dt':''}, 
                       ]
                        
                }
        return data
    @staticmethod
    def config_r():
        data = {'list':{'n':'','v':'','t':'','keys':['CorporateID'],'db':'dbo.Cyzone_Corporate','check':'CorporateName'},
                'data':[
                       {'n':'公司名称','En':'CorporateName','v':'//h1/text()','t':'xpath_join,','dt':''}, 
                       {'n':'公司名称ID','En':'CorporateID','v':'\/(\d+?)\.html','t':'url_re','dt':''}, 
                       {'n':'公司全称','En':'CorporateFullName','v':'//li[@class="time"]/text()','t':'xpath_join,','dt':''}, 
                       {'n':'公司官网','En':'OfficialWebsite','v':'//div[@class="com-url"]/a/@href','t':'xpath_join,','dt':''}, 
                       {'n':'简介','En':'introduction','v':'//div[@class="info-box"]/p//text()','t':'xpath_join,','dt':''}, 
                       {'n':'创立时间','En':'EstablishmentTime','v':'//i[@class="i1"]/following-sibling::span/text()','t':'xpath_join,','dt':''}, 
                       {'n':'所在区域','En':'Location','v':'//i[@class="i2"]/following-sibling::span/a/text()','t':'xpath_join,','dt':''}, 
                       {'n':'轮次','En':'Turns','v':'//i[@class="i3"]/following-sibling::span/a/text()','t':'xpath_join,','dt':''}, 
                       {'n':'行业','En':'industry','v':'//i[@class="i6"]/following-sibling::span/a/text()','t':'xpath_join,','dt':''}, 
                       {'n':'注册号','En':'RegistrationNumber','v':'//p[span[text()="注册号:"]]/text()','t':'xpath_join,','dt':''}, 
                       {'n':'经营状态','En':'ManagementState','v':'//p[span[text()="经营状态:"]]/text()','t':'xpath_join,','dt':''}, 
                       {'n':'法定代表','En':'LegalRepresentative','v':'//p[span[text()="法定代表:"]]/text()','t':'xpath_join,','dt':''}, 
                       {'n':'股东','En':'Shareholder','v':'//p[span[text()="股东:"]]/span[position()>1 ]/text()[position()!=last()]','t':'xpath_join,','dt':''}, 
                       {'n':'公司类型','En':'CompanyType','v':'//p[span[text()="公司类型:"]]/text()','t':'xpath_join,','dt':''}, 
                       {'n':'成立日期','En':'SetupTime','v':'//p[span[text()="成立日期:"]]/text()','t':'xpath_join,','dt':''}, 
                       {'n':'注册资本','En':'RegisteredCapital','v':'//p[span[text()="注册资本:"]]/text()','t':'xpath_join,','dt':''}, 
                       {'n':'住所','En':'Residence','v':'//p[span[text()="住所:"]]/text()','t':'xpath_join,','dt':''}, 
#                       {'n':'经营状态','En':'ManagementState','v':'//p[span[text()="经营状态:"]]/text()','t':'xpath_join,','dt':''}, 
                       ]
                        
                }
        return data
    