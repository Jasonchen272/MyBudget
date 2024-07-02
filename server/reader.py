import csv
import gspread
import time

sources = ['wells_fargo', 'discover', 'capital_one']
months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
transactions =[]

def wellsFargoTrans(file):
    try:
        with open(file, mode = 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            for line in csv_reader:
                if line:
                    date = line[0]
                    amount = float(line[1])
                    name = line[4]
                    category = "other"
                    if "DISCOVER E-PAYMENT" in name:
                        continue
                    elif "UNIVERSITY OF MI UMNPAY" in name:
                        category = "TA payment"
                    transaction = ([date, amount, name, category])
                    transactions.append(transaction)
            return transactions
    except IOError as e:
        return transactions


    
def discoverTransactions(file):
    try:
        with open(file, mode = 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)
            for line in csv_reader:
                if line:
                    date = line[0]
                    amount = -float(line[3])
                    name = line[2]
                    if "INTERNET PAYMENT" in name:
                        continue
                    category = line[4]
                    transaction = ([date, amount, name, category])
                    transactions.append(transaction)
            return transactions
    except IOError as e:
        return transactions
    
def capitalOneTransactions(file):
    try:
        with open(file, mode = 'r') as csvfile:
            for line in csvfile:
                date = line[0]
    except IOError as e:
        return transactions



sa = gspread.service_account()
sh = sa.open("Expenses 2")


for month in months:
    transactions = []
    file = f"wells_fargo_{month}.csv"
    rows = wellsFargoTrans(file)
    file = f"discover_{month}.csv"
    discoverTransactions(file)

    wks = sh.worksheet(f"{month}")
    for row in rows:
        wks.insert_row([row[0], row[2], row[3], row[1]], 7)
        time.sleep(2)
    wks.update_acell('B2', '=SUMIF(D7:D,">0")')
    wks.update_acell('B3', '=SUMIF(D7:D,"<0")')