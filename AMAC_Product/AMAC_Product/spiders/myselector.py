#-*- coding:utf-8 -*-


import re
import urllib.parse
from itertools import chain
import datetime

class Selector(object):
    def __init__(self):
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
            invalid_chars = {'\t','\r','\n','[',']',' ','--','\u3000','\xa0'}
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
if __name__ == "__main__":
    pass
#    a = Selector.changdt(True)
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