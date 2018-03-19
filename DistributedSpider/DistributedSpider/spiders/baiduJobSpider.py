# coding:utf-8


import scrapy,json,pymssql,math,re, sys,os


from user_agent import generate_user_agent
from SpiderHelp import SpiderHelp
from jsonpath import jsonpath


conn_flag = False

def get_manager():
    
    conn = pymssql.connect('10.1.18.35', user="sa",
                           password="8927968", database="Haifeng.CrawlerData")
    cursor = conn.cursor()
    sql = "select fundManagerName from AMAC.Amac_privateFundManager"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return (i[0] for i in result)


class BaisuSpider(scrapy.Spider, SpiderHelp):
    name = 'baidu_jobspider'
    start_urls = list(get_manager())
    # managers = set(start_urls)


    @property
    def headers(self):
        return {'User-Agent': generate_user_agent(),
                'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',}

    def start_requests(self):
        for manager in self.start_urls:
            # test
            # manager = '北京好租科技发展有限公司'
            url = 'http://zhaopin.baidu.com/api/quanzhiasync?query={manager}'.format(manager=manager)
            fmt = url + '&pn={pn}&rn={rn}'
            yield scrapy.Request(url,
                headers=self.headers,
                meta={'manager': manager, 'fmt': fmt},
                callback=self.baidu_search)

    @SpiderHelp.check_response
    def baidu_com(self, response):
        # 提取结构化数据

        # 公司基本信息
        _configs = [{
                'list': {
                        'n': '',
                        'v': '',
                        't': 'xpath',
                        'db': 'JobSpider.BaiduComBaseInfo',
                        'keys': ['officialname'],
                        'check': 'officialname',
                        'conn': conn_flag
                        },
                'response_type':
                    'xpath',
                    'data': [
                        {
                            'n': '公司名称',
                            'En': 'officialname',
                            'v': '//div[@class="content"]//span[@class="title line-clamp1"]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '公司logo',
                            'En': 'ComLogo',
                            'v': '//div[@class="logo"]//@src',
                            't': 'xpath_first',
                        },  {
                            'n': '公司官网',
                            'En': 'website',
                            'v': '//div[@class="content"]//text()[contains(string(.),"公司官网")]/following-sibling::a[1]//@href',
                            't': 'xpath_first',
                        },  {
                            'n': '总部地点',
                            'En': 'headPlace',
                            'v': '//div[@class="base items-firm-details"]//p/text()[contains(string(.),"总部地点")]',
                            't': 'xpath_re',
                            're': '总部地点[:：](.+)'
                        },  {
                            'n': '所属行业',
                            'En': 'industry',
                            'v': '//div[@class="base items-firm-details"]//p/text()[contains(string(.),"所属行业")]',
                            't': 'xpath_re',
                            're': '所属行业[:：](.+?)(?:公司福利)'
                        },  {
                            'n': '公司福利',
                            'En': 'welfare',
                            'v': '//div[@class="base items-firm-details"]//p/text()[contains(string(.),"公司福利")]',
                            't': 'xpath_re',
                            're': '公司福利[:：](.+)'
                        },  {
                            'n': '公司简介',
                            'En': 'Profile',
                            'v': '//div[@class="desc"]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '工商注册号',
                            'En': 'regCode',
                            'v': '//td[text()="工商注册号："]/following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '组织机构代码',
                            'En': 'orgcode',
                            'v': '//td[text()="组织机构代码："]/following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '统一信用代码',
                            'En': 'CreditCode',
                            'v': '//td[text()="统一信用代码："]/following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '经营状态',
                            'En': 'opState',
                            'v': '//td[text()="经营状态："]/following-sibling::td[1]/text()y',
                            't': 'xpath_first',
                        },  {
                            'n': '企业类型',
                            'En': 'ComType',
                            'v': '//td[text()="企业类型："]/following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '法定代表人',
                            'En': 'LegalMan',
                            'v': '//td[text()="法定代表人："]/following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '营业期限开始',
                            'En': 'opFrome',
                            'v': '//td[text()="营业期限："]/following-sibling::td[1]/text()',
                            't': 'xpath_re',
                            're': '(.*?)至'
                        },  {
                            'n': '营业期限截至',
                            'En': 'opTo',
                            'v': '//td[text()="营业期限："]/following-sibling::td[1]/text()',
                            't': 'xpath_re',
                            're': '至(.+)'
                        },  {
                            'n': '注册资本',
                            'En': 'regCapital',
                            'v': '//td[text()="注册资本："]/following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '核准日期',
                            'En': 'approvalDate',
                            'v': '//td[text()="核准日期："]/following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '登记机关',
                            'En': 'regOrg',
                            'v': '//td[text()="登记机关："]/following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '企业地址',
                            'En': 'address',
                            'v': '//td[text()="企业地址："]/following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '经营范围',
                            'En': 'scope',
                            'v': '//td[text()="经营范围："]/following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '电子邮箱',
                            'En': 'contact_email',
                            'v': '//td[text()="电子邮箱："]/following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '企业联系电话',
                            'En': 'contact_tel',
                            'v': '//td[text()="企业联系电话："]/following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': 'keywords',
                            'En': 'keywords',
                            'v': 'manager',
                            't': 'meta',
                        }, 
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
            # print(item)

        # 对外投资
        _configs = [{
                'list': {
                        'n': '',
                        'v': '//div[contains(@class,"fxxx items-firm-details")]//div[contains(@class,"fxxx-li") and .//div[@class="sub-title"]/text()]',
                        't': 'xpath',
                        'db': 'JobSpider.BaiduOutInvestment',
                        'keys': ['officialname', 'ComName', 'turns'],
                        'check': 'officialname',
                        'conn': conn_flag
                        },
                'response_type':
                    'xpath',
                    'data': [
                        {
                            'n': '公司名称',
                            'En': 'ComName',
                            'v': './/div[@class="sub-title"]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '融资阶段',
                            'En': 'turns',
                            'v': './/div[@class="sub-title"]/i/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '公司logo',
                            'En': 'ComLogo',
                            'v': './/div[@class="image"]//@src',
                            't': 'xpath_first',
                        },  {
                            'n': '投资公司',
                            'En': 'officialname',
                            'v': '//div[@class="content"]//span[@class="title line-clamp1"]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': 'keywords',
                            'En': 'keywords',
                            'v': 'manager',
                            't': 'meta',
                        }, 
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
            # print(item)

        # 股东信息
        _configs = [{
                'list': {
                        'n': '',
                        'v': '//div[contains(@class,"gszc items-firm-details")]/div[.//span[text()="股东信息"]]//table//tr[position()>1]',
                        't': 'xpath',
                        'db': 'JobSpider.BaiduShare',
                        'keys': ['officialname', 'shName','shType'],
                        'check': 'officialname',
                        'conn': conn_flag
                        },
                'response_type':
                    'xpath',
                    'data': [
                        {
                            'n': '股东类型',
                            'En': 'shType',
                            'v': './td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '股东',
                            'En': 'shName',
                            'v': './td[2]/text()',
                            't': 'xpath_first',
                        },   {
                            'n': '认缴出资（金额/时间）',
                            'En': 'Amt',
                            'v': './td[3]/text()',
                            't': 'xpath_first',
                        },   {
                            'n': '认缴比例',
                            'En': 'fundedRitio',
                            'v': './td[4]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '投资公司',
                            'En': 'officialname',
                            'v': '//div[@class="content"]//span[@class="title line-clamp1"]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': 'keywords',
                            'En': 'keywords',
                            'v': 'manager',
                            't': 'meta',
                        }, 
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
            # print(item)

        # 主要人员
        _configs = [{
                'list': {
                        'n': '',
                        'v': '//div[contains(@class,"gszc items-firm-details")]/div[.//span[text()="主要人员"]]//td[@class="tr-title"]',
                        't': 'xpath',
                        'db': 'JobSpider.BaiduMainPerson',
                        'keys': ['officialname', 'Name', 'Pos'],
                        'check': 'officialname',
                        'conn': conn_flag
                        },
                'response_type':
                    'xpath',
                    'data': [
                        {
                            'n': '公司名称',
                            'En': 'Name',
                            'v': './following-sibling::td[1]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': '职务',
                            'En': 'Pos',
                            'v': './text()',
                            't': 'xpath_re',
                            're': '(.+)[:：]'
                        },  {
                            'n': '投资公司',
                            'En': 'officialname',
                            'v': '//div[@class="content"]//span[@class="title line-clamp1"]/text()',
                            't': 'xpath_first',
                        },  {
                            'n': 'keywords',
                            'En': 'keywords',
                            'v': 'manager',
                            't': 'meta',
                        }, 
                ]
            }]
        results = self.item_parse(_configs, response)
        for item in results:
            yield item
            # print(item)

    @SpiderHelp.check_response
    def baidu_search(self, response):

        '''
        json path  获取以关键词(之前的次匹配
        jsonpath(JS,'$..disp_data[?(@.officialname^="北京海峰科技有限责任公司")].officialname')
        '''

        com_tag = '$..disp_data[?(@.officialname=="%s")].company_id' % response.meta['manager']
        # 翻页
        page = response.meta.get('page',1)
        try:
            JS = json.loads(response.text)
        except:
            print(response.text)
        
        totalpage = response.meta.get('totalpage',0) or math.ceil(int(jsonpath(JS,'$..listNum')[0])/20)
        if page < totalpage:
            yield  scrapy.Request(response.meta['fmt'].format(pn=20*page,rn=20),
                            headers=self.headers,
                            meta={'manager': response.meta['manager'],'page': page+1,'totalpage': totalpage, 'fmt': response.meta['fmt']},
                            callback=self.baidu_search)

        match = response.xpath('//*[@class="result-num"]//text()[string(.)>0]')
        data = jsonpath(JS,'$..disp_data')[0]
        

        if not data:
            # 无数据 结束
            return
        # # 提取结构化数据
        # _configs = [{
        #         'list': {
        #                 'n': '',
        #                 'v': 'data/main/data/disp_data',
        #                 't': 'json',
        #                 'db': 'JobSpider.BaiduJob',
        #                 'keys': ['officialname', 'jobid','url','jobtitle', 'md5_str'],
        #                 'check': 'officialname',
        #                 'conn': conn_flag
        #                 },
        #         'response_type':
        #             'json',
        #             'data': [
        #                 {
        #                     'n': '公司名称',
        #                     'En': 'officialname',
        #                     'v': 'officialname',
        #                     't': 'json',
        #                 }, {
        #                     'n': '公司名称',
        #                     'En': 'jobid',
        #                     'v': '@id',
        #                     't': 'json',
        #                 },  {
        #                     'n': 'urlfrom',
        #                     'En': 'url',
        #                     'v': 'url',
        #                     't': 'json',
        #                 },  {
        #                     'n': '标题',
        #                     'En': 'jobtitle',
        #                     'v': 'title',
        #                     't': 'json',
        #                 },  {
        #                     'n': '招聘类型',
        #                     'En': 'jobtype',
        #                     'v': 'type',
        #                     't': 'json',
        #                 },  {
        #                     'n': '发布时间',
        #                     'En': 'startdate',
        #                     'v': 'startdate',
        #                     't': 'json',
        #                 },  {
        #                     'n': '有效日期',
        #                     'En': 'enddate',
        #                     'v': 'enddate',
        #                     't': 'json',
        #                 },  {
        #                     'n': 'Email',
        #                     'En': 'contact_email',
        #                     'v': 'contact_email',
        #                     't': 'json',
        #                 },  {
        #                     'n': '联系电话',
        #                     'En': 'contact_tel',
        #                     'v': 'contact_tel',
        #                     't': 'json',
        #                 },  {
        #                     'n': '联系微信',
        #                     'En': 'contact_wx',
        #                     'v': 'contact_wx',
        #                     't': 'json',
        #                 },  {
        #                     'n': '最后修改时间',
        #                     'En': 'lastmod',
        #                     'v': 'lastmod',
        #                     't': 'json',
        #                 },  {
        #                     'n': '工作描述',
        #                     'En': 'description',
        #                     'v': 'description',
        #                     't': 'json',
        #                 },  {
        #                     'n': '经纬度',
        #                     'En': 'lbs_crd',
        #                     'v': 'lbs_crd',
        #                     't': 'json',
        #                 },  {
        #                     'n': '地址',
        #                     'En': 'location',
        #                     'v': 'location',
        #                     't': 'json',
        #                 },  {
        #                     'n': '行业',
        #                     'En': 'industry',
        #                     'v': 'industry',
        #                     't': 'json',
        #                 },  {
        #                     'n': '职业分类1',
        #                     'En': 'jobfirstclass',
        #                     'v': 'jobfirstclass',
        #                     't': 'json',
        #                 },  {
        #                     'n': '职业分类2',
        #                     'En': 'jobsecondclass',
        #                     'v': 'jobsecondclass',
        #                     't': 'json',
        #                 },  {
        #                     'n': 'md5_str',
        #                     'En': 'md5_str',
        #                     'v': 'md5_str',
        #                     't': 'json',
        #                 },  {
        #                     'n': '招聘人数',
        #                     'En': 'numbers',
        #                     'v': 'number',
        #                     't': 'json',
        #                 },  {
        #                     'n': '年龄限制',
        #                     'En': 'Age',
        #                     'v': 'age',
        #                     't': 'json',
        #                 },  {
        #                     'n': '区域',
        #                     'En': 'area',
        #                     'v': 'area',
        #                     't': 'json',
        #                 },  {
        #                     'n': '所在城市',
        #                     'En': 'city',
        #                     'v': 'city',
        #                     't': 'json',
        #                 },  {
        #                     'n': '学历要求',
        #                     'En': 'education',
        #                     'v': 'education',
        #                     't': 'json',
        #                 },  {
        #                     'n': '经验要求',
        #                     'En': 'experience',
        #                     'v': 'experience',
        #                     't': 'json',
        #                 },  {
        #                     'n': '企业类型',
        #                     'En': 'employertype',
        #                     'v': 'employertype',
        #                     't': 'json',
        #                 },  {
        #                     'n': '薪资',
        #                     'En': 'salary',
        #                     'v': 'salary',
        #                     't': 'json',
        #                 },  {
        #                     'n': '性别要求',
        #                     'En': 'Gender',
        #                     'v': 'sex',
        #                     't': 'json',
        #                 },  {
        #                     'n': '来源站',
        #                     'En': 'Source',
        #                     'v': 'source',
        #                     't': 'json',
        #                 },  {
        #                     'n': '公司对应站主页',
        #                     'En': 'employerurl',
        #                     'v': 'employerurl',
        #                     't': 'json',
        #                 },  {
        #                     'n': '公司描述',
        #                     'En': 'companydescription',
        #                     'v': 'companydescription',
        #                     't': 'json',
        #                 },  {
        #                     'n': '部门',
        #                     'En': 'depart',
        #                     'v': 'depart',
        #                     't': 'json',
        #                 },   {
        #                     'n': '福利待遇',
        #                     'En': 'welfare',
        #                     'v': 'welfare',
        #                     't': 'json_join',
        #                 },   {
        #                     'n': 'keywords',
        #                     'En': 'keywords',
        #                     'v': 'manager',
        #                     't': 'meta',
        #                 }, 
        #         ]
        #     }]
        # results = self.item_parse(_configs, response)
        # for _item in results:
        #     item = _item.copy()
        #     try:
        #         item['result']['salary_min'],item['result']['salary_max'] = item['result']['salary'].split('-')
        #         item['result']['salary_union'] = '元/月'
        #     except:
        #         pass
        #     yield(item)
        #     # print(item)
        # 标准化数据
        _configs = [{
                'list': {
                        'n': '',
                        'v': 'data/main/data/disp_data',
                        't': 'json',
                        'db': 'JobSpider.BaiduJobCleanData',
                        'keys': ['CropFullName', 'URL', 'JobTitleTmp', 'StartDate'],
                        'check': 'CropFullName',
                        'conn': conn_flag
                        },
                'response_type':
                    'json',
                    'data': [
                        {
                            'n': '公司名称',
                            'En': 'CropFullName',
                            'v': 'officialname',
                            't': 'json',
                        }, 
                        {
                            'n': '原标题',
                            'En': 'JobTitleTmp',
                            'v': 'title',
                            't': 'json',
                        },  {
                            'n': '薪资',
                            'En': 'Salary',
                            'v': 'salary',
                            't': 'json'
                        },  {
                            'n': '经验要求',
                            'En': 'Experience',
                            'v': 'experience',
                            't': 'json',
                        },  {
                            'n': '所在城市',
                            'En': 'Location',
                            'v': 'city',
                            't': 'json',
                        },  {
                            'n': '所在省',
                            'En': 'Province',
                            'v': 'province',
                            't': 'json',
                        },  {
                            'n': '街道',
                            'En': 'District',
                            'v': 'district',
                            't': 'json',
                        },  {
                            'n': '学历要求',
                            'En': 'Education',
                            'v': 'education',
                            't': 'json',
                        },  {
                            'n': '发布时间',
                            'En': 'StartDate',
                            'v': 'startdate',
                            't': 'json',
                        },  {
                            'n': '有效日期',
                            'En': 'EndDate',
                            'v': 'enddate',
                            't': 'json',
                        },  {
                            'n': 'urlfrom',
                            'En': 'URL',
                            'v': 'url',
                            't': 'json',
                        },  {
                            'n': '来源站点',
                            'En': 'Source',
                            'v': 'source',
                            't': 'json_join',
                        },   {
                            'n': '招聘人数',
                            'En': 'NumberOfRecruitment',
                            'v': 'number',
                            't': 'json',
                        },  {
                            'n': '工作描述',
                            'En': 'Description',
                            'v': 'description',
                            't': 'json',
                        },  
                ]
            }]
        results = self.item_parse(_configs, response)
        for _item in results:
            item = _item.copy()
            if item['result'].get('CropFullName') not in self.start_urls:
                continue
            if item['result'].get('Salary') == '0-1':
                item['result']['Salary'] = '面议'
            else:
                item['result']['Salary'] = '' or item['result']['Salary']
                item['result']['SalaryTmp'] = item['result']['Salary']
            if '-' in item['result']['Salary']:
                item['result']['SalaryLow'],item['result']['SalaryHigh'] = item['result']['Salary'].split('-')
            elif item['result']['Salary'] != '面议':
                item['result']['SalaryLow'],item['result']['SalaryHigh'] = item['result']['Salary'], None
            item['result']['JobTitle'] = re.sub('[\(\（].*?[\)\）]','',item['result']['JobTitleTmp'])
            yield(item)
            # print(item)

        # if page == 1:
        #     #公司信息页面
            
        #     try:
        #         company_id = jsonpath(JS, com_tag)[0]
        #     except TypeError:
        #         pass
        #     else:
        #         company_url = 'http://zhaopin.baidu.com/company?query=%s' % company_id
        #         yield scrapy.Request(company_url,
        #             headers=self.headers,
        #             meta={'manager': response.meta['manager']},
        #             callback=self.baidu_com)


    def baidu_job_detail(self, response):
        pass


