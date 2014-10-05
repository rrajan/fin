#!/usr/bin/python

import numpy as np
import pandas as pd
import datetime

import Amop
from CalcIV import IV

def join_options(calls, puts):
    c = pd.DataFrame(calls[['Strike', 'Symbol', 'Bid', 'Ask']], copy=True)
    p = pd.DataFrame(puts[['Strike', 'Symbol', 'Bid', 'Ask']], copy=True)
    c['Expiry'] = pd.to_datetime(`20` + c['Symbol'].apply(lambda x: x[-15:-9]) )
    c['Sym'] = c['Symbol'].apply(lambda x: x[:-15])
    p['Expiry'] = pd.to_datetime(`20` + p['Symbol'].apply(lambda x: x[-15:-9]) )
    p['Sym'] = p['Symbol'].apply(lambda x: x[:-15])
    c = c.set_index(['Sym', 'Expiry', 'Strike'])
    p = p.set_index(['Sym', 'Expiry', 'Strike'])
    st = c.join(p, lsuffix='_c', rsuffix='_p')
    del st['Symbol_c']
    del st['Symbol_p']

    return st

def ivs(st, S, r, t0):
    st['IV'] = -1
    st['TV_c'] = -1
    st['TV_p'] = -1
    st = st.fillna(0)
    for i in st.index:
        t = (i[1].date() - t0).days / 365.0
        d = st.loc[i]
        iv = IV(S, i[2],d[0], d[1], d[2], d[3], r, t)
        iv.calc()
        d[4] = iv.sigma
        d[5] = iv.Ctv
        d[6] = iv.Ptv
        st.loc[i] = d

    out = st[['Bid_c', 'TV_c', 'Ask_c', 'IV', 'Bid_p', 'TV_p', 'Ask_p']]
    return out
