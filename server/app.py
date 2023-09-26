#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request, abort
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
api=Api(app)


@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        all_campers = []
        for camper in Camper.query.all():
            camper_dict = {'id': camper.id, 
                         'name': camper.name, 
                         'age': camper.age}
            all_campers.append(camper_dict)

        response = make_response(all_campers, 200)
        return response
    
    def post(self):
        data = request.get_json()
        try:
            new_camper = Camper(
                name=data['name'],
                age=data['age']
            )
        except:
            body = {'errors':['validation errors']}
            return make_response(body, 400)
        
        db.session.add(new_camper)
        db.session.commit()

        body = {'id': new_camper.id, 
                'name': new_camper.name, 
                'age': new_camper.age}
        return make_response(body, 202)


class CampersById(Resource):
    def get(self, id):
        camper = Camper.query.filter(Camper.id==id).first()
        if camper:
            body = camper.to_dict()
            return make_response(body, 200)
    
        else:
            body = {'error': 'Camper not found'}
            return make_response(body, 404)
    
    def patch(self, id):
        camper = Camper.query.filter(Camper.id==id).first()
        data = request.get_json()
        if camper:
            try:
                for key in data.keys():
                    setattr(camper, key, data[key])
                db.session.add(camper)
                db.session.commit()
                body={'id': camper.id, 
                    'name': camper.name,
                    'age': camper.age}
                return make_response(body, 202)
            except:
                body = {'errors': ['validation errors']} 
                return make_response(body, 400)

        if not camper:
            body = {'error': 'Camper not found'}
            return make_response(body, 404)


class Activities(Resource):
    def get(self):
        all_activities = []
        for activity in Activity.query.all():
            activity_dict = {'id': activity.id, 
                         'name': activity.name, 
                         'difficulty': activity.difficulty}
            all_activities.append(activity_dict)

        response = make_response(all_activities, 200)
        return response
    
class ActivitiesByID(Resource):
    def delete(self, id):
        activity = Activity.query.filter(Activity.id==id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return ('', 204)
        
        if not activity:
            body = {'error':'Activity not found'}
            return make_response(body, 404)

class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_signup = Signup(
                camper_id = data['camper_id'],
                activity_id = data['activity_id'],
                time = data['time']
            )
            db.session.add(new_signup)
            db.session.commit()
            body = new_signup.to_dict()
            return make_response(body, 202)
        except:
            body = {'errors': ['validation errors']}
            return make_response(body, 400)

api.add_resource(Campers, '/campers')
api.add_resource(CampersById, '/campers/<int:id>')
api.add_resource(Activities, '/activities')
api.add_resource(ActivitiesByID, '/activities/<int:id>')
api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
