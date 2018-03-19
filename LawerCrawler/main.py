# -*- coding: utf-8 -*-
from scrapy.cmdline import execute
import os
BASEDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASEDIR)
def run():
    project_name = "LawerCrawler"
    spider_name = "lawyerspider"
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

if __name__ == '__main__':
    run()