#!/usr/bin/python

import numpy as np
import pandas as pd
import sys
import datetime
import urllib
import time

from pandas.io.data import DataReader
from pandas.io.data import Options

np.set_printoptions(precision=4, suppress=True, linewidth=2000)
pd.set_option('display.width', 2000)
pd.set_option('max.columns', 50)
pd.set_option('precision', 4)

def get_quote(symbol):
    data = []
    url = 'http://finance.yahoo.com/d/quotes.csv?s='
    #for s in symbols:
    #    url += s+"+"
    #url = url[0:-1]
    url += symbol
    url += "&f=sb3b2l1l"
    now = datetime.datetime.now()
    f = urllib.urlopen(url,proxies = {})
    rows = f.read()
    now2 = datetime.datetime.now()
    print 'get_quote():', now2-now
    values = [x for x in rows.split(',')]
    #symbol = values[0][1:-1]
    #bid = values[1]
    #ask = values[2]
    #last = values[3]
    #data.append([symbol,bid,ask,last,values[4]])
    #return data
    return (now2, values)

def get_underlying(sym, start_date):
    now = datetime.datetime.now()
    dr = DataReader(sym, 'yahoo', start=start_date)
    now2 = datetime.datetime.now()
    print 'get_underlying():', now2-now
    return (now2, dr)

def get_options(sym, expiry, above_below=0):
    opt = Options(sym, 'yahoo')
    now = datetime.datetime.now()
    opt_data = opt.get_options_data(expiry=expiry)
    if (above_below > 0):
        opt_data = opt.get_near_stock_price(expiry=expiry, put=True, above_below=above_below)
    now2 = datetime.datetime.now()
    print 'get_options():', now2-now
    return (now2, opt_data)

def run():
    while [True]:
        print "Help"
        time.sleep(10)

if __name__ == '__main__':

    run()

    if (len(sys.argv) < 2):
        print 'need symbol, usage:', sys.argv[0], '<sym> [start_date or expiration] [OPT]'
        sys.exit(1)

    sym = sys.argv[1]
    today = datetime.date.today()
    lastMonth = today - datetime.timedelta(days=30)
    nextMonth = today + datetime.timedelta(days=30)

    if (len(sys.argv) < 3):
        data = get_quote(sym)
    else:
        d = pd.to_datetime(sys.argv[2]).date()
        start_date = d
        expiry = d
        if (len(sys.argv) < 4):
            print 'fetch underlying from', start_date
            data = get_underlying(sym, start_date)
        else:
            print 'fetch option', expiry
            data = get_options(sym, expiry)

    print data[0]
    print data[1]
