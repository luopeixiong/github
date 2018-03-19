# -*- coding: utf-8 -*-
import scrapy
from user_agent import generate_user_agent as ua
import re
from .myselector import Selector as S
import json
from JQKA.items import JqkaItem


class JqkaSpider(scrapy.Spider):
    '''同花顺信托产品以及信托公司Crawler\nEntrance url  is http://trust.10jqka.com.cn/xtcp/0_0_0_0_0_all_fxqzsj_desc_1.shtml
    开放式基金所有页面信息 http://fund.10jqka.com.cn/datacenter/sy/
    '''
    name = "jqka"
    allowed_domains = ["10jqka.com.cn"]
    start_urls = ['http://trust.10jqka.com.cn/xtcp/_0_0_0_0_all_fxqzsj_desc_{0}.shtml',
                  'http://fund.ijijin.cn/data/Net/info/all_rate_desc_0_0_1_9999_0_0_0_jsonp.html']
    def start_requests(self):
        print('Start Crawl Object %s'%self.__class__.__name__)
        print('Docment:\n%s'%self.__doc__)
        page = 1
        for _url in self.start_urls:
            if _url == 'http://trust.10jqka.com.cn/xtcp/_0_0_0_0_all_fxqzsj_desc_{0}.shtml':
                url = _url.format(page)
                yield scrapy.Request(url,
                                     meta = {'page':page,'_url':_url},
                                     callback = self.parse,
                                     method='GET',
                                     headers = {'User-Agent':ua()})
            if _url == 'http://fund.ijijin.cn/data/Net/info/all_rate_desc_0_0_1_9999_0_0_0_jsonp.html':
                url = _url
                yield scrapy.Request(url,
                                      callback = self.privateFundparse,
                                      method='GET',
                                      headers = {'User-Agent':ua()},
                                      encoding='latin-1')
                
    def privateFundparse(self,response):
        #解决乱码问题 更改编码
        response = response.replace(body = response.body.decode('unicode-escape'))
        js = json.loads(response.text)
        configs = {'list':{'n':'','v':'data/data','t':'json'},
                   'data':[{'n':'基金代码','En':'code','v':'code','t':'json'},
                           {'n':'公司代码','En':'ComID','v':'orgid','t':'json'},
                           ]
                   }
        for k,_js in S.select_content(js,configs['list']).items():
            result = dict()
            for config in configs['data']:
                k = config['En']
                result[k] = S.select_content(_js, config)
            code = result['code']
            ComID = result['ComID']
            '''http://fund.10jqka.com.cn/{code}/interduce.html    #基金基本信息'''
            yield scrapy.Request('http://fund.10jqka.com.cn/{code}/interduce.html'.format(code=code),
                                 method='GET',
                                 meta = {'code':code},
                                 headers = {'User-Agent':ua()},
                                 callback = self.interduceParse)
            '''http://fund.10jqka.com.cn/{code}/historynet.html   #历史净值'''
            yield scrapy.Request('http://fund.10jqka.com.cn/{code}/historynet.html'.format(code=code),
                                 method='GET',
                                 headers = {'User-Agent':ua()},
                                 callback = self.historynetParse,
                                 meta = {'code':code})
            '''http://fund.10jqka.com.cn/company/{ComID}/   公司信息'''
            yield scrapy.Request('http://fund.10jqka.com.cn/company/{ComID}/'.format(ComID = ComID),
                                 method='GET',
                                 headers = {'User-Agent':ua()},
                                 callback = self.companyParse,
                                 meta = {'ComID':ComID}
                                 )
            '''http://fund.10jqka.com.cn/{code}/manager.html      基金经理'''
            yield scrapy.Request('http://fund.10jqka.com.cn/{code}/manager.html'.format(code=code),
                                 method='GET',
                                 headers = {'User-Agent':ua()},
                                 callback = self.managerParse,
                                 meta = {'code':code}                                 
                                 )
            '''http://fund.10jqka.com.cn/{code}/commissionagents.html   代销机构'''
            yield scrapy.Request('http://fund.10jqka.com.cn/{code}/commissionagents.html'.format(code=code),
                                 method='GET',
                                 headers = {'User-Agent':ua()},
                                 callback = self.commissionagentsParse,
                                 meta = {'code':code} 
                                 )
            '''http://fund.10jqka.com.cn/{code}/holdchange.html 持仓变动'''
            yield scrapy.Request('http://fund.10jqka.com.cn/{code}/holdchange.html'.format(code=code),
                                 method='GET',
                                 headers = {'User-Agent':ua()},
                                 callback = self.holdchangeParse,
                                 meta = {'code':code} 
                                 )
            '''http://fund.10jqka.com.cn/{code}/rating.html 基金评级'''
#            先忽略这个
#            yield scrapy.Request('http://fund.10jqka.com.cn/{code}/rating.html'.format(code=code),
#                                 method='GET',
#                                 headers = {'User-Agent':ua()},
#                                 callback = self.ratingParse,
#                                 meta = {'code':code}                                  
#                                 )
            '''http://fund.10jqka.com.cn/{code}/dividends.html 基金分红'''
            yield scrapy.Request('http://fund.10jqka.com.cn/{code}/dividends.html'.format(code=code),
                                 method='GET',
                                 headers = {'User-Agent':ua()},
                                 callback = self.ratingParse,
                                 meta = {'code':code}                                  
                                 )
            '''http://fund.10jqka.com.cn/519690/pubnote.html#all   基金公告'''
            '''http://fund.10jqka.com.cn/519690/allocation.html 资产配置'''
            yield scrapy.Request('http://fund.10jqka.com.cn/{code}/allocation.html'.format(code=code),
                                 method='GET',
                                 headers = {'User-Agent':ua()},
                                 callback = self.allocationParse,
                                 meta = {'code':code}                                  
                                 )
            '''http://fund.10jqka.com.cn/519690/bond.html 重仓债券'''
            yield scrapy.Request('http://fund.10jqka.com.cn/{code}/bond.html'.format(code=code),
                                 method='GET',
                                 headers = {'User-Agent':ua()},
                                 callback = self.bondParse,
                                 meta = {'code':code}                                  
                                 )            
            '''http://fund.10jqka.com.cn/{code}/stock.html 重仓股票'''
            yield scrapy.Request('http://fund.10jqka.com.cn/{code}/stock.html'.format(code=code),
                                 method='GET',
                                 headers = {'User-Agent':ua()},
                                 callback = self.stockParse,
                                 meta = {'code':code}                                  
                                 )  
            '''http://fund.10jqka.com.cn/519690/holder.html 持有人结构'''
            yield scrapy.Request('http://fund.10jqka.com.cn/{code}/holder.html'.format(code=code),
                                 method='GET',
                                 headers = {'User-Agent':ua()},
                                 callback = self.holderParse,
                                 meta = {'code':code}                                  
                                 )            
            '''http://fund.10jqka.com.cn/519690/scale.html 份额规模'''
            yield scrapy.Request('http://fund.10jqka.com.cn/{code}/scale.html'.format(code=code),
                                 method='GET',
                                 headers = {'User-Agent':ua()},
                                 callback = self.scaleParse,
                                 meta = {'code':code}                                  
                                 )
    def scaleParse(self,response):
        configs = [{'list':{'n':'持有人统计','v':'//div[@class="sub_wraper_1 cb mt20"]//tr[td[not(contains(text(),"暂无"))]]','t':'xpath'},
                    'data':[{'n':'报告日期','En':'stockCode','v':'td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'期间申购（亿份）','En':'stockCode','v':'td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'期间赎回（亿份）','En':'managerName','v':'td[3]/text()','t':'xpath_first','dt':''},
                            {'n':'期末总份额（亿份）','En':'managerName','v':'td[4]/text()','t':'xpath_first','dt':''},
                            {'n':'总份额变动率（%）','En':'startDate','v':'td[5]/text()','t':'xpath_first','dt':''},
                            {'n':'期末净资产（亿元）','En':'inst','v':'td[6]/text()','t':'xpath_first','dt':''},
                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
                            ]
                    }
            ]
        _response = response
        return self.configPaese(configs,_response,response)
    def holderParse(self, response):
        configs = [{'list':{'n':'持有人统计','v':'//table[@class="m_table" and .//th[text()="报告日期"]]//tr[td[not(contains(text(),"暂无"))]]','t':'xpath'},
                    'data':[{'n':'报告日期','En':'stockCode','v':'td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'机构持有份额（亿份）','En':'stockCode','v':'td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'机构持有比例 （%）','En':'managerName','v':'td[3]/text()','t':'xpath_first','dt':''},
                            {'n':'个人持有份额（亿份）','En':'managerName','v':'td[4]/text()','t':'xpath_first','dt':''},
                            {'n':'个人持有比例（%）','En':'startDate','v':'td[5]/text()','t':'xpath_first','dt':''},
                            {'n':'总份额（亿份）','En':'inst','v':'td[6]/text()','t':'xpath_first','dt':''},
                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
                            ]
                    }
                ]
        _response = response
        return self.configPaese(configs,_response,response)
    def stockParse(self, response):
        configs = [{'list':{'n':'股票重仓','v':'//tbody[contains(@id,"tb_st_")]//tr[td[not(contains(text(),"暂无"))]]','t':'xpath'},
                    'data':[{'n':'标题','En':'stockCode','v':'parent::tbody/@id','t':'xpath_first','dt':''},
                            {'n':'股票代码','En':'stockCode','v':'td[2]/a/text()','t':'xpath_first','dt':''},
                            {'n':'股票名称','En':'managerName','v':'td[3]/a/text()','t':'xpath_first','dt':''},
                            {'n':'持有量（万股）','En':'managerName','v':'td[4]/text()','t':'xpath_first','dt':''},
                            {'n':'市值（万元）','En':'startDate','v':'td[5]/text()','t':'xpath_first','dt':''},
                            {'n':'占净值比','En':'inst','v':'td[6]/text()','t':'xpath_first','dt':''},
                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
                            ]
                    },
                    {'list':{'n':'行业重仓','v':'//tbody[contains(@id,"tb_hy_")]//tr[td[not(contains(text(),"暂无"))]]','t':'xpath'},
                    'data':[{'n':'标题','En':'stockCode','v':'parent::tbody/@id','t':'xpath_first','dt':''},
                            {'n':'行业代码','En':'stockCode','v':'td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'行业类别','En':'managerName','v':'td[3]/text()','t':'xpath_first','dt':''},
                            {'n':'市值（万元）','En':'managerName','v':'td[4]/text()','t':'xpath_first','dt':''},
                            {'n':'占净值比','En':'startDate','v':'td[5]/text()','t':'xpath_first','dt':''},
                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
                            ]
                    }
                ]
        _response = response
        return self.configPaese(configs,_response,response)
    def bondParse(self, response):
        configs = [{'list':{'n':'证券重仓','v':'//tbody[contains(@id,"tb_bo_")]//tr[td[not(contains(text(),"暂无"))]]','t':'xpath'},
                    'data':[{'n':'标题','En':'stockCode','v':'parent::tbody/@id','t':'xpath_first','dt':''},
                            {'n':'股票代码','En':'stockCode','v':'td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'股票名称','En':'managerName','v':'td[3]/text()','t':'xpath_first','dt':''},
                            {'n':'持有量（万股）','En':'managerName','v':'td[4]/text()','t':'xpath_first','dt':''},
                            {'n':'市值（万元）','En':'startDate','v':'td[5]/text()','t':'xpath_first','dt':''},
                            {'n':'占净值比','En':'inst','v':'td[6]/text()','t':'xpath_first','dt':''},
                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
                            ]
                    }
                ]
        _response = response
        return self.configPaese(configs,_response,response)
    def allocationParse(self, response):
        configs = [{'list':{'n':'资产配置','v':'//div[@class="sub_wraper_1 cb mt20"]//tr[td[not(contains(text(),"暂无"))]]','t':'xpath'},
                    'data':[{'n':'报告日期','En':'ReportDate','v':'td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'股票市值（亿元）','En':'StockMarketValue','v':'td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'股票占净比（%）','En':'NetShareRatio','v':'td[3]/text()','t':'xpath_first','dt':''},
                            {'n':'债券市值（亿元）','En':'bondsMarketvalue','v':'td[4]/text()','t':'xpath_first','dt':''},
                            {'n':'债券占净比（%）','En':'inst','v':'td[5]/text()','t':'xpath_first','dt':''},
                            {'n':'现金市值（亿元））','En':'inst','v':'td[6]/text()','t':'xpath_first','dt':''},
                            {'n':'现金占净比（%）','En':'inst','v':'td[7]/text()','t':'xpath_first','dt':''},
                            {'n':'其他市值（亿元）','En':'inst','v':'td[8]/text()','t':'xpath_first','dt':''},
                            {'n':'其他占净比（%）','En':'inst','v':'td[9]/text()','t':'xpath_first','dt':''},
                            {'n':'净资产（亿元）','En':'inst','v':'td[10]/text()','t':'xpath_first','dt':''},
                            {'n':'资产总值（亿元）','En':'inst','v':'td[11]/text()','t':'xpath_first','dt':''},
                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
                            ]
                    }
                ]
        _response = response
        return self.configPaese(configs,_response,response)
    def ratingParse(self, response):
        
        configs = [{'list':{'n':'分红详情','v':'//div[@class="sub_cont_0 fl w100" and .//h2[text()="分红详情"]]/div[2]//tr[td[td[not(contains(text(),"暂无"))]]','t':'xpath'},
                    'data':[{'n':'公告日期','En':'stockCode','v':'td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'权益登记日','En':'managerName','v':'td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'除息日','En':'managerName','v':'td[3]/text()','t':'xpath_first','dt':''},
                            {'n':'每份分红','En':'startDate','v':'td[4]/text()','t':'xpath_first','dt':''},
                            {'n':'分红发放日','En':'inst','v':'td[5]/text()','t':'xpath_first','dt':''},
                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
                            ]
                    }
                ]
        _response = response
        return self.configPaese(configs,_response,response)
    def holdchangeParse(self, response):
        configs = [{'list':{'n':'持仓变动','v':'//div[contains(@typeid,"increase_")]//tr[td]','t':'xpath'},
                    'data':[{'n':'股票代码','En':'stockCode','v':'td[2]/a/text()','t':'xpath_first','dt':''},
                            {'n':'标题','En':'managerName','v':'ancestor::div[contains(@typeid,"increase_")]//div[@class="m_title_4"]//span[re:test(text(),"\d{4}年\d季度")]/text()','t':'xpath_first','dt':''},
                            {'n':'截止日期','En':'managerName','v':'ancestor::div[contains(@typeid,"increase_")]//div[@class="m_title_4"]//span[re:test(text(),"\d{4}-\d{2}-\d{2}")]/text()','t':'xpath_first','dt':''},
                            {'n':'股票名称','En':'startDate','v':'td[3]/a/text()','t':'xpath_first','dt':''},
                            {'n':'本期累计买入金额（万元）','En':'inst','v':'td[5]/text()','t':'xpath_first','dt':''},
                            {'n':'占期初基金资产净值比例','En':'code','v':'td[6]/text()','t':'xpath_first','dt':''},
                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
                            ]
                    }
                ]
        _response = response
        return self.configPaese(configs,_response,response)
    def commissionagentsParse(self, response):
        configs = [{'list':{'n':'代销机构','v':'','t':''},
                    'data':[{'n':'证券公司','En':'managerName','v':'//table[@class="m_table m_table_1"]//tr[td]/td[1]/span[re:match(text(),"[\u4e00-\u9fa5]")]//text()','t':'xpath_split','dt':''},
                            {'n':'银行','En':'startDate','v':'//table[@class="m_table m_table_1"]//tr[td]/td[2]/span[re:match(text(),"[\u4e00-\u9fa5]")]//text()','t':'xpath_split','dt':''},
                            {'n':'其他','En':'inst','v':'//table[@class="m_table m_table_1"]//tr[td]/td[3]/span[re:match(text(),"[\u4e00-\u9fa5]")]//text()','t':'xpath_split','dt':''},
                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
                            ]
                    }
                ]
        _response = response
        return self.configPaese(configs,_response,response)
    def managerParse(self, response):
        #编写configs
        configs = [{'list':{'n':'基金经理','v':'//div[@class="news_detail_0 mt20"]','t':'xpath'},
                    'data':[{'n':'姓名','En':'managerName','v':'.//dl/dd[1]/text()','t':'xpath_first','dt':''},
                            {'n':'上任日期','En':'startDate','v':'.//dl/dd[2]/text()','t':'xpath_first','dt':''},
                            {'n':'简历','En':'inst','v':'.//dl/dd[3]/text()','t':'xpath_first','dt':''},
                            {'n':'一寸照','En':'image','v':'.//@src','t':'xpath_first','dt':''},
                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
                            ]
                    },
#                    {'list':{'n':'','v':'','t':''},
#                    'data':[{'n':'姓名','En':'managerName','v':'//div[div[@class="m_title_1 mb0" and h2[contains(text(),"现任基金经理")]]]//dl/dd[1]/text()','t':'xpath_first','dt':''},
#                            {'n':'上任日期','En':'startDate','v':'//div[div[@class="m_title_1 mb0" and h2[contains(text(),"现任基金经理")]]]//dl/dd[2]/text()','t':'xpath_first','dt':''},
#                            {'n':'简历','En':'inst','v':'//div[div[@class="m_title_1 mb0" and h2[contains(text(),"现任基金经理")]]]//dl/dd[3]/text()','t':'xpath_first','dt':''},
#                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
#                            ]
#                    }
                   ]
        _response = response
        return self.configPaese(configs,_response,response)
    def companyParse(self, response):
        #基金信息
        #编写configs
        configs = [{'list':{'n':'公司信息','v':'','t':''},
                    'data':[{'n':'公司ID','En':'ComID','v':'ComID','t':'meta','dt':''},
                            {'n':'公司名称','En':'ComName','v':'//table[@class="m_table sub_table"]//tr[1]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'成立日期','En':'SetupDate','v':'//table[@class="m_table sub_table"]//tr[1]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'法人代表','En':'','v':'//table[@class="m_table sub_table"]//tr[2]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'总经理','En':'','v':'//table[@class="m_table sub_table"]//tr[2]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'注册资金','En':'','v':'//table[@class="m_table sub_table"]//tr[3]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'管理规模','En':'','v':'//table[@class="m_table sub_table"]//tr[3]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'联系电话','En':'','v':'//table[@class="m_table sub_table"]//tr[4]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'邮政编码','En':'','v':'//table[@class="m_table sub_table"]//tr[4]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'客户邮箱','En':'','v':'//table[@class="m_table sub_table"]//tr[5]/td[1]/a/text()','t':'xpath_first','dt':''},
                            {'n':'网站地址','En':'','v':'//table[@class="m_table sub_table"]//tr[5]/td[1]/a/text()','t':'xpath_first','dt':''},
                            {'n':'传真号码','En':'','v':'//table[@class="m_table sub_table"]//tr[6]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'办公地址','En':'','v':'//table[@class="m_table sub_table"]//tr[6]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'公司介绍','En':'','v':'//div[@class = "sub_wraper_1 cb" and div[h2[contains(text(),"公司介绍")]]]/div[2]/*/text()','t':'xpath_first','dt':''},
                            {'n':'旗下基金数','En':'','v':'//ul[@class="rank_list fl"]/li[1]/text()[1]','t':'xpath_first','dt':''},
                            {'n':'基金经理人数','En':'','v':'//ul[@class="rank_list fl"]/li[4]/text()[1]','t':'xpath_first','dt':''},
                            {'n':'份额数量','En':'','v':'//ul[@class="rank_list fl"]/li[2]/text()[1]','t':'xpath_first','dt':''},
                            {'n':'资产净值','En':'','v':'//ul[@class="rank_list fl"]/li[5]/text()[1]','t':'xpath_first','dt':''},
                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
                            ]
                    }
            ]
        _response = response
        return self.configPaese(configs,_response,response)
    def historynetParse(self,response):
        configs = [{'list':{'n':'历史净值','v':'static','t':'static'},
                    'data':[{'n':'日期','En':'date','v':'date','t':'json','dt':''},
                            {'n':'单位净值','En':'net','v':'net','t':'json','dt':''},
                            {'n':'累计净值','En':'totalnet','v':'totalnet','t':'json','dt':''},
                            {'n':'--','En':'fqnet','v':'fqnet','t':'json','dt':''},
                            {'n':'增长值','En':'inc','v':'inc','t':'json','dt':''},
                            {'n':'增长率 (%)','En':'rate','v':'rate','t':'json','dt':''},
                            {'n':'基金编码','En':'code','v':'code','t':'meta','dt':''},
                           ]
                    }
            ]
        #正则提取js字段 
        response = response.replace(body = re.search('JsonData\s*?=\s*?(\[.*?\])',response.text,re.S).group(1))
        _response = json.loads(response.text)
        
        return self.configPaese(configs,_response,response)
    def configPaese(self, configs,_response,response=None,meta={}):
        #实例化item
        item = JqkaItem()
        #迭代可能多个的configs
        for _configs in configs:
            #根据key v 修改response为列表
            if _configs['list']['v']:
                res = S.select_content(_response,_configs['list'])
            else:
                #list(response)   ----让response可迭代
                res = [_response]
            #避免select[]列表
            if res:
                for _res in res:
                    #初始化result
                    result = dict()
                    #遍历每个字段提取
                    for config in _configs['data']:
                        k = config['n']
#                        print(k)
                        result[k] = S.select_content(_res, config, response)
                        result[k] = S.replace_invalid_char(result[k])
                    item['result'] = result
                    #传递pipelin处理item字段
                    yield item    
    def interduceParse(self, response):
        #基金信息
        #编写configs
        configs = [{'list':{'n':'基金信息','v':'//div[@class="cont_table"]','t':'xpath'},
                    'data':[{'n':'基金代码','En':'','v':'.//tr[1]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'基金简称','En':'','v':'.//tr[1]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'基金类型','En':'','v':'.//tr[2]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'基金全称','En':'','v':'.//tr[2]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'投资类型','En':'','v':'.//tr[3]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'基金经理','En':'','v':'.//tr[3]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'成立日期','En':'','v':'.//tr[4]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'成立规模','En':'','v':'.//tr[4]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'管理费','En':'','v':'.//tr[5]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'份额规模','En':'','v':'.//tr[5]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'首次最低金额(元)','En':'','v':'.//tr[6]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'托管费','En':'','v':'.//tr[6]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'基金管理人','En':'','v':'.//tr[7]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'基金托管人','En':'','v':'.//tr[7]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'最高认购费','En':'','v':'.//tr[8]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'最高申购费','En':'','v':'.//tr[8]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'最高赎回费','En':'','v':'.//tr[9]/td[1]/text()','t':'xpath_first','dt':''},
                            {'n':'业绩比较基准','En':'','v':'.//tr[9]/td[2]/text()','t':'xpath_first','dt':''},
                            {'n':'投资目标','En':'','v':'//div[h2[contains(text(),"投资目标")]]/following-sibling::div/*/text()','t':'xpath_first','dt':''},
                            {'n':'投资范围','En':'','v':'//div[h2[contains(text(),"投资范围")]]/following-sibling::div/*/text()','t':'xpath_first','dt':''},
                            {'n':'投资策略','En':'','v':'//div[h2[contains(text(),"投资策略")]]/following-sibling::div/*/text()','t':'xpath_first','dt':''},
                            {'n':'风险收益特征','En':'','v':'//div[h2[contains(text(),"风险收益特征")]]/following-sibling::div/*/text()','t':'xpath_first','dt':''},
                            ]
                    }
            ]
        _response = response
        return self.configPaese(configs,_response,response)
    def parse(self, response):
        page = response.meta['page']
        _url = response.meta['_url']
        if page == 1:
            totalPage = response.xpath('//a[text()="末页"]/@href').extract_first()
            if totalPage:
#                regex = re.compile(r'http://trust.10jqka.com.cn/xtcp/_0_0_0_0_all_fxqzsj_desc_(\d+).shtml',re.I)
                re_res = re.search(r'http://trust.10jqka.com.cn/xtcp/_0_0_0_0_all_fxqzsj_desc_(\d+).shtml',totalPage,re.I)
                totalPage = int(re_res.group(1)) if re_res else 1
            else:
                totalPage = 1
        else:
            totalPage = response.meta['totalPage']
        urls_Com = response.xpath('//td[@class="left_td"]/a/@href').extract()
        urls_Prod = response.xpath('//td[@class="name_row left_td"]/a/@href').extract()
        for url in urls_Com:
            yield scrapy.Request(url,
                                 callback = self.InfoParse,
                                 method='GET',
                                 headers = {'User-Agent':ua()})
        for url in urls_Prod:
            yield scrapy.Request(url,
                                 callback = self.InfoParse,
                                 method='GET',
                                 headers = {'User-Agent':ua()})
                
        '''爬取下一页'''      
        if page < totalPage:
            page+=1
            url = _url.format(page)
            yield scrapy.Request(url,
                                     meta = {'page':page,'_url':_url,'totalPage':totalPage},
                                     callback = self.parse,
                                     method='GET',
                                     headers = {'User-Agent':ua()})
     
        
    def InfoParse(self, response):
        
        
        if re.search('^http:\/\/trust\.10jqka\.com\.cn\/\w+?\/$',response.url):
            #信托公司cfg
            configs = [{'list':{'n':'','v':'//div[@class="table_cont"  and table[@class="m_table"]]','t':'xpath','keys':[],'db':''},
                    'data':[{'n':'公司ID','En':'ComdId','v':-2,'t':'url_split','dt':''},
                            {'n':'公司名称','En':'ComName','v':'.//tr[1]/td/text()','t':'xpath_first','dt':''},
                            {'n':'英文名称','En':'ComEname','v':'.//tr[2]/td/text()','t':'xpath_first','dt':''},
                            {'n':'是否上市','En':'is_Listed','v':'.//tr[3]/td/text()','t':'xpath_first','dt':''},
                            {'n':'省份','En':'Province','v':'.//tr[4]/td/text()','t':'xpath_first','dt':''},
                            {'n':'城市','En':'city','v':'.//tr[5]/td/text()','t':'xpath_first','dt':''},
                            {'n':'成立日期','En':'setupDate','v':'.//tr[6]/td/text()','t':'xpath_first','dt':''},
                            {'n':'注册资本(亿元)','En':'RegCapital','v':'.//tr[7]/td/text()','t':'xpath_first','dt':''},
                            {'n':'公司网址','En':'website','v':'.//tr[8]/td/a/@href','t':'xpath_first','dt':''},
                            {'n':'注册地址','En':'RegAddress','v':'.//tr[9]/td/text()','t':'xpath_first','dt':''},
                            {'n':'办公地址','En':'OfficeAddress','v':'.//tr[10]/td/text()','t':'xpath_first','dt':''},
                            {'n':'邮政编码','En':'PositionCode','v':'.//tr[11]/td/text()','t':'xpath_first','dt':''},
                            {'n':'电话','En':'TelNumber','v':'.//tr[12]/td/text()','t':'xpath_first','dt':''},
                            {'n':'传真','En':'Fax','v':'.//tr[13]/td/text()','t':'xpath_first','dt':''},
                            {'n':'电子邮件','En':'Email','v':'.//tr[14]/td/text()','t':'xpath_first','dt':''},
                            {'n':'法人代表','En':'Legal_representative','v':'.//tr[15]/td/text()','t':'xpath_first','dt':''},
                            {'n':'总经理','En':'General_manager','v':'.//tr[16]/td/text()','t':'xpath_first','dt':''},
                            {'n':'经营范围','En':'Business_scope','v':'.//tr[17]/td/*/text()','t':'xpath_first','dt':''},
                            {'n':'产品数量','En':'ProdNums','v':'//span[text()="共有"]/strong/text()','t':'xpath_first','dt':''},
                            ],
                    'clear':[]
                    }
                    ]
        if re.search('^http:\/\/trust\.10jqka\.com\.cn\/\w+?\/\w+?\/$',response.url):
            #信托产品cfg
            configs = [{'list':{'n':'','v':'//div[@class="table_cont"  and table[@class="m_table"]]','t':'xpath','keys':[],'db':''},
                    'data':[{'n':'产品ID','En':'ProdId','v':-2,'t':'url_split','dt':''},
                            {'n':'产品名称','En':'ProName','v':'.//tr[1]/td/text()','t':'xpath_first','dt':''},
                            {'n':'信托类型','En':'trust_type','v':'.//tr[2]/td/text()','t':'xpath_first','dt':''},
                            {'n':'信托公司','En':'trust_Com','v':'.//tr[3]/td/a/text()','t':'xpath_first','dt':''},
                            {'n':'信托公司ID','En':'trust_ComID','v':'.//tr[3]/td/a/@href','t':'xpath_first','dt':''},
                            {'n':'推介起始日','En':'recommendStart_date','v':'.//tr[4]/td/text()','t':'xpath_first','dt':''},
                            {'n':'推介截止日','En':'recommendEnd_date','v':'.//tr[5]/td/text()','t':'xpath_first','dt':''},
                            {'n':'成立日期','En':'setupDate','v':'.//tr[6]/td/text()','t':'xpath_first','dt':''},
                            {'n':'截止日期','En':'endDate','v':'.//tr[7]/td/text()','t':'xpath_first','dt':''},
                            {'n':'预期发行规模(万元)','En':'expectScale','v':'.//tr[8]/td/text()','t':'xpath_first','dt':''},
                            {'n':'实际发行规模(万元)','En':'actualScal','v':'.//tr[9]/td/text()','t':'xpath_first','dt':''},
                            {'n':'预计收益率(%)','En':'ExpectYieldRatio','v':'.//tr[10]/td/text()','t':'xpath_first','dt':''},
                            {'n':'存续期(年)','En':'Duration','v':'.//tr[11]/td/text()','t':'xpath_first','dt':''},
                            {'n':'资金门槛(万元)','En':'Cpital_threshold','v':'.//tr[12]/td/text()','t':'xpath_first','dt':''},
                            {'n':'发行地','En':'pulsh_area','v':'.//tr[13]/td/text()','t':'xpath_first','dt':''},
                            {'n':'托管人','En':'Trustee','v':'.//tr[14]/td/text()','t':'xpath_first','dt':''},
                            {'n':'投资范围','En':'investment_filed','v':'.//tr[15]/td/text()','t':'xpath_first','dt':''},
                            {'n':'投资理念及目标','En':'ideaAndGoal','v':'.//tr[16]/td/text()','t':'xpath_first','dt':''},
                            {'n':'投资策略','En':'investment_strategy','v':'.//tr[17]/td/text()','t':'xpath_first','dt':''},
                            {'n':'投资顾问及代表简介','En':'adviser_introduction','v':'.//tr[18]/td/text()','t':'xpath_first','dt':''},
                            {'n':'信托计划摘要','En':'abstract','v':'.//tr[19]/td/text()','t':'xpath_first','dt':''},
#                            {'n':'','En':'','v':'.//td[19]/text()','t':'xpath_first','dt':''},
                            ],
                    'clear':[{'En':'trust_ComID','t':'splitwith/','v':-2}]
                    }
                    ]
        for _configs in configs:
            if _configs['list']['v']:
                res = S.select_content(response, _configs['list'])
                if res is []:
                    raise ValueError('check %s and %s is writed True'%(_configs['list']['v'],_configs['list']['t']))
            else:
                res = [response]
            for _response in res:
                result = dict()
                for config in _configs['data']:
                    k = config['En']
                    result[k] = S.select_content(_response,config,response)
                    result[k] = S.replace_invalid_char(result[k])
                if _configs.get('clear'):
                    for config in _configs['clear']:
                        k = config['En']
                        result[k]  = S.select_content(result[k],config)
                        result[k] = S.replace_html_tag(result[k])
                if '暂无相关信息' not in response.text:
                    print(result)