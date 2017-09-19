#-*- coding:utf-8 -*-


import re
import urllib.parse
from itertools import chain
import datetime

class Selector(object):
    def __init__(self):
        pass
    
    
    @staticmethod
    def select_content(content,config):
        selector_type = config['type']
        tag = config['value']
        if content:
            try:
                if hasattr(content,'text'):
                    body = content.text
                else:
                    body = content
            except Exception as e:
                print(e)
        else:
            content = ''
        try:
            if selector_type == "json":
                for i in tag:
                    if isinstance(content,dict):
                        pass
                    else:
                        raise TypeError("typeError")
                    content = content[i] if i in content else ''
                v = content
                if v is None:
                    return ''
                else:
                    return str(v)
            if selector_type == "xpath":
                v = content.xpath(tag).extract()
                if v:
                    v = v[0]
                    return v
            if selector_type == "css":
                v = content.css[tag]
                if v:
                    return v
            if selector_type == "re_first":
                v = re.search(tag,body)
                if hasattr(v,"group"):
                    v = v.group(0)
                else:
                    return ''
            if selector_type == "re_findall":
                v = re.findall(tag,body)
                return v
            if selector_type == "url":
                if hasattr(content,"url"):
                    return content.url
                else:
                    raise AttributeError("url is Not Method")
            if selector_type =="date":
                #set tag = "%Y-%m-%d %H:%M:%S"
                return datetime.datetime.now().strftime(tag)
            if selector_type == "getfmeta":
                return content.meta[tag]
        except Exception as e:
            print(e)
            
    @staticmethod
    def replace_invalid_char(content):
        invalid_chars = {'\t','\r','\n','[',']',' ','--','\u3000','\xa0'}
        for char in invalid_chars:
            content = content.replace(char,'')
        return content
    @staticmethod
    def replace_invalid_html_char(content):
        try:
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
if __name__ == "__main__":
    a = Selector.select_content({"aa":{"aaa":111}},{"type":"json","value":("aa","aaa")})
    print(a)