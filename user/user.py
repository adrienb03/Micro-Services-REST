from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

from flask_jwt_extended import create_access_token, get_jwt_identity, JWTManager

app = Flask(__name__)

# Initialisation de la partie JWT
app.config["JWT_SECRET_KEY"] = "super-secret"
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

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

# Route d'authentification
@app.route("/login", methods=["POST"])
def login():
    # 1. Recuperer dans la requête le nom de l'utilisateur qui souhaite se connecter
    username = request.get_json().get("username")
    # 2. Valider que l'utilisateur existe bien
    user = None
    for u in users:
        if u["name"] == username:
            user = u
            break
    if user is None:
        return make_response(jsonify({"error": "User not found"}), 404)
    # 3. Création d'un token d'accès JWT
    access_token = create_access_token(identity=user["id"])
    # 4. Renvoi du token créé
    return make_response(jsonify({"access_token": access_token}), 200)

@app.route("/users/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(users), 200)
    return res

# get user by id
@app.route("/users/<userid>", methods=['GET'])
def get_user_by_id(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user),200)
            return res
    return make_response(jsonify({"error":"User ID not found"}),500)

@app.route("/users/<userid>", methods=['POST'])
def add_user(userid):
    req = request.get_json()

    for user in users:
        if str(user["id"]) == str(userid):
            return make_response(jsonify({"error":"user ID already exists"}),500)

    users.append(req)
    write(users)
    res = make_response(jsonify({"message":"user added"}),200)
    return res

@app.route("/users/<userid>", methods=['DELETE'])
def del_user(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            users.remove(user)
            write(users)
            return make_response(jsonify(user),200)

    res = make_response(jsonify({"error":"user ID not found"}),500)
    return res

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
