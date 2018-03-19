# -*- coding: utf-8 -*-
import scrapy

class CyzoneSpider(scrapy.Spider):
    name = "cyzone"
    allowed_domains = ["cyzone.cn"]
    start_urls = ['https://mobile.rongzi.cyzone.cn/?m=appv5&c=company&a=capitalCompanyList',
                  'https://mobile.rongzi.cyzone.cn/?m=appv5&c=capital&a=getCapitalList',
                  'https://mobile.rongzi.cyzone.cn/?m=appv456&c=project&a=ProLists']
    
    def start_requests(self):
        for url in self.start_urls:
            if url == 'https://mobile.rongzi.cyzone.cn/?m=appv456&c=project&a=ProLists':
                """创业公司"""
                data = {'uid':'787052',
                       'cat':'',
                       'city':'',
                       'series':'',
                       'page':'100'}
                headers = {'User-Agengt': '创业邦 4.8.5 rv:4372 (iPhone; iOS 10.3; zh_CN)'}
                yield scrapy.FormRequest(url,
                                         method='POST',
                                         formdata = data,
                                         headers = headers,
#                                         encoding = 'unicode_escape',
                                         callback = self.starts_companyParse)
            if url == 'https://mobile.rongzi.cyzone.cn/?m=appv5&c=capital&a=getCapitalList':
                """投资人"""
                data = {'page':'0',
                        'type':'2',
                        'cat':'',
                        'series':'',
                        'city':''
                        }
                headers = {'User-Agengt': '创业邦 4.8.5 rv:4372 (iPhone; iOS 10.3; zh_CN)'}
                yield scrapy.FormRequest(url,
                                         method='POST',
                                         formdata = data,
                                         headers = headers,
#                                         encoding = 'unicode_escape',
                                         callback = self.invilmentparse)
            if url == 'https://mobile.rongzi.cyzone.cn/?m=appv5&c=company&a=capitalCompanyList':
                """投资机构"""
                data = {'page':'0',
                        'cat':'',
                        'series':''
                        }
                headers = {'User-Agengt': '创业邦 4.8.5 rv:4372 (iPhone; iOS 10.3; zh_CN)'}
                yield scrapy.FormRequest(url,
                                         method='POST',
                                         formdata = data,
                                         headers = headers,
#                                         encoding = 'unicode_escape',
                                         callback = self.invilmentparse)
    def parse(self, response):
        
        pass
    
    def invilmentparse(self, response):
        response.body_as_unicode = 'unicode_escape'
        print(response.text.encode('latin-1').decode('unicode_escape'))
    def starts_companyParse(self, response):
        response.body_as_unicode = 'unicode_escape'
        print(response.text.encode('latin-1').decode('unicode_escape'))
