from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"



# Route 1 (GET) : Tout le planning (/json)
@app.route("/json", methods=['GET'])
def planning():
   res = make_response(jsonify(schedule), 200)
   return res

# Route 2 (GET) : Films programmés à une date (/schedule/<date>)


# Route 3 (GET) : Dates où passent passe le film (/moviedates/<movieid>)


# Route 4 (POST) : Ajouter une date et ses films (/schedule/<date>)


# Route 5 (DELETE) : Supprimer une date (/schedule/<date>)



if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
