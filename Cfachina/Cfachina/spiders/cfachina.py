# -*- coding: utf-8 -*-
import scrapy
from user_agent import generate_user_agent
from .myselector import Selector as S
from Cfachina.items import CfachinaItem
import urllib.parse
from .config import Configs as C
Con = C()


class CfachinaSpider(scrapy.Spider):
    '''该爬虫为爬取期货业协会以下基础信息  
1:期货公司基本情况
2：历史情况

3：分支机构
4：高管人员信息
5：从业人员信息
6：股东信息
7:诚信记录信息
8：财务信息
9：次级债务信息
'''
    name = "cfachina"
    allowed_domains = ["cfachina.org"]
    start_urls = ['http://www.cfachina.org/cfainfo/organbaseinfoServlet',
                  ]
    page = 1
    size = 20
    def madedata(self,page):
        data = {'currentPage':str(page),
                'pageSize':str(self.size),
                'all':'personinfo'}
        return data
    def start_requests(self):
        print("Start Crawl %s"%self.__class__.__name__)
        print("爬虫任务描述:%s"%self.__doc__)
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
        """从业资格信息"""
#        '''保存为本地html'''
#        print(response.text)
#        with open("1.html","wb") as f:
#            f.write(response.body)
        if self.page == 1:
            self.cdfQualificationListTotalPages = int(response.xpath('//ul[@class="yema"]/li[last()]/span/text()').extract_first())
        currentPage = 1
        for info in response.xpath('//td[text()=" 机构编号 "]/parent::tr/following-sibling::tr'):
            #获取机构编号，构造九表url
            organid = info.xpath('td[1]/text()').extract_first()
            #构造url
            #资管业务--暂时未写逻辑
#            data_ = {'organid':organid}
#            yield scrapy.Request('http://www.cfachina.org/cfainfo/personOfAssetmanageinfoServlet?'+urllib.parse.urlencode(data_),
#                                 meta = {'organid':organid},
#                                 callback = self.infoParse1,
#                                 headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))}
#                                 )
            for selecttype in [
                               {'t':'organbaseinfo','callback':'self.infoParse'},
                               {'t':'organhisinfo','callback':'self.infoParse'},
                               {'t':'organbranchinfo','callback':'self.infoParse'},
                               {'t':'supervisorinfo','callback':'self.infoParse'},
                               {'t':'personinfo','callback':'self.infoParse'},
                               {'t':'organshareholderinfo','callback':'self.infoParse'},
                               {'t':'organcreditinfo','callback':'self.infoParse'},
                               {'t':'organfinancialinfo','callback':'self.infoParse'},
                               {'t':'subdebtmonthinfo','callback':'self.infoParse'}
                            ]:
                #urlencode生成method:get url
                data = {'organid':organid,
                        'currentPage':str(currentPage),
                        'pageSize':'20',
                        'selectType':selecttype['t']
                        }
                url = 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?'+urllib.parse.urlencode(data)
                callbacks = selecttype['callback']
                selectType = selecttype['t']
                #发送url request
                yield scrapy.Request(url,
                                     meta = {'currentPage':currentPage,'organid':organid,'callbacks':callbacks,'selectType':selectType},
                                     callback = eval(callbacks),
                                     headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))}
                                     )
                
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
    
    def infoParse(self, response):
        item = CfachinaItem()
        currentPage = response.meta['currentPage']
        organid = response.meta['organid']
        callbacks = response.meta['callbacks']
        selectType = response.meta['selectType']
        #第一页时，获取全局totalPage
        if currentPage == 1:
            totalPage = response.xpath('//li[text()="共["]/span/text()').extract_first()
            totalPage = int(totalPage) if totalPage and totalPage.isdigit() else None
        #非第一页时，从meta里获取全局totalPage
        else:
            
            totalPage = response.meta['totalPage']
        configs = Con.main(response.url)
        if configs['list']['v'] is not '':
            res = S.select_content(response, configs['list'])
        else:
            res = [response]
        #res可能为None,若非None，则parse数据
        if res is not None:
            for info in res:
                result = dict()
                for config in configs['data']:
                    k = config['En']
                    result[k] = S.select_content(info, config)
                    result[k] = S.replace_all(result[k])
    #            print(result)
                item['result'] = result
                item['keys'] = configs['list']['keys']
                item['db'] = configs['list']['db']
                yield item
        #根据类和totalPage判断是否还有下一页，有就继续request nextpage   
        if isinstance(totalPage,int) and currentPage<totalPage/20:
            currentPage+=1
            data = {'organid':organid,
                    'currentPage':str(currentPage),
                    'pageSize':'20',
                    'selectType':selectType
                        }
            url = 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?'+urllib.parse.urlencode(data)
            yield scrapy.Request(url,
                                 callback=eval(callbacks),
                                 headers = {'User-Agent':generate_user_agent(os=('win','mac','linux'))},
                                 meta = {'currentPage':currentPage,'totalPage':totalPage,'organid':organid,'callbacks':callbacks,'selectType':selectType},
                                 )
#    def infoParse1(self, response):
#        '''资管业务'''
#        configs = {'list':{'n':'','v':'//table//tr[position()>1]','t':'xpath'},
#                            'data':[{'n':'债务名称','En':'','v':'td[1]/text()','t':'xpath_first','dt':''},
#        