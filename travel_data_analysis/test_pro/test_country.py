# -*-coding:UTF-8 -*-

__author__ = 'HJH'

"""
########################################################
purpose    : 蚂蜂窝酒店数据爬虫项目——国外城市测试
date       : 2015/10/15
author     : junho
--------------------------------------------------------
########################################################
"""

from multiprocessing import Pool
from lxml import etree
import requests
import time
import pandas as pd
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Country():
    def __init__(self, name, city, personNum):
        self.name = name
        self.city = city
        self.personNum = personNum

    def __init__(self, name):
        self.name = name

    def printCountry(self):
        print u'国家名称：%s' % self.name

    def getCountry(self):
        li = []
        li.append(self.name)
        li.append(self.city)
        li.append(self.personNum)
        return li

# 获取page
def getPage(url):
    html = requests.get(url, timeout=30)
    return etree.HTML(html.text)

# 获取国家信息（剔除中国）
def getCountryInfo(page):
    content_field = page.xpath('//*[@data-cs-p="全球目的地"]/div/dl')
    cNames = []
    deltas = []
    for each in content_field:
        delta = each.xpath('dt/text()')[0]
        print delta  # 测试洲
        tmpCnames = each.xpath('dd/ul/a/text()')
    return cNames

# 获取城市信息
def getCityInfo(page):


# 国外城市爬取信息汇总
def getCountrys(url):
    countrys = []
    page = getPage(url)
    cNames = getCountryInfo(page)
    for name in cNames:
        country = Country(name)
        countrys.append(country)
    return countrys

# 测试案例1:
def test1():
    start = time.time()
    url = 'http://www.mafengwo.cn/mdd/'
    countrys = getCountrys(url)
    for c in countrys:
        c.printCountry()

# -------------------------主函数------------------------- #
if __name__ == '__main__':
    test1()