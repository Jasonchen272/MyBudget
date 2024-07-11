from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import csv
import gspread
from gspread.utils import ExportFormat
import time
import os
from werkzeug.utils import secure_filename
import json



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
                    if "DISCOVER E-PAYMENT" in name or "CAPITAL ONE MOBILE PMT" in name:
                        continue
                    elif "UNIVERSITY OF MI UMNPAY" in name:
                        category = "SALARY"
                    transaction = ([date, amount, name, category])
                    transactions.append(transaction)
            return transactions
    except Exception as e:
        return False


    
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
    except Exception as e:
        return False

    
def capitalOneTransactions(file): #add to transactions with capital one csv 
    transactions = []
    try:
        with open(file, mode = 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)

            for line in csv_reader:
                if line:
                    date = line[0]
                    name = line[3]
                    if "CAPITAL ONE MOBILE PYMT" in name:
                        continue
                    category = line[4]
                    amount = -float(line[5])
                    transaction = ([date, amount, name, category])
                    transactions.append(transaction)
            return transactions
    except Exception as e:
        return False
    
def otherTransactions(file, formatObj):
    transactions = []

    try:
        with open(file, mode = 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            if formatObj['skip']:
                next(csv_reader)
            paymentMessages = formatObj['paymentMessages']

            for line in csv_reader:
                if line:
                    date = line[formatObj['date']]
                    amount = -float(line[formatObj['amount']]) if formatObj['isCredit'] else float(line[formatObj['amount']])
                    name = line[formatObj['description']]
                    if any(message in name for message in paymentMessages):
                        continue
                    category = 'other'
                    transaction = ([date, amount, name, category])
                    transactions.append(transaction)
            return transactions
    except Exception as e:
        return False



sa = gspread.service_account(filename = "avian-sunlight-423320-q2-89a5759c0252.json")  
template = sa.open("Expenses 2") #sheets we will edit
sh = None

app = Flask(__name__)   
CORS(app, resources={r"/files": {"origins": "http://localhost:3000"},
                     r"/uploadSheets": {"origins": "http://localhost:3000"},
                     r"/create_sheet": {"origins": "http://localhost:3000"},
                     r"/export": {"origins": "http://localhost:3000"}})
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename): #only csv files
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


all_files = []

def write_data(formatObj = None):
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
            elif f['bank'] == "other":
                rows = otherTransactions(cur_file, formatObj)


            wks = sh.worksheet(f"{f['month']}")
            for row in rows:
                wks.insert_row([row[0], row[2], row[3], row[1]], 7)
                time.sleep(2)
            wks.update_acell('B2', '=SUMIF(D7:D,">0")')
            wks.update_acell('B3', '=SUMIF(D7:D,"<0")')
            os.remove(cur_file)
        all_files = []
        return True
    except Exception as e:
        os.remove(cur_file)
        return None
    
def del_all_extra(new_id):
    files_list = (sa.list_spreadsheet_files())
    for f in files_list:
        if f['id'] != template.id and f['id'] != new_id:
            print(f['name'])
            sa.del_spreadsheet(f['id'])
    print(template.id)
    
@app.route('/create_sheet', methods=['GET', 'POST'])
def create_sheet():
    global sh
    if request.method == 'POST':
        new_sheet_name = request.form.get('sheetName')
        sh = sa.copy(template.id, title=new_sheet_name)
        sh.share('jchen.012004@gmail.com', perm_type='user', role='writer')
        del_all_extra(sh.id)
        return jsonify({'message': 'Sheet created successfully','sheetName': request.form.get('sheetName')}), 200
    elif(request.method == 'GET'):
        return jsonify([])

@app.route('/files', methods=['POST', 'GET'])
def files():
    if (request.method == 'POST'):
        global all_files
        global sh
        try:
            if 'file' not in request.files:
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
            success = True
            if bank == 'other':
                formatObj = request.form.get('otherFormat')
                success = write_data(json.loads(formatObj))
            else:
                success = write_data()
            if success == False: return jsonify({'error': 'File or Format Error'}), 400

            return jsonify({'message': 'File successfully uploaded', 'fileName': file_name, 'month': month, 'bank': bank}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif(request.method == 'GET'):
        return jsonify(all_files)
    

@app.route('/export', methods=["GET"])
def download_file():
    global sh
    if (request.method == "GET"):
        if sh != None:
            exported = sh.export(format=ExportFormat.EXCEL)
            f = open("MyBudget.xlsx", 'wb')
            f.write(exported)
            f.close()
            sa.del_spreadsheet(sh.id)
            sh = None
            print("success")
            return send_file("MyBudget.xlsx")
    print("error")
    return jsonify({"error": "error"})




if __name__ == '__main__':
    app.run(debug=True)

