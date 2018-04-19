# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import codecs
import json
import MySQLdb.cursors
from twisted.enterprise import adbapi

class WebsocspiderPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWithEncodingPipeline(object):
    json_tree = {}
    child = {}
    detail = {}  # 父标签
    children = []  # 子标签
    message = {}
    messages = []  # 子标签URL
    #自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding="utf-8")

    def process_item(self, item, spider):
        self.detail["num"] = item["num"]
        self.detail["name"] = item["name"]
        self.detail["grade"] = item["grade"]
        self.detail["CVE_ID"] = item["CVE_ID"]
        self.detail["CNNVD_ID"] = item["CNNVD_ID"]
        self.detail["CNVD_ID"] = item["CNVD_ID"]
        self.detail["update_time"] = item["update_time"]
        self.detail["influnce"] = item["influnce"]
        self.detail["description"] = item["description"]

        self.child["child_tag"] = item["tag"]
        self.child["detail"] = self.detail
        self.children.append(self.child)

        self.message["parent_tag"] = item["parent_tag"]
        self.message["children"] = self.children
        self.messages.append(self.message)

        self.json_tree["messages"] = self.messages

        lines = json.dumps(self.json_tree, ensure_ascii=False)
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()

class MysqlPipeline(object):
    #采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'root', 'websocspider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def do_insert(self, cursor, item):
        #执行具体的插入
        #根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
        self.conn.commit()
    def process_item(self, item, spider):
        insert_sql, params = item.get_insert_sql()
        self.cursor.execute(insert_sql, params)
        self.conn.commit()


class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider) #处理异常

    def handle_error(self, failure, item, spider):
        #处理异步插入的异常
        print (failure)

    def do_insert(self, cursor, item):
        #执行具体的插入
        #根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)