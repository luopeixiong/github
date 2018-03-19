# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 17:13:07 2017
sql注入测试
@author: luopx
"""
import requests as s
from selenium import webdriver


if __name__ == '__main__':
    
    
    
    #此处获取userID
    user = '11111@qq.com'
    
    
    psw = '22222'
    
    
    driver = webdriver.Chrome()
    driver.get('http://www.pedata.cn/auth_do/toregister')
    driver.find_element_by_xpath("//a[starts-with(@href,'/auth_do/m_toregister')]").click()
    driver.find_element_by_xpath("//input[@name='email']").send_keys(user)
    
    driver.find_element_by_xpath("//input[@name='password']").send_keys(psw)
    driver.find_element_by_xpath("//input[@name='pwd']").send_keys(psw)
    
    #此处保存图片到本地
    #此处解析yzm
    
    yzm = 'asac'
    
    driver.find_element_by_xpath("//input[@name='codeImageValue']").send_keys(yzm)
    driver.find_element_by_xpath("//input[@id='yzm']").click()
    
    #此处处理极验
    
    
    
    
    
    
    
    
    #url = 'http://pe.pedata.cn/ajaxLoginMember.action'
    #data = {'param.loginName':	'gzuivd60935@027168.com',
    #        'param.pwd':	'asd123456',
    #        'param.iscs'	:'true',
    #        'param.macaddress'	:'',
    #        'param.language'	:'zh_CN',
    #        'request_locale'	:'zh_CN'}
    #
    #res = s.post(url, data=data)
    #print(res.text)
    #viewurl = 'http://pe.pedata.cn/getDetailOrg.action?param.org_id=2971'
    #
    #cookies = res.cookies.get_dict()
    #print(cookies)
    #print(s.get(viewurl,cookies=cookies).text)