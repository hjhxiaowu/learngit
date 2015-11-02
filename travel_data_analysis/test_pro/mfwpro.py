# -*-coding:UTF-8 -*-

__author__ = 'junho'

"""
########################################################
purpose    : 蚂蜂窝数据爬虫项目——整合
date       : 2015/10/18
author     : junho
--------------------------------------------------------
########################################################
"""

import re
from multiprocessing import Pool
from lxml import etree
import requests
import time
import MySQLdb
import json
# UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-5: ordinal not in range(128)
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# 城市类
class City:
    def __init__(self, delta=None, country=None, city_name=None, city_id=None, people=None):
        self.delta = delta
        self.country = country
        self.city_name = city_name
        self.city_id = city_id
        self.people = people

    def get_city(self):
        li = []
        li.append(self.delta)
        li.append(self.country)
        li.append(self.city_name)
        li.append(self.city_id)
        li.append(self.people)
        return li


# 酒店类
class Hotel:
    def __init__(self, city_id=None, hotel_name=None, comment_num=None, travel_note_num=None, area=None,
                 min_price=None, min_price_site=None):
        self.city_id = city_id
        self.hotel_name = hotel_name
        self.comment_num = comment_num
        self.travel_note_num = travel_note_num
        self.area = area
        self.min_price = min_price
        self.min_price_site = min_price_site

    def get_hotel(self):
        li = []
        li.append(self.city_id)
        li.append(self.hotel_name)
        li.append(self.comment_num)
        li.append(self.travel_note_num)
        li.append(self.area)
        li.append(self.min_price)
        li.append(self.min_price_site)
        return li


# ----------------------------------爬虫---------------------------------- #
# 获取页面
def get_page(url):
    html = requests.get(url, timeout=30)
    return etree.HTML(html.text)


# 获取国家信息
def get_country_info(page):
    content_field = page.xpath('//div[@class="container"]/div[7]/div/div[1]/div/dl')
    countries = []
    deltas = []
    country_ids = []
    for each in content_field:
        delta = each.xpath('dt/text()')[0]
        tmp_countries = each.xpath('dd/ul/li/a/text()')
        tmp_country_ids = each.xpath('dd/ul/li/a/@href')
        for i in range(len(tmp_countries)):
            countries.append(tmp_countries[i].strip())
            deltas.append(delta)
            country_ids.append(str(tmp_country_ids[i])[-10:-5])
    return deltas, countries, country_ids


# 获取城市信息
def get_city_info(country_ids):
    cities = []
    url = 'http://www.mafengwo.cn/gonglve/sg_ajax.php?sAct=getMapData&iMddid=%s&iType=3&iPage=1' % country_ids
    html = requests.get(url, timeout=30)
    page = html.content.encode('utf-8')
    target = json.loads(page)
    if target['mode'] == 1:
        for i in range(len(target['list'])):
            city = City(city_name=target['list'][i]['name'], city_id=target['list'][i]['id'],
                        people=target['list'][i]['rank'])
            cities.append(city)
    else:
        for i in range(len(target['list'])):
            city = City(city_name=target['list'][i]['name'], city_id=target['list'][i]['id'], people=0)
            cities.append(city)
    return cities


# 获取城市类
def get_cities(url):
    start_in = time.time()
    page = get_page(url)
    cities = []
    tmp_deltas, tmp_countries, tmp_country_ids = get_country_info(page)
    print u'len(tmp_countries):%s' % len(tmp_countries)
    pool = Pool(4)
    results = pool.map(get_city_info, tmp_country_ids)
    pool.close()
    pool.join()
    end_in = time.time()
    print u'城市类信息爬取时间：%s' % (end_in - start_in)
    for i in range(len(results)):
        for j in range(len(results[i])):
            city = City(tmp_deltas[i], tmp_countries[i], results[i][j].city_name, results[i][j].city_id,
                        results[i][j].people)
            cities.append(city)
    print 'len(cities):%s' % len(cities)
    return cities


# 获取酒店信息
def get_hotels(url):
    # print url
    tmp_ints = re.findall('\d+', url)
    city_id = None
    if tmp_ints:
        city_id = tmp_ints[1]
    html = requests.get(url, timeout=30)
    page = html.content.encode('utf-8')
    target = json.loads(page)
    hotels = []
    comments = []
    travel_note_nums = []
    areas = []
    min_prices = []
    min_price_sites = []
    page_xpath = etree.HTML(target['html'])
    # 酒店名称
    hotel_names = page_xpath.xpath('//div[@class="hotel-item clearfix h-item"]/@data-name')
    content_field = page_xpath.xpath('//div[@class="hotel-item clearfix h-item"]')
    for each in content_field:
        # 酒店评论条数
        comment = each.xpath('div[@class="hotel-info"]/ul/li[1]/a/em/text()')
        if comment:
            comments.append(comment[0])
        else:
            comments.append(u'0条')
        # 游记提及条数
        travel_note_num = each.xpath('div[@class="hotel-info"]/ul/li[3]/a/em/text()')
        if travel_note_num:
            travel_note_nums.append(travel_note_num[0])
        else:
            travel_note_nums.append(u'0篇')
        area = each.xpath('div[3]/div/span/a/text()')
        if area:
            areas.append(area[0])
        else:
            areas.append(u'无提供信息')
        # 价格信息
        prices = each.xpath('div[5]/a/em[@class="p"]/span[1]/text()')
        sites = each.xpath('div[5]/a/@data-otaname')
        if prices:
            i = 0
            min_price = int(prices[0])
            for index, item in enumerate(prices):
                prices[index] = int(item)
                if min_price >= prices[index]:
                    min_price = prices[index]
                    i = index
            min_prices.append(min_price)
            min_price_sites.append(sites[i])
        else:
            min_prices.append('0')
            min_price_sites.append('none')
    # debug
    # print 'city_id:%s len(hotel_names);%s len(comments):%s len(travel_note_nums):%s len(min_prices):%s ' \
    #       'len(min_price_sites):%s len(areas):%s' % (city_id, len(hotel_names), len(comments), len(travel_note_nums),
    #                                                  len(min_prices), len(min_price_sites), len(areas))
    for i in range(len(hotel_names)):
        hotel = Hotel(city_id, hotel_names[i], comments[i], travel_note_nums[i], areas[i], min_prices[i],
                      min_price_sites[i])
        hotels.append(hotel)
    return hotels


# 获取酒店url
def get_hotels_url_list(city_id):
    in_date = '2015-11-22'
    out_date = '2015-11-23'
    url_list = []
    url_tmp = 'http://www.mafengwo.cn/hotel/ajax.php?sAction=getPoiList4&iMddId=%s&sKeyWord=&sCheckIn=%s&s' \
          'CheckOut=%s&iPage=1&sTags=&iPriceMin=0&iPriceMax=&only_available=0&only_fav=0&' \
          'sSortType=comment&sSortFlag=DESC' % (city_id, in_date, out_date)
    html = requests.get(url_tmp, timeout=30)
    page = html.content.encode('utf-8')
    target = json.loads(page)
    if target:
        length_page = target['msg']['count']/20 + 1
        for i in range(1, length_page + 1):
            url_hotel = 'http://www.mafengwo.cn/hotel/ajax.php?sAction=getPoiList4&iMddId=%s&sKeyWord=&sCheckIn=%s&s' \
            'CheckOut=%s&iPage=%s&sTags=&iPriceMin=0&iPriceMax=&only_available=0&only_fav=0&' \
            'sSortType=comment&sSortFlag=DESC' % (city_id, in_date, out_date, i)
            url_list.append(url_hotel)
    return url_list


# 测试1
def test1():
    url_mdd = 'http://www.mafengwo.cn/mdd/'
    cities = get_cities(url_mdd)  # 城市模块
    values = []
    for city in cities:
        values.append(city.get_city())
    str_sql_city = 'insert into mfw_city values(%s, %s, %s, %s, %s)'
    test_mysql(values, str_sql_city)
    cities = cities[:50]
    hotels = []
    url_list = []
    for city in cities:
        tmp_list = get_hotels_url_list(city.city_id)
        url_list.extend(tmp_list)
    pool = Pool(4)
    results = pool.map(get_hotels, url_list)
    pool.close()
    pool.join()
    if len(results) >= 1:
        for r in results:
            hotels.extend(r)
    print 'len(hotels):%s' % len(hotels)
    values = []
    for hotel in hotels:
        values.append(hotel.get_hotel())
    str_sql_city = 'insert into mfw_hotel values(%s, %s, %s, %s, %s, %s, %s)'
    test_mysql(values, str_sql_city)


def test_mysql(values, str_sql):
    try:
        conn = MySQLdb.connect(host="localhost", user="root", passwd="544989", db="python", charset="utf8")
        print u'mysql测试正常'
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    start1 = time.time()
    try:
        conn = MySQLdb.connect(host="localhost", user="root", passwd="544989", db="python", charset="utf8")
        cursor = conn.cursor()
        cursor.executemany(str_sql, values)
        cursor.close()
        conn.commit()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    end1 = time.time()
    print u'导入mysql执行时间：%s' % (end1 - start1)


if __name__ == '__main__':
    start = time.time()
    test1()
    end = time.time()
    print u'总执行时间：%s' % (end - start)

