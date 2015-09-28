# -*-coding:UTF-8 -*-

__author__ = 'junho'

"""
蚂蜂窝酒店数据爬虫项目——酒店名称测试
2015/09/26
"""

from multiprocessing import Pool
from lxml import etree
import requests
import time

# 酒店类
class Hotel():
    def __init__(self, name, comments, travelNotes, area, priceInfo):
        self.name = name
        self.comments = comments
        self.travelNotes = travelNotes
        self.area = area
        self.priceInfo = priceInfo

    def printHotel(self):
        print u'酒店名称：' + self.name
        print u'评论条数：' + str(self.comments) + u'条'
        print u'游记提及条数：' + str(self.travelNotes) + u'条'
        print u'位于区域：' + self.area
        print u'最低价格：' + str(self.priceInfo) + u'元'

# -------------------------解析方法-------------------------- #
# 获取page
def getPage(url):
    html = requests.get(url)
    return etree.HTML(html.text)

# 爬取酒店名称
def getNames(page):
    names = page.xpath('//div[@class="hotel-list"]/div[@class="hotel-item clearfix h-item"]/@data-name')
    return names

# 爬取评论条数
def getComments(page):
    comments = page.xpath('//*[@id="hotel_list"]/div[@class="hotel-item clearfix h-item"]/div[3]/ul/li[1]/a/em/text()')
    for index,item in enumerate(comments):
        tmp = item.replace('条', '')
        print tmp
        comments[index] = int(tmp)
    return comments

# 爬取游记提及条数
def getTravelNotes(page):
    travelNotes = page.xpath('//*[@id="hotel_list"]/div[@class="hotel-item clearfix h-item"]/div[3]/ul/li[3]/a/em/text()')
    for index,item in enumerate(travelNotes):
        travelNotes[index] = int(item.replace('条', ''))
    return travelNotes

# 爬取酒店位于区域
def getAreas(page):
    areas = page.xpath('//*[@id="hotel_list"]/div[@class="hotel-item clearfix h-item"]/div[3]/div/span/a/text()')
    return areas

# 爬取最低价格信息
def getPriceInfos(page):
    content_field = page.xpath('//*[@id="hotel_list"]/div[@class="hotel-item clearfix h-item"]/div[5]')
    priceInfos = []
    for each in content_field:
        prices = each.xpath('a/em[@class="p"]/span[1]/text()')
        for index,item in enumerate(prices):
            prices[index] = int(item)
        priceInfos.append(min(prices))
    return priceInfos

def getHotels(url):
    hotels = []
    page = getPage(url)
    names = getNames(page)
    comments = getComments(page)
    travelNotes = getTravelNotes(page)
    priceInfos = getPriceInfos(page)
    areas = getAreas(page)
    for i in range(20):
        hotel = Hotel(names[i], comments[i], travelNotes[i], areas[i], priceInfos[i])
        hotels.append(hotel)
    return hotels

# -------------------------主函数------------------------- #
if __name__ == '__main__':
    start2 = time.time()
    pool = Pool(4)
    urllist = []
    for i in range(7):
        url = 'http://www.mafengwo.cn/hotel/11053/?sFrom=mdd#indate=2015-09-28&outdate=2015-09-29&q=&p=%s&scope=city%%2C0%%2C&sort=comment_desc&sales=0&price=0%%2C' % i
        urllist.append(url)
    # 多进程测试
    hotels = []
    results = pool.map(getHotels, urllist)
    pool.close()
    pool.join()
    for li in results:
        hotels.extend(li)
    hotels[0].printHotel()
    hotels[1].printHotel()
    print len(hotels)
    end2 = time.time()
    print u'多进程执行时间：%s' % (end2 - start2)

