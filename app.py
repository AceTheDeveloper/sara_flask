from flask import Flask, request
from flask_cors import CORS
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import gspread
import random
import json
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# ─── SPREADSHEET ─────────────────────────────────────────────────────────────

def get_spreadsheet():
    creds_dict = json.loads(os.environ.get("GOOGLE_CREDENTIALS"))
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(os.environ.get("SPREADSHEET_ID"))


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def generate_order_id():
    return f"ORD-{random.randint(0, 999999):06d}"

def get_total(order_items):
    if not order_items:
        return {"error": "order_items is required"}, 400
    return sum(float(i['price']) * int(i['quantity']) for i in order_items)

def add_order_items(order_items, order_id):
    sheet = get_spreadsheet().worksheet("Order Items")
    for i in order_items:
        total = int(i['quantity']) * float(i['price'])
        sheet.append_row([order_id, i['name'], i['quantity'], i['price'], total])
        
    return True
        
def update_food_qty(order_items):
    sheet = get_spreadsheet().worksheet("Menu List")
    
    records = sheet.get_all_records()
    
    for i in order_items:
        for index, row in enumerate(records):
            if row['name'] == i['name']:
                row_number = index + 2
                current_qty = int(row['quantity'])
                new_qty = current_qty - int(i['quantity'])
                
                headers = sheet.row_values(1)
                col_number = headers.index('quantity') + 1
                
                sheet.update_cell(row_number, col_number, new_qty)
                
    return True

# ─── ROUTES ──────────────────────────────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "hello"}

@app.get("/get_menu")
def get_menu():
    sheet = get_spreadsheet().worksheet("Menu List")
    return {"menu": sheet.get_all_records()}

@app.post("/add_order")
def add_order():
    data         = request.get_json()
    order_items  = data.get("order_items")
    order_id     = generate_order_id()
    status       = 'pending'

    sheet = get_spreadsheet().worksheet("Orders")
    sheet.append_row([
        order_id,
        data.get("name"),
        data.get("email"),
        data.get("service_type"),
        data.get("address"),
        get_total(order_items),
        status
    ])

    if(add_order_items(order_items, order_id)):
        # update_food_qty(order_items)
        return {"message": "Order added!", "isSuccess" : True, "order_id": order_id, "order": data}
    else:
        return {"error" : "Error on adding foods"}
    
@app.post("/check_order")
def check_order():
    data = request.get_json()
    order_id = f"ORD-{data.get('order_id')}"
    print("===============================================")
    print(f"Order_ID : {order_id}")
    print("===============================================")

    if not order_id:
        return {"message": "order_id is required"}, 400

    orders_sheet = get_spreadsheet().worksheet("Orders")
    order = next((row for row in orders_sheet.get_all_records() if row["order_id"] == order_id), None)

    if not order:
        return {"message": "Order not found"}, 404

    items_sheet = get_spreadsheet().worksheet("Order Items")
    items = [row for row in items_sheet.get_all_records() if row["order_id"] == order_id]

    return {"order": order, "items": items}


if __name__ == "__main__":
    # if os.environ.get("NODE_TYPE") == 'DEVELOPMENT':
    #     app.run(debug=True)
    # else:
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))