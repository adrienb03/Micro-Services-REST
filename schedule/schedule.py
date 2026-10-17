from flask import Flask, render_template, request, jsonify, make_response
import json
import requests
from werkzeug.exceptions import NotFound
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
from pymongo import MongoClient
from bson.json_util import dumps
import os

app = Flask(__name__)

# JWT configuration
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False

jwt = JWTManager(app)

PORT = 3202
HOST = '0.0.0.0'

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]

client = MongoClient(os.environ["MONGO_URI"])
db = client[os.environ["MONGO_DB"]]
collection = db["schedule"]

if collection.count_documents({}) == 0 and schedule:
    collection.insert_many(schedule)

def fetch_movies():
    movies_response = requests.get("http://movie:3200/json", timeout=5)
    movies_response.raise_for_status()
    movies = movies_response.json()
    return movies

# returns True if the current user is an admin, False otherwise
def is_admin():
    claims = get_jwt()
    return claims.get("admin", False)

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

# Route 1 (GET) : Tout le planning (/json)
@app.route("/json", methods=["GET"])
def planning():
    schedules = list(collection.find({}, {"_id": 0}))
    return make_response(jsonify(schedules), 200)

# Route 2 (GET) : Le schedule associé à une date (/schedule/<date>)
# Test : GET http://localhost:3202/schedule/20151201
@app.route("/schedule/<date>", methods=['GET'])
def film_selon_date(date):
    s = collection.find_one({"date": date}, {"_id": 0})
    if s is None:
        return make_response(jsonify({"error": "Aucune programmation à cette date"}), 404)
    return make_response(jsonify(s), 200)

# Route 3 (GET) : Dates où passent le film (/moviedates/<movieid>)
# Test : GET http://localhost:3202/moviedates/a8034f44-aee4-44cf-b32c-74cf452aaaae
@app.route("/moviedates/<movieid>", methods=['GET'])
def date_selon_film(movieid):
    schedules = collection.find(
        {"movies": movieid},
        {"_id": 0, "date": 1}
    )
    dates = [s["date"] for s in schedules]
    if not dates:
        return make_response(jsonify({"error": "Ce film ne passe à aucune date"}), 404)
    return make_response(jsonify(dates), 200)


# Route 4 (POST) : Ajouter une date et ses films (/schedule/<date>)
# Test url : http://localhost:3202/schedule/20151230
# Test body : {"date": "20151230", "movies": ["720d006c-3a57-4b6a-b18f-9b713b073f3c"]}
# Nettoyage :git restore databases/times.json
@app.route("/schedule/<date>", methods=['POST'])
@jwt_required()
def ajout_date(date):
    
    if not is_admin():
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    req = request.get_json()

    if collection.find_one({"date": date}):
        return make_response(jsonify({"error": "cette date existe déjà"}), 409)

    movies = fetch_movies()
    # Check if all movie IDs exist in movies.json
    for movie_id in req["movies"]:
        if not any(movie["id"] == movie_id for movie in movies):
            return make_response(
                jsonify({"error": f"Movie {movie_id} not found"}),
                400
            )
    collection.insert_one(req)

    return make_response(jsonify({"message": "date ajoutée"}), 201)



# Route 5 (DELETE) : Supprimer une date (/schedule/<date>)
# Test : DELETE http://localhost:3202/schedule/20151231
@app.route("/schedule/<date>", methods=['DELETE'])
@jwt_required()
def suppression_date(date):

    if not is_admin():
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    result = collection.delete_one({"date": date})

    if result.deleted_count == 0:
        return make_response(jsonify({"error": "cette date n'existe pas"}), 404)

    return make_response(jsonify({"message": "date supprimée"}), 200)


# Additional endpoint number 3/3
# Get scheduled movies for a date with their details
@app.route("/schedule/<date>/details", methods=["GET"])
def get_schedule_details(date):

    s = collection.find_one({"date": date}, {"_id": 0})
    if s is None:
        return make_response(jsonify({"error": "Schedule not found"}), 404)

    result = {
        "date": s["date"],
        "movies": []
    }

    movies = fetch_movies()
    for movie_id in s["movies"]:
        for movie in movies:
            if movie["id"] == movie_id:
                result["movies"].append(movie)
                break

    return make_response(jsonify(result), 200)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
