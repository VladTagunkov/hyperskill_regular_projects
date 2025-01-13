# Write your code here
# Write your code here
prices=["Bubblegum: $202","Toffee: $118","Ice cream: $2250","Milk chocolate: $1680",
        "Doughnut: $1075","Pancake: $80"]
total_income=0
print("Earned amount:")
for elem in prices:
    inc=int(elem.split()[-1][1:])
    total_income += inc
    print(elem)

print('\n'f"Income: {total_income}")

print("Staff expenses:")
st_exp=int(input())
print("Other expenses:")
ot_exp=int(input())

total_income=total_income-st_exp-ot_exp

print(f'Net income: {total_income}')