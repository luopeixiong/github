# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import sys,csv
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

BASE_DIR = os.getcwd()

from pipeline import Pipeline


class DistributedspiderPipeline(Pipeline):
    pass


class CsvPipeline(object):

    def __init__(self):
        path = os.path.join(BASE_DIR,'out_file.csv')
        self.f = open(path,'w+',newline='')
        self.writer = csv.writer(self.f)
        self.nums = 1

    def process_item(self,item,spider):
        if self.nums == 1:
            self.nums +=1
            keys = tuple(item['result'].keys())
            self.writer.writerow(keys)
        values = tuple(item['result'].values())
        print(values)
        self.writer.writerow(values)
        return item

    def close_spider(self, spider):
        self.f.close()

