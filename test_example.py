from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.key = None

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.key = True
            print('<%s>' % tag)

    def handle_data(self, data):
        if self.key:
            print(data)
            self.key = None

    """
    def handle_comment(self, data):
        print('<!-- -->')
    def handle_entityref(self, name):
        print('&%s;' % name)

    def handle_charref(self, name):
        print('&#%s;' % name)

    """
parser = MyHTMLParser()
parser.feed('<html><head></head><body><p>Some <a href=\"#\">html</a> tutorial...<br>END</p></body></html>')
