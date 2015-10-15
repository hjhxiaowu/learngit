# -*-coding:UTF-8 -*-

__author__ = 'junho'

"""
########################################################
purpose    : 蚂蜂窝酒店数据爬虫项目——酒店名称测试
date       : 2015/09/26
author     : junho
--------------------------------------------------------
2015/10/12 : 添加pandas
2015/10/13 : 添加爬取评分字段
2015/10/14 : 添加爬取满意条数字段；导入mysql数据库；增加最低价格提供网站字段
########################################################
"""

from multiprocessing import Pool
from lxml import etree
import requests
import time
import random
import pandas as pd
import MySQLdb
# UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-5: ordinal not in range(128)
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# 酒店类
class Hotel():
    def __init__(self, name, comments, gComments, travelNotes, area, priceInfo, score):
        self.name = name
        self.comments = comments
        self.gComments = gComments
        self.travelNotes = travelNotes
        self.area = area
        self.priceInfo = priceInfo
        self.score = score

    def __init__(self, name, comments, travelNotes, area, priceInfo, priceSite):
        self.name = name
        self.comments = comments
        self.travelNotes = travelNotes
        self.area = area
        self.priceInfo = priceInfo
        self.priceSite = priceSite

    def printHotel(self):
        print u'酒店名称：%s' % self.name
        print u'评论条数：%s' % self.comments
        # print u'满意条数：%s' % self.gComments
        print u'游记提及条数：%s' % self.travelNotes
        print u'位于区域：%s' % self.area
        print u'最低价格：%s元' % self.priceInfo
        print u'来自：%s元' % self.priceSite
        # print u'评分：%s' % self.score

    def getHotel(self):
        li = []
        li.append(self.name)
        li.append(self.comments)
        # li.append(self.gComments)
        li.append(self.travelNotes)
        li.append(self.area)
        li.append(self.priceInfo)
        li.append(self.priceSite)
        # li.append(self.score)
        return li

# -------------------------爬取方法-------------------------- #
# 获取page
def getPage(url):
    html = requests.get(url, timeout=30)
    return etree.HTML(html.text)

# 爬取酒店名称
def getNames(page):
    names = page.xpath('//div[@class="hotel-list"]/div[@class="hotel-item clearfix h-item"]/@data-name')
    return names

# 爬取评论条数
def getComments(page):
    comments = []
    content_field = page.xpath('//div[@class="hotel-list"]/div[@class="hotel-item clearfix h-item"]')
    for each in content_field:
        comment = each.xpath('div[@class="hotel-info"]/ul/li[1]/a/em/text()')
        if comment:
            comments.append(comment[0])
        else:
            comments.append(u'0条')
    return comments

# 爬取游记提及条数
def getTravelNotes(page):
    travelNotes = []
    content_field = page.xpath('//div[@class="hotel-list"]/div[@class="hotel-item clearfix h-item"]')
    for each in content_field:
        travelNote = each.xpath('div[@class="hotel-info"]/ul/li[3]/a/em/text()')
        if travelNote:
            travelNotes.append(travelNote[0])
        else:
            travelNotes.append(u'0篇')
    return travelNotes

# 爬取酒店位于区域
def getAreas(page):
    areas = []
    content_field = page.xpath('//div[@class="hotel-list"]/div[@class="hotel-item clearfix h-item"]/div[3]/div/span')
    for each in content_field:
        area = each.xpath('a/text()')
        if area:
            areas.append(area[0])
        else:
            areas.append(u'无提供信息')
    return areas

# 爬取最低价格信息
def getPriceInfos(page):
    content_field = page.xpath('//*[@id="hotel_list"]/div[@class="hotel-item clearfix h-item"]/div[5]')
    priceInfos = []
    priceSites = []
    for each in content_field:
        prices = each.xpath('a/em[@class="p"]/span[1]/text()')
        sites = each.xpath('a/@data-otaname')
        i = 0
        minPrices = int(prices[0])
        for index, item in enumerate(prices):
            prices[index] = int(item)
            if minPrices >= prices[index]:
                minPrices = prices[index]
                i = index
        priceSites.append(sites[i])
        priceInfos.append(minPrices)
    return priceInfos, priceSites

# 2015/10/13 : 添加爬取评分、满意条数字段
def getInsideInfo(page):
    scores = []
    gComments = []
    hrefs = page.xpath('//div[@class="hotel-list"]/div[@class="hotel-item clearfix h-item"]/div[@class="hotel-title"]/div[@class="title"]/h3/a/@href')
    homeUrl = 'http://www.mafengwo.cn'
    for href in hrefs:
        url = homeUrl + href
        print url
        inpage = getPage(url)
        scores.append(inpage.xpath('//div[@class="btn_booking"]/span/em/text()'))
        gcomm = inpage.xpath('//*[@id="comment_header"]/div/ul/li[3]/a/span/text()')
        gComments.append(gcomm)
        print gcomm
        # 防反爬虫（反爬虫机制：并发）
        time.sleep(random.randint(1, 3))
    return scores, gComments

# 酒店类信息爬取汇总
def getHotels(url):
    hotels = []
    page = getPage(url)
    names = getNames(page)
    comments = getComments(page)
    travelNotes = getTravelNotes(page)
    priceInfos, priceSites = getPriceInfos(page)
    areas = getAreas(page)
    # scores, gComments = getInsideInfo(page)
    for i in range(20):
        # hotel = Hotel(names[i], comments[i], gComments[i], travelNotes[i], areas[i], priceInfos[i], scores[i])
        hotel = Hotel(names[i], comments[i], travelNotes[i], areas[i], priceInfos[i], priceSites[i])
        hotels.append(hotel)
    return hotels

# 测试案例1：多进程
def test1():
    start = time.time()
    indate = '2015-11-22'
    outdate = '2015-11-23'
    urllist, hotels = [], []
    for i in range(1, 2):
        url = 'http://www.mafengwo.cn/hotel/11053/#indate=%s&outdate=%s&q=&p=%s&scope=city%%2C0%%2C&sort=comment_desc&sales=0&price=0%%2C' % (indate, outdate, i)
        print url
        urllist.append(url)
    pool = Pool(4)
    results = pool.map(getHotels, urllist)
    pool.close()
    pool.join()
    for li in results:
        hotels.extend(li)
    end = time.time()
    print u'多进程执行时间：%s' % (end - start)
    return hotels

# 测试案例2：pandas
def test2(hotels):
    # 2015/10/12 : 增加pandas
    # tips : 用二维list数组读取数据，然后一次性放入DataFrame中会快很多
    hotelList = []
    for h in hotels:
        hotelList.append(h.getHotel())
    # df = pd.DataFrame(hotelList, columns=['酒店名称', '评论数', '满意数', '游记提及条数', '位于区域', '酒店最低价格', '评分'])
    df = pd.DataFrame(hotelList, columns=['hotel_name', 'comments', 'travelNotes', 'area', 'priceInfo', 'priceSite'])
    print df

# 测试案例3：直接导入mysql数据库
def test3(hotels):
    try:
        conn = MySQLdb.connect(host="localhost", user="root", passwd="544989", db="test_mysql", charset="utf8")
        cursor = conn.cursor()
        values = []
        for hotel in hotels:
            values.append(hotel.getHotel())
        cursor.executemany('insert into tmp_testPython values(%s, %s, %s, %s, %s, %s)', values)
        cursor.close()
        conn.commit()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

# -------------------------主函数------------------------- #
if __name__ == '__main__':
    hotels = test1()
    test2(hotels)
