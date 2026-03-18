from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return {"message" : "hello"}

@app.get('/get_menu')
def get_menu():
    return {
        "menu" : "Menu"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))