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

strUrl = 'http://www.mafengwo.cn/mdd/smap.php?mddid='

class Country():
    def __init__(self, delta, name, city, personNum):
        self.delta = delta
        self.name = name
        self.city = city
        self.personNum = personNum

    def __init__(self, name):
        self.name = name

    def printCountry(self):
        print u'国家名称：%s' % self.name

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
    content_field = page.xpath('//div[@class="container"]/div[7]/div/div[1]/div/dl')
    names = []
    deltas = []
    hrefs = []
    for each in content_field:
        delta = each.xpath('dt/text()')[0]
        tmp_names = each.xpath('dd/ul/li/a/text()')
        tmp_hrefs = each.xpath('dd/ul/li/a/@href')
        for i in range(len(tmp_names)):
            names.append(tmp_names[i].strip())
            deltas.append(delta)
            hrefs.append(str(tmp_hrefs[i])[-10:-5])
    return deltas, names, hrefs

# 获取城市信息
def getCityInfo(page):
    # //*[@id="poi_146952"]/h3/a
    # //*[@id="poiList"]
    citys = page.xpath('//*[@id="poiList"]/li/h3/a/text()')
    personNums = page.xpath('//*[@id="poiList"]/li/p[1]/span/text()')
    print len(citys), len(personNums)
    return citys, personNums


# 国外城市爬取信息汇总
def getCountrys(url):
    page = getPage(url)
    countrys = []
    tmp_deltas, tmp_names, hrefs = getCountryInfo(page)
    for i in range(len(hrefs)):
        page_in = getPage(strUrl + hrefs[i])
        print strUrl + hrefs[i]
        tmp_citys, tmp_personNums = getCityInfo(page_in)
        for j in range(len(tmp_citys)):
            countrys = Country(tmp_deltas[i], tmp_names[i], tmp_citys[j], tmp_personNums[j])
    return countrys

# 测试案例1:
def test1():
    url = 'http://www.mafengwo.cn/mdd/'
    countrys = getCountrys(url)
    countrylists = []
    for c in countrys:
        countrylists.append(c.getCountry())
    df = pd.DataFrame(countrylists, columns=['delta', 'name', 'city', 'personNum'])
    print df

# -------------------------主函数------------------------- #
if __name__ == '__main__':
    test1()