# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request, FormRequest
import json
from urllib import parse
from WebSocSpider.items import WebsocspiderItemLoader,WebsocImageItem

class WebsocSpider(scrapy.Spider):
    name = 'websoc'
    allowed_domains = ['demo.websoc.knownsec.com']
    start_urls = ['http://demo.websoc.knownsec.com:9121/help/vul/'] #爬虫爬取的起始URL

    login_url = "http://demo.websoc.knownsec.com:9121/login/" #登录URL

    headers = { #request请求头
        "User_Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Mobile Safari/537.36",
        "Host": "demo.websoc.knownsec.com:9121",
        "Referer": "http://demo.websoc.knownsec.com:9121/help/vul/?tag_id=1"
    }
    #将数据转换成json格式
    # json_tree = {'messages': [{'parent_tag': '',
    #                      'children': [{'child_tag': '',
    #                                         'detail': {'num': '', 'name': ''
    #                                                     }
    #                                            }]
    #                      }]}

    def parse(self, response):
        tags = response.css("#navigation > li")
        parent_tags = tags.css(".tag_item::text").extract()
        index = 0
        for parent_tag in parent_tags: #先遍历一级父标签
            urls = tags[index].css("a::attr(href)").extract()
            children_tags = tags[index].css("ul a::text").extract()
            index += 1
            # for child_tag in children_tags: #遍历二级标签
            #     self.children_list.append(child_tag)
            for url in urls: #遍历二级标签的URL
                # self.urls.append(url)
                yield Request(url=parse.urljoin(response.url, url),
                              callback=self.parse_detail, meta = {"parent_tag": parent_tag}) #深度遍历每个子标签的URL


    def parse_detail(self, response):
        count_tr = len(response.css(".table-bordered tr").extract()) #统计表格有多少行
        item_loader = WebsocspiderItemLoader(item=WebsocImageItem(), response=response)
        while count_tr > 0:
            item_loader.add_css("num", ".table-bordered tr:nth-child({}) td:nth-child(1)::text".format(count_tr))
            item_loader.add_value("parent_tag", response.meta["parent_tag"])
            item_loader.add_css("name", ".table-bordered tr:nth-child({}) td:nth-child(2) a::text".format(count_tr))
            item_loader.add_css("grade", ".table-bordered tr:nth-child({}) td:nth-child(3)::text".format(count_tr))
            #由于tag, CVE_ID, CNNVD_ID, CNVD_ID可能不存在，要进行判断
            if response.css(".table-bordered tr:nth-child({}) td:nth-child(4) a::attr(href)".format(count_tr)).extract_first(""):
                item_loader.add_css("tag", ".table-bordered tr:nth-child({}) td:nth-child(4) a::text".format(count_tr))
            else:
                item_loader.add_value("tag", " ")

            if response.css(
                    ".table-bordered tr:nth-child({}) td:nth-child(5) a::attr(href)".format(count_tr)).extract_first(
                    ""):
                item_loader.add_css("CVE_ID", ".table-bordered tr:nth-child({}) td:nth-child(5) a::text".format(count_tr))
            else:
                item_loader.add_value("CVE_ID", " ")

            if response.css(
                    ".table-bordered tr:nth-child({}) td:nth-child(6) a::attr(href)".format(count_tr)).extract_first(
                    ""):
                item_loader.add_css("CNNVD_ID", ".table-bordered tr:nth-child({}) td:nth-child(6) a::text".format(count_tr))
            else:
                item_loader.add_value("CNNVD_ID", " ")

            if response.css(
                    ".table-bordered tr:nth-child({}) td:nth-child(7) a::attr(href)".format(count_tr)).extract_first(
                    ""):
                item_loader.add_css("CNVD_ID", ".table-bordered tr:nth-child({}) td:nth-child(7) a::text".format(count_tr))
            else:
                item_loader.add_value("CNVD_ID", " ")

            item_loader.add_css("update_time", ".table-bordered tr:nth-child({}) td:nth-child(8)::text".format(count_tr))
            description_url = response.css(".table-bordered tr:nth-child({}) td:nth-child(2) a::attr(href)".format(count_tr)).extract_first("")

            item = item_loader.load_item()
            count_tr -= 1

            yield Request(url=parse.urljoin(response.url, description_url),
                    callback=self.parse_description, meta={"item": item})

    def parse_description(self,response): #获取漏洞影响及描述信息
        item = response.meta["item"]
        item["influnce"] = response.css("#basc_info ~ div p:nth-child(2)::text").extract_first("")
        item["description"] = response.css("#basc_info ~ div p:nth-child(4)::text").extract_first("")

        yield item

    def start_requests(self): #爬虫的入口
        return [Request(url = self.login_url, headers = self.headers, callback=self.login)]

    def login(self, response): #网站登录
        response_text = response.text #获取登录页面HTML内容
        csrfmiddlewaretoken = response.css("input[name = 'csrfmiddlewaretoken']::attr(value)").extract()[0] #获取csrf_token
        post_data = { #request请求的form_data数据
            "username": "liuxs",
            "password": "Liuxs@123",
            "next": "/site/",
            "csrfmiddlewaretoken": csrfmiddlewaretoken
        }
        return [FormRequest.from_response(response,
                                         dont_filter=True,
                                         url = self.login_url,
                                         formdata=post_data,
                                         headers= self.headers,
                                         callback= self.check_login
                                         )] #通过request请求进行登录

    def check_login(self, response): # 验证服务器的返回数据判断是否成功
        text = response.text
        if 200 == response.status and text: #返回200， 说明登录成功
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)