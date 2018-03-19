# -*- coding: utf-8 -*-

__autor__ = 'Arito'

import sys
# 环境变量
import os

# 获取项目主目录路径  存放了一些关键模块
BASEDIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# 加入环境变量  临时性非全局
sys.path.append(BASEDIR)
sys.path.append('../')
import scrapy
import re
import requests
from scrapy.http.response.text import TextResponse
from scrapy.http.response import Response
import urllib.parse
from user_agent import generate_user_agent
from myselector import Selector as S
import json
import logging
from math import ceil
import time

conn_flag = False   # False使用本地数据库 True 使用公司数据库
start_time = time.time()
proxy_flag = True

'_configs 统一为页面抓取信息配置'

# 睡眠函数  可放入check_response内
def sleep_flag():
    if (time.time() - start_time) % (20 * 60) > (15 * 60):
        print('start_sleep')
        time.sleep(5)
        print('continue')
    else:
        print('pass')


# 日志handler
logger = logging.getLogger(__name__)

# 代理去http/https
_ip = re.compile('\/\/(.*?):')
# 一些页面的pagesize全局变量
PAGESIZE = 100
# 处理json
true = 'true'
# 处理json
false = 'false'
# 最大重试次数
MAX_TIMES = 3





#    error = scrapy.Field()  # 计划


# 删除proxy
def delete_proxy(response: Response):  # 删除不可用代理
    ip = _ip.search(response.meta['proxy']).group(1)
    requests.get(
        "http://10.1.18.35:8000/delete?ip={}".format(ip),
        allow_redirects=False)
    requests.get(
        "http://10.1.18.35:8000/delete?types=2", allow_redirects=False)



# 重庆预计2018年2月23日开启  http://118.178.181.229:8080/Ntalker/lawfirms.aspx?search
# 陕西  http://www.sxsf.gov.cn/public/sxsfww/ggflfw/wsbs/lsfw.html
# 西藏  http://www.xzsft.gov.cn/cxfw/801.jhtml
# 海南   http://www.hainanlawyer.org/index.php?c=content&a=show&id=500   撞库

# 爬虫类
class lawyerspiderSpider(scrapy.Spider):
    '''
    @  --------------页面分析-------------------------

-1- @  -->北京律所列表
    @ -url   http://app.bjsf.gov.cn/tabid/219/Default.aspx
    @  data
    @  connect_type  application/x-www-form-urlencoded; charset=UTF-8
    @  method  POST
    @  extract xpath
    @  schedule -->crawler finished --> DB in the rough

-2- @  -->天津律所
    @ -url http://60.28.163.201:8091/lawyer/lawyeroffice/getLawyerOfficeSearch
    @  data {"lawofficeresult":"0","fuzeren":"","lawofficenature":"","lawofficename":"","areacode":"","permit":"","creditnumber":"","page":{1:page},"pagesize":20}
    @  connect_type application/json
    @  method  POST
    @  extract json
    @  out  -->ID-->url-->Request

    @  -->律所info
    @ -url http://60.28.163.201:8091/lawyer/lawyeroffice/getLawofficeById/{B6BB6C48788F4645B7B6A7483C286413:ID}
    @  method GET
    @  extract json
    @  out  -->Item

    @  -->天津律所列表
    @  http://60.28.163.201:8091/lawyer/lawyer/getLawyerListByHome
    @  connect_type application/json
    @  data {"username":"","usersex":"","lawyertype":"","areacode":"","lawofficename":"","workcardnumber":"","officeresult":"0","beginage":0,"endage":1000,"page":{2:page},"pagesize":20}
    @  method POST
    @  extract json
    @  nextPage True
    @  out  -->ID-->url-->Request

    @  -->律师info
    @  http://60.28.163.201:8091/lawyer/lawyer/getLawyerById/{0c9b8f60-f222-4ec5-82bb-31d1d2de60a3:ID}
    @  method  GET
    @  extract json
    @  out  -->Item
    @  schedule -->crawler in the rough --> DB in the rough
    
-3- @  -->内蒙古 律师事务所
    @  http://110.16.70.5/fwsf_shfwh/lsswsList/{1:page}//////.html
    @  method  GET
    @  extract xpath
    @  nextPage True
    @  out  -->ID-->url-->Request

    @  -->律师事务所info
    @  http://110.16.70.5/fwsf_shfwh/cxzqDetail/{8a901e4c55d401870155d943424f0377:ID}/LS/1.html
    @  method GET
    @  extract xpath
    @  out  -->Item

    @  -->律师 列表
    @  http://110.16.70.5/fwsf_shfwh/lsList/{1:PAGE}//////.html
    @  method GET
    @  extract xpath
    @  nextPage True
    @  out  -->ID-->url-->Request

    @  -->律师 info
    @  http://110.16.70.5/fwsf_shfwh/{cxzqDetail/8a901e4c55b40d6b0155bf9ea73f5475:ID}/LS/2.html
    @  method GET
    @  extract xpath
    @  out  -->Item

-4- @  -->辽宁律师列表
    @  http://218.60.145.124:8080/lnlxoa/govhall/lawyerResult.jsp?pn={1:PAGE}&gender=null&lawyerName=null&licenseNumber=null&licenseCompany=null&jbId=null
    @  method  GET
    @  extract xpath
    @  nextPage True
    @  out  -->ID-->url-->Request

    @  -->律师info
    @  http://218.60.145.124:8080/lnlxoa/govhall/lawyerDetail.jsp?lawyerId={5a2d1a40a4644ff5b78edca5e395b75c:ID}
    @  method  GET
    @  extract xpath
    @  out  -->Item

    @  -->律所列表(无info页)
    @  http://218.60.145.124:8080/lnlxoa/govhall/lawFirmResult.jsp?pn={1:PAGE}&jbId=null&officeName=null&licenseNumber=null&principalname=null&organizationtype=null
    @  method  GET
    @  extract xpath
    @  nextPage True
    @  out  -->Item

-5- @  --> 上海律师列表
    @  https://credit.justice.gov.cn/subjects.jsp?zoneId=All&typeId=10d341aea6674146b36dd23c25090f04&page={2:PAGE}  #typeID 律师
    @  method  GET
    @  extract xpath
    @  nextpage True
    @  out-->ID-->url-->Request

    @  -->律师 info
    @  https://credit.justice.gov.cn/subject.jsp?subjectId={1dd45a7e4d484bb7b5901244015136ad:ID}
    @  method  GET
    @  extract  xpath
    @  out-->Item

    @  -->律所列表
    @  https://credit.justice.gov.cn/subjects.jsp?zoneId=All&typeId=41cb822a0fcd46dda5af6da58283b35d&page={2:PAGE}
    @  method  GET
    @  extract  xpath
    @  nextpage  True
    @  out-->ID-->url-->Request

    @  -->律所info
    @  https://credit.justice.gov.cn/subject.jsp?subjectId={6d48422afa3544c0ab506ae8d1482640:ID}
    @  method  GET
    @  extract  XPATH
    @  out-->Item

-6- @  江苏律师列表
    @  -->http://218.94.1.186:8090/lawyerIntegrity/lawyer/getLawyerListPage
    @  Method:POST
    @  Content-Type:application/json;charset=UTF-8
    @  extract  json
    @  out-->ID-->url-->Request

    @  --> 律师info
    @  http://218.94.1.186:8090/lawyerIntegrity/#/lawyer/lawyerDetail?lawyerid={{C1E7C725-68EC-4B59-A9FC-97157F0883DA}:ID}
    @  Method:GET
    @  extract  json
    @  out-->Item

    @  律所列表
    @  -->http://218.94.1.186:8090/lawyerIntegrity/lawoffice/initLawofficeList
    @  Method:POST
    @  Content-Type:application/json;charset=UTF-8
    @  extract  json
    @  out-->ID-->url-->Request

    @  --> 律师info
    @  http://218.94.1.186:8090/lawyerIntegrity/lawoffice/getLawofficeDetail/{{6936161D-3293-4B7D-A306-87DA365DDCCD}:ID}
    @  Method:GET
    @  extract  json
    @  out-->Item

-7- @  -->浙江律师列表
    @  http://lsgl.zjsft.gov.cn/zjlawyermanager/view/lawyers/LawyerOfficePageList/execute/lawofficeList.do
    @  method POST
    @  connect  application/x-www-form-urlencoded
    @  data  {'pageNo':'2'}
    @  out-->ID-->url-->Request

    @  律所info
    @  http://lsgl.zjsft.gov.cn/zjlawyermanager/view/lawyers/Lawyers/LawyerOfficeShow/lawofficeShow.do?id={2144:id}
    @  method  GET
    @  out-->Item

    @  律师列表
    @  http://lsgl.zjsft.gov.cn/zjlawyermanager/view/lawyers/LawyerPageList/execute/lawyersList.do
    @  method  POST
    @  connect  application/x-www-form-urlencoded
    @  data  {'personname':'','officename':'','button4':'确认查询'','pageNo':'3'}
    @  out-->ID-->url-->Request

    @  律师info
    @  http://lsgl.zjsft.gov.cn/zjlawyermanager/view/lawyers/Lawyers/LawyerShow/lawyersShow.do?id={10517:id}
    @  method  GET
    @  out-->Item

-8- @  -->安徽律所列表
    @  http://flfw.ahsft.gov.cn/lssws/index.jsp?pid=1

    @   律所info
    @   http://flfw.ahsft.gov.cn/lssws/article.jsp?id=6349
    
    @   律师列表
    @   http://flfw.ahsft.gov.cn/ls/index.jsp?pid=1
    
    @   律师info
    @   http://flfw.ahsft.gov.cn/ls/article.jsp?yhid=39702

-9- @  -->福建律师列表
    @  http://www.fjsf.gov.cn/fjsf/lawMemberlawyer.do?task=slist&currentPage={1:page}
    @  method  GET
    @  out-->ID-->url-->Request

    @  律师info
    @  http://www.fjsf.gov.cn/fjsf/lawMemberlawyer.do?task=sselect&fid={63137dcf0a164fcdaf255957bee2046a:id}
    @  method  GET
    @  out-->Item

    @  律所列表
    @  http://www.fjsf.gov.cn/fjsf/lawOffice.do?task=slist&currentPage=1
    @  method  GET
    @  out-->ID-->url-->Request

    @  律所info
    @  http://www.fjsf.gov.cn/fjsf/lawOffice.do?task=sselect&fid={331cf590bf6540b890eb11f0a8daefea:id}
    @  method  GET
    @  out-->Item

-10-@  -->山东律师列表
    @  http://www.sd12348.gov.cn/sftIDC/select/search.do
    @  method  POST
    @  data  {'page':'2', 'areacode':'37','order':'','pageSize':'10','type':'lawyer','flag':'0'}
    @  connect_type  application/x-www-form-urlencoded
    @  extract  json
    @  out-->ID-->url-->Request

    @  律师info
    @  http://sd.12348.gov.cn/sftIDC/lawworkmanage/findPersonnelListByid.do?type=lawyer&id={L305ffGE5xj8YPDKoqY:id}
    @  extract  json
    @  method  GET
    @  out-->Item

    @  律所列表
    @  http://sd.12348.gov.cn/sftIDC/select/search.do
    @  method  POST
    @  data  {'page': '1','areacode': '', 'order': '', 'pageSize': '10', 'type':'lawfirm', 'flag':'1', 'status':'1'}
    @  connect_type  application/x-www-form-urlencoded
    @  extract  json
    @  out-->ID-->url-->Request

    @  律所info
    @  http://sd.12348.gov.cn/sftIDC/lawworkmanage/institutioninfo.do?type=lawyer&orgid={ATLTezz30eOOcmVp1223:id}
    @  extract  json
    @  method  GET
    @  out-->Item

-11-@  江西 past

-12-@  湖北-武汉律师律所信息
    @  http://www.hbsf.gov.cn:8081/application/onlineWeb/lsjjgList?filter_LIKE_sname=&filter_LIKE_zyxkzh=&filter_LIKE_attorney=&filter_LIKE_zyzh=&sortField=xh&sortDir=ASC&pageNumber={10:page}&_searchFlag=_searchFlag
    @  method  GET
    @  xpath
    @  out-->nextpage
    @  out-->Item

-12-@  湖南律师律所信息    -----mark-----   请求响应很慢   ---past---
    @  http://www.rufa.gov.cn/executiveModule
    @  method  POST
    @  data  {  'moduleId':'4028c7895136f9ad0151374c06410006',
                'moduleIndex':'7',
                'lawyerName':'',
                'serviceCode':'',
                'professionCode':'',
                'areaName':'system_manage_sfdq_huns,',  #  直接获取湖南省全部数据
                'workyer':'',
                'isLawyerstatu':'',
                'status':'',# 0 在线 1不在线
                'pageId':'4028c78d519042e60151906825380195',
                'pageNo':'2',
                'pageSize':'9',   # max
                'sort':'ly.pinyin'}
    @  xpath
    @  out-->nextpage
    @  out-->Item

-13-@  广东律师列表info  --数据在json里
    @  http://12348.gdsf.gov.cn/front/servItemDataqueryAction.ered?reqCode=dataTypeQuery&querymethod=10&type=1&curpage={0:page}&limit=9
    @  method  GET
    @  out-->nextpage
    @  out-->Item

    @  律所列表info
    @  http://12348.gdsf.gov.cn/front/servItemDataqueryAction.ered?reqCode=orgQuery&type=1&curpage=0&limit=500 -->全部获取 修改limit
    @  out-->nextpage
    @  out-->Item

-14-@  重庆律师列表   token
    @  http://118.178.181.229:8080/Ntalker/lawyers.aspx   --http://118.178.181.229:8080/Ntalker/lawyers.aspx?search
    @  method  POST
    @  data 获取
    @  http://118.178.181.229:8080/Ntalker/lawfirms.aspx  --http://118.178.181.229:8080/Ntalker/lawfirms.aspx?search
    @  data  获取
    @  method  POST

-15-@  四川律师列表
    @  http://fwpt.scsf.gov.cn/scssfpt/lvshi/lplvshi!lvshiquery.action
    @  method  GET
    @  data  {'firstname': '', 'city': '', 'lspageNo': '2', 'zyzh': ''}   # 有IdCard

    @  律所列表
    @  http://fwpt.scsf.gov.cn/scssfpt/lvshi/lplvshi!lvsuo.action
    @  method  GET
    @  data  {'city': '', 'lvsuoname': '', 'pageNo': '2', 'lvsuoxkzh': ''}

-16-@  贵州    token
    @  http://www.gzsft.gov.cn/channels/11.html?num=1
    @  regex = re.compile('pars\s?=\s*?\"(.*?)\"',re.S|re.I)

-17-@  甘肃律所列表 -- 律师律所同一页   律师无详情页
    @  http://www.gslawyer.com/HdApp/HdBas/HdLawFirmMain.asp?ac=lawfirm&xianqu=0&xingshi=0&w=&page=1
    @  method  GET
    @  out->Request

    @  律所律师info
    @  http://www.gslawyer.com/HdApp/HdBas/HdLawFirmDisp.asp?ac=lawfirm&Id={2636:id}
    @  method  GET
    @  yield Item



    @  http://www.gslawyer.com/HdApp/HdBas/HdLawFirmDisp.asp?ac=lawfirm&Id=2636

-18-@  河北  ---有律所列表    律师是excel文件
    @  http://www.hebsft.gov.cn/wsbsdt/lsyw/lsswscx/  http://apps.hebei.com.cn/wsbsdt/lssousuo.php?pageNow=1
    @  http://apps.hebei.com.cn/wsbsdt/lssousuo.php?pageNow=2


    @  http://att.hebei.com.cn/0/10/76/82/10768238_345173.xls
    @  http://att.hebei.com.cn/0/10/76/82/10768239_976251.xls

-19-@  广西
    @  http://www.gxlawyer.org.cn/searchLawFirm?association=&lawFirmType=&name=&licenseNumber=&x=68&y=15&page=2

    @  律师
    @  http://www.gxlawyer.org.cn/searchLawyer?gender=&practiceScope=43ea076234e049579dd12b9715c6783f&page=1

    @  http://www.gxlawyer.org.cn/searchLawyer?gender=&practiceScope=43ea076234e049579dd12b9715c6783f&page=2

-20-@  宁夏
    @  http://www.nxlawyers.org/lsfind.asp?page=1

-21-@  新疆律所列表    info
    @  http://oa.xjlx.org/html/index1.asp?page={1:page}&page1=0&swsmc=&zyzh=&lxmc=
    
    @  律师info 
    @  http://oa.xjlx.org/html/lscx.asp?page={1:page}
    
    @ 考核信息
    @  http://oa.xjlx.org/html/khcx2.asp?key=641&id=%E5%BC%A0%E5%9B%BD%E6%A0%8B&xyz=0.9156170044154921
    @  remark  未爬取

-22-@  山西律师列表
    @  http://sx.sxlsw.org/lvshiS.aspx?page=1

    @  律师info
    @  http://sx.sxlsw.org/lvshiD.aspx?id=6142

    @  律所
    @  http://sx.sxlsw.org/index.aspx?page=1

    @  律所info
    @  http://sx.sxlsw.org/lvsuoD.aspx?id=704



'''
    name = "lawyerspider"
    state = {}
    website_possible_httpstatus_list = [404, 407, 502, 500, 504]
    start_urls = (
        'http://app.bjsf.gov.cn/tabid/219/Default.aspx',  # 完成crawler 完成数据库
        'http://app.bjsf.gov.cn/tabid/220/Default.aspx',  # 完成crawler  完成数据库
        'http://60.28.163.201:8091/lawyer/lawyeroffice/getLawyerOfficeSearch',  # 完成crawler  完成数据库
        'http://60.28.163.201:8091/lawyer/lawyer/getLawyerListByHome',  # 完成crawler  完成数据库
        'http://110.16.70.5/fwsf_shfwh/lsswsList/%s//////.html',  # 完成crawler  完成数据库
        'http://110.16.70.5/fwsf_shfwh/lsList/%s//////.html',  # 完成crawler  完成数据库
        'http://218.60.145.124:8080/lnlxoa/govhall/lawyerResult.jsp?pn=%s',  # 完成crawler  完成数据库
        'http://218.60.145.124:8080/lnlxoa/govhall/lawFirmResult.jsp?pn=%s',  # 完成crawler  完成数据库
        'http://218.94.1.186:8090/lawyerIntegrity/lawyer/getLawyerListPage',  # 完成crawler  完成数据库
        'http://218.94.1.186:8090/lawyerIntegrity/lawoffice/initLawofficeList',  # 完成crawler  完成数据库
        'http://lsgl.zjsft.gov.cn/zjlawyermanager/view/lawyers/LawyerOfficePageList/execute/lawofficeList.do',  # 完成crawler 完成数据库
        'http://lsgl.zjsft.gov.cn/zjlawyermanager/view/lawyers/LawyerPageList/execute/lawyersList.do',  # 完成crawler 完成数据库
        'http://www.fjsf.gov.cn/fjsf/lawMemberLawer.do?task=slist&year=0',  # 完成crawlerr  完成数据库
        'http://www.fjsf.gov.cn/fjsf/lawOffice.do?task=slist&year=0',  # 完成crawlerr  完成数据库
        'http://www.sd12348.gov.cn/sftIDC/select/search.do',  # 完成crawlerr  完成数据库
        'http://sd.12348.gov.cn/sftIDC/select/search.do',  # 完成crawlerr  完成数据库
        'http://www.hbsf.gov.cn:8081/application/onlineWeb/lsjjgList?pageNumber=1&_searchFlag=_searchFlag',  # 完成crawler  完成数据库
        'http://12348.gdsf.gov.cn/front/servItemDataqueryAction.ered?reqCode=dataTypeQuery&querymethod=10&type=1&curpage=0&limit=100',  # 完成crawlerr  完成数据库
        'http://12348.gdsf.gov.cn/front/servItemDataqueryAction.ered?reqCode=orgQuery&type=1&curpage=0&limit=100',  # 完成crawlerr  完成数据库
        'http://118.178.181.229:8080/Ntalker/lawyers.aspx?search',  # 完成crawler  完成数据库
        'http://118.178.181.229:8080/Ntalker/lawfirms.aspx?search',  # 完成crawler  完成数据库
        'http://fwpt.scsf.gov.cn/scssfpt/lvshi/lplvshi!lvshiquery.action?firstname=&city=&lspageNo=1&zyzh=',  # 完成crawler  完成数据库
        'http://fwpt.scsf.gov.cn/scssfpt/lvshi/lplvshi!lvsuo.action?city=&lvsuoname=&pageNo=1&lvsuoxkzh=',  # 完成crawler  完成数据库
        'http://www.gzsft.gov.cn/channels/11.html?num=1',  # 完成crawler  完成数据库
        'http://www.gslawyer.com/HdApp/HdBas/HdLawFirmMain.asp?ac=lawfirm&xianqu=0&xingshi=0&w=&page=1',  # 完成crawler  完成数据库
        'http://apps.hebei.com.cn/wsbsdt/lssousuo.php?pageNow=1',  # 完成crawler  完成数据库
        'http://www.gxlawyer.org.cn/searchLawyer?gender=&practiceScope=43ea076234e049579dd12b9715c6783f&page=1',  # 完成crawler  完成数据库
        'http://www.nxlawyers.org/lsfind.asp?page=1',  # 完成crawler  完成数据库
        'http://oa.xjlx.org/html/index1.asp?page=1',  # 完成crawler  完成数据库
        'http://oa.xjlx.org/html/lscx.asp?page=1',  # 完成crawler  完成数据库
        'http://sx.sxlsw.org/lvshiS.aspx?page=1',  # 完成crawler  完成数据库
        'http://sx.sxlsw.org/index.aspx?page=1',  # 完成crawler  完成数据库
        'http://flfw.ahsft.gov.cn/lssws/index.jsp?pid=1',  # 完成crawler  完成数据库
        'http://flfw.ahsft.gov.cn/ls/index.jsp?pid=1',  # 完成crawler  完成数据库

        # # 'https://credit.justice.gov.cn/subjects.jsp?zoneId=All&typeId=10d341aea6674146b36dd23c25090f04&page=%s',  # 未完成 https代理
        # # 'https://credit.justice.gov.cn/subjects.jsp?zoneId=All&typeId=41cb822a0fcd46dda5af6da58283b35d&page=%s',  # 未完成 https代理
        # 'http://www.rufa.gov.cn/executiveModule',  #past
        '',

    )
    custom_settings = {
        # 'DOWNLOADER_MIDDLEWARES': {
        #     # 启用中间件
        #     'LawerCrawler.middlewares.RotateUserAgentMiddleware': 401,
        #     # 启用代理
        #     # 'LawerCrawler.middlewares.ProxyMiddleware': 700,
        # },
        # 最大并发
        'CONCURRENT_REQUESTS': 32,
        # 单ip最大并发
        # 'CONCURRENT_REQUESTS_PER_IP': 16,
        #下载延迟
        'DOWNLOAD_DELAY': 0.1,
        # 爬虫策略
        'DEPTH_PRIORITY': 1,
        # 允许的status
        'HTTPERROR_ALLOWED_CODES': [404, 502, 500, 504],
    }
    def start_requests(self):
        page = 1
        for url in self.start_urls:
            if url == 'http://app.bjsf.gov.cn/tabid/219/Default.aspx':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': 1},
                    dont_filter=True,
                    callback=self.bj_law_firm_parse)

            elif url == 'http://app.bjsf.gov.cn/tabid/220/Default.aspx':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': 1},
                    dont_filter=True,
                    callback=self.bj_lawyer_parse)

            elif url == 'http://60.28.163.201:8091/lawyer/lawyeroffice/getLawyerOfficeSearch':
                data = self.tj_first_data(page)
                yield scrapy.Request(
                    url,
                    method='POST',
                    body=data,
                    headers=self.default_jheader,
                    dont_filter=True,
                    priority=100,
                    meta={'page': 1},
                    callback=self.tj_law_firm_parse)
            elif  url == 'http://60.28.163.201:8091/lawyer/lawyer/getLawyerListByHome':
                data = self.tj_lawyer_data(page)
                yield scrapy.Request(
                    url,
                    method='POST',
                    body=data,
                    headers=self.default_jheader,
                    dont_filter=True,
                    priority=100,
                    meta={'page': 1},
                    callback=self.tj_lawyer_parse)

            elif url == 'http://110.16.70.5/fwsf_shfwh/lsswsList/%s//////.html':
                url = url % page
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': 1},
                    priority=100,
                    dont_filter=True,
                    callback=self.nmg_law_firm_parse)
            elif url == 'http://110.16.70.5/fwsf_shfwh/lsList/%s//////.html':
                url = url % page
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': 1},
                    priority=100,
                    dont_filter=True,
                    callback=self.nmg_lawyer_parse)
            elif url == 'http://218.60.145.124:8080/lnlxoa/govhall/lawyerResult.jsp?pn=%s':
                url = url % page
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': 1},
                    priority=100,
                    dont_filter=True,
                    callback=self.liaoning_lawyer_parse)
            elif url == 'http://218.60.145.124:8080/lnlxoa/govhall/lawFirmResult.jsp?pn=%s':
                url = url % page
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': 1},
                    priority=100,
                    callback=self.liaoning_law_firm_parse)
            elif url == 'https://credit.justice.gov.cn/subjects.jsp?zoneId=All&typeId=10d341aea6674146b36dd23c25090f04&page=%s':
                url = url % page
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': 1},
                    dont_filter=True,
                    priority=100,
                    callback=self.sh_lawyer_parse)
            elif url == 'https://credit.justice.gov.cn/subjects.jsp?zoneId=All&typeId=41cb822a0fcd46dda5af6da58283b35d&page=%s':
                url = url % page
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': 1},
                    priority=100,
                    dont_filter=True,
                    callback=self.sh_law_firm_parse)
            elif url == 'http://218.94.1.186:8090/lawyerIntegrity/lawyer/getLawyerListPage':
                data = self.js_lawyer_data(page)
                yield scrapy.Request(
                    url,
                    body=data,
                    method='POST',
                    priority=100,
                    headers=self.default_jheader,
                    meta={'page': 1},
                    dont_filter=True,
                    callback=self.js_lawyer_parse)
            elif url == 'http://218.94.1.186:8090/lawyerIntegrity/lawoffice/initLawofficeList':
                data = self.js_law_firm_data(page)
                yield scrapy.Request(
                    url,
                    body=data,
                    method='POST',
                    priority=100,
                    headers=self.default_jheader,
                    meta={'page': 1},
                    dont_filter=True,
                    callback=self.js_law_firm_parse)
            elif url == 'http://lsgl.zjsft.gov.cn/zjlawyermanager/view/lawyers/LawyerOfficePageList/execute/lawofficeList.do':
                data = urllib.parse.urlencode({'pageNo': '1'})
                yield scrapy.Request(
                    url,
                    body=data,
                    method='POST',
                    dont_filter=True,
                    priority=100,
                    headers=self.default_header,
                    meta={'page': 1},
                    callback=self.zj_law_firm_parse)
            elif url == 'http://lsgl.zjsft.gov.cn/zjlawyermanager/view/lawyers/LawyerPageList/execute/lawyersList.do':
                data = urllib.parse.urlencode({
                    'personname': '',
                    'officename': '',
                    'button4': '确认查询',
                    'pageNo': str(page)
                })
                yield scrapy.Request(
                    url,
                    body=data,
                    method='POST',
                    dont_filter=True,
                    headers=self.default_header,
                    meta={'page': page},
                    priority=100,
                    callback=self.zj_lawyer_parse)
            elif url == 'http://www.fjsf.gov.cn/fjsf/lawMemberLawer.do?task=slist&year=0':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    method='POST',
                    body=urllib.parse.urlencode({'sfname':'','sfnumber1':'','x':'27','y':'7'}),
                    dont_filter=True,
                    priority=100,
                    callback=self.fj_lawyer_parse)
            elif url == 'http://www.fjsf.gov.cn/fjsf/lawOffice.do?task=slist&year=0':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    method='POST',
                    priority=100,
                    body=urllib.parse.urlencode({'sfname':'','sflincese':'','sprincipal':'','x':'17','y':'13'}),
                    dont_filter=True,
                    callback=self.fj_law_firm_parse)
            elif url == 'http://www.sd12348.gov.cn/sftIDC/select/search.do':
                data = urllib.parse.urlencode({
                    'page': str(page),
                    'areacode': '37',
                    'order': '',
                    'pageSize': '10',
                    'type': 'lawyer',
                    'flag': '0',
                    'status': '1'
                })
                yield scrapy.Request(
                    url,
                    body=data,
                    method='POST',
                    headers=self.default_header,
                    meta={'page': page},
                    priority=100,
                    callback=self.sd_lawyer_parse)
            elif url == 'http://sd.12348.gov.cn/sftIDC/select/search.do':
                data = urllib.parse.urlencode({
                    'page': str(page),
                    'areacode': '',
                    'order': '',
                    'pageSize': '10',
                    'type': 'lawfirm',
                    'flag': '1',
                    'status': '1'
                })
                yield scrapy.Request(
                    url,
                    body=data,
                    method='POST',
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    callback=self.sd_law_firm_parse)
            elif url == 'http://www.hbsf.gov.cn:8081/application/onlineWeb/lsjjgList?pageNumber=1&_searchFlag=_searchFlag':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    callback=self.wh_lawyer_firm_parse)
            elif url == 'http://www.rufa.gov.cn/executiveModule':
                data = self.hn_lawyer_data(page)
                yield scrapy.Request(
                    url,
                    body=data,
                    method='POST',
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    headers=self.default_header,
                    callback=self.hn_lawyer_parse)
            elif url == 'http://12348.gdsf.gov.cn/front/servItemDataqueryAction.ered?reqCode=dataTypeQuery&querymethod=10&type=1&curpage=0&limit=9':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    callback=self.gd_lawyer_parse)
            elif url == 'http://12348.gdsf.gov.cn/front/servItemDataqueryAction.ered?reqCode=orgQuery&type=1&curpage=0&limit=9':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    callback=self.gd_law_firm_parse)
            elif url == 'http://118.178.181.229:8080/Ntalker/lawyers.aspx?search':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': 0},
                    dont_filter=True,
                    priority=100,
                    callback=self.cq_lawyer_parse)
            elif url == 'http://118.178.181.229:8080/Ntalker/lawfirms.aspx?search':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': 0},
                    dont_filter=True,
                    priority=100,
                    callback=self.cq_law_firm_parse)
            elif url == 'http://fwpt.scsf.gov.cn/scssfpt/lvshi/lplvshi!lvshiquery.action?firstname=&city=&lspageNo=1&zyzh=':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    priority=100,
                    callback=self.sc_lawyer_parse)
            elif url == 'http://fwpt.scsf.gov.cn/scssfpt/lvshi/lplvshi!lvsuo.action?city=&lvsuoname=&pageNo=1&lvsuoxkzh=':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    callback=self.sc_law_firm_parse)
            elif url == 'http://www.gzsft.gov.cn/channels/11.html?num=1':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    priority=100,
                    callback=self.guizhou_entrance_parse)
            elif url == 'http://www.gslawyer.com/HdApp/HdBas/HdLawFirmMain.asp?ac=lawfirm&xianqu=0&xingshi=0&w=&page=1':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    callback=self.gs_parse)
            elif url == 'http://apps.hebei.com.cn/wsbsdt/lssousuo.php?pageNow=1':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    callback=self.henan_law_firm_parse)
            elif url == 'http://www.gxlawyer.org.cn/searchLawyer?gender=&practiceScope=43ea076234e049579dd12b9715c6783f&page=1':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    callback=self.gx_lawyer_parse)
            elif url == 'http://www.nxlawyers.org/lsfind.asp?page=1':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    callback=self.nx_lawyer_parse)
            elif url == 'http://oa.xjlx.org/html/index1.asp?page=1':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    callback=self.xz_law_firm_info_parse)
            elif url == 'http://oa.xjlx.org/html/lscx.asp?page=1':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    callback=self.xz_lawyer_info_parse)
            elif url == 'http://sx.sxlsw.org/lvshiS.aspx?page=1':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    callback=self.sx1_lawyer_parse)
            elif url == 'http://sx.sxlsw.org/index.aspx?page=1':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    callback=self.sx1_law_firm_parse)
            elif  url == 'http://flfw.ahsft.gov.cn/lssws/index.jsp?pid=1':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    callback=self.ah_law_firm_parse)
            elif  url == 'http://flfw.ahsft.gov.cn/ls/index.jsp?pid=1':
                yield scrapy.Request(
                    url,
                    headers=self.default_header,
                    meta={'page': page},
                    dont_filter=True,
                    priority=100,
                    callback=self.ah_lawyer_parse)

    def tj_lawyer_data(self, page, response=None, pagesize=20):
        return json.dumps({"username":"",
            "usersex":"","lawyertype":"",
            "areacode":"",
            "lawofficename":"",
            "workcardnumber":"",
            "officeresult":"0",
            "beginage":0,
            "endage":1000,
            "page": str(page),
            "pagesize": str(pagesize)})

    def tj_first_data(self, page: int or str, pagesize=PAGESIZE, response=None):
        return json.dumps({
            "lawofficeresult": "0",
            "fuzeren": "",
            "lawofficenature": "",
            "lawofficename": "",
            "areacode": "",
            "permit": "",
            "creditnumber": "",
            "page": str(page),
            "pagesize": str(pagesize)
        })

    # 默认的表头
    @property
    def default_header(self) -> dict:

        return {
            'User_Agent': generate_user_agent(os=('win', )),
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

    # 默认的表头
    @property
    def default_jheader(self) -> dict:
        return {
            'User_Agent': generate_user_agent(os=('win', )),
            'Content-Type': 'application/json'
        }

    # 北京body
    def bj_law_firm_date(self, page: int or str, response=None) -> bytes:
        '''
        @params page: 页数 int
        @parsms rsrf: 令牌 str
        @output body post-data本身 bytes
        '''
        rsrf = response.xpath('//input[@name="__VIEWSTATE"]/@value').extract_first()
        return urllib.parse.urlencode({
            "__EVENTTARGET":
            "ess$ctr740$LawOfficeSearchList$lbtnGoto",
            "__EVENTARGUMENT":
            "",
            "__VIEWSTATE":
            rsrf,
            "__VIEWSTATEENCRYPTED":
            "",
            "ScrollTop":
            "295",
            "__essVariable":
            '{"__scdoff":"1","__ess_pageload":"__ess_setScrollTop();"}',
            "ess$ctr740$LawOfficeSearchList$txtName":
            "",
            "ess$ctr740$LawOfficeSearchList$txtCodeNum":
            "",
            "ess$ctr740$LawOfficeSearchList$txtReponseName":
            "",
            "ess$ctr740$LawOfficeSearchList$ddlType":
            "1",
            "ess$ctr740$LawOfficeSearchList$ddlCountry":
            "-1",
            "ess$ctr740$LawOfficeSearchList$txtPageNum":
            str(page)
        })


    # 江苏body
    def js_law_firm_data(self,
                         page: int or str = 1,
                         pagesize: int or str = 8,
                         response=None):
        return json.dumps({
            "search": {
                "typeList": [-1, -1, -1, -1]
            },
            "input": {
                "page": str(page),
                "pagesize": str(pagesize)
            },
            "sort": [{
                "isSelect": true,
                "isDown": false,
                "name": "nvl(law.lawyernum,0)"
            }, {
                "isSelect": false,
                "isDown": true,
                "name": "o.approve_date"
            }, {
                "isSelect": false,
                "isDown": false,
                "name": "nvl(r.rolenum,0)"
            }]
        })

    # 江苏body
    def js_lawyer_data(self,
                      page: int or str = 1,
                      pagesize: int or str = 8,
                      response=None):
        return json.dumps({
            "sort": [{
                "isSelect": true,
                "isDown": true,
                "name": "nlssort(username,'NLS_SORT=SCHINESE_PINYIN_M')"
            }, {
                "isSelect": false,
                "isDown": false,
                "name": "practice_year"
            }],
            "ageList": [{
                "name": "18~20岁",
                "startAge": 18,
                "endAge": 20,
                "isSelect": false
            }, {
                "name": "20~25岁",
                "startAge": 20,
                "endAge": 25,
                "isSelect": false
            }, {
                "name": "25~35岁",
                "startAge": 25,
                "endAge": 35,
                "isSelect": false
            }],
            "practiceList": [{
                "name": "1~5年",
                "startPractice": 1,
                "endPractice": 5,
                "isSelect": false
            }, {
                "name": "5~10年",
                "startPractice": 5,
                "endPractice": 10,
                "isSelect": false
            }, {
                "name": "10~15年",
                "startPractice": 10,
                "endPractice": 15,
                "isSelect": false
            }],
            "educationList": [{
                "chinaname": "大专",
                "isSelect": false,
                "refid": "5"
            }, {
                "chinaname": "本科",
                "isSelect": false,
                "refid": "4"
            }, {
                "chinaname": "双学士",
                "isSelect": false,
                "refid": "3"
            }, {
                "chinaname": "硕士",
                "isSelect": false,
                "refid": "2"
            }, {
                "chinaname": "博士",
                "isSelect": false,
                "refid": "1"
            }, {
                "chinaname": "其他",
                "isSelect": false,
                "refid": "6"
            }],
            "lawyerTypeList": [{
                "chinaname": "专职律师",
                "refid": "2",
                "isSelect": false
            }, {
                "chinaname": "兼职律师",
                "refid": "1",
                "isSelect": false
            }],
            "punish":
            false,
            "cite":
            false,
            "page":
            str(page),
            "pagesize":
            str(pagesize),
            "languageLevelList": [{
                "rn": 1,
                "chinaname": "初级",
                "refid": "1",
                "isSelect": false
            }, {
                "rn": 2,
                "chinaname": "中级",
                "refid": "2",
                "isSelect": false
            }, {
                "rn": 3,
                "chinaname": "高级",
                "refid": "3",
                "isSelect": false
            }, {
                "rn": 4,
                "chinaname": "专业",
                "refid": "4",
                "isSelect": false
            }]
        })

    def hn_lawyer_data(self, page=1, pagesize=9, response=None):
        return urllib.parse.urlencode({
            'moduleId':
            '4028c7895136f9ad0151374c06410006',
            'moduleIndex':
            '7',
            'lawyerName':
            '',
            'serviceCode':
            '',
            'professionCode':
            '',
            'areaName':
            'system_manage_sfdq_huns,',  #  直接获取湖南省全部数据
            'workyer':
            '',
            'isLawyerstatu':
            '',
            'status':
            '',
            'pageId':
            '4028c78d519042e60151906825380195',
            'pageNo':
            str(page),
            'pageSize':
            str(pagesize),  # max
            'sort':
            'ly.pinyin'
        })

    # 重庆token
    def cq_get_rsrf(self, page, response):
        VIEWSTATE = response.xpath(
            '//input[@name="__VIEWSTATE"]/@value').extract_first()
        VIEWSTATEGENERATOR = response.xpath(
            '//input[@name="__VIEWSTATEGENERATOR"]/@value').extract_first()
        txtx = response.xpath(
            '//input[@name="txtx"]/@value').extract_first()
        return urllib.parse.urlencode({
            '__VIEWSTATE':
            VIEWSTATE,
            '__VIEWSTATEGENERATOR':
            VIEWSTATEGENERATOR,
            'key':
            '',
            'areas':
            '',
            'series':
            '',
            'sex':
            '',
            'Pages':
            str(page),
            'E':
            '',
            'txtx':txtx,
        })

    def cq_start_data(self, page, response):
        VIEWSTATE = response.xpath(
            '//input[@name="__VIEWSTATE"]/@value').extract_first()
        VIEWSTATEGENERATOR = response.xpath(
            '//input[@name="__VIEWSTATEGENERATOR"]/@value').extract_first()
        txtx = response.xpath(
            '//input[@name="txtx"]/@value').extract_first()
        return urllib.parse.urlencode(
            {'__VIEWSTATE':
            VIEWSTATE,
            '__VIEWSTATEGENERATOR':
            VIEWSTATEGENERATOR,
            'txt1': '',
            'txt2': '',
            'txt3': '',
            'txt4': '',
            'Search.x':'42',
            'Search.y':'10',
            'areas':
            '',
            'series':
            '',
            'sex':
            '',
            'Pages':
            str(page),
            'E':
            '',
            'txtx':txtx,
        })

    def cq_start_data2(self, page, response):
        VIEWSTATE = response.xpath(
            '//input[@name="__VIEWSTATE"]/@value').extract_first()
        VIEWSTATEGENERATOR = response.xpath(
            '//input[@name="__VIEWSTATEGENERATOR"]/@value').extract_first()
        txtx = response.xpath(
            '//input[@name="txtx"]/@value').extract_first()
        return urllib.parse.urlencode(
            {'__VIEWSTATE':
            VIEWSTATE,
            '__VIEWSTATEGENERATOR':
            VIEWSTATEGENERATOR,
            'txt1': '',
            'txt2': '',
            'txt3': '',
            'Search.x':'42',
            'Search.y':'10',
            'areas':
            '',
            'organizational':
            '',
            'Pages':
            str(page),
            'E':
            '',
            'txtx':txtx,
        })

    # 重庆token
    def cq_get_rsrf2(self, page, response):
        VIEWSTATE = response.xpath(
            '//input[@name="__VIEWSTATE"]/@value').extract_first()
        VIEWSTATEGENERATOR = response.xpath(
            '//input[@name="__VIEWSTATEGENERATOR"]/@value').extract_first()
        txtx = response.xpath(
            '//input[@name="txtx"]/@value').extract_first()
        return urllib.parse.urlencode({
            '__VIEWSTATE':
            VIEWSTATE,
            '__VIEWSTATEGENERATOR':
            VIEWSTATEGENERATOR,
            'key':
            '',
            'areas':
            '',
            'organizational':
            '',
            'Pages':
            str(page),
            'E':
            '',
            'txtx':txtx})

    # 重庆token
    def get_rsrf(self, response: Response) -> str:
        '''
        @params response:页面响应 Response
        @output rsrf xpath str
        '''
        return response.xpath(
            "//input[@name='__VIEWSTATE']/@value").extract_first()

    # 贵州token
    def guizhou_law_firm_token(self, response):
        token = response.xpath(
            '//span[@id="ajaxElement_3_394"]/following-sibling::script/text()'
        ).re('templateContent=(.*?)\"')
        if token:
            return token[0]
        else:
            raise ValueError('not Found')

    # 贵州token
    def guizhou_page_url(self, response):
        pageUrl = scrapy.Selector(response).re('pageUrl=(\S*?)&')
        return pageUrl[0]

    # 贵州token
    def guizhou_lawyer_token(self, response):
        token = response.xpath(
            '//span[@id="ajaxElement_8_394"]/following-sibling::script/text()'
        ).re('templateContent=(.*?)\"')
        if token:
            return token[0]
        else:
            raise ValueError('not Found')

    # 贵州basebody
    def guizhou_base_data(self,
                          page=1,
                          response=None,
                          ajaxDivID=None,
                          templateContent=None):
        pageUrl = self.guizhou_page_url
        return urllib.parse.urlencode({
            'pageNodeID': '11',
            'pageContentID': '0',
            'pageTemplateID': '6',
            'isPageRefresh': 'False',
            'pageUrl': pageUrl,
            'ajaxDivID': ajaxDivID,
            'templateContent': str(templateContent),
            'pageNum': str(page)
        })

    # 贵州body
    def guizhou_lawyer_data(self, page=1, response=None):
        ajaxDivID = 'ajaxElement_8_394'
        templateContent = self.guizhou_lawyer_token
        return self.guizhou_base_data(
            page, ajaxDivID=ajaxDivID, templateContent=templateContent)

    # 贵州body
    def guizhou_law_firm_data(self, page=1, response=None):
        ajaxDivID = 'ajaxElement_3_394'
        templateContent = self.guizhou_law_firm_token
        return self.guizhou_base_data(
            page, ajaxDivID=ajaxDivID, templateContent=templateContent)

    # 删除 绑定在response内的代理
    def delete_proxy(self, response: Response):
        '''
        @params response
        @目标 删除response proxy
        @output None
        '''
        if response.meta.get('proxy'):
            ip = _ip.search(response.meta['proxy']).group(1)
            requests.get("http://10.1.18.35:8000/delete?ip={}".format(ip))

    # 类判断
    def get_instance(self, args: tuple or list, cls):
        '''
        @params  args:参数列表
        @params cls:类
        @output i  -> if ininstance(i,cls) == True
        '''
        if args:
            for i in args:
                if isinstance(i, cls):
                    return i

    def _get_instance(self, kwargs: dict, cls):
        '''
        @params  args:参数字典
        @params cls:类
        @output i.values()  -> if ininstance(i.values(),cls) == True
        '''
        if kwargs:
            _list = list(kwargs.values())
            return self.get_instance(_list)

    def getfinstance(self, args, kwargs, cls):
        '''
        @params cls -->type or tuple of types
        '''
        flag = self.get_instance(args, cls)
        return flag if flag else self._get_instance(kwargs, cls)

    # 判断失败页面逻辑
    def response_failed(self, response: Response) -> bool:
        '''
        @output Ture-->重新发送请求 False:为正确请求
        @output False-->正确请求，参数传递给 parse
        '''
        if response.status in [404,  407]:
            if response.status in [404, 407]:
                self.delete_proxy(response)
            return True
        elif re.compile('seturl|没有查询到相关结果[\s\S]*没有查询到相关结果', re.I|re.S).search(response.text):
            return True
        else:
            return False

    # logger 日志
    def check_response(func: callable):
        '''
        @parsms:func  装饰函数
        '''

        def decorate(self, *args, **kwargs):
            if not callable(func):
                raise TypeError('<class %s is not a callback func>' %
                                (func.__class__))
            response = self.getfinstance(args, kwargs,
                                         (TextResponse, Response))
            logger.debug('<url:%s body:%s status:%s proxy:%s>' %
                         (response.url, response.request.body, response.status,
                          response.meta.get('proxy')))
            result = func(self, *args, **kwargs)
            if self.response_failed(response):
                request = response.request.replace(dont_filter=True)
                yield request
            else:
                if result:
                    for i in result.__iter__():
                        yield i

        return decorate

    @check_response
    def bj_law_firm_parse(self, response):
        '''
        @ 北京事务所列表页逻辑
        @output Request generator page页
        @output Request generator info页
        '''
        if self.response_failed(response):
            yield self.request_try(response)
            return
        

        urls = response.xpath(
            "//tr[@class='datagrid-Item']/td[1]/a/@href|//tr[@class='datagrid-Alter']/td[1]/a/@href"
        ).extract()
        for url in urls:
            itemid = url.split("=")[-1]
            url = "http://app.bjsf.gov.cn/tabid/238/Default.aspx?itemid={itemid}".format(
                itemid=itemid)
            yield scrapy.Request(
                url,
                method="GET",
                priority=100,
                headers=self.default_header,
                callback=self.bj_lawfirm_info_parse)
        # 废弃代码端
        '''
        # headers = {"user-agent": generate_user_agent()}

        # page = response.meta['page']
        # totalpage = response.meta['totalpage'] if response.meta.get(
        #     'totalpage'
        # ) else float(
        #     response.xpath(
        #         "//span[@id='ess_ctr740_LawOfficeSearchList_lblPageInfo']/text()[2]"
        #     ).extract_first().split("/")[-1]
        # ) if response.xpath(
        #     "//span[@id='ess_ctr740_LawOfficeSearchList_lblPageInfo']/text()[2]"
        # ).extract_first() else 1
        # if page < totalpage and page < totalpage:
        #     page += 1
        #     rsrf = self.get_rsrf(response)
        #     data = self.bj_law_firm_date(page, rsrf)
        #     yield scrapy.Request(
        #         'http://app.bjsf.gov.cn/tabid/219/Default.aspx',
        #         body=data,
        #         method="POST",
        #         headers=self.default_header,
        #         meta={'page': page,
        #               'totalpage': totalpage},
        #         callback=self.bj_law_firm_parse)
        '''
        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            method="POST",
            config={'t': 'xpath_re',
                    'v': '//span[@id="ess_ctr740_LawOfficeSearchList_lblPageInfo"]/text()[2]',
                    're': '\/(\d+)'},
            callback=self.bj_law_firm_parse,
            headers=self.default_header,
            urlfunc=lambda page: 'http://app.bjsf.gov.cn/tabid/219/Default.aspx',
            bodyfunc=self.bj_law_firm_date,
            divmod=1,
            response_type='xpath')
        for req in reqs:
            yield req

    @check_response
    def bj_lawfirm_info_parse(self, response):
        '''
        return Ite,
        '''
        # 错误页面重试
        if self.response_failed(response):
            yield self.request_try(response)
            return

        # 抓取配置
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'dbo.BjLawFirmData',
                'keys': ['LawFirmName'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [{
                'n':
                '事务所中文全称',
                "En":
                "LawFirmName",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblName']/text()",
                't':
                'xpath_first'
            }, {'n':
                '英文名称',
                "En":
                "EnglishFullName",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblEName']/text()",
                't':
                'xpath_first'
            }, {'n':
                '事务所地址',
                "En":
                "LawFirmAddress",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblADDRESS']/text()",
                't':
                'xpath_first'
            }, {'n':
                '邮箱',
                "En":
                "ZipCode",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblMAILCODE']/text()",
                't':
                'xpath_first'
            }, {'n':
                '所在区县',
                "En":
                "AreaName",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblCITY']/text()",
                't':
                'xpath_first'
            }, {'n':
                '主管司法局',
                "En":
                "CompetentAuthorities",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblSUPERINTEND_OFFICE']/text()",
                't':
                'xpath_first'
            }, {'n':
                '社会统一信用代码',
                "En":
                "UnifiedSocialCreditCode",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblBusiness_Code']/text()",
                't':
                'xpath_first'
            }, {'n':
                '发证日期 ',
                "En":
                "IssueDate",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblCERTIFICATE_DATE']/text()",
                't':
                'xpath_first'
            }, {'n':
                '律师事务所主任',
                "En":
                "PersonInCharge",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblDIRECTOR']/text()",
                't':
                'xpath_first'
            }, {'n':
                '总所分所',
                "En":
                "HeadquartersOrBranch",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblIF_HQ']/text()",
                't':
                'xpath_first'
            }, {'n':
                '执业状态',
                "En":
                "StateOfPractice",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblStatus']/text()",
                't':
                'xpath_first'
            }, {'n':
                '状态说明',
                "En":
                "RmarkForState",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblstate_explain']/text()",
                't':
                'xpath_first'
            }, {'n':
                '组织形式',
                "En":
                "OrganizationalForm",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblorganize_format']/text()",
                't':
                'xpath_first'
            }, {'n':
                '注册资金（万元）',
                "En":
                "RegisteredCapital",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblcapital']/text()",
                't':
                'xpath_first'
            }, {'n':
                '办公电话',
                "En":
                "OfficePhoneNumber",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lbltel']/text()",
                't':
                'xpath_first'
            }, {'n':
                '传真',
                "En":
                "FaxNumber",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblfax']/text()",
                't':
                'xpath_first'
            }, {'n':
                '电子邮箱',
                "En":
                "EmailAddress",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblemail']/text()",
                't':
                'xpath_first'
            }, {'n':
                '事务所主页',
                "En":
                "OrgHomePage",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblhomepage']/text()",
                't':
                'xpath_first'
            }, {'n':
                '场所面积',
                "En":
                "Areas",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lbllocation_area']/text()",
                't':
                'xpath_first'
            }, {'n':
                '场所性质',
                "En":
                "AreaNature",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblpartybranch']/text()",
                't':
                'xpath_first'
            }, {'n':
                '党支部负责人',
                "En":
                "PartyInCharge",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblparty_director']/text()",
                't':
                'xpath_first'
            }, {'n':
                '简介',
                "En":
                "BriefIntroduction",
                "v":
                "//span[@id='ess_ctr741_LawOfficeView_lblbrief_introduction']/p/text()",
                't':
                'xpath_first'
            }]
        }]
        # 抓取结果
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

    # 北京body
    def bj_lawyer_data(self, page: int or str, response=None)-> bytes:
        # 获取token
        rsrf = response.xpath(
            "//input[@name='__VIEWSTATE']/@value").extract_first()

        return urllib.parse.urlencode({
            "__EVENTTARGET":
            "ess$ctr706$LawyerSearchList$lbtnGoto",
            "__EVENTARGUMENT":
            "",
            "__VIEWSTATE":
            rsrf,
            "__VIEWSTATEENCRYPTED":
            "",
            "ScrollTop":
            "",
            "__essVariable":
            '{"__scdoff":"1"}',
            "ess$ctr706$LawyerSearchList$txtName":
            "",
            "ess$ctr706$LawyerSearchList$txtCodeNum":
            "",
            "ess$ctr706$LawyerSearchList$txtOfficeName":
            "",
            "ess$ctr706$LawyerSearchList$ddlType":
            "-1",
            "ess$ctr706$LawyerSearchList$txtPageNum":
            str(page)
        })

    @check_response
    def bj_lawyer_parse(self, response):
        '''
        @output Request meta--None method--POST generator 律师列表页 ->self.bj_lawyer_parse
        @output Request meta--None method--GET  generator 律师详情页 ->self.bj_lawyer_info_parse
        '''
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _tag = "//tr[@class='datagrid-Item']/td[1]/a/@href|//tr[@class='datagrid-Alter']/td[1]/a/@href"
        urls = response.xpath(_tag).extract()
        for url in urls:
            itemid = url.split("=")[-1]
            url = "http://app.bjsf.gov.cn/tabid/239/Default.aspx?itemid={itemid}".format(
                itemid=itemid)
            yield scrapy.Request(
                url,
                method="GET",
                headers=self.default_header,
                priority=100,
                callback=self.bj_lawyer_info_parse)

        # 废弃代码段  旧逻辑--留存
        '''
        # rsrf = response.xpath(
        #    "//input[@name='__VIEWSTATE']/@value").extract_first()
        # #        print(rsrf)
        # page = response.meta['page']
        # #            print(self.bjtotalpage )
        # totalpage = response.meta['totalpage'] if response.meta.get(
        #     'totalpage'
        # ) else float(
        #     response.xpath(
        #         "//span[@id='ess_ctr706_LawyerSearchList_lblPageInfo']/text()[2]"
        #     ).extract_first().split("/")[-1]
        # ) if response.xpath(
        #     "//span[@id='ess_ctr706_LawyerSearchList_lblPageInfo']/text()[2]"
        # ).extract_first() else 1

        #        #http://www.bjsf.gov.cn/publish/portal0/tab196/?itemid=1037490
        # if page < totalpage and page < totalpage:
        #     page += 1
        #     data = self.bj_lawyer_date(page, rsrf)
        #     yield scrapy.Request(
        #         'http://app.bjsf.gov.cn/tabid/220/Default.aspx',
        #         body=data,
        #         method="POST",
        #         meta={'page': page,
        #               'totalpage': totalpage},
        #         headers=self.default_header,
        #         callback=self.bj_lawyer_parse)'''
        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            method="POST",
            config={'t': 'xpath_re',
                    'v': '//span[@id="ess_ctr706_LawyerSearchList_lblPageInfo"]/text()[2]',
                    're': '\/(\d+)'},
            callback=self.bj_lawyer_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://app.bjsf.gov.cn/tabid/220/Default.aspx',
            bodyfunc=self.bj_lawyer_data,
            divmod=1,
            response_type='xpath')
        for req in reqs:
            yield req

    @check_response
    def bj_lawyer_info_parse(self, response):
        '''
        @output Item 律师信息 -->pepeline
        '''
        if self.response_failed(response):
            yield self.request_try(response)
            return

        # 配置抓取信息
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'json',
                'db': 'dbo.BjLawyerData',
                'keys': ['LawyerName', 'WebID'],
                'check': 'LawyerName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '姓名',
                    "En": "LawyerName",
                    "v": "//span[@id='ess_ctr742_LawyerView_lblName']/text()",
                    't': 'xpath_first'
                },
                 {
                    'n': '网站ID',
                    "En": "WebID",
                    "v": '//form[@name="Form"]/@action',
                    't': 'xpath_re',
                    're':'itemid=(\d+)'
                },
                {
                    'n': '性别',
                    "En": "Grader",
                    "v": "//span[@id='ess_ctr742_LawyerView_lblSex']/text()",
                    't': 'xpath_first'
                },
                {
                    'n': '头像image',
                    "En": "Photo",
                    "v": "//img[@id='ess_ctr742_LawyerView_Image1']/@src",
                    't': 'xpath_first'
                },
                {
                    'n': '出生日期',
                    "En": "DateOfBirth",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblBirthday']/text()",
                    't': 'xpath_first'
                },
                {
                    'n': '民族',
                    "En": "Nation",
                    "v": "//span[@id='ess_ctr742_LawyerView_lblFolk']/text()",
                    't': 'xpath_first'
                },
                {
                    'n': '学历',
                    "En": "Education",
                    "v": "//span[@id='ess_ctr742_LawyerView_lblEdu']/text()",
                    't': 'xpath_first'
                },
                {
                    'n':
                    '专业',
                    "En":
                    "Speciality",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblSpeciality']/text()",
                    't':
                    'xpath_first'
                },
                {
                    'n': '政治面貌',
                    "En": "PoliticalOutlook",
                    "v": "//span[@id='ess_ctr742_LawyerView_lblParty']/text()",
                    't': 'xpath_first'
                },
                {
                    'n': '宗教信仰',
                    "En": "Religion",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblReligion']/text()",
                    't': 'xpath_first'
                },
                {
                    'n':
                    '是否合伙人',
                    "En":
                    "IsPartner",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblIsCopartner']/text()",
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '首次人合伙人时间',
                    "En":
                    "FristPartncyType",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblFrist_Partncy_Type']/text()",
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '证书类别',
                    "En":
                    "CertificateType",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblCompetency_Type']/text()",
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '资格证取得日期',
                    "En":
                    "QualificationCertificateGetTime",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblCompetency_Date']/text()",
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '首次执业省市',
                    "En":
                    "FirstPracticeArea",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblFirst_City']/text()",
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '首次执业日期',
                    "En":
                    "FirstPracticeTime",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblFirst_Date']/text()",
                    't':
                    'xpath_first'
                },
                {
                    'n': '单位电话',
                    "En": "OfficePhoneNumber",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblHomeTel']/text()",
                    't': 'xpath_first'
                },
                {
                    'n': '邮编',
                    "En": "ZipCode",
                    "v": "//span[@id='ess_ctr742_LawyerView_lblZIP']/text()",
                    't': 'xpath_first'
                },
                {
                    'n':
                    '具有何国永久居留权',
                    "En":
                    "GreenCard",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblGreenCard']/text()",
                    't':
                    'xpath_first'
                },
                {
                    'n': '执业状态',
                    "En": "StateOfPractice",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblStatus']/text()",
                    't': 'xpath_first'
                },
                {
                    'n':
                    '部门',
                    "En":
                    "Department",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblDepartment']/text()",
                    't':
                    'xpath_first'
                },{
                    'n':
                    '所属律所',
                    "En":
                    "LawFirmName",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblLo_Name']/text()",
                    't':
                    'xpath_first'
                },
                {
                    'n': '职务',
                    "En": "Post",
                    "v": "//span[@id='ess_ctr742_LawyerView_lblPost']/text()",
                    't': 'xpath_first'
                },
                {
                    'n':
                    '执业证号',
                    "En":
                    "LicenseNumber",
                    "v":
                    "//span[@id='ess_ctr742_LawyerView_lblCertificate_Code']/text()",
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def tj_law_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        JS = json.loads(response.text)
        items = JS['items']
        for item in items:
            pkid = item['pkid']
            url = 'http://60.28.163.201:8091/lawyer/lawyeroffice/getLawofficeById/%s' % pkid
            yield scrapy.Request(
                url,
                priority=100,
                meta=item,
                callback=self.tj_law_firm_info_parse)

        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            method="POST",
            config={'t': 'json',
                    'v': 'totalcount'
                    },
            callback=self.tj_law_firm_parse,
            headers=self.default_jheader,
            urlfunc=
            lambda page: 'http://60.28.163.201:8091/lawyer/lawyeroffice/getLawyerOfficeSearch',
            bodyfunc=self.tj_first_data,
            divmod=PAGESIZE,
            response_type='json')
        for req in reqs:
            yield req

    @check_response
    def tj_law_firm_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'json',
                'db': 'dbo.TJLawFrimData',
                'keys': ['LawFirmName'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '律所名称',
                    'En': 'LawFirmName',
                    'v':
                    'lawoffice/lawofficename',
                    't': 'json'
                },
                {
                    'n': '组织形式',  # 0 国资所  1 特殊的普通合伙所 2 普通合伙所 3 个人所 4 公职所 5 公司所
                    'En': 'OrganizationalForm',
                    'v':
                    'lawoffice/lawofficenature',
                    't': 'json'
                },
                {
                    'n': '批准日期',
                    'En': 'ApproveDate',
                    'v':
                    'lawoffice/approve_date',
                    't': 'json'
                },
                {
                    'n': '设立资产',
                    'En': 'RegisteredCapital',
                    'v':
                    'lawoffice/asset',
                    't': 'json'
                },
                {
                    'n': '地址',
                    'En': 'LawFirmAddress',
                    'v': 'lawoffice/lawfirmaddress',
                    't': 'json'
                },
                {
                    'n': '电话',
                    'En': 'PhoneNumber',
                    'v': 'lawoffice/tel',
                    't': 'json'
                },
                {
                    'n': '邮编',
                    'En': 'ZipCode',
                    'v':
                    'lawoffice/postcode',
                    't': 'json'
                },{
                    'n': '执业状态',
                    'En': 'StateOfPractice',
                    'v':
                    'lawoffice/lawofficeresult', # 0 正常 1 缓注 2 注销 3 强制注销  4 吊证 5 名称检索中 6 新所设立中
                    't': 'json'
                },{
                    'n': '考核年度',
                    'En': 'AssessmentYear',
                    'v':
                    'lawoffice/jckhyear',
                    't': 'json'
                },{
                    'n': '执业证有效期至',
                    'En': 'LicenseEndTime',
                    'v':
                    'lawoffice/zyxkenddate',
                    't': 'json'
                },{
                    'n': '批准文号',
                    'En': 'ApprovalNumber',
                    'v':
                    'lawoffice/approvalnum',
                    't': 'json'
                },{
                    'n': '场所面积',
                    'En': 'Areas',
                    'v':
                    'lawoffice/area',
                    't': 'json'
                },{
                    'n': '地区代码',
                    'En': 'AreaCode',
                    'v':
                    'lawoffice/areacode',
                    't': 'json'
                },{
                    'n': '房产属性',
                    'En': 'HouseProperty',
                    'v':
                    'lawoffice/houseproperty',
                    't': 'json'
                },{
                    'n': '是否有效',
                    'En': 'IsValid',
                    'v':
                    'lawoffice/is_valid',
                    't': 'json'
                },{
                    'n': '是否分部',
                    'En': 'HeadquartersOrBranch',
                    'v':
                    'lawoffice/ischildren',
                    't': 'json'
                },{
                    'n': '是否合伙',
                    'En': 'IsPartner',
                    'v':
                    'lawoffice/ishumangroup',
                    't': 'json'
                },{
                    'n': '社会统一信用',
                    'En': 'UnifiedSocialCreditCode',
                    'v':
                    'lawoffice/creditnumber',
                    't': 'json'
                },{
                    'n': '律所类别',
                    'En': 'CategoryOfPractice',
                    'v':
                    'lawoffice/lawyercategory',
                    't': 'json'
                },{
                    'n': '登录ID',
                    'En': 'LoginID',
                    'v':
                    'lawoffice/login_id',
                    't': 'json'
                },{
                    'n': '密码(md5加密过后)',
                    'En': 'PassWord',
                    'v':
                    'lawoffice/password',
                    't': 'json'
                },{
                    'n': '是否党组织',
                    'En': 'IsPartyOrg',
                    'v':
                    'lawoffice/partyorg',
                    't': 'json'
                },{
                    'n': '执业许可证号',
                    'En': 'LicenseNumber',
                    'v':
                    'lawoffice/permit',
                    't': 'json'
                },
                # {
                #     'n': '移动号码',
                #     'En': 'MobileNumber',
                #     'v':
                #     'lawoffice/xzrytel',
                #     't': 'json'
                # },
                {
                    'n': '负责人',
                    'En': 'PersonInCharge',
                    'v':
                    'fuzeren/username',
                    't': 'json'
                },{
                    'n': '负责人工号',
                    'En': 'ChargerWorkCardNumber',
                    'v':
                    'fuzeren/workcardnumber',
                    't': 'json'
                },{
                    'n': '负责人身份证',
                    'En': 'IdNumber',
                    'v':
                    'fuzeren/cardnum',
                    't': 'json'
                },{
                    'n': '专职人数',
                    'En': 'Count1',
                    'v':
                    'count/count1',
                    't': 'json'
                },{
                    'n': '专职（派驻）',
                    'En': 'Count2',
                    'v':
                    'count/count2',
                    't': 'json'
                },{
                    'n': 'Count0',
                    'En': 'Count0',
                    'v':
                    'count/count0',
                    't': 'json'
                },{
                    'n': 'Count3',
                    'En': 'Count3',
                    'v':
                    'count/count3',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def tj_lawyer_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        JS = json.loads(response.text)
        items = JS['items']
        for item in items:
            pkid = item['pkid']
            url = 'http://60.28.163.201:8091/lawyer/lawyer/getLawyerById/%s' % pkid
            yield scrapy.Request(
                url,
                priority=100,
                meta=item,
                callback=self.tj_lawyer_info_parse)

        # '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            method="POST",
            config={'t': 'json',
                    'v': 'totalcount'
                    },
            callback=self.tj_lawyer_parse,
            headers=self.default_jheader,
            urlfunc=
            lambda page: 'http://60.28.163.201:8091/lawyer/lawyer/getLawyerListByHome',
            bodyfunc=self.tj_lawyer_data,
            divmod=20,
            response_type='json')
        for req in reqs:
            yield req
    
    @check_response
    def tj_lawyer_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': '',    
                't': 'json',
                'db': 'dbo.TJLawyerData',
                'keys': ['LawyerName', 'IdNumber'],
                'check': 'LawyerName',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '律师姓名',
                    'En': 'LawyerName',
                    'v':
                    'lawyer_name',
                    't': 'json'
                },
                {
                    'n': '出身日期',  
                    'En': 'DateOfBirth',
                    'v':
                    'birthday',
                    't': 'json'
                },
                {
                    'n': '执业证号',
                    'En': 'LicenseNumber',
                    'v':
                    'workcardnumber',
                    't': 'json'
                },
                {
                    'n': '性别',
                    'En': 'Gender',
                    'v':
                    'usersex',
                    't': 'json'
                },
                {
                    'n': '资格证号',
                    'En': 'QualificationCertificateNumber',
                    'v': 'qualificationnumber',
                    't': 'json'
                },
                {
                    'n': '执业类别',
                    'En': 'CategoryOfPractice',
                    'v': 'lawyertype',
                    't': 'json'
                },
                {
                    'n': '首次执业时间',
                    'En': 'FirstPracticeTime',
                    'v':
                    'practiceyear',
                    't': 'json'
                },{
                    'n': '所在事务所',
                    'En': 'LawFirmName',
                    'v':
                    'lawofficename', 
                    't': 'json'
                },{
                    'n': '地址',
                    'En': 'Address',
                    'v':
                    'address',
                    't': 'json'
                },{
                    'n': '电话',
                    'En': 'PhoneNumber',
                    'v':
                    'tel',
                    't': 'json'
                },{
                    'n': '电子邮箱',
                    'En': 'EmailAddress',
                    'v':
                    'email',
                    't': 'json'
                },{
                    'n': '地区代码',
                    'En': 'AreaCode',
                    'v':
                    'areacode',
                    't': 'json'
                },{
                    'n': '身份证',
                    'En': 'IdNumber',
                    'v':
                    'cardnum',
                    't': 'json'
                },{
                    'n': '毕业证编号',
                    'En': 'EducationNumber',
                    'v':
                    'cultuerlevnumber',
                    't': 'json'
                },{
                    'n': '户籍',
                    'En': 'Domicile',
                    'v':
                    'domicile',
                    't': 'json'
                },{
                    'n': '户籍类型',
                    'En': 'DomicileType',
                    'v':
                    'domiciletype',
                    't': 'json'
                },{
                    'n': '检验日期',
                    'En': 'ExamineDate',
                    'v':
                    'examinedate',
                    't': 'json'
                },{
                    'n': '首次执业城市',
                    'En': 'FirstPracticeArea',
                    'v':
                    'firstaddress',
                    't': 'json'
                },{
                    'n': '第一外语',
                    'En': 'ForeignLangunge',
                    'v':
                    'foreignmyself',
                    't': 'json'
                },{
                    'n': 'Photo',
                    'En': 'Photo',
                    'v':
                    'image',
                    't': 'json'
                },{
                    'n': '加入时间',
                    'En': 'JoinTime',
                    'v':
                    'jointime',
                    't': 'json'
                },{
                    'n': '民族',
                    'En': 'Nation',
                    'v':
                    'nation',
                    't': 'json'
                },{
                    'n': '执业状态',
                    'En': 'StateOfPractice',
                    'v':
                    'officeresult',
                    't': 'json'
                },{
                    'n': '位置信息',
                    'En': 'OrgRelLocation',
                    'v':
                    'orgrellocation',
                    't': 'json'
                },{
                    'n': '政治面貌',
                    'En': 'PoliticalOutlook',
                    'v':
                    'political',
                    't': 'json'
                },{
                    'n': '资格证书获取时间',
                    'En': 'QualificationCertificateGetTime',
                    'v':
                    'qualificationdate',
                    't': 'json'
                },{
                    'n': '资格证书类型',
                    'En': 'QualificationCertificateCategory',
                    'v':
                    'qualificationtype',
                    't': 'json'
                },{
                    'n': '档案所在地',
                    'En': 'RecordLocation',
                    'v':
                    'recordlocation',
                    't': 'json'
                },{
                    'n': '毕业院校',
                    'En': 'School',
                    'v':
                    'school',
                    't': 'json'
                },{
                    'n': '专业',
                    'En': 'Speciality',
                    'v':
                    'specialty',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def nmg_law_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # print(response.text)
        _tag = '//table[@class="table"]//tr/td/a[@title]/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.nmg_law_firm_info_parse)
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     int(response.xpath('//span[@class="Normal"]/span/text()').re('总数:(\d+)')[0]) if response.xpath('//span[@class="Normal"]/span/text()')\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://110.16.70.5/fwsf_shfwh/lsswsList/%s//////.html' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.nmg_law_firm_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re',
                    'v': '//a[text()="尾页"]/@href',
                    're': 'd\((\d+)\)'},
            callback=self.nmg_law_firm_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://110.16.70.5/fwsf_shfwh/lsswsList/%s//////.html' % page,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def nmg_law_firm_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="table01"]',
                't': 'xpath',
                'db': 'dbo.NmgLawFirmData',
                'keys': ['LawFirmName'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n':
                    '单位名称',
                    'En':
                    'LawFirmName',
                    'v':
                    './/th[re:test(text(),"单位名称")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '组织形式',
                    'En':
                    'OrganizationalForm',
                    'v':
                    './/th[re:test(text(),"组织形式")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '负责人',
                    'En':
                    'PersonInCharge',
                    'v':
                    './/th[re:test(text(),"负责人")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '主管机关',
                    'En':
                    'CompetentAuthorities',
                    'v':
                    './/th[re:test(text(),"主管机关")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '合伙人',
                    'En':
                    'Partner',
                    'v':
                    './/th[re:test(text(),"合伙人")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '许可证号',
                    'En':
                    'LicenseKey',
                    'v':
                    './/th[re:test(text(),"许可证号")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '执业律师数',
                    'En':
                    'lawyerNumbers',
                    'v':
                    './/th[re:test(text(),"执业律师数")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '专职律师数',
                    'En':
                    'NumberOfPracticingLawyers',
                    'v':
                    './/th[re:test(text(),"职律师数")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '兼职律师数',
                    'En':
                    'NumberOfPartTimeLawyers',
                    'v':
                    './/th[re:test(text(),"兼职律师数")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '实习律师数',
                    'En':
                    'NumberOfInternLawyers',
                    'v':
                    './/th[re:test(text(),"实习律师数")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '办公地址',
                    'En':
                    'OfficeAddress',
                    'v':
                    './/th[re:test(text(),"办公地址")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '电子邮箱',
                    'En':
                    'EmailAddress',
                    'v':
                    './/th[re:test(text(),"电子邮箱")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '邮编',
                    'En':
                    'ZipCode',
                    'v':
                    './/th[re:test(text(),"邮编")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '电话',
                    'En':
                    'TelephoneNumber',
                    'v':
                    './/th[re:test(text(),"电话")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '传真',
                    'En':
                    'FaxNumber',
                    'v':
                    './/th[re:test(text(),"传真")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '统一社会信用代码',
                    'En':
                    'UnifiedSocialCreditCode',
                    'v':
                    './/th[re:test(text(),"统一社会信用代码")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '简介',
                    'En':
                    'BriefIntroduction',
                    'v':
                    './/th[re:test(text(),"简介")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '照片',
                    'En':
                    'Photo',
                    'v':
                    './/th[re:test(text(),"照片")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '乘车路线',
                    'En':
                    'BusLine',
                    'v':
                    './/th[re:test(text(),"乘车路线")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '地图',
                    'En':
                    'Map',
                    'v':
                    './/th[re:test(text(),"地图")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def nmg_lawyer_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _tag = '//table[@class="table"]//tr/td/a/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.nmg_lawyer_info_parse)
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     int(response.xpath('//span[@class="Normal"]/span/text()').re('总数:(\d+)')[0]) if response.xpath('//span[@class="Normal"]/span/text()')\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://110.16.70.5/fwsf_shfwh/lsList/%s//////.html' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.nmg_lawyer_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re',
                    'v': '//a[text()="尾页"]/@href',
                    're': 'd\((\d+)\)'},
            callback=self.nmg_lawyer_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://110.16.70.5/fwsf_shfwh/lsList/%s//////.html' % page,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def nmg_lawyer_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': '//table[@class="table01"]',
                't': 'xpath',
                'db': 'dbo.NmgLawyerData',
                'keys': ['LawyerName', 'WebID'],
                'check': 'LawyerName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [{
                'n':
                '姓名',
                'En':
                'LawyerName',
                'v':
                './/th[re:test(text(),"姓名")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            },{
                'n':
                'Photo',
                'En':
                'Photo',
                'v':
                './/img/@src',
                't':
                'xpath_first'
            }, {
                'n':
                'WebID',
                'En':
                'WebID',
                'v':
                '\/(\w+)\/LS/2\.html',
                't':
                'url_re'
            }, {
                'n':
                '性别',
                'En':
                'Gender',
                'v':
                './/th[re:test(text(),"性别")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '民族',
                'En':
                'Nation',
                'v':
                './/th[re:test(text(),"民族")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '政治面貌',
                'En':
                'PoliticalOutlook',
                'v':
                './/th[re:test(text(),"政治面貌")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '最高学历',
                'En':
                'HighestEducation',
                'v':
                './/th[re:test(text(),"最高学历")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '首次执业年度',
                'En':
                'FirstPracticeYear',
                'v':
                './/th[re:test(text(),"首次执业年度")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '专业技术职称',
                'En':
                'ProfessionalTechnicalTitle',
                'v':
                './/th[re:test(text(),"专业技术职称")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '执业证号',
                'En':
                'LicenseNumber',
                'v':
                './/th[re:test(text(),"执业证号")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '邮编',
                'En':
                'ZipCode',
                'v':
                './/th[re:test(text(),"邮编")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '办公电话',
                'En':
                'OfficePhoneNumber',
                'v':
                './/th[re:test(text(),"办公电话")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '是否蒙汉语兼通',
                'En':
                'MongolianAndChinese',
                'v':
                './/th[re:test(text(),"是否蒙汉语兼通")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '执业机构',
                'En':
                'PractisingInstitution',
                'v':
                './/th[re:test(text(),"执业机构：")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '执业机构地址',
                'En':
                'PracticeAgencyAddress',
                'v':
                './/th[re:test(text(),"执业机构地址")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '专长法律领域',
                'En':
                'SpecializedFieldOfLaw',
                'v':
                './/th[re:test(text(),"专长法律领域")]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }]
        }]
        #        for configs in _configs:
        #            result = dict()
        #            for config in configs['data']:
        #                result[config['En']] = S.select_content(response, config)
        #                result[config['En']] = S.replace_all(result[config['En']])
        #            print(result)
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def liaoning_lawyer_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _tag = '//span[@class="zi11"]/a/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.liaoning_lawyer_info_parse)
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     int(response.xpath('//div[@class="page"]').re('当前第\d+\/(\d+)页')[0]) if response.xpath('//div[@class="page"]')\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://218.60.145.124:8080/lnlxoa/govhall/lawyerResult.jsp?pn=%s' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.liaoning_lawyer_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re',
                    'v':'//div[@class="page"]/text()[1]',
                    're': '(\d+)页'},
            callback=self.liaoning_lawyer_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://218.60.145.124:8080/lnlxoa/govhall/lawyerResult.jsp?pn=%s' % page,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def liaoning_lawyer_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="zi35"]/table',
                't': 'xpath',
                'db': 'dbo.LiaoNingLawyerData',
                'keys': ['LawyerName','WebID'],
                'check': 'LawyerName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [{
                'n': '律师姓名',
                'En': 'LawyerName',
                'v': './/td[re:test(text(),"律师姓名")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': 'WebID',
                'En': 'WebID',
                'v': 'lawyerId=(\w+)',
                't': 'url_re'
            }, {
                'n': 'Photo',
                'En': 'Photo',
                'v': './/@src',
                't': 'xpath_first'
            }, {
                'n': '性别',
                'En': 'Gender',
                'v': './/td[re:test(text(),"性别")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': '律师事务所',
                'En': 'LawFirmName',
                'v': './/td[re:test(text(),"律师事务所")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': '民族',
                'En': 'Nation',
                'v': './/td[re:test(text(),"民族")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': '政治面貌',
                'En': 'PoliticalOutlook',
                'v': './/td[re:test(text(),"政治面貌")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': '学历',
                'En': 'Education',
                'v': './/td[re:test(text(),"学历")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': '联系电话',
                'En': 'ContactNumber',
                'v': './/td[re:test(text(),"联系电话")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': '擅长领域',
                'En': 'ExcelInTheField',
                'v': './/td[re:test(text(),"擅长领域")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': '执业类别',
                'En': 'CategoryOfPractice',
                'v': './/td[re:test(text(),"执业类别")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': '首次执业时间',
                'En': 'FirstPracticeTime',
                'v': './/td[re:test(text(),"首次执业时间")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': '执业证号',
                'En': 'LicenseNumber',
                'v': './/td[re:test(text(),"执业证号")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': '考核结果',
                'En': 'AssessmentResults',
                'v': './/td[re:test(text(),"考核结果")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': '个人主页',
                'En': 'PersonalHomePage',
                'v': './/td[re:test(text(),"个人主页")]/text()',
                't': 'xpath_re',
                're': '：(.+)'
            }, {
                'n': '电子邮箱',
                'En': 'EmailAddress',
                'v': '//td[contains(text(),"mail")]/text()',
                't': 'xpath_re',
                're': '[:：](.+)'
            }]
        }]
        #        for configs in _configs:
        #            result = dict()
        #            for config in configs['data']:
        #                result[config['En']] = S.select_content(response, config)
        #                result[config['En']] = S.replace_all(result[config['En']])
        #            print(result)
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def liaoning_law_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': '//div[@class="zi36"]/table',
                't': 'xpath',
                'db': 'dbo.LiaoNingLawFirmData',
                'keys': ['LawFirmName'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律所名称',
                    'En': 'LawFirmName',
                    'v': './..//h3/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业许可证号',
                    'En': 'LicenseNumber',
                    'v': './/td[re:test(text(),"执业许可证号")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
                {
                    'n': '住所',
                    'En': 'Residence',
                    'v': './/td[re:test(text(),"住所")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
                {
                    'n': '联络地址',
                    'En': 'ContactAddress',
                    'v': './/td[re:test(text(),"联络地址")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
                {
                    'n': '电话',
                    'En': 'PhoneNumber',
                    'v': './/td[re:test(text(),"电话")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
                {
                    'n': '传真',
                    'En': 'FaxNumber',
                    'v': './/td[re:test(text(),"传真")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
                {
                    'n': '网站',
                    'En': 'Website',
                    'v': './/td[re:test(text(),"网站")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
                {
                    'n': '负责人',
                    'En': 'PersonInCharge',
                    'v': './/td[re:test(text(),"负责人")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
                {
                    'n': '主管机关',
                    'En': 'CompetentAuthorities',
                    'v': './/td[re:test(text(),"主管机关")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
                {
                    'n': '批准日期',
                    'En': 'DateOfApproval',
                    'v': './/td[re:test(text(),"批准日期")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
                {
                    'n': '执业状态',
                    'En': 'StateOfPractice',
                    'v': './/td[re:test(text(),"执业状态")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
                {
                    'n': '考核结果',
                    'En': 'AssessmentResults',
                    'v': './/td[re:test(text(),"考核结果")]/text()',
                    't': 'xpath_re',
                    're': '[:：](.+)'
                },
            ]
        }]
        #        for configs in _configs:
        #            if configs['list']['v']:
        #                _response_copy = S.select_content(response, configs['list'])
        #            else:
        #                _response_copy = [response]
        #            for _response in _response_copy:
        #                result = dict()
        #                for config in configs['data']:
        #                    result[config['En']] = S.select_content(_response, config)
        #                    result[config['En']] = S.replace_all(result[config['En']])
        #                print(result)
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     int(response.xpath('//div[@class="page"]').re('当前第\d+\/(\d+)页')[0]) if response.xpath('//div[@class="page"]')\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://218.60.145.124:8080/lnlxoa/govhall/lawFirmResult.jsp?pn=%s' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.liaoning_law_firm_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re',
                    'v':'//div[@class="page"]/text()[1]',
                    're': '(\d+)页'},
            callback=self.liaoning_law_firm_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://218.60.145.124:8080/lnlxoa/govhall/lawFirmResult.jsp?pn=%s' % page,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req


#    def out_item(func):

    def item_parse(self, _configs: list, response, response1=None) -> dict:
        '''
        @parsma _configs->字段抓取设置  list
        @params response->Response
        @output -->result  字段-值 的字典
        '''
        if hasattr(response,'url'):
            response1 = response
        for configs in _configs:
            response_change = self.change_response_f_type(configs, response)
            if configs['list']['v']:
                _response_copy = S.select_content(response_change,
                                                  configs['list'], response1)
            else:
                if isinstance(response_change, list):
                    _response_copy = response_change
                else:
                    _response_copy = [response_change]
            for _response in _response_copy:
                result = dict()
                for config in configs['data']:
                    result[config['En']] = S.select_content(
                        _response, config, response1)
                    result[config['En']] = S.replace_all(result[config['En']])
                item = self.item_db_parse(configs, result)
                if item:
                    # 持久化记录item
                    self.state['items_count'] = self.state.get(
                        'items_count', 0) + 1
                    yield item

    def item_db_parse(self, configs, result):
        '''
        @params configs 字典 里面有keys,db,check3个参数 check在result里有对应key
        @params result 字典 解析字段的返回值
        '''
        check = configs['list']['check']
        if not result[check]:  # 非空字段检索 为None ''  return
            return
        item = Item()
        item['result'] = result
        item['db'] = configs['list']['db']
        item['keys'] = configs['list']['keys']
        item['conn'] = configs['list'].get('conn',False)
        return item

    def change_response_f_type(self, configs, response):
        if configs.get('response_type') == 'json':
            return json.loads(response.text)
        else:
            return response

    @check_response
    def sh_lawyer_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        #        print(response.text)
        _tag = '//ul[@class="multi-list"]/li/a/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                headers=self.default_header,
                priority=100,
                callback=self.sh_lawyer_info_parse)
        '''def generator_page(self, response, {'t':'','v':'','re':''},
                divmod=1,formatter=,body='',method='GET',
                response_type='urlencode'):
            response = json.loads(response) if response_type == 'json' else response
            totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
            ceil(int(response.xpath('//div[@class="list-count"]').re('共\s*?(\d+)\s*?条')[0]) / divmod) if response.xpath('//div[@class="list-count"]/text()')\
            else 1
            if page == 1 and page < totalpage:
                for page in range(page+1, totalpage+1):
                    url = 'https://credit.justice.gov.cn/subjects.jsp?zoneId=All&typeId=10d341aea6674146b36dd23c25090f04&page=%s' % page
                    yield scrapy.Request(url,
                                         headers=self.default_header,
                                         meta={'page': page, 'totalpage': totalpage},
                                         callback=self.sh_lawyer_parse)

        '''
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(response.xpath('//div[@class="list-count"]').re('共\s*?(\d+)\s*?条')[0]) / 20) if response.xpath('//div[@class="list-count"]/text()')\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'https://credit.justice.gov.cn/subjects.jsp?zoneId=All&typeId=10d341aea6674146b36dd23c25090f04&page=%s' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.sh_lawyer_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共\s*?(\d+)\s*?条'},
            callback=self.sh_lawyer_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'https://credit.justice.gov.cn/subjects.jsp?zoneId=All&typeId=10d341aea6674146b36dd23c25090f04&page=%s' % page,
            divmod=5,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def sh_lawyer_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        #        print(response.text)A
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'cbrc_institution',
                'keys': ['lawyerName'],
                'check': 'lawyerName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律师姓名',
                    'En': 'lawyerName',
                    'v': '//div[@class="data"]/h3/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业证号',
                    'En': 'LicenseNumber',
                    'v': '//p[span[contains(text(),"执业证号")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业机构',
                    'En': 'PractisingInstitution',
                    'v': '//p[span[contains(text(),"执业机构")]]/a/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '性别',
                    'En': 'Gender',
                    'v': '//li[label[contains(text(),"性别")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '年龄',
                    'En': 'Age',
                    'v': '//li[label[contains(text(),"年龄")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '政治面貌',
                    'En': 'PoliticalOutlook',
                    'v': '//li[label[contains(text(),"政治面貌")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '学历',
                    'En': 'Education',
                    'v': '//li[label[contains(text(),"学历")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业类别',
                    'En': 'CategoryOfPractice',
                    'v': '//li[label[contains(text(),"执业类别")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业状态',
                    'En': 'StateOfPractice',
                    'v': '//li[label[contains(text(),"执业状态")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '主管机关',
                    'En': 'CompetentAuthorities',
                    'v': '//li[label[contains(text(),"主管机关")]]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        #        for configs in _configs:
        #            if configs['list']['v']:
        #                _response_copy = S.select_content(response, configs['list'])
        #            else:
        #                _response_copy = [response]
        #            for _response in _response_copy:
        #                result = dict()
        #                for config in configs['data']:
        #                    result[config['En']] = S.select_content(_response, config)
        #                    result[config['En']] = S.replace_all(result[config['En']])
        #                print(result)
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def sh_law_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        '''
        def (self,_tag,response, response_type,config={'v':'t'},urlformater='',data=func):
            _response = change_type(response,response_type)
            urls = _response.select(config)

        '''
        _tag = '//ul[@class="multi-list"]/li/a/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                headers=self.default_header,
                priority=100,
                callback=self.sh_law_firm_info_parse)

        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(response.xpath('//div[@class="list-count"]').re('共\s*?(\d+)\s*?条')[0]) / 20) if response.xpath('//div[@class="list-count"]/text()')\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'https://credit.justice.gov.cn/subjects.jsp?zoneId=All&typeId=41cb822a0fcd46dda5af6da58283b35d&page=%s' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.sh_lawyer_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共\s*?(\d+)\s*?条'},
            callback=self.sh_lawyer_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'https://credit.justice.gov.cn/subjects.jsp?zoneId=All&typeId=41cb822a0fcd46dda5af6da58283b35d&page=%s' % page,
            divmod=20,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def sh_law_firm_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'cbrc_institution',
                'keys': ['lawyerFirmName'],
                'check': 'lawyerFirmName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律所姓名',
                    'En': 'lawyerFirmName',
                    'v': '//div[@class="data"]/h3/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '负责人',
                    'En': 'PersonInCharge',
                    'v': '//li[label[contains(text(),"负责人")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '地址',
                    'En': 'Address',
                    'v': '//li[label[contains(text(),"地址")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业状态',
                    'En': 'StateOfPractice',
                    'v': '//li[label[contains(text(),"执业状态")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业许可证号',
                    'En': 'LicenseNumber',
                    'v': '//li[label[contains(text(),"执业许可证号")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '批准日期',
                    'En': 'DateOfApproval',
                    'v': '//li[label[contains(text(),"批准日期")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '批准文号',
                    'En': 'ApprovalNumber',
                    'v': '//li[label[contains(text(),"批准文号")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '传真号码',
                    'En': 'FaxNumber',
                    'v': '//li[label[contains(text(),"传真号码")]]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '联系电话',
                    'En': 'ContactNumber',
                    'v': '//li[label[contains(text(),"联系电话")]]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def js_lawyer_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        #        print(response.text)
        #        JS_response = json.loads(response.text)
        configs = {
            'list': {
                'v': 'items',
                't': 'json'
            },
            'data': [{
                'En': 'pkid',
                'v': 'pkid',
                't': 'json'
            }],
            'response_type': 'json'
        }
        urls = self.result_parse(configs, response)
        for url in urls:
            url = 'http://218.94.1.186:8090/lawyerIntegrity/lawyer/getLawyerDetail/{pkid}'.format(
                **url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.js_lawyer_info_parse)
        # JS_response = json.loads(response.text)
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(JS_response, {'t': 'json', 'v': 'totalcount'})) / 8) if S.select_content(JS_response, {'t': 'json', 'v': 'totalcount'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://218.94.1.186:8090/lawyerIntegrity/lawyer/getLawyerListPage'
        #         data = self.js_law_firm_data(page)
        #         yield scrapy.Request(
        #             url,
        #             method='POST',
        #             body=data,
        #             headers=self.default_jheader,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.js_lawyer_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json',
                    'v': 'totalcount'},
            callback=self.js_lawyer_parse,
            headers=self.default_jheader,
            method='POST',
            urlfunc=
            lambda page: 'http://218.94.1.186:8090/lawyerIntegrity/lawyer/getLawyerListPage',
            bodyfunc=self.js_lawyer_data,
            divmod=8,
            response_type='json',
        )
        for req in reqs:
            yield req

    @check_response
    def js_lawyer_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'json',
                'db': 'dbo.JsLawyerData',
                'keys': ['LawyerName', 'LicenseNumber'],
                'check': 'LawyerName',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '律师姓名',
                    'En': 'LawyerName',
                    'v': 'lawyer/username',
                    't': 'json'
                },{
                    'n': '头像',
                    'En': 'Photo',
                    'v': 'lawyer/image',
                    't': 'json'
                },
                {
                    'n': '年龄',
                    'En': 'Age',
                    'v': 'lawyer/age',
                    't': 'json'
                },
                {
                    'n': '学历',
                    'En': 'Education',
                    'v': 'lawyer/education',  # 1 博士 2硕士 3双学士 4 本科 5大专 6其他
                    't': 'json'
                },
                {
                    'n': '地址',
                    'En': 'Address',
                    'v': 'lawyer/areaname',
                    't': 'json'
                },
                {
                    'n': '执业类别',
                    'En': 'CategoryOfPractice',
                    'v': 'lawyer/lawyertype',  # 1:兼职律师 2：专职律师 3：
                    't': 'json'
                },
                {
                    'n': '执业证号',
                    'En': 'LicenseNumber',
                    'v': 'lawyer/workcardnumber',
                    't': 'json'
                },
                {
                    'n': '外语水平',
                    'En': 'LanguageLevel',
                    'v': 'lawyer/language',
                    't': 'json'
                },
                {
                    'n': '执业机构',
                    'En': 'PractisingInstitution',
                    'v': 'lawyer/lawofficename',
                    't': 'json'
                },
                {
                    'n': '执业年限',
                    'En': 'PracticeYears',
                    'v': 'lawyer/practice_year',
                    't': 'json'
                },
                {
                    'n': '政治面貌',
                    'En': 'PoliticalOutlook',
                    'v':
                    'lawyer/political_status',  # 1中国共产党党员2中国共产党预备党员3中国共产主义青年团团员\
                    # 4中国国民党革命委员会会员 5中国民主同盟盟员 6 中国民主建国会会员
                    # 7中国民主促进会会员 8中国农工民主党党员 9 中国致公党党员 10九三学社社员 11台湾民主自治同盟盟员
                    # 12无党派人士 13 群众 14其他
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    def result_parse(self, configs, response):
        response_change = self.change_response_f_type(configs, response)
        # print(response_change)
        if configs['list']['v']:
            _response_copy = S.select_content(response_change, configs['list'])
        else:
            if isinstance(response_change, list):
                _response_copy = response_change
            else:
                _response_copy = [response_change]
        for _response in _response_copy:
            result = dict()
            for config in configs['data']:
                result[config['En']] = S.select_content(_response, config)
                result[config['En']] = S.replace_all(result[config['En']])
                yield result

    @check_response
    def js_law_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        configs = {
            'list': {
                'v': 'items',
                't': 'json'
            },
            'data': [{
                'En': 'pkid',
                'v': 'pkid',
                't': 'json'
            }],
            'response_type': 'json'
        }
        urls = self.result_parse(configs, response)
        for url in urls:
            url = 'http://218.94.1.186:8090/lawyerIntegrity/lawoffice/getLawofficeDetail/{pkid}'.format(
                **url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.js_law_firm_info_parse)
        # JS_response = json.loads(response.text)
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(JS_response, {'t': 'json', 'v': 'totalcount'})) / 8) if S.select_content(JS_response, {'t': 'json', 'v': 'totalcount'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://218.94.1.186:8090/lawyerIntegrity/lawoffice/initLawofficeList'
        #         data = self.js_law_firm_data(page)
        #         yield scrapy.Request(
        #             url,
        #             method='POST',
        #             body=data,
        #             headers=self.default_jheader,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.js_law_firm_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json',
                    'v': 'totalcount'},
            callback=self.js_law_firm_parse,
            headers=self.default_jheader,
            method='POST',
            urlfunc=
            lambda page: 'http://218.94.1.186:8090/lawyerIntegrity/lawoffice/initLawofficeList',
            bodyfunc=self.js_law_firm_data,
            divmod=8,
            response_type='json',
        )
        for req in reqs:
            yield req

    @check_response
    def js_law_firm_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'json',
                'db': 'JsLawFirmData',
                'keys': ['LawFirmName'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [{
                'n': '律所名称',
                'En': 'LawFirmName',
                'v': 'loginid',
                't': 'json'
            }, {
                'n': '密码(128位加密)',
                'En': 'PassWord_AES128',
                'v': 'password',
                't': 'json'
            }, {
                'n': '密码(明文)',# 需要短信登录 放弃
                'En': 'PassWord',
                'v': 'viewpwd',
                't': 'json'
            }, {
                'n': '机构英文名称',
                'En': 'EnglishFullName',
                'v': 'englishname',
                't': 'json'
            }, {
                'n': '合伙人人数',
                'En': 'PartnerNums',
                'v': 'lawofficenature_num',
                't': 'json'
            }, {
                'n': '律师总数',
                'En': 'lawyerNumbers',
                'v': 'lawyersum', # int
                't': 'json'
            }, {
                'n': '批准文号',
                'En': 'ApprovalNumber',
                'v': 'approvalnum',
                't': 'json'
            }, {
                'n': '批准日期',
                'En': 'ApproveDate',
                'v': 'approve_date',
                't': 'json'
            }, {
                'n': '场所面积（平米）',
                'En': 'Areas',
                'v': 'area',
                't': 'json'
            }, {
                'n': '所在地区代码',
                'En': 'AreaCode',
                'v': 'areacode',
                't': 'json'
            }, {
                'n': '所在地区',
                'En': 'AreaName',
                'v': 'areaname',
                't': 'json'
            }, {
                'n': '律所地址',
                'En': 'LawFirmAddress',
                'v': 'lawfirmaddress',
                't': 'json'
            }, {
                'n': '注册资金（万元）',
                'En': 'RegisteredCapital',
                'v': 'asset',
                't': 'json'
            }, {
                'n': '设立日期',
                'En': 'SetUpTime',
                'v': 'begintime',
                't': 'json'
            }, {
                'n': '变更信息',
                'En': 'ChangeMsg',
                'v': 'change_msg',
                't': 'json'
            }, {
                'n': '电子邮箱',
                'En': 'EmailAddress',
                'v': 'email',
                't': 'json'
            }, {
                'n': '传真号码',
                'En': 'FaxNumber',
                'v': 'fax',
                't': 'json'
            }, {
                'n': '负责人',
                'En': 'PersonInCharge',
                'v': 'fuzeren_name',
                't': 'json'
            }, {
                'n': '经度',
                'En': 'Lat',
                'v': 'lat',
                't': 'json'
            }, {
                'n': '纬度',
                'En': 'Lng',
                'v': 'lng',
                't': 'json'
            }, {
                'n': '邮编',
                'En': 'ZipCode',
                'v': 'postcode',
                't': 'json'
            }, {
                'n': '备注',
                'En': 'Remark',
                'v': 'remark',
                't': 'json'
            }, {
                'n': '专长法律领域',
                'En': 'SpecializedFieldOfLaw',
                'v': 'speciality',
                't': 'json'
            }, {
                'n': '状态码(未知)',
                'En': 'StatusTemp',
                'v': 'status_temp',
                't': 'json'
            }, {
                'n': '执业证号',
                'En': 'LicenseNumber',
                'v': 'permit',
                't': 'json'
            }, {
                'n': '是否分公司', # 0 总 1 分
                'En': 'HeadquartersOrBranch',
                'v': 'ischildren',
                't': 'json'
            }, 
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def zj_law_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _tag = '//td[text()="机构名称"]/../../tr[position()>1]/td[1]/a/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.zj_law_firm_info_parse)
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(response, {'t': 'regex1', 'v': '当前第\s*?\d+/(\d+)\s*?页'})) / 1) if S.select_content(response, {'t': 'regex1', 'v': '当前第\s*?\d+/(\d+)\s*?页'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://lsgl.zjsft.gov.cn/zjlawyermanager/view/lawyers/LawyerOfficePageList/execute/lawofficeList.do'
        #         data = urllib.parse.urlencode({'pageNo': str(page)})
        #         yield scrapy.Request(
        #             url,
        #             method='POST',
        #             body=data,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.zj_law_firm_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re', 'v': '//a[text()="尾页"]/@onclick','re':'changepage\((\d+)\)'},
            callback=self.zj_law_firm_parse,
            headers=self.default_header,
            method='POST',
            urlfunc=lambda page:'http://lsgl.zjsft.gov.cn/zjlawyermanager/view/lawyers/LawyerOfficePageList/execute/lawofficeList.do',
            bodyfunc=lambda page, response:urllib.parse.urlencode({'pageNo': str(page)}),
            divmod=1,
            response_type='xpath',
            )
        for req in reqs:
            yield req

    @check_response
    def zj_law_firm_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'dbo.ZjLawFirmData',
                'keys': ['LawFirmName'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [{
                'n':
                '律所名称',
                'En':
                'LawFirmName',
                'v':
                '//td[text()="机构名称"]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n': '律所地址',
                'En': 'LawFirmAddress',
                'v': '//td[text()="地址"]/following-sibling::td[1]/text()',
                't': 'xpath_first'
            }, {
                'n':
                '主管机关',
                'En':
                'CompetentAuthorities',
                'v':
                '//td[text()="主管机关"]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n': '邮编',
                'En': 'ZipCode',
                'v': '//td[text()="邮编"]/following-sibling::td[1]/text()',
                't': 'xpath_first'
            }, {
                'n': '电话',
                'En': 'TelephoneNumber',
                'v': '//td[text()="电话"]/following-sibling::td[1]/text()',
                't': 'xpath_first'
            }, {
                'n':
                '执业许可证号码',
                'En':
                'LicenseKey',
                'v':
                '//td[text()="执业许可证号码"]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '统一社会信用代码',
                'En':
                'UnifiedSocialCreditCode',
                'v':
                '//td[text()="统一社会信用代码"]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '负责人',
                'En':
                'PersonInCharge',
                'v':
                '//td[text()="负责人"]/following-sibling::td[1]/a/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '业务特长',
                'En':
                'BusinessExpertise',
                'v':
                '//td[text()="业务特长"]/following-sibling::td[1]/text()',
                't':
                'xpath_join,'
            }]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def zj_lawyer_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # print(response.text)
        _tag = '//td[text()="姓名"]/../../tr[position()>1]/td[1]/a/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                headers=self.default_header,
                priority=100,
                callback=self.zj_lawyer_info_parse)
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(response, {'t': 'regex1', 'v': '当前第\s*?\d+/(\d+)\s*?页'})) / 1) if S.select_content(response, {'t': 'regex1', 'v': '当前第\s*?\d+/(\d+)\s*?页'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://lsgl.zjsft.gov.cn/zjlawyermanager/view/lawyers/LawyerOfficePageList/execute/lawofficeList.do'
        #         data = urllib.parse.urlencode({'pageNo': str(page)})
        #         yield scrapy.Request(
        #             url,
        #             method='POST',
        #             body=data,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.zj_law_firm_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re', 
            'v': '//a[text()="尾页"]/@onclick',
            're':'changepage\((\d+)\)'},
            callback=self.zj_lawyer_parse,
            headers=self.default_header,
            method='POST',
            urlfunc=lambda page:'http://lsgl.zjsft.gov.cn/zjlawyermanager/view/lawyers/LawyerPageList/execute/lawyersList.do',
            bodyfunc=lambda page, response:urllib.parse.urlencode({'pageNo': str(page)}),
            divmod=1,
            response_type='xpath',
            )
        for req in reqs:
            yield req

    @check_response
    def zj_lawyer_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        '''
        好像数据会少 ，原因未明
        '''
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'dbo.ZjLawyerData',
                'keys': ['LawyerName', 'LicenseNumber'],
                'check': 'LawyerName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [{
                'n':
                '律所名称',
                'En':
                'LawyerFirmName',
                'v':
                '//td[text()="执业机构"]/following-sibling::td[1]/a/text()',
                't':
                'xpath_first'
            }, {
                'n': '律师姓名',
                'En': 'LawyerName',
                'v': '//td[text()="姓名"]/following-sibling::td[1]/text()',
                't': 'xpath_first'
            }, {
                'n':
                '机构主管机关',
                'En':
                'CompetentAuthorities',
                'v':
                '//td[text()="机构主管机关"]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n': '性别',
                'En': 'Gender',
                'v': '//td[text()="性别"]/following-sibling::td[1]/text()',
                't': 'xpath_first'
            }, {
                'n':
                '是否负责人',
                'En':
                'IsPersonInCharge',
                'v':
                '//td[text()="是否负责人"]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '执业类别',
                'En':
                'CategoryOfPractice',
                'v':
                '//td[text()="执业类别"]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '执业证号',
                'En':
                'LicenseNumber',
                'v':
                '//td[text()="执业证号"]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '资格证号',
                'En':
                'QualificationCertificateNumber',
                'v':
                '//td[text()="资格证号"]/following-sibling::td[1]/text()',
                't':
                'xpath_first'
            }, {
                'n':
                '业务特长',
                'En':
                'BusinessExpertise',
                'v':
                '//td[text()="业务特长"]/following-sibling::td[1]/text()',
                't':
                'xpath_join,'
            }]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def fj_lawyer_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # print(response.text)
        _tag = '//td[text()="姓名"]/../../tr[position()>1]/td[1]/a/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                headers=self.default_header,
                priority=100,
                callback=self.fj_lawyer_info_parse)
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(response, {'t': 'regex1', 'v': '共\s*?(\d+)\s*?页'})) / 1) if S.select_content(response, {'t': 'regex1', 'v': '共\s*?(\d+)\s*?页'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://www.fjsf.gov.cn/fjsf/lawMemberlawyer.do?task=slist&currentPage=%s' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.fj_lawyer_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re',
                    'v': '//form[@name="pageform"]/a[text()="最后一页"]/@href',
                    're': 'currentPage=(\d+)'},
            callback=self.fj_lawyer_parse,
            headers=self.default_header,
            method='POST',
            urlfunc=
            lambda page: 'http://www.fjsf.gov.cn/fjsf/lawMemberLawer.do?task=slist&currentPage=%s' % page,
            divmod=1,
            bodyfunc=lambda page, response:urllib.parse.urlencode({'year':'0','y':'7','x':'27','currentPage':str(page-1)}),
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def fj_lawyer_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'dbo.FjLawyerData',
                'keys': ['LawyerName', 'LicenseNumber'],
                'check': 'LawyerName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律师姓名',
                    'En': 'LawyerName',
                    'v': '//*[text()="律师姓名"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '曾用名/英文名',
                    'En': 'UsedOrEnglishName',
                    'v':
                    '//*[text()="曾用名/英文名"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '性别',
                    'En': 'Gender',
                    'v': '//*[text()="性　　别"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '出生年月',
                    'En': 'DateOfBirth',
                    'v': '//*[text()="出生年月"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '主管机关',
                    'En': 'CompetentAuthorities',
                    'v': '//*[text()="主管机关"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '职务',
                    'En': 'Post',
                    'v': '//*[text()="职　　务"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '资格证类别',
                    'En': 'QualificationCertificateCategory',
                    'v': '//*[text()="资格证类别"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '资格证号',
                    'En': 'QualificationCertificateNumber',
                    'v': '//*[text()="资格证号"]/following-sibling::td[1]/text()',
                    't': 'xpath_join,'
                },
                {
                    'n': '取得方式',
                    'En': 'AcquisitionMode',
                    'v': '//*[text()="取得方式"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '资格证取得时间',
                    'En': 'QualificationCertificateGetTime',
                    'v':
                    '//*[text()="资格证取得时间"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '工作单位',
                    'En': 'WorkUnit',
                    'v': '//*[text()="工作单位"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业证号',
                    'En': 'LicenseNumber',
                    'v': '//*[text()="执业证号"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '首次执业时间',
                    'En': 'FirstPracticeTime',
                    'v':
                    '//*[text()="首次执业时间"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '律师类型',
                    'En': 'TypeOfLawyer',
                    'v': '//*[text()="律师类型"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '是否合伙人',
                    'En': 'IsPartner',
                    'v': '//*[text()="是否合伙人"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '颁证时间',
                    'En': 'IssueDate',
                    'v':
                    '//*[text()="颁证时间"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '联系电话',
                    'En': 'ContactNumber',
                    'v': '//*[text()="联系电话"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '工作地址',
                    'En': 'WorkingAddress',
                    'v': '//*[text()="工作地址"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '是否注销',
                    'En': 'IsCancellation',
                    'v': '//*[text()="是否注销"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '设区市',
                    'En': 'DistrictCity',
                    'v': '//*[text()="设区市"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '县市区',
                    'En': 'CountyCity',
                    'v': '//*[text()="县市区"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '注销时间',
                    'En': 'CancellationTime',
                    'v': '//*[text()="注销时间"]/following-sibling::td[1]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def fj_law_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # print(response.text)
        _tag = '//a[re:test(@href,"fid=")]/@href'

        urls = response.xpath(_tag).extract()
        for url in urls:
            # print(response.url,url)
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.fj_law_firm_info_parse)

        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(response, {'t': 'regex1', 'v': '共\s*?(\d+)\s*?页'})) / 1) if S.select_content(response, {'t': 'regex1', 'v': '共\s*?(\d+)\s*?页'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://www.fjsf.gov.cn/fjsf/lawOffice.do?task=slist&currentPage=%s' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.fj_law_firm_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re',
                    'v': '//form[@name="pageform"]/a[text()="最后一页"]/@href',
                    're': 'currentPage=(\d+)'},
            callback=self.fj_law_firm_parse,
            method='POST',
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://www.fjsf.gov.cn/fjsf/lawOffice.do?task=slist&currentPage=%s' % page,
            bodyfunc=lambda page, response:urllib.parse.urlencode({'year':'0','y':'9','x':'29','currentPage':str(page-1)}),
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def fj_law_firm_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'dbo.FjLawFirmData',
                'keys': ['LawFirmName'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n':
                    '事务所名称',
                    'En':
                    'LawFirmName',
                    'v':
                    '//*[re:test(text(),"事务所名称")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '中文简称',
                    'En':
                    'ChineseAbbreviation',
                    'v':
                    '//*[contains(text(),"中文简称")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '英文全称',
                    'En':
                    'EnglishFullName',
                    'v':
                    '//*[re:test(text(),"英文全称")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '事务所地址',
                    'En':
                    'LawFirmAddress',
                    'v':
                    '//*[re:test(text(),"事务所地址")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '设立资产(万元)',
                    'En':
                    'EstablishmentOfAssets',
                    'v':
                    '//*[re:test(text(),"设立资产")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '组织形式',
                    'En':
                    'OrganizationalForm',
                    'v':
                    '//*[re:test(text(),"组织形式")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '主管机关',
                    'En':
                    'CompetentAuthorities',
                    'v':
                    '//*[re:test(text(),"主管机关")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '执业许可证号',
                    'En':
                    'LicenseNumber',
                    'v':
                    '//*[re:test(text(),"执业")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '批准文号',
                    'En':
                    'ApprovalNumber',
                    'v':
                    '//*[re:test(text(),"批准文号")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '总所分所',
                    'En':
                    'HeadquartersOrBranch',
                    'v':
                    '//*[re:test(text(),"总所分所")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '批准日期',
                    'En':
                    'DateOfApproval',
                    'v':
                    '//*[re:test(text(),"批准日期")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '首次发证日期',
                    'En':
                    'DateOfFirstIssuing',
                    'v':
                    '//*[re:test(text(),"首次发证日期")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '联系电话',
                    'En':
                    'ContactNumber',
                    'v':
                    '//*[re:test(text(),"联系电话")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '负责人',
                    'En':
                    'PersonInCharge',
                    'v':
                    '//*[re:test(text(),"负责人")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '网址',
                    'En':
                    'WebSite',
                    'v':
                    '//*[re:test(text(),"网址")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '税务登记号',
                    'En':
                    'TaxRegistrationNumber',
                    'v':
                    '//*[re:test(text(),"税务登记号")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '合伙人',
                    'En':
                    'Partner',
                    'v':
                    '//*[re:test(text(),"合伙人")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '邮政编码',
                    'En':
                    'ZipCode',
                    'v':
                    '//*[re:test(text(),"邮政编码")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '专职律师',
                    'En':
                    'FullTimeLawyer',
                    'v':
                    '//*[re:test(text(),"专职律师")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '兼职律师',
                    'En':
                    'PartTimeLawyer',
                    'v':
                    '//*[re:test(text(),"兼职律师")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '传真',
                    'En':
                    'FaxNumber',
                    'v':
                    '//*[re:test(text(),"传真")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '是否注销',
                    'En':
                    'IsCancellation',
                    'v':
                    '//*[re:test(text(),"是否注销")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '设区市',
                    'En':
                    'DistrictCity',
                    'v':
                    '//*[re:test(text(),"设区市")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '县市区',
                    'En':
                    'CountyCity',
                    'v':
                    '//*[re:test(text(),"县市区")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def sd_lawyer_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # print(response.text)
        JS_response = json.loads(response.text)
        urls = JS_response['list']
        for url in urls:
            data = urllib.parse.urlencode({'type': 'lawyer', 'id': url['id']})
            url = 'http://sd.12348.gov.cn/sftIDC/lawworkmanage/findPersonnelListByid.do'
            yield scrapy.Request(
                url,
                method='POST',
                priority=100,
                body=data,
                headers=self.default_header,
                callback=self.sd_lawyer_info_parse)
        # 废弃代码  使用封装好的函数生成page页面
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(response, {'t': 'json', 'v': 'totalCount'})) / 10) if S.select_content(response, {'t': 'json', 'v': 'totalCount'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://www.sd12348.gov.cn/sftIDC/select/search.do'
        #         data = urllib.parse.urlencode({'page':str(page), 'areacode':'37','order':'','pageSize':'10','type':'lawyer','flag':'0'})
        #         yield scrapy.Request(
        #             url,
        #             method='POST',
        #             body=data,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.sd_lawyer_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json', 'v': 'totalCount'},
            callback=self.sd_lawyer_parse,
            method='POST',
            headers=self.default_header,
            urlfunc=lambda page:'http://www.sd12348.gov.cn/sftIDC/select/search.do',
            bodyfunc=lambda page, response:urllib.parse.urlencode({'page':str(page), 'areacode':'37','order':'','pageSize':'10','type':'lawyer','flag':'0'}),
            divmod=10,
            response_type='json',
            )
        for req in reqs:
            yield req

    @check_response
    def sd_lawyer_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'json',
                'db': 'dbo.SdLawyerData',
                'keys': ['LawFirmName', 'LicenseNumber'],
                'check': 'LawyerName',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '律师姓名',
                    'En': 'LawyerName',
                    'v': 'name',
                    't': 'json'
                },
                {
                    'n': '学历',
                    'En': 'Education',
                    'v': 'education',
                    't': 'json'
                },
                {
                    'n': '照片',
                    'En': 'Photo',
                    'v': 'logourl',
                    't': 'json'
                },
                {
                    'n': '身份证号码',
                    'En': 'IdNumber',
                    'v': 'idnum',
                    't': 'json'
                },
                {
                    'n': '颁证时间',
                    'En': 'IssueDate',
                    'v': 'issuedate',
                    't': 'json'
                },
                {
                    'n': '颁证机关',
                    'En': 'IssueOrgan',
                    'v': 'issuedate',
                    't': 'json'
                },
                {
                    'n': '执业类别',
                    'En': 'CategoryOfPractice',
                    'v': 'jobcategory',
                    't': 'json'
                },
                {
                    'n': '律所地址',
                    'En': 'LawFirmAddress',
                    'v': 'lawfirmaddress',
                    't': 'json'
                },
                {
                    'n': '乘车路线',
                    'En': 'BusLine',
                    'v': 'lawfirmbus',
                    't': 'json'
                },
                {
                    'n': '律所经纬度',
                    'En': 'LawFirmLocal_xy',
                    'v': 'lawfirmlocalxy',
                    't': 'json'
                },
                {
                    'n': '律所名称',
                    'En': 'LawFirmName',
                    'v': 'lawfirmname',
                    't': 'json'
                },
                {
                    'n': '执业证号',
                    'En': 'LicenseNumber',
                    'v': 'licenseno',
                    't': 'json'
                },
                {
                    'n': '许可证编号',
                    'En': 'LicenseSerialNo',
                    'v': 'licenseserialno',
                    't': 'json'
                },
                {
                    'n': '政治面貌',
                    'En': 'PoliticalOutlook',
                    'v': 'party',
                    't': 'json'
                },
                {
                    'n': '资格证号',
                    'En': 'QualificationCertificateNumber',
                    'v': 'qualificationno',
                    't': 'json'
                },
                {
                    'n': '毕业院校',
                    'En': 'School',
                    'v': 'school',
                    't': 'json'
                },
                {
                    'n': '电话号码',
                    'En': 'PhoneNumber',
                    'v': 'telnum',
                    't': 'json'
                },
                {
                    'n': '专长法律领域',
                    'En': 'SpecializedFieldOfLaw',
                    'v': 'zhuangchang',
                    't': 'json_join,'
                },
                {
                    'n': '个人简介',
                    'En': 'PersonalProfile',
                    'v': 'lawyerinfo',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def sd_law_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        JS_response = json.loads(response.text)
        urls = JS_response['list']
        for url in urls:
            data = urllib.parse.urlencode({'type': 'lawyer', 'orgid': url['id']})
            url = 'http://sd.12348.gov.cn/sftIDC/lawworkmanage/institutioninfo.do'
            yield scrapy.Request(
                url,
                method='POST',
                body=data,
                priority=100,
                headers=self.default_header,
                callback=self.sd_law_firm_info_parse)
        # 废弃代码
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(JS_response, {'t': 'json', 'v': 'totalCount'})) / 10) if S.select_content(JS_response, {'t': 'json', 'v': 'totalCount'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://sd.12348.gov.cn/sftIDC/select/search.do'
        #         data = urllib.parse.urlencode({'page':str(page), 'areacode':'37','order':'','pageSize':'10','type':'lawyer','flag':'0'})
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             method='POST',
        #             body=data,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.sd_law_firm_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json', 'v': 'totalCount'},
            callback=self.sd_law_firm_parse,
            method='POST',
            headers=self.default_header,
            urlfunc=lambda page:'http://sd.12348.gov.cn/sftIDC/select/search.do',
            bodyfunc=lambda page, response:urllib.parse.urlencode({'page':str(page), 'areacode':'','order':'','pageSize':'10','type':'lawfirm','flag':'1','status':'1'}),
            divmod=10,
            response_type='json',
            )
        for req in reqs:
            yield req

    @check_response
    def sd_law_firm_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'json',
                'db': 'dbo.SdLawFirmData',
                'keys': ['LawFirmName'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [{
                'n': '律所名称',
                'En': 'LawFirmName',
                'v': 'result/name',
                't': 'json'
            }, {
                'n': '地址',
                'En': 'Address',
                'v': 'result/address',
                't': 'json'
            }, {
                'n': '所属地区',
                'En': 'AreaName',
                'v': 'result/areaname',
                't': 'json'
            }, {
                'n': '地区编码',
                'En': 'AreaCode',
                'v': 'result/areacode',
                't': 'json'
            }, {
                'n': '颁证日期',
                'En': 'IssueDate',
                'v': 'result/issuedate',
                't': 'json'
            }, {
                'n': '电子邮箱',
                'En': 'EmailAddress',
                'v': 'result/email',
                't': 'json'
            }, {
                'n': '信用代码',
                'En': 'UnifiedSocialCreditCode',
                'v': 'result/ext4',
                't': 'json'
            }, {
                'n': '发证机构',
                'En': 'IssueOrgan',
                'v': 'result/issueorgan',
                't': 'json'
            }, {
                'n': '执业证号',
                'En': 'LicenseNumber',
                'v': 'result/licenceno',
                't': 'json'
            }, {
                'n': '许可证号',
                'En': 'LicenceSerialNo',
                'v': 'result/licenceserialno',
                't': 'json'
            }, {
                'n': '经纬度',
                'En': 'Local_xy',
                'v': 'result/localxy',
                't': 'json'
            },{
                'n': '主管机关',
                'En': 'CompetentAuthorities',
                'v': 'result/organincharge',
                't': 'json'
            }, {
                'n': '组织形式',
                'En': 'OrganizationalForm',
                'v': 'result/organizationalcategory',
                't': 'json'
            }, {
                'n': '合伙人',
                'En': 'Partner',
                'v': 'result/partner',
                't': 'json'
            }, {
                'n': '负责人',
                'En': 'PersonInCharge',
                'v': 'result/personincharge',
                't': 'json'
            }, {
                'n': '邮编',
                'En': 'ZipCode',
                'v': 'result/postcode',
                't': 'json'
            }, {
                'n': '电话号码',
                'En': 'PhoneNumber',
                'v': 'result/tel',
                't': 'json'
            }, {
                'n': '批准日期',
                'En': 'ApproveDate',
                'v': 'result/approvedate',
                't': 'json'
            }, {
                'n': '行政划分',
                'En': 'AdminDivid',
                'v': 'result/admindivid',
                't': 'json'
            }, {
                'n': '机构简介',
                'En': 'AgencyIntroduction',
                'v': 'result/lawfirminfo',
                't': 'json'
            }, {
                'n': '奖励记录',
                'En': 'AwardRecord',
                'v': 'result/jcount',
                't': 'json'
            }, {
                'n': '惩戒记录',
                'En': 'DisciplinaryRecord',
                'v': 'result/cjcount',
                't': 'json'
            }]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def wh_lawyer_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '//table//tr[td[not(@sort)]]',
                't': 'xpath',
                'db': 'dbo.HbLawFirmData',
                'keys': ['LawFirmName'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律所名称',
                    'En': 'LawFirmName',
                    'v': './td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业许可证号',
                    'En': 'LicenseNumber',
                    'v': './td[2]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '组织形式',
                    'En': 'OrganizationalForm',
                    'v': './td[3]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '地址',
                    'En': 'Address',
                    'v': './td[4]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '负责人',
                    'En': 'PersonInCharge',
                    'v': './td[5]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '联系电话',
                    'En': 'ContactNumber',
                    'v': './td[6]/text()',
                    't': 'xpath_first'
                },
            ]
        }, {
            'list': {
                'n': '',
                'v': '//table//tr[td[not(@sort)]]',
                't': 'xpath',
                'db': 'dbo.HbLawyerData',
                'keys': ['LicenseNumber', 'LawyerName'],
                'check': 'LawyerName',
                'conn': False
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律所名称',
                    'En': 'LawFirmName',
                    'v': './td[1]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '律师姓名',
                    'En': 'LawyerName',
                    'v': './td[7]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业证号',
                    'En': 'LicenseNumber',
                    'v': './td[8]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(response, {'t': 'regex1', 'v': '当前第\s*?\d*?\/(\d+)\s*?页'})) / 1) if S.select_content(response, {'t': 'regex1', 'v': '当前第\s*?\d*?\/(\d+)\s*?页'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://www.hbsf.gov.cn:8081/application/onlineWeb/lsjjgList?filter_LIKE_sname=&filter_LIKE_zyxkzh=&filter_LIKE_attorney=&filter_LIKE_zyzh=&sortField=xh&sortDir=ASC&pageNumber=%s&_searchFlag=_searchFlag' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.wh_lawyer_firm_parse)

        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '当前第\s*?\d*?\/(\d+)\s*?页'},
            callback=self.wh_lawyer_firm_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://www.hbsf.gov.cn:8081/application/onlineWeb/lsjjgList?pageNumber=%s&_searchFlag=_searchFlag' % page,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def hn_lawyer_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        print(response.text)

    @check_response
    def gd_lawyer_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': 'rows',
                't': 'json',
                'db': 'dbo.GdLawyerData',
                'keys': ['LawyerName', 'LicenseNumber'],
                'check': 'LawyerName',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '律师姓名',
                    'En': 'LawyerName',
                    'v': 'person_chinese_name',
                    't': 'json'
                },
                {
                    'n': '性别',  # 0 未知  1 男  2 女 3 未说明的性别
                    'En': 'Gender',
                    'v': 'sex',
                    't': 'json'
                },
                {
                    'n': '是否法律顾问',
                    'En': 'IsLawAdviser',
                    'v': 'islawadviser',
                    't': 'json'
                },
                {
                    'n': '人员类型',  #  1 实习人员  2 律师  3  雇员  4 代表  5 公司律师
                    'En': 'CategoryOfPractice',
                    'v': 'person_type',
                    't': 'json'
                },
                {
                    'n': '所属地区',
                    'En': 'AreaName',
                    'v': 'areacode',
                    't': 'json'
                },
                {
                    'n': '律师类别',
                    'En': 'LawyerType',
                    'v': 'lawyer_type',
                    't': 'json'
                },
                {
                    'n': '执业证号',
                    'En': 'LicenseNumber',
                    'v': 'certificate_no',
                    't': 'json'
                },
                {
                    'n': '服务机构',
                    'En': 'LawFirmName',
                    'v': 'orgname',
                    't': 'json'
                },
                {
                    'n': '律师类别',
                    'En': 'LawyerKind',
                    'v': 'lawyer_kind',
                    't': 'json'
                },
                {
                    'n': '身份证号码',
                    'En': 'IdNumber',
                    'v': 'identity_card',
                    't': 'json'
                },
                {
                    'n': '颁证日期',
                    'En': 'IssueDate',
                    'v': 'issue_date',
                    't': 'json'
                },
                {
                    'n': '邮编',
                    'En': 'ZipCode',
                    'v': 'master_dept',
                    't': 'json'
                },
                {
                    'n': '原证书',
                    'En': 'OldLicenseNumber',
                    'v': 'old_cert_no',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        # JS_response = json.loads(response.text)
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(JS_response, {'t': 'json', 'v': 'total'})) / 500) if S.select_content(JS_response, {'t': 'json', 'v': 'total'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://12348.gdsf.gov.cn/front/servItemDataqueryAction.ered?reqCode=dataTypeQuery&querymethod=10&type=1&curpage=%s&limit=500' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.gd_lawyer_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json',
                    'v': 'total'},
            callback=self.gd_lawyer_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://12348.gdsf.gov.cn/front/servItemDataqueryAction.ered?reqCode=dataTypeQuery&querymethod=10&type=1&curpage=%s&limit=9' % page-1,
            divmod=9,  # 默认
            response_type='json',
        )
        for req in reqs:
            yield req

    @check_response
    def gd_law_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': 'rows',
                't': 'json',
                'db': 'dbo.GdLawFirmData',
                'keys': ['LawFirmName', 'LicenseNumber'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'json',
            'data': [
                {
                    'n': '律所名称',
                    'En': 'LawFirmName',
                    'v': 'org_name',
                    't': 'json'
                },
                {
                    'n': '执业证号',
                    'En': 'LicenseNumber',
                    'v': 'cert_code',
                    't': 'json'
                },
                {
                    'n': '律所英文名',
                    'En': 'EnglishFullName',
                    'v': 'eng_name',
                    't': 'json'
                },
                {
                    'n': '总部',
                    'En': 'HeadQuarters',
                    'v': 'master_dept',
                    't': 'json'
                },
                {
                    'n': '联系电话',
                    'En': 'PhoneNumber',
                    'v': 'office_phone',
                    't': 'json'
                },
                {
                    'n':
                    '机构类别',  # 1 合作  2 普通合伙 3 国资  4 个人 5 公职所 6 公司 7 驻澳代表图 8 特殊合伙 9 法援 10 联营机构
                    'En': 'OrganizationalCategory',
                    'v': 'org_type',
                    't': 'json'
                },
                {
                    'n': '执业状态',  # 0 正常 5 停业 6 注销 9 吊销 15 非正常
                    'En': 'StateOfPractice',
                    'v': 'cur_status',
                    't': 'json'
                },
                {
                    'n': '邮编',
                    'En': 'ZipCode',
                    'v': 'zipcode',
                    't': 'json'
                },
                {
                    'n': '负责人',
                    'En': 'PersonInCharge',
                    'v': 'person_chinese_name',
                    't': 'json'
                },
                {
                    'n': '身份证号码',
                    'En': 'IdNumber',
                    'v': 'idcard',
                    't': 'json'
                },
                {
                    'n': '传真',
                    'En': 'FaxNumber',
                    'v': 'fax',
                    't': 'json'
                },
                {
                    'n': '律所面积',
                    'En': 'Areas',
                    'v': 'areage',
                    't': 'json'
                },
                {
                    'n': '律所主页',
                    'En': 'OrgHomePage',
                    'v': 'homepage',
                    't': 'json'
                },
                {
                    'n': '电子邮箱',
                    'En': 'EmailAddress',
                    'v': 'email',
                    't': 'json'
                },
                {
                    'n': '地址',
                    'En': 'Address',
                    'v': 'addreds',
                    't': 'json'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
        # JS_response = json.loads(response.text)
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(JS_response, {'t': 'json', 'v': 'total'})) / 1) if S.select_content(JS_response, {'t': 'json', 'v': 'total'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://12348.gdsf.gov.cn/front/servItemDataqueryAction.ered?reqCode=orgQuery&type=1&curpage=%s&limit=500' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.gd_law_firm_parse)
        # 获取所有列表页
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json',
                    'v': 'total'},
            callback=self.gd_law_firm_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://12348.gdsf.gov.cn/front/servItemDataqueryAction.ered?reqCode=orgQuery&type=1&curpage=%s&limit=9' % page,
            bodyfunc=self.cq_get_rsrf,
            divmod=9,
            response_type='json',
        )
        for req in reqs:
            yield req

    @check_response
    def cq_lawyer_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        with open('cq.html','w',encoding='utf-8') as f:
            f.write(response.text)
        page = response.meta.get('page', 0)
        if page == 0:
            page += 1
            url = 'http://118.178.181.229:8080/Ntalker/lawyers.aspx'
            # data = self.cq_start_data(page,response)
            yield scrapy.Request(
                url,
                method='POST',
                body=self.cq_start_data(page,response),
                headers=self.default_header,
                meta={'page': page},
                callback=self.cq_lawyer_parse)
            return
        # print(response.text)
        urls = response.xpath('//*[@class="lawlysonename"]/a/@href').extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.cq_lawyer_info_parse)
        # 废弃的代码 留存
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(response, {'t': 'regex1', 'v': 'plink\((\d+)\)\"\s*?title=\"最后页'})) / 1) if S.select_content(response, {'t': 'json', 'v': 'total'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://118.178.181.229:8080/Ntalker/lawyers.aspx'
        #         data = self.cq_get_rsrf(response, page)
        #         yield scrapy.Request(
        #             url,
        #             method='POST',
        #             body=data,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.cq_lawyer_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': 'plink\((\d+)\)\"\s*?title=\"最后页'},
            callback=self.cq_lawyer_parse,
            headers=self.default_header,
            method='POST',
            urlfunc=
            lambda x: 'http://118.178.181.229:8080/Ntalker/lawyers.aspx',
            bodyfunc=self.cq_get_rsrf,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def cq_lawyer_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # print(response.text)
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'dbo.CqLawyerData',
                'keys': ['LicenseNumber', 'LawyerName'],
                'check': 'LawyerName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律师姓名',
                    'En': 'LawyerName',
                    'v': '//span[@id="Label1"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '职称',
                    'En': 'Title',
                    'v': '//span[@id="Label2"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '所在律所',
                    'En': 'LawFirmName',
                    'v': '//span[@id="Label3"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '主管机关',
                    'En': 'CompetentAuthorities',
                    'v': '//span[@id="Label4"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '毕业院校',
                    'En': 'School',
                    'v': '//span[@id="Label5"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '民族',
                    'En': 'Nation',
                    'v': '//span[@id="Label6"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '最高学历',
                    'En': 'HighestEducation',
                    'v': '//span[@id="Label7"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '党派',
                    'En': 'Party',
                    'v': '//span[@id="Label8"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '资格证号',
                    'En': 'QualificationCertificateNumber',
                    'v': '//span[@id="Label9"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '资格证取得时间',
                    'En': 'QualificationCertificateGetTime',
                    'v': '//span[@id="Label10"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业证号',
                    'En': 'LicenseNumber',
                    'v': '//span[@id="Label11"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业证取得时间',
                    'En': 'LicenseGetTime',
                    'v': '//span[@id="Label12"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '联系电话',
                    'En': 'ContactNumber',
                    'v': '//span[@id="Label13"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '电子邮箱',
                    'En': 'EmailAddress',
                    'v': '//span[@id="Label14"]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    @check_response
    def cq_law_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        page = response.meta.get('page', 0)
        if page == 0:
            page += 1
            url = 'http://118.178.181.229:8080/Ntalker/lawfirms.aspx'
            data = self.cq_start_data2(page, response)
            yield scrapy.Request(
                url,
                method='POST',
                body=data,
                headers=self.default_header,
                meta={'page': page},
                callback=self.cq_law_firm_parse)
            return
        urls = response.xpath('//*[@class="lawlsname"]/a/@href').extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.cq_law_firm_info_parse)
        # 废弃的代码
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(response, {'t': 'regex1', 'v': 'plink\((\d+)\)\"\s*?title=\"最后页'})) / 1) if S.select_content(response, {'t': 'json', 'v': 'total'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://118.178.181.229:8080/Ntalker/lawfirms.aspx'
        #         data = self.cq_get_rsrf2(response, page)
        #         yield scrapy.Request(
        #             url,
        #             method='POST',
        #             body=data,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.cq_law_firm_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': 'plink\((\d+)\)\"\s*?title=\"最后页'},
            callback=self.cq_law_firm_parse,
            method='POST',
            headers=self.default_header,
            urlfunc=
            lambda x: 'http://118.178.181.229:8080/Ntalker/lawfirms.aspx',
            bodyfunc=self.cq_get_rsrf2,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def cq_law_firm_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'dbo.CqLawFirmData',
                'keys': ['LawFirmName'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律所名称',
                    'En': 'LawFirmName',
                    'v': '//span[@id="Label1"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '执业许可证',
                    'En': 'LicenseNumber',
                    'v': '//span[@id="Label2"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '组织形式',
                    'En': 'OrganizationalForm',
                    'v': '//span[@id="Label4"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '电话',
                    'En': 'PhoneNumber',
                    'v': '//span[@id="Label5"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '主管机关',
                    'En': 'CompetentAuthorities',
                    'v': '//span[@id="Label6"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '传真',
                    'En': 'FaxNumber',
                    'v': '//span[@id="Label7"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '成立时间',
                    'En': 'SetUpTime',
                    'v': '//span[@id="Label8"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '邮编',
                    'En': 'ZipCode',
                    'v': '//span[@id="Label9"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '联系地址',
                    'En': 'ContactAddress',
                    'v': '//span[@id="Label10"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '网址',
                    'En': 'Website',
                    'v': '//span[@id="Label11"]/text()',
                    't': 'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item

    # @check_response
    def sc_lawyer_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        JS_response = json.loads(response.text)
        urls = JS_response['list']
        for url in urls:
            result = url.copy()
            IdNumber = result[5]
            Partner = result[3]
            Org = result[2]
            url = 'http://fwpt.scsf.gov.cn/scssfpt/lvshi/lplvshi!lvshixq.action?lvshiid=%s' % url[
                0]
            yield scrapy.Request(
                url,
                meta={'IdNumber': IdNumber,
                      'Partner': Partner,
                      'Org': Org},
                priority=100,
                headers=self.default_header,
                callback=self.sc_lawyer_info_parse)
        # 废弃
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(JS_response, {'t': 'json', 'v': 'lspageSize'})) / 5) if S.select_content(JS_response, {'t': 'json', 'v': 'lspageSize'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://fwpt.scsf.gov.cn/scssfpt/lvshi/lplvshi!lvshiquery.action?firstname=&city=&lspageNo=%s&zyzh=' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.sc_lawyer_parse)
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json',
                    'v': 'lspageSize'},
            callback=self.sc_lawyer_parse,
            headers=self.default_header,
            urlfunc=
            lambda x: 'http://fwpt.scsf.gov.cn/scssfpt/lvshi/lplvshi!lvshiquery.action?firstname=&city=&lspageNo=%s&zyzh=' % x,
            divmod=5,
            response_type='json',
        )
        for req in reqs:
            yield req

    @check_response
    def sc_lawyer_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        # 字段设置
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'dbo.ScLawyerData',
                'keys': ['IdNumber', 'LawyerName'],
                'check': 'LawyerName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律师名称',
                    'En': 'LawyerName',
                    'v': '//span[@class="font28"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '职务',
                    'En': 'Partner',
                    'v': 'Partner',
                    't': 'meta'
                },
                {
                    'n': '身份证',
                    'En': 'IdNumber',
                    'v': 'IdNumber',
                    't': 'meta'
                },
                {
                    'n':
                    '性别',
                    'En':
                    'Gender',
                    'v':
                    '//td[re:test(text(),"性\s*?别")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '民族',
                    'En':
                    'Nation',
                    'v':
                    '//td[re:test(text(),"民\s*?族")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '政治面貌',
                    'En':
                    'PoliticalOutlook',
                    'v':
                    '//td[re:test(text(),"政治面貌")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '律师职称',
                    'En':
                    'Title',
                    'v':
                    '//td[re:test(text(),"律师职称")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '执业类别',
                    'En':
                    'CategoryOfPractice',
                    'v':
                    '//td[re:test(text(),"执业类别")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '首次执业时间',
                    'En':
                    'FirstPracticeTime',
                    'v':
                    '//td[re:test(text(),"执业时间")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '执业机构',
                    'En':
                    'PractisingInstitution',
                    'v':
                    '//td[re:test(text(),"执业机构")]/following-sibling::td[1]//a/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '律所电话',
                    'En':
                    'PhoneNumber',
                    'v':
                    '//td[re:test(text(),"律所电话")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '联系电话',
                    'En':
                    'ContactNumber',
                    'v':
                    '//td[re:test(text(),"联系电话")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '电子邮箱',
                    'En':
                    'EmailAddress',
                    'v':
                    '//td[re:test(text(),"电子邮箱")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        # 解析字段
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

    @check_response
    def sc_law_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        JS_response = json.loads(response.text)
        urls = JS_response['list']
        for url in urls:

            url = 'http://fwpt.scsf.gov.cn/scssfpt/lvshi/lplvshi!lsuoxq.action?sid=%s' % url[
                1]
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.sc_law_firm_info_parse)

        reqs = self.scrapy_page_help(
            response,
            config={'t': 'json',
                    'v': 'pageSize'},
            callback=self.sc_law_firm_parse,
            headers=self.default_header,
            urlfunc=
            lambda x: 'http://fwpt.scsf.gov.cn/scssfpt/lvshi/lplvshi!lvsuo.action?city=&lvsuoname=&pageNo=%s&lvsuoxkzh=' % x,
            divmod=1,
            response_type='json',
        )
        for req in reqs:
            yield req
        # @废弃
        # page = response.meta.get('page', 1)
        # totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
        #     ceil(int(S.select_content(JS_response, {'t': 'json', 'v': 'pageSize'})) / 1) if S.select_content(JS_response, {'t': 'json', 'v': 'pageSize'})\
        #     else 1
        # if page == 1 and page < totalpage:
        #     for page in range(page + 1, totalpage + 1):
        #         url = 'http://fwpt.scsf.gov.cn/scssfpt/lvshi/lplvshi!lvshiquery.action?firstname=&city=&lspageNo=%s&zyzh=' % page
        #         yield scrapy.Request(
        #             url,
        #             headers=self.default_header,
        #             meta={'page': page,
        #                   'totalpage': totalpage},
        #             callback=self.sc_law_firm_parse)

    def scrapy_info_url_help(
            self,
            response,
            config=None,
            callback=None,
            headers=None,
            urlfunc=None,
            bodyfunc=None,
            response_type='xpath',
            method='GET',
            connect_type='urlencode',
    ):
        urlfunc = urlfunc if urlfunc else lambda x: response.url
        bodyfunc = bodyfunc if bodyfunc else lambda x: ''
        if response_type.lower() == 'json':
            JS_response = json.loads(response.text)
        else:
            JS_response = response
        #  需要拆分
        urls = S.select_content(JS_response, config)
        reqs = set()
        for url in urls:
            url = urlfunc(url)
            body = body(response)
            req = scrapy.Request(
                url,
                method='POST',
                body=body,
                priority=100,
                headers=headers,
                callback=callback)
            reqs.add(req)
        return reqs

    def scrapy_page_help(self,
                         response: Response,
                         config: dict = None,
                         callback: callable = None,
                         headers: dict = None,
                         urlfunc: callable = None,
                         bodyfunc: callable = None,
                         divmod: int = 1,
                         response_type: 'xpath' or 'json' = 'xpath',
                         method: 'GET' or 'POST' = 'GET',
                         flag=False,  # True为下一页翻页，False为生成所有页面
                         pagestart=1,  # 其实页说明
                         connect_type: 'urlencode'
                         or 'json' = 'urlencode') -> scrapy.Request:
        '''
        @ params response  parse的response形参
        @ params config  获取total方法参数  调用S.select_content
        @ callback  回调函数
        @ headers 默认为urlencode
        @ urlfunc  常用lambda函数 
        @ connect_type 决定body的encode方法
        @ response_type 决定参数获取方式
        @ method Request method
        @ divmod 获取到total 后计算totalpage的除数
        @ bodyfunc 常用lambda表达式
        return [Requests]
        '''
        page = response.meta.get('page', 1)
        if page != pagestart or flag:
            return []
        dataencode = urllib.parse.urlencode if connect_type == 'urlencode' else json.loads
        if response_type.lower() == 'json':
            JS_response = json.loads(response.text)
        else:
            JS_response = response
        totalpage = response.meta['totalpage'] if response.meta.get('totalpage') else \
            ceil(int(S.select_content(JS_response, config)) / divmod) if S.select_content(JS_response, config)\
            else 1
        reqs = set()
        logger.info('totalpage is %s' % totalpage)
        # 直接获取最大页码 生成request
        if page < totalpage and not flag:
            for page in range(page + 1, totalpage + 1):
                if callable(bodyfunc):
                    body = bodyfunc(page, response=response)
                    if isinstance(body, str):
                        pass
                    else:
                        body = dataencode(body)
                else:
                    body = None
                if callable(urlfunc):
                    url = urlfunc(page)
                else:
                    url = response.url
                req = scrapy.Request(
                    url,
                    method=method,
                    body=body,
                    headers=headers,
                    meta={'page': page,
                          'totalpage': totalpage},
                    callback=callback)
                reqs.add(req)
        # 下一页判断翻页 
        elif page < totalpage and flag:
            if S.select_content(JS_response, config):
                page += 1
                req = scrapy.Request(
                    url,
                    method=method,
                    body=body,
                    headers=headers,
                    meta={'page': page,
                          'totalpage': totalpage},
                    callback=callback)
                reqs.add(req)
        return reqs

    @check_response
    def sc_law_firm_info_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'dbo.ScLawFirmData',
                'keys': ['LawFirmName'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律所名称',
                    'En': 'LawFirmName',
                    'v': '//span[@class="font28"]/text()',
                    't': 'xpath_first'
                },
                {
                    'n': '许可证编号',
                    'En': 'LicenseNumber',
                    'v': '许可证号\s*?\(\s*?(\d+)\s*?\)',
                    't': 'regex1'
                },
                {
                    'n':
                    '主管机关',
                    'En':
                    'CompetentAuthorities',
                    'v':
                    '//td[re:test(text(),"主管机关")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '组织形式',
                    'En':
                    'OrganizationalForm',
                    'v':
                    '//td[re:test(text(),"组织形式")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '成立时间',
                    'En':
                    'SetUpTime',
                    'v':
                    '//td[re:test(text(),"成立时间")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '负责人',
                    'En':
                    'PersonInCharge',
                    'v':
                    '//td[re:test(text(),"负\s*?责\s*?人")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '律师人数',
                    'En':
                    'LawyersNumber',
                    'v':
                    '//td[re:test(text(),"律师人数")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '网址',
                    'En':
                    'Website',
                    'v':
                    '//td[re:test(text(),"网\s*?址")]/following-sibling::td[1]/a/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '联系电话',
                    'En':
                    'ContactNumber',
                    'v':
                    '//td[re:test(text(),"联系电话")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '电子邮箱',
                    'En':
                    'EmailAddress',
                    'v':
                    '//td[re:test(text(),"电子邮箱")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '地址',
                    'En':
                    'ContactAddress',
                    'v':
                    '//td[re:test(text(),"地\s*?址")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

    @check_response
    def guizhou_entrance_parse(self, response):
        self.guizhou_lawyer_token = self.guizhou_lawyer_token(response)
        self.guizhou_law_firm_token = self.guizhou_law_firm_token(response)
        self.guizhou_page_url = self.guizhou_page_url(response)
        page = response.meta.get('page', 1)
        lawyer_body = self.guizhou_lawyer_data(page)
        law_firm_body = self.guizhou_law_firm_data(page)
        url = 'http://www.gzsft.gov.cn/sitefiles/services/wcm/dynamic/output.aspx?publishmentSystemID=1&num=1'
        yield scrapy.Request(
            url,
            method='POST',
            body=lawyer_body,
            meta={'page': page},
            callback=self.guizhou_lawyer_parse,
            headers=self.default_header)
        yield scrapy.Request(
            url,
            method='POST',
            body=law_firm_body,
            meta={'page': page},
            callback=self.guizhou_law_firm_parse,
            headers=self.default_header)

    @check_response
    def guizhou_lawyer_parse(self, response):
        # print(response.text)
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n':
                '',
                'v':
                '//table[@class="table table-bordered table-hover"]//table[@class="table table-bordered"]',
                't':
                'xpath',
                'db':
                'dbo.GuiZhouLawyerData',
                'keys': ['LicenseNumber', 'LawyerName'],
                'check':
                'LawyerName',
                'conn':
                conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n':
                    '律师姓名',
                    'En':
                    'LawyerName',
                    'v':
                    './/td[re:test(text(),"姓名")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '原执业/工作证号',
                    'En':
                    'OldLicenseNumber',
                    'v':
                    './/td[re:test(text(),"原执业")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '性别',
                    'En':
                    'Gender',
                    'v':
                    './/td[re:test(text(),"性别")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '执业证号码',
                    'En':
                    'LicenseNumber',
                    'v':
                    './/td[re:test(text(),"执业证号码")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '首次执业时间',
                    'En':
                    'FirstPracticeTime',
                    'v':
                    './/td[re:test(text(),"首次执业时间")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '执业/工作类别',
                    'En':
                    'CategoryOfPractice',
                    'v':
                    './/td[re:test(text(),"工作类别")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '执业机构',
                    'En':
                    'PractisingInstitution',
                    'v':
                    './/td[re:test(text(),"执业机构")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '证书流水号',
                    'En':
                    'CertificateSerialNumber',
                    'v':
                    './/td[re:test(text(),"证书流水号")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '兼职律师所在单位',
                    'En':
                    'UnitOfPartTimeLawyer',
                    'v':
                    './/td[re:test(text(),"兼职律师所在单位")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '受到表彰情况',
                    'En':
                    'Commendation',
                    'v':
                    './/td[re:test(text(),"受到表彰情况")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '受到行政处罚情况',
                    'En':
                    'AdministrativeSanction',
                    'v':
                    './/td[re:test(text(),"受到行政处罚情况")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '受到行业惩戒情况',
                    'En':
                    'IndustryDiscipline',
                    'v':
                    './/td[re:test(text(),"受到行业惩戒情况")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item
        # #  翻页逻辑
        reqs = self.scrapy_page_help(
            response,
            config={
                't': 'xpath_first',
                'v': '//select[@class="input-small"]/option[last()]/@value'
            },
            callback=self.guizhou_lawyer_parse,
            headers=self.default_header,
            method='POST',
            urlfunc=
            lambda x: 'http://www.gzsft.gov.cn/sitefiles/services/wcm/dynamic/output.aspx?publishmentSystemID=1&num=1',
            bodyfunc=self.guizhou_lawyer_data,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def guizhou_law_firm_parse(self, response):
        # print(response.text)
        if self.response_failed(response):
            yield self.request_try(response)
            return
        _configs = [{
            'list': {
                'n':
                '',
                'v':
                '//table[@class="table table-bordered table-hover"]/tr[position()>1]//table[@class="table table-bordered"]',
                't':
                'xpath',
                'db':
                'dbo.GuiZhouLawFirmData',
                'keys': ['LawFirmName'],
                'check':
                'LawFirmName',
                'conn':
                conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n':
                    '律所名称',
                    'En':
                    'LawFirmName',
                    'v':
                    './/td[re:test(text(),"事务所中文全称")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '总所/分所',
                    'En':
                    'HeadquartersOrBranch',
                    'v':
                    './/td[re:test(text(),"总所")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '执业许可证号',
                    'En':
                    'LicenseNumber',
                    'v':
                    './/td[re:test(text(),"执业许可证号")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '设立资产(万元)',
                    'En':
                    'EstablishmentOfAssets',
                    'v':
                    './/td[re:test(text(),"设立资产")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '发证日期',
                    'En':
                    'IssueDate',
                    'v':
                    './/td[re:test(text(),"发证日期")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '组织形式',
                    'En':
                    'OrganizationalForm',
                    'v':
                    './/td[re:test(text(),"组织形式")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '批准日期',
                    'En':
                    'DateOfApproval',
                    'v':
                    './/td[re:test(text(),"批准日期")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '批准文号',
                    'En':
                    'ApprovalNumber',
                    'v':
                    './/td[re:test(text(),"批准文号")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '负责人',
                    'En':
                    'PersonInCharge',
                    'v':
                    './/td[re:test(text(),"负责人")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '合伙人',
                    'En':
                    'Partner',
                    'v':
                    './/td[re:test(text(),"合伙人")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '主管机关',
                    'En':
                    'CompetentAuthorities',
                    'v':
                    './/td[re:test(text(),"主管机关")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '发证机关',
                    'En':
                    'IssuingOrgan',
                    'v':
                    './/td[re:test(text(),"发证机关")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '邮编',
                    'En':
                    'ZipCode',
                    'v':
                    './/td[re:test(text(),"邮编")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '联系电话',
                    'En':
                    'ContactNumber',
                    'v':
                    './/td[re:test(text(),"联系电话")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '地址',
                    'En':
                    'Address',
                    'v':
                    './/td[re:test(text(),"地址")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '受到表彰情况',
                    'En':
                    'Commendation',
                    'v':
                    './/td[re:test(text(),"受到表彰情况")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '受到行政处罚情况',
                    'En':
                    'AdministrativeSanction',
                    'v':
                    './/td[re:test(text(),"受到行政处罚情况")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '受到行业惩戒情况',
                    'En':
                    'IndustryDiscipline',
                    'v':
                    './/td[re:test(text(),"受到行业惩戒情况")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item
        #  翻页逻辑
        reqs = self.scrapy_page_help(
            response,
            config={
                't': 'xpath_first',
                'v': '//select[@class="input-small"]/option[last()]/@value'
            },
            callback=self.guizhou_law_firm_parse,
            headers=self.default_header,
            method='POST',
            urlfunc=
            lambda x: 'http://www.gzsft.gov.cn/sitefiles/services/wcm/dynamic/output.aspx?publishmentSystemID=1&num=1',
            bodyfunc=self.guizhou_law_firm_data,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def gs_parse(self, response):
        # response有效性复检  无效最大重试发送新请求
        if self.response_failed(response):
            yield self.request_try(response)
            return

        # url关键参数提取
        _tag = '//ul[@class="lvsuolist"]/li//a/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.gs_info_parse)

        # 翻页逻辑 一次性yield所有page页面
        reqs = self.scrapy_page_help(
            response,
            config={
                't': 'xpath_first',
                'v': '//ul[@class="pagination"]/li[last()-1]/a/text()'
            },
            callback=self.gs_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://www.gslawyer.com/HdApp/HdBas/HdLawFirmMain.asp?ac=lawyers&xianqu=0&xingshi=0&w=&page=%s' % page,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    def request_try(self, response):
        try_times = response.meta.get('try_times', 0)
        if try_times < MAX_TIMES:
            meta = response.meta.copy()
            meta['try_times'] = try_times + 1
            request = response.request.replace(dont_filter=True, meta=meta)
            return request
        else:
            # 记录日志  便于直接获取页面重新获取 正则提取 分别url,body,headers
            logger.error('"%s|%s|%s"try more than %s times,throw out' (
                response.url, response.request.body, response.request.headers,
                MAX_TIMES))

    def gs_info_parse(self, response):
        # response有效性复检  无效最大重试发送新请求
        if self.response_failed(response):
            yield self.request_try(response)
            return

        # 抓取配置
        _configs = [{
            'list': {
                'n': '',
                'v': '',
                't': 'xpath',
                'db': 'dbo.GsLawFirmData',
                'keys': ['LawFirmName'],
                'check': 'LawFirmName',
                'conn': conn_flag
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律所名称',
                    'En': 'LawFirmName',
                    'v': '//p[@class="text1"]//text()',
                    't': 'xpath_first'
                },
                {
                    'n':
                    '律师人数',
                    'En':
                    'LawyersNumber',
                    'v':
                    '//div[@style="float:right; font-size:36px; color:#0069ae; margin-top:-20px;"]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '许可证号',
                    'En':
                    'LicenseNumber',
                    'v':
                    '//th[re:test(text(),"许可证号")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '地址',
                    'En':
                    'Address',
                    'v':
                    '//th[re:test(text(),"地址")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '组织形式',
                    'En':
                    'OrganizationalForm',
                    'v':
                    '//th[re:test(text(),"组织形式")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '电话',
                    'En':
                    'PhoneNumber',
                    'v':
                    '//th[re:test(text(),"电话")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '主任',
                    'En':
                    'PersonInCharge',
                    'v':
                    '//th[re:test(text(),"主任")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
                {
                    'n':
                    '邮编',
                    'En':
                    'ZipCode',
                    'v':
                    '//th[re:test(text(),"邮编")]/following-sibling::td[1]/text()',
                    't':
                    'xpath_first'
                },
            ]
        }, {
            'list': {
                'n': '',
                'v': '//div[@id="ContentDetail"]//text()',
                't': 'xpath',
                'db': 'dbo.GsLawyerData',
                'keys': ['LawyerName', 'LicenseNumber'],
                'check': 'LawyerName',
                'conn': False
            },
            'response_type':
            'xpath',
            'data': [
                {
                    'n': '律所名称',
                    'En': 'LawFirmName',
                    'v': '//p[@class="text1"]//text()',
                    't': 'response_xpath_first'
                },
                {
                    'n': '律师姓名',
                    'En': 'LawyerName',
                    'v': '[^\x00-\xff].*[^\x00-\xff]',
                    't': '.re'
                },
                {
                    'n': '执业证号',
                    'En': 'LicenseNumber',
                    'v': '\d{10,}',
                    't': '.re'
                },
            ]
        }]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

    @check_response
    def henan_law_firm_parse(self, response):
        if self.response_failed(response):
            yield self.request_try(response)
            return

        _tag = "//a[contains(@href,'lsmessage')]/@href"
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                headers=self.default_header,
                # encoding='UTF-8-SIG',
                callback=self.henan_law_firm_info_parse)

        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共(\d+)页'},
            callback=self.henan_law_firm_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://apps.hebei.com.cn/wsbsdt/lssousuo.php?pageNow=%s' % page,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def henan_law_firm_info_parse(self, response):

        if self.response_failed(response):
            yield self.request_try(response)
            return
        # 需要加这个
        response = response.replace(body=response.body.decode('UTF-8-SIG'))

        # 抓取配置
        _configs = [
            {
                'list': {
                    'n': '',
                    'v': '//table',
                    't': 'xpath',
                    'db': 'dbo.HeBeiLawFrimData',
                    'keys': ['LawFirmName'],
                    'check': 'LawFirmName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n':
                        '律所名称',
                        'En':
                        'LawFirmName',
                        'v':
                        '//*[re:test(text(),"事务所名称")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '组织形式',
                        'En':
                        'OrganizationalForm',
                        'v':
                        '//*[re:test(text(),"组织形式")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '许可证号',
                        'En':
                        'LicenseNumber',
                        'v':
                        '//*[re:test(text(),"许可证号")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '住所地址',
                        'En':
                        'Address',
                        'v':
                        '//*[re:test(text(),"住所地址")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '电话',
                        'En':
                        'PhoneNumber',
                        'v':
                        '//*[re:test(text(),"电话")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '所在地区',
                        'En':
                        'AreaName',
                        'v':
                        '//*[re:test(text(),"所在地区")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '邮编',
                        'En':
                        'ZipCode',
                        'v':
                        '//*[re:test(text(),"邮编")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                ]
            },
        ]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

    @check_response
    def gx_lawyer_parse(self, response):
        # 替换一些可能引发错误的内容
        response = response.replace(
            body=response.body.decode('utf-8').replace('\xa9', ''))

        # 提取链接
        _tag = '//div[@class="lawyer_list"]//dt/span/a/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.gx_lawyer_info_parse)
        _tag1 = '//div[@class="lawyer_list"]//dl/dd[1]/a/@href'
        urls = response.xpath(_tag1).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.gx_law_firm_info_parse)

        # 翻页逻辑
        reqs = self.scrapy_page_help(
            response,
            config={
                't': 'xpath_first',
                'v': '//div[@class="page"]/a[last()-1]/text()'
            },
            callback=self.gx_lawyer_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://www.gxlawyer.org.cn/searchLawyer?gender=&practiceScope=43ea076234e049579dd12b9715c6783f&page=%s' % page,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def gx_lawyer_info_parse(self, response):
        # 替换一些可能引发错误的内容
        response = response.replace(
            body=response.body.decode('utf-8').replace('\xa9', ''))
        # 抓取配置
        _configs = [
            {
                'list': {
                    'n': '',
                    'v': '//table',
                    't': 'xpath',
                    'db': 'dbo.GXLawyerData',
                    'keys': ['LawyerName', 'LicenseNumber'],
                    'check': 'LawyerName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n':
                        '律师姓名',
                        'En':
                        'LawyerName',
                        'v':
                        '//td[div[contains(text(),"律师姓名")]]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '律师事务所',
                        'En':
                        'LawFirmName',
                        'v':
                        '//td[div[contains(text(),"律师事务所")]]/following-sibling::td[1]/a/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '性　别',
                        'En':
                        'Gender',
                        'v':
                        '//td[div[contains(text(),"性　别")]]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '民　族',
                        'En':
                        'Nation',
                        'v':
                        '//td[div[contains(text(),"民　族")]]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '政治面貌',
                        'En':
                        'PoliticalOutlook',
                        'v':
                        '//td[div[contains(text(),"政治面貌")]]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '学　历',
                        'En':
                        'Education',
                        'v':
                        '//td[div[contains(text(),"学　历")]]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业范围',
                        'En':
                        'PracticeArea',
                        'v':
                        '//td[div[contains(text(),"执业范围")]]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业类别',
                        'En':
                        'CategoryOfPractice',
                        'v':
                        '//td[div[contains(text(),"执业类别")]]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '首次执业时间',
                        'En':
                        'FirstPracticeTime',
                        'v':
                        '//td[div[contains(text(),"首次执业时间")]]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业证号',
                        'En':
                        'LicenseNumber',
                        'v':
                        '//td[div[contains(text(),"执业证号")]]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业状态',
                        'En':
                        'StateOfPractice',
                        'v':
                        '//td[div[contains(text(),"执业状态")]]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '考核结果',
                        'En':
                        'ExaminationResults',
                        'v':
                        '//td[div[contains(text(),"考核结果")]]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '个人主页',
                        'En':
                        'PersonalHomePage',
                        'v':
                        '//td[div[contains(text(),"个人主页")]]/following-sibling::td[1]/a/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '电子邮箱',
                        'En':
                        'EmailAddress',
                        'v':
                        '//td[div[contains(text(),"E-mail")]]/following-sibling::td[1]/a/text()',
                        't':
                        'xpath_first'
                    },
                ]
            },
        ]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

    @check_response
    def gx_law_firm_info_parse(self, response):
        # 替换一些可能引发错误的内容
        response = response.replace(
            body=response.body.decode('utf-8').replace('\xa9', ''))
        # 抓取配置
        _configs = [
            {
                'list': {
                    'n': '',
                    'v': '//table',
                    't': 'xpath',
                    'db': 'dbo.GxLawFirmData',
                    'keys': ['LawFirmName'],
                    'check': 'LawFirmName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': '律所名称',
                        'En': 'LawFirmName',
                        'v': '//div[@class="office_list"]//h3/a/text()',
                        't': 'xpath_first',
                    },
                    {
                        'n': '执业许可证号',
                        'En': 'LicenseNumber',
                        'v': '//*[contains(text(),"执业许可证号")]/text()',
                        't': 'xpath_re',
                        're': '：(.*)'
                    },
                    {
                        'n': '住所',
                        'En': 'OfficeAddress',
                        'v': '//*[contains(text(),"住所")]/text()',
                        't': 'xpath_re',
                        're': '：(.*)'
                    },
                    {
                        'n': '联络地址',
                        'En': 'ContactAddress',
                        'v': '//*[contains(text(),"联络地址")]/text()',
                        't': 'xpath_re',
                        're': '：(.*)'
                    },
                    {
                        'n': '电话',
                        'En': 'PhoneNumber',
                        'v': '//*[contains(text(),"电话")]/text()',
                        't': 'xpath_re',
                        're': '：(.*)'
                    },
                    {
                        'n': '传真',
                        'En': 'FaxNumber',
                        'v': '//*[contains(text(),"传真")]/text()',
                        't': 'xpath_re',
                        're': '：(.*)'
                    },
                    {
                        'n': '网站',
                        'En': 'Website',
                        'v': '//*[contains(text(),"网站")]/a/text()',
                        't': 'xpath_first',
                    },
                    {
                        'n': '负责人',
                        'En': 'PersonInCharge',
                        'v': '//*[contains(text(),"负责人")]/a/text()',
                        't': 'xpath_first',
                    },
                    {
                        'n': '组织形式',
                        'En': 'OrganizationalForm',
                        'v': '//*[contains(text(),"组织形式")]/text()',
                        't': 'xpath_re',
                        're': '：(.*)'
                    },
                    {
                        'n': '主管机关',
                        'En': 'CompetentAuthorities',
                        'v': '//*[contains(text(),"主管机关")]/text()',
                        't': 'xpath_re',
                        're': '：(.*)'
                    },
                    {
                        'n': '批准日期',
                        'En': 'ApproveDate',
                        'v': '//*[contains(text(),"批准日期")]/text()',
                        't': 'xpath_re',
                        're': '：(.*)'
                    },
                    {
                        'n': '执业状态',
                        'En': 'StateOfPractice',
                        'v': '//*[contains(text(),"执业状态")]/text()',
                        't': 'xpath_re',
                        're': '：(.*)'
                    },
                ]
            },
        ]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

    @check_response
    def nx_lawyer_parse(self, response):
        _tag = '//td[text()="律师姓名"]/../following-sibling::tr[position()>1]//a/@href'
        lawyer_urls = response.xpath(_tag).extract()
        for url in lawyer_urls:
            url = response.urljoin(
                urllib.parse.quote(url, safe='/?&=', encoding='gbk'))
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.nx_lawyer_info_parse)

        page = response.meta['page']
        # '''只访问一次 每页都出现'''
        if page == 1:
            _tag = '//a[contains(@href,"showsws.asp?id=")]/@href'
            law_firm_urls = response.xpath(_tag).extract()
            for url in law_firm_urls:
                url = response.urljoin(url)
                yield scrapy.Request(
                    url,
                    priority=100,
                    headers=self.default_header,
                    callback=self.nx_law_firm_info_parse)

        # 翻页逻辑
        reqs = self.scrapy_page_help(
            response,
            config={
                't':
                'xpath_first',
                'v':
                '//span[@class="jcbh"]/../following-sibling::a[last()]/span/text()'
            },
            callback=self.nx_lawyer_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://www.nxlawyers.org/lsfind.asp?page=%s' % page,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def nx_lawyer_info_parse(self, response):
        response = response.replace(
            body=response.body.decode('gb2312', 'ignore'))
        # print(response.text)
        # 抓取配置
        _configs = [
            {
                'list': {
                    'n': '',
                    'v': '//table',
                    't': 'xpath',
                    'db': 'dbo.NxLawyerData',
                    'keys': ['LawyerName', 'LicenseNumber'],
                    'check': 'LawyerName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': '律师名称',
                        'En': 'LawyerName',
                        'v': '//td[text()="律师详细信息"]/span/text()',
                        't': 'xpath_first',
                    },
                    {
                        'n':
                        '性别',
                        'En':
                        'Gender',
                        'v':
                        '//table//td[contains(text(),"性别：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '民族',
                        'En':
                        'Nation',
                        'v':
                        '//table//td[contains(text(),"民族：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '政治面貌',
                        'En':
                        'PoliticalOutlook',
                        'v':
                        '//table//td[contains(text(),"政治面貌：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '学历',
                        'En':
                        'Education',
                        'v':
                        '//table//td[contains(text(),"学历：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业范围',
                        'En':
                        'PracticeArea',
                        'v':
                        '//table//td[contains(text(),"执业范围：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业类别',
                        'En':
                        'CategoryOfPractice',
                        'v':
                        '//table//td[contains(text(),"执业类别：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first',
                    },
                    {
                        'n':
                        '职称',
                        'En':
                        'Title',
                        'v':
                        '//table//td[contains(text(),"职称：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '联系电话',
                        'En':
                        'ContactNumber',
                        'v':
                        '//table//td[contains(text(),"联系电话：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '首次执业时间',
                        'En':
                        'FirstPracticeTime',
                        'v':
                        '//table//td[contains(text(),"首次执业时间：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业证号',
                        'En':
                        'LicenseNumber',
                        'v':
                        '//table//td[contains(text(),"执业证号：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '个人简介',
                        'En':
                        'PersonalProfile',
                        'v':
                        '//table//td[contains(text(),"个人简介：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_join'
                    },
                    {
                        'n':
                        '个人主页',
                        'En':
                        'PersonalHomePage',
                        'v':
                        '//table//td[contains(text(),"个人主页：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '邮箱',
                        'En':
                        'EmailAddress',
                        'v':
                        '//table//td[contains(text(),"邮箱：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '服务律所',
                        'En':
                        'LawFirmName',
                        'v':
                        '//table//td[contains(text(),"服务律所：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                ]
            },
        ]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

    @check_response
    def nx_law_firm_info_parse(self, response):
        response = response.replace(
            body=response.body.decode('gb2312', 'ignore'))
        # print(response.text)
        # 抓取配置
        _configs = [
            {
                'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'dbo.NxLawFirmData',
                    'keys': ['LawFirmName'],
                    'check': 'LawFirmName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': '律所名称',
                        'En': 'LawFirmName',
                        'v': '//td[text()="详细信息"]/span/text()',
                        't': 'xpath_first',
                    },
                    {
                        'n':
                        '组织形式',
                        'En':
                        'OrganizationalForm',
                        'v':
                        '//table//td[contains(text(),"组织形式：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业许可证号',
                        'En':
                        'LicenseNumber',
                        'v':
                        '//table//td[contains(text(),"执业许可证号：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '负责人',
                        'En':
                        'PersonInCharge',
                        'v':
                        '//table//td[contains(text(),"负责人：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '地址',
                        'En':
                        'Address',
                        'v':
                        '//table//td[contains(text(),"地址：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '邮编',
                        'En':
                        'ZipCode',
                        'v':
                        '//table//td[contains(text(),"邮编：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '联系电话',
                        'En':
                        'ContactNumber',
                        'v':
                        '//table//td[contains(text(),"联系电话：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first',
                    },
                    {
                        'n':
                        '邮箱',
                        'En':
                        'EmailAddress',
                        'v':
                        '//table//td[contains(text(),"邮箱：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first',
                    },
                    {
                        'n':
                        '网址',
                        'En':
                        'Website',
                        'v':
                        '//table//td[contains(text(),"网址：")]/following-sibling::td[1]/a/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '简介',
                        'En':
                        'AgencyIntroduction',
                        'v':
                        '//table//td[contains(text(),"简介：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_join'
                    },
                    {
                        'n':
                        '所属律协',
                        'En':
                        'LawyersAssociation',
                        'v':
                        '//table//td[contains(text(),"所属律协：")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first',
                    },
                ]
            },
        ]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

    @check_response
    def xz_law_firm_info_parse(self, response):
        # print(response.text)

        _configs = [
            {
                'list': {
                    'n':
                    '',
                    'v':
                    '//tr[td[text()="序号"]]/following-sibling::tr[position()<last()]',
                    't':
                    'xpath',
                    'db':
                    'dbo.XzLawFirmData',
                    'keys': ['LawFirmName'],
                    'check':
                    'LawFirmName',
                    'conn':
                    conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': '事务所名称',
                        'En': 'LawFirmName',
                        'v': './td[2]/a/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '执业证号',
                        'En': 'LicenseNumber',
                        'v': './td[3]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '联系电话',
                        'En': 'ContactNumber',
                        'v': './td[4]/text()',
                        't': 'xpath_first'
                    },
                ]
            },
        ]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item
        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={
                't': 'xpath_re',
                'v': '//a[text()="最后一页"]/@href',
                're': '\?page=(\d+)'
            },
            callback=self.xz_law_firm_info_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://oa.xjlx.org/html/index1.asp?page=%s' % page,
            divmod=1,
            response_type='xpath',
        )
        for req in reqs:
            yield req

    @check_response
    def xz_lawyer_info_parse(self, response):

        _configs = [
            {
                'list': {
                    'n':
                    '',
                    'v':
                    '//tr[td[text()="序号"]]/following-sibling::tr[position()<last()]',
                    't':
                    'xpath',
                    'db':
                    'dbo.XzLawyerData',
                    'keys': ['LicenseNumber', 'LawyerName'],
                    'check':
                    'LawyerName',
                    'conn':
                     conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n': '执业律师姓名',
                        'En': 'LawyerName',
                        'v': './td[2]/text()',
                        't': 'xpath_first',
                    },
                    {
                        'n': '律师事务所',
                        'En': 'LawFirmName',
                        'v': './td[3]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '执业证号',
                        'En': 'LicenseNumber',
                        'v': './td[4]/text()',
                        't': 'xpath_first'
                    },
                    {
                        'n': '联系电话',
                        'En': 'ContactNumber',
                        'v': './td[5]/text()',
                        't': 'xpath_first'
                    },
                ]
            },
        ]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item
        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={
                't': 'xpath_re',
                'v': '//a[text()="最后一页"]/@href',
                're': '\?page=(\d+)'
            },
            callback=self.xz_lawyer_info_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://oa.xjlx.org/html/lscx.asp?page=%s' % page,
            divmod=1,
            response_type='xpath')
        for req in reqs:
            yield req

    @check_response
    def sx1_lawyer_parse(self, response):
        '''山西省律师列表'''
        # print(response.text)
        _tag = '//table[@class="danga"]//tr[position()>1]/td[1]/a/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                priority=100,
                headers=self.default_header,
                callback=self.sx1_lawyer_info_parse)
        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共(\d+)页'},
            callback=self.sx1_lawyer_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://sx.sxlsw.org/lvshiS.aspx?page=%s' % page,
            divmod=1,
            response_type='xpath')
        for req in reqs:
            yield req

    def sx1_lawyer_info_parse(self, response):
        # print(response.text)
        _configs = [
            {
                'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'dbo.Sx1LawyerData',
                    'keys': ['LicenseNumber', 'LawyerName'],
                    'check': 'LawyerName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n':
                        '律师姓名',
                        'En':
                        'LawyerName',
                        'v':
                        '//td[contains(text(),"姓名")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first',
                    },
                    {
                        'n': '头像',
                        'En': 'Photo',
                        'v': '//td[@class="tu"]//@src',
                        't': 'xpath_first',
                    },
                    {
                        'n':
                        '姓别',
                        'En':
                        'Gender',
                        'v':
                        '//td[contains(text(),"姓别")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '民族',
                        'En':
                        'Nation',
                        'v':
                        '//td[contains(text(),"民族")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '学历（最高）',
                        'En':
                        'HighestEducation',
                        'v':
                        '//td[contains(text(),"学历")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '毕业院校',
                        'En':
                        'School',
                        'v':
                        '//td[contains(text(),"毕业院校")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '政治面貌',
                        'En':
                        'PoliticalOutlook',
                        'v':
                        '//td[contains(text(),"政治面貌")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '邮编',
                        'En':
                        'ZipCode',
                        'v':
                        '//td[contains(text(),"邮编")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '电子邮箱',
                        'En':
                        'EmailAddress',
                        'v':
                        '//td[contains(text(),"电子邮箱")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '手机号码',
                        'En':
                        'PhoneNumber',
                        'v':
                        '//td[contains(text(),"手机号码")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '单位电话',
                        'En':
                        'OfficeAddress',
                        'v':
                        '//td[contains(text(),"单位电话")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '专/兼职',
                        'En':
                        'FullorPartTime',
                        'v':
                        '//td[contains(text(),"专/兼职")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业证编号',
                        'En':
                        'LicenseNumber',
                        'v':
                        '//td[contains(text(),"执业证编号")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业状态',
                        'En':
                        'StateOfPractice',
                        'v':
                        '//td[contains(text(),"执业状态")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '业务专长',
                        'En':
                        'SpecializedFieldOfLaw',
                        'v':
                        '//td[contains(text(),"业务专长")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '资格证取得日期',
                        'En':
                        'QualificationCertificateGetTime',
                        'v':
                        '//td[contains(text(),"资格证取得日期")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '所属律所',
                        'En':
                        'LawFirmName',
                        'v':
                        '//td[contains(text(),"所属律所")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '是否合伙人',
                        'En':
                        'IsPartner',
                        'v':
                        '//td[contains(text(),"是否合伙人")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '首次执业省市',
                        'En':
                        'FirstPracticeArea',
                        'v':
                        '//td[contains(text(),"首次执业省市")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '首次执业日期',
                        'En':
                        'FirstPracticeTime',
                        'v':
                        '//td[contains(text(),"首次执业日期")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '奖励记录',
                        'En':
                        'AwardRecord',
                        'v':
                        '//tr[td[contains(text(),"奖励记录")]]/following-sibling::tr[1]/td//text()',
                        't':
                        'xpath_join'
                    },
                    {
                        'n':
                        '惩戒记录',
                        'En':
                        'DisciplinaryRecord',
                        'v':
                        '//tr[td[contains(text(),"惩戒记录")]]/following-sibling::tr[1]/td//text()',
                        't':
                        'xpath_join'
                    },
                ]
            },
        ]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

    @check_response
    def sx1_law_firm_parse(self, response):
        '''山西省律所列表'''
        # print(response.text)
        _tag = '//table[@class="danga"]//tr[position()>1]/td[1]/a/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(
                url, 
                headers=self.default_header,
                priority=100,
                callback=self.sx1_law_firm_info_parse)
        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'regex1',
                    'v': '共(\d+)页'},
            callback=self.sx1_law_firm_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://sx.sxlsw.org/index.aspx?page=%s' % page,
            divmod=1,
            response_type='xpath')
        for req in reqs:
            yield req

    @check_response
    def sx1_law_firm_info_parse(self, response):
        # print(response.text)
        _configs = [
            {
                'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'dbo.Sx1LawFirmData',
                    'keys': ['LawFirmName'],
                    'check': 'LawFirmName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n':
                        '事务所中文全称',
                        'En':
                        'LawFirmName',
                        'v':
                        '//td[contains(text(),"事务所中文全称")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first',
                    },
                    {
                        'n':
                        '所在区县',
                        'En':
                        'AreaName',
                        'v':
                        '//td[contains(text(),"所在区县")]/following-sibling::td[1]/span/text()',
                        't':
                        'xpath_json-',
                    },
                    {
                        'n':
                        '英文名称',
                        'En':
                        'EnglishFullName',
                        'v':
                        '//td[contains(text(),"英文名称")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '邮编',
                        'En':
                        'ZipCode',
                        'v':
                        '//td[contains(text(),"邮编")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '事务所地址',
                        'En':
                        'OfficeAddress',
                        'v':
                        '//td[contains(text(),"事务所地址")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '主管司法（厅）局',
                        'En':
                        'CompetentAuthorities',
                        'v':
                        '//td[contains(text(),"主管司法（厅）局")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业许可证号码',
                        'En':
                        'LicenseNumber',
                        'v':
                        '//td[contains(text(),"执业许可证号码")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '总所/分所',
                        'En':
                        'HeadquartersOrBranch',
                        'v':
                        '//td[contains(text(),"总所/分所")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业状态',
                        'En':
                        'CategoryOfPractice',
                        'v':
                        '//td[contains(text(),"执业状态")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '状态说明',
                        'En':
                        'RmarkForState',
                        'v':
                        '//td[contains(text(),"状态说明")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '办公电话',
                        'En':
                        'OfficePhoneNumber',
                        'v':
                        '//td[contains(text(),"办公电话")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '注册资金（万元）',
                        'En':
                        'RegisteredCapital',
                        'v':
                        '//td[contains(text(),"注册资金")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '邮箱',
                        'En':
                        'EmailAddress',
                        'v':
                        '//td[contains(text(),"邮箱")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '传真',
                        'En':
                        'FaxNumber',
                        'v':
                        '//td[contains(text(),"传真")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '律师事务所主任',
                        'En':
                        'PersonInCharge',
                        'v':
                        '//td[contains(text(),"律师事务所主任")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '事务所性质',
                        'En':
                        'lawFirmType',
                        'v':
                        '//td[contains(text(),"事务所性质")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '党支部形式',
                        'En':
                        'Party',
                        'v':
                        '//td[contains(text(),"党支部形式")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '党支部负责人',
                        'En':
                        'PartyInCharge',
                        'v':
                        '//td[contains(text(),"党支部负责人")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '场所面积（平米）',
                        'En':
                        'Areas',
                        'v':
                        '//td[contains(text(),"场所面积")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '场所性质',
                        'En':
                        'AreaNature',
                        'v':
                        '//td[contains(text(),"场所性质")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '律所简介',
                        'En':
                        'AgencyIntroduction',
                        'v':
                        '//tr[td[contains(text(),"律所简介")]]/following-sibling::tr[1]//span[@id="Label3"]/text()',
                        't':
                        'xpath_join'
                    },
                    {
                        'n':
                        '奖励记录',
                        'En':
                        'AwardRecord',
                        'v':
                        '//tr[td[contains(text(),"奖励记录")]]/following-sibling::tr[1]//span[@id="Label4"]/text()',
                        't':
                        'xpath_join'
                    },
                    {
                        'n':
                        '惩戒记录',
                        'En':
                        'DisciplinaryRecord',
                        'v':
                        '//tr[td[contains(text(),"惩戒记录")]]/following-sibling::tr[1]//span[@id="Label5"]/text()',
                        't':
                        'xpath_join'
                    },
                ]
            },
        ]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

    @check_response
    def ah_law_firm_parse(self, response):
        '''安徽省律所列表'''
        # print(response.text)
        _tag = '//tr[contains(@class,"title_cont01")]//a/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url, 
                priority=100,
                callback=self.ah_law_firm_info_parse)
        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re',
                    'v': '//a[contains(text(),"尾页")]/@href',
                    're': 'pid=(\d+)'},
            callback=self.ah_law_firm_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://flfw.ahsft.gov.cn/lssws/index.jsp?pid=%s' % page,
            divmod=1,
            response_type='xpath')
        for req in reqs:
            yield req

    @check_response
    def ah_law_firm_info_parse(self, response):
        # print(response.text)
        _configs = [
            {
                'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'dbo.AhLawFirmData',
                    'keys': ['LawFirmName'],
                    'check': 'LawFirmName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n':
                        '律所名称',
                        'En':
                        'LawFirmName',
                        'v':
                        '//td[contains(text(),"律所名称")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first',
                    },
                    {
                        'n':
                        '律所简称',
                        'En':
                        'LawFirmShortName',
                        'v':
                        '//td[contains(text(),"律所简称")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first',
                    },
                    {
                        'n':
                        '执业证号',
                        'En':
                        'LicenseNumber',
                        'v':
                        '//td[contains(text(),"执业证号")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '发证机关',
                        'En':
                        'IssueOrgan',
                        'v':
                        '//td[contains(text(),"发证机关")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '发证日期',
                        'En':
                        'IssueDate',
                        'v':
                        '//td[contains(text(),"发证日期")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '律所地址',
                        'En':
                        'LawFirmAddress',
                        'v':
                        '//td[contains(text(),"律所地址")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '业务范围',
                        'En':
                        'BusinessExpertise',
                        'v':
                        '//td[contains(text(),"业务范围")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '负责人',
                        'En':
                        'PersonInCharge',
                        'v':
                        '//td[re:test(text(),"负.*?责.*?人")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '合伙人',
                        'En':
                        'Partner',
                        'v':
                        '//td[re:test(text(),"合.*?伙.*?人")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '电话',
                        'En':
                        'PhoneNumber',
                        'v':
                        '//td[re:test(text(),"电.*?话")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业状态',
                        'En':
                        'StateOfPractice',
                        'v':
                        '执业状态[^<]*?<[^>]*?>[^<]*?<[^>]*?>(.*?)<',
                        't':
                        'regex1'
                    },
                    {
                        'n':
                        '协会主管',
                        'En':
                        'HeadOfAssociation',
                        'v':
                        '协会主管[^<]*?<[^>]*?>[^<]*?<[^>]*?>(.*?)<',
                        't':
                        'regex1'
                    },
                    {
                        'n':
                        '行政主管',
                        'En':
                        'ExecutiveDirector',
                        'v':
                        '行政主管[^<]*?<[^>]*?>[^<]*?<[^>]*?>(.*?)<',
                        't':
                        'regex1'
                    },
                    {
                        'n':
                        '组织形式',
                        'En':
                        'OrganizationalForm',
                        'v':
                        '组织形式[^<]*?<[^>]*?>[^<]*?<[^>]*?>(.*?)<',
                        't':
                        'regex1'
                    },
                    
                ]
            },
        ]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

    @check_response
    def ah_lawyer_parse(self, response):
        '''安徽省律师列表'''
        # print(response.text)
        _tag = '//tr[contains(@class,"title_cont01")]//a[1]/@href'
        urls = response.xpath(_tag).extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url, 
                priority=100,
                callback=self.ah_lawyer_info_parse)
        '''翻页逻辑'''
        reqs = self.scrapy_page_help(
            response,
            config={'t': 'xpath_re',
                    'v': '//a[contains(text(),"尾页")]/@href',
                    're': 'pid=(\d+)'},
            callback=self.ah_lawyer_parse,
            headers=self.default_header,
            urlfunc=
            lambda page: 'http://flfw.ahsft.gov.cn/ls/index.jsp?pid=%s' % page,
            divmod=1,
            response_type='xpath')
        for req in reqs:
            yield req

    @check_response
    def ah_lawyer_info_parse(self, response):
        # print(response.text)
        _configs = [
            {
                'list': {
                    'n': '',
                    'v': '',
                    't': 'xpath',
                    'db': 'dbo.AhLawyerData',
                    'keys': ['LawyerName', 'LicenseNumber'],
                    'check': 'LawyerName',
                    'conn': conn_flag
                },
                'response_type':
                'xpath',
                'data': [
                    {
                        'n':
                        '姓名',
                        'En':
                        'LawyerName',
                        'v':
                        '//td[contains(text(),"姓名")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first',
                    },
                    {
                        'n':
                        '照片',
                        'En':
                        'Photo',
                        'v':
                        '//td[contains(text(),"照片")]/following-sibling::td[1]/img/@src',
                        't':
                        'xpath_first',
                    },
                    {
                        'n':
                        '性别',
                        'En':
                        'Gender',
                        'v':
                        '//td[contains(text(),"性别")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业证号',
                        'En':
                        'LicenseNumber',
                        'v':
                        '//td[contains(text(),"执业证号")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业状态',
                        'En':
                        'StateOfPractice',
                        'v':
                        '//td[contains(text(),"执业状态")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '执业证类别',
                        'En':
                        'FullorPartTime',
                        'v':
                        '//td[contains(text(),"执业证类别")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '颁发日期',
                        'En':
                        'IssueDate',
                        'v':
                        '//td[contains(text(),"颁发日期")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '律师职称',
                        'En':
                        'Title',
                        'v':
                        '//td[re:test(text(),"律师职称")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '联系电话',
                        'En':
                        'ContactNumber',
                        'v':
                        '//td[re:test(text(),"联系电话")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '专长',
                        'En':
                        'SpecializedFieldOfLaw',
                        'v':
                        '//td[re:test(text(),"专长")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '律师事务所',
                        'En':
                        'LawFirmName',
                        'v':
                        '//td[contains(text(),"律师事务所")]/following-sibling::td[1]/a/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '文化程度',
                        'En':
                        'Education',
                        'v':
                        '//td[re:test(text(),"文化程度")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    {
                        'n':
                        '颁发机关',
                        'En':
                        'IssueOrgan',
                        'v':
                        '//td[re:test(text(),"颁发机关")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    }, {
                        'n':
                        '合伙人标识',
                        'En':
                        'IsPartner',
                        'v':
                        '//td[re:test(text(),"合伙人标识")]/following-sibling::td[1]/text()',
                        't':
                        'xpath_first'
                    },
                    
                ]
            },
        ]
        results = self.item_parse(_configs, response, response)
        for item in results:
            yield item

# if __name__ == '__main__':
#     # 代码美化工具 don't care
#     from yapf.yapflib.yapf_api import FormatFile
#     FormatFile(__file__, in_place=True)
