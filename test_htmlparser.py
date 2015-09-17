# -*- coding:UTF-8 -*-

__author__ = 'Junho'

from HTMLParser import HTMLParser
import urllib

class myHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.key = None

    def handle_starttag(self, tag, attrs):
       #  if tag == 'div' and attrs.__contains__(('class', 'zm-profile-side-following zg-clear')):
       if tag == 'strong':
            # debug
            print 'The key is true.'
            self.key = True

    def handle_data(self, data):
        if self.key:
            print 'The key is true(handle_data).'
            print(data)
            self.key = None

parser = myHTMLParser()
html = urllib.urlopen('http://www.zhihu.com/people/JunH-Huang').read()
parser.feed(html)

