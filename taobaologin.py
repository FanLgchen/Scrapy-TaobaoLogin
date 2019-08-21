import json
from urllib.parse import quote
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
from pyquery import PyQuery as pq



class Taobao_Spider:

    def __init__(self, username, password):

        """初始化参数"""
        url = 'https://login.taobao.com/member/login.jhtml'
        self.url = url

        keyword = 'IPad'
        self.keyword = keyword

        options = webdriver.ChromeOptions()

        # 不加载图片,加快访问速度
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

        # 设置为开发者模式，避免被识别
        options.add_experimental_option('excludeSwitches',
                                        ['enable-automation'])
        self.browser = webdriver.Chrome(options=options)

        self.wait = WebDriverWait(self.browser, 10)

        # 初始化用户名
        self.username = username

        # 初始化密码
        self.password = password



    def login(self):

        """登陆接口"""

        self.browser.get(self.url)

        try:
            # 这里设置等待：等待输入框
            login_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.qrcode-login > .login-links > .forget-pwd')))
            login_element.click()

            # 打开微博登录
            sina_login = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.weibo-login')))
            sina_login.click()

            # 用户名填写框
            weibo_user = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.username > .W_input')))
            weibo_user.send_keys(self.username)

            # 密码填写框
            sina_password = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.password > .W_input')))
            sina_password.send_keys(self.password)

            # 提交
            submit = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btn_tip > a > span')))
            submit.click()

            # 获取用户名
            taobao_name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.site-nav-bd > ul.site-nav-bd-l > '
                                'li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')))

            # 登陆成功打印提示信息
            print("登陆成功：%s" % taobao_name.text)

        except Exception:

            self.browser.close()

            print("登陆失败")


        #获取cookies
        cookies = self.browser.get_cookies()
        self.browser.close()

        #保存cookies
        jsonCookies = json.dumps(cookies)

        with open('taobaoCookies.json','w') as f :

            f.write(jsonCookies)

        print(cookies)


    def index_page(self,page):


        with open('taobaoCookies.json', 'r', encoding='utf-8') as f:

            listcookies = json.loads(f.read())  # 获取cookies

        # 把获取的cookies处理成dict类型

        for cookie in listcookies:

            self.browser.add_cookie(cookie)


        try:

            url = 'https://s.taobao.com/search?q=' + quote(self.keyword)

            # 发送请求
            self.browser.get(url)

            print('你当前访问的是第%d页' % page)

            if page > 1:
                J_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager div.form > input')))

                J_submit = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager div.form > span.btn.J_Submit')))

                J_input.clear()

                J_input.send_keys(page)

                J_submit.click()

            wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,
                                                         '#mainsrp-pager li.item.active > span'), str(page)))
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-itemlist .items .item')))

            self.get_products()

        except TimeoutException:

            print('try again')

            self.index_page(page)


    """PyQuery解析库解析"""

    def get_products(self):

        html = self.browser.page_source

        doc = pq(html)

        items = doc('#mainsrp-itemlist .items .item').items()

        for item in items:
            product = {}
            product['image'] = item.find('.img').attr('src')
            product['price'] = item.find('.price').text()
            product['payment'] = item.find('.deal-cnt').text()
            product['title'] = item.find('.title').text()
            product['location'] = item.find('.location').text()
            product['shop'] = item.find('.shopname').text()
            product['shop-link'] = item.find('.shopname').attr('href')
            print(product)
            print('完成')



if __name__ == "__main__":

    username = input("请输入你的微博用户名:")

    password = input("请输入密码:")

    spider = Taobao_Spider(username, password)

    spider.login()

    spider.index_page(1)