from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

with open('{}./movie/databases/movies.json'.format("."), "r") as jsf:
   movies = json.load(jsf)["movies"]
   print(movies)

with open('{}./schedule/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]
   print(schedule)

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

# get booking by id
@app.route("/bookings/<userid>", methods=['GET'])
def get_booking_by_id(userid):
    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            res = make_response(jsonify(booking),200)
            return res
    return make_response(jsonify({"error":"Booking ID not found"}),500)

# get schedules with movies from booking by user_id
@app.route("/bookings/<userid>/schedules", methods=['GET'])
def get_schedules_by_userid(userid):
   for booking in bookings:
      if str(booking["userid"]) == str(userid):
         result = {
            "userid": booking["userid"],
            "dates": []
         }
         for booking_date in booking["dates"]:
            date_result = {
               "date": booking_date["date"],
               "movies": []
            }
            for movie_id in booking_date["movies"]:
               for movie in movies:
                  if str(movie["id"]) == str(movie_id):
                        date_result["movies"].append(movie)
                        break
            result["dates"].append(date_result)
         return make_response(jsonify(result), 200)

   return make_response(jsonify({"error": "User booking not found"}), 404)

# Post a new booking
@app.route("/bookings/<userid>", methods=['POST'])
def add_booking(userid):
    req = request.get_json()

    dates = req.get("dates")
    for booking_schedule in dates:
      date = booking_schedule.get("date")
      movies = booking_schedule.get("movies")
      for movie_id in movies:
         for scheduleItem in schedule:
            if str(movie_id) in str(scheduleItem["movies"]) and str(scheduleItem["date"]) == str(date):
               break
         else:
            return make_response(jsonify({"error":"la date réservée pour le film n'est pas correcte"}),500)

    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            return make_response(jsonify({"error":"user ID already exists"}),500)

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
