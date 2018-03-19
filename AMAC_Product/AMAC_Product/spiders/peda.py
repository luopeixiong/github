# -*- coding: utf-8 -*-
import scrapy
from .myselector import Selector as S
class PedaSpider(scrapy.Spider):
    name = "peda"
    allowed_domains = ["pedaily.cn"]
    start_urls = ['http://zdb.pedaily.cn/inv/',
                  'http://zdb.pedaily.cn/ipo/']
    invpage = 1
    ipopage = 1
    def start_requests(self):
        for url in self.start_urls:
#            if url == 'http://zdb.pedaily.cn/inv/':
#                '''投资事件'''
#                yield scrapy.Request(url,
#                                     headers = S.headers(),
#                                     callback = self.invparse
#                                     )
            if url == 'http://zdb.pedaily.cn/ipo/':
                '''上市事件'''
                yield scrapy.Request(url,
                                     headers = S.headers(),
                                     callback = self.ipoparse
                                     )
    def invparse(self, response):
#        print(response.text)
        if self.invpage == 1:
            self.invTotal = int(response.xpath('//span[@class="total"]/text()').extract_first())
        configs = [{'n':'受资方','En':'Receiver_name','t':'xpath_first','v':'dl[1]/dt[@class="company"]/a/text()','dt':''},
                   {'n':'投资发生时间','En':'Investment_happen_date','t':'xpath_first','v':'div[1]/span[1]/text()','dt':''},
                   {'n':'受资方ID','En':'Receiver_ID','t':'xpath_first','v':'dl[1]/dt[@class="company"]/a/@href','dt':''},
                   {'n':'所属行业','En':'trade','t':'xpath_first','v':'dl[1]/dt[@class="industry"]/a/text()','dt':''},
                   {'n':'投资轮次','En':'Investment_round','t':'xpath_first','v':'dl[1]/dt[@class="money"]/span[@class="r"]/text()','dt':''},
                   {'n':'投资币种','En':'Investment_currency','t':'xpath_first','v':'dl[1]/dt[@class="money"]/span[@class="d"]/text()','dt':''},
                   {'n':'投资金额','En':'Investment_money','t':'xpath_first','v':'dl[1]/dt[@class="money"]/span[@class="m"]/text()','dt':''},
                   {'n':'投资方','En':'InvestorsName','t':'xpath_split','v':'dl[1]/dt[@class="group"]/a/text()','dt':''},
                   {'n':'投资方ID','En':'InvestorsID','t':'xpath_split','v':'dl[1]/dt[@class="group"]/a/@href','dt':''},
                   {'n':'事件ID','En':'invID','t':'xpath_first','v':'dl[1]/dt[@class="view"]/a/@href','dt':''}
                   ]
        for info in response.xpath('//li[@class="head"]/following-sibling::li'):
            result = dict()
            for config in configs:
                result[config['En']] = S.select_content(info, config)  
            print(result)
            
        if self.invpage<self.invTotal/20:
            self.invpage+=1
            url = 'http://zdb.pedaily.cn/inv/p{page}'.format(page=self.invpage)
            yield scrapy.Request(url,
                                 headers = S.headers(),
                                 callback = self.invparse
                                 )
    def ipoparse(self, response):
        if self.ipopage == 1:
            self.ipoTotal = int(response.xpath('//span[@class="total"]/text()').extract_first())
        configs = [{'n':'上市公司','En':'Listed_company_name','t':'xpath_first','v':'dl[1]/dt[@class="company"]/a/text()','dt':''},
                   {'n':'上市公司ID','En':'Listed_company_ID','t':'xpath_first','v':'dl[1]/dt[@class="company"]/a/@href','dt':''},
                   {'n':'上市发生时间','En':'Listed_happen_date','t':'xpath_first','v':'div[1]/span[1]/text()','dt':''},
                   {'n':'所属行业','En':'trade','t':'xpath_first','v':'dl[1]/dt[@class="industry"]/a/text()','dt':''},
                   {'n':'募集金额','En':'Raised_round','t':'xpath_join','v':'dl[1]/dt[@class="money"]/span/text()','dt':''},
                   {'n':'交易所','En':'exchange','t':'xpath_first','v':'dl[1]/dt[@class="place"]/a/text()','dt':''},
                   {'n':'上市事件ID','En':'Listed_Event_ID','t':'xpath_first','v':'dl[1]/dt[@class="view"]/a/@href','dt':''}
                   ]
        for info in response.xpath('//li[@class="head"]/following-sibling::li'):
            result = dict()
            for config in configs:
                result[config['En']] = S.select_content(info, config)  
            print(result)   
            
        if self.ipopage<self.ipoTotal/20:
            self.ipopage+=1
            url = 'http://zdb.pedaily.cn/ipo/p{page}'.format(page=self.ipopage)
            yield scrapy.Request(url,
                                 headers = S.headers(),
                                 callback = self.ipoparse
                                 )
    def parse(self, response):
        pass
        