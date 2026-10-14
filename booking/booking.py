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

def fetch_user(userid):
    response = requests.get(
        f"http://user:3203/user/{userid}",
        headers={
            "Authorization": request.headers.get("Authorization", "")
        },
        timeout=5
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()

def fetch_movies():
    movies_response = requests.get("http://movie:3200/json", timeout=5)
    movies_response.raise_for_status()
    movies = movies_response.json()
    return movies

def fetch_schedule():
    schedule_response = requests.get("http://schedule:3202/json", timeout=5)
    schedule_response.raise_for_status()
    schedule = schedule_response.json()
    return schedule

def write(bookings):
    with open('{}/databases/bookings.json'.format("."), 'w') as f:
        full = {}
        full['bookings']=bookings
        json.dump(full, f)

# returns True if the current user is an admin, False otherwise
def is_admin():
    claims = get_jwt()
    return claims.get("admin", False)

# returns True if the current user can access the specified user's data, False otherwise
def can_access_user(userid):
    current_user_id = get_jwt_identity()
    return current_user_id == userid or is_admin()

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings/json", methods=['GET'])
@jwt_required()
def get_bookings():
    if not is_admin():
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    res = make_response(jsonify(bookings), 200)
    return res

# get booking by userid
@app.route("/bookings/<userid>", methods=['GET'])
@jwt_required()
def get_booking_by_id(userid):

    # Check authorization
    if not can_access_user(userid):
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            res = make_response(jsonify(booking),200)
            return res
    return make_response(jsonify({"error":"Booking ID not found"}),404)

# Post a new booking for a user
@app.route("/bookings/<userid>", methods=["POST"])
@jwt_required()
def add_booking(userid):

    if not can_access_user(userid):
        return make_response(jsonify({"error": "Forbidden"}), 403)

    req = request.get_json()
    dates = req["dates"]

    # Check if user already has bookings
    if any(booking["userid"] == userid for booking in bookings):
        return make_response(jsonify({"error": "User already has bookings"}), 409)

    # Check if every movie is scheduled on the requested date
    schedule = fetch_schedule()
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
@jwt_required()
def del_booking(userid):

    if not can_access_user(userid):
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            bookings.remove(booking)
            write(bookings)
            return make_response(jsonify(booking),200)

    res = make_response(jsonify({"error":"booking ID not found"}),404)
    return res

# Additional endpoint number 1/3
# get bookings by user id and return the movies with their details
@app.route("/bookings/<userid>/details", methods=['GET'])
@jwt_required()
def get_schedules_by_userid(userid):

   if not can_access_user(userid):
        return make_response(jsonify({"error": "Forbidden"}), 403) 
             
   for booking in bookings:
      if str(booking["userid"]) == str(userid):
         result = {
            "userid": booking["userid"],
            "dates": []
         }
         movies = fetch_movies()
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
@jwt_required()
def get_booking_with_user(userid):
    
    if not can_access_user(userid):
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    for booking in bookings:
        if booking["userid"] == userid:
            user = fetch_user(userid)
            if user is None:
                return make_response(jsonify({"error": "User not found"}), 404)
            result = {
                "user": user,
                "dates": booking["dates"]
            }
            return make_response(jsonify(result), 200)

    return make_response(jsonify({"error": "Booking not found"}), 404)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
