# -*- coding: utf-8 -*-
import scrapy
from user_agent import generate_user_agent as ua
import re
from .config import Config
from myselector import Selector as S
import requests
from Cyzone.items import CyzoneItem
def get_ua():
    return {'User-Agent':ua(os=('win','mac','linux'))}

def get_proxy():
    res = requests.get("http://10.1.18.35:5010/get_all/")
    proxies = re.compile('\"(.*?)\"').findall(res.text)
    proxies = ['http://'+proxy for proxy in proxies]
    return proxies

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))
    
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
    request = response.request.replace(dont_filter = True)
    if flag and 'setTimeout' in response.text:
        return request
    elif response.status not in [200,302,301]:
        try:
            proxy = response.meta['proxy'].replace('http://','')
            delete_proxy(proxy)
            meta = response.meta
            meta['proxy'] = get_proxy
            request = request.replace(meta=meta,dont_filter=True)
            return request
        except:
            pass
        
    
class CyzoneSpider(scrapy.Spider):
    name = "cyzone"
    allowed_domains = ["cyzone.cn"]
    start_urls = [
                  'http://www.cyzone.cn/vcompany/list-0-0-{page}-0-0/',
                  'http://www.cyzone.cn/company/list-0-{page}-4/',
                  'http://www.cyzone.cn/vpeople/list-0-{page}/',
                  'http://www.cyzone.cn/people/list-0-{page}-0-0/'
                  ]
    pools = set()
    custom_settings = {'DOWNLOADER_MIDDLEWARES': {
                        'Cyzone.middlewares.RotateUserAgentMiddleware':401,
                        'Cyzone.middlewares.ProxyMiddleware':700,
                        },
                        'CONCURRENT_REQUESTS' :16,
#                        'DOWNLOAD_DELAY':0.5,
                        'DEPTH_PRIORITY' : 1,
                        }
    config_s = Config.config_s()
    config_f = Config.config_f()
    config_d = Config.config_d()
    config_r = Config.config_r()
    
    def start_requests(self):
        for url in self.start_urls:
            url = url.format(page=1)
            yield scrapy.Request(url,
                                 meta = {'page':1,'LatsUrl':None},
                                 dont_filter=True,
                                 headers = get_ua())
    def parse(self, response):
        request = checkTimeError(response)
        if request:
            yield request
            return None
        page,LatsUrl = response.meta['page'],response.meta['LatsUrl']
        if LatsUrl is None:
            LatsUrl = response.urljoin(response.xpath('//div[@id="pages"]/a[last()]/@href').extract_first())
        #http://www.cyzone.cn/s/20171013/23764.html
        #http://www.cyzone.cn/f/20170728/3184.html
        #http://www.cyzone.cn/d/20110626/9.html
        #http://www.cyzone.cn/r/20171016/57530.html
        urlList = re.findall('https?:\/\/www\.cyzone\.cn\/[sfdr]/\d+\/\d+\.html',response.text)
        if urlList:
            for url in urlList:
                if url not in self.pools:
                    self.pools.add(url)
                    yield scrapy.Request(url,
                                         callback = self.infoParse,
                                         headers=get_ua(),
                                         dont_filter=True)
        if response.url!=LatsUrl:
            page+=1
            nexturl = self.urlparse(response.url).format(page=page)
            yield scrapy.Request(nexturl,
                                 headers=get_ua(),
                                 meta = {'page':page,'LatsUrl':LatsUrl},
                                 dont_filter=True)
    
    def infoParse(self, response):
        item = CyzoneItem()
        request = checkTimeError(response)
        if request:
            yield request
            return None
        item = CyzoneItem()
        configs = self.configChance(response.url)
        result = dict()
        for config in configs['data']:
            k = config['En']
            result[k] = S.select_content(response, config, response)
            result[k] = S.replace_all(result[k])
        item['result'] = result
        item['keys'] = configs['list']['keys']
        item['db'] = configs['list']['db']
        if result[configs['list']['check']]:
            yield item
        
    def urlparse(self,url):
        config  = [{'i':r'http://www.cyzone.cn/vcompany/','o':'http://www.cyzone.cn/vcompany/list-0-0-{page}-0-0/'},
                   {'i':r'http://www.cyzone.cn/company/','o':'http://www.cyzone.cn/company/list-0-{page}-4/'},
                   {'i':r'http://www.cyzone.cn/vpeople/','o':'http://www.cyzone.cn/vpeople/list-0-{page}/'},
                   {'i':r'http://www.cyzone.cn/people/','o':'http://www.cyzone.cn/people/list-0-{page}-0-0/'}]
        for i in config:
            if re.search(i['i'],url):
                return i['o']
            
    def configChance(self,url):
        
        config = [{'i':'https?:\/\/www\.cyzone\.cn\/s/\d+\/\d+\.html','o':self.config_s},
                  {'i':'https?:\/\/www\.cyzone\.cn\/f/\d+\/\d+\.html','o':self.config_f},
                  {'i':'https?:\/\/www\.cyzone\.cn\/d/\d+\/\d+\.html','o':self.config_d},
                  {'i':'https?:\/\/www\.cyzone\.cn\/r/\d+\/\d+\.html','o':self.config_r}
                  ]
        for c in config:
            if re.search(c['i'], url):
                return c['o']