#from items import Items


rzrqConfigs = [{'list':{'n':'','v':'//table[@id="REPORTID_tab2"]//tr[position()>1]','t':'xpath','keys':['date','code'],'check':'shortname','db':'dbo.SZSE_rzrq'},
            'data':[{'n':'日期','En':'date','v':'//input[@name="txtDate"]/@value','t':'xpath_first'},
                     {'n':'证券代码','En':'code','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortname','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'融资买入额(元) ','En':'rzmre','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'融资余额(元)','En':'rzye','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'融券卖出量(股)','En':'rqmcy','v':'td[5]/text()','t':'xpath_first'},
                     {'n':'融券余量(股)','En':'rqyl','v':'td[6]/text()','t':'xpath_first'},
                     {'n':'融券余额(元)','En':'rqye','v':'td[7]/text()','t':'xpath_first'},
                     {'n':'融资融券余额(元)','En':'rzrqye','v':'td[8]/text()','t':'xpath_first'},
                     
                     
                     ]
            }
            ]
zrdsConfigs = [{'list':{'n':'','v':'//table[@class="cls-data-table-common cls-data-table"]//tr[position()>1]','t':'xpath','keys':['dongshi','code'],'check':'dongshi','db':'dbo.SZSE_dlds'},
            'data':[
                     {'n':'代码','En':'code','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'公司简称','En':'shortname','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'独立董事姓名','En':'dongshi','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'简历','En':'ins','v':'td[5]/a/@href','t':'xpath_first'},
                     ]
            }
            ]

zrdmConfigs = [{'list':{'n':'','v':'//*[@id="REPORTID_tab1"]//tr[position()>1]','t':'xpath','keys':['dongmi','code'],'check':'dongmi','db':'dbo.SZSE_dldm'},
            'data':[
                     {'n':'代码','En':'code','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'公司简称','En':'shortname','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'姓名','En':'dongmi','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'性别','En':'gender','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'现任职务','En':'position','v':'td[5]/text()','t':'xpath_first'},
                     {'n':'获得董秘资格时间','En':'gettime','v':'td[6]/text()','t':'xpath_first'},
                     {'n':'最近培训时间','En':'lasttime','v':'td[7]/text()','t':'xpath_first'},
                     ]
            }
            ]



dmzgpxdaconfigs = [{'list':{'n':'','v':'//*[@id="REPORTID_tab2"]//tr[position()>1]','t':'xpath','keys':['name','lasttime'],'check':'name','db':'dbo.SZSE_dmzgpxda'},
            'data':[
                     {'n':'姓名','En':'name','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'性别','En':'gender','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'学历','En':'education','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'获得董秘资格时间','En':'gettime','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'最近培训时间','En':'lasttime','v':'td[5]/text()','t':'xpath_first'},
                     ]
            }
            ]

dsrckInfoConfigs = [{'list':{'n':'','v':'//*[@id="1900_detailtab1"]','t':'xpath','keys':['name','startDate'],'check':'name','db':'dbo.SZSE_dsrck'},
            'data':[
                    {'n':'学员姓名','En':'name','v':'.//tr[3]/td[2]/text()','t':'xpath_first'},
                     {'n':'性别','En':'gender','v':'.//tr[3]/td[4]/text()','t':'xpath_first'},
                     {'n':'年龄','En':'age','v':'.//tr[4]/td[2]/text()','t':'xpath_first'},
                     {'n':'培训期数','En':'trainingTimes','v':'.//tr[1]/td[2]/text()','t':'xpath_first'},
                     {'n':'培训地点','En':'trainingPlace','v':'.//tr[1]/td[4]/text()','t':'xpath_first'},
                     {'n':'培训开始日期','En':'startDate','v':'.//tr[2]/td[2]/text()','t':'xpath_first'},
                     {'n':'培训结束日期','En':'endDate','v':'.//tr[2]/td[4]/text()','t':'xpath_first'},
                     {'n':'所属企业名称','En':'company','v':'.//tr[4]/td[4]/text()','t':'xpath_first'},
                     {'n':'职务','En':'position','v':'.//tr[5]/td[2]/text()','t':'xpath_first'},
                     {'n':'学历','En':'education','v':'.//tr[5]/td[4]/text()','t':'xpath_first'},
                     {'n':'职称','En':'Title','v':'.//tr[6]/td[2]/text()','t':'xpath_first'},
                     {'n':'专业','En':'major','v':'.//tr[7]/td[4]/text()','t':'xpath_first'},
                     ]
            }
            ]

chufaConfigs = [{'list':{'n':'','v':'//*[@id="REPORTID_tab1"]//tr[position()>1]','t':'xpath','keys':['code','PunishmentDate','url','Party'],'check':'code','db':'dbo.SZSE_chufa'},
            'data':[
                     {'n':'公司代码','En':'code','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'公司简称','En':'shortname','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'处分日期','En':'PunishmentDate','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'处分类别','En':'PunishmentType','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'当事人','En':'Party','v':'td[5]/text()','t':'xpath_first'},
                     {'n':'标题','En':'title','v':'td[6]/text()','t':'xpath_first'},
                     {'n':'内容','En':'contents','v':'td[7]//@onclick','t':'xpath_first'},
                     {'n':'url','En':'url','v':'td[7]//@onclick','t':'xpath_first'},
                     ]
            }
            ]

zhongjiechufaConfigs = [{'list':{'n':'','v':'//*[@id="REPORTID_tab1"]//tr[position()>1]','t':'xpath','keys':['code','PunishmentDate','url','Party','PunishmentType'],'check':'code','db':'dbo.SZSE_zhongjiechufa'},
            'data':[
                     {'n':'中介机构名称','En':'orgName','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'中介机构类别','En':'orgType','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'处分日期','En':'PunishmentDate','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'处分类别','En':'PunishmentType','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'涉及公司代码','En':'code','v':'td[5]/text()','t':'xpath_first'},
                     {'n':'涉及公司简称','En':'shortname','v':'td[6]/text()','t':'xpath_first'},
                     {'n':'当事人','En':'Party','v':'td[7]/text()','t':'xpath_first'},
                     {'n':'标题','En':'title','v':'td[8]/text()','t':'xpath_first'},
                     {'n':'内容','En':'contents','v':'td[9]//@onclick','t':'xpath_first'},
                     {'n':'url','En':'url','v':'td[9]//@onclick','t':'xpath_first'},
                     ]
            }
            ]

jiechuxianshouConfigs = [{'list':{'n':'','v':'//*[@id="REPORTID_tab1"]//tr[position()>1]','t':'xpath','keys':['code','RelieveLimitDate'],'check':'code','db':'dbo.SZSE_jiechuxianshou'},
            'data':[
                     {'n':'证券代码','En':'code','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortname','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'解除限售日期','En':'RelieveLimitDate','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'本次解除限售股东总数','En':'shareholderS','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'本次解除限售股份总数(股)','En':'shares','v':'td[5]/text()','t':'xpath_first'},
                     {'n':'本次解除限售股份占公司总股本比例(％)','En':'capitalRatio','v':'td[6]/text()','t':'xpath_first'},
                     ]
            }
            ]

jiechuxianshou1perConfigs = [{'list':{'n':'','v':'//*[@id="REPORTID_tab2"]//tr[position()>1]','t':'xpath','keys':['code','HoderName','RelieveLimitDate'],'check':'code','db':'dbo.SZSE_jiechuxianshou1per'},
            'data':[
                     {'n':'证券代码','En':'code','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortname','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'股东名称','En':'HoderName','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'解除限售日期','En':'RelieveLimitDate','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'本次解除限售股份-股数(股)','En':'shares','v':'td[5]/text()','t':'xpath_first'},
                     {'n':'本次解除限售股份-占总股本比例(%)','En':'capitalRatio','v':'td[6]/text()','t':'xpath_first'},
                     {'n':'托管会员名称','En':'Trustee','v':'td[7]/text()','t':'xpath_first'},
                     ]
            }
            ]

jiechuxianshou5perConfigs =  [{'list':{'n':'','v':'//*[@id="REPORTID_tab3"]//tr[position()>1]','t':'xpath','keys':['code','HoderName','disclosureDate'],'check':'code','db':'dbo.SZSE_jiechuxianshou5per'},
            'data':[
                     {'n':'证券代码','En':'code','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortname','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'股东名称','En':'HoderName','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'披露日期','En':'disclosureDate','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'本次披露减持股份-股数(股)','En':'reduceSharesThis','v':'td[5]/text()','t':'xpath_first'},
                     {'n':'本次披露减持股份-占总股本比例(%)','En':'reducecapitalRatioThis','v':'td[6]/text()','t':'xpath_first'},
                     {'n':'通过大宗交易减持-股数(股)','En':'reduceSharesBlocktrade','v':'td[7]/text()','t':'xpath_first'},
                     {'n':'通过大宗交易减持-占总股本比例(%)','En':'reducecapitalBlocktrade','v':'td[8]/text()','t':'xpath_first'},
                     {'n':'减持后仍持有股份-股数(股)','En':'SharesAfter','v':'td[9]/text()','t':'xpath_first'},
                     {'n':'减持后仍持有股份-占总股本比例(%)','En':'capitalAfter','v':'td[10]/text()','t':'xpath_first'},
                     ]
            }
            ]

sghgqdInfoConfigs = [{'list':{'n':'','v':'','t':'','keys':['fundCode','regDate'],'check':'fundCode','db':'dbo.SZSE_sghgqdInfo'},
            'data':[
                     {'n':'标题','En':'title','v':'\S*清单','t':'regex0'},
                     {'n':'登记日','En':'regDate','v':'\d{4}-\d{2}-\d{2}','t':'regex0'},
                     {'n':'基金名称','En':'fundName','v':'基金名称：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'基金管理公司名称','En':'ManagerName','v':'基金管理公司名称：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'基金代码','En':'fundCode','v':'基金代码：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'目标指数代码','En':'Targetcode','v':'目标指数代码：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'基金类型','En':'fundType','v':'基金类型：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'现金差额','En':'CashBalance','v':' 现金差额：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'最小申购、赎回单位资产净值','En':'minasset','v':'最小申购、赎回单位资产净值：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'基金份额净值','En':'NetFundShare','v':'基金份额净值：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'预估现金差额','En':'EstimatedCashBalance','v':'预估现金差额：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'可以现金替代比例上限','En':'CashSubstitutionRitio','v':'可以现金替代比例上限：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'是否需要公布IOPV','En':'IOPV','v':'是否需要公布IOPV：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'最小申购、赎回单位','En':'MinUnit','v':'最小申购、赎回单位：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'最小申购赎回单位现金红利','En':'MinDividendUnit','v':'最小申购赎回单位现金红利：\s{2,10}(\S*)','t':'regex1'},
                     {'n':' 申购赎回组合证券只数','En':'StockNumber','v':' 申购赎回组合证券只数：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'全部申购赎回组合证券只数','En':'StockAllNumber','v':'全部申购赎回组合证券只数：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'是否开放申购','En':'IsApply','v':'是否开放申购：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'是否开放赎回','En':'IsRedeem','v':'是否开放赎回：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'当天净申购的基金份额上限','En':'SubscriptionCeiling','v':'当天净申购的基金份额上限：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'当天净赎回的基金份额上限','En':'RedemptionCeiling','v':'当天净赎回的基金份额上限：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'单个证券账户当天净申购的基金份额上限','En':'SubscriptionCeilingPer','v':'单个证券账户当天净申购的基金份额上限：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'单个证券账户当天净赎回的基金份额上限','En':'RedemptionCeilingPer','v':'单个证券账户当天净赎回的基金份额上限：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'当天累计可申购的基金份额上限','En':'CumulativeSubscriptionCeiling','v':'当天累计可申购的基金份额上限：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'当天累计可赎回的基金份额上限','En':'CumulativeRedemptionCeiling','v':'当天累计可赎回的基金份额上限：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'单个证券账户当天累计可申购的基金份额上限','En':'CumulativeSubscriptionCeilingPer','v':'单个证券账户当天累计可申购的基金份额上限：\s{2,10}(\S*)','t':'regex1'},
                     {'n':'单个证券账户当天累计可赎回的基金份额上限','En':'CumulativeRedemptionCeilingPer','v':'单个证券账户当天累计可赎回的基金份额上限：\s{2,10}(\S*)','t':'regex1'},
                     ]
            }
            ]

sghgqdInfo2Configs = [{'list':{'n':'','v':'','t':'','keys':['code','regcode','regDate'],'check':'code','db':'dbo.SZSE_sghgqdInfo2'},
            'data':[
                    {'n':'登记日期','En':'regDate','v':'regDate','t':'json'},
                    {'n':'申购赎回清单基金代码','En':'regcode','v':'regcode','t':'json'},
                    {'n':'证券代码','En':'code','v':'code','t':'json'},
                    {'n':'证券简称','En':'name','v':'name','t':'json'},
                    {'n':'股份数量','En':'shares','v':'shares','t':'json'},
                    {'n':'现金替代标志','En':'label','v':'label','t':'json'},
                    {'n':'现金替代保证金率','En':'Ritio','v':'Ritio','t':'json'},
                    {'n':'挂牌市场','En':'market','v':'market','t':'json'},
                    {'n':'赎回替代金额','En':'shuhui','v':'shuhui','t':'json'},
                    {'n':'申购替代金额','En':'shendai','v':'shendai','t':'json'},
                    ]
            }
            ]

zcjhcjxxConfigs =  [{'list':{'n':'','v':'//*[@id="REPORTID_tab1"]//tr[position()>1]','t':'xpath','keys':['code','TransactionDate','TransactionNumbers'],'check':'code','db':'dbo.SZSE_zcjhcjxx'},
            'data':[
                     {'n':'交易日期','En':'TransactionDate','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'证券代码','En':'code','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortName','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'管理人','En':'manager','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'成交价格(元)','En':'TransactionPrice','v':'td[5]/text()','t':'xpath_first'},
                     {'n':'成交数量（份）','En':'TransactionNumbers','v':'td[6]/text()','t':'xpath_first'},
                     {'n':'成交金额（元）','En':'TransactionAmount','v':'td[7]/text()','t':'xpath_first'},
                     
                     ]
            }
            ]  

zcjhcpxxConfigs =   [{'list':{'n':'','v':'//*[@id="REPORTID_tab1"]//tr[position()>1]','t':'xpath','keys':['code','ProdName'],'check':'code','db':'dbo.SZSE_zcjhcpxx'},
            'data':[
                     {'n':'产品名称','En':'ProdName','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'证券代码','En':'code','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortName','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'转让开始日','En':'transferStartDate','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'转让到期日','En':'transferEndDate','v':'td[5]/text()','t':'xpath_first'},
                     {'n':'管理人','En':'manager','v':'td[6]/text()','t':'xpath_first'},
                     {'n':'转让范围','En':'transferRange','v':'td[7]/text()','t':'xpath_first'},
                     
                     ]
            }
            ]  

tfpxxConfigs =   [{'list':{'n':'','v':'//*[@id="REPORTID_tab1"]//tr[position()>1]','t':'xpath','keys':['code','Suspensiontime','resumptiontime','limittime','Suspensionreason'],'check':'code','db':'dbo.SZSE_tfpxx'},
            'data':[
                     {'n':'证券代码','En':'code','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortName','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'停牌时间','En':'Suspensiontime','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'复牌时间','En':'resumptiontime','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'停牌期限','En':'limittime','v':'td[5]/text()','t':'xpath_first'},
                     {'n':'停牌原因','En':'Suspensionreason','v':'td[6]/text()','t':'xpath_first'},
                     ]
            }
            ]    

stockinfoParse_configs = {'flag':True,
                  'list':{'n':'','v':'//table[@class="cls-data-table-detail"]','t':'xpath','check':'ComName','keys':['ComCode'],'db':'dbo.SZSE_stockinfo'},
                  'data':[{'n':'公司名称','En':'ComName','t':'xpath_first','v':'tr[1]/td[2]/text()'},
                           {'n':'公司代码','En':'ComCode','t':'meta','v':'code'},
                           {'n':'英文名称','En':'comEname','t':'xpath_first','v':'tr[2]/td[2]/text()'},
                           {'n':'注册地址','En':'Reg_address','t':'xpath_first','v':'tr[3]/td[2]/text()'},
                           {'n':'A股代码','En':'AshareCode','t':'xpath_first','v':'tr[4]/td[2]/text()'},
                           {'n':'A股简称','En':'AshortName','t':'xpath_first','v':'tr[4]/td[4]/text()'},
                           {'n':'A股上市日期','En':'AlistingDate','t':'xpath_first','v':'tr[5]/td[2]/text()'},
                           {'n':'A股总股本','En':'Ashares1','t':'xpath_first','v':'tr[5]/td[4]/text()'},
                           {'n':'A股流通股本','En':'Ashares2','t':'xpath_first','v':'tr[5]/td[6]/text()'},
                           {'n':'B股代码','En':'Bcode','t':'xpath_first','v':'tr[6]/td[2]/text()'},
                           {'n':'B股 简 称','En':'BshortName','t':'xpath_first','v':'tr[6]/td[4]/text()'},
                           {'n':'B股上市日期','En':'BlistingDate','t':'xpath_first','v':'tr[7]/td[2]/text()'},
                           {'n':'B股总股本','En':'BShareCapital','t':'xpath_first','v':'tr[7]/td[4]/text()'},
                           {'n':'B股流通股本','En':'BShareCapitalCirculating','t':'xpath_first','v':'tr[7]/td[6]/text()'},
                           {'n':'地 区','En':'Areas','t':'xpath_first','v':'tr[8]/td[2]/text()'},
                           {'n':'省 份','En':'Provincen','t':'xpath_first','v':'tr[8]/td[4]/text()'},
                           {'n':'城 市','En':'city','t':'xpath_first','v':'tr[8]/td[6]/text()'},
                           {'n':'所属行业','En':'Industry','t':'xpath_first','v':'tr[9]/td[2]/text()'},
                           {'n':'公司网址','En':'website','t':'xpath_first','v':'tr[10]/td[2]/a/text()'},

                            ],
                    }  

fundConfigs = [{'list':{'n':'','v':'//*[@id="REPORTID_tab1"]//tr[position()>1]','t':'xpath','keys':['fundcode'],'check':'fundcode','db':'dbo.SZSE_fund'},
            'data':[
                     {'n':'基金代码','En':'fundcode','v':'td[1]//u/text()','t':'xpath_first'},
                     {'n':'基金简称','En':'shortName','v':'td[2]//u/text()','t':'xpath_first'},
                     {'n':'上市日期','En':'ListingDate','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'当前规模(份)','En':'Scale','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'基金管理人','En':'managerName','v':'td[5]/text()','t':'xpath_first'},
                     ]
            }
            ]  

zqConfigs  = [{'list':{'n':'','v':'//*[@id="REPORTID_tab1"]//tr[position()>1]','t':'xpath','keys':['code'],'check':'shortName','db':'dbo.SZSE_zq'},
            'data':[
                     {'n':'证券代码','En':'code','v':'td[1]//u/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortName','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'上市日期','En':'ListingDate','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'发行量(亿)','En':'publishScale','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'起息日期','En':'InterestDate','v':'td[5]/text()','t':'xpath_first'},
                     {'n':'到期日期','En':'DueDate','v':'td[6]/text()','t':'xpath_first'},
                     {'n':'票面利率','En':'CouponRate','v':'td[7]/text()','t':'xpath_first'},
                     {'n':'挂牌方式','En':'ListingMethod','v':'td[8]/text()','t':'xpath_first'},
                     ]
            }
            ] 

fullnamechangeConfigs = [{'list':{'n':'','v':'//*[@id="REPORTID_tab1"]//tr[position()>1]','t':'xpath','keys':['code','changeDate'],'check':'shortname','db':'dbo.SZSE_fullnamechange'},
            'data':[
                     {'n':'变更日期','En':'changeDate','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'证券代码','En':'code','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortname','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'变更前全称','En':'fullNamedBefore','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'变更后全称','En':'fullNamedAfter','v':'td[5]/text()','t':'xpath_first'},
                     ]
            }
            ] 

shortnamechangeConfigs = [{'list':{'n':'','v':'//*[@id="REPORTID_tab2"]//tr[position()>1]','t':'xpath','keys':['code','changeDate'],'check':'shortname','db':'dbo.SZSE_shortnamechange'},
            'data':[
                     {'n':'变更日期','En':'changeDate','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'证券代码','En':'code','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortname','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'变更前简称','En':'shortNamedBefore','v':'td[4]/text()','t':'xpath_first'},
                     {'n':'变更后简称','En':'shortNamedAfter','v':'td[5]/text()','t':'xpath_first'},
                     ]
            }
            ] 

suspendListingConfigs = [{'list':{'n':'','v':'//*[@id="REPORTID_tab1"]//tr[position()>1]','t':'xpath','keys':['code','suspendListingDate'],'check':'shortName','db':'dbo.SZSE_suspendListing'},
            'data':[
                     {'n':'证券代码','En':'code','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortName','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'上市日期','En':'ListingDate','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'暂停上市日期','En':'suspendListingDate','v':'td[4]/text()','t':'xpath_first'},
                     ]
            }
            ]

StopListingConfigs = [{'list':{'n':'','v':'//*[@id="REPORTID_tab2"]//tr[position()>1]','t':'xpath','keys':['code','StopListingDate'],'check':'shortName','db':'dbo.SZSE_StopListing'},
            'data':[
                     {'n':'证券代码','En':'code','v':'td[1]/text()','t':'xpath_first'},
                     {'n':'证券简称','En':'shortName','v':'td[2]/text()','t':'xpath_first'},
                     {'n':'上市日期','En':'ListingDate','v':'td[3]/text()','t':'xpath_first'},
                     {'n':'终止上市日期','En':'StopListingDate','v':'td[4]/text()','t':'xpath_first'},
                     ]
            }
            ] 

projInfoConfigs =  [{'list':{'n':'','v':'','t':'','keys':['bondName','Update_Date'],'check':'bondName','db':'dbo.SZSE_projInfo'},
            'data':[
                     {'n':'债券名称','En':'bondName','v':'//table[@id="xmjdxx_xqtab1" or @id="xmjdxx_xgmxqtab1"]//tr[1]/td[2]/text()','t':'xpath_first'},
                     {'n':'债券类别','En':'bondType','v':'//table[@id="xmjdxx_xqtab1" or @id="xmjdxx_xgmxqtab1"]//tr[2]/td[2]/text()','t':'xpath_first'},
                     {'n':'拟发行金额（单位：亿元）','En':'publishScale','v':'//table[@id="xmjdxx_xqtab1" or @id="xmjdxx_xgmxqtab1"]//tr[3]/td[2]/text()','t':'xpath_first'},
                     {'n':'发行人','En':'publisher','v':'//table[@id="xmjdxx_xqtab1" or @id="xmjdxx_xgmxqtab1"]//tr[4]/td[2]/text()','t':'xpath_first'},
                     {'n':'地区','En':'areas','v':'//table[@id="xmjdxx_xqtab1" or @id="xmjdxx_xgmxqtab1"]//tr[5]/td[2]/text()','t':'xpath_first'},
                     {'n':'行业','En':'Industry','v':'//table[@id="xmjdxx_xqtab1" or @id="xmjdxx_xgmxqtab1"]//tr[6]/td[2]/text()','t':'xpath_first'},
                     {'n':'承销商/管理人','En':'Manger','v':'//table[@id="xmjdxx_xqtab1" or @id="xmjdxx_xgmxqtab1"]//tr[7]/td[2]/text()','t':'xpath_first'},
                     {'n':'项目状态','En':'ProjStatus','v':'//table[@id="xmjdxx_xqtab1" or @id="xmjdxx_xgmxqtab1"]//tr[8]/td[2]/text()','t':'xpath_first'},
                     {'n':'更新日期','En':'Update_Date','v':'//table[@id="xmjdxx_xqtab1" or @id="xmjdxx_xgmxqtab1"]//tr[9]/td[2]/text()','t':'xpath_first'},
                     {'n':'募集说明书URL','En':'ProspectusUrl','v':'//*[@id="REPORTID_tab2"]//@onclick','t':'xpath_first'},
                     {'n':'反馈意见URL ','En':'FeedbackUrl','v':'//*[@id="REPORTID_tab3"]//@onclick','t':'xpath_first'},
#                     文本太大 放弃
#                     {'n':'募集说明书','En':'ProspectusContent','v':'//*[@id="REPORTID_tab2"]//@onclick','t':'xpath_first'},
#                     {'n':'反馈意见 ','En':'FeedbackContent','v':'//*[@id="REPORTID_tab3"]//@onclick','t':'xpath_first'}
                     ]
            }
            ]

