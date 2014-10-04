#!/usr/bin/py

import numpy as np
import scipy.optimize

from Amop import *

class IV:

    def __init__(self, S, K, Cb, Ca, Pb, Pa, rate, time, amop_steps=100, opt_iter=1000, disp=False, full_output=False):
        self.S = S
        self.K = K
        self.Cb = Cb
        self.Ca = Ca
        self.Ctv = -1
        self.Pb = Pb
        self.Pa = Pa
        self.Ptv = -1
        self.rate = rate
        self.time = time
        self.sigma = 0.1
        self.amop_step=amop_steps
        self.opt_iter=opt_iter
        self.disp=disp
        self.full_output=full_output

    def cost(self, sigma):
        self.Ctv = option_price_call_american_binomial(self.S, self.K, self.rate, sigma, self.time, self.amop_steps)
        self.Ptv = option_price_put_american_binomial(self.S, self.K, self.rate, sigma, self.time, self.amop_steps)

        return abs(self.Ctv - self.Ptv - self.S + self.K * np.exp(-self.rate * self.time))

    def calc(S, K, Cb, Ca, Pb, Pa, r, t):
        self.sigma = scipy.optimize.fmin(func=self.cost, x0=self.sigma, max_iter=self.opt_iter, disp=self.disp, full_output=self.full_output)
        return self.sigma


if __name__ == '__main__':

    S = 99.62
    rate = 0.01
    time = 0.136986301369863  #[ a_exp = datetime.date(2014,11,22), a_last = datetime.date(2014,10,3)]
    K = 100.0
#>>> d[d['Strike'] == 100]
#    Strike                Symbol  Last   Chg   Bid   Ask   Vol  Open Int
#    25     100   AAPL141107C00100000  3.25  0.15  3.10  3.20   266      1004
#    26     100   AAPL141122C00100000  3.50  0.20  3.45  3.55  5755     82991
#    27     100  AAPL7141122C00100000  3.50  0.11  3.40  3.55    82       323
#>>> dp[dp['Strike'] == 100]
#    Strike                Symbol  Last   Chg   Bid   Ask  Vol  Open Int
#    28     100   AAPL141107P00100000  3.64  0.03  3.70  3.85    5       154
#    29     100   AAPL141122P00100000  4.15  0.10  4.15  4.25  599     26207
#    30     100  AAPL7141122P00100000  4.20  0.00  4.05  4.25    8       313

    Cb = 3.45
    Ca = 3.55
    Pb = 4.15
    Pa = 4.25
    iv = IV(S, K, Cb, Ca, Pb, Pa, rate, time, amop_steps=100, opt_iter=1000, disp=True, full_output=True)
    iv.calc

    print "Vol:", iv.sigma, "TV:", iv.Ctv, "(C)", iv.Ptv, "(P)"
