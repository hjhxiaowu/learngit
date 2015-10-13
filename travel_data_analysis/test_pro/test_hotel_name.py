# -*-coding:UTF-8 -*-

__author__ = 'junho'

"""
########################################################
purpose    : 蚂蜂窝酒店数据爬虫项目——酒店名称测试
date       : 2015/09/26
author     : junho
--------------------------------------------------------
2015/10/12 : 添加pandas
2015/10/13 : 添加爬取评分、满意条数字段
########################################################
"""

from multiprocessing import Pool
from lxml import etree
import requests
import time
import random
import pandas as pd

# 酒店类
class Hotel():
    def __init__(self, name, comments, travelNotes, area, priceInfo, score):
        self.name = name
        self.comments = comments
        self.travelNotes = travelNotes
        self.area = area
        self.priceInfo = priceInfo
        self.score = score

    def printHotel(self):
        print u'酒店名称：%s' % self.name
        print u'评论条数：%s' % self.comments
        print u'游记提及条数：%s' % self.travelNotes
        print u'位于区域：%s' % self.area
        print u'最低价格：%s元' % self.priceInfo
        print u'评分：%s' % self.score

    def hotelInfo(self):
        li = []
        li.append(self.name)
        li.append(self.comments)
        li.append(self.travelNotes)
        li.append(self.area)
        li.append(self.priceInfo)
        li.append(self.score)
        return li

# -------------------------解析方法-------------------------- #
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
    for each in content_field:
        prices = each.xpath('a/em[@class="p"]/span[1]/text()')
        for index,item in enumerate(prices):
            prices[index] = int(item)
        priceInfos.append(min(prices))
    return priceInfos

# 2015/10/13 : 添加爬取评分、满意条数字段
def getScores(page):
    scores = []
    homeUrl = 'http://www.mafengwo.cn'
    hrefs = page.xpath('//div[@class="hotel-list"]/div[@class="hotel-item clearfix h-item"]/div[@class="hotel-title"]/div[@class="title"]/h3/a/@href')
    for href in hrefs:
        url = homeUrl + href
        print url
        scorePage = getPage(url)
        # //div[@class="wrapper-bg"]/div/div[@class="m-box m-intro clearfix"]/dl/dd/div[@class="btn_booking"]/span/em/text()
        score = scorePage.xpath('//div[@class="btn_booking"]/span/em/text()')
        scores.append(score)
        # 防反爬虫（反爬虫机制：并发）
        time.sleep(2)
    return scores

def getHotels(url):
    hotels = []
    page = getPage(url)
    names = getNames(page)
    comments = getComments(page)
    travelNotes = getTravelNotes(page)
    priceInfos = getPriceInfos(page)
    areas = getAreas(page)
    scores = getScores(page)
    for i in range(20):
        hotel = Hotel(names[i], comments[i], travelNotes[i], areas[i], priceInfos[i], scores[i])
        hotels.append(hotel)
    return hotels

# -------------------------主函数------------------------- #
if __name__ == '__main__':
    start2 = time.time()
    # indate = raw_input(u'请输入入住时间（如：2015-11-22）：')
    # outdate = raw_input(u'请输入退房时间（如：2015-11-23）：')
    indate = '2015-11-22'
    outdate = '2015-11-23'
    # ------------END------------ #
    pool = Pool(4)
    urllist = []
    for i in range(1, 3):
        print i
        url = 'http://www.mafengwo.cn/hotel/11053/?sFrom=mdd#indate=%s&outdate=%s&q=&p=%s&scope=city%%2C0%%2C&sort=comment_desc&sales=0&price=0%%2C' % (indate, outdate, i)
        urllist.append(url)
    # 多进程测试
    hotels = []
    results = pool.map(getHotels, urllist)
    pool.close()
    pool.join()
    for li in results:
        hotels.extend(li)
    # 2015/10/12 : 增加pandas
    # tips : 用二维list数组读取数据，然后一次性放入DataFrame中会快很多
    hotelList = []
    for h in hotels:
        hotelList.append(h.hotelInfo())
    df = pd.DataFrame(hotelList, columns=['酒店名称', '评论数', '游记提及条数', '位于区域', '酒店最低价格', '评分'])
    print df
    print len(hotels)
    end2 = time.time()
    print u'多进程执行时间：%s' % (end2 - start2)

