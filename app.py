from flask import Flask
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # ← This is the key fix

@app.route("/")
def home():
    return {"message": "hello"}

@app.get('/get_menu')
def get_menu():
    return {
        "menu": "Menu"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))