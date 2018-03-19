
#办公地址                r'http://map.baidu.com/m?word=(.*?)\"'
#上线时间                //div[@class="time"]/text()
#公司名称  companyName   //div[@class='name']/text()
#综合利率  rate          //div[@class="val rate"]/text()
#期限范围  period         //div[@class="val period"]//text()
#公司名称                 //div[@class="k" and text()="公司名称"]
#电话                    //div[@class="k" and text()="电话"]
#统一社会信用代码         //div[@class="k" and text()="统一社会信用代码"]
#工商注册号               //div[@class="k" and text()="工商注册号"]
#组织机构代码             //div[@class="k" and text()="组织机构代码"]
#经营状态                 //div[@class="k" and text()="经营状态"]
#法定代表人               //div[@class="k" and text()="法定代表人"]
#注册资本                 //div[@class="k" and text()="注册资本"]
#公司类型                 //div[@class="k" and text()="公司类型"]
#成立日期                 //div[@class="k" and text()="成立日期"]
#营业期限                 //div[@class="k" and text()="营业期限"]
#登记机关                 //div[@class="k" and text()="登记机关"]
#核准日期                 //div[@class="k" and text()="核准日期"]
#所属行业                 //div[@class="k" and text()="核准日期"]
#曾用名                   //div[@class="k" and text()="曾用名"]
#企业地址                 //div[@class="k" and text()="企业地址"]
#备案域名                 //div[@class="k" and text()="经营范围"]
#备案域名时间             //div[@class="k" and text()="经营范围"]
#备案单位名称             //div[@class="k" and text()="经营范围"]
#备案单位性质             //div[@class="k" and text()="经营范围"]
#ICP备案号               //div[@class="k" and text()="经营范围"]
#ICP经营许可证           //div[@class="k" and text()="经营范围"]

BaseInfoConfigs = [{'list':{'v':'','t':'','check':'companyShortName','keys':['companyShortName'],'db':'dbo.p2peye_BaseInfo'},
           'data':[
            {'n':'办公地址','En':'officeAddress','t':'regex1','v':'http:\/\/map\.baidu\.com\/m\?word=(.*?)\"','dt':''},
            {'n':'上线时间','En':'upLinetime','t':'regex1','v':'上线时间：([^<]*?)<','dt':''},
            {'n':'公司名称缩写','En':'companyShortName','t':'xpath_first','v':'//div[@class="name"]/text()','dt':''},
            {'n':'综合利率','En':'interestRate','t':'xpath_first','v':'//div[@class="val rate"]/text()','dt':''},
            {'n':'期限范围','En':'TermRange','t':'xpath_first','v':'//div[@class="val period"]//text()','dt':''},
            {'n':'公司名称','En':'CompanyFullName','t':'xpath_first','v':'//div[@class="k" and text()="公司名称"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'电话','En':'TelPhoneNumber','t':'xpath_first','v':'//div[@class="k" and text()="电话"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'统一社会信用代码','En':'SocialCreditCode','t':'xpath_first','v':'//div[@class="k" and text()="统一社会信用代码"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'工商注册号','En':'BusinessRegistrationNumber','t':'xpath_first','v':'//div[@class="k" and text()="工商注册号"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'组织机构代码','En':'OrganizationCode','t':'xpath_first','v':'//div[@class="k" and text()="组织机构代码"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'经营状态','En':'ManagementState','t':'xpath_first','v':'//div[@class="k" and text()="经营状态"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'法定代表人','En':'LegalRepresentative','t':'xpath_first','v':'//div[@class="k" and text()="法定代表人"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'注册资本','En':'RegisteredCapital','t':'xpath_first','v':'//div[@class="k" and text()="注册资本"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'公司类型','En':'CompanyType','t':'xpath_first','v':'//div[@class="k" and text()="公司类型"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'成立日期','En':'SetupDate','t':'xpath_first','v':'//div[@class="k" and text()="成立日期"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'营业期限','En':'BusinessTerm','t':'xpath_first','v':'//div[@class="k" and text()="营业期限"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'登记机关','En':'RegistrationAuthority','t':'xpath_first','v':'//div[@class="k" and text()="登记机关"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'核准日期','En':'ApprovalDate','t':'xpath_first','v':'//div[@class="k" and text()="核准日期"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'所属行业','En':'IndustryOwned','t':'xpath_first','v':'//div[@class="k" and text()="核准日期"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'曾用名','En':'NameUsedBefore','t':'xpath_first','v':'//div[@class="k" and text()="曾用名"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'企业地址','En':'RegisteredAddress','t':'xpath_first','v':'//div[@class="k" and text()="企业地址"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'备案域名','En':'RegisterDomainName','t':'xpath_first','v':'//div[@class="k" and text()="备案域名"]/following-sibling::div[@class="v"]/span/text()','dt':''},
            {'n':'备案域名时间','En':'RegisterDomainTime','t':'xpath_first','v':'//div[@class="k" and text()="备案域名时间"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'备案单位名称','En':'RegisterUnitName','t':'xpath_first','v':'//div[@class="k" and text()="备案单位名称"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'备案单位性质','En':'RegisterUnitNature','t':'xpath_first','v':'//div[@class="k" and text()="备案单位性质"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'ICP备案号','En':'ICPRecordNumber','t':'xpath_first','v':'//div[@class="k" and text()="ICP备案号"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'ICP经营许可证','En':'ICPoperatingLicense','t':'xpath_first','v':'//div[@class="k" and text()="ICP经营许可证"]/following-sibling::div[@class="v"]/text()','dt':''},
            {'n':'domain','En':'domain','t':'meta','v':'domain','dt':''},
            {'n':'pid','En':'pid','t':'meta','v':'pid','dt':''},
            ]
           }]
           
seniorExecutiveConfigs = [{'list':{'v':'//div[@class="kvs kvs_zyry"]/div','t':'xpath','check':'companyShortName','keys':['companyShortName','position','name'],'db':'dbo.p2peye_seniorExecutive'},
           'data':[
            {'n':'职务','En':'position','t':'xpath_first','v':'./div[@class="k"]/text()','dt':''},
            {'n':'姓名','En':'name','t':'xpath_first','v':'./div[@class="v"]/text()','dt':''},
            {'n':'公司','En':'companyShortName','t':'xpath_first','v':'//div[@class="name"]/text()','dt':''},
            {'n':'domain','En':'domain','t':'meta','v':'domain','dt':''},
            {'n':'pid','En':'pid','t':'meta','v':'pid','dt':''},
            ]
           }
           ]

ShareholderinfoConfigs  = [{'list':{'v':'data/data','t':'json','check':'name','keys':['id_','name'],'db':'dbo.p2peye_Shareholderinfo'},
           'data':[
            {'n':'id_','En':'id_','t':'json','v':'id','dt':''},
            {'n':'pid','En':'pid','t':'meta','v':'pid','dt':''},
            {'n':'认缴出资（万元）','En':'amount','t':'json','v':'amount','dt':''},
            {'n':'认缴比例','En':'bl','t':'json','v':'bl','dt':''},
#            {'n':'估计是实缴','En':'capitalActlAmomon','t':'json','v':'capitalActl[0]/amomon','dt':''},
            {'n':'股东名称','En':'name','t':'json','v':'name','dt':''},
            {'n':'企业状态','En':'regStatus','t':'json','v':'regStatus','dt':''},
            {'n':'得分','En':'pencertileScore','t':'json','v':'pencertileScore','dt':''},
            {'n':'股东类型1企业2个人','En':'type','t':'json','v':'type','dt':''},
            ]
           }
           ]  

ChangeRecordConfigs = [{'list':{'v':'data/data','t':'json','check':'pid','keys':['id_','pid','changeTime'],'db':'dbo.p2peye_ChangeRecord'},
           'data':[
            {'n':'id_','En':'id_','t':'json','v':'id','dt':''},
            {'n':'pid','En':'pid','t':'json','v':'pid','dt':''},
            {'n':'变更前信息','En':'contentBefore','t':'json','v':'contentBefore','dt':''},
            {'n':'变更后信息','En':'contentAfter','t':'json','v':'contentAfter','dt':''},
            {'n':'变更项目','En':'changeItem','t':'json','v':'changeItem','dt':''},
            {'n':'变更时间','En':'changeTime','t':'json','v':'changeTime','dt':''},
            {'n':'创建时间','En':'create_time','t':'json','v':'create_time','dt':''}
            ]
           }
           ]  