# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 12:47:36 2017

@author: luopx
"""

import requests
from user_agent import generate_user_agent
import time
import json
s = requests.Session()


url = "http://www.gsxt.gov.cn/SearchItemCaptcha?v=%s"%(int(time.time())*1000)

res = s.get(url,headers = {'User-Agent':generate_user_agent(),'Accept': 'application/json, text/javascript, */*; q=0.01'})
js = json.loads(res.text)
gt = js['gt']
challenge = js['challenge']
print(js)
#result = s.get("http://www.gsxt.gov.cn/corp-query-search-test.html?searchword=%E5%A5%BD%E7%A7%9F%E7%A7%91%E6%8A%80%E5%8F%91%E5%B1%95%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8")
#print(result.text)
#data = {
#        "tab"	:"ent_tab",
#        "token"	:"128166491",
#        "searchword"	:"111",
#        "geetest_challenge"	:"2a805c49be00d0c3924cff74745196c992",
#        "geetest_validate"	:"db3462b0a2b54c95335928b7484a7998",
#        "geetest_seccode"	:"db3462b0a2b54c95335928b7484a7998|jordan"}
#url1 = "http://www.gsxt.gov.cn/corp-query-search-1.html"
#resu = s.post(url1,data=data,headers = {'User-Agent':generate_user_agent(),'Accept': 'application/json, text/javascript, */*; q=0.01'})
#print(resu.text)