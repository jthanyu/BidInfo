# _*_ coding:utf-8 _*_
import scrapy
from scrapy.linkextractors import LinkExtractor
import time
import json

from scrapy_splash import SplashRequest
import re
from ..items import BidInfoItem


class BaseSpider(scrapy.Spider):
    def __init__(self):
        self.current_date = time.strftime("%Y-%m-%d")

class EpSpider(BaseSpider):
    name = 'ep'
    start_urls = ['http://ep.fosunproperty.com:8888/index/group_zblist.aspx', ]

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
            info['end_date'] = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblBmEndDate"]/text()').extract_first().split(' ')[0]
            info['content'] = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblProduct"]').extract_first().split(
                '<span id="ctl00_ContentPlaceHolder1_lblProduct">')[1]
            info['contact'] = response.xpath(
                '//*[@id="ctl00_ContentPlaceHolder1_lblContactMan"]/text()').extract_first()
            info['tel'] = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblMobilePhone"]/text()').extract_first()
            info['url'] = response.meta['url']
            yield info


class CgSpider(BaseSpider):
    '''
    这个比较简单,找到了他的json数据,全都有啊,不过这个的内容是在附件里面的,这个要怎么做的???
    附件地址没有在json里面,这个要怎么搞呢?
    '''
    name = 'cg'
    start_urls = [
        'http://cg.xincheng.com/private-rest/rest/forenotice/getForenotices?pageNum=1&pageSize=100&publishStartTime={date}'.format(date=time.strftime("%Y-%m-%d"))]

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
            bid_info['end_date'] = info['jhinvitebidtime'].split()[0]
            bid_info['content'] = '获取不到下载URL'
            bid_info['contact'] = info['contactman']
            bid_info['tel'] = info['contactphone']
            bid_info['url'] = self.BASE_URL + info['invitebidforenoticeguid']
            yield bid_info


class BpSpider(BaseSpider):
    name = 'bp'
    # start_urls = ['http://bp.cfldcn.com/article!list.do?categoryCode=zbgg']

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



class PrSpider(BaseSpider):
    '''
    这个网址是一页返回6条数据,是按照发布时间排序的，招标信息不多,不想爬后面页面的了
    '''
    name = 'pr'
    start_urls = ['http://pr.landsea.cn:38082/ccenrun-frontm/bidInfo.htm?currentnumber=1']
    allow_domains = ['http://pr.landsea.cn:38082/']


    def parse(self, response):
        infos = response.xpath('//div[@class="bulletin-dv-a"]/ul/li')
        for info in infos:
            url = info.xpath('./a/@href').extract_first()
            # 这里记得筛选时间
            publish_date = info.xpath('./a/span/text()').extract_first()
            if publish_date == self.current_date:
                yield scrapy.Request(response.urljoin(url),self.parse_detail)

    def parse_detail(self,response):
        bid_info = BidInfoItem()
        bid_info['url'] = response.url
        bid_info['title'] = response.xpath('//h3/text()').extract_first().strip()
        bid_info['end_date'] = response.xpath('//table//tr[17]/td/text()').extract_first().strip().split('：')[-1].split()[0]
        # 这个招标地址有的有问题，因为他没有地址这个字段，略显尴尬
        bid_info['area'] = response.xpath('//table//tr[5]/td/text()').extract_first().strip().split("；")[0].split("：")[-1]
        bid_info['type'] = response.xpath('//table//tr[3]/td/text()').extract_first().strip().split("：")[-1]
        bid_info['content'] = response.xpath('//table').extract_first()
        bid_info['contact'] = response.xpath('//table//tr[18]/td/text()').extract_first().strip().split('：')[-1]
        bid_info['tel'] = response.xpath('//table//tr[19]/td/text()').extract_first().strip().split('：')[-1]
        yield bid_info
        

class SupplierSpider(BaseSpider):
    '''
    这个抓取的电话和联系人有问题，需要改进，
    目前没找到合适的方法抓取
    '''
    name = 'supplier'
    start_urls = ['http://supplier.zhonghongholdings.com/index!zhaoBiaoList.do?type=1']
    allow_domains = ['http://supplier.zhonghongholdings.com/']

    def parse(self,response):
        rows = response.xpath('//tr[@class="zblist_over"]')
        for row in rows:
            title = row.xpath('./td/@title').extract_first()
            publish_date = row.xpath('./td[2]/text()').extract_first().split()[0]
            url = row.xpath('./td[1]/a/@onclick').extract_first().split("href='")[-1].split("'")[0]
            print('url--------------------------------------------------->'+response.urljoin(url))
            yield scrapy.Request(response.urljoin(url),callback=self.parse_detail,meta={'title':title})

    def parse_detail(self,response):
        bid_info = BidInfoItem()
        # bid_info['title'] = response.xpath('//div[@class="newstitle"]/text()').extract_first()
        bid_info['title'] = meta['title']
        bid_info['url'] = response.url
        bid_info['end_date'] = response.xpath('//table//tr[2]/td/span/text()').extract_first().split('报名截止日期：')[-1].split()[0]
        
        # q:没有分类
        bid_info['type'] = '木有分类'
        bid_info['content'] = response.xpath('//div[@class="detail_c"]').extract_first()
        content = response.xpath('//div[@class="detail_c"]').extract_first()
        bid_info['area'] = content.split('项目地点：【')[-1].split('】')[0]
        bid_info['contact'] = content.split('供方专员：')[-1].split('<br>')[0]
        bid_info['tel'] = content.split('供方服务热线：')[-1].split('<br>')[0]
        return bid_info

class DzzbSpider(BaseSpider):
    '''
    这个没有区域
    '''
    name = 'dzzb'
    start_urls = ['https://dzzb.ciesco.com.cn/gg/zgysList']
    allow_domains = ['https://dzzb.ciesco.com.cn']

    def parse(self,response):
        rows = response.xpath('//table//tr')
        for row in rows:
            publish_date = row.xpath('./td[5]').extract_first()
            if publish_date == self.current_date:
                url = row.xpath('./td[3]/a/@href').extract_first()
                yield scrapy.Request(response.urljoin(url),callback=self.parse_detail)

    def parse_detail(self,response):
        bid_info = BidInfoItem()
        bid_info['url'] = response.url
        bid_info['title'] = response.xpath('//span[@class="title"]/text()').extract_first()
        bid_info['end_date'] = response.xpath('//tr[@class="sqWJDiJiaoEndTime ZhiJieQueDingZBR"]/td/text()').extract_first().strip().split()[0]
        bid_info['type'] = response.xpath('//div[@class="template"]/div[1]/table//tr[3]/td/text()').extract_first().strip()
        bid_info['content'] = response.xpath('//div[@class="template"]').extract_first()
        # 木有区域
        bid_info['contact'] = response.xpath('//div[@class="template"]/div[2]/table//tr[2]/td[1]/text()').extract_first()
        bid_info['tel'] = response.xpath('//div[@class="template"]/div[2]/table//tr[2]/td[2]/text()').extract_first()
        yield bid_info


class ChiwaylandSpider(BaseSpider):
    '''
    这个没有分类
    '''
    name = 'chiwayland'
    start_urls = ['http://www.chiwayland.com/BidNews/BidPlan.htm']
    allow_domains = ['http://www.chiwayland.com']

    def parse(self,response):
        rows = response.xpath('//ul[@class="ucanNewsUl ms_BidPlan"]/li[position()>1]')
        for row in rows:
            publish_date = row.xpath('./span[@class="addtime"]/text()').extract_first()
            url = row.xpath('./a/@href').extract_first()
            if publish_date == self.current_date:
                yield scrapy.Request(response.urljoin(url),callback=self.parse_detail)

    def parse_detail(self,response):
        bid_info = BidInfoItem()
        bid_info['url'] = response.url
        bid_info['title'] = response.xpath('//h1/span[@id="txtTitle"]/text()').extract_first()
        bid_info['end_date'] = response.xpath('//*[@id="txt_EndTime"]/text()').extract_first()
        bid_info['content'] = response.xpath('//table').extract_first()
        bid_info['contact'] = response.xpath('//table//tr[25]/td[2]/p/text()').extract_first().split('：')[-1]
        bid_info['tel'] = response.xpath('//table//tr[26]/td[2]/p/text()').extract_first().split('：')[-1]
        bid_info['area'] = response.xpath('//table//tr[6]/td[2]/p/text()').extract_first().strip('：').split('：')[-1]
        yield bid_info

class CzSpider(BaseSpider):
    '''
    为什么网站会有不同的布局啊啊啊啊啊
    恶心死了，这个还是有点点问题的
    列表有15条数据，但是我这里只能抓取8条....
    '''
    name = 'cz'
    start_urls = ['http://cz.newhope.cn/index.php?m=default.bidding']
    allow_domains = ['http://cz.newhope.cn']

    def parse(self,response):
        urls = response.xpath('//div[@class="f_wzbox"]/a/@href').extract()
        for url in urls:
            yield scrapy.Request(response.urljoin(url),callback = self.parse_detail)

    def parse_detail(self,response):
        publish_date = response.xpath('//div[@class="cc_bg"]/p[4]/text()').extract_first()
        if publish_date is not None:
            publish_date = publish_date.split('发布时间：')[-1].split(" ")[0]
            if publish_date == self.current_date:
                bid_info = BidInfoItem()
                bid_info['url'] = response.url
                bid_info['title'] = response.xpath('//div[@class="con_con"]/h1/text()').extract_first()
                bid_info['end_date'] = response.xpath('//div[@class="cc_bg"]/p[1]/span/text()').extract_first().split()[0]
                bid_info['content'] = response.xpath('//div[@class="con_con"]/p[1]').extract_first()
                bid_info['area'] = response.xpath('//div[@class="cc_bg"]/p[6]/text()').extract_first().split('：')[-1]
                bid_info['contact'] = response.xpath('//div[@class="cc_bg"]/p[2]/text()').extract_first().split('：')[-1]
                # bid_info['tel'] = response.xpath('//div[@class="con_con"]/p[1]/span[4]/span/text()').extract_first().split('联系电话：')[-1].split('；')[0]
                bid_info['type'] = response.xpath('//div[@class="cc_bg"]/p[3]/text()').extract_first()
                yield bid_info

class ZcSpider(BaseSpider):
    '''
    1.不是按照发布时间排序，所以担心会不会最近的日期会在后边 的页面里，因为我这里为了快速，只抓第一页
    2.详情是在文件里面
    '''
    name = 'zc'
    start_urls = ['http://zc.gtcloud.cn/HomePage/TenderNotice.aspx']
    allow_domains = ['http://zc.gtcloud.cn/HomePage/']
    
    def parse(self,response):
        titles = response.xpath('//nobr/a/text()').extract()
        
        rows = response.xpath('//div[@class="f-gridpanel"]//table//tr[position()>2]')
        for row in rows:
            publish_date = row.xpath('./td[4]/text()').extract_first()
            if publish_date == self.current_date:
                url = row.xpath('.//nobr/a/@href').extract_first()
                yield scrapy.Request(response.urljoin(url),callback = self.parse_detail)

    def parse_detail(self,response):
        bid_info = BidInfoItem()
        bid_info['url'] = response.url
        bid_info['title'] = response.xpath('//span[@id="ctl00_ContentPlaceHolder1_lblForenoticeTitle"]/text()').extract_first()
        bid_info['end_date'] = response.xpath('//span[@id="ctl00_ContentPlaceHolder1_lblBmEndDate"]/text()').extract_first().split()[0]
        bid_info['content'] = '内容在附件里，没抓取'
        # 没有area
        bid_info['type'] = response.xpath('//span[@id="ctl00_ContentPlaceHolder1_lblProductTypeName"]/text()').extract_first()
        bid_info['contact'] = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblContactMan"]/text()').extract_first()
        bid_info['tel'] = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblMobilePhone"]/text()').extract_first()
        yield bid_info

class WinwinSpider(BaseSpider):
    '''
    这个木有分类
    '''
    name = 'win'
    start_urls = ['http://winwin.yango.com.cn/HomePage/TenderNotice.aspx']
    allow_domains = ['http://winwin.yango.com.cn/HomePage']

    def parse(self,response):
        rows = response.xpath('//*[@id="ctl00_ContentPlaceHolder1__AppGrid_DXMainTable"]//tr[position()>2]')
        for row in rows:
            publish_date = row.xpath('./td[4]/text()').extract_first()
            if publish_date == self.current_date:
                url = row.xpath('td/nobr/a/@href').extract_first()
                yield scrapy.Request(response.urljoin(url),callback=self.parse_detail)

    def parse_detail(self,response):
        bid_info = BidInfoItem()
        bid_info['url'] = response.url
        bid_info['title'] = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblForenoticeTitle"]/text()').extract_first()
        bid_info['end_date'] = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblBmEndDate"]/text()').extract_first().split()[0]
        bid_info['content'] = response.xpath('//table//tr[1]/td').extract_first()
        bid_info['area'] = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblRegion"]/text()').extract_first()
        bid_info['type'] = '没有分类'
        bid_info['contact'] = response.xpath('//table//tr[1]/td').extract_first().split('联系人：')[-1].split('<br>')[0]
        bid_info['tel'] = response.xpath('//table//tr[1]/td').extract_first().split('联系方式：')[-1].split('<br>')[0]
        yield bid_info

class TmsSpider(BaseSpider):
    '''
    这个 area ,type,contact,tel 全都是在正文里面，一定规律都没有，先不写了
    '''
    name = 'tms'
    start_urls = ['http://tms.zldcgroup.cn/TMX/TMX/TMXMain.aspx']

    def parse(self,response):
        rows = response.xpath('//div[@class="index_list"]/ul')
        for row in rows:
            publish_date = row.xpath('li[3]/text()').extract_first()
            if publish_date == self.current_date:
                url = row.xpath('./li/a/@href').extract_first().split(",'")[-1].split("')")[0]
                yield scrapy.Request("http://tms.zldcgroup.cn/TMX/TMX/TMXNoticeView.aspx?keyid="+url,callback=self.parse_detail,meta={'url':"http://tms.zldcgroup.cn/TMX/TMX/TMXNoticeView.aspx?keyid="+url})

    def parse_detail(self,response):
        bid_info = BidInfoItem()
        bid_info['url'] = response.meta['url']
        bid_info['title'] = response.xpath('//div[@class="read"]/h2/text()').extract_first().strip()
        bid_info['content'] = response.xpath('//div[@id="details"]').extract_first()
        
        yield bid_info

class CrcSpider(BaseSpider):
    '''
    没有区域，也没有类型
    截止日期不好获取

    '''
    name = 'crc'
    start_urls = ['http://crc.cifi.com.cn/fdc/invite/splweb/inviteProjectListWebPage.do?method=initalize&conversationid=1517902669386']
    allow_domains = ['crc.cifi.com.cn']

    def parse(self,response):
        rows = response.xpath('//table//tr')
        for row in rows:
            publish_date = row.xpath('./td[4]/text()').extract_first()
            url = row.xpath('./td[2]/@onclick').extract_first().split('("')[-1].split('")')[0]
            print('----------------------------->'+response.urljoin(url))
            yield scrapy.Request(response.urljoin(url),callback=self.parse_detail)

    def parse_detail(self,response):
        bid_info = BidInfoItem()
        bid_info['url'] = bid_info.url
        bid_info['title'] = response.xpath('//div[@class="title"]/text()').extract_first().strip()
        bid_info['content'] = response.xpath('//div[@class="content"]').extract_first()
        bid_info['tel'] = response.xpath('//div[@class="inp_2"]').extract_first()
        bid_info['end_date'] = response.xpath('//div[@class="content"]/div[last()-1]/div[2]/text()').extract_first()
        bid_info['contact'] = response.xpath('//div[@class="content"]/div[last()-1]/div[3]/div[2]/text()').extract_first()
        yield bid_info
