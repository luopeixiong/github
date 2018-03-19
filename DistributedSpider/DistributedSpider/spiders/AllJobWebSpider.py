# coding:utf-8

import json,re,urllib.parse,sys, os, collections
from functools import wraps

import scrapy
from jsonpath import jsonpath
from user_agent import generate_user_agent


class Item(scrapy.Item):
    result = scrapy.Field()
    db = scrapy.Field()
    check = scrapy.Field()
    keys = scrapy.Field()

class Headers(object):

    def headers(self,*args,**kwargs):
        if kwargs:
            dic = dict(kwargs)
        else:
            dic = {}
        dic.update({'User-Agent': generate_user_agent(os=('win',))})
        return dic


class ZhaopinSpider(scrapy.Spider, Headers):
    name = 'zhaopingCom'
    start_urls = ['http://company.zhaopin.com/beijing/']
    check_regex = re.compile('(FlashVars)',re.I).search
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url,
                headers=self.headers(),
                dont_filter=True,
                callback=self.get_citys)
            return

    def check_response(func):
        @wraps(func)
        def filter_r(self, response):
            match = self.check_regex(response.text)
            if match:
                if response.meta.get('max_time2_try', 0) < 10:
                    response.meta['max_time2_try'] = response.meta.get('max_time2_try', 0) + 1
                    print('its invaild response find %s' % match.group(1))
                    yield response.request.replace(dont_filter=True)
            else:
                result = func(self, response) 
                try:
                    for _r in result:
                        yield _r  
                except:
                    print(result)
        return filter_r

    @check_response
    def get_citys(self, response):
        citys_gen = (response.urljoin(url) for url in response.xpath('//*[@id="city"]/*//@href').extract())
        for url in citys_gen:
            yield scrapy.Request(url,
                headers=self.headers(Referer=None),
                dont_filter=True,
                callback=self.get_industry)
            return

    @check_response
    def get_industry(self, response):
        industry_gen = (response.urljoin(url) for url in response.xpath('//*[@id="industry"]/*//@href').extract())
        for url in industry_gen:
            fmt = url + 'p{page}/'
            yield scrapy.Request(url,
                headers=self.headers(),
                meta={'fmt':fmt},
                callback=self.city_com_in)
            return

    def get_totalpage(self, response):
        match = response.xpath('//span[contains(text(),"共")]/text()').re("共(\d+)页")
        return int(match[0]) if match else 1


    def nextpage(self, response, perpage = 16):
        page = response.meta.get('page', 1)
        totalpage = response.meta.get('totalpage',self.get_totalpage(response))
        if page < totalpage:
            max_n = min(page + 16, totalpage)
            for _p in range(page+1, max_n+1):
                yield response.request.replace(url=response.meta['fmt'].format(page=_p))
                return

    def com_url(self, response):
        urls = (response.urljoin(url) for url in response.xpath('//*[@class="result-jobs"]//div/a/@href').extract())
        for url in urls:
            yield scrapy.Request(url,
                headers=self.headers(),
                callback=self.com_detail)
            return

    def factor(func):
        pass

    @check_response
    def city_com_in(self, response):
        # yield from self.nextpage(response)
        # yield from self.com_url(response)
        yield from  self.zhilian_all_list(response)


    def zhilian_com_parse(self, response):
        pass

    def zhilian_all_list(self, response):
        for i in response.xpath('//*[@class="result-jobs"]//li[position()>1]/div'):
            item = Item()
            item['result'] = i.xpath('string(./*[1])').extract_first(),i.xpath('string(./*[2])').extract_first(),\
            i.xpath('string(./*[3])').extract_first(),i.xpath('string(./*[4])').extract_first()
            yield item

    def zhilian_job_parse(self, response):
        pass

    @check_response
    def com_detail(self, response):
        print(response.text)

class Selector_u(object):

    def xpath(self, response, path):
        return response.xpath(path)

    def xpath_first(self):
        return self.xpath(response,path).extract_first()

    def xpath_join(self, response, path, sep=''):
        return 'sep'.join(self.xpath(response).extract())

    def json_path(self, JS, path):
        if JS is False:
            return False
        else:
            return jsonpath(JS, path)

    def json_re(self,JS,path, regex):
        result = self.jsonpath(JS, path)
        if not result:
            pass

    def get_content(self, response):
        if response.hasattr('text'):
            content = response.text
        elif isinstance(response, str):
            content = response
        try:
            return json.dumps(response, ensure_ascii=False)
        except:
            return ''

    def findall(self, content, regex):
        return regex.findall(content)

    def re_search(self, response, regex):
        content = self.get_content(response) 
        return self.match(content, regex)

    def match(self, content, regex):
        match = regex.search(content)
        return match.group(1) if match else None

    def re_findall(self, response, regex):
        content = self.get_content(response)
        return self.findall(content)

    def replace_invaild(self, content):
        if not isinstance(content, str):
            return

        chars = {
                    'nbsp': ' ',
                    '160': ' ',
                    'lt': '<',
                    '60': '<',
                    'gt': '>',
                    '62': '>',
                    'amp': '&',
                    '38': '&',
                    'quot': '"',
                    '34': '"',
                }
        re_char_entity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_char_entity.search(content)
        while sz:
            key = sz.group('name')
            try:
                content = re_char_entity.sub(chars[key], content, 1)
                sz = re_char_entity.search(content)
            except KeyError:
                content = re_char_entity.sub('', content, 1)
                sz = re_char_entity.search(content)
        return content




