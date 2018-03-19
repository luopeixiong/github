from lxml import etree
from settings import RULE


class HtmlParser(object):
    def __init__(self,response):
        self.response = response

    def parser(self,data_name,rule_name="Xpath"):
        tree = etree.HTML(self.response)
        data = tree.xpath(RULE["Xpath"][data_name])
        if not rule_name:
            pass    #暂空

        return data