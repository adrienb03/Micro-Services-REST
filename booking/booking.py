from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt

app = Flask(__name__)

# JWT configuration
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False

jwt = JWTManager(app)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

with open('{}./user/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

with open('{}./movie/databases/movies.json'.format("."), "r") as jsf:
   movies = json.load(jsf)["movies"]

with open('{}./schedule/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]

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

# get booking by userid
@app.route("/bookings/<userid>", methods=['GET'])
@jwt_required()
def get_booking_by_id(userid):
    current_user_id = get_jwt_identity()
    is_admin = get_jwt().get("admin", False)

    # Check authorization
    if current_user_id != userid and not is_admin:
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            res = make_response(jsonify(booking),200)
            return res
    return make_response(jsonify({"error":"Booking ID not found"}),404)

# Post a new booking for a user
@app.route("/bookings/<userid>", methods=["POST"])
def add_booking(userid):
    req = request.get_json()
    dates = req["dates"]

    # Check if user exists
    if not any(user["id"] == userid for user in users):
        return make_response(jsonify({"error": "User not found"}), 404)

    # Check if user already has bookings
    if any(booking["userid"] == userid for booking in bookings):
        return make_response(jsonify({"error": "User already has bookings"}), 409)

    # Check if every movie is scheduled on the requested date
    for entry in dates:
        date = entry["date"]
        for movie_id in entry["movies"]:
            if not any(
                item["date"] == date and movie_id in item["movies"]
                for item in schedule
            ):
                return make_response(
                    jsonify({"error": f"Movie {movie_id} is not scheduled on {date}"}),
                    400
                )

    bookings.append({
        "userid": userid,
        "dates": dates
    })
    write(bookings)

    return make_response(jsonify({"message": "Booking created"}), 201)

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

# Additional endpoint number 1/3
# get bookings by user id and return the movies with their details
@app.route("/bookings/<userid>/details", methods=['GET'])
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

# Additional endpoint number 2/3
# Get booking with user details
@app.route("/bookings/<userid>/userdetail", methods=["GET"])
def get_booking_with_user(userid):
    for booking in bookings:
        if booking["userid"] == userid:
            for user in users:
                if user["id"] == userid:
                    result = {
                        "user": user,
                        "dates": booking["dates"]
                    }
                    return make_response(jsonify(result), 200)

    return make_response(jsonify({"error": "Booking not found"}), 404)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
