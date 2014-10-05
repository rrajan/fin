#!/usr/bin/python

import unittest
import Amop

class AmopTest(unittest.TestCase):

    def test_option_price_call_american_binomial(self):
        S = 100
        K = 100
        r = 0.10
        sigma = 0.25
        time = 1.0
        steps = 100
        test_val = Amop.option_price_call_american_binomial(S, K, r, sigma, time, steps)
        self.assertEqual(str(round(test_val, 4)), "14.9505")
        # Test 2
        S = 72
        K = 72
        r = 0.05
        sigma = 0.40
        time = 0.5
        steps = 200
        test_val = Amop.option_price_call_american_binomial(S, K, r, sigma, time, steps)
        self.assertEqual(str(round(test_val, 5)), "8.90719")


    def test_option_price_put_american_binomial(self):
        S = 100
        K = 100
        r = 0.10
        sigma = 0.25
        time = 1.0
        steps = 100
        test_val = Amop.option_price_put_american_binomial(S, K, r, sigma, time, steps)
        self.assertEqual(str(round(test_val, 5)), "6.54691")
        # Test 2
        S = 72
        K = 72
        r = 0.05
        sigma = 0.40
        time = 0.5
        steps = 200
        test_val = Amop.option_price_put_american_binomial(S, K, r, sigma, time, steps)
        self.assertEqual(str(round(test_val, 5)), "7.29582")

    def test_option_price_call_american_discrete_dividends_binomial(self):
        S = 100
        K = 100
        r = 0.10
        sigma = 0.25
        time = 1.0
        steps = 100
        dividend_times = [0.25, 0.75]
        dividend_amounts = [2.5, 2.5]
        test_val = Amop.option_price_call_american_discrete_dividends_binomial(S, K, 
                    r, sigma, time, steps, dividend_times, dividend_amounts)
        self.assertEqual(str(round(test_val, 4)), "12.0233")


    def test_option_price_put_american_discrete_dividends_binomial(self):
        S = 100
        K = 100
        r = 0.10
        sigma = 0.25
        time = 1.0
        steps = 100
        dividend_times = [0.25, 0.75]
        dividend_amounts = [2.5, 2.5]
        test_val = Amop.option_price_put_american_discrete_dividends_binomial(S, K, 
                    r, sigma, time, steps, dividend_times, dividend_amounts)
        self.assertEqual(str(round(test_val, 5)), "8.11801")

    def test_option_price_call_american_proportional_dividends_binomial(self):    
        S = 100
        K = 100
        r = 0.10
        sigma = 0.25
        time = 1.0
        steps = 100
        dividend_times = [0.25, 0.75]
        dividend_yields = [0.025, 0.025]
        test_val = Amop.option_price_call_american_proportional_dividends_binomial(S, 
                K, r, sigma, time, steps, dividend_times, dividend_yields)
        self.assertEqual(str(round(test_val, 4)), "11.8604")

    def test_option_price_put_american_proportional_dividends_binomial(self):    
        S = 100
        K = 100
        r = 0.10
        sigma = 0.25
        time = 1.0
        steps = 100
        dividend_times = [0.25, 0.75]
        dividend_yields = [0.025, 0.025]
        test_val = Amop.option_price_put_american_proportional_dividends_binomial(S, 
                K, r, sigma, time, steps, dividend_times, dividend_yields)
        self.assertEqual(str(round(test_val, 5)), "7.99971")


if __name__ == '__main__':
    unittest.main()
