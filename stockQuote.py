#!/usr/bin/python

import urllib
import re

class StockQuote:

    def get_quote(self, symbol):
            #base_url = 'http://finance.google.com/finance?q='
            base_url = 'http://finance.yahoo.com/d/quotes.csv?s='
            content = urllib.urlopen(base_url + symbol).read()
            m = re.search('id="ref_694653_l".*?>(.*?)<', content)
            if m:
                quote = m.group(1)
            else:
                quote = 'no quote available for: ' + symbol
                return quote

if __name__ == '__main__':
    sq = StockQuote()
    print sq.get_quote('AAPL')
