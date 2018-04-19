# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from WebSocSpider.settings import   SQL_DATE_FORMAT
class WebsocspiderItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()

class WebsocspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
class WebsocImageItem(scrapy.Item):
    num = scrapy.Field()
    parent_tag = scrapy.Field()
    name = scrapy.Field()
    grade = scrapy.Field()
    tag = scrapy.Field()
    influnce = scrapy.Field()
    description = scrapy.Field()
    CVE_ID = scrapy.Field()
    CNNVD_ID = scrapy.Field()
    CNVD_ID = scrapy.Field()
    update_time = scrapy.Field()

    def get_insert_sql(self): #SQL插入语句
        insert_sql = """
               insert into websoc_spider(num, parent_tag, name, grade, tag, influnce, description, CVE_ID,
               CNNVD_ID, CNVD_ID, update_time) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           """
        # ON DUPLICATE KEY UPDATE name=VALUES(name), grade=VALUES(grade)
        params = (
            self["num"], self["parent_tag"], self["name"], self["grade"], self["tag"], self["influnce"],
            self["description"], self["CVE_ID"], self["CNNVD_ID"],
            self["CNVD_ID"], self["update_time"]
        )

        return insert_sql, params

