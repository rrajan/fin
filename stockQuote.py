#!/usr/bin/python

import urllib
import re

class StockQuote:

    def get_quote(self, symbol):
        data = []
        url = 'http://finance.yahoo.com/d/quotes.csv?s='
        #for s in symbols:
        #    url += s+"+"
        #url = url[0:-1]
        url += symbol
        url += "&f=sb3b2l1l"
        f = urllib.urlopen(url,proxies = {})
        rows = f.read()
        values = [x for x in rows.split(',')]
        #symbol = values[0][1:-1]
        #bid = values[1]
        #ask = values[2]
        #last = values[3]
        #data.append([symbol,bid,ask,last,values[4]])
        #return data
        return values

if __name__ == '__main__':
    sq = StockQuote()
    print sq.get_quote('AAPL')
