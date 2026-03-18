from flask import Flask, request
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
CORS(app)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "13emxywRjUsScWX8O3xBo2y8QOgiRpvxrBj2zqbjkCn4"

def get_spreadsheet():
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)

@app.route("/")
def home():
    return {"message": "hello"}

@app.get('/get_menu')
def get_menu():
    sheet = get_spreadsheet().worksheet("Menu")
    return {"menu": sheet.get_all_records()}

@app.post('/add_order')
def add_order():
    data = request.get_json()

    order_id     = data.get("order_id")
    name         = data.get("name")
    email        = data.get("email")
    service_type = data.get("service_type")
    address      = data.get("address")
    total        = data.get("total")

    sheet = get_spreadsheet().worksheet("Orders")
    sheet.append_row([order_id, name, email, service_type, address, total])

    return {"message": "Order added!", "order": data}

if __name__ == "__main__":
    app.run(debug=True)