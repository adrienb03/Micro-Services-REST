from flask import Flask, request, jsonify, make_response
import json
import sys
from werkzeug.exceptions import NotFound
from flask_jwt_extended import JWTManager, jwt_required, get_jwt

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

def write(movies):
    with open('{}/databases/movies.json'.format("."), 'w') as f:
        full = {}
        full['movies']=movies
        json.dump(full, f)

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
    res = make_response(jsonify(movies), 200)
    return res

# get movie by id
@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_byid(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            res = make_response(jsonify(movie),200)
            return res
    return make_response(jsonify({"error":"Movie ID not found"}),404)

# Post a new movie
@app.route("/movies/<movieid>", methods=['POST'])
@jwt_required()
def add_movie(movieid):

    if not is_admin():
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    req = request.get_json()

    for movie in movies:
        if str(movie["id"]) == str(movieid):
            print(movie["id"])
            print(movieid)
            return make_response(jsonify({"error":"movie ID already exists"}),409)

    movies.append(req)
    write(movies)
    res = make_response(jsonify({"message":"movie added"}),201)
    return res

# Delete a movie
@app.route("/movies/<movieid>", methods=['DELETE'])
@jwt_required()
def del_movie(movieid):

    if not is_admin():
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movies.remove(movie)
            write(movies)
            return make_response(jsonify(movie),200)

    res = make_response(jsonify({"error":"movie ID not found"}),404)
    return res

if __name__ == "__main__":
    #p = sys.argv[1]
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)