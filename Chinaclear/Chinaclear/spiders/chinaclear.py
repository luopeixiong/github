# -*- coding: utf-8 -*-
import scrapy
from myselector import Selector as S
from Help import *
from .ownerconfig import *
import datetime
  
#import mysele
class ChinaclearSpider(scrapy.Spider,other):
    handle_httpstatus_list = [404, 500]
    name = "chinaclear"
    allowed_domains = ["www.chinaclear.cn"]
    start_urls = ['http://www.chinaclear.cn/cms-rank/queryPledgeProportion?queryDate={date}&secCde=']
    custom_settings = {'DOWNLOAD_DELAY':1,
                       'CURRENT_REQUESTS':1}
    def start_requests(self):
        page = 1
        for url in self.start_urls:
            if url == 'http://www.chinaclear.cn/cms-rank/queryPledgeProportion?queryDate={date}&secCde=':
                dateformat = "%Y.%m.%d"
                today = datetime.datetime.now().strftime("%Y%m%d")
                datelist = S.datelist('20100101',today,dateformat)
                datelist.reverse()
                for date in datelist:
                    _url = url.format(date=date)
                    yield scrapy.Request(_url,
                                         meta = {'page':page,'date':date},
                                         headers= hdr(),
                                         priority=0)
                    
    def parse(self, response):
        if 'setTimeout' in response.text or response.status == 404:
            url = response.url.replace('%20%20%20','')
            print(url)
            request = response.request.replace(url=url,dont_filter=True)
            return request
        items = self.configParse(Configs,response,response)
        for item in items.__iter__():
            yield item
        
        page = response.meta['page']
        date = response.meta['date']
        if page==1:
            totalPage = int(re.search("\'pageNum\'\s*?,\s*?\'(\d+?)\'",response.text).group(1)) if re.search("\'pageNum\'\s*?,\s*?\'(\d+?)\'",response.text) else 1
        else:
            totalPage = response.meta['totalPage']
        
        if page<totalPage:
            page+=1
            url= 'http://www.chinaclear.cn/cms-rank/queryPledgeProportion?queryDate={date}&secCde=&page={page}'.format(page=page,date=date)
            yield scrapy.Request(url,
                                 meta = {'page':page,'date':date,'totalPage':totalPage},
                                 headers= hdr(),
                                 priority=1)
            
        