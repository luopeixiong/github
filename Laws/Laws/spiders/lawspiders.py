# -*- coding: utf-8 -*-
import scrapy
from user_agent import generate_user_agent
from .myselector import Selector as S
from Laws.items import LawsItem
class LawspidersSpider(scrapy.Spider):
    name = "lawspiders"
#    allowed_domains = ["None"]
    start_urls = ['http://www.gslawyer.com/HdApp/HdBas/HdLawFirmMain.asp?ac=lawyers',#gs 甘肃
                  'http://www.gslawyer.com/HdApp/HdBas/HdLawFirmMain.asp?ac=lawfirm',#gs 甘肃
                  'http://218.60.147.121:8080/lnlxoa/govhall/lawFirmResult.jsp',#ln 辽宁
                  'http://218.60.147.121:8080/lnlxoa/govhall/lawyerResult.jsp',#ln 辽宁
                  'http://www.hbsf.gov.cn:8081/application/onlineWeb/lsjjgList',#hb 湖北
                  'http://wsbs.gdsf.gov.cn/front/search.ered?reqCode=orgQueryInit',#gd
                  'http://12348.gdsf.gov.cn/front/servItemDataqueryAction.ered?reqCode=dataTypeInit&itemid=2015082714175924211&areaVal=undefined&persontype=&name=&no=&org=&itemNo=LS0003',#广东
                  'http://www.rufa.gov.cn/index?pageId=4028c78d519042e60151905462a800e2&action=lawfirm',#hn 湖南
                  'http://36.7.109.3:9012/ls/',#ah 安徽
                  'http://36.7.109.3:9012/lssws/',#ah 安徽
                  'http://law.jxsf.gov.cn/Default.aspx?Type=3',#jx
                  'http://xzsp.sdsft.gov.cn/gea/appprochiswebshow/queryAllReturnListtwo.do',#sd 山东
                  'http://sft.hebei.com.cn/wsbsdt/lsyw/lsswscx/',#hb 河北
                  #黑龙江 暂无'http://www.hljls.org.cn/project/index.php?c=sws&a=list&id=34&title=&zyzh=&quyu=%E5%93%88%E5%B0%94%E6%BB%A8%E5%B8%82',# hlz 黑龙江
                  'http://www.gzsft.gov.cn/channels/11.html',#gz 贵州
                  'http://218.94.1.186:8090/lawyerIntegrity/#/lawyer/lawyerList',#js 江苏
                  'http://218.94.1.186:8090/lawyerIntegrity/#/lawoffice/lawofficeList',#js 江苏
                  'http://zj.12348.gov.cn/public/find/find_lawyer.jsp',#zj 浙江 这个麻烦
                  'http://zj.12348.gov.cn/public/find/find_org.jsp',#zj 浙江 这个麻烦
                  'http://www.fjsf.gov.cn/fjsf/lawOffice.do?task=slist&year=0',#fj 福建
                  'http://www.fjsf.gov.cn/fjsf/lawMemberLawer.do?task=slist&year=0',#fj 福建
                  'http://fwpt.scsf.gov.cn/scssfpt/content/lsquery/lawyer_lvshi.jsp',#sc 四川
                  'http://fwpt.scsf.gov.cn/scssfpt/content/lsquery/lawyer_lvsuo.jsp',#sc 四川
                  'http://old.cdjustice.chengdu.gov.cn/ssh23/platform/lpusermode!search.action',#cd 成都
                  'http://old.cdjustice.chengdu.gov.cn/ssh23/platform/lpgroupmode!searchMap.action',#cd 成都 解析地图 easy
                  'http://www.sxsf.gov.cn/public/sxsfww/ggflfw/wsbs/lsfw.html',#sx 陕西
                  'http://www.sxsf.gov.cn/public/sxsfww/ggflfw/wsbs/lsfw.html',#sx 陕西
                  'http://60.28.163.201:8091/lawyer/home/office-list.html',#tj 天津
                  'http://60.28.163.201:8091/lawyer/home/lawyer-list.html',#tj 天津
                  'https://credit.justice.gov.cn/subjects.jsp?typeId=10d341aea6674146b36dd23c25090f04&zoneId=All&partWord=',#sh 上海
                  'https://credit.justice.gov.cn/subjects.jsp?typeId=41cb822a0fcd46dda5af6da58283b35d&zoneId=All&partWord=',#sh 上海
                  'http://www.gzlawyer.org/integrity/b183746b294a4e78ab35ae87b4ccadc7',#gz 广州
                  'http://www.gzlawyer.org/integrity/146e5ce8cd5945468604bae08c2a7b48',#gz 广州
                  'http://app.bjsf.gov.cn/tabid/220/Default.aspx',#bj 北京
                  'http://app.bjsf.gov.cn/tabid/219/Default.aspx',#bj 北京
                  'http://www.szlawyers.com/lawyer-list']#sz 深圳
    sz_lawyers = []
    sz_lawfirms = []
    szpage = 1
    bjpage = 1
    custom_settings = {
                        "CONCURRENT_REQUESTS": 16 ,  #并发数
                        "CONCURRENT_REQUESTS_PER_DOMAIN": 8 ,#网站并发数
                        "CONCURRENT_REQUESTS_PER_IP": 2#单IP并发数
                        }
    def start_requests(self):
        for url in self.start_urls:
            headers = {"User-Agent":generate_user_agent()}
            if url == 'http://www.szlawyers.com/lawyer-list':
                yield scrapy.Request(url,
                                     headers=headers,
                                     callback=self.szparse)
            elif url == 'http://app.bjsf.gov.cn/tabid/219/Default.aspx':
                yield scrapy.Request(url,
                                     headers=headers,
                                     callback=self.bjparse)
            elif url == 'http://app.bjsf.gov.cn/tabid/220/Default.aspx':
                yield scrapy.Request(url,
                                     headers=headers,
                                     callback=self.bjparse2)
    def bjparse2(self, response):
        headers = {"user-agent":generate_user_agent()}
        rsrf = response.xpath("//input[@name='__VIEWSTATE']/@value").extract_first()
#        print(rsrf)
        if self.bjpage==1:
            self.bjtotalpage = float(response.xpath("//span[@id='ess_ctr706_LawyerSearchList_lblPageInfo']/text()[2]").extract_first().split("/")[-1])
#            print(self.bjtotalpage )

        data = {"__EVENTTARGET":"ess$ctr706$LawyerSearchList$lbtnGoto",
                "__EVENTARGUMENT":"",
                "__VIEWSTATE":rsrf,
                "__VIEWSTATEENCRYPTED":"",
                "ScrollTop":"",
                "__essVariable":'{"__scdoff":"1"}',
                "ess$ctr706$LawyerSearchList$txtName":"",
                "ess$ctr706$LawyerSearchList$txtCodeNum":"",
                "ess$ctr706$LawyerSearchList$txtOfficeName":"",
                "ess$ctr706$LawyerSearchList$ddlType":"-1",
                "ess$ctr706$LawyerSearchList$txtPageNum":str(self.bjpage)
                }
#        #http://www.bjsf.gov.cn/publish/portal0/tab196/?itemid=1037490
        urls = response.xpath("//tr[@class='datagrid-Item']/td[1]/a/@href|//tr[@class='datagrid-Alter']/td[1]/a/@href").extract()
        for url in urls:
            itemid = url.split("=")[-1]
            url = "http://app.bjsf.gov.cn/tabid/239/Default.aspx?itemid={itemid}".format(itemid = itemid)
            print(url)
            yield scrapy.Request(url,
                                 method="GET",
                                 headers = headers,
                                 callback=self.bj_lawyer_parse)
        if self.bjpage<self.bjtotalpage:
            self.bjpage += 1

            yield scrapy.FormRequest('http://app.bjsf.gov.cn/tabid/220/Default.aspx',
                                     formdata=data,
                                     method="POST",
                                     headers = headers,
                                     callback=self.bjparse2)
    def bj_lawyer_parse(self, response):
        item = LawsItem()
        configs = [ {'n':'姓名',"En":"name","v":"//span[@id='ess_ctr742_LawyerView_lblName']/text()",'t':'xpath_first'},
                    {'n':'性别',"En": "grade", "v": "//span[@id='ess_ctr742_LawyerView_lblSex']/text()",'t':'xpath_first'},
                    {'n':'头像image',"En": "Image", "v": "//img[@id='ess_ctr742_LawyerView_Image1']/@src",'t':'xpath_first'},
                    {'n':'出生日期',"En": "birthday", "v": "//span[@id='ess_ctr742_LawyerView_lblBirthday']/text()",'t':'xpath_first'},
                    {'n':'民族',"En": "Folk", "v": "//span[@id='ess_ctr742_LawyerView_lblFolk']/text()",'t':'xpath_first'},
                    {'n':'学历',"En": "education", "v": "//span[@id='ess_ctr742_LawyerView_lblEdu']/text()",'t':'xpath_first'},
                    {'n':'专业',"En": "Speciality", "v": "//span[@id='ess_ctr742_LawyerView_lblSpeciality']/text()",'t':'xpath_first'},
                    {'n':'政治面貌',"En": "Party", "v": "//span[@id='ess_ctr742_LawyerView_lblParty']/text()",'t':'xpath_first'},
                    {'n':'宗教信仰',"En": "Religion", "v": "//span[@id='ess_ctr742_LawyerView_lblReligion']/text()",'t':'xpath_first'},
                    {'n':'是否合伙人',"En": "IsCopartner", "v": "//span[@id='ess_ctr742_LawyerView_lblIsCopartner']/text()",'t':'xpath_first'},
                    {'n':'首次人合伙人时间',"En": "Frist_Partncy_Type", "v": "//span[@id='ess_ctr742_LawyerView_lblFrist_Partncy_Type']/text()",'t':'xpath_first'},
                    {'n':'证书类别',"En": "Competency_Type", "v": "//span[@id='ess_ctr742_LawyerView_lblCompetency_Type']/text()",'t':'xpath_first'},
                    {'n':'资格证取得日期',"En": "Competency_Date", "v": "//span[@id='ess_ctr742_LawyerView_lblCompetency_Date']/text()",'t':'xpath_first'},
                    {'n':'首次执业省市',"En": "First_City", "v": "//span[@id='ess_ctr742_LawyerView_lblFirst_City']/text()",'t':'xpath_first'},
                    {'n':'首次执业日期',"En": "First_Date", "v": "//span[@id='ess_ctr742_LawyerView_lblFirst_Date']/text()",'t':'xpath_first'},
                    {'n':'单位电话',"En": "HomeTel'", "v": "//span[@id='ess_ctr742_LawyerView_lblHomeTel']/text()",'t':'xpath_first'},
                    {'n':'邮编',"En": "ZIP", "v": "//span[@id='ess_ctr742_LawyerView_lblZIP']/text()",'t':'xpath_first'},
                    {'n':'具有何国永久居留权',"En": "GreenCard", "v": "//span[@id='ess_ctr742_LawyerView_lblGreenCard']/text()",'t':'xpath_first'},
                    {'n':'执业状态',"En": "Status", "v": "//span[@id='ess_ctr742_LawyerView_lblStatus']/text()",'t':'xpath_first'},
                    {'n':'部门',"En": "Department", "v": "//span[@id='ess_ctr742_LawyerView_lblDepartment']/text()",'t':'xpath_first'},
                    {'n':'职务',"En": "Post", "v": "//span[@id='ess_ctr742_LawyerView_lblPost']/text()",'t':'xpath_first'},
                    {'n':'执业证号',"En": "Certificate_Code", "v": "//span[@id='ess_ctr742_LawyerView_lblCertificate_Code']/text()",'t':'xpath_first'},

                    ]
        result = dict()
        for config in configs:
            result[config['En']] = S.select_content(response, config)
            result[config['En']] = S.replace_all(result[config['En']])
        result['city'] = 'bj'
        item['result'] = result
        item['keys'] = []
        item['db'] = ''
        yield item
    def bjparse(self, response):
        headers = {"user-agent":generate_user_agent()}
        rsrf = response.xpath("//input[@name='__VIEWSTATE']/@value").extract_first()
        if self.bjpage==1:
            self.bjtotalpage = float(response.xpath("//span[@id='ess_ctr740_LawOfficeSearchList_lblPageInfo']/text()[2]").extract_first().split("/")[-1])
            print(self.bjtotalpage )

        data = {"__EVENTTARGET":"ess$ctr740$LawOfficeSearchList$lbtnGoto",
                "__EVENTARGUMENT":"",
                "__VIEWSTATE":rsrf,
                "__VIEWSTATEENCRYPTED":"",
                "ScrollTop":"295",
                "__essVariable":'{"__scdoff":"1","__ess_pageload":"__ess_setScrollTop();"}',
                "ess$ctr740$LawOfficeSearchList$txtName":"",
                "ess$ctr740$LawOfficeSearchList$txtCodeNum":"",
                "ess$ctr740$LawOfficeSearchList$txtReponseName":"",
                "ess$ctr740$LawOfficeSearchList$ddlType":"1",
                "ess$ctr740$LawOfficeSearchList$ddlCountry":"-1",
                "ess$ctr740$LawOfficeSearchList$txtPageNum":str(self.bjpage)
                }
        #http://app.bjsf.gov.cn/tabid/238/Default.aspx?itemid=125688
        urls = response.xpath("//tr[@class='datagrid-Item']/td[1]/a/@href|//tr[@class='datagrid-Alter']/td[1]/a/@href").extract()
        for url in urls:
            itemid = url.split("=")[-1]
            url = "http://app.bjsf.gov.cn/tabid/238/Default.aspx?itemid={itemid}".format(itemid = itemid)
            yield scrapy.Request(url,
                                 method="GET",
                                 headers = headers,
                                 callback=self.bj_lawfirm_parse)
        if self.bjpage<self.bjtotalpage:
            self.bjpage += 1

            yield scrapy.FormRequest('http://app.bjsf.gov.cn/tabid/219/Default.aspx',
                                     formdata=data,
                                     method="POST",
                                     headers = headers,
                                     callback=self.bjparse)
    def bj_lawfirm_parse(self, response):
        item = LawsItem()
        result = {}
        configs = [
            {"n":"name","v":"//span[@id='ess_ctr741_LawOfficeView_lblName']/text()"},
            {"n": "Ename", "v": "//span[@id='ess_ctr741_LawOfficeView_lblEName']/text()"},
            {"n": "ADDRESS", "v": "//span[@id='ess_ctr741_LawOfficeView_lblADDRESS']/text()"},
            {"n": "MAILCODE", "v": "//span[@id='ess_ctr741_LawOfficeView_lblMAILCODE']/text()"},
            {"n": "CITY", "v": "//span[@id='ess_ctr741_LawOfficeView_lblCITY']/text()"},
            {"n": "SUPERINTEND_OFFICE", "v": "//span[@id='ess_ctr741_LawOfficeView_lblSUPERINTEND_OFFICE']/text()"},
            {"n": "Business_Code", "v": "//span[@id='ess_ctr741_LawOfficeView_lblBusiness_Code']/text()"},
            {"n": "CERTIFICATE_DATE", "v": "//span[@id='ess_ctr741_LawOfficeView_lblCERTIFICATE_DATE']/text()"},
            {"n": "DIRECTOR", "v": "//span[@id='ess_ctr741_LawOfficeView_lblDIRECTOR']/text()"},
            {"n": "IF_HQ", "v": "//span[@id='ess_ctr741_LawOfficeView_lblIF_HQ']/text()"},
            {"n": "Status", "v": "//span[@id='ess_ctr741_LawOfficeView_lblStatus']/text()"},
            {"n": "state_explain", "v": "//span[@id='ess_ctr741_LawOfficeView_lblstate_explain']/text()"},
            {"n": "organize_format", "v": "//span[@id='ess_ctr741_LawOfficeView_lblorganize_format']/text()"},
            {"n": "capital", "v": "//span[@id='ess_ctr741_LawOfficeView_lblcapital']/text()"},
            {"n": "tel", "v": "//span[@id='ess_ctr741_LawOfficeView_lbltel']/text()"},
            {"n": "fax", "v": "//span[@id='ess_ctr741_LawOfficeView_lblfax']/text()"},
            {"n": "email", "v": "//span[@id='ess_ctr741_LawOfficeView_lblemail']/text()"},
            {"n": "homepage", "v": "//span[@id='ess_ctr741_LawOfficeView_lblhomepage']/text()"},
            {"n": "location_area", "v": "//span[@id='ess_ctr741_LawOfficeView_lbllocation_area']/text()"},
            {"n": "partybranch", "v": "//span[@id='ess_ctr741_LawOfficeView_lblpartybranch']/text()"},
            {"n": "party_director", "v": "//span[@id='ess_ctr741_LawOfficeView_lblparty_director']/text()"},
            {"n": "brief_introduction", "v": "//span[@id='ess_ctr741_LawOfficeView_lblbrief_introduction']/p/text()"}
        ]
        for config in configs:
            result[config['n']] = response.xpath(config['v']).extract()
            if result[config['n']]:
                result[config['n']] = "".join(result[config['n']])
            else:
                result[config['n']] = ''
        result['url']=response.url
        result['city'] = 'bj'
        item['result'] = result
        item['keys'] = []
        item['db'] = ''
        yield item
    def szparse(self, response):
        if self.szpage == 1:
            self.sztotalPage = float(response.xpath("//a[text()='下一页']/preceding-sibling::a[1]/text()").extract_first())
            print(self.sztotalPage)
        configs = {"list":{'t':'','v':"//table[@class='tab_list']/tbody/tr[position()>1]",'dt':''},
                   "data":[{"n":'律师ID','En':'lawyerID','t':'xpath','v':'td[1]/a/@href','dt':''},
                           {"n":'事务所ID','En':'lawfirmID','t':'xpath','v':'td[4]/a/@href','dt':''}]}
        for info in response.xpath(configs['list']['v']):
            headers = {"User-Agent":generate_user_agent()}
            result = dict()
            for config in configs['data']:
                result[config['En']] = info.xpath(config['v']).extract_first()
                if result[config['En']]:
                    result[config['En']] = result[config['En']].split("/")[-1]
            if result['lawyerID'] and result['lawyerID'] not in self.sz_lawyers:
                self.sz_lawyers.append(result['lawyerID'])
                lawyer_url = "http://www.szlawyers.com/lawyer/{lawyerID}".format(lawyerID=result['lawyerID'])
                yield scrapy.Request(lawyer_url,
                                     headers=headers,
                                     meta = {"lawyerID":result['lawyerID'],'lawfirmID':result['lawfirmID']},
                                     callback=self.sz_lawyer_parse)
            if result['lawfirmID'] and result['lawfirmID'] not in self.sz_lawfirms:
                self.sz_lawfirms.append(result['lawfirmID'])
                lawfirm_url = "http://www.szlawyers.com/lawfirm/{lawfirmID}".format(lawfirmID=result['lawfirmID'])
                yield scrapy.Request(lawfirm_url,
                                     headers=headers,
                                     meta = {'lawfirmID':result['lawfirmID']},
                                     callback=self.sz_lawfirm_parse)
        if self.szpage < self.sztotalPage:
            self.szpage+=1
            headers = {"User-Agent":generate_user_agent()}
            url = 'http://www.szlawyers.com/lawyer-list?page={page}'.format(page=self.szpage)
            yield scrapy.Request(url,
                                 headers=headers,
                                 callback=self.szparse)
    def sz_lawyer_parse(self, response):
        item = LawsItem()
        configs = [{"n":'姓名','En':'lawyer_name','t':'xpath_first','v':'//span[@id="lawlist_LawerName"]/text()','dt':''},
                    {"n":'英文名','En':'lawyercym','t':'xpath_first','v':'//span[@id="lawlist_cym"]/text()','dt':''},
                    {"n":'性别','En':'lawyer_Enterprise','t':'xpath_first','v':'//span[@id="lawlist_Enterprise"]/text()','dt':''},
                    {"n":'所属事务所','En':'lawyer_Enterprise','t':'xpath_first','v':'//span[@id="lawlist_Enterprise"]/text()','dt':''},
                    {"n":'专业类型  ','En':'lawyer_Class','t':'xpath_first','v':'//span[@id="lawlist_Class"]/text()','dt':''},
                    {"n":'资格证号  ','En':'lawyer_LawerqualNo','t':'xpath_first','v':'//span[@id="lawlist_LawerqualNo"]/text()','dt':''},
                    {"n":'取得律师资格证时间  ','En':'lawyer_dtLawerqua','t':'xpath_first','v':'//span[@id="lawlist_dtLawerqualNo"]/text()','dt':''},
                    {"n":'执业证号  ','En':'lawyer_LawNo','t':'xpath_first','v':'//span[@id="lawlist_LawNo"]/text()','dt':''},
                    {"n":'取得律师执业证时间  ','En':'lawyer_qdzyzsj','t':'xpath_first','v':'//span[@id="lawlist_qdzyzsj"]/text()','dt':''},
                    {"n":'在深圳开始执业时间  ','En':'lawyer_zszkszysj','t':'xpath_first','v':'//span[@id="lawlist_zszkszysj"]/text()','dt':''},
                    {"n":'政治面貌  ','En':'lawyer_zzmm','t':'xpath_first','v':'//span[@id="lawlist_zzmm"]/text()','dt':''},
                    {"n":'工作语言  ','En':'lawyer_gzyy','t':'xpath_first','v':'//span[@id="lawlist_gzyy"]/text()','dt':''},
                    {"n":'业务专长','En':'Label18','t':'xpath_join','v':'//span[@id="lawlist_Label18"]/parent::td/parent::tr/following-sibling::tr[1]/td[1]/span/text()','dt':''},
                    {"n":'ID','En':'lawyer_ID','t':'meta','v':'lawyerID','dt':''},
                    {"n":'律所ID','En':'lawfirmID','t':'meta','v':'lawfirmID','dt':''}
                    ###还有一些字段为补上，常空
                    ]
        result = dict()
        for config in configs:
            result[config['En']] = S.select_content(response, config)
            result[config['En']] = S.replace_all(result[config['En']])
        result['city'] = 'sz'
        item['result'] = result
        item['keys'] = []
        item['db'] = ''
        yield item
    def sz_lawfirm_parse(self, response):
        item = LawsItem()
        configs = [{"n":'事务所名称	','En':'lawfirm_name','t':'xpath_join','v':'//td[text()="事务所名称"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'英文名称','En':'lawfirm_Ename','t':'xpath_join','v':'//td[text()="英文名称"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'主管机关','En':'Competent_organ','t':'xpath_join','v':'//td[text()="主管机关"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'执业证号','En':'Practice_number','t':'xpath_join','v':'//td[text()="执业证号"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'统一社会信用代码','En':'Uniform_code','t':'xpath_join','v':'//td[text()="统一社会信用代码"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'设立时间','En':'setup_date','t':'xpath_join','v':'//td[text()="设立时间"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'组织形式','En':'org_form','t':'xpath_join','v':'//td[text()="组织形式"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'负责人','En':'lawfirm_head','t':'xpath_join','v':'//td[text()="负责人"]/following-sibling::td[1]/a/text()','dt':''},
                    {"n":'派驻律师','En':'Accredited_lawyer','t':'xpath_join','v':'//td[text()="派驻律师"]/following-sibling::td[1]/a/text()','dt':''},
                    {"n":'合伙人','En':'lawfirm_Partner','t':'xpath_split','v':'//td[text()="合伙人"]/following-sibling::td[1]/span/a/text()','dt':''},
                    {"n":'律师人数	','En':'lawfirm_nums','t':'xpath_join','v':'//td[text()="律师人数"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'执业律师','En':'lawyers','t':'xpath_join','v':'//td[text()="执业律师"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'办公地址','En':'work_loction','t':'xpath_join','v':'//td[text()="办公地址"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'邮政编码','En':'Postal_Code','t':'xpath_join','v':'//td[text()="邮政编码"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'总机电话','En':'telephone','t':'xpath_join','v':'//td[text()="总机电话"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'传真号码	','En':'fox','t':'xpath_join','v':'//td[text()="传真号码"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'电子邮箱	','En':'email','t':'xpath_join','v':'//td[text()="电子邮箱"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'单位网址','En':'website','t':'xpath_join','v':'//td[text()="单位网址"]/following-sibling::td[1]/a/text()','dt':''},
                    {"n":'事务所简介','En':'lawfirm_introduction','t':'xpath_join','v':'//td[text()="事务所简介"]/following-sibling::td[1]/text()','dt':''},
                    {"n":'事务所ID','En':'lawfirm_ID','t':'meta','v':'lawfirmID','dt':''}

                    ]
        result = {}
        for config in configs:
            result[config['En']] = S.select_content(response, config)
            result[config['En']] = S.replace_all(result[config['En']])
        result['city'] = 'sz'
        item['result'] = result
        item['keys'] = []
        item['db'] = ''
        yield item

