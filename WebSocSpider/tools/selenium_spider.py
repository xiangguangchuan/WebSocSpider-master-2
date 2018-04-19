import scrapy
from selenium import webdriver
import time

start_url = "http://demo.websoc.knownsec.com:9121/login/"

def get_page_source(self, response):
    browser = webdriver.Chrome(executable_path="D:\\python\\tools\\chromedriver_win32\\chromedriver.exe")#Chromedriver的path路径
    browser.get(start_url)

    #用户名和密码的提交
    browser.find_element_by_css_selector("input[name='username']").send_keys("liuxs")
    browser.find_element_by_css_selector("input[name='password']").send_keys("Liuxs@123")

    time.sleep(2) #睡一会儿，目的防止数据还没有提交，就进行了登录操作，导致登录失败

    browser.find_element_by_css_selector("#submit-button").click()
    return browser.page_source
    browser.quit()