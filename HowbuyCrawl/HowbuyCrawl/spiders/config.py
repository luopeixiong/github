# -*- coding: utf-8 -*-

import re
def func(a):
    print(a)
    return a

#处理好买私募产品列表页post表单
def postdata_Prod(page,perPage=20,allPage=''):
    data = {"orderType": "Desc",
                "sortField": "hb1n",
                "ejfl": "",
                "sylx": "J",
                "gzkxd": "1",
                "jgxs": "",
                "skey": "",
                "page": str(page),
                "perPage": str(perPage),
                "allPage": str(allPage),
                "targetPage": ""}
    return data
#处理好买私募公司列表页post表单
def company_data(page,perPage=20,allPage=''):
#        """构造howbuy 私募基金公司列表页post 表单"""
    data = {"orderType": "Desc",
            "sortField": "hb1nscclzyjj",
            "ejflsccl": "",
            "djbh": "",
            "skey": "",
            "page": str(page),
            "perPage": str(perPage),
            "allPage": str(allPage),
            "targetPage": ""}
    return data
#处理好买私募经理列表页post表单
def Manager_data(page,perPage=20,allPage=''):
#        """构造howbuy 私募基金经理列表页post 表单"""        
    data = {"cynxRang":"",
            "orderType":"Desc",
            "sortField":"hb1nscclzyjj",
            "ejflsccl":"",
            "jjjlly":"",
            "skey":"",
            "page":str(page),
            "perPage":str(perPage),
            "allPage":str(allPage),
            "targetPage":"",
            }
    return data
#处理好买公募基金产品抓取配置
config_fundProdinfo = [
                          {'list':{'n':'','v':'//div[@class="fund_Overview_a"]/table','t':'xpath','db':''},
                           'data':[{'n':'基金简称','En':'fund_short_name','v':'.//tr[1]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'基金代码','En':'fund_code','v':'.//tr[1]/td[4]/text()','t':'xpath_first','dt':''},
                               {'n':'基金全称','En':'fund_fullName','v':'.//tr[2]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'基金类型','En':'fund_Type','v':'.//tr[3]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'成立日期','En':'setup_date','v':'.//tr[3]/td[4]/text()','t':'xpath_first','dt':''},
                               {'n':'基金状态','En':'fund_status','v':'.//tr[4]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'交易状态','En':'status','v':'.//tr[4]/td[4]/text()','t':'xpath_first','dt':''},
                               {'n':'基金公司','En':'fund_com','v':'.//tr[5]/td[2]/a/text()','t':'xpath_first','dt':''},
                               {'n':'基金公司','En':'fund_comID','v':'.//tr[5]/td[2]/a/@href','t':'xpath_first','dt':''},
                               {'n':'基金经理','En':'fund_manger','v':'.//tr[5]/td[4]/a/text()','t':'xpath_first','dt':''},
                               {'n':'基金经理','En':'fund_mangerID','v':'.//tr[5]/td[4]/a/@href','t':'xpath_first','dt':''},
                               {'n':'基金管理费','En':'fund_mangerFee','v':'.//tr[6]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'基金托管费','En':'fund_trusteeFee','v':'.//tr[6]/td[4]/text()','t':'xpath_first','dt':''},
                               {'n':'首募规模','En':'First_scale','v':'.//tr[7]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'最新份额','En':'newst_share','v':'.//tr[7]/td[4]/text()','t':'xpath_first','dt':''},
                               {'n':'托管银行','En':'trusteeBank','v':'.//tr[8]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'最新规模','En':'newst_scale','v':'.//tr[8]/td[4]/text()','t':'xpath_first','dt':''},
                               ]
                           }
                     ]
#处理好买公募基金产品列表页配置
config_fundProd = {'list':{'n':'','v':'','t':'','db':'','v':''},
                   'nextpage':{'n':'','v':'','method':'get'},
                   'data':[{'n':'','En':'','v':'','t':'','dt':''},
                           ],
#                    'geturl':{'t':'xpathSet','v':'//table//tr[td[3]/a[@href]]/td[3]/a/@href'},
                    'geturl':{'t':'re_findall','v':'\"/fund/(\d+?)/\"'},
                    'format':'https://www.howbuy.com/fund/ajax/gmfund/fundsummary.htm?jjdm={0}',
                    'postdata':func,
                    'method':'get',
#                    'htmlreplace':[('<textarea style="display:none">','<table>'),('</textarea>','</table>')],
                    'htmlreplace':'',
                    'callback':'self.infoParse',
                    'encoding':'utf-8',
                   }
#处理好买公募基金公司抓取配置
config_fundCominfo = [{'list':{'n':'','v':'//div[@class="strength_content"]','t':'xpath','db':''},
                       'data':[{'En':'Com_name','n':'公司名称','v':'.//tr[1]/td[2]/span/text()','t':'xpath_first','dt':''},
                               {'En':'Org_form','n':'组织形式','v':'.//tr[1]/td[4]/span/text()','t':'xpath_first','dt':''},
                               {'En':'Reg_capital','n':'注册资本','v':'.//tr[2]/td[2]/span/text()','t':'xpath_first','dt':''},
                               {'En':'General_manager','n':'总经理','v':'.//tr[2]/td[4]/span/text()','t':'xpath_first','dt':''},
                               {'En':'Legal_representative','n':'法定代表人','v':'.//tr[3]/td[2]/span/text()','t':'xpath_first','dt':''},
                               {'En':'Chairman','n':'董事长','v':'.//tr[3]/td[4]/span/text()','t':'xpath_first','dt':''},
                               {'En':'office_address','n':'办公地址','v':'.//tr[4]/td[2]/span/text()','t':'xpath_first','dt':''},
                               {'En':'Reg_address','n':'注册地址','v':'.//tr[5]/td[2]/span/text()','t':'xpath_first','dt':''},
                               {'En':'Tel','n':'公司电话','v':'.//tr[6]/td[2]/span/text()','t':'xpath_first','dt':''},
                               {'En':'Fax','n':'公司传真','v':'.//tr[6]/td[4]/span/text()','t':'xpath_first','dt':''},
                               {'En':'Email','n':'电子邮箱','v':'.//tr[7]/td[2]/span/text()','t':'xpath_first','dt':''},
                               {'En':'website','n':'公司网址','v':'.//tr[7]/td[4]/span/text()','t':'xpath_first','dt':''},
                               {'En':'service_Tel','n':'客服电话','v':'.//tr[8]/td[2]/span/text()','t':'xpath_first','dt':''},
                               {'En':'Prod_nums','n':'公司旗下产品数','v':'.//tr[9]/td[2]/a/text()','t':'xpath_first','dt':''},
                               {'En':'manager_nums','n':'旗下基金经理数','v':'.//tr[9]/td[4]/a/text()','t':'xpath_first','dt':''},
                               {'En':'capital_scale','n':'公司资产规模','v':'.//tr[10]/td[2]/span/text()','t':'xpath_first','dt':''},
                               {'En':'Com_id','n':'好买ID','v':'company\/(.*?)\/','t':'url_re','dt':''}
                               ]
                   }]
#处理好买公募基金公司列表配置
config_fundCom = {'list':{'n':'','v':'','t':'','db':'','v':''},
                   'nextpage':{'n':'','v':'','method':'get'},
                   'data':[{'n':'','En':'','v':'','t':'','dt':''},
                           ],
                    'geturl':{'t':'re_findall','v':'\/fund\/company\/(\d+?)\/'},
                    'format':'https://www.howbuy.com/fund/company/{0}/files/',
                    'postdata':func,
                    'method':'get',
                    'callback':'self.infoParse',
                    'encoding':'utf-8',
                    'htmlreplace':'',
                   }
#处理好买公募基金经理信息抓取配置
config_fundManinfo = [{'list':{'n':'','v':'','t':'','db':''},
                       'data':[{'n':'经理姓名:','En':'manager_name','v':'//div[@class="manager_name"]/text()','t':'xpath_first','dt':''},
                               {'n':'当前所在公司:','En':'Current_companyName','v':'//li[@class="info_item" and contains(text(),"当前所在公司: ")]/a/text()','t':'xpath_first','dt':''},
                               {'n':'当前所在公司ID:','En':'Current_companyID','v':'//li[@class="info_item" and contains(text(),"当前所在公司: ")]/a/@href','t':'xpath_first','dt':''},
                               {'n':'最擅长的基金类型','En':'best_types','v':'//li[@class="info_item" and contains(text(),"最擅长的基金类型: ")]/span/text()','t':'xpath_first','dt':''},
                               {'n':'代表基金','En':'Representative_fund','v':'//li[@class="info_item" and contains(text(),"代表基金: ")]/a/text()','t':'xpath_first','dt':''},
                               {'n':'代表基金ID','En':'Representative_fundID','v':'//li[@class="info_item" and contains(text(),"代表基金: ")]/a/@href','t':'xpath_first','dt':''},
                               {'n':'好买人气指数','En':'popularity_Hb','v':'//li[@class="info_item" and contains(text(),"人气指数: ")]/span/text()','t':'xpath_first','dt':''},
                               {'n':'好买点评','En':'Comment_Hb','v':'//div[@class="hb_reviews clearfix"]/div[2]/text()','t':'xpath_first','dt':''},
                               {'n':'简介','En':'introduction','v':'//div[@class="des_con"]/text()','t':'xpath_first','dt':''},
                               {'n':'首次任职时间','En':'First_manager_date','v':'//tr[td[text()="首次任职时间"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'任基金经理时间','En':'manager_time','v':'//tr[td[text()="任基金经理时间"]]/td[4]/text()','t':'xpath_first','dt':''},
                               {'n':'历任公司数','En':'Successive_Coms','v':'//tr[td[text()="历任公司数"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'跳槽频率','En':'Job_hopping_frequency','v':'//tr[td[text()="跳槽频率"]]/td[4]/text()','t':'xpath_first','dt':''},
                               {'n':'历史管理基金数','En':'history_ProdNums','v':'//tr[td[text()="历史管理基金数"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'从业年均回报','En':'ave_yield_ratio','v':'//tr[td[text()="从业年均回报"]]/td[4]/span/text()','t':'xpath_first','dt':''},
                               {'n':'当前管理基金数量','En':'manager_Prod_nums','v':'//div[@class="contrast_title fl" and contains(text(),"当前管理基金")]/span/text()','t':'xpath_first','dt':''},
                               {'n':'管理最长基金','En':'longest_Prod','v':'//div[@class="content_r fr" and div[contains(text(),"管理时间最长的基金")]]/div[2]/a/text()','t':'xpath_first','dt':''},
                               {'n':'管理最长基金ID','En':'longest_ProdID','v':'//div[@class="content_r fr" and div[contains(text(),"管理时间最长的基金")]]/div[2]/a/@href','t':'xpath_first','dt':''},
                               {'n':'好买头像weisite','En':'img_website','v':'//div[@class="manager_info_left fl"]//@src','t':'xpath_first','dt':''},
                               {'n':'经理好买ID','En':'manager_Hbid','v':'manager\/(\d+?)\/','t':'url_re','dt':''}
                               ]
                   }]
#处理好买公募基金经理列表配置
config_fundMan = {'list':{'n':'','v':'','t':'','db':'','v':''},
                   'nextpage':{'n':'','v':'','method':'get'},
                   'data':[{'n':'','En':'','v':'','t':'','dt':''},
                           ],
                    'geturl':{'t':'re_findall','v':'\/fund\/manager\/(\d+?)\/'},
                    'format':'https://www.howbuy.com/fund/manager/{}/',
                    'postdata':func,
                    'method':'get',
                    'callback':'self.infoParse',
                    'encoding':'utf-8',
                    'htmlreplace':'',
                   }
#处理好买私募基金产品抓取配置
config_simuProdinfo=[{'list':{'n':'','v':'','t':'','db':''},
                       'data':[{'n':'基金全称:','En':'Private_fund_name','v':'//tr[td[text()="基金全称"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'基金类型:','En':'Private_fundType','v':'//tr[td[text()="基金类型"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'组织形式:','En':'Org_form','v':'//tr[td[text()="组织形式"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'托管银行','En':'trustee_bank','v':'//tr[td[text()="托管银行"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'开放日期','En':'openDate','v':'//tr[td[text()="开放日期"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'币种','En':'currency','v':'//tr[td[text()="币种"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'封闭期','En':'closedDate','v':'//tr[td[text()="封闭期"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'备案号','En':'Record_num','v':'//tr[td[text()="备案号"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'成立日期','En':'setupDate','v':'//tr[td[text()="成立日期"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'结构形式','En':'structural_form','v':'//tr[td[text()="结构形式"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'基金发行人','En':'Publisher','v':'//tr[td[text()="基金发行人"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'基金状态','En':'Private_fundStatus','v':'//tr[td[text()="基金状态"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'净值单位','En':'Net_unit','v':'//tr[td[text()="净值单位"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'准封闭期','En':'Quasi_closed_period','v':'//tr[td[text()="准封闭期"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'风险等级','En':'Risk_grade','v':'//tr[td[text()="风险等级"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'基金公司','En':'manager_comName','v':'//div[@class="trade_fund_top_dotted_bott"]//p[contains(text(),"基金公司")]//a/text()','t':'xpath_first','dt':''},
                               {'n':'基金公司ID','En':'manager_comID','v':'//div[@class="trade_fund_top_dotted_bott"]//p[contains(text(),"基金公司")]//a/@href','t':'xpath_first','dt':''},
                               {'n':'基金经理','En':'manager_name','v':'//div[@class="trade_fund_top_dotted_bott"]//p[contains(text(),"基金经理")]//a/text()','t':'xpath_first','dt':''},
                               {'n':'基金经理ID','En':'manager_ID','v':'//div[@class="trade_fund_top_dotted_bott"]//p[contains(text(),"基金经理")]//a/@href','t':'xpath_first','dt':''},
                               ]
                       }
                    ]
#处理好买私募基金产品列表配置
config_simuProd = {'list':{'n':'','v':'','t':'','db':'','v':''},
                   'nextpage':{'n':'','v':'','postFormRequest':'get'},
                   'data':[{'n':'','En':'','v':'','t':'','dt':''},
                           ],
                    #https://simu.howbuy.com/meigang/S28074/
                    'geturl':{'t':'re_findall','v':'\"(https?:\/\/simu\.howbuy\.com\/[a-z1-9|-]+?\/[A-Z]{1,2}\d+?\/)\"'},
                    'postdata':postdata_Prod,
                    'format':'{0}',
                    'postdata_type':'',
                    'method':'get',
                    'callback':'self.infoParse',
                    'encoding':'utf-8',
                    'htmlreplace':'',
                   }
#处理好买私募基金公司抓取配置
config_simuCominfo = [{'list':{'n':'','v':'','t':'','db':''},
                       'data':[{'En':'Com_name','n':'公司名称','v':'//h2/text()','t':'xpath_first','dt':''},
                               {'En':'Org_form','n':'成立日期','v':'//li[contains(text(),"成立日期")]/span[1]/text()','t':'xpath_first','dt':''},
                               {'En':'Reg_capital','n':'注册资本','v':'//li[contains(text(),"注册资本：")]/span/text()','t':'xpath_first','dt':''},
                               {'En':'Com_Type','n':'公司类型','v':'//li[contains(text(),"公司类型")]/text()','t':'xpath_first','dt':''},
                               {'En':'Com_location','n':'所在区域','v':'//li[contains(text(),"所在区域：")]/span[1]/text()','t':'xpath_first','dt':''},
                               {'En':'Record_Nums','n':'备案证号','v':'//li[contains(text(),"备案证号：")]/span[1]/text()','t':'xpath_first','dt':''},
                               {'En':'Investment_idea','n':'投资理念','v':'//div[@class="review_rt lt"]/text()','t':'xpath_first','dt':''},
                               {'En':'Research_team','n':'投研团队','v':'//div[@class="item_con1 clearfix" and parent::div[@id="company_intro1"]]/ul[2]/li[3]/i/text()','t':'xpath_first','dt':''},
                               {'En':'fund_nums','n':'基金数量','v':'//div[@class="item_con1 clearfix" and parent::div[@id="company_intro1"]]/ul[2]/li[4]/i/text()','t':'xpath_first','dt':''},
                               {'En':'manager_nums','n':'基金经理人数','v':'//div[@class="item_con1 clearfix" and parent::div[@id="company_intro1"]]/ul[2]/li[5]/i/text()','t':'xpath_first','dt':''},
                               {'En':'setuptime','n':'成立时间（年）','v':'//div[@class="item_con1 clearfix" and parent::div[@id="company_intro1"]]/ul[2]/li[2]/i/text()','t':'xpath_first','dt':''},
                               {'En':'Com_id','n':'好买ID','v':'simu.howbuy.com\/(\w+?)\/','t':'url_re','dt':''}
                               ]
                   }]
#处理好买私募基金公司列表页配置
config_simuCom = {'list':{'n':'simuCom','v':'','t':'','db':'','v':''},
                   'nextpage':{'n':'','v':'','postFormRequest':'get'},
                   'data':[{'n':'','En':'','v':'','t':'','dt':''},
                           ],
                    'geturl':{'t':'xpathList','v':'//tr[@class="tr_normal"]/td[2]/a[2]/@href'},
                    'postdata':func,
                    'format':'{0}',
                    'method':'get',
                    'callback':'self.infoParse',
                    'encoding':'utf-8',
                    'htmlreplace':'',
                   }
#处理好买私募基金经理抓取配置
config_simuManinfo = [{'list':{'n':'','v':'','t':'','db':''},
                       'data':[{'n':'经理姓名:','En':'manager_name','v':'//div[@class="manager_name"]/text()','t':'xpath_first','dt':''},
                               {'n':'当前所在公司:','En':'Current_companyName','v':'//li[@class="info_item" and contains(text(),"所在公司: ")]/a/text()','t':'xpath_first','dt':''},
                               {'n':'当前所在公司ID:','En':'Current_companyID','v':'//li[@class="info_item" and contains(text(),"所在公司: ")]/a/@href','t':'xpath_first','dt':''},
                               {'n':'最擅长的基金类型','En':'best_types','v':'//li[@class="info_item" and contains(text(),"擅长类型: ")]/span/text()','t':'xpath_first','dt':''},
                               {'n':'代表基金','En':'Representative_fund','v':'//li[@class="info_item" and contains(text(),"代表基金: ")]/a/text()','t':'xpath_first','dt':''},
                               {'n':'代表基金ID','En':'Representative_fundID','v':'//li[@class="info_item" and contains(text(),"代表基金: ")]/a/@href','t':'xpath_first','dt':''},
                               {'n':'所获奖项','En':'Awards','v':'//li[@class="info_item" and contains(text(),"所获奖项: ")]/span/text()','t':'xpath_first','dt':''},
                               {'n':'简介','En':'introduction','v':'//div[@class="des_con"]/text()','t':'xpath_first','dt':''},
                               {'n':'从业年限','En':'PractitionersYears','v':'//tr[td[text()="从业年限"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'任职私募年限','En':'PrivateYears','v':'//tr[td[text()="任职私募年限"]]/td[4]/text()','t':'xpath_first','dt':''},
                               {'n':'履历背景','En':'background','v':'//tr[td[text()="履历背景"]]/td[2]/text()','t':'xpath_first','dt':''},
                               {'n':'任职私募日期','En':'PrivateDate','v':'//tr[td[text()="任职私募日期"]]/td[4]/text()','t':'xpath_first','dt':''},
                               {'n':'年均回报','En':'Yearyield','v':'//tr[td[text()="年均回报"]]/td[2]/span/text()','t':'xpath_first','dt':''},
                               {'n':'管理基金数量','En':'management_fund','v':'//tr[td[text()="管理基金数量"]]/td[4]/text()','t':'xpath_first','dt':''},
                               {'n':'过往履历','En':'Resume','v':'//tr[td[text()="过往履历"]]/td[4]/span/text()','t':'xpath_first','dt':''},
                               {'n':'当前管理基金数量','En':'management_fundNow','v':'//div[@class="contrast_title mt15" and contains(text(),"当前管理基金")]/span/text()','t':'xpath_first','dt':''},
                               {'n':'管理最长基金','En':'longest_Prod','v':'//div[@class="content_r fr" and div[contains(text(),"管理时间最长的基金")]]/div[2]/a/text()','t':'xpath_first','dt':''},
                               {'n':'管理最长基金ID','En':'longest_ProdID','v':'//div[@class="content_r fr" and div[contains(text(),"管理时间最长的基金")]]/div[2]/a/@href','t':'xpath_first','dt':''},
                               {'n':'好买头像weisite','En':'img_website','v':'//div[@class="manager_info_left fl"]//@src','t':'xpath_first','dt':''},
                               {'n':'经理好买ID','En':'manager_Hbid','v':'https:\/\/simu\.howbuy\.com\/manager\/(\d+)\.html','t':'url_re','dt':''}
                               ]
                   }]
#处理好买私募经理列表配置                   
config_simuMan = {'list':{'n':'','v':'','t':'','db':'','v':''},
                   'nextpage':{'n':'','v':'','postFormRequest':'get'},
                   'data':[{'n':'','En':'','v':'','t':'','dt':''},
                           ],
                    'geturl':{'t':'re_findall','v':'\"\/manager\/(\d+?)\.html\"'},
                    'format':'https://simu.howbuy.com/manager/{}.html',
                    'postdata':'func',
                    'method':'get',
                    'callback':'self.infoParse',
                    'encoding':'utf-8',
                    'htmlreplace':'',
                   }
#列表页config选择器
def parseChioce(url):
    flags = [{'regex':r'https://www.howbuy.com/fund/fundranking','configs':config_fundProd},
             {'regex':r'https://www.howbuy.com/fund/company','configs':config_fundCom},
             {'regex':r'https://www.howbuy.com/fund/manager','configs':config_fundMan},
             {'regex':r'https://simu.howbuy.com/mlboard.htm','configs':config_simuProd},
             {'regex':r'https://simu.howbuy.com/manager','configs':config_simuMan},
             {'regex':r'https://simu.howbuy.com/company','configs':config_simuCom},
            ]
    for _ in flags:
        if re.search(_['regex'],url):
            return _['configs']
#抓取页config选择器
def configIngochange(url):
    flags = [{'regex':r'^https://www.howbuy.com/fund/ajax/gmfund/fundsummary.htm\?jjdm=\d+$','configs':config_fundProdinfo},
             {'regex':r'^https://www.howbuy.com/fund/company/\d+?/files/$','configs':config_fundCominfo},
             {'regex':r'^https://www.howbuy.com/fund/manager/\d+?/$','configs':config_fundManinfo},
             {'regex':r'^https://simu.howbuy.com/manager/\d+?.html$','configs':config_simuManinfo},
             {'regex':'^https?:\/\/simu\.howbuy\.com\/[a-z1-9|-]+?\/[A-Z]{1,2}\d+?\/','configs':config_simuProdinfo},
             {'regex':r'^https://simu.howbuy.com/\w+?/$','configs':config_simuCominfo},
            ]
    for _ in flags:
        if re.search(_['regex'],url):
            return _['configs']
#表单选择
def changeData(url,*args):
    flags = [
             {'regex':r'https://simu.howbuy.com/mlboard.htm','data':postdata_Prod},
             {'regex':r'https://simu.howbuy.com/manager','data':company_data},
             {'regex':r'https://simu.howbuy.com/company','data':Manager_data},
            ]
    for _ in flags:
        if re.search(_['regex'],url):
            return _['data'](*args)
#修改页面结构
def replaceHtml(text,List):
    try:
        if hasattr(text,'replace'):
            pass
        else:
            raise AttributeError('value %s %s has not attribute replace'%(str(text),type(text)))
        for _ in List:
            text = text.replace(*_)
        return text
    except Exception as e:
        print(e)
#类修饰器
def getpostdata(func,*args):
    q = func(*args)
    return q