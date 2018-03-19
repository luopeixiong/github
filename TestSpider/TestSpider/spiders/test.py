# -*- coding: utf-8 -*-
import scrapy
import json
from user_agent import generate_user_agent


class TestSpider(scrapy.Spider):
    name = "test"
#    allowed_domains = ["tst.com"]
    start_urls = ['http://60.28.163.201:8091/lawyer/lawyeroffice/getLawyerOfficeSearch']


    def start_requests(self):
        page = 1
        for url in self.start_urls:
            if url == 'http://60.28.163.201:8091/lawyer/lawyeroffice/getLawyerOfficeSearch':
                    data = self.tj_first_data(page)
                    yield scrapy.Request(
                        url,
                        method='POST',
                        body=data,
                        headers=self.default_jheader,
                        meta={'page': 1},
                        )

    def parse(self, response):
        print(response.text)

    def tj_first_data(self,page,pagesize=20):
        data = {
            "lawofficeresult":"0",
            "fuzeren":"",
            "lawofficenature":"",
            "lawofficename":"",
            "areacode":"",
            "permit":"",
            "creditnumber":"",
            "page":str(page),
            "pagesize":str(pagesize)
        }
        return json.dumps(data)
#{"lawofficeresult":"0","fuzeren":"","lawofficenature":"","lawofficename":"","areacode":"","permit":"","creditnumber":"","page":1,"pagesize":20}

    @property
    def default_jheader(self) -> dict:
        return {
            'User-Agent': generate_user_agent(os=('win', )),
            'Content-Type': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }