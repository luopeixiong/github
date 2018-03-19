# -*- coding: utf-8 -*-
import scrapy
from user_agent import generate_user_agent as ua
import re
import random


RANGE = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
         11, 12, 13, 14, 15, 16, 17, 18, 20,
         21, 24, 25, 27, 28, 30, 32, 35, 36,
         40, 42, 45, 48, 49, 54, 56, 63, 64,
         72, 81}

def trytime_(response):
    if response.meta.get('maxtrys'):
        response.meta['maxtrys'] += 1
    else:
        response.meta['maxtrys'] = 1
def gettrytime(response,maxtry=10):
    trytime_(response)
    if response.meta['maxtrys']<maxtry:
        return True
    
def checkTimeError(response,maxtry=3):
    flag = gettrytime(response,maxtry)
    if flag and 'setTimeout' in response.text:
        request = response.request.replace(dont_filter = True)
        return request 

class GsxtcxSpider(scrapy.Spider):
    name = "gsxtcx"
#    allowed_domains = ["gsxt.gov.cn"]
    start_urls = ['http://qyxy.baic.gov.cn/']
    custom_settings = {'DOWNLOADER_MIDDLEWARES': {
                        'gsxt.middlewares.RotateUserAgentMiddleware':401,
                        'gsxt.middlewares.ProxyMiddleware':700,
                        },
                        'CONCURRENT_REQUESTS' :16,
                        'DOWNLOAD_DELAY':1,
                        'DEPTH_PRIORITY' : 1,
                        }
    def start_requests(self):
        for i,url in enumerate(self.start_urls):
            yield scrapy.Request('http://qyxy.baic.gov.cn/',
                                 headers=self.bash_headers,
                                 callback=self.parse,
                                 dont_filter=True,
                                 meta={'cookiejar': i},
                                 )
    
    def parse(self, response):
        request = checkTimeError(response)
        if request:
            yield request
            return None
        url = re.compile('href\s*?=\s*?\"(.*?)\"').search(response.text).group(1)
        yield scrapy.Request(url,
                             headers=self.bash_headers,
                             callback=self.getyzm_parse,
                             meta = {'cookiejar': response.meta['cookiejar']})
    
    
    def getyzm_parse(self, response):
        request = checkTimeError(response)
        if request:
            yield request
            return None
        print(response.text)
        credit_ticket = re.search('credit_ticket\s*?=\s*?\"(.*?)\";',response.text).group(1)
        currentTimeMillis = re.search('currentTimeMillis\"\s*?value=\"(.*)\"',response.text).group(1)
        CodeUrl = 'http://qyxy.baic.gov.cn/CheckCodeYunSuan?currentTimeMillis=%s&r=%s'%(currentTimeMillis,random.random())
        yield scrapy.Request(CodeUrl,
                             headers=self.bash_headers,
                             callback=self.pass_parse,
                             meta = {'cookiejar': response.meta['cookiejar'],
                                     'currentTimeMillis':currentTimeMillis,
                                     'credit_ticket':credit_ticket,
                                     'code':0})
    
    def pass_parse(self, response):
        request = checkTimeError(response)
        if request:
            yield request
            return None
        code = response.meta['code']
        currentTimeMillis = response.meta['currentTimeMillis']
        credit_ticket = response.meta['credit_ticket']
        url = 'http://qyxy.baic.gov.cn/login/loginAction!checkCode.dhtml?check_code={2}&currentTimeMillis={0}&random={1:0<5}'.format(currentTimeMillis,int(random.random()*100000),code)
        yield scrapy.Request(url,headers=self.bash_headers,
                             callback=self.check_code_parse,
                             meta = {'cookiejar': response.meta['cookiejar'],
                                     'currentTimeMillis':currentTimeMillis,
                                     'credit_ticket':credit_ticket,
                                     'code':code})
    
    def check_code_parse(self, response):
        request = checkTimeError(response)
        if request:
            yield request
            return None
        code = response.meta['code']
        currentTimeMillis = response.meta['currentTimeMillis']
        credit_ticket = response.meta['credit_ticket']
        if 'true' in response.meta:
            print(response.text)
        else:
            code += 1
            return scrapy.Request(response.url,headers=self.bash_headers,
                             callback=self.check_code_parse,
                             meta = {'cookiejar': response.meta['cookiejar'],
                                     'currentTimeMillis':currentTimeMillis,
                                     'credit_ticket':credit_ticket,
                                     'code':code})
    @property
    def bash_headers(self):
        headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'Accept-Encoding':'gzip, deflate',
                   'Accept-Language':'zh-CN,zh;q=0.8',
                   'Connection':'keep-alive',
                   'Host':'qyxy.baic.gov.cn',
                   'Upgrade-Insecure-Requests':'1',
                   'User-Agent':ua(os=('win',))}
        return headers


#if __name__ == '__main__':
#    a = GsxtcxSpider()
#    print(a.bash_headers)