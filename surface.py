#!/usr/bin/python

import numpy as np
import pandas as pd
import datetime
import sys

import Amop
from CalcIV import IV

def join_options(calls, puts):
    c = pd.DataFrame(calls[['Quote_Time', 'Underlying_Price', 'Strike', 'Symbol', 'Bid', 'Ask']], copy=True)
    p = pd.DataFrame(puts[['Quote_Time', 'Underlying_Price', 'Strike', 'Symbol', 'Bid', 'Ask']], copy=True)
    c['Expiry'] = pd.to_datetime(`20` + c['Symbol'].apply(lambda x: x[-15:-9]) )
    c['Quote_Time'] = pd.to_datetime(c['Quote_Time'])
    c['Sym'] = c['Symbol'].apply(lambda x: x[:-15])
    p['Expiry'] = pd.to_datetime(`20` + p['Symbol'].apply(lambda x: x[-15:-9]) )
    p['Quote_Time'] = pd.to_datetime(p['Quote_Time'])
    p['Sym'] = p['Symbol'].apply(lambda x: x[:-15])
    c = c.set_index(['Sym', 'Quote_Time', 'Underlying_Price', 'Expiry', 'Strike'])
    p = p.set_index(['Sym', 'Quote_Time', 'Underlying_Price', 'Expiry', 'Strike'])
    st = c.join(p, lsuffix='_c', rsuffix='_p')
    del st['Symbol_c']
    del st['Symbol_p']

    return st

def ivs(st, r):
    st['Tau'] = -1
    st['IV'] = -1
    st['TV_c'] = -1
    st['TV_p'] = -1
    st = st.fillna(0)
    for i in st.index:
        t = (i[3] - i[1]).days / 365.0
        S = i[2]
        K = i[4]
        d = st.loc[i]
        iv = IV(S, K, d[0], d[1], d[2], d[3], r, t)
        iv.calc()
        d[4] = t
        d[5] = iv.sigma
        d[6] = iv.Ctv
        d[7] = iv.Ptv
        st.loc[i] = d

    out = st[['Bid_c', 'TV_c', 'Ask_c', 'IV', 'Tau', 'Bid_p', 'TV_p', 'Ask_p']]
    return out

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print "need input"
        sys.exit(1)

    mktData = pd.read_csv(sys.argv[1])
    mktData = mktData[mktData['IsNonstandard'] == False] # remove non-standards
    r = 0.01
    #print mktData
    calls = mktData[mktData['Type'] == 'call']
    puts = mktData[mktData['Type'] == 'put']

    opt = join_options(calls, puts)
    opt_ivs = ivs(opt, r)

    print 'writing to - ', sys.argv[1] + '.ivs'
    opt_ivs.to_csv(sys.argv[1] + '.ivs', float_format='%.4f')
