# /usr/bin/python3
# -*- coding:utf-8 -*-

import math
import requests
from user_agent import generate_user_agent
from scrapy import Selector
import os
import calendar as cal
import pymssql
s = requests.Session()
import time

class pedataCookieJar(object):
    def __init__(self):
        self.login_url = "http://pe.pedata.cn/ajaxLoginMember.action"
        self.path = "pedata_cookieJar.json"
#        self.user = "wanzh@hffss.com"
#        self.psw = "111111"
        self.user = "499722757@qq.com"
        self.psw = "8927968"
        self.headers = {"User-agent": generate_user_agent()}
    def getcookiesformpath(self):
        with open(self.path, "r") as f:
            read = f.readline()
            cookie_jar = eval(read)
        return cookie_jar

    def trycookie(self, cookies):
        res = self.getOrgListHtml(cookies)
        if "Login timeout" in res.text:
            return False
        elif "投资策略" in res.text:
            return True

    def getcookiesfromlogin(self):

        login_data = {"param.loginName": self.user,
                      "param.pwd": self.psw,
                      "param.iscs": "true",
                      "param.macaddress": "90-CD-B6-61-0E-61,48-4D-7E-A3-9D-AE,90-CD-B6-61-0E-62,00-50-56-C0-00-01,00-50-56-C0-00-08,52-CD-B6-61-0E-61",
                      "param.language": "zh_CN",
                      "request_locale": "zh_CN"}

        
        login_res = s.post(self.login_url, data=login_data, headers=self.headers)
        print(login_res.text)
        print(login_res.cookies.get_dict())
#        cookies = {'IS_CS_KEY': 'true', 'JSESSIONID': '90D0701C776A387CFE70EB8D826A6B86', 'USER_CLIENT_ID': '""', 'USER_LOGIN_ID': '764f969215fc4766a48c63aaef715a3b', 'USER_LOGIN_LANGUAGE': 'zh_CN', 'USER_LOGIN_NAME': '17600811823', 'USER_LOGIN_NAME_KEY': '764f969215fc4766a48c63aaef715a3b', 'request_locale': 'zh_CN'}
        cookies = login_res.cookies.get_dict()
        self.writecookie(cookies)
        return cookies

    def writecookie(self, cookie_jar):
        with open(self.path, "w+") as f:
            f.write(str(cookie_jar))
        return False

    def getOrgListHtml(self, cookies):
        headers = {"User-agent": generate_user_agent()}
        org_url_list = "http://pe.pedata.cn/getListOrg.action"
        data = {"param.quick": "",
                "param.orderBy": "desc",
                "param.orderByField": "history_invest_count",
                "param.search_type": "base",
                "param.showInfo": "true",
                "param.search_type_check": "",
                "param.org_name": "",
                "param.org_manage_capital_begin": "",
                "param.org_manage_capital_end": "",
                "param.orgBackground": "",
                "param.org_record": "",
                "param.org_setup_date_begin": "yyyy-mm-dd",
                "param.org_setup_date_end": "yyyy-mm-dd",
                "param.fund_goal_money_us_begin": "",
                "param.fund_goal_money_us_end": "",
                "param.fund_record": "",
                "param.fund_setup_date_begin": "yyyy-mm-dd",
                "param.fund_setup_date_end": "yyyy-mm-dd",
                "param.epValue__start": "",
                "param.epValue__end": "",
                "param.epSetupDate_begin": "yyyy-mm-dd",
                "param.epSetupDate_end": "yyyy-mm-dd",
                "param.invest_money_begin": "",
                "param.invest_money_end": "",
                "param.invest_stake_start": "",
                "param.invest_stake_end": "",
                "param.invest_enterprise_start": "",
                "param.invest_enterprise_end": "",
                "param.invest_date_begin": "yyyy-mm-dd",
                "param.invest_date_end": "yyyy-mm-dd",
                "param.column": ["0", "1", "2", "3", "4", "5", "6", "7", "13"],
                # page页面
                "param.currentPage": "1"
                }
        res = s.post(org_url_list, data=data, cookies=cookies, headers=self.headers)
        # print(res.text)
        return res
    @staticmethod  
    def getinfos(url, cookies):
        headers = {"User-agent": generate_user_agent()}
#        url = "http://pe.pedata.cn/getDetailOrg.action?param.org_id=3261"
        res = s.get(url, cookies=cookies, headers=headers)
        return res
    @staticmethod
    def getOrgList():
        host = "127.0.0.1"
        db = "Haifeng.FundRawData.DB"
        user = "sa"
        passwd = "8927968"
        conn = pymssql.connect(host = host,database=db,user = user,password=passwd,charset="utf8")
        cursor = conn.cursor()
        sql = "select org_id from dbo.Pedata_pedata_org_list"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        if result:
            result = [x[0] for x in result]
        return result
    @staticmethod
    def ymd(y, m, s=2):
        offset = math.ceil(28/s)
        FORMAT = "{0}-{1:0>2}-{2:0>2}"
        d = cal.monthrange(y, m)
        datedata = []
        for i in range(s):
            start = 1+offset*(i)
            if i< s-1:
                end = offset*(i+1)
            else:
                end = d[1]
            datedata.append((FORMAT.format(y, m, start), FORMAT.format(y, m, end)))
        return datedata
    def main(self):
        if os.path.exists(self.path):
            try:
                cookies = self.getcookiesformpath()
                time.sleep(2)
                if self.trycookie(cookies):
                    print("cookies 可用")
                    return cookies
                else:
                    return self.getcookiesfromlogin()
            except:
                cookies = self.getcookiesfromlogin()
                return cookies
        else:
            return self.getcookiesfromlogin()
            # if __name__ =="__main__":
            #     pass
            # cookies = self.getcookiesfromlogin()
            # res = getOrgListHtml(cookies)
            # print(res.text)
            # #urls xpaht("// a[contains( @ href, 'getDetailOrg.action?param.org_id=')] / @href")

            # url = "http://pe.pedata.cn/getDetailOrg.action?param.org_id=2441"
            # res = getinfos(url,cookies)
    @staticmethod
    def makedata_1(start,end,page):
        showlist = list(map(lambda x:str(x),range(0,32)))
        data = {
        "param.quick":"",
        "param.orderBy":"desc",
        "param.orderByField":"invest_date",
        "param.search_type":"base",
        "param.showInfo":"true",
        "param.search_type_check":"ownerCheck,conditionsUl,",
        "param.invest_money_begin":"",
        "param.invest_money_end":"",
        "param.invest_stake_start":"",
        "param.invest_stake_end":"",
        "param.invest_enterprise_start":"",
        "param.invest_enterprise_end":"",
        "param.invest_date_begin":start,
        "param.invest_date_end":end,
        "param.invest_date_base_lable_id":"自定义",
        "param.epValue__start":"",
        "param.epValue__end":"",
        "param.epSetupDate_begin":"yyyy-mm-dd",
        "param.epSetupDate_end":"yyyy-mm-dd",
        "param.isTargetIpo":"",
        "param.orgBackground":"",
        "param.orgRecord":"",
        "param.fund_record":"",
        "param.fund_setup_date_begin":"yyyy-mm-dd",
        "param.fund_setup_date_end":"yyyy-mm-dd",
        "param.column": showlist,
        "param.currentPage": str(page)
        }
        return data
if __name__ == "__main__":
    pass
#    a = pedataCookieJar()
#a.main()
#    print(pedataCookieJar.ymd(2016,5,1))
#    print("start Crawl")
#    result = pedataCookieJar.getOrgList()
    Cookies = pedataCookieJar()
    cookies = Cookies.main()
    print(cookies)
#    cookies = {'IS_CS_KEY': 'true', 'USER_CLIENT_ID': '""', 'USER_LOGIN_ID': '3AE28892-4B16-4E16-859B-BBF420E3322D', 'USER_LOGIN_LANGUAGE': 'zh_CN', 'USER_LOGIN_NAME': '499722757%40qq.com', 'USER_LOGIN_NAME_KEY': '499722757%40qq.com', 'request_locale': 'zh_CN'}
    url = "http://pe.pedata.cn/getDetailOrg.action?param.org_id=52053"
    time.sleep(5)
    res = Cookies.getinfos(url,cookies)
#    print(res.text)
    with open("f://last.html","w+",encoding="utf-8") as f:
        f.write(res.text)
    print(res.url)
#    url = "http://pe.pedata.cn/getListInvest.action"
#    time.sleep(2)
#    data = Cookies.makedata_1("2001-01-01","2001-01-31",1)
#    res = s.post(url,data=data,cookies=cookies)
#    time.sleep(2)
#    print(res)
#    print(res.text)