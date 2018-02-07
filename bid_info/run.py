# _*_ coding:utf-8 _*_

# 启动程序
import time
import os

def run():
    cmd_ep = 'scrapy crawl ep -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_ep)
    cmd_cg = 'scrapy crawl cg -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_cg)
    cmd_bp = 'scrapy crawl bp -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_bp)
    cmd_pr = 'scrapy crawl pr -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_pr)
    cmd_supplier = 'scrapy crawl supplier -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_supplier)
    cmd_dzzb = 'scrapy crawl dzzb -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_dzzb)
    cmd_chiwayland = 'scrapy crawl chiwayland -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_chiwayland)
    cmd_cz = 'scrapy crawl cz -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_cz)
    cmd_zc = 'scrapy crawl zc -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_zc)
    cmd_winwin = 'scrapy crawl winwin -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_winwin)
    cmd_tms = 'scrapy crawl tms -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_tms)
    cmd_crc = 'scrapy crawl crc -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_crc)
    cmd_zhaocai = 'scrapy crawl zhaocai -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd_zhaocai)


if __name__ == '__main__':
    run()

