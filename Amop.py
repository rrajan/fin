#!/usr/bin/python

import numpy as np
import array

def option_price_call_american_binomial(S, K, r, sigma, t, steps): 
    """American Option (Call) using binomial approximations
    Converted to Python from "Financial Numerical Recipes in C" by:
    Bernt Arne Odegaard
    http://finance.bi.no/~bernt/gcc_prog/index.html
    @param S: spot (underlying) price
    @param K: strike (exercise) price,
    @param r: interest rate
    @param sigma: volatility 
    @param t: time to maturity 
    @param steps: Number of steps in binomial tree
    @return: Option price
    """
    R = np.exp(r*(t/steps))
    Rinv = 1.0/R
    u = np.exp(sigma*np.sqrt(t/steps)) 
    d = 1.0/u
    p_up = (R-d)/(u-d)
    p_down = 1.0-p_up
    prices = array.array('d', (0 for i in range(0,steps+1))) # price of underlying
    prices[0] = S*pow(d, steps) # fill in the endnodes.
    uu = u*u

    for i in xrange(1, steps+1):
        prices[i] = uu*prices[i-1]

    call_values = array.array('d', (0 for i in range(0,steps+1))) # value of corresponding call
    for i in xrange(0, steps+1):
        call_values[i] = max(0.0, (prices[i]-K)) # call payoffs at maturity

    for step in xrange(steps-1, -1, -1):
        for i in xrange(0, step+1):
            call_values[i] = (p_up*call_values[i+1]+p_down*call_values[i])*Rinv
            prices[i] = d*prices[i+1]
            call_values[i] = max(call_values[i],prices[i]-K) # check for exercise
    return call_values[0]


def option_price_put_american_binomial(S, K, r, sigma, t, steps):
    """American Option (Put) using binomial approximations
    Converted to Python from "Financial Numerical Recipes in C" by:
    Bernt Arne Odegaard
    http://finance.bi.no/~bernt/gcc_prog/index.html
    @param S: spot (underlying) price
    @param K: strike (exercise) price,
    @param r: interest rate
    @param sigma: volatility 
    @param t: time to maturity 
    @param steps: Number of steps in binomial tree
    @return: Option price
    """
    R = np.exp(r*(t/steps)) # interest rate for each step
    Rinv = 1.0/R # inverse of interest rate
    u = np.exp(sigma*np.sqrt(t/steps)) # up movement
    uu = u*u
    d = 1.0/u
    p_up = (R-d)/(u-d)
    p_down = 1.0-p_up
    prices = array.array('d', (0 for i in range(0,steps+1))) # price of underlying
    prices[0] = S*pow(d, steps) 

    for i in xrange(1, steps+1):
        prices[i] = uu*prices[i-1]

    put_values = array.array('d', (0 for i in range(0,steps+1))) # value of corresponding put

    for i in xrange(0, steps+1):
        put_values[i] = max(0.0, (K-prices[i])) # put payoffs at maturity

    for step in xrange(steps-1, -1, -1):
        for i in xrange(0, step+1):
            put_values[i] = (p_up*put_values[i+1]+p_down*put_values[i])*Rinv
            prices[i] = d*prices[i+1]
            put_values[i] = max(put_values[i],(K-prices[i])) # check for exercise
    return put_values[0]

def option_price_call_american_discrete_dividends_binomial(S, K, r, sigma, t, steps, dividend_times, dividend_amounts):
    """American Option (Call) for dividends with specific (discrete) dollar amounts 
    using binomial approximations
    Converted to Python from "Financial Numerical Recipes in C" by:
    Bernt Arne Odegaard
    http://finance.bi.no/~bernt/gcc_prog/index.html
    @param S: spot (underlying) price
    @param K: strike (exercise) price,
    @param r: interest rate
    @param sigma: volatility 
    @param t: time to maturity 
    @param steps: Number of steps in binomial tree
    @param dividend_times: Array of dividend times. (Ex: [0.25, 0.75] for 1/4 and 3/4 of a year)
    @param dividend_amounts: Array of dividend amounts for the 'dividend_times'
    @return: Option price
    """
    no_dividends = len(dividend_times)
    if (no_dividends==0): 
        return option_price_call_american_binomial(S,K,r,sigma,t,steps) # just do regular
    steps_before_dividend = (int)(dividend_times[0]/t*steps)
    R = np.exp(r*(t/steps))
    Rinv = 1.0/R
    u = np.exp(sigma*np.sqrt(t/steps))
    d = 1.0/u
    pUp = (R-d)/(u-d)
    pDown = 1.0 - pUp
    dividend_amount = dividend_amounts[0]
    tmp_dividend_times = array.array('d', (0 for i in range(0,no_dividends-1))) # temporaries with 
    tmp_dividend_amounts = array.array('d', (0 for i in range(0,no_dividends-1))) # one less dividend 
    for i in xrange(0, no_dividends-1):
        tmp_dividend_amounts[i] = dividend_amounts[i+1]
        tmp_dividend_times[i]   = dividend_times[i+1] - dividend_times[0]

    prices = array.array('d', (0 for i in range(0,steps_before_dividend+1)))
    call_values = array.array('d', (0 for i in range(0,steps_before_dividend+1)))
    prices[0] = S*pow(d, steps_before_dividend)

    for i in xrange(1, steps_before_dividend+1):
        prices[i] = u*u*prices[i-1]

    for i in xrange(0, steps_before_dividend+1):
        value_alive = option_price_call_american_discrete_dividends_binomial(prices[i]-dividend_amount,K, r, sigma,
                                     t-dividend_times[0], # time after first dividend
                                     steps-steps_before_dividend, 
                                     tmp_dividend_times,
                                     tmp_dividend_amounts)
        call_values[i] = max(value_alive,(prices[i]-K)) # compare to exercising now

    for step in xrange(steps_before_dividend-1, -1, -1):
        for i in xrange(0, step+1):
            prices[i] = d*prices[i+1]
            call_values[i] = (pDown*call_values[i]+pUp*call_values[i+1])*Rinv
            call_values[i] = max(call_values[i], prices[i]-K)

    return call_values[0]


def option_price_put_american_discrete_dividends_binomial(S, K, r, sigma, t, steps, dividend_times, dividend_amounts): 
    """American Option (Put) for dividends with specific (discrete) dollar amounts 
    using binomial approximations.
    Converted to Python from "Financial Numerical Recipes in C" by:
    Bernt Arne Odegaard
    http://finance.bi.no/~bernt/gcc_prog/index.html
    @param S: spot (underlying) price
    @param K: strike (exercise) price,
    @param r: interest rate
    @param sigma: volatility 
    @param t: time to maturity 
    @param steps: Number of steps in binomial tree
    @param dividend_times: Array of dividend times. (Ex: [0.25, 0.75] for 1/4 and 3/4 of a year)
    @param dividend_amounts: Array of dividend amounts for the 'dividend_times'
    @return: Option price
    """

    # given an amount of dividend, the binomial tree does not recombine, have to 
    # start a new tree at each ex-dividend date.
    # do this recursively, at each ex dividend date, at each step, put the 
    # binomial formula starting at that point to calculate the value of the live
    # option, and compare that to the value of exercising now.

    no_dividends = len(dividend_times)
    if (no_dividends == 0): # just take the regular binomial 
        return option_price_put_american_binomial(S,K,r,sigma,t,steps)
    steps_before_dividend = (int)(dividend_times[0]/t*steps);

    R = np.exp(r*(t/steps))
    Rinv = 1.0/R
    u = np.exp(sigma*np.sqrt(t/steps))
    uu= u*u
    d = 1.0/u
    pUp = (R-d)/(u-d)
    pDown = 1.0 - pUp
    dividend_amount = dividend_amounts[0]

    tmp_dividend_times = array.array('d', (0 for i in range(0,no_dividends-1))) # temporaries with 
    tmp_dividend_amounts = array.array('d', (0 for i in range(0,no_dividends-1))) # one less dividend 
    for i in xrange(0, no_dividends-1): 
        tmp_dividend_amounts[i] = dividend_amounts[i+1]
        tmp_dividend_times[i]= dividend_times[i+1] - dividend_times[0]

    prices = array.array('d', (0 for i in range(0,steps_before_dividend+1)))
    put_values = array.array('d', (0 for i in range(0,steps_before_dividend+1)))
    prices[0] = S*pow(d, steps_before_dividend)

    for i in xrange(1, steps_before_dividend+1):
        prices[i] = uu*prices[i-1]

    for i in xrange(0, steps_before_dividend+1):
        value_alive = option_price_put_american_discrete_dividends_binomial(
                    prices[i]-dividend_amount, K, r, sigma, 
                    t-dividend_times[0], # time after first dividend
                    steps-steps_before_dividend, 
                    tmp_dividend_times, tmp_dividend_amounts)  
        # what is the value of keeping the option alive?  Found recursively, 
        # with one less dividend, the stock price is current value 
        # less the dividend.
        put_values[i] = max(value_alive,(K-prices[i])) # compare to exercising now

    for step in xrange(steps_before_dividend-1, -1, -1):
        for i in xrange(0, step+1):
            prices[i] = d*prices[i+1]
            put_values[i] = (pDown*put_values[i]+pUp*put_values[i+1])*Rinv
            put_values[i] = max(put_values[i], K-prices[i]) # check for exercise

    return put_values[0]


def option_price_call_american_proportional_dividends_binomial(S, K, r, sigma, 
                            time, no_steps, dividend_times, dividend_yields):
    """American Option (Call) with proportional dividend payments 
    using binomial approximations.
    Converted to Python from "Financial Numerical Recipes in C" by:
    Bernt Arne Odegaard
    http://finance.bi.no/~bernt/gcc_prog/index.html
    @param S: spot (underlying) price
    @param K: strike (exercise) price,
    @param r: interest rate
    @param sigma: volatility 
    @param time: time to maturity 
    @param no_steps: Number of steps in binomial tree
    @param dividend_times: Array of dividend times. (Ex: [0.25, 0.75] for 1/4 and 3/4 of a year)
    @param dividend_yields: Array of dividend yields for the 'dividend_times'
    @return: Option price
    """
    # note that the last dividend date should be before the expiry date, problems if dividend at terminal node
    no_dividends=len(dividend_times)
    if (no_dividends == 0):
        return option_price_call_american_binomial(S,K,r,sigma,time,no_steps) # price w/o dividends

    delta_t = time/no_steps
    R = np.exp(r*delta_t)
    Rinv = 1.0/R
    u = np.exp(sigma*np.sqrt(delta_t))
    uu= u*u
    d = 1.0/u
    pUp = (R-d)/(u-d)
    pDown = 1.0 - pUp
    dividend_steps = array.array('d', (0 for i in range(0,no_dividends))) # when dividends are paid

    for i in xrange(0, no_dividends): 
        dividend_steps[i] = (int)(dividend_times[i]/time*no_steps)

    prices = array.array('d', (0 for i in range(0,no_steps+1)))
    call_prices = array.array('d', (0 for i in range(0,no_steps+1)))
    prices[0] = S*pow(d, no_steps)# adjust downward terminal prices by dividends

    for i in xrange(0, no_dividends):
        prices[0]*=(1.0-dividend_yields[i])

    for i in xrange(1, no_steps+1):
        prices[i] = uu*prices[i-1]

    for i in xrange(1, no_steps+1):
        call_prices[i] = max(0.0, (prices[i]-K))

    for step in xrange(no_steps-1, -1, -1):
        for i in xrange(0, no_dividends): # check whether dividend paid      
            if (step==dividend_steps[i]): 
                for j in xrange(0, step+2):
                    prices[j]*=(1.0/(1.0-dividend_yields[i]))
        for i in xrange(0, step+1):            
            call_prices[i] = (pDown*call_prices[i]+pUp*call_prices[i+1])*Rinv
            prices[i] = d*prices[i+1]
            call_prices[i] = max(call_prices[i], prices[i]-K) #check for exercise

    return call_prices[0]


def option_price_put_american_proportional_dividends_binomial(S, K, r, sigma, 
                            time, no_steps, dividend_times, dividend_yields):
    """American Option (Put) with proportional dividend payments 
    using binomial approximations.
    Converted to Python from "Financial Numerical Recipes in C" by:
    Bernt Arne Odegaard
    http://finance.bi.no/~bernt/gcc_prog/index.html
    @param S: spot (underlying) price
    @param K: strike (exercise) price,
    @param r: interest rate
    @param sigma: volatility 
    @param time: time to maturity 
    @param no_steps: Number of steps in binomial tree
    @param dividend_times: Array of dividend times. (Ex: [0.25, 0.75] for 1/4 and 3/4 of a year)
    @param dividend_yields: Array of dividend yields for the 'dividend_times'
    @return: Option price
    """

    # when one assume a dividend yield, the binomial tree recombines 
    # note that the last dividend date should be before the expiry date
    no_dividends=len(dividend_times);
    if (no_dividends == 0): # just take the regular binomial 
        return option_price_put_american_binomial(S,K,r,sigma,time,no_steps)

    R = np.exp(r*(time/no_steps))
    Rinv = 1.0/R
    u = np.exp(sigma*np.sqrt(time/no_steps))
    uu= u*u
    d = 1.0/u
    pUp   = (R-d)/(u-d)
    pDown = 1.0 - pUp
    dividend_steps = array.array('d', (0 for i in range(0,no_dividends))) # when dividends are paid

    for i in xrange(0, no_dividends):
        dividend_steps[i] = (int)(dividend_times[i]/time*no_steps);

    prices = array.array('d', (0 for i in range(0,no_steps+1)))
    put_prices = array.array('d', (0 for i in range(0,no_steps+1)))
    prices[0] = S*pow(d, no_steps);

    for i in xrange(0, no_dividends):
        prices[0]*=(1.0-dividend_yields[i])

    for i in xrange(1, no_steps+1):
        prices[i] = uu*prices[i-1] #terminal tree nodes

    for i in xrange(1, no_steps+1):
        put_prices[i] = max(0.0, (K-prices[i]))

    for step in xrange(no_steps-1, -1, -1):
        for i in xrange(0, no_dividends): # check whether dividend paid
            if (step==dividend_steps[i]):
                for j in xrange(0, step+2):
                    prices[j]*=(1.0/(1.0-dividend_yields[i]))
        for i in xrange(0, step+1): 
            prices[i] = d*prices[i+1]
            put_prices[i] = (pDown*put_prices[i]+pUp*put_prices[i+1])*Rinv
            put_prices[i] = max(put_prices[i], K-prices[i]) # check for exercise

    return put_prices[0]
