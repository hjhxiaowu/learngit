# -*- coding:UTF-8 -*-

__author__ = 'Junho'

import urllib,urllib2
import time
import threading
from multiprocessing import Pool
from lxml import etree
import requests
import json

t = None
def test(num):
    url = 'http://www.heibanke.com/lesson/crawler_ex01/'
    test_data = {'username':'123', 'password': '%d' % num}
    # post_data = urllib.urlencode(test_data)
    # print 'f.open()'
    # f = urllib2.urlopen(url, post_data)
    # html = f.read()
    html = requests.post(url,data=test_data)
    page = etree.HTML(html.content)
    h3 = page.xpath(u'//h3')
    global t
    for h in h3:
        t = h.text
    print t, num
    return t
    # print 'f.close()'
    # f.close()
    # if t != u'您输入的密码错误, 请重新输入':
          # print '测试成功'
          # print text,num
          # return num
    # else:
          # print text,num
          # return num

def test2(num):
    return num*num

start = time.time()
ret = []
for i in range(30):
    ret.append(test2(i))
end = time.time()
print u'单线程执行时间：'
print end - start
print ret

# -------------------------------------- #
# 多进程
start1 = time.time()
pool = Pool(4)
# for i in range(31):
results = pool.map(test2,range(30))
pool.close()
pool.join()
end1 = time.time()
print u'多进程执行时间:'
print end1 - start1
print len(results)
print results
"""
# -------------------------------------- #
# 多线程1
start2 = time.time()
threads = []
for i in range(30):
    t = threading.Thread(target=test,args=(i,))
    t.start()
    threads.append(t)
for th in threads:
    th.join()
end2 = time.time()
print u'多线程执行时间'
print end2 - start2


# -------------------------------------- #
# 并行（极客学院）
start3 = time.time()
pool = Pool(4)
nums = range(31)
results = pool.map(test,nums)
pool.close()
pool.join()
end3 = time.time()
print u'并行（极客学院）执行时间'
print end3 - start3

"""
