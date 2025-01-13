# write your code here
import argparse
import math
import sys


parser = argparse.ArgumentParser()
parser.add_argument('--payment')
parser.add_argument('--principal')
parser.add_argument('--periods')
parser.add_argument('--interest')
parser.add_argument('--type')

args = parser.parse_args()

loan_prin = args.principal
payment = args.payment
periods = args.periods
interest = args.interest
type_ = args.type

# Check negative values in args.
params_list = [loan_prin, payment, periods, interest]
def neg_val_checker(val):
    if val is not None:
        if float(val) < 0:
            return False
        else:
            return True
    else:
        return True

def neg_checker(params_list_):
    neg_list = [neg_val_checker(elem) for elem in params_list_]
    if False in neg_list:
        return True
    else:
        return False

loan_prin = int(loan_prin) if loan_prin is not None else None
periods = int(periods) if periods is not None else None
payment = int(payment) if payment is not None else None

#calculations block
def period_calc(payment_,nom_int_, loan_prin_):
    return math.log(payment_ / (payment_ - nom_int_ * loan_prin_), 1 + nom_int_)

def payment_calc(periods_,nom_int_, loan_prin_):
    return loan_prin_ * (nom_int_*(1+nom_int_)**periods_)/((1+nom_int_)**periods_-1)

def loan_principal_calc(payment_,nom_int_, periods_):
    return float(payment_) / ((nom_int_ * (1 + nom_int_) ** periods_) / ((1 + nom_int_) ** periods_ - 1))

def diff_payment_calc(month_,nom_int_, loan_prin_, periods_):
    part = nom_int_*(loan_prin_-(loan_prin_*(month_-1))/(periods_))
    D = (loan_prin_/periods_+part)
    return part, D

#calculate nominal rates.
def nom_rate_calc(interest_):
    return float(interest_)/(12 * 100)

# here we check task conditions.
if (((type_ is None)
    or (type == 'annuity' and interest is None))
    or (interest is None) or len(vars(args)) < 5)\
    or (neg_checker(params_list)):
    print("Incorrect parameters")

elif type_ == 'annuity':
    nom_int = nom_rate_calc(interest)
    if periods is None:
        n_mon = period_calc(payment,nom_int, loan_prin)
        if math.ceil(n_mon)%12 == 0:
            years = math.ceil(n_mon)/12
            cum_sum = math.ceil(n_mon) * payment
            print(f"It will take {int(years)} years repay this loan!")
            print(f"Overpayment = {cum_sum - loan_prin}")
        else:
            years = math.ceil(n_mon)/12
            mon = math.ceil(n_mon - 12 * years)
            print(f"It will take {int(years)} years and {mon} months to repay this loan!")
    elif payment is None:
        payment = payment_calc(periods,nom_int, loan_prin)
        print(f"Your monthly payment = {math.ceil(payment)}!")
    elif loan_prin is None:
        loan_prin = loan_principal_calc(payment,nom_int, periods)
        print(f"Your loan principal = {int(loan_prin)}!")
elif type_ == 'diff':
    nom_int = nom_rate_calc(interest)
    cum_sum = 0
    for month in range(1,periods+1):
        part, D = diff_payment_calc(month,nom_int, loan_prin, periods)
        cum_sum += math.ceil(D)
        print(f"Month {month+1}: payment is {math.ceil(D)}!")
    print(f"Overpayment = {cum_sum - loan_prin}")