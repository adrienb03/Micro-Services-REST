from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound
from flask_jwt_extended import JWTManager, jwt_required, get_jwt

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

with open('{}./movie/databases/movies.json'.format("."), "r") as jsf:
   movies = json.load(jsf)["movies"]

def write(schedule):
    with open('{}/databases/times.json'.format("."), 'w') as f:
        full = {}
        full['schedule'] = schedule
        json.dump(full, f)

# returns True if the current user is an admin, False otherwise
def is_admin():
    claims = get_jwt()
    return claims.get("admin", False)

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

# Route 1 (GET) : Tout le planning (/json)
@app.route("/json", methods=['GET'])
def planning():
   res = make_response(jsonify(schedule), 200)
   return res

# Route 2 (GET) : Le schedule associé à une date (/schedule/<date>)
# Test : GET http://localhost:3202/schedule/20151201
@app.route("/schedule/<date>", methods=['GET'])
def film_selon_date(date):
    for s in schedule:
        if str(s["date"]) == str(date):
            return make_response(jsonify(s), 200)
    return make_response(jsonify({"error": "Aucune programmation à cette date"}), 404)

# Route 3 (GET) : Dates où passent passe le film (/moviedates/<movieid>)
# Test : GET http://localhost:3202/moviedates/a8034f44-aee4-44cf-b32c-74cf452aaaae
@app.route("/moviedates/<movieid>", methods=['GET'])
def date_selon_film(movieid):
    dates = []
    for s in schedule:
        if movieid in s["movies"]:
            dates.append(s["date"])
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

    for s in schedule:
        if str(s["date"]) == str(date):
            return make_response(jsonify({"error": "cette date existe déjà"}), 409)

    # Check if all movie IDs exist in movies.json
    for movie_id in req["movies"]:
        if not any(movie["id"] == movie_id for movie in movies):
            return make_response(
                jsonify({"error": f"Movie {movie_id} not found"}),
                400
            )

    schedule.append(req)
    write(schedule)
    return make_response(jsonify({"message": "date ajoutée"}), 201)



# Route 5 (DELETE) : Supprimer une date (/schedule/<date>)
# Test : DELETE http://localhost:3202/schedule/20151231
@app.route("/schedule/<date>", methods=['DELETE'])
@jwt_required()
def suppression_date(date):

    if not is_admin():
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    for s in schedule:
        if str(s["date"]) == str(date):
            schedule.remove(s)
            write(schedule)
            return make_response(jsonify({"message": "date supprimée"}), 200)
    return make_response(jsonify({"error": "cette date n'existe pas"}), 404)


# Additional endpoint number 3/3
# Get scheduled movies for a date with their details
@app.route("/schedule/<date>/details", methods=["GET"])
def get_schedule_details(date):
    for s in schedule:
        if s["date"] == date:
            result = {
                "date": s["date"],
                "movies": []
            }
            for movie_id in s["movies"]:
                for movie in movies:
                    if movie["id"] == movie_id:
                        result["movies"].append(movie)
                        break
            return make_response(jsonify(result), 200)

    return make_response(jsonify({"error": "Schedule not found"}), 404)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
