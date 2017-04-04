#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import argparse
import decimal

MONTHS_IN_YEAR = 12
DOLLAR_QUANTIZE = decimal.Decimal('.01')

class MissingValue(Exception):
    def __init__(self,val):
        self._val=val
    def __str__(self):
        return str(self._val)

def dollar(f, round=decimal.ROUND_CEILING):
    """
    This function rounds the passed float to 2 decimal places.
    """
    if not isinstance(f, decimal.Decimal):
        f = decimal.Decimal(str(f))
    return f.quantize(DOLLAR_QUANTIZE, rounding=round)

class Mortgage:
    # def __init__(self, interest, months, amount):
    def __init__(self, interest, months, 
                  house_price=None, downpayment=None,
                  amount=None,
                 ):
        self._interest = float(interest)
        self._months = int(months)
        if house_price and downpayment:
            self._amount = dollar(house_price)-dollar(downpayment)
            self._house_price=dollar(house_price)
        elif amount and house_price:
            self._amount = dollar(amount)
            self._house_price=dollar(house_price)
        else:
            raise MissingValue("need to specify house price and either load amount or downpayment")
        # self._property_tax=property_tax
        # self._investments=investments
        # self._insurance_annual=annual_insurance

    @property
    def house_price(self):
        return self._house_price

    @property
    def rate(self):
        return self._interest

    @property
    def month_growth(self):
        return 1. + self._interest / MONTHS_IN_YEAR

    @property
    def apy(self):
        return self.month_growth ** MONTHS_IN_YEAR - 1

    @property
    def loan_years(self):
        return float(self._months) / MONTHS_IN_YEAR

    @property
    def loan_months(self):
        return self._months

    @property
    def amount(self):
        return self._amount

    @property
    def monthly_payment(self):
        pre_amt = float(self.amount) * self.rate / (float(MONTHS_IN_YEAR) * (1.-(1./self.month_growth) ** self.loan_months))
        return dollar(pre_amt, round=decimal.ROUND_CEILING)

    def total_value(self, m_payment):
        return m_payment / self.rate * (float(MONTHS_IN_YEAR) * (1.-(1./self.month_growth) ** self.loan_months))

    @property
    def annual_payment(self):
        return self.monthly_payment * MONTHS_IN_YEAR

    @property
    def total_payout(self):
        return self.monthly_payment * self.loan_months

    def monthly_prepayment(self,month):
        return 0

    def monthly_payment_schedule(self):
        monthly = self.monthly_payment
        balance = dollar(self.amount)
        rate = decimal.Decimal(str(self.rate)).quantize(decimal.Decimal('.000001'))
        # while True:
        for month in range(1,self._months):
            interest_unrounded = balance * rate * decimal.Decimal(1)/MONTHS_IN_YEAR
            interest = dollar(interest_unrounded, round=decimal.ROUND_HALF_UP)
            pmt=monthly+self.monthly_prepayment(month)
            if pmt >= balance + interest:
                yield balance, interest
                break
            principal = pmt - interest
            yield principal, interest
            balance -= principal

def print_summary(m):
    print('{0:>25s}:  {1:>12.6f}'.format('Rate', m.rate))
    print('{0:>25s}:  {1:>12.6f}'.format('Month Growth', m.month_growth))
    print('{0:>25s}:  {1:>12.6f}'.format('APY', m.apy))
    print('{0:>25s}:  {1:>12.0f}'.format('Payoff Years', m.loan_years))
    print('{0:>25s}:  {1:>12.0f}'.format('Payoff Months', m.loan_months))
    print('{0:>25s}:  {1:>12.2f}'.format('Amount', m.amount))
    print('{0:>25s}:  {1:>12.2f}'.format('Monthly Payment', m.monthly_payment))
    print('{0:>25s}:  {1:>12.2f}'.format('Annual Payment', m.annual_payment))
    print('{0:>25s}:  {1:>12.2f}'.format('Mortgage Payout', m.total_payout))

def main():
    parser = argparse.ArgumentParser(description='Mortgage Amortization Tools')
    parser.add_argument('-i', '--interest', default=6, dest='interest')
    parser.add_argument('-y', '--loan-years', default=30, dest='years')
    parser.add_argument('-m', '--loan-months', default=None, dest='months')
    parser.add_argument('-a', '--amount', default=100000, dest='amount')
    args = parser.parse_args()

    if args.months:
        m = Mortgage(float(args.interest) / 100, float(args.months), args.amount)
    else:
        m = Mortgage(float(args.interest) / 100, float(args.years) * MONTHS_IN_YEAR, args.amount)

    print_summary(m)

if __name__ == '__main__':
    main()
