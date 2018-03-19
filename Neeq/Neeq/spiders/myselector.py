#-*- coding:utf-8 -*-


import re
import urllib.parse
#from itertools import chain
import datetime
#import random
from user_agent import generate_user_agent
from pdfminer.pdfparser import PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
import requests
import os
from win32com import client as wc
#from imp import reload

s = requests.Session()
class Selector(object):
    def __init__(self):
        pass
    @staticmethod
    def pdfparse(url=None,res=None,name=None):
        path1 = os.getcwd()+"\\%s.pdf"%name.split(".")[0]
        if url:
            res = s.get(url,headers = {"user-agent":generate_user_agent()})
            
    #        path2 = os.getcwd()+"\\%s.txt"%name.split(".")[0]
            print(path1)
        elif res:
            res = res
        with open(path1,'wb') as f:
            f.write(res.content)
        f =  open(path1,'rb')
        praser = PDFParser(f)
        doc = PDFDocument()
        praser.set_document(doc)
        doc.set_parser(praser)
        f.close()
        doc.initialize()
        if not doc.is_extractable:
            raise PDFTextExtractionNotAllowed
        else:
            # 创建PDf 资源管理器 来管理共享资源
            rsrcmgr = PDFResourceManager()
            # 创建一个PDF设备对象
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            # 创建一个PDF解释器对象
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            text = ''
            # 循环遍历列表，每次处理一个page的内容
            for page in doc.get_pages(): # doc.get_pages() 获取page列表
                interpreter.process_page(page)
                # 接受该页面的LTPage对象
                layout = device.get_result()
                #text = "".join(map(lambda x:x.get_text().strip(" ") if x.get_text() else "",layout))
                #print(text)
                # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等 想要获取文本就获得对象的text属性，
                for x in layout:
                    results = x.get_text()
                    if results:
                        text = text+results.strip('\n')
            return text
    @staticmethod
    def docparse(url,name):
        path1 = os.getcwd()+"\\%s.doc"%name.split(".")[0]
        path2 = os.getcwd()+"\\%s.txt"%name.split(".")[0]
        
        doc  = s.get(url,headers = {"user-agent":generate_user_agent()})
        word = wc.Dispatch('Word.Application')
        with open(path1,"wb") as f:
            f.write(doc.content)
        docment = word.Documents.Open(path1)
        docment.SaveAs(path2, 4)
        docment.Close()
        try:
            with open(path2) as f:
                    workdoc = f.read()
        except:
            workdoc = ""
        return workdoc 
        try:
            os.remove(path1)
        except:
            pass
        try:
            os.remove(path2)
        except:
            pass
    @classmethod
    def replace_all(self,content):
        content = self.replace_html_tag(content)
        content = self.replace_invalid_html_char(content)
        content = self.replace_invalid_char(content)
        return content
    @staticmethod
    def changdt(content,dt):
        if dt == "int":
            v = int(content) if hasattr(content,'replace') and content.isdigit() else content if isinstance(content,int) else None
            return v
        elif dt == "float":
            try:
                v = round(float(content),4)
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
                if re.match("\d{4}-\d+-\d+",content):
                    result = content.split("-")
                    return "{0:0>4}-{1:0>2}-{2:0>2}".format(result[0],result[1],result[2])
                else:
                    return content
        else:
            return content
    @staticmethod
    def select_content(content,config):
        selector_type = config['t']
        tag = config['v']
        try:
            if hasattr(content,'text'):
                body = content.text
            else:
                body = content
        except Exception as e:
            print(e)
        try:
            if selector_type == 'meta':
                return content.meta[tag]
            elif selector_type == "json":
                
                content = content[tag]
                v = content
                if v is None:
                    return ''
                else:
                    return str(v)
            elif selector_type == "xpath":
                return content.xpath(tag)
            elif selector_type  == 'xpath_split':
                v = content.xpath(tag).extract()
                if v:
                    return ",".join(v)
            elif selector_type == "xpath_first":
                v = content.xpath(tag).extract_first()
                return v
            elif selector_type == "xpath_join":
                v = content.xpath(tag).extract()
                if v:
                    v = "".join(v)
                else:
                    v = None
                return v
            elif selector_type == "css":
                v = content.css[tag]
                if v:
                    return v
            elif selector_type == "re_first":
                v = re.search(tag,body)
                if hasattr(v,"group"):
                    v = v.group(0)
                else:
                    return ''
            elif selector_type == "re_findall":
                v = re.findall(tag,body)
                
                return v
            elif selector_type == "url":
                if hasattr(content,"url"):
                    return content.url
                else:
                    raise AttributeError("url is Not Method")
            elif selector_type =="date":
                #set tag = "%Y-%m-%d %H:%M:%S"
                return datetime.datetime.now().strftime(tag)
            elif selector_type =='abs':
                return tag
        except Exception as e:
            print(e)
    @staticmethod
    def replace_html_tag(content):
        if hasattr(content, 'replace'):
            return re.subn('<[\s\S]*?>','',content)[0]
        return content
    @staticmethod
    def replace_invalid_char(content):
        if hasattr(content, 'replace'):
            invalid_chars = {'\t','\r','\n','[',']',' ','--','\u3000','\xa0',"'"}
            for char in invalid_chars:
                content = content.replace(char,'')
        return content
    @staticmethod
    def replace_invalid_html_char(content):
        try:
            if hasattr(content, 'replace'):
                chars = {'nbsp': ' ','160': ' ',
                         'lt': '<', '60':'<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"',
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
        return urlp.scheme+'://'+urlp.netloc+'/'+path
    @staticmethod
    def urljoin2(path, url):
        urlp = urllib.parse.urlparse(url)
        return urlp.scheme+'://'+urlp.netloc+path
    @classmethod
    def headers(self):
        return {'User-Agent':generate_user_agent()}
if __name__ == "__main__":
    pass
#    a = Selector.pdfparse("http://www.szse.cn/UpFiles/cfwj/2017-09-20_002638676.pdf","2017-09-20_002638676.pdf")
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