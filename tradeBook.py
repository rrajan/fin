#!/usr/bin/python

import sys
import pandas as pd

class TradeBook:

    def build(self, d):
        trade = d[d[1] == 'P']
        quote = d[d[1] == 'Q']
        bid = quote[quote[4] == 'B'][[5,6,7]]
        ask = quote[quote[4] == 'A'][[5,6,7]]
        bid.columns = ['bprice', 'bsize', 'borders']
        ask.columns = ['aprice', 'asize', 'aorders']

        bid_ask = bid.join(ask, how="outer")
        ba = bid_ask.fillna(method='ffill')

        trade[4] = trade[4].astype(float)
        t = trade.iloc[:,(3,4)]
        t.columns = ['tprice', 'tq']
        tgp = t.groupby(level=0)

        tr = pd.DataFrame(tgp['tprice'].mean()).join(pd.DataFrame(tgp['tq'].sum()))

        book = tr.join(ba, how="outer")
        book['tprice'] = book['tprice'].fillna(0)
        book['tq'] = book['tq'].fillna(0)
        book = book.fillna(method='ffill')

        return book


if __name__ == '__main__':

    if (len(sys.argv) < 3):
        print "Need 2 arugments! <arg1=input_file> <arg2=output_file>. Exiting..."
        sys.exit()

    pd.options.mode.chained_assignment = None

    d = pd.read_csv(sys.argv[1], index_col=0, header=None)
    tb = TradeBook()
    book = tb.build(d)
    book.to_csv(sys.argv[2])
