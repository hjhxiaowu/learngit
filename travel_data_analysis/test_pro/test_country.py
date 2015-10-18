# -*-coding:UTF-8 -*-

__author__ = 'junho'

"""
########################################################
purpose    : 蚂蜂窝酒店数据爬虫项目——国外城市测试
date       : 2015/10/15
author     : junho
--------------------------------------------------------
2015/10/17 : 爬取城市信息（动态网页获取json）
########################################################
"""

import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from multiprocessing import Pool
from lxml import etree
import requests
import time
import MySQLdb
import pandas as pd
import sys
from functools import partial
reload(sys)
sys.setdefaultencoding('utf-8')

strUrl = 'http://www.mafengwo.cn/mdd/smap.php?mddid='

class Country():
    def __init__(self, delta=None, name=None, city=None, personNum=None):
        self.delta = delta
        self.name = name
        self.city = city
        self.personNum = personNum

    def printCountry(self):
        print u'所属洲：%s' % self.delta
        print u'国家名称：%s' % self.name
        print u'城市名称：%s' % self.city
        print u'去过人数：%s' % self.personNum

    def getCountry(self):
        li = []
        li.append(self.delta)
        li.append(self.name)
        li.append(self.city)
        li.append(self.personNum)
        return li

# 获取page
def getPage(url):
    html = requests.get(url, timeout=30)
    return etree.HTML(html.text)

# 获取国家信息：所属洲，国家名称，国家链接
def getCountryInfo(page):
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

# 获取城市信息
"""
def getCityInfo(countryid):
    citys = []
    personNums = []
    url = 'http://www.mafengwo.cn/gonglve/sg_ajax.php?sAct=getMapData&iMddid=%s&iType=3&iPage=1' % countryid
    html = requests.get(url, timeout=30)
    page = html.content.encode('utf-8')
    target = json.loads(page)
    print target['mode'], type(target['mode'])
    if target['mode'] == 1:
        for i in range(len(target['list'])):
            citys.append(target['list'][i]['name'])
            personNums.append(target['list'][i]['rank'])
    else:
        for i in range(len(target['list'])):
            citys.append(target['list'][i]['name'])
            personNums.append('0')
    return citys, personNums
"""

def getCityInfo(countryid):
    countrys = []
    url = 'http://www.mafengwo.cn/gonglve/sg_ajax.php?sAct=getMapData&iMddid=%s&iType=3&iPage=1' % countryid
    html = requests.get(url, timeout=30)
    page = html.content.encode('utf-8')
    target = json.loads(page)
    if target['mode'] == 1:
        for i in range(len(target['list'])):
            country = Country(city=target['list'][i]['name'], personNum=target['list'][i]['rank'])
            countrys.append(country)
    else:
        for i in range(len(target['list'])):
            country = Country(target['list'][i]['name'], '0')
            countrys.append(country)
    return countrys


# 国外城市爬取信息汇总
def getCountrys(url):
    page = getPage(url)
    countrys = []
    tmp_deltas, tmp_names, tmp_countryids = getCountryInfo(page)
    for i in range(len(tmp_countryids)):
        tmp_citys, tmp_personNums = getCityInfo(tmp_countryids[i])
        for j in range(len(tmp_citys)):
            country = Country(tmp_deltas[i], tmp_names[i], tmp_citys[j], tmp_personNums[j])
            country.printCountry()
            countrys.append(country)
    return countrys

# 国外城市爬取信息汇总：多进程
def getCountrys2(url):
    start = time.time()
    page = getPage(url)
    countrys = []
    tmp_deltas, tmp_names, tmp_countryids = getCountryInfo(page)
    pool = Pool(4)
    results = pool.map(getCityInfo, tmp_countryids)
    pool.close()
    pool.join()
    end = time.time()
    print u'多进程执行时间：%s' % (end - start)
    for i in range(len(results)):
        for j in range(len(results[i])):
            country = Country(tmp_deltas[i], tmp_names[i], results[i][j].city, results[i][j].personNum)
            countrys.append(country)
    print 'len(countrys):%s' % len(countrys)
    return countrys

# 测试案例1:导入pandas
def test1():
    start = time.time()
    url = 'http://www.mafengwo.cn/mdd/'
    countrys = getCountrys2(url)
    countrylists = []
    for c in countrys:
        countrylists.append(c.getCountry())
    df = pd.DataFrame(countrylists, columns=['delta', 'name', 'city', 'personNum'])
    end = time.time()
    print u'导入pandas执行时间：%s' % (end - start)
    print df

# 测试案例3：导入mysql数据库
def test3():
    try:
        conn = MySQLdb.connect(host="localhost", user="root", passwd="544989", db="python_pro", charset="utf8")
        print u'mysql测试正常'
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    start = time.time()
    url = 'http://www.mafengwo.cn/mdd/'
    countrys = getCountrys2(url)
    try:
        conn = MySQLdb.connect(host="localhost", user="root", passwd="544989", db="python_pro", charset="utf8")
        cursor = conn.cursor()
        values = []
        for country in countrys:
            values.append(country.getCountry())
        cursor.executemany('insert into tb_mfw values(%s, %s, %s, %s)', values)
        cursor.close()
        conn.commit()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    end = time.time()
    print u'导入mysql执行时间：%s' % (end - start)

# -------------------------主函数------------------------- #
if __name__ == '__main__':
    test1()