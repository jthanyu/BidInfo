# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class BidInfoItem(scrapy.Item):
    title = Field()  # 标题
    area = Field()  # 区域
    type = Field()  # 招标分类
    end_date = Field()  # 截止时间
    # content = Field()   #招标内容
    contact = Field()  # 联系人
    tel = Field()  # 联系信息
    url = Field()  # 详情页
    publish_date = Field()  # 发布日期
    attachment_url = Field()  # 附件地址
    attachment_content = Field()  # 附件内容
