from mortgage import Mortgage

class RapidPayMortgage(Mortgage):
  """Mortgage with Rapid pre-payment option
  supplied prepayment_table needs to reflect prepayment
  for each month of the mortgage"""
  def __init__(self, interest, months, 
                  house_price=None, downpayment=None,
                  amount=None,
                  prepayment_table=None
                 ):
      Mortgage.__init__(self,interest,months,
                  house_price=house_price, downpayment=downpayment,
                  amount=amount
                 )
      self.prepayment_table=prepayment_table


  def monthly_prepayment(self,month):
      return self.prepayment_table[month-1]

class MortgageGenerator:
    def __init__(self, interest, months, mortgage_class, **kwargs):
        self._interest=interest
        self._months=months
        self._kwargs=kwargs
        self._mortgage_class=mortgage_class

    def get_mortgage(self, house_price=None, downpayment=None, amount=None):
        return self._mortgage_class(self._interest,
                                    self._months,
                                    house_price,
                                    downpayment,
                                    amount,**self.kwargs)

class ROI:
    """Mortgage Return on investment calculator. Includes
    rough calculations of tax returns combined with all 
    house associated payments and refunds"""
    def __init__(self,
                 mortgage,
                 target_sell_price=None,
                 appreciation=1,
                 baseline_return=None,
                 investments=0,
                 property_tax=0,
                 property_insurance=0,
                 tax_rate=0.4
                ):
        self._mortgage=mortgage
        if target_sell_price is None:
            self._target_sell_price=self.mortgage.house_price
        else: self._target_sell_price=target_sell_price
        self._appreciation=appreciation
        if baseline_return is None:
            # at the minimum we want our downpayment back
            self._baseline_return=self.mortgage.house_price-self.mortgage.amount
        else:
            self._baseline_return=baseline_return
        self._investments=investments
        self._property_insurance=property_insurance
        self._property_tax=property_tax
        self._tax_rate=tax_rate

    @property
    def mortgage(self):
        return self._mortgage

    @property
    def target_sell_price(self):
        return self._target_sell_price

    @property
    def appreciation(self):
        return self._appreciation

    @property
    def baseline_return(self):
        return self._baseline_return

    @property
    def investments(self):
        return self._investments

    @property
    def property_tax(self):
        return self._property_tax

    @property
    def property_insurance(self):
        return self._property_insurance

    @property
    def tax_rate(self):
        return self._tax_rate

    def monthly_table(self):
        house_tax_monthly=float(self.mortgage.house_price)*self.property_tax/12
        insurance_monthly=self.property_insurance/12
        write_off_gain=0
        principal_remaining=float(self.mortgage.amount)

        principal_paid=float(0)
        interest_paid=float(0)
        insurance_paid=float(0)
        mortgage_paid=float(0)
        # house_tax_paid=float(0)
        target_net_worth=self.baseline_return+self.investments

        year=0
        month=0

        for index, payment in enumerate(self.mortgage.monthly_payment_schedule()):
          principal, interest = payment
          month=(index%12)+1
          year=(index/12)
          mortgage_paid+=float(principal)+float(interest)
          principal_remaining-=float(principal)
          principal_paid+=float(principal)
          interest_paid+=float(interest)

          month_appreciation_delta=month*float(self.mortgage.house_price)*(self.appreciation**(year-1))*(self.appreciation - 1)/12

          monthly_writeoff_gain=(float(interest)+float(house_tax_monthly))*self.tax_rate

          # house_tax_paid+=house_tax_monthly
          insurance_paid+=insurance_monthly
          write_off_gain+=monthly_writeoff_gain
          
          # net_worth_gain=self.target_sell_price*0.93-principal_remaining-target_net_worth-house_tax_paid-insurance_paid+write_off_gain
          net_worth_gain=self.target_sell_price*0.93-principal_remaining-target_net_worth+write_off_gain

          appreciated_price=float(self.mortgage.house_price)*(self.appreciation**(year))+month_appreciation_delta
          # appreciated_net_worth_gain=appreciated_price*0.93-principal_remaining-target_net_worth-house_tax_paid-insurance_paid+write_off_gain
          appreciated_net_worth_gain=appreciated_price*0.93-principal_remaining-target_net_worth+write_off_gain
          
          monthly_expence_avg=(net_worth_gain)/(index+1)

          # all_paid_monthly (mortgage+tax+insurance)
          # principal_remaining
          # sale_gain (surplus_money-insurance_paid-house_tax_paid)
          # net_worth_gain (surplus_money)
          # appreciated_net_worth_gain (surplus_money+potential_price_gain)
          row=(year, month, 
                  principal,
                  interest,
                  appreciated_price,
                  house_tax_monthly,
                  insurance_monthly,
                  monthly_writeoff_gain,
                  net_worth_gain,
                  appreciated_net_worth_gain,
               )

          yield row
          

