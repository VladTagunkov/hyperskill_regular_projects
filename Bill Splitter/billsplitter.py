# write your code here
from random import random
from random import randint

def lucky_random(gn_,df_):
    lucky_num = randint(0, gn_ - 1)
    user_list = list(df_.keys())
    return user_list[lucky_num]

def splitter(bill_amount_, gn_):
    return round((bill_amount_ / gn_),2)

def dict_maker(df_,amount_):
    for key in df_:
        df_[key] = amount_
    return df_

gn = int(input("Enter the number of friends joining (including you): "))
if gn < 1:
    print("No one is joining for the party")
else:
    df = {}
    print("Enter the name of every friend (including you), each on a new line:")
    for _ in range(gn):
        g = input()
        df[g] = 0


    bill_amount = int(input("Enter the total bill value: "))
    split_amount = splitter(bill_amount, gn)
    df = dict_maker(df, split_amount)

    lucky = input('Do you want to use the "Who is lucky?" feature? Write Yes/No:')
    if lucky == 'Yes':
        lucky_person = lucky_random(gn,df)
        print(f"{lucky_person} is the lucky one!")
        new_split_amount = splitter(bill_amount, gn-1)
        df = dict_maker(df, new_split_amount)
        df[lucky_person] = 0
        print(df)
    else:
        print("No one is going to be lucky")
        print(df)
