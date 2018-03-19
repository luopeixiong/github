# -*- coding: utf-8 -*-
"""
help文件
"""


from user_agent import generate_user_agent as ua
import urllib.parse
import scrapy
from scrapy.http.response.html import HtmlResponse
import re
from collections import Iterable
import json
from myselector import Selector as S



Referer = ''

def trytime_(response):
    if response.meta.get('maxtrys'):
        response.meta['maxtrys'] += 1
    else:
        response.meta['maxtrys'] = 1
def gettrytime(response,maxtry=3):
    trytime_(response)
    if response.meta['maxtrys']<maxtry:
        return True
def checkTimeError(response,maxtry=3,txt = 'setURL'):
    flag = gettrytime(response,maxtry)
    if flag and txt in response.text:
        request = response.request.replace(dont_filter = True)
        print(request)
        return request
    elif response.status in [403]:
        request = response.request.replace(dont_filter = True)
        return request

class SzseItem(scrapy.Item):
    # define the fields for your item here like:
    result = scrapy.Field()
    keys = scrapy.Field()
    db = scrapy.Field()
    conn = scrapy.Field()

RegexModle = re.S
def hdr():
    return {'User-Agent':ua(os=('win','linux','mac')),
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            }

def doRequest(url,method='GET',body='',headers=hdr(),headersupdate={},meta=None,encoding='UTF-8',dong_filter=False,
            errback=None,priority=0,callback='self.parse'):
    if headersupdate:
        headers.update(headersupdate)
    return {'url':url,
            'method':method,
            'body':body,
            'headers':headers,
            'encoding':encoding,
            'dont_filter':dong_filter,
            'meta':meta,
            'errback':errback,
            'callback':callback,
            'priority':priority,
            }




def response_decode(response,decoding='utf-8',flag=False):
    if decoding!='utf-8':
        if isinstance(response,HtmlResponse):
            response =  response.replace(body=response.body.decode(decoding))
        else:
            raise TypeError('response has not attribute replace,please check response is class HtmlResponse')
    return response
def response_replace(response,_replace=None,flag=False):
    if isinstance(response,HtmlResponse):
        if _replace:
            if isinstance(_replace,dict):
                _replace = _replace.items()
            for i in _replace.items:
                Regex = re.compile(i[0],flag=RegexModle)
                response = response.replace(body=Regex.sub(i[1],response.text))
    return response


def response_model(response,types,flag=False):
    if types == 'json':
        if hasattr(response,'text'):
            response = response.text
        response =  json.loads(response)
    return response

def response_Regex(response,_Regex,flag=False):
    if _Regex:
        Regex = re.compile(_Regex,flags = RegexModle)
        _response = Regex.search(response.text)
        if hasattr(_response,'group(1)'):
            _response = _response.group(1)
        else:
            raise ValueError('check Regex:%s'%_Regex)
        response =  response.replace(body = _response)
    return response

def _response(response,_replace,_Regex='',types='html.Parse',decoding='utf-8',flag=False):
    if flag is False:
        return response
    response = response_decode(response,decoding)
    response = response_replace(response,_replace)
    response = response_Regex(response,_Regex)
    response = response_model(response,types)
    return response

def text2Html(text):
    try:
        a = scrapy.Selector(text=text)
        return a
    except Exception as e:
        print(e)

class other(object):
    def __init__(self):pass

    def body2dict(self,response,decode='utf-8'):
        body = response.request.body.decode(decode)
        items = body.split('&')
        data={}
        for item in items:
            _item = item.split('=')
            data[_item[0]] = urllib.parse.unquote(_item[1])
        return data

    def configParse(self,configs,_response,response=None):
        item = SzseItem()
        if isinstance(configs,dict):
            configs = [configs]
        for _configs in configs:
            #迭代可能多个的configs
            if _configs.get('flag') is None:
                _configs['flag'] = True
            if _configs['list']['v'] and _configs['flag']:
                res = S.select_content(_response,_configs['list'])
            elif isinstance(_response,list):
                res = _response
            else:
                #list(response)   ----让response可迭代
                res = [_response]
            if res:
                for _res in res:
                    #初始化result
                    result = dict()
                    #遍历每个字段提取
                    for config in _configs['data']:
                        k = config['En']
                        result[k] = S.select_content(_res, config, response)
                        result[k] = S.replace_invalid_char(result[k])
                        result[k] = S.replace_invalid_html_char(result[k])
                    if _configs.get('clear'):
                        for config in _configs['clear']:
                            k = config['En']
                            result[k] = S.select_content(result[k],config,response)
                    item['result'] = result
                    item['keys'] = _configs['list']['keys']
                    item['db'] = _configs['list']['db']
                    item['conn'] = _configs['list'].get('conn')
                    #传递pipelin处理item字段
                    if result[_configs['list']['check']]:
                        yield item

'''-----------------------------------------------------------------------------------------------------------'''

def szse_data(page,CATALOGID,tabkey='tab1',tab1PAGECOUNT='',tab1RECORDCOUNT=''):
    data = {
            'ACTIONID':'7',
            'AJAX':'AJAX-TRUE',
            'CATALOGID':CATALOGID, #1110,1105,1273,1277,1928,1945,1795,1793,SSGSGMXX{'tab1','tab2'}
            'TABKEY':tabkey,
            'tab1PAGENO':str(page),
            'tab1PAGECOUNT':'',
            'tab1RECORDCOUNT':'',
            'REPORT_ACTION':'navigate',
    }
    postdata = urllib.parse.urlencode(data)
    return postdata



def startConfigs(urls):
    page = 1
    for _url in urls:
        for CATALOGID,configKey in Start.items():
            postdata = szse_data(page,CATALOGID)
            meta = {'CATALOGID':CATALOGID,'configKey':configKey,'page':1}
            kwarg = ('self.parse1',doRequest(url=_url,method='post',meta=meta,body=postdata))
            yield kwarg
            if CATALOGID in ['SSGSGMXX','1793_ssgs']:
                postdata = szse_data(page,CATALOGID,tabkey='tab2')
                kwarg = ('self.parse1',doRequest(url=_url,method='post',meta=meta,body=postdata))
                yield kwarg


def getUrl1(response,config,formats=None,formats2=None):

    urls = S.select_content(response, config, response)
    if urls:
        urlList = []
        for url in urls:
            if formats:
                urlList.append(formats.format(url))
            else:
                urlList.append(formats2%url)
    return urlList

def getUrl2(response, config,formats=None,formats2=None):
    urls = S.select_content(response, config, response)
    if urls:
        urlList = []
        for url in urls:
            if formats:
                urlList.append(formats.format(*url))
            else:
                urlList.append(formats2%url)
    return urlList

def nextpages(response,configs,formats = None,formats2=None):

    flag = len(re.findall('\{[^:]*?\}',formats))
    if flag==1:
        urls = getUrl1(response,configs['url'],formats=formats)
    elif flag>1:
        urls = getUrl2(response,configs['url'],formats=formats)
    else:
        raise ValueError('check configs%s'%configs)
    return urls


def getbody(response,configs):

    formats = configs['dataform']
    q = re.findall('%s',formats)
    if q:
        flag = len(q)
        if flag==1:
            body = getUrl1(response,configs['body']['args'],formats2=formats)
        elif flag>1:
            body = getUrl2(response,configs['body']['args'],formats2=formats)
        else:
            raise ValueError('check configs%s'%configs)
        if body:
            body = list(map(lambda x:eval(x),body))
        else:
            body=''
        return body
    else:
        return ''

def wap(func):
    def fo(*args,**kwargs):
        result = getbody(*args,**kwargs)
        if result:
            result = func(result)
        else:
            result = ''
        return result
    return fo


def p2(body):
    page = int(body[0]['tab1PAGENO'])
    page+=1
    tpage = int(body[0]['tab1PAGECOUNT'])
    bodys = []
    if page<tpage:
        _body = body[0].copy()
        _body['tab1PAGENO'] = str(page)
        bodys.append(urllib.parse.urlencode(_body))
    return bodys

def p1(body):
    bodys = []
    if body:
        for i in body:
            bodys.append(urllib.parse.urlencode(i))
        return bodys
    else:
        return ['']