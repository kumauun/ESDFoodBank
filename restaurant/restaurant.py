import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from datetime import datetime
import json
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or "mysql+mysqlconnector://admin:rootroot@db-savood.c0hav88yk9mq.us-east-1.rds.amazonaws.com:3306/restaurant"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)

class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    restaurant_id = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(255), nullable=False)
    restaurant_address = db.Column(db.String(255), nullable=False)
    region = db.Column(db.Enum('Central', 'North', 'West', 'East', 'North-East'), nullable=False)
    
    def json(self):
        dto = {
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant_name,
            'phone_number': self.phone_number,
            'restaurant_address': self.restaurant_address,
            'region': self.region
        }

        return dto

#get restaurant by id
@app.route("/get_restaurant/<restaurant_id>")
def get_restaurant_by_id(restaurant_id):
    restaurant = Restaurant.query.filter_by(restaurant_id=restaurant_id).first()
    if restaurant:
        return jsonify(
            {
                "code": 200,
                "data": restaurant.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Restaurant not found."
        }
    ), 404



@app.route("/new_restaurant", methods=['POST'])
def create_restaurant():
    print("")
    data = request.get_json()

    print('ini datanya', data)
    restaurant_id = data.get('restaurant_id')
    restaurant_name = data.get('restaurant_name')
    phone_number = data.get('phone_number')
    restaurant_address = data.get('address')
    region = data.get('region')

    new_restaurant = Restaurant(restaurant_id = restaurant_id, restaurant_name=restaurant_name, phone_number=phone_number,restaurant_address = restaurant_address, region=region)

    print(restaurant_id)
    try:
        db.session.add(new_restaurant)
        db.session.commit()
        print('masuk ke data')
    except Exception as e:
        print(e)
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while adding new restaurant" + str(e)
            }
        ), 500
    
    print(json.dumps(new_restaurant.json(), default=str)) # convert a JSON object to a string and print
    print()

    return jsonify(
        {
            "code": 201,
            "data": new_restaurant.json()
        }
    ), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("This is flask for " + os.path.basename(__file__) + ": restaurant")
    app.run(host='0.0.0.0', port=5001, debug=True)