# -*- coding:utf-8 -*-


import time,random,json,re,os,sys
import scrapy,xlrd
from numbers import Real
from user_agent import generate_user_agent
from SpiderHelp import SpiderHelp,Item
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


class FileItem(scrapy.Item):
    path = scrapy.Field()


BASE_DIR = os.getcwd()
# UA池
class Headers(object):
    def __init__(self,os=('win',),content_type=1):
        self.os = os
        self.content_type = 'application/x-www-form-urlencoded' if content_type else 'application/json'

    @property
    def choice(self):
        return {'User-Agent':generate_user_agent(os=self.os),
                'Content-Type': self.content_type,
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Accept-Encoding': 'gzip, deflate', 
                'Connection': 'keep-alive',
                'Accept': '*/*'}

headers = Headers()

# 简化时间戳 乘以1000  可复用格式化类
class mytime(int):
    def __init__(self):
        import time
        self.val = time.time()
        del time

    @property
    def time(self):
        return int(self.val.__mul__(1000))


class CrbcSpider(scrapy.Spider,SpiderHelp):
    name = 'crbcspider'
    start_urls = ['http://xukezheng.cbrc.gov.cn/ilicence/getProvinceInfo.do?_dc={time.time}'.format(time=mytime())]
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES':
        {
            # 启用UA中间件
            # 'DistributedSpider.middlewares.RotateUserAgentMiddleware': 401,
            # 启用代理
            'DistributedSpider.middlewares.ProxyMiddleware': 700,
        },
        # 最大并发
        'CONCURRENT_REQUESTS': 16,
        # 单ip最大并发
        # 'CONCURRENT_REQUESTS_PER_IP': 8,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        # 下载延迟
        # 'DOWNLOAD_DELAY': 1,
        # 爬虫策略
        'DEPTH_PRIORITY': 1,
        # 允许的status
        'HTTPERROR_ALLOWED_CODES': list(range(400,600))
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url,
                headers=headers.choice,
                meta={'proxys':True},
                callback=self.get_provinece)

    def get_provinece(self, response):
        JS = json.loads(re.compile('(\[.*?\])').search(response.text).group(1))
        provineceCodes = ((provinece['provinceName'],provinece['provineceCode']) 
                            for provinece in JS 
                                if provinece['provineceCode'] >0)
        for city,code in provineceCodes:
            url = 'http://xukezheng.cbrc.gov.cn/ilicence/reportLicence.do?useState=3&organNo=&fatherOrganNo=&province={code}&orgAddress=&organType=&branchType=&fullName=&address=&flowNo='.format(code=code)
            yield scrapy.Request(url,
                headers=headers.choice,
                meta={'city':city,'url':url,'proxys':True},
                callback=self.save_xls)

    # @SpiderHelp.check_response
    def save_xls(self, response):
        if 'Content-Disposition' in response.headers:
            file_path = os.path.join(BASE_DIR,response.meta['city']+'.xls')
            with open(file_path,'wb') as f:
                f.write(response.body)
            xls = xlrd.open_workbook(file_path)
            table = xls.sheets()[0] 
            for rows in range(1,table.nrows+1):
                data = table.row(rows)
                data = [row.value for row in data]
                data[:2] = ['%s-%s' % (data[0],data[1])]
                result = {}
                for index,word in enumerate('site_of_institution serial_number org_code org_name org_address longitude latitude date_of_approval exchangeDate issuingDate State'.split()):
                    result[word] = data[index]
                result['serial_number'] = '{0:{1}8}'.format(int(result['serial_number']),0)
                item=Item()
                item['result'] = result
                item['keys'] = ['org_code', 'org_name', 'serial_number']
                item['db'] = 'CBRC.cbrc_institution_from_xls'
                item['conn'] = False
                if result['org_code']:
                    yield item
            time.sleep(0.1)
            os.remove(file_path)
        else:
            yield response.request.replace(dont_filter=True)







