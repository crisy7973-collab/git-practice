# -*- coding: utf-8 -*-
name = "Zhang Wei"
department = "Sales Department"
target = 500000
sales = 586432.75
cost = 398765.4
bonus_rate = 0.035

completion_rate = sales / target
profit = sales - cost
profit_rate = profit / sales
bonus = profit * bonus_rate

print("{:^60}".format("MONTHLY SALES REPORT"))
print("{:<20}{:>40}".format("Name:", name))
print("{:<20}{:>40}".format("Department:", department))
print("{:<20}{:>40}".format("Target:", "¥{:,.2f}".format(target)))
print("{:<20}{:>40}".format("Sales:", "¥{:,.2f}".format(sales)))
print("{:<20}{:>40}".format("Cost:", "¥{:,.2f}".format(cost)))
print("{:<20}{:>40}".format("Completion Rate:", "{:.2%}".format(completion_rate)))
print("{:<20}{:>40}".format("Profit:", "¥{:,.2f}".format(profit)))
print("{:<20}{:>40}".format("Profit Rate:", "{:.2%}".format(profit_rate)))
print("{:<20}{:>40}".format("Bonus Rate:", "{:.2%}".format(bonus_rate)))
print("{:<20}{:>40}".format("Bonus:", "¥{:,.2f}".format(bonus)))

if completion_rate >= 1.1:
    grade = "EXCELLENT"
elif completion_rate >= 1.0:
    grade = "GOOD"
elif completion_rate >= 0.8:
    grade = "PASS"
else:
    grade = "FAIL"

print("{:^60}".format("Performance: {}".format(grade)))
