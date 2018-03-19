# -*- coding: utf-8 -*-
import scrapy
from user_agent import generate_user_agent
from .myselector import Selector as S
from AMAC_Product.items import AmacProductItem
class CfachinaSpider(scrapy.Spider):
    name = "cfachina"
    allowed_domains = ["cfachina.org"]
    start_urls = ['http://www.cfachina.org/cfainfo/organbaseinfoServlet']
    page = 1
    size = 20
    def madedata(self,page):
        data = {'currentPage':str(page),
                'pageSize':str(self.size),
                'all':'personinfo'}
        return data
    def start_requests(self):
        for url in self.start_urls:
            if url == 'http://www.cfachina.org/cfainfo/organbaseinfoServlet':
                data = self.madedata(self.page)
                headers = {'User-Agent':generate_user_agent()}
                yield scrapy.FormRequest(url,
                                         method='POST',
                                         formdata=data,
                                         headers = headers,
                                         callback=self.cdfQualificationListparse
                                         )
    def cdfQualificationListparse(self, response):
#        print(response.text)
#        with open("1.html","wb") as f:
#            f.write(response.body)
        if self.page == 1:
            self.cdfQualificationListTotalPages = int(response.xpath('//ul[@class="yema"]/li[last()]/span/text()').extract_first())
#            print(self.cdfQualificationListTotalPages)
        for info in response.xpath('//td[text()=" 机构编号 "]/parent::tr/following-sibling::tr'):
#            print(info)
            name = info.xpath('td[2]/a/text()').extract_first()
            organid = info.xpath('td[1]/text()').extract_first()
#            print(name,organid,)
            data = {'name':name,
                    'organid':organid,
                    'selectType':'personinfo'}
            headers = {'User-Agent':generate_user_agent()}
            yield scrapy.FormRequest('http://www.cfachina.org/cfainfo/organbaseinfoOneServlet',
                                     formdata = data,
                                     headers=headers,
                                     meta = {'page':1,'Totalpage':None,'data':data},
                                     callback = self.cdfQualificationinfoparse)
#            return False
        if self.page < self.cdfQualificationListTotalPages:
            self.page+=1
            nextdata = self.madedata(self.page)
            nextheaders = {'User-Agent':generate_user_agent()}
            nexturl = 'http://www.cfachina.org/cfainfo/organbaseinfoServlet'
            yield scrapy.FormRequest(nexturl,
                                     method='POST',
                                     formdata=nextdata,
                                     headers = nextheaders,
                                     callback=self.cdfQualificationListparse
                                     )
    def parse(self, response):
        pass
    
    def cdfQualificationinfoparse(self, response):
#        print(response.text)
        item = AmacProductItem()
        page = response.meta['page']
        Totalpage = response.meta['Totalpage']
        data = response.meta['data']
        if Totalpage:
            pass
        else:
            Totalpage = int(response.xpath('//ul[@class="yema"]/li[last()]/span/text()').extract_first())
        configs = [{'n':'姓名','En':'name','t':'xpath_first','v':'td[1]/text()','dt':''},
                   {'n':'性别','En':'Gender','t':'xpath_first','v':'td[2]/text()','dt':''},
                   {'n':'从业资格号','En':'QualificationNo','t':'xpath_first','v':'td[3]/text()','dt':''},
                   {'n':'投资咨询从业证书号','En':'inviderQualificationNo','t':'xpath_first','v':'td[4]/text()','dt':''},
                   {'n':'任职部门','En':'department','t':'xpath_first','v':'td[5]/text()','dt':''},
                   {'n':'职务','En':'position','t':'xpath_first','v':'td[6]/text()','dt':''},
                   {'n':'任现职时间','En':'Appointment_time','t':'xpath_first','v':'td[7]/text()','dt':''},
                   {'n':'公司名称','En':'org_name','t':'xpath_first','v':'//div[@class="gst_title"]/a[3]/text()','dt':''},
                   {'n':'公司id','En':'prg_id','t':'xpath_first','v':'//input[@name="organid"]/@value','dt':''},
                   ]
        for info in response.xpath('//tr[starts-with(@id,"tr_")]'):
            result = dict()
            for config in configs:
                result[config['En']] = S.select_content(info, config)
#            print(result)
            item['result'] = result
            item['keys'] = ['name','org_name']
            item['db'] = 'dbo.cfa_futures_practitionsers'
            yield item
        
        if page < Totalpage/20:
            page+=1
            data['currentPage'] = str(page)
            data['pageSize'] = '20'
            data['all'] ='undefined'
            nextheaders = {'User-Agent':generate_user_agent()}
            nexturl = 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet'
            yield scrapy.FormRequest(nexturl,
                                     method='POST',
                                     formdata=data,
                                     headers = nextheaders,
                                     meta = {'page':page,'Totalpage':Totalpage,'data':data},
                                     callback=self.cdfQualificationinfoparse
                                     )