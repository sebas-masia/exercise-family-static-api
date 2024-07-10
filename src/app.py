"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# create the jackson family object
jackson_family = FamilyStructure("Jackson")

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/members', methods=['GET'])
def get_all_members():
    members = jackson_family.get_all_members()
    return jsonify(members), 200

@app.route('/member/<int:id>', methods=['GET'])
def get_single_member(id):
    member = jackson_family.get_member(id)
    if member is None:
        raise APIException("Member not found", status_code=404)
    required_keys = ['first_name', 'id', 'age', 'lucky_numbers']
    if not all(key in member for key in required_keys):
        raise APIException("Member data is incomplete", status_code=500)
    return jsonify(member), 200

@app.route('/member', methods=['POST'])
def add_member():
    member = request.json
    if not member or 'first_name' not in member or 'age' not in member or 'lucky_numbers' not in member:
        raise APIException("Invalid member data", status_code=400)
    jackson_family.add_member(member)
    return jsonify("Member added"), 200

@app.route('/member/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = jackson_family.get_member(id)
    if member is None:
        raise APIException("Member not found", status_code=404)
    jackson_family.delete_member(id)
    return jsonify({"done": True}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
