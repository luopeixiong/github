
exmple = [{'list':{'v':'','t':'','keys':[],'db':''
                   },
           'data':[
                   {'n':'','En':'','t':'','v':'','dt':''},
                   ]
           }
         ]
import re

companyConfigs = [{'list':{'v':'','t':'','keys':[],'db':'','check':'FullName'
                   },
           'data':[
                   {'n':'全称','En':'FullName','t':'xpath_first','v':'//h1/text()','dt':''},
                   {'n':'简称','En':'ShortName','t':'xpath_first','v':'//h1/em/text()','dt':''},
                   {'n':'英文名','En':'Ename','t':'xpath_first','v':'//h2/text()','dt':''},
                   {'n':'资本类型','En':'CapitalType','t':'xpath_first','v':'//li[span[contains(text(),"资本类型")]]/text()','dt':''},
                   {'n':'机构性质','En':'OrgNature','t':'xpath_first','v':'//li[span[contains(text(),"机构性质")]]/text()','dt':''},
                   {'n':'注册地点','En':'RegAddress','t':'xpath_first','v':'//li[span[contains(text(),"注册地点")]]/text()','dt':''},
                   {'n':'成立时间','En':'SetupDate','t':'xpath_first','v':'//li[span[contains(text(),"成立时间")]]/text()','dt':''},
                   {'n':'机构总部','En':'OrgHeader','t':'xpath_first','v':'//li[span[contains(text(),"机构总部")]]/text()','dt':''},
                   {'n':'官方网站','En':'WebSite','t':'xpath_first','v':'//li[span[contains(text(),"官方网站")]]/a/text()','dt':''},
                   {'n':'投资阶段','En':'jeiduan','t':'xpath_first','v':'//li[span[contains(text(),"投资阶段")]]/text()','dt':''},
                   {'n':'简介','En':'inv','t':'xpath_join','v':'//div[h3[span[text()="简介"]]]//p[em]//text()','dt':''},
                   {'n':'联系电话','En':'TelPhoneNumber','t':'xpath_first','v':'//p[span[contains(text(),"联系电话")]]/text()','dt':''},
                   {'n':'传 真','En':'Fax','t':'xpath_first','v':'//p[span[contains(text(),"传 真")]]/text()','dt':''},
                   {'n':'地 址','En':'Address','t':'xpath_first','v':'//p[span[contains(text(),"地 址")]]/text()','dt':''},
                   {'n':'邮 编','En':'ZipCode','t':'xpath_first','v':'//p[span[contains(text(),"邮 编")]]/text()','dt':''},
                   {'n':'WebCompanyID','En':'WebCompanyID','t':'url_re','v':'show(\d+)\/','dt':''},
                   ]
           }
         ]
invConfigs = [{'list':{'v':'','t':'','keys':[],'db':'','check':'invTitle'
                   },
           'data':[
                   {'n':'事件标题','En':'invTitle','t':'xpath_first','v':'//h1/text()','dt':''},
                   {'n':'融  资  方','En':'1','t':'','v':'//li[span[re:test(text(),"融.*?资.*?方")]]/a/text()','dt':''},
                   {'n':'融  资  方ID','En':'2','t':'regex1','v':'融[^>]*?资[^>]*?方.*?<a\s*?href=\".*?show(\d+)\/','dt':''},
                   {'n':'投  资  方','En':'3','t':'xpath_join|','v':'//li[span[re:test(text(),"投.*?资.*?方")]]/a/text()','dt':''},
                   {'n':'投  资  方ID','En':'4','t':'re_join|','v':'(?=投[^>]*?资[^>]*?方).*?<a\s*?href=\".*?show(\d+)\/','dt':''},
                   {'n':'金　　额','En':'5','t':'xpath_join ','v':'//li[span[re:test(text(),"金.*?额")]]/span[@class]/text()','dt':''},
                   {'n':'轮　　次','En':'6','t':'xpath_first','v':'//li[span[re:test(text(),"轮.*?次")]]/span[@class]/text()','dt':''},
                   {'n':'融资时间','En':'7','t':'xpath_first','v':'//li[span[re:test(text(),"融资时间")]]/text()','dt':''},
                   {'n':'所属行业','En':'8','t':'xpath_first','v':'//li[span[re:test(text(),"所属行业")]]/a/text()','dt':''},
                   {'n':'invID','En':'invID','t':'url_re','v':'show(\d+)\/','dt':''},
                   ]
           }
         ]
ipoConfigs = [{'list':{'v':'','t':'','keys':[],'db':'','check':'ComFullName'
                   },
           'data':[
                   {'n':'公司全称','En':'ComFullName','t':'xpath_first','v':'//*[span[contains(text(),"公司名称")]]/a/text()','dt':''},
                   {'n':'公司简称','En':'1','t':'xpath_first','v':'//h1/text()','dt':''},
                   {'n':'公司id','En':'2','t':'regex1','v':'公司名称：.*?show(\d+)\/','dt':''},
                   {'n':'IPO事件id','En':'3','t':'url_re','v':'show(\d+)\/','dt':''},
                   {'n':'所属行业','En':'4','t':'xpath_join/','v':'//*[span[contains(text(),"所属行业")]]/a/text()','dt':''},
                   {'n':'投  资  方','En':'5','t':'xpath_first','v':'//*[span[contains(text(),"投  资  方")]]/text()','dt':''},
                   {'n':'上市时间','En':'6','t':'xpath_first','v':'//*[span[contains(text(),"上市时间")]]/text()','dt':''},
                   {'n':'发  行  价','En':'7','t':'xpath_first','v':'//*[span[contains(text(),"发  行  价")]]/text()','dt':''},
                   {'n':'上市地点','En':'8','t':'xpath_first','v':'//*[span[contains(text(),"上市地点")]]/a/text()','dt':''},
                   {'n':'发  行  量','En':'9','t':'xpath_first','v':'//*[span[contains(text(),"发  行  量")]]/text()','dt':''},
                   {'n':'股票代码','En':'10','t':'xpath_first','v':'//*[span[contains(text(),"股票代码")]]/text()','dt':''},
                   {'n':'是否VC/PE支持','En':'11','t':'xpath_first','v':'//*[span[contains(text(),"是否VC/PE支持：")]]/text()','dt':''},
                   
                   ]
           }
         ]
maConfigs = [{'list':{'v':'','t':'','keys':[],'db':'','check':'2'
                   },
           'data':[
                   {'n':'并购事件id','En':'1','t':'url_re','v':'show(\d+)','dt':''},
                   {'n':'并购事件标题','En':'2','t':'xpath_first','v':'//h1/text()','dt':''},
                   {'n':'并  购  方','En':'3','t':'xpath_first','v':'//*[span[contains(text(),"并  购  方")]]/a/text()','dt':''},
                   {'n':'并购方id','En':'4','t':'regex1','v':'>并  购  方.*?show(\d+)','dt':''},
                   {'n':'被并购方','En':'5','t':'xpath_first','v':'//*[span[contains(text(),"被并购方")]]/a/text()','dt':''},
                   {'n':'被并购方id','En':'6','t':'regex1','v':'被并购方.*?show(\d+)','dt':''},
                   {'n':'并购状态','En':'87','t':'xpath_first','v':'//*[span[contains(text(),"并购状态")]]/text()','dt':''},
                   {'n':'所属行业','En':'9','t':'xpath_join/','v':'//*[span[contains(text(),"所属行业")]]/a/text()','dt':''},
                   {'n':'涉及股权','En':'0','t':'xpath_first','v':'//*[span[contains(text(),"涉及股权")]]/text()','dt':''},
                   {'n':'并购开始时间','En':'10','t':'xpath_first','v':'//*[span[contains(text(),"并购开始时间")]]/text()','dt':''},
                   {'n':'并购结束时间','En':'11','t':'xpath_first','v':'//*[span[contains(text(),"并购结束时间")]]/text()','dt':''},
                   {'n':'是否VC/PE支持','En':'12','t':'xpath_first','v':'//*[span[contains(text(),"是否VC/PE支持")]]/text()','dt':''},
                   {'n':'简介','En':'13','t':'xpath_join','v':'//div[h3[span[contains(text(),"简介")]]]//p/text()','dt':''},
                   
                   ]
           }
         ]
peConfigs = [{'list':{'v':'','t':'','keys':[],'db':'','check':'title'
                   },
           'data':[
                   {'n':'peid','En':'peid','t':'url_re','v':'show(\d+)','dt':''},
                   {'n':'title','En':'title','t':'xpath_first','v':'//h1/text()','dt':''},
                   {'n':'基金名称','En':'fundname','t':'xpath_first','v':'//li[span[contains(text(),"基金名称")]]/text()','dt':''},
                   {'n':'币 种','En':'currency','t':'xpath_first','v':'//li[span[contains(text(),"币 种")]]/text()','dt':''},
                   {'n':'成立时间','En':'setupdate','t':'xpath_first','v':'//li[span[contains(text(),"成立时间")]]/text()','dt':''},
                   {'n':'募集状态','En':'1','t':'xpath_first','v':'//li[span[contains(text(),"募集状态")]]/text()','dt':''},
                   {'n':'管理机构','En':'2','t':'xpath_first','v':'//li[span[contains(text(),"管理机构")]]/a/text()','dt':''},
                   {'n':'管理机构ID','En':'22','t':'regex1','v':'管理机构.*?company\/(\d+)\/','dt':''},
                   {'n':'目标规模','En':'3','t':'xpath_first','v':'//li[span[contains(text(),"目标规模")]]/text()','dt':''},
                   {'n':'资本类型','En':'4','t':'xpath_first','v':'//li[span[contains(text(),"资本类型")]]/text()','dt':''},
                   {'n':'募集金额','En':'5','t':'xpath_first','v':'//li[span[contains(text(),"募集金额")]]/text()','dt':''},
                   {'n':'简介','En':'6','t':'xpath_join','v':'//div[h3[span[contains(text(),"简介")]]]//p/text()','dt':''},
                   ]
           }
         ]
peopleConfigs = [{'list':{'v':'','t':'','keys':[],'db':'','check':''
                   },
           'data':[
                   {'n':'','En':'','t':'','v':'','dt':''},
                   ]
           }
         ]
enterpriseConfigs = [{'list':{'v':'','t':'','keys':[],'db':'','check':''
                   },
           'data':[
                   {'n':'','En':'','t':'','v':'','dt':''},
                   ]
           }
         ]
urlconfigs = (('http:\/\/zdb\.pedaily\.cn\/people\/index\.shtml-p\d+\/',{'t':'xpath_list','v':'//div[@class="txt"]/h3/a/@href'}),
              ('http:\/\/zdb\.pedaily\.cn\/enterprise\/p\d+\/',{'t':'xpath_list','v':'//div[@class="txt"]/h3/a/@href'}),
              ('http:\/\/zdb\.pedaily\.cn\/company\/all-p\d+\/',{'t':'xpath_list','v':'//div[@class="txt"]/h3/a/@href'}),
              ('http:\/\/zdb\.pedaily\.cn\/pe\/p\d+\/',{'t':'xpath_list','v':'//*[@class="view"]/a/@href'}),
              ('http:\/\/zdb\.pedaily\.cn\/ma\/p\d+\/',{'t':'xpath_list','v':'//*[@class="view"]/a/@href'}),
              ('http:\/\/zdb\.pedaily\.cn\/ipo\/p\d+\/',{'t':'xpath_list','v':'//*[@class="view"]/a/@href'}),
              ('http:\/\/zdb\.pedaily\.cn\/inv\/p\d+\/',{'t':'xpath_list','v':'//*[@class="view"]/a/@href'}),
              )
pageConfigs = (('http:\/\/zdb\.pedaily\.cn\/people\/index\.shtml-p\d+\/',{'t':'xpath_list','v':'//*[@class="next" and contains(text(),"下一页")]/@href'}),
                  ('http:\/\/zdb\.pedaily\.cn\/enterprise\/p\d+\/',{'t':'xpath_list','v':'//*[@class="next" and contains(text(),"下一页")]/@href'}),
                  ('http:\/\/zdb\.pedaily\.cn\/company\/all-p\d+\/',{'t':'xpath_list','v':'//*[@class="next" and contains(text(),"下一页")]/@href'}),
                  ('http:\/\/zdb\.pedaily\.cn\/pe\/p\d+\/',{'t':'xpath_list','v':'//*[@class="next" and contains(text(),"下一页")]/@href'}),
                  ('http:\/\/zdb\.pedaily\.cn\/ma\/p\d+\/',{'t':'xpath_list','v':'//*[@class="next" and contains(text(),"下一页")]/@href'}),
                  ('http:\/\/zdb\.pedaily\.cn\/ipo\/p\d+\/',{'t':'xpath_list','v':'//*[@class="next" and contains(text(),"下一页")]/@href'}),
                  ('http:\/\/zdb\.pedaily\.cn\/inv\/p\d+\/',{'t':'xpath_list','v':'//*[@class="next" and contains(text(),"下一页")]/@href'}),
                  )
contentsConfigs = (('http:\/\/zdb\.pedaily\.cn\/company\/show\w+\/',companyConfigs),
                   ('http:\/\/zdb\.pedaily\.cn\/inv\/show\w+\/',invConfigs),
                   ('http:\/\/zdb\.pedaily\.cn\/pe\/show\d+\/',peConfigs),
                   ('http:\/\/zdb\.pedaily\.cn\/ma\/show\d+\/',maConfigs),
                   ('http:\/\/zdb\.pedaily\.cn\/ipo\/show\d+\/',ipoConfigs),
                   ('http:\/\/zdb\.pedaily\.cn\/people\/show\d+\/',peopleConfigs),
                   ('http:\/\/zdb\.pedaily\.cn\/enterprise\/show\d+\/',enterpriseConfigs),
                  )
def choice(url,List):
    for x,y in List:
        if re.compile(x).match(url):return y

configs = ('regexg','')