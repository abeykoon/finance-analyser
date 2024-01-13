import re
import matplotlib.pyplot as plt
import mplcursors
import matplotlib.dates as mdates
import numpy as np
import datetime as dt
from datetime import datetime, timedelta

#Variables
creditLimit = 1000000
dateRegex = r'on (\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} [APMapm]{2})'
availableBalanceRegex = r'Avl bal (\d[\d,.]*)'
amountRegex = r'LKR\s+([\d,]+(?:\.\d{2})?)'
locationRegex = r'at\s+([A-Z\s]+)'
paymentIdentifier = 'payment'
debitIdentifier = 'debit'


plotData = {}

from enum import Enum
class TxType(Enum):
    PAYMENT = 'Payment'
    DEBIT = 'Debit'

# Using readlines()
file1 = open('/Users/hasithah/private/sms-log-cc/log-13-01-2024.txt', 'r')
Lines = file1.readlines()

count = 0

def find_date(line):
    # Define a regular expression pattern to match the date
    date_pattern = re.compile(dateRegex)

    # Find the date in the line
    match = date_pattern.search(line)

    # Check if a match is found and extract the date
    if match:
        extracted_date = match.group(1)
        #print("Extracted Date:", extracted_date)
        return extracted_date
    else:
        print("Date not found in the line.")
        return None

def find_available_balance(line):
    # Define a regular expression pattern to match the date
    avail_balance_pattern = re.compile(availableBalanceRegex)

    # Find the date in the line
    match = avail_balance_pattern.search(line)

    # Check if a match is found and extract the date
    if match:
        avail_balance = match.group(1)
        avail_balance = float(avail_balance.replace(',', ''))
        #print("Available Balance:", avail_balance)
        return avail_balance
    else:
        print("Available balance not found in the line.")
        return 0

def find_tx_type(line):
    if paymentIdentifier in line:
        return TxType.PAYMENT
    elif debitIdentifier in line:
        return TxType.DEBIT
    else:
        return None

def find_amount(line):
    # Define a regular expression pattern to match the date
    amount_pattern = re.compile(amountRegex)

    # Find the date in the line
    match = amount_pattern.search(line)

    # Check if a match is found and extract the date
    if match:
        amount = match.group(1)
        amount = float(amount.replace(',', ''))
        #print("Amount:", amount)
        return amount
    else:
        #print("Amount not found in the line.")
        return 0

def find_location(line):
    location_pattern = re.compile(locationRegex)

    # Find the location in the line
    match = location_pattern.search(line)

    # Check if a match is found and extract the location
    if match:
        extracted_location = match.group(1).strip()
        extracted_location = extracted_location.rstrip('LK')
        extracted_location = re.sub(r'\s+', ' ', extracted_location)
        #print("Extracted Location:", extracted_location)
        return extracted_location
    else:
        print("NOT FOUND")
        return "NOT LOCATION"

# Strips the newline character
for line in Lines:
    count += 1
    print("Line{}: {}".format(count, line.strip()))
    tx_date = find_date(line)
    if tx_date:
        newdict = {}
        newdict['date'] = find_date(line)
        avail_balance = find_available_balance(line)
        newdict['avail_balance'] = avail_balance
        newdict['total_payable'] = round((creditLimit - avail_balance), 2)
        newdict['amount'] = find_amount(line)
        newdict['location'] = find_location(line)
        newdict['tx_type'] = find_tx_type(line)
        print(newdict)
        print('-----------------------')
        plotData[newdict['date']] = newdict

#---------------------------------------
# Plotting


# Extract keys, values, and details
keys = list(plotData.keys())
# Convert date strings to datetime objects
date_objects = [datetime.strptime(date, '%d/%m/%Y %I:%M:%S %p') for date in keys]
values = [entry['total_payable'] for entry in plotData.values()]
details = list(plotData.values())

#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))


# Create a line chart
plt.plot(date_objects, values, marker='o', linestyle='-', color='b', label='Credit Card Payments')
# Change the color of payment data points
for payindex, payValue in enumerate(details):
    if payValue['tx_type'] == TxType.PAYMENT:
        plt.plot(date_objects[payindex], values[payindex], marker='o', linestyle='-', color='red')

start_date = min(date_objects)
end_date = max(date_objects)

print(start_date)
print(end_date)

# Draw vertical lines at every 6th and 26th day of the month
for day in range(6, 32, 20):  # 6th and 26th day
    date_to_plot = start_date.replace(day=day)
    if date_to_plot <= end_date:
        plt.axvline(x=date_to_plot, color='red', linestyle='--', label=f'Vertical Line at {date_to_plot.strftime("%d/%m/%Y %I:%M:%S %p")}')

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator())
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=3))
plt.gcf().autofmt_xdate()

# Add labels and title
plt.xlabel('Date')
plt.ylabel('Total Payable')
plt.title('Total Payable by Date')

# Add legend
plt.legend()

# Add annotations on mouseover
cursor = mplcursors.cursor(hover=True)
@cursor.connect("add")
def on_add(sel):
    index = sel.target.index
    detail = details[index]
    detailText = f"{detail['date']}\n{detail['tx_type'].value}\n{detail['amount']}\n{detail['location']}\n{detail['total_payable']}"
    sel.annotation.set_text(f"({detailText})")

# Display the plot
plt.show()
