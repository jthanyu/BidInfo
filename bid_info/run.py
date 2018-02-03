# _*_ coding:utf-8 _*_

# 启动程序
import time
import os

def run():
    cmd = 'scrapy crawl ep -o %s.csv' % time.strftime("%Y-%m-%d")
    os.system(cmd)

if __name__ == '__main__':
    run()

