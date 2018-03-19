# -*- coding: utf-8 -*-
import scrapy
import random
import urllib.parse
import json
from user_agent import generate_user_agent
from .myselector import Selector as S
from scrapy import Selector as S1
"""
name : 基金业协会基金管理人spider 
v : beta/0.1

"""
class AmacManagerSpider(scrapy.Spider):
    name = "amac_manager"
    allowed_domains = ["amac.org.cn"]
    start_urls = ['http://gs.amac.org.cn/amac-infodisc/api/pof/manager']
    rand = "{:1<18}".format(str(random.random()))
    page = 0
    size = 20
    def madeurl(self, page):
        data = {"rand":self.rand,
                "page":str(page),
                "size":str(self.size)}
        data = urllib.parse.urlencode(data)
        url = 'http://gs.amac.org.cn/amac-infodisc/api/pof/manager?'+data
        return url
    def start_requests(self):
        for url in self.start_urls:
            if url == 'http://gs.amac.org.cn/amac-infodisc/api/pof/manager':
                headers = {'User-Agent':generate_user_agent(),
                           'Content-Type':'application/json'}
                url = self.madeurl(self.page)
                yield scrapy.Request(url,
                                     headers = headers,
                                     method = 'POST',
                                     body = json.dumps({}),
                                     callback=self.managerListpase)
    def managerListpase(self, response):
        js = json.loads(response.text)
        if self.page == 0:
            self.managerTotalPages = js['totalPages']
        for _json in js['content']:
            headers = {'User-Agent':generate_user_agent()}
            managerID = _json['id']
            url = 'http://gs.amac.org.cn/amac-infodisc/res/pof/manager/{managerID}.html'.format(managerID=managerID)
            yield scrapy.Request(url,
                                 method = 'GET',
                                 headers = headers,
                                 callback = self.managerparse)
        if self.page<self.managerTotalPages:
            self.page+=1
            headers = {'User-Agent':generate_user_agent(),
                       'Content-Type':'application/json'}
            url = self.madeurl(self.page)
            print(url)
            yield scrapy.Request(url,
                                 headers = headers,
                                 method = 'POST',
                                 body = json.dumps({}),
                                 callback=self.managerListpase)
    def managerparse(self, response):
        response_invaild = S1(text=S.replace_invalid_html_char(response.text))
        configs = [{'n':'基金管理人全称(中文):','En':'fund_manager_full_name','t':'xpath_first','v':'//td[text()="基金管理人全称(中文):" and @class="td-title"]/following-sibling::td[1]/div[1]/text()','dt':''},
                   {'n':'基金管理人全称(英文):','En':'fund_manager_full_Ename','t':'xpath_first','v':'//td[text()="基金管理人全称(英文):" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'登记编号:','En':'record_No','t':'xpath_first','v':'//td[text()="登记编号:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'组织机构代码:','En':'org_code','t':'xpath_first','v':'//td[text()="组织机构代码:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'登记时间:','En':'register_date','t':'xpath_first','v':'//td[text()="登记时间:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'成立时间:','En':'setup_time','t':'xpath_first','v':'//td[text()="成立时间:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'注册地址:','En':'register_address','t':'xpath_first','v':'//td[text()="注册地址:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'办公地址:','En':'work_address','t':'xpath_first','v':'//td[text()="办公地址:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'注册资本(万元)(人民币):','En':'registered_capital','t':'xpath_first','v':'//td[text()="注册资本(万元)(人民币):" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'实缴资本(万元)(人民币):	','En':'Paidin_capital','t':'xpath_first','v':'//td[text()="实缴资本(万元)(人民币):" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'企业性质:	','En':'Enterprise_nature','t':'xpath_first','v':'//td[text()="企业性质:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'注册资本实缴比例:','En':'registered_rateof__Paidin','t':'xpath_first','v':'//td[text()="注册资本实缴比例:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'机构类型:	','En':'org_type','t':'xpath_first','v':'//td[text()="机构类型:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'业务类型:','En':'Business_type','t':'xpath_first','v':'//td[text()="业务类型:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'员工人数:','En':'emp_nums','t':'xpath_first','v':'//td[text()="员工人数:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'机构网址:','En':'org_website','t':'xpath_first','v':'//td[text()="机构网址:" and @class="td-title"]/following-sibling::td[1]/a/text()','dt':''},
                   {'n':'是否为会员:','En':'is_member','t':'xpath_first','v':'//td[text()="是否为会员:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'当前会员类型:','En':'member_type','t':'xpath_first','v':'//td[text()="当前会员类型:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'入会时间:','En':'Membership_date','t':'xpath_first','v':'//td[text()="入会时间:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'法律意见书状态:','En':'legal_advice_status','t':'xpath_first','v':'//td[text()="法律意见书状态:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'法定代表人/执行事务合伙人(委派代表)姓名:','En':'legal_person','t':'xpath_first','v':'//td[text()="法定代表人/执行事务合伙人(委派代表)姓名:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'是否有从业资格:','En':'LP_Qualification','t':'xpath_first','v':'//td[text()="是否有从业资格:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'资格取得方式:','En':'Qualification_getmethod','t':'xpath_first','v':'//td[text()="资格取得方式:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'机构信息最后更新时间:','En':'orginfo_updatetime','t':'xpath_first','v':'//td[text()="机构信息最后更新时间:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'特别提示信息:','En':'specialInfos','t':'xpath_first','v':'//td[text()="特别提示信息:" and @class="td-title"]/following-sibling::td[1]/text()','dt':''},
                   {'n':'机构诚信信息:','En':'org_Credit_info','t':'xpath_first','v':'//td[text()="机构诚信信息:" and @class="td-title"]/following-sibling::td[1]/table/text()','dt':''}
                   ]
        result = dict()
        for config in configs:
            result[config['En']] = S.select_content(response_invaild, config)
            if result[config['En']]:
                result[config['En']] = S.replace_all(result[config['En']])
        if result['fund_manager_full_name']:
            print(result)
        else:
            print("try again")
            headers = {'User-Agent':generate_user_agent()}
            yield scrapy.Request(response.url,
                                 method = "GET",
#                                 meta = {'result':result},
                                 headers = headers,
                                 dont_filter=True,
                                 callback = self.managerparse)
            return False
    def parse(self, response):
        pass
