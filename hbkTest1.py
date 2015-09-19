# -*- coding:UTF-8 -*-

__author__ = 'Junho'

import urllib,re
from lxml import etree

number = ('39642',)
i = 1
while number:
    url = 'http://www.heibanke.com/lesson/crawler_ex00/' + number[0]
    print url
    html_file = urllib.urlopen(url)
    html = html_file.read()
    page = etree.HTML(html)
    h3 = page.xpath(u'//h3')
    for text in h3:
        number = re.findall('[0-9]+', text.text)
    html_file.close()
    i = i + 1
print url,i
