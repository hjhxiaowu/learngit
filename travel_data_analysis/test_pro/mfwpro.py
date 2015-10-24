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

from multiprocessing import Pool
from lxml import etree
import requests
import time
import random
import pandas as pd
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


# 爬虫类
"""
class Crawler:
    def __init__(self):
        pass

    def get_page(self, url):
        html = requests.get(url, timeout=30)
        return etree.HTML(html.text)

    def get_country_info(self, page):
        content_field = page.xpath('//div[@class="container"]/div[6]/div/div[1]/div/dl')
        names = []
        deltas = []
        countryids = []
        for each in content_field:
            delta = each.xpath('dt/text()')[0]
            tmp_names = each.xpath('dd/ul/li/a/text()')
            tmp_countryids = each.xpath('dd/ul/li/a/@href')
            for i in range(len(tmp_names)):
                names.append(tmp_names[i].strip())
                deltas.append(delta)
                countryids.append(str(tmp_countryids[i])[-10:-5])
        return deltas, names, countryids
"""


# ----------------------------------爬虫---------------------------------- #
def get_page(url):
    html = requests.get(url, timeout=30)
    return etree.HTML(html.text)


def get_country_info(page):
    content_field = page.xpath('//div[@class="container"]/div[6]/div/div[1]/div/dl')
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


def get_city_info(country_ids):
    city_names = []
    peoples = []
    city_ids = []
    url = 'http://www.mafengwo.cn/gonglve/sg_ajax.php?sAct=getMapData&iMddid=%s&iType=3&iPage=1' % country_ids
    html = requests.get(url, timeout=30)
    page = html.content.encode('utf-8')
    target = json.loads(page)
    print target['mode'], type(target['mode'])
    if target['mode'] == 1:
        for i in range(len(target['list'])):
            city_names.append(target['list'][i]['name'])
            peoples.append(target['list'][i]['rank'])
            city_ids.append(target['list'][i]['id'])
    else:
        for i in range(len(target['list'])):
            city_names.append(target['list'][i]['name'])
            peoples.append('0')
            city_ids.append(target['list'][i]['id'])
    return city_names, peoples, city_ids


def get_cities(url):
    start_in = time.time()
    page = get_page(url)
    cities = []
    tmp_deltas, tmp_countries, tmp_country_ids = get_country_info(page)
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


def get_hotel_name(page):
    hotel_names = page.xpath('//div[@class="hotel-list"]/div[@class="hotel-item clearfix h-item"]/@data-name')
    return hotel_names


def get_comments(page):
    comments = []
    content_field = page.xpath('//div[@class="hotel-list"]/div[@class="hotel-item clearfix h-item"]')
    for each in content_field:
        comment = each.xpath('div[@class="hotel-info"]/ul/li[1]/a/em/text()')
        if comment:
            comments.append(comment[0])
        else:
            comments.append(u'0条')
    return comments


def get_travel_note_info(page):
    travel_note_nums = []
    content_field = page.xpath('//div[@class="hotel-list"]/div[@class="hotel-item clearfix h-item"]')
    for each in content_field:
        travel_note_num = each.xpath('div[@class="hotel-info"]/ul/li[3]/a/em/text()')
        if travel_note_num:
            travel_note_nums.append(travel_note_num[0])
        else:
            travel_note_nums.append(u'0篇')
    return travel_note_nums


def get_areas(page):
    areas = []
    content_field = page.xpath('//div[@class="hotel-list"]/div[@class="hotel-item clearfix h-item"]/div[3]/div/span')
    for each in content_field:
        area = each.xpath('a/text()')
        if area:
            areas.append(area[0])
        else:
            areas.append(u'无提供信息')
    return areas


def get_price_info(page):
    content_field = page.xpath('//*[@id="hotel_list"]/div[@class="hotel-item clearfix h-item"]/div[5]')
    min_prices = []
    min_price_sites = []
    for each in content_field:
        prices = each.xpath('a/em[@class="p"]/span[1]/text()')
        sites = each.xpath('a/@data-otaname')
        i = 0
        min_price = int(prices[0])
        for index, item in enumerate(prices):
            prices[index] = int(item)
            if min_price >= prices[index]:
                min_price = prices[index]
                i = index
        min_prices.append(min_price)
        min_price_sites.append(sites[i])
    return min_prices, min_price_sites


def get_hotels(url):
    hotels = []
    city_id = url[29:34]
    print city_id
    page = get_page(url)
    hotel_names = get_hotel_name(page)
    comments = get_comments(page)
    travel_note_nums = get_travel_note_info(page)
    min_prices, min_price_sites = get_price_info(page)
    areas = get_areas(page)
    for i in range(20):
        hotel = Hotel(city_id, hotel_names[i], comments[i], travel_note_nums[i], areas[i], min_prices[i],
                      min_price_sites[i])
        hotels.append(hotel)
    return hotels


def get_hotels_pool(city_id):
    in_date = '2015-11-22'
    out_date = '2015-11-23'
    url_tmp = 'http://www.mafengwo.cn/hotel/%s/#indate=%s&outdate=%s&q=&p=1&scope=city%%2C0%%2C&sort=comment_desc&sales=0&price=0%%2C' % (city_id, in_date, out_date)
    length_hotel = get_page(url_tmp).xpath('//div[@id="list_paginator"]/span/span[1]/text()')[0]
    url_list, hotels = [], []
    for i in range(1, length_hotel + 1):
        url_hotel = 'http://www.mafengwo.cn/hotel/%s/#indate=%s&outdate=%s&q=&p=%s&scope=city%%2C0%%2C&sort=comment_desc&sales=0&price=0%%2C' % (city_id, in_date, out_date, i)
        print url_hotel
        url_list.append(url_hotel)
    pool = Pool(4)
    results = pool.map(get_hotels, url_list)
    pool.close()
    pool.join()
    if len(results) != 0:
        for li in results:
            hotels.extend(li)
    return hotels


def test1():
    url_mdd = 'http://www.mafengwo.cn/mdd/'
    cities = get_cities(url_mdd)  # 城市模块
    hotels = []
    for city in cities:
        if city.people == '0' or city.people is None or city.people == 'null':
            hotel = Hotel(city_id=city.city_id)
            hotels.append(hotel)
        else:
            hotel_list = get_hotels_pool(city.city_id)
            hotels.extend(hotel_list)
    mfws = []
    li = []
    for i in range(len(hotels)):
        li.append()


def tmp_test():
    url_tmp = 'http://www.mafengwo.cn/hotel/10855/?sFrom=mdd#indate=2015-11-10&outdate=2015-11-11&q=&p=1&scope=city%2C0%2C&sort=comment_desc&sales=0&price=0%2C&tag=0'
    page = get_page(url_tmp)
    length = page.xpath('//div[@id="list_paginator"]/span/span[1]/text()')[0]
    print length


if __name__ == '__main__':
    start = time.time()
    # test1()
    tmp_test()
    end = time.time()
    print u'总执行时间：%s' % (end - start)

