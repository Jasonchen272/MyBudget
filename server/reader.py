from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import gspread
import time
import os
from werkzeug.utils import secure_filename



UPLOAD_FOLDER = './UploadedFiles/'
ALLOWED_EXTENSIONS = {'csv'}

transactions = []


def wellsFargoTrans(file): #add to transactions with wells fargo csv
    transactions = []
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
                        category = "SALARY"
                    transaction = ([date, amount, name, category])
                    transactions.append(transaction)
            return transactions
    except IOError as e:
        return transactions


    
def discoverTransactions(file): #add to transactions with discover csv
    transactions = []

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
    
def capitalOneTransactions(file): #add to transactions with capital one csv #TODO finish after I get format
    transactions = []

    try:
        with open(file, mode = 'r') as csvfile:
            for line in csvfile:
                date = line[0]
    except IOError as e:
        return transactions



sa = gspread.service_account()  
sh = sa.open("Expenses 2") #sheets we will edit

app = Flask(__name__)   
CORS(app, resources={r"/files": {"origins": "http://localhost:3000"},
                     r"/uploadSheets": {"origins": "http://localhost:3000"}})
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename): #only csv files
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


all_files = []

def write_data():
    global all_files
    try:
        for f in all_files:
            rows = []
            cur_file = f['filename']
            if f['bank'] == "wells_fargo":
                rows = wellsFargoTrans(cur_file)
            elif f['bank'] == "discover":
                rows = discoverTransactions(cur_file)
            elif f['bank'] == "capital_one":
                rows = capitalOneTransactions(cur_file)

            wks = sh.worksheet(f"{f['month']}")
            for row in rows:
                wks.insert_row([row[0], row[2], row[3], row[1]], 7)
                time.sleep(2)
            wks.update_acell('B2', '=SUMIF(D7:D,">0")')
            wks.update_acell('B3', '=SUMIF(D7:D,"<0")')
            os.remove(cur_file)
            del all_files[0]
        all_files = []
        return jsonify({'Success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files', methods=['POST', 'GET'])
def files():
    if (request.method == 'POST'):
        global all_files
        try:
            print(request)
            if 'file' not in request.files:
                print(request.files)
                return jsonify({'error': 'No file part'}), 400

            file = request.files['file']
            file_name = request.form.get('fileName')
            month = request.form.get('month')
            bank = request.form.get('bank')

            print(f"Received file: {file_name}, month: {month}, bank: {bank}")


            if file.filename == '' or not allowed_file(file.filename):
                return jsonify({'error': 'Wrong file type or name'}), 400


            filename = secure_filename(file.filename)
            file.save(app.config['UPLOAD_FOLDER']+ filename)

            all_files.append({'file': file, 'month': month, 'bank': bank, "filename": app.config['UPLOAD_FOLDER']+file_name})
            write_data()

            return jsonify({'message': 'File successfully uploaded', 'fileName': file_name, 'month': month, 'bank': bank}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif(request.method == 'GET'):
        print(request)
        return jsonify({'message': 'GET successfully'})
     





if __name__ == '__main__':
    app.run(debug=True)

