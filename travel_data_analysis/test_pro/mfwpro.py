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

# 酒店类
class Hotel:
    def __init__(self, delta, country, city, people, hotel, comment_num, travel_note_num, area, min_price,
                 min_price_site):
        self.delta = delta
        self.country = country
        self.city = city
        self.people = people
        self.hotel = hotel
        self.comment_num = comment_num
        self.travel_note_num = travel_note_num
        self.area = area
        self.min_price = min_price
        self.min_price_site = min_price_site

    def get_hotel(self):
        li = []
        li.append(self.delta)
        li.append(self.country)
        li.append(self.city)
        li.append(self.people)
        li.append(self.hotel)
        li.append(self.comment_num)
        li.append(self.travel_note_num)
        li.append(self.area)
        li.append(self.min_price)
        li.append(self.min_price_site)
        return li

# ----------------------------------爬虫---------------------------------- #


def get_page(url):
    html = requests.get(url, timeout=30)
    return etree.HTML(html.text)


def get_country_info(page):
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


def get_city_info(country_ids):
    cities = []
    peoples = []
    city_ids = []
    url = 'http://www.mafengwo.cn/gonglve/sg_ajax.php?sAct=getMapData&iMddid=%s&iType=3&iPage=1' % country_ids
    html = requests.get(url, timeout=30)
    page = html.content.encode('utf-8')
    target = json.loads(page)
    print target['mode'], type(target['mode'])
    if target['mode'] == 1:
        for i in range(len(target['list'])):
            cities.append(target['list'][i]['name'])
            peoples.append(target['list'][i]['rank'])
            city_ids.append(target['list'][i]['id'])
    else:
        for i in range(len(target['list'])):
            cities.append(target['list'][i]['name'])
            peoples.append('0')
            city_ids.append(target['list'][i]['id'])
    return cities, peoples, city_ids


def get_hotel_info(page):
    names = page.xpath('//div[@class="hotel-list"]/div[@class="hotel-item clearfix h-item"]/@data-name')
    return names


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


def get_travel_ote_info(page):
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





