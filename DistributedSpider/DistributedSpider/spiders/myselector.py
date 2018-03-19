# -*- coding:utf-8 -*-

import re
import urllib.parse
#from itertools import chain
import datetime
#import random
from user_agent import generate_user_agent
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
import requests
import os
import execjs
import tabula
from io import BytesIO
import scrapy
from copy import copy
from array import array
import pandas as pd

DEBUG = False

try:
    from win32com import client as wc
except:
    win_flag = False
#from imp import reload
import pandas as pd
s = requests.Session()
import time
import logging

def rr(x):
    if isinstance(x,float):
        return ''
    else:
        return x

def pdf_to_html(url:'path or url',encoding='gbk'):
    df2 = tabula.read_pdf(url,pages='all',encoding='gbk')
    q = copy(df2.values[1:])
    max_size = len(q)-2
    for index,item in enumerate(q):
        if isinstance(item[0],float):
            up,down = index,index
            while True:
    #             print(index_copy)
                if up>=max_size:
                    up=max_size-1
                    break
                up += 1
                if isinstance(q[up][0],str):
                    break
            while True:
    #             print(index)
                if down<=0:
                    down=0
                    break
                down -= 1
                if isinstance(q[down][0],str):
                    break
                
            flag = True
            for index,value in enumerate(item):
                if index == 0:
                    continue
                if type(value) == type(q[up][index]):
                    flag=False
                    break
            result=[up,down][flag==False]
            q[result] = [rr(x)+rr(y) for x,y in zip(q[result],item)]
            q = filter(lambda x:isinstance(x[0],str),q)
            response = scrapy.Selector(text = pd.DataFrame(list(q)).to_html())
            return response

logger = logging.getLogger(__name__)
_parterrn = re.compile('^(?P<key>.*)\[(?P<index>.*?)\]').search
class Re(object):
    @staticmethod
    def regex1(Regex, txt):
        result = re.compile(Regex, re.S).search(txt)
        if result:
            return result.group(1)
        else:
            return None

    @staticmethod
    def regex0(Regex, txt):
        result = re.compile(Regex, re.S).search(txt)
        if result:
            return result.group(0)
        else:
            return None


def counttime(cls):
    now = time.time()

    def fo(*args, **kwargs):
        q = cls(*args, **kwargs)
        print('解析文件花费{0:<2.2}秒'.format(time.time() - now))
        return q

    return fo


class Selector(object):
    def __init__(self):
        pass

    @classmethod
    def pdfparse(self, url):
        try:
            if url:
                res = s.get(url, headers={"user-agent": generate_user_agent()})
                res.encoding = 'utf-8'
                f = BytesIO()
                f.write(res.content)
                f.seek(0)
                praser = PDFParser(f)
                doc = PDFDocument()
                praser.set_document(doc)
                doc.set_parser(praser)
                doc.initialize()

                if not doc.is_extractable:
                    raise PDFTextExtractionNotAllowed
                else:
                    # 创建PDf 资源管理器 来管理共享资源
                    #                    print("a")
                    rsrcmgr = PDFResourceManager()
                    # 创建一个PDF设备对象
                    laparams = LAParams()
                    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
                    # 创建一个PDF解释器对象
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
                    text = ''
                    # 循环遍历列表，每次处理一个page的内容
                    for page in doc.get_pages():  # doc.get_pages() 获取page列表
                        interpreter.process_page(page)
                        # 接受该页面的LTPage对象
                        layout = device.get_result()
                        #text = "".join(map(lambda x:x.get_text().strip(" ") if x.get_text() else "",layout))
                        #print(text)
                        # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等 想要获取文本就获得对象的text属性，
                        for x in layout:
                            if hasattr(x, 'get_text'):
                                results = x.get_text()
                                if results:
                                    text += results.strip('\n')
                    f.close()
                    return text
        except Exception as e:
            print(e)

    @classmethod
    def docparse(self, url):
        if win_flag:
            name = url.split("/")[-1]
            try:
                path1 = os.getcwd() + "\\%s.doc" % name.split(".")[0]
                path2 = os.getcwd() + "\\%s.txt" % name.split(".")[0]
                #        print(path1,path2)
                doc = s.get(url, headers={"user-agent": generate_user_agent()})
                word = wc.Dispatch('Word.Application')
                with open(path1, "wb") as f:
                    f.write(doc.content)
                docment = word.Documents.Open(path1)
                docment.SaveAs(path2, 4)
                docment.Close()
                try:
                    with open(path2) as f:
                        workdoc = f.read()
                except:
                    workdoc = ""
                os.remove(path1)
                os.remove(path2)
                return workdoc
            except Exception as e:
                print(e)
        else:
            print('it\'s only support on win')

    @classmethod
    @counttime
    def _txtparse(self, url):
        if re.search('.*?pdf', url, re.I):
            return self.pdfparse(url)
        elif re.search('.*?docx?', url, re.I):
            if win_flag:
                return self.docparse(url)
            else:
                raise ImportError('it has not install pywin32')

    @classmethod
    def replace_all(self, content):
        content = self.replace_html_tag(content)
        content = self.replace_invalid_html_char(content)
        content = self.replace_invalid_char(content)
        return content

    @staticmethod
    def changdt(content, dt):
        if dt == "int":
            v = int(content) if hasattr(
                content,
                'replace') and content.isdigit() else content if isinstance(
                    content, int) else None
            return v
        elif dt == "float":
            try:
                v = round(float(content), 4)
                return v
            except:
                return None
        if dt == 'str':
            try:
                if content:
                    return str(content)
            except:
                return None
        if dt == "date":
            if content:
                if re.match("\d{4}-\d+-\d+", content):
                    result = content.split("-")
                    return "{0:0>4}-{1:0>2}-{2:0>2}".format(
                        result[0], result[1], result[2])
                else:
                    return content
        else:
            return content

    @classmethod
    def select_content(self, content, config, response=None):
        selector_type = config['t']
        tag = config['v']
        retag = config.get('re','.*?')
        try:
            if hasattr(content, 'text'):
                body = content.text
            else:
                body = content
        except Exception as e:
            print(e)
        try:
            if selector_type == 'body':
                body = response.request.body.decode(response.encoding)
                data = urllib.parse.parse_qs(body)
                data = dict((k, v if len(v) > 1 else v[0])
                            for k, v in urllib.parse.parse_qs(body).items())
                v = data.get(tag)
                if v:
                    return v
                else:
                    raise KeyError('body data has not attribute %s' % tag)
            if selector_type == 'meta':
                return response.meta[tag]

           # 废弃 留存 
           # elif selector_type == "json":
           #     if isinstance(content,dict):
           #         pass
           #     else:
           #         content = json.loads(content)
           #     print(content)
           #     for i in tag.split("/"):
           #         if isinstance(content,dict):
           #             pass
           #         else:
           #             raise TypeError("typeError")
           #         content = content[i] if i in content else ''
           #     v = content
           #     return v

            # 需要修改  正常dict用/分割
            # 遇到list 遍历获取
            elif selector_type == "json":
                if isinstance(content,(dict,list)):
                    pass
                elif hasattr(content,'text'):
                    try:
                        content = json.loads(response.text)
                    except:
                        content = execjs.eval(content.text)
                else:
                    raise TypeError('js can\'t decode <Class %s at x%s>' % content.__class__,id(content))
                for _tag in tag.split("/"):
                    _flag = _parterrn(_tag)
                    if _flag:
                        _t = _flag.group('key')
                        index = _flag.group('index')
                    # elif re.compile('\[(\d+)\]').match(_tag):
                    #     index = re.compile('\[(\d+)\]').search(_tag).group(1)
                    else:
                        _t = _tag
                        try:
                            del index
                        except:
                            pass
                    if _t:
                        if isinstance(content, dict):
                            content =  content[_t]
                        elif isinstance(content, list) and content and _t in content[0]:
                            content = [c[_t] for c in content]

                    try:
                        if index:
                            try:
                                content = content[int(index)]
                            except IndexError as e:
                                if DEBUG:
                                 logger.info(repr(e))
                    except:
                        pass
                v = content
                return v

            elif selector_type == "json_re":
                if isinstance(content,(dict,list)):
                    pass
                elif hasattr(content,'text'):
                    try:
                        content = json.loads(response.text)
                    except:
                        content = execjs.eval(content.text)
                else:
                    raise TypeError('js can\'t decode <Class %s at x%s>' % content.__class__,id(content))
                for _tag in tag.split("/"):
                    _flag = _parterrn(_tag)
                    if _flag:
                        _t = _flag.group('key')
                        index = _flag.group('index')
                    # elif re.compile('\[(\d+)\]').match(_tag):
                    #     index = re.compile('\[(\d+)\]').search(_tag).group(1)
                    else:
                        _t = _tag
                        try:
                            del index
                        except:
                            pass
                    if _t:
                        if isinstance(content, dict):
                            content =  content[_t]
                        elif isinstance(content, list) and content and _t in content[0]:
                            content = [c[_t] for c in content]

                    try:
                        if index:
                            try:
                                content = content[int(index)]
                            except IndexError as e:
                                if DEBUG:
                                 logger.info(repr(e))
                    except:
                        pass
                content = content or ''
                match = re.compile(retag,re.I).search(content)
                if match:
                    return match.group(1)

            elif 'json_join' in selector_type :
                rep = selector_type.replace('json_join', '')
                if isinstance(content,(dict,list)):
                    pass
                elif hasattr(content,'text'):
                    try:
                        content = json.loads(content.text)
                    except:
                        content = execjs.eval(content.text)
                else:
                    raise TypeError('js can\'t decode <Class %s at x%s>' % content.__name__,id(content))
                for _tag in tag.split("/"):
                    _flag = _parterrn(_tag)
                    if _flag:
                        _t = _flag.group('key')
                        index = _flag.group('index')
                    # elif re.compile('\[(\d+)\]').match(_tag):
                    #     index = re.compile('\[(\d+)\]').search(_tag).group(1)
                    else:
                        _t = _tag
                        try:
                            del index
                        except:
                            pass
                    if _t:
                        if isinstance(content, dict):
                            content =  content[_t]
                        elif isinstance(content, list) and content and _t in content[0]:
                            content = [c[_t] for c in content]

                    try:
                        if index:
                            try:
                                content = content[int(index)]
                            except IndexError as e:
                                if DEBUG:
                                    logger.info(repr(e))
                    except:
                        pass
                v = content or []
                return rep.join(v)
            elif selector_type == "xpath":
                return content.xpath(tag)
            elif selector_type == 'xpath_extract':
                v = content.xpath(tag).extract()
                return v
            elif selector_type == "xpath_first":
                v = content.xpath(tag).extract_first()
                return v
            elif "xpath_join" in selector_type:
                q = selector_type.replace("xpath_join", '')
                v = content.xpath(tag).extract()
                if v:
                    v = q.join(v)
                else:
                    v = None
                return v
            elif selector_type == 'xpathSet':
                v = content.xpath(tag).extract()
                v = set(v)
                return v
            elif 'xpath_re' in selector_type:
                q = selector_type.replace('xpath_re','')
                v = content.xpath(tag)
                if v:
                    if q:
                        return v.re(retag,re.S)
                    else:
                        v = v.re(retag,re.S)
                        if v:
                            return v[0]
            elif selector_type == "css":
                v = content.css[tag]
                if v:
                    return v
            elif selector_type == 'regex1':
                return Re.regex1(tag, body)
            elif selector_type == 'regex0':
                if not hasattr(content,'replace'):
                    content = body
                return Re.regex0(tag, content)
            elif selector_type == "re_first":
                v = re.search(tag, body).group(1)
                return v
            elif selector_type == "re_findall":
                if isinstance(tag, str):
                    v = re.findall(tag, body)
                    return v
                else:
                    return tag.findall(body)
            elif selector_type == "re_groups":
                return re.search(tag, body).groups()
            elif 're_join' in selector_type:
                q = selector_type.replace('re_join', '')
                v = re.compile(tag, re.S).findall(body)
                if v:
                    return q.join(v)
            elif 'splitwith' in selector_type:
                if hasattr(selector_type, 'replace'):
                    b = selector_type.replace('splitwith', '')
                else:
                    raise AttributeError(
                        '%s has not attribute replace' % selector_type)
                if hasattr(content, 'split'):
                    try:
                        return content.split(b)[tag]
                    except IndexError as e:
                        print(e)
                else:
                    raise AttributeError(
                        '%s has not attribute split' % content)
            elif selector_type == "url":
                if hasattr(response, "url"):
                    return response.url
                else:
                    raise AttributeError("url is Not Method")
            elif selector_type == "date":
                #set tag = "%Y-%m-%d %H:%M:%S"
                return datetime.datetime.now().strftime(tag)
            elif selector_type == 'abs':
                return tag
            elif selector_type == 'url_re':
                url = response.url
                v = re.compile(tag,re.S|re.I).search(url)
                if v:
                    return v.group(1)
            elif selector_type == 'url_split':
                if hasattr(response, "url"):
                    return response.url.split('/')[tag]
                else:
                    raise AttributeError("url is Not Method")
            elif selector_type == 'static':
                return content
            elif selector_type == 'response.url':
                return response.url
            elif selector_type == 'url2txt':
                content = urllib.parse.urljoin(tag, content)
                v = self._txtparse(content)
                return v
            elif selector_type == 'page_range':
                page = re.search(tag, body).group(1)
                return range(1, page)
            elif selector_type == '.re':
                v = content.re(tag)
                if v:
                    return v[0]
            elif selector_type == 'response_xpath_first':
                v = response.xpath(tag).extract_first()
                return v
            elif selector_type == 'request_body':
                body = response.request.body.decode('utf-8')
                item = urllib.parse.parse_qsl(body)
                k = {}
                k.update(item)
                return k.get(tag)

        except Exception as e:
            if DEBUG:
                logger.info(repr(e))

    @classmethod
    def select_contents(self, content, config, response=None):
        result = self.select_content(content, config, response=None)
        if callable(config.get(re)):
            return config.get(re)(result)
        else:
            return result

    @staticmethod
    def replace_html_tag(content):
        if hasattr(content, 'replace'):
            return re.subn('<[\s\S]*?>', '', content)[0]
        return content

    @staticmethod
    def replace_invalid_char(content):
        if hasattr(content, 'replace'):
            invalid_chars = {
                '\t', '\r', '\n', '[', ']', ' ', '--', '\u3000', '\xa0', "'",
                "&nbsp",'NaN'
            }
            for char in invalid_chars:
                content = content.replace(char, '')
        elif content is False:
            content = 0
        elif content is True:
            content = 1
        return content

    @staticmethod
    def replace_invalid_html_char(content):
        try:
            if hasattr(content, 'replace'):
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
        except Exception as e:
            print(e)
            return e
        return content

    @staticmethod
    def urljoin(path, url):
        urlp = urllib.parse.urlparse(url)
        return urlp.scheme + '://' + urlp.netloc + '/' + path

    @staticmethod
    def urljoin2(path, url):
        urlp = urllib.parse.urlparse(url)
        return urlp.scheme + '://' + urlp.netloc + path

    @classmethod
    def headers(self):
        return {'User-Agent': generate_user_agent()}

    @staticmethod
    def datelist(start, end, formats="%Y%m%d"):
        # beginDate, endDate是形如‘20160601’的字符串或datetime格式
        date_l = [
            datetime.datetime.strftime(x, formats)
            for x in list(pd.date_range(start=start, end=end))
        ]
        return date_l

if __name__ == "__main__":

    pass
#    a = Selector._txtparse('http://www.szse.cn/UpFiles/cfwj/2002-05-09_000013580.doc')
#    print(a)
#    a = Selector.pdfparse("http://static.sse.com.cn/disclosure/listedinfo/announcement/c/2017-08-30/603303_20170830_1.pdf")
#    print(a)
#    a = Selector()
#    a = a.headers()
#    print(a)
#    print(type(a))
#    print(a)
#    a = Selector.replace_all('''<td style="text-align:center">男</td>
#              <td style="text-align:center">南山区
#
#              </td>
#              <td style="text-align:center">
#
#              			<a href="/lawfirm/12e61b22fa6045deb55ca13d8ac5777c" target="_blank">广东君言律师事务所</a>
#''')
#    print(a)
    # import requests
    # import json
    # url = 'http://ba.amac.org.cn/pages/amacWeb/user!list.action?filter_LIKES_MPI_NAME=&filter_LIKES_AOI_NAME=&filter_LIKES_MPI_PRODUCT_CODE=&filter_GES_MPI_CREATE_DATE=&filter_LES_MPI_CREATE_DATE=&page.searchFileName=publicity_web&page.sqlKey=PAGE_QH_PUBLICITY_WEB&page.sqlCKey=SIZE_QH_PUBLICITY_WEB&_search=false&nd=1513235188288&page.pageSize=50&page.pageNo=2&page.orderBy=MPI_CREATE_DATE&page.order=desc'
    # res = requests.get(url)
    # url = Selector.select_content(json.loads(res.text)['result'],{'v':'MPI_NAME[1]','t':'json'},res)
    # print(url)