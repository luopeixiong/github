# -*- coding: utf-8 -*-
from scrapy.cmdline import execute
import os

if __name__ == '__main__':
    project_name = "AMAC_Product"
    spider_name = "private_fund"
    if not os.path.exists(project_name):
        print("Please Edit the project files and Run again!!!")
        s = "scrapy startproject %s" % project_name
        execute(s.split())
    else:
        print("Start Crawling!!!")
        path = os.getcwd() 
        os.chdir(path+"/"+project_name) 
        s = "scrapy crawl %s" % spider_name
        execute(s.split())