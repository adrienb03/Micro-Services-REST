from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

from flask_jwt_extended import create_access_token, get_jwt_identity, JWTManager, jwt_required, set_access_cookies, get_jwt

app = Flask(__name__)

# Initialisation de la partie JWT
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False
jwt = JWTManager(app)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

def write(users):
    with open('{}/databases/users.json'.format("."), 'w') as f:
        full = {}
        full['users']=users
        json.dump(full, f)

# returns True if the current user is an admin, False otherwise
def is_admin():
    claims = get_jwt()
    return claims.get("admin", False)

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

# Route d'authentification
# username is the user id
@app.route("/login", methods=["POST"])
def login():
    # 1. Recuperer dans la requête le nom de l'utilisateur qui souhaite se connecter
    username = request.get_json().get("username")
    # 2. Valider que l'utilisateur existe bien
    user = next((u for u in users if u["id"] == username), None)
    if user is None:
        return make_response(jsonify({"error": "User not found"}), 404)
    # Add admin role to JWT
    additional_claims = {
        "admin": user.get("admin", False)
    }
    # 3. Création d'un token d'accès JWT
    access_token = create_access_token(identity=user["id"], additional_claims=additional_claims)
    # renvoyer le token JWT à la fois dans la réponse et dans un cookie
    response = make_response(jsonify({"access_token": access_token}), 200)
    set_access_cookies(response, access_token)
    # 4. Renvoi du token créé
    return response

# get user by id
#only the user himself or an admin can access this endpoint
@app.route("/user/<userid>", methods=["GET"])
@jwt_required()
def infos(userid):
    # 1. Récuperer l'identité jwt
    current_user_id = get_jwt_identity()
    # Find requested user
    user = next((u for u in users if u["id"] == userid), None)
    if user is None:
        return make_response(jsonify({"error": "User not found"}), 404)
    # Check authorization
    if user["id"] != current_user_id and not is_admin():
        return make_response(jsonify({"error": "Forbidden"}), 403)
    return make_response(jsonify(user), 200)

# get all users
# only an admin can access this endpoint
@app.route("/users/json", methods=['GET'])
@jwt_required()
def get_json():
    if not is_admin():
        return make_response(jsonify({"error": "Forbidden"}), 403)
    res = make_response(jsonify(users), 200)
    return res

# Post a new user
# only an admin can post a new user
@app.route("/users/<userid>", methods=['POST'])
@jwt_required()
def add_user(userid):

    if not is_admin():
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    req = request.get_json()

    if not req or req.get("id") != userid:
        return make_response(jsonify({"error": "Invalid user data"}), 400)

    for user in users:
        if str(user["id"]) == str(userid):
            return make_response(jsonify({"error":"user ID already exists"}),409)

    users.append(req)
    write(users)
    res = make_response(jsonify({"message":"user added"}),201)
    return res

# Delete a user
# only an admin can delete a user
@app.route("/users/<userid>", methods=['DELETE'])
@jwt_required()
def del_user(userid):

    if not is_admin():
        return make_response(jsonify({"error": "Forbidden"}), 403)
    
    for user in users:
        if str(user["id"]) == str(userid):
            users.remove(user)
            write(users)
            return make_response(jsonify(user),200)

    res = make_response(jsonify({"error":"user ID not found"}),404)
    return res


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
