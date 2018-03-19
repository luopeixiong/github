# -*- coding: utf-8 -*-
import scrapy
from user_agent import generate_user_agent as ua
import re
from .myselector import Selector as S
class HexunSpider(scrapy.Spider):
    name = "hexun"
    allowed_domains = ["hexun.com"]
    start_urls = ['http://data.trust.hexun.com/list1.shtml',
                  'http://data.trust.hexun.com/list2.shtml',
                  'http://data.trust.hexun.com/list3.shtml',
                  'http://data.trust.hexun.com/list4.shtml',
                  'http://jingzhi.funds.hexun.com/newpj/allpj.aspx',
                  'http://data.trust.hexun.com/companylist.shtml',
                  'http://stockdata.stock.hexun.com/rzrq/broker.shtml',
                  'http://data.bank.hexun.com/lccp/AllLccp.aspx?col=fld_issenddate&tag=desc&orderMarks=&page={page}'
                  
                  ]
    def start_requests(self):
        for url in self.start_urls:
            if url in ['http://data.trust.hexun.com/list1.shtml',
                  'http://data.trust.hexun.com/list2.shtml',
                  'http://data.trust.hexun.com/list3.shtml',
                  'http://data.trust.hexun.com/list4.shtml',]:
                yield scrapy.Request(url,
                                     meta={'page':1,'baseUrl':url},
                                     headers = {'User-Agent':ua(os=('linux','win','mac'))},
                                     callback=self.trustListparse)
            if url in ['http://jingzhi.funds.hexun.com/newpj/allpj.aspx']:
                yield scrapy.Request(url,
                                     headers = {'User-Agent':ua(os=('linux','win','mac'))},
                                     callback=self.gradeListparse)
            if url in ['http://data.trust.hexun.com/companylist.shtml']:
                yield scrapy.Request(url,
                                     headers = {'User-Agent':ua(os=('linux','win','mac'))},
                                     callback=self.trustConpanyListparse)
            if url in ['http://stockdata.stock.hexun.com/rzrq/broker.shtml']:
                yield scrapy.Request(url,
                                     headers = {'User-Agent':ua(os=('linux','win','mac'))},
                                     callback=self.rzrqConpanyListparse)
            if url in ['http://data.bank.hexun.com/lccp/AllLccp.aspx?col=fld_issenddate&tag=desc&orderMarks=&page={page}']:
                yield scrapy.Request(url,
                                     headers = {'User-Agent':ua(os=('linux','win','mac'))},
                                     callback=self.BankProListparse)
    def trustListparse(self, response):
        baseUrl = response.meta['baseUrl']
        page = response.meta['page']
        if not response.meta.get('TotalPage'):
            TotalPage = int(response.xpath('//a[text()="末页"]/@href').extract_first().split('=')[-1])
        else:
            TotalPage = response.meta['TotalPage']
        urls = response.xpath('//a[re:test(@href,"\/\d+\.shtml")]/@href').extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url,
                                 headers = {'User-Agent':ua(os=('linux','win','mac'))},
                                 callback = self.trustParse
                                 )
        if page<TotalPage:
            page+=1
            NextUrl = baseUrl +'?&index=0&order=1&page={page}'.format(page=page)
            yield scrapy.Request(NextUrl,
                                 meta={'page':page,'TotalPage':TotalPage,'baseUrl':baseUrl},
                                 headers = {'User-Agent':ua(os=('linux','win','mac'))},
                                 callback=self.trustListparse)
    def trustParse(self, response):
        '''和讯信托'''
        
        configs = {'list':{'v':'','keys':'','db':'','t':'xpath'},
                   'data':[
                           {'n':'发行机构','En':'','v':'//td[contains(text(),"发行机构")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'项目经理','En':'','v':'//td[contains(text(),"项目经理")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'产品类型','En':'','v':'//td[contains(text(),"产品类型")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'产品状态','En':'','v':'//td[contains(text(),"产品状态")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'理财币种','En':'','v':'//td[contains(text(),"理财币种")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'投资管理类型','En':'','v':'//td[contains(text(),"投资管理类型")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'发行时间','En':'','v':'//td[contains(text(),"发行时间")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'发售对象','En':'','v':'//td[contains(text(),"发售对象")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'发行规模','En':'','v':'//td[contains(text(),"发行规模")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'投资门槛','En':'','v':'//td[contains(text(),"投资门槛")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'产品期限','En':'','v':'//td[contains(text(),"产品期限")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'期限类型','En':'','v':'//td[contains(text(),"期限类型")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'预期年收益率','En':'','v':'//td[contains(text(),"预期年收益率")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'实际年收益率','En':'','v':'//td[contains(text(),"实际年收益率")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'投资方式','En':'','v':'//td[contains(text(),"投资方式")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'资金投向','En':'','v':'//td[contains(text(),"资金投向")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'资金托管费率','En':'','v':'//td[contains(text(),"资金托管费率")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'销售手续费率','En':'','v':'//td[contains(text(),"销售手续费率")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'成立日期','En':'','v':'//td[contains(text(),"成立日期")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'成立规模','En':'','v':'//td[contains(text(),"成立规模")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'收益类型','En':'','v':'//td[contains(text(),"收益类型")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'是否保本','En':'','v':'//td[contains(text(),"是否保本")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'合作机构名称','En':'','v':'//td[contains(text(),"合作机构名称")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'合作类型','En':'','v':'//td[contains(text(),"合作类型")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'到期日期','En':'','v':'//td[contains(text(),"到期日期")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'发行地','En':'','v':'//td[contains(text(),"发行地")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'到期日期','En':'','v':'//td[contains(text(),"到期日期")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'发行地','En':'','v':'//td[contains(text(),"发行地")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'资金运用情况','En':'','v':'//td[contains(text(),"资金运用情况")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'信用增级情况','En':'','v':'//td[contains(text(),"信用增级情况")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'其他相关信息','En':'','v':'//td[contains(text(),"其他相关信息")]/following-sibling::td[1]/text()','t':'xpath_first','dt':''},
                           {'n':'信托产品','En':'','v':'//caption/text()','t':'xpath_first','dt':''},
                          
                           ]
                       }
        result = dict()
        for config in configs['data']:
            k = config['n']
            result[k] = S.select_content(response, config)
            result[k] = S.replace_all(result[k])
        print(result)
                    
    def gradeListparse(self, response):
        configs = 1
        if configs['list']['v']:
            response = response.xpath[configs['list']['v']]
        else:
            response = [response]
        for content in response:
            result= dict()
            for config in configs['data']:
                k = config['n']
                result[k] = S.select_content(content, config)
    def trustConpanyListparse(self, response):
        urls = response.xpath("//ul[@class='clearfix xtList']/li/a/@href").extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url,
                                 callback=self.trustConpanyInfoParse,
                                 headers = {'User-Agent':ua(os=('linux','win','mac'))})
    def trustConpanyInfoParse(self, response):
        configs = {'list':{'v':'','t':''},
                   'data':[
                           {'n':'机构全称','En':'','v':'//td[@class="firstTd" and text()="机构全称"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'邮政编码','En':'','v':'//td[@class="firstTd" and text()="邮政编码"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'机构地址','En':'','v':'//td[@class="firstTd" and text()="机构地址"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'机构简称','En':'','v':'//td[@class="firstTd" and text()="机构简称"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'机构电话','En':'','v':'//td[@class="firstTd" and text()="机构电话"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'机构类型','En':'','v':'//td[@class="firstTd" and text()="机构类型"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'机构传真','En':'','v':'//td[@class="firstTd" and text()="机构传真"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'信用级别','En':'','v':'//td[@class="firstTd" and text()="信用级别"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'客服电话','En':'','v':'//td[@class="firstTd" and text()="客服电话"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'所在省份','En':'','v':'//td[@class="firstTd" and text()="所在省份"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'电子邮件','En':'','v':'//td[@class="firstTd" and text()="电子邮件"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'所在城市','En':'','v':'//td[@class="firstTd" and text()="所在城市"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'机构网址','En':'','v':'//td[@class="firstTd" and text()="机构网址"]/following-sibling::td[1]//text()','t':'xpath_first','dt':''},
                           {'n':'机构简介','En':'','v':'//td[@class="firstTd" and text()="机构简介"]/following-sibling::td[1]/p/text()','t':'xpath_first','dt':''},
                           {'n':'机构Logo','En':'','v':'//td[@class="firstTd" and text()="机构Logo"]/following-sibling::td[1]//@src','t':'xpath_first','dt':''},
                           ]
                   }
        if configs['list']['v']:
            response_ = response.xpath(configs['list']['v'])
        else:
            response_ = [response]
        for res in response_:
            print(type(res))
            result = dict()
            for config in configs['data']:
                k = config['n']
                result[k] = S.select_content(res, config)
                result[k] = S.replace_all(result[k])
            print(result)
    def rzrqConpanyListparse(self, response):
        pass
    
    def BankProListparse(self, response):
        pass