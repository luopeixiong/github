# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 14:54:39 2017

@author: luopx
"""

import re
import requests
from user_agent import generate_user_agent
from scrapy import Selector

headers = {'User-Agent': generate_user_agent(os=('win',))}
url = 'http://www.mca.gov.cn/article/sj/tjbz/a/2017/1123/11233.html'
res = requests.get(url,headers=headers)

response = Selector(res)
trees = response.xpath('//tr[td[@class="xl6529709" or @class="xl6929709" or @class="xl6929709"]][position()>1]')
first_regex = re.compile('\d{2}0{3}')  #  省市直辖区
second_regex = re.compile('\d{3}[1-9]0{2}')  # 市级地区
area_1_levle = ''
area_2_level = ''
area_code = {}
LEVEL = 2

def get_key(dicts, keys, result):
    _re = dicts.copy()
    for _key in keys:
        _re = _re.get(_key)
    if _re:
        _re.update(result)
        return _re
    else:
        return result

def area_codes()->'qqq':
    for tree in trees:
        code = tree.xpath('./td[2]/text()').extract_first()
        area = tree.xpath('./td[3]/text()').extract_first()
        if not code:
            continue
        _result = {area: code}
        if first_regex.match(code):
            #  省级地区
            LEVEL = 1
            area_1_level = area
            result = get_key(area_code, [area_1_level], _result)
            area_code[area_1_level] = result
        elif second_regex.match(code):
            #  市直辖区
            LEVEL = 2
            area_2_level = area
            result = get_key(area_code, [area_1_level, area_2_level], _result)
            area_code[area_1_level][area_2_level] = result
        else:
            if LEVEL == 1:
                result = get_key(area_code, [area_1_level], _result)
                area_code[area_1_level] = result
            else:
                result = get_key(area_code, [area_1_level, area_2_level], _result)
                area_code[area_1_level][area_2_level] = result
    return area_code


if __name__ == '__main__':
    result = area_codes()
    print(result)
