from datetime import datetime, timedelta
import os
import csv
from money import Money
import glob
import pandas as pd

os.chdir("files")

date_input = input('Tarixi daxil edin: ')
date_text_invoice = None
date_objs = []
if date_input:
    if '-' in date_input:
        date_from, date_to = tuple(date_input.split('-'))
        date_from, date_to = datetime.strptime(
            date_from.strip(), '%d.%m.%Y'), datetime.strptime(date_to.strip(), '%d.%m.%Y')
        delta = date_to - date_from
        for i in range(delta.days + 1):
            day = date_from + timedelta(days=i)
            date_objs.append(day)
        date_text_invoice = f"""{date_from.strftime('%d.%m.%Y')} - {date_to.strftime('%d.%m.%Y')}"""
    else:
        date_objs = [datetime.strptime(date_input, '%d.%m.%Y')]
        date_text_invoice = date_objs[0].strftime('%d.%m.%Y')


# JOIN ALL CSV FILES
extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])
combined_csv.to_csv("combined_csv.csv", index=False, encoding='utf-8-sig')

drivers = {}


payment_methods = [("Cash", "Nağd"), ("Card Terminal", "Kart Terminal"),
                   ("Bolt Payments", "Bolt Payments"), ("Bolt Business", "Bolt Biznes")]

with open('combined_csv.csv', encoding = 'cp850') as file:
    csv_reader = csv.DictReader(file)
    date_minimum = None
    date_maximum = None
    for row in csv_reader:
        date_order = datetime.strptime(row["Date"].split(' ')[0], '%d.%m.%Y')
        if (not date_order in date_objs) and date_objs:
            continue
        if not date_text_invoice:
            if (not date_minimum) or date_minimum > date_order:
                date_minimum = date_order
            if (not date_maximum) or date_maximum < date_order:
                date_maximum = date_order
        driver = row["Driver"]
        if not drivers.get(row["Driver"], None):
            drivers[driver] = {}
            for met, _ in payment_methods:
                drivers[driver][met] = Money(currency='AZN')
        drivers[driver][row["Payment Method"]
                        ] += Money(row["Price Total"], currency='AZN')
    if not date_text_invoice:
        date_text_invoice = f"""{date_minimum.strftime('%d.%m.%Y')} - {date_maximum.strftime('%d.%m.%Y')}"""

summary_of_all_income = 0

output = \
    f"""\
Hesabat
=======\n\
{date_text_invoice}
"""

for driver, payments in drivers.items():
    driver_text = f"\n{driver}\n"+('-'*len(driver)) + '\n'
    for met_en, met_az in payment_methods:
        driver_text += f"{met_az}: {payments[met_en]}\n"
    summary_money = sum([payments[pay] for pay, _ in payment_methods])
    driver_text += f"Cəmi: {summary_money}\n"
    output += driver_text+'\n'
    summary_of_all_income += summary_money


# Sum
sum_data = {}
for met, _ in payment_methods:
    sum_data[met] = Money(currency='AZN')
for _, payments in drivers.items():
    for met, _ in payment_methods:
        sum_data[met] += payments[met]
output += f"\nÜmumi\n"+'-----'+'\n'
for met_en, met_az in payment_methods:
    output += f"{met_az}: {sum_data[met_en]}\n"
output += f'Cəmi: {summary_of_all_income}'

os.remove('combined_csv.csv')

os.chdir('../')
with open('output.txt', 'w') as f:
    f.write(output)
