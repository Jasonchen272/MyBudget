from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import gspread
import time

transactions = []

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


def write_data(f):
    print("write")
    transactions = []
    cur_file = f['file']
    if f['bank'] == "Wells Fargo":
        rows = wellsFargoTrans(cur_file)
    elif f['bank'] == "Discover":
        rows = discoverTransactions(cur_file)
    elif f['bank'] == "Capital One":
        rows = capitalOneTransactions(cur_file)

    print("after transactions")

    wks = sh.worksheet(f"{f['month']}")
    print("after wks")
    for row in rows:
        print("in loop")
        wks.insert_row([row[0], row[2], row[3], row[1]], 7)
        time.sleep(2)
    print("after writes")
    wks.update_acell('B2', '=SUMIF(D7:D,">0")')
    wks.update_acell('B3', '=SUMIF(D7:D,"<0")')


app = Flask(__name__)
CORS(app, resources={r"/files": {"origins": "http://localhost:3000"}})


@app.route('/members')
def members():
    return {'members': ["Member 1", "Member 2", "Member 3"]}

@app.route('/files', methods=['GET','POST'])
def files():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        file_name = request.form.get('fileName')
        month = request.form.get('month')
        bank = request.form.get('bank')

        print(f"Received file: {file_name}, month: {month}, bank: {bank}")


        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        print("before write")

        print("written")


        return jsonify({'message': 'File successfully uploaded', 'fileName': file_name, 'month': month, 'bank': bank}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)

