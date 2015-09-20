# -*- coding:UTF-8 -*-

__author__ = 'Junho'

import urllib,urllib2
import threading,time
from lxml import etree

def test():
    url = 'http://www.heibanke.com/lesson/crawler_ex01/'
    for i in range(30):
        test_data = {'username':'123', 'password': '%d' % i}
        post_data = urllib.urlencode(test_data)
        f = urllib2.urlopen(url, post_data)
        html = f.read()
        page = etree.HTML(html)
        h3 = page.xpath(u'//h3')
        for h in h3:
            text = h.text
        f.close()
        if text != u'您输入的密码错误, 请重新输入':
            print '测试成功'
            break

test()
