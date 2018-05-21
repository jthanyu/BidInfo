# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from logging import log

import pymysql

from .settings import *


class BidInfoPipeline(object):
    def process_item(self, item, spider):
        # 给type加引号用的
        if item['type'] != None:
            item['type'] = '["' + item['type'] + '"]'
        return item


class BidInfoDefaultPipeline():
    '''
    为Field设置默认值
    '''

    def process_item(self, item, spider):
        item.setdefault('title', None)
        item.setdefault('area', None)
        item.setdefault('type', None)
        item.setdefault('end_date', None)
        item.setdefault('contact', None)
        item.setdefault('tel', None)
        item.setdefault('url', None)
        item.setdefault('publish_date', None)
        item.setdefault('attachment_url', None)
        item.setdefault('attachment_content', None)
        return item


class DBPipeline():
    def __init__(self):
        # 连接数据库
        self.connect = pymysql.connect(
            host=MYSQL_HOST,
            db=MYSQL_DBNAME,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True
        )
        # 通过cursor执行增量查改
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        try:
            # 插入数据
            self.cursor.execute(
                """insert into bidinfo_bid(title, area, bidtype, end_date ,content,tel,detail_url,publish_date,attachment_url,attachment_content)
                                value (%s, %s, %s, %s, %s, %s,%s, %s,%s,%s)""",
                (item['title'],
                 item['area'],
                 item['type'],
                 item['end_date'],
                 item['contact'],
                 item['tel'],
                 item['url'],
                 item['publish_date'],
                 item['attachment_url'],
                 item['attachment_content']))
            # 提交sql语句
            self.connect.commit()
        except Exception as error:
            log(error)
        return item
