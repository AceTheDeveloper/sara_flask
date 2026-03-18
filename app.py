from flask import Flask, request
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
import os
import json
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
CORS(app)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_spreadsheet():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")  # reads from env
    creds_dict = json.loads(creds_json)
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(os.environ.get("SPREADSHEET_ID"))


def add_order_items(arr, order_id):
    sheet = get_spreadsheet().worksheet("Order Items")
    for i in arr:
        total = int(i['quantity']) * float(i['price'])
        sheet.append_row([order_id, i['name'], i['quantity'], i['price'], total]) 
        
def get_total(arr):
    total = 0
    
    for i in arr:
        total += (float(i['price']) * int(i['quantity']))
    return total

@app.route("/")
def home():
    return {"message": "hello"}

@app.get('/get_menu')
def get_menu():
    sheet = get_spreadsheet().worksheet("Menu List")
    return {"menu": sheet.get_all_records()}

@app.post('/add_order')
def add_order():
    data = request.get_json()

    order_id     = data.get("order_id")
    name         = data.get("name")
    email        = data.get("email")
    service_type = data.get("service_type")
    address      = data.get("address")
    orders       = data.get('order_items')
    total        = get_total(orders)

    sheet = get_spreadsheet().worksheet("Orders")
    sheet.append_row([order_id, name, email, service_type, address, total])
    
    add_order_items(orders, order_id)

    return {"message": "Order added!", "order": data}



@app.get('/get_sheets')
def get_sheets():
    spreadsheet = get_spreadsheet()
    sheets = [sheet.title for sheet in spreadsheet.worksheets()]
    return {"sheets": sheets}

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))