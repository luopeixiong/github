#!usr/bin/python
# -*-  coding:utf-8 -*-


from selenium import webdriver
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapy import Selector
import pymssql,time


def get_manager():
    
    conn = pymssql.connect('10.1.18.35', user="sa",
                           password="8927968", database="Haifeng.CrawlerData", charset='utf8')
    cursor = conn.cursor()
    sql = "select fundManagerName from AMAC.Amac_privateFundManager"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return (i[0] for i in result)



chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--no-sandbox')

class Spider(object):
    def __init__(self):
        self.conn = pymssql.connect('localhost', user="sa",
                           password="8927968", database="Haifeng.CrawlerData", charset='utf8')
        self.cursor = self.conn.cursor()
        # self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver = webdriver.Chrome()
        self.driver.get('http://www.tianyancha.com')
        self.driver.maximize_window()
        self.keywords = list(get_manager())[:-5000]
        self.keyword = ''
        self.nums = 1
        self.wait = 10
        while True:
            a = input('START Y/N')
            if a.lower().startswith('y'):
                break

    def get(self):
        if self.keywords:
            self.keyword = self.keywords.pop()
            # self.keyword = '北京海峰科技有限责任公司'
            js = 'window.location.href = "https://www.tianyancha.com/search?key=%s"' % self.keyword
            self.driver.execute_script(js)
            self._response()
            if self.nums % 51 == 0:
                time.sleep(50)
            if self.nums % 201 == 0:
                time.sleep(50)
            else:
                time.sleep(self.wait)
            self.nums +=1
            if '503 Service Temporarily Unavailable' in self.text or 'antirobot.tianyancha.com' in self.driver.current_url:
                try:
                    self.wait = int(input('pass'))
                except:
                    pass
            return 1
        else:
            return 0

    def switch_Home(self):
        self.driver.close()
        handles = self.driver.window_handles
        self.driver.switch_to_window(handles[0])
    

    def switch_com(self):
        handles = self.driver.window_handles
        self.driver.switch_to_window(handles[1])
        time.sleep(0.1)
        self.driver.implicitly_wait(30)

    def _response(self):
        self.text = self.driver.page_source
        self.response = Selector(text=self.text)

    def com_in(self):
        result = self.response.xpath('string(//div[@class="b-c-white search_result_container"]//div[@class="search_right_item ml10"][1]//a/span)').extract_first()
        if result and (result in self.keyword or self.keyword in result):
            com_in = self.driver.find_element_by_xpath('//div[@class="b-c-white search_result_container"]//a[1]')
            self.driver.execute_script("arguments[0].scrollIntoView();", com_in)
            self.driver.find_element_by_xpath("//body").send_keys(Keys.UP) 
            self.driver.find_element_by_xpath("//body").send_keys(Keys.UP) 
            self.driver.find_element_by_xpath("//body").send_keys(Keys.UP) 
            time.sleep(0.1)
            com_in.click()

            self.switch_com()
            return 1
        else:
            return 0

    def parse_first(self):
        response_x = Selector(text = self.driver.page_source)
        keyword = self.keyword
        for sel in response_x.xpath('//div[@id="_container_recruit"]//tr[td]'):
            Name = response_x.xpath('//span[@class="f18 in-block vertival-middle sec-c2"]/text()').extract_first('')
            PushDate = sel.xpath('string(./td[1])').extract_first()
            Pos_name = sel.xpath('string(./td[2])').extract_first()
            Work_exp = sel.xpath('string(./td[3])').extract_first()
            Nums = sel.xpath('string(./td[4])').extract_first()
            Work_place = sel.xpath('string(./td[5])').extract_first()
            Json_content = sel.xpath('string(./td[7])').extract_first()
            # print(date, pos_name, work_exp, nums, work_place, json_content)
            sql = "insert into JobSpider.Tianyancha_Job (Name,PushDate,Pos_name,Work_exp,Nums,Work_place,Json_content,keyword) \
            values ('%s','%s','%s','%s','%s','%s','%s','%s')"
            print(sql % (Name,PushDate,Pos_name,Work_exp,Nums,Work_place,Json_content,keyword))
            try:
                self.cursor.execute(sql % (Name,PushDate,Pos_name,Work_exp,Nums,Work_place,Json_content,keyword))
                self.conn.commit()
            except BaseException as e:
                print('%r' % e)

    def parse_company(self):
        Url = self.driver.current_url 
        keyword = self.keyword

        response_x = Selector(text = self.driver.page_source)
        Name = response_x.xpath('//span[@class="f18 in-block vertival-middle sec-c2"]/text()[string(.)!="添加" and string(.)!="编辑"]').extract_first('')
        Tel = response_x.xpath('//span[text()="电话："]/following-sibling::span[1]/text()[string(.)!="添加" and string(.)!="编辑"]').extract_first('')
        Email = response_x.xpath('//span[text()="邮箱："]/following-sibling::span[1]/text()[string(.)!="添加" and string(.)!="编辑"]').extract_first('')
        Website = response_x.xpath('//span[text()="网址："]/following-sibling::span[1]/text()[string(.)!="添加" and string(.)!="编辑"]').extract_first('')
        Address= response_x.xpath('//span[text()="地址："]/following-sibling::span[1]/text()[string(.)!="添加" and string(.)!="编辑"]').extract_first('')
        Profile = response_x.xpath('//*[@id="company_base_info_detail"]/text()').extract_first('')
        LegalMan = response_x.xpath('//div[@class="human-top"]//div[@class="f18 overflow-width sec-c3"]/a/text()').extract_first('')
        Status = response_x.xpath('//div[@class="baseinfo-module-content-value statusType1"]/text()').extract_first('')
        Capital = response_x.xpath('string(//td[div[text()="注册资本"]]/following-sibling::td[div/em/font]//em)').extract_first('')
        RegistrationNum = response_x.xpath('string(//td[text()="工商注册号"]/following-sibling::td[1])').extract_first('')
        OrganizationCode = response_x.xpath('string(//td[text()="组织机构代码"]/following-sibling::td[1])').extract_first('')
        UnifiedCreditCode = response_x.xpath('string(//td[text()="统一信用代码"]/following-sibling::td[1])').extract_first('')
        CompanyType = response_x.xpath('string(//td[text()="公司类型"]/following-sibling::td[1])').extract_first('')
        Taxpayer = response_x.xpath('string(//td[text()="纳税人识别号"]/following-sibling::td[1])').extract_first('')
        Industry = response_x.xpath('string(//td[text()="行业"]/following-sibling::td[1])').extract_first('')
        BussinessTerm = response_x.xpath('string(//td[text()="营业期限"]/following-sibling::td[1])').extract_first('')
        ApprovalDate = response_x.xpath('string(//td[text()="核准日期"]/following-sibling::td[1])').extract_first('')
        RegistrationAuthority = response_x.xpath('string(//td[text()="登记机关"]/following-sibling::td[1])').extract_first('')
        EnglishName = response_x.xpath('string(//td[text()="英文名称"]/following-sibling::td[1])').extract_first('')
        RegAddress = response_x.xpath('string(//td[text()="注册地址"]/following-sibling::td[1])').extract_first('')
        OperationScope = response_x.xpath('string(//td[text()="经营范围"]/following-sibling::td[1]//span/text())').extract_first('')
        sql = "insert into JobSpider.Tianyancha_Com (Name,Tel,Email,Website,Address,Profile,LegalMan,Status,Capital,RegistrationNum,OrganizationCode,\
        UnifiedCreditCode,CompanyType,Taxpayer,Industry,BussinessTerm,ApprovalDate,RegistrationAuthority,EnglishName,\
        RegAddress,OperationScope,Url,keyword ) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',\
        '%s','%s','%s','%s','%s','%s' )"
        print(sql % (Name,Tel,Email,Website,Address,Profile,LegalMan,Status,Capital,RegistrationNum,OrganizationCode,
            UnifiedCreditCode,CompanyType,Taxpayer,Industry,BussinessTerm,ApprovalDate,RegistrationAuthority,EnglishName,
            RegAddress,OperationScope,Url,keyword))
        try:
            self.cursor.execute(sql % (Name,Tel,Email,Website,Address,Profile,LegalMan,Status,Capital,RegistrationNum,OrganizationCode,
            UnifiedCreditCode,CompanyType,Taxpayer,Industry,BussinessTerm,ApprovalDate,RegistrationAuthority,EnglishName,
            RegAddress,OperationScope,Url,keyword))
            self.conn.commit()
        except BaseException as e:
            print('%r' % e)

    def find(self, tag):
        try:
            self.driver.find_element_by_xpath(tag)
            return 1
        except:
            return 0

    def get_next(self, totalpage):
        response_x = Selector(text = self.driver.page_source)
        this_page = int(response_x.xpath('//div[@id="_container_recruit"]//li[@class="pagination-page  active "]/a/text()[string(.)>0]').extract_first('0'))
        if this_page < totalpage:
            page = this_page +1
            try:
                tag = '//div[@id="_container_recruit"]//a[@onclick="companyPageChange(%s,this)"]' % page
                page_ele = self.driver.find_element_by_xpath(tag)
                page_ele.location_once_scrolled_into_view
                self.driver.find_element_by_xpath("//body").send_keys(Keys.DOWN) 
                self.driver.find_element_by_xpath("//body").send_keys(Keys.DOWN) 
                self.driver.find_element_by_xpath("//body").send_keys(Keys.DOWN) 
                time.sleep(0.1)
                page_ele.click()
                locator = (By.XPATH, '//*[@class="pagination-page  active "]/a[text()="%s"]' % page)
                WebDriverWait(self.driver, 5, 0.5).until(EC.presence_of_element_located(locator))
                self.parse_first()
                print('parse %s at page %s' % (self.keyword, page))
            except BaseException as e:
                print('down')
            finally:
                return 1
        else:
            return 0

    def get_nextall(self):
        self.parse_company()
        response_x = Selector(text = self.driver.page_source)
        total_page = int(response_x.xpath('//div[@id="_container_recruit"]//div[@class="total"]/text()[string(.)>0]').extract_first('0'))
        self.driver.implicitly_wait(30)
        if total_page > 1:
            while self.get_next(total_page):
                pass
        self.switch_Home()

    def close(self):
        self.conn.close()
        self.cursor.close()

def run():
    obj = Spider()
    while obj.get():
        if not obj.com_in():
            continue 
        else:
            obj.parse_first()
            obj.get_nextall()
    obj.close()

if __name__ == '__main__':
    run()
