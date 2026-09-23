from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

def write(bookings):
    with open('{}/databases/bookings.json'.format("."), 'w') as f:
        full = {}
        full['bookings']=bookings
        json.dump(full, f)

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(bookings), 200)
    return res

# Post a new booking
@app.route("/bookings/<userid>", methods=['POST'])
def add_booking(userid):
    req = request.get_json()

    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            return make_response(jsonify({"error":"booking ID already exists"}),500)

    bookings.append(req)
    write(bookings)
    res = make_response(jsonify({"message":"booking added"}),200)
    return res

# Delete a booking
@app.route("/bookings/<userid>", methods=['DELETE'])
def del_booking(userid):
    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            bookings.remove(booking)
            write(bookings)
            return make_response(jsonify(booking),200)

    res = make_response(jsonify({"error":"booking ID not found"}),500)
    return res

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
