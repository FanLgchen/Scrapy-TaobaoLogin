# Scrapy-TaobaoLogin
使用Selenium+pyquery模拟淘宝第三方登录
## demo说明
* 绕过taobao登录验证码，利用新浪微博第三方登录爬取数据
### 准备库
* pip install selenium
* pip install pyquery
* pip install urllib
### ChromeDriver安装
* 下载安装ChromeDriver(对应浏览器版本)
### demo说明
#### 登录：使用Selenium库模拟浏览器请求登录
```python
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
```
#### 获取商品列表数据
```python
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
```
#### pyquery库解析商品列表
```python
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
```
