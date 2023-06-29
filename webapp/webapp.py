import json
from flask import Flask
from flask import jsonify
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/zipcode/<zip_code>")
def hello_world_zipcode(zip_code):
    # zip_code =
    print("Looking up infor for Zip Code: " + zip_code)
    return_string = {
        "zip_code": 501,
        "latitude": 40.922326,
        "longitude": -72.637078,
        "city": "Holtsville",
        "state": "NY",
        "county": "Suffolk"
    }
    return jsonify(return_string)
    # return "<p>Hello, World!" + zip_code + "</p>"
