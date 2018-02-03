# _*_ coding:utf-8 _*_
import scrapy
from scrapy.linkextractors import LinkExtractor
import time
import json

from scrapy_splash import SplashRequest
import re
from ..items import BidInfoItem


class EpSpider(scrapy.Spider):
    name = 'ep'
    start_urls = ['http://ep.fosunproperty.com:8888/index/group_zblist.aspx', ]

    def __init__(self):
        self.current_date = time.strftime("%Y-%m-%d")

    def parse(self, response):
        le = LinkExtractor(restrict_xpaths='//tr/td/nobr[@class="grid-title"]')
        links = le.extract_links(response)
        if links:
            for link in links:
                yield scrapy.Request(link.url, callback=self.parse_detail, meta={'url': link.url})

    def parse_detail(self, response):
        info = BidInfoItem()
        publish_date = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblPublishTime"]/text()').extract_first()
        if self.current_date == publish_date:
            info['title'] = response.xpath(
                '//*[@id="ctl00_ContentPlaceHolder1_lblForenoticeTitle"]/text()').extract_first()
            info['area'] = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblPrjPos"]/text()').extract_first()
            info['type'] = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblService"]/text()').extract_first()
            info['end_date'] = \
                response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblBmEndDate"]/text()').extract_first().split(' ')[0]
            info['content'] = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblProduct"]').extract_first().split(
                '<span id="ctl00_ContentPlaceHolder1_lblProduct">')[1]
            info['contact'] = response.xpath(
                '//*[@id="ctl00_ContentPlaceHolder1_lblContactMan"]/text()').extract_first()
            info['tel'] = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblMobilePhone"]/text()').extract_first()
            info['url'] = response.meta['url']
            yield info


class CgSpider(scrapy.Spider):
    '''
    这个比较简单,找到了他的json数据,全都有啊,不过这个的内容是在附件里面的,这个要怎么做的???
    附件地址没有在json里面,这个要怎么搞呢?
    '''
    name = 'cg'
    start_urls = [
        'http://cg.xincheng.com/private-rest/rest/forenotice/getForenotices?publishStartTime=2018-02-02&pageNum=1&pageSize=100']

    BASE_URL = 'http://cg.xincheng.com/bid-detail.html?id='

    def parse(self, response):
        infos = json.loads(response.body.decode('utf-8'))
        # 提取链接
        for info in infos['returnValue']['recordList']:
            # id_detail = info['invitebidforenoticeguid']
            bid_info = BidInfoItem()
            bid_info['title'] = info['forenoticetitle']
            bid_info['area'] = info['province'] + "-" + info['city']
            bid_info['type'] = info['producttypename']
            bid_info['end_date'] = info['jhinvitebidtime']
            bid_info['content'] = '获取不到下载URL'
            bid_info['contact'] = info['contactman']
            bid_info['tel'] = info['contactphone']
            bid_info['url'] = self.BASE_URL + info['invitebidforenoticeguid']
            yield bid_info


class BpSpider(scrapy.Spider):
    name = 'bp'
    # start_urls = ['http://bp.cfldcn.com/article!list.do?categoryCode=zbgg']

    def __init__(self):
        self.current_date = time.strftime("%Y-%m-%d")

    def start_requests(self):
        yield scrapy.FormRequest(url='http://bp.cfldcn.com/article!list.do?categoryCode=zbgg',
                                 formdata={'limit': '50'}, callback=self.parse)

    def parse(self, response):
        rows = response.xpath('//tr')
        for row in rows:
            title = row.xpath('./td/@title').extract_first()
            end_date = str(row.xpath('./td[3]/text()').extract_first()).strip()
            url = row.xpath('./td/a/@onclick').extract_first()
            url_parse = re.search('details.do\?id=\d+&categoryCode=zbgg', str(url))
            # 如果发布时间是当前日期,则解析详情
            publish_date = str(row.xpath('./td[5]/text()').extract_first()).strip()
            if publish_date == self.current_date:
                if url_parse is not None:
                    # 真实的详情页地址
                    url_parsed = url_parse.group(0)
                    # 详情页又嵌套了一个页面,这个页面中只有内容
                    url_content = url_parsed.replace('details','content')
                    print("我需要的地址-------------------------->"+url_content)
                    yield scrapy.Request("http://bp.cfldcn.com/article!"+url_content,callback=self.parse_detail,meta={'title':title,'end_date':end_date,'url':"http://bp.cfldcn.com/article!"+url_content})

    def parse_detail(self,response):
        bid_info = BidInfoItem()
        # title = response.xpath('/html/body/div/div[2]/div[1]')
        bid_info['title'] = response.meta['title']
        bid_info['end_date'] = response.meta['end_date']
        bid_info['url'] = response.meta['url']
        # 这个网页中没有招标区域的概念,这里选择了招标联系人的联系地址,截取其城市
        bid_info['area'] = response.xpath('/html/body/p[last()-2]/span/span/text()').extract_first()
        bid_info['type'] = response.xpath('/html/body/p[4]/span[1]/text()').extract_first()
        bid_info['content'] = response.xpath('//body').extract_first()
        bid_info['contact'] = response.xpath('/html/body/p[18]/span/text()').extract_first()
        bid_info['tel'] = response.xpath('/html/body/p[19]/span/text()').extract_first()
        yield bid_info



class PrSpider(scrapy.Spider):
    '''
    这个网址是一页返回6条数据,招标信息不多,不想爬后面页面的了
    '''
    name = 'pr'
    start_urls = ['http://pr.landsea.cn:38082/ccenrun-frontm/bidInfo.htm?currentnumber=1']
    allow_domains = ['http://pr.landsea.cn:38082/']
    def parse(self, response):
        infos = response.xpath('//div[@class="bulletin-dv-a"]/ul/li')
        for info in infos:
            url = info.xpath('./a/@href').extract_first()
            publish_date = info.xpath('./a/span/text()').extract_first()
            yield scrapy.Request(response.urljoin(url),self.parse_detail)

    def parse_detail(self,response):
        bid_info = BidInfoItem()
        bid_info['url'] = response.url
