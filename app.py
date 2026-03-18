from flask import Flask
from flask_cors import CORS
import os


menu = [
    {"name" : "Cheese Burger", "price" : "$24.5"},
    {"name" : "Shawarma Fries", "price" : "$28.5"},
    {"name" : "Tacos", "price" : "$23.5"}
    
]

app = Flask(__name__)
CORS(app)  # ← This is the key fix

@app.route("/")
def home():
    return {"message": "hello"}

@app.get('/get_menu')
def get_menu():
    return {
        "menu": menu
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))