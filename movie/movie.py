from flask import Flask, request, jsonify, make_response
import json
import sys
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

PORT = 3200
HOST = '0.0.0.0'

with open('{}/databases/movies.json'.format("."), 'r') as jsf:
    movies = json.load(jsf)["movies"]

client = MongoClient(os.environ["MONGO_URI"])
db = client[os.environ["MONGO_DB"]]
collection = db["movies"]

if collection.count_documents({}) == 0 and movies:
    collection.insert_many(movies)

# returns True if the current user is an admin, False otherwise
def is_admin():
    claims = get_jwt()
    return claims.get("admin", False)   

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# get all movies
@app.route("/json", methods=['GET'])
def get_json():
    movies = list(collection.find({}, {"_id": 0}))
    return make_response(jsonify(movies), 200)

# get movie by id
@app.route("/movies/<movieid>", methods=["GET"])
def get_movie_byid(movieid):
    movie = collection.find_one({"id": movieid}, {"_id": 0})
    if movie is None:
        return make_response(jsonify({"error": "Movie ID not found"}), 404)
    return make_response(jsonify(movie), 200)

# Post a new movie
@app.route("/movies/<movieid>", methods=['POST'])
@jwt_required()
def add_movie(movieid):

    if not is_admin():
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    req = request.get_json()

    if collection.find_one({"id": movieid}):
        return make_response(jsonify({"error": "movie ID already exists"}), 409)

    collection.insert_one(req)

    return make_response(jsonify({"message": "movie added"}), 201)

# Delete a movie
@app.route("/movies/<movieid>", methods=['DELETE'])
@jwt_required()
def del_movie(movieid):

    if not is_admin():
        return make_response(jsonify({"error": "Forbidden"}), 403)

    movie = collection.find_one_and_delete(
        {"id": movieid},
        {"_id": 0}
    )

    if movie is None:
        return make_response(jsonify({"error": "movie ID not found"}), 404)

    return make_response(jsonify(movie), 200)

if __name__ == "__main__":
    #p = sys.argv[1]
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)