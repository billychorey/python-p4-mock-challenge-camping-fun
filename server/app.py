#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)


# Routes
@app.route('/campers', methods=['GET'])
def get_campers():
    campers = Camper.query.all()
    campers_list = [camper.to_dict() for camper in campers]
    return make_response(jsonify(campers_list), 200)


@app.route('/campers/<int:id>', methods=['GET'])
def get_camper(id):
    camper = Camper.query.get(id)
    if camper:
        # Include the signups in the response for this specific route
        return make_response(jsonify(camper.to_dict(rules=('-signups.activity',))), 200)
    else:
        return make_response(jsonify({"error": "Camper not found"}), 404)


@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    camper = Camper.query.get(id)
    if camper:
        data = request.get_json()
        try:
            if 'name' in data and not data['name']:
                raise ValueError("validation errors")
            if 'age' in data and not (8 <= data['age'] <= 18):
                raise ValueError("validation errors")
            for key, value in data.items():
                setattr(camper, key, value)
            db.session.commit()
            return make_response(jsonify(camper.to_dict()), 202)
        except ValueError as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)
    else:
        return make_response(jsonify({"error": "Camper not found"}), 404)


@app.route('/campers', methods=['POST'])
def create_camper():
    data = request.get_json()

    # Check if name is empty
    if not data.get('name'):
        return make_response(jsonify({"errors": ["Name cannot be empty"]}), 400)
    
    try:
        camper = Camper(**data)
        db.session.add(camper)
        db.session.commit()
        return make_response(jsonify(camper.to_dict()), 201)
    except ValueError as e:
        return make_response(jsonify({"errors": [str(e)]}), 400)

@app.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()
    activities_list = [activity.to_dict() for activity in activities]
    return make_response(jsonify(activities_list), 200)


@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.get(id)
    if activity:
        db.session.delete(activity)
        db.session.commit()
        return make_response('', 204)
    else:
        return make_response(jsonify({"error": "Activity not found"}), 404)

@app.route('/signups', methods=['POST'])
def create_signup():
    data = request.get_json()
    try:
        # Validate the time directly in the route
        if 'time' in data and not (0 <= data['time'] <= 23):
            raise ValueError("validation errors")
        signup = Signup(**data)
        db.session.add(signup)
        db.session.commit()
        return make_response(jsonify(signup.to_dict()), 201)
    except ValueError as e:
        return make_response(jsonify({"errors": [str(e)]}), 400)



# Home route
@app.route('/')
def home():
    return ''


if __name__ == '__main__':
    app.run(port=5555, debug=True)
