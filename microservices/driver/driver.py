import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from datetime import datetime
import json
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or "mysql+mysqlconnector://admin:rootroot@db-savood.c0hav88yk9mq.us-east-1.rds.amazonaws.com:3306/driver"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)

class Driver(db.Model):
    __tablename__ = 'drivers'

    driver_id = db.Column(db.Integer, primary_key=True)
    driver_name = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(255), nullable=False)
    region = db.Column(db.Enum('Central', 'North', 'West', 'East', 'North-East'), nullable=False)
    availability = db.Column(db.Boolean, default=True, nullable=False)
    
    def json(self):
        dto = {
            'driver_id': self.driver_id,
            'driver_name': self.driver_name,
            'phone_number': self.phone_number,
            'region': self.region,
            'availability': self.availability,
        }

        return dto
    
    
#get driver by id
@app.route("/get_driver/<int:driver_id>")
def get_driver_by_id(driver_id):
    driver = Driver.query.filter_by(driver_id=driver_id).first()
    if driver:
        return jsonify(
            {
                "code": 200,
                "data": driver.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Driver not found."
        }
    ), 404

#get driver by region and availability=true
@app.route("/get_available_driver_region/<region>")
def get_driver_region_availaibility(region):
    driverlist = Driver.query.filter_by(region=region).filter_by(availability=True).all()

    if len(driverlist):
        return jsonify(
            {
                "code": 200,
                "data": [driver.json() for driver in driverlist]
            }
            
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no drivers."
        }
    ), 404

#update driver availability
@app.route("/update_driver_status/<int:driver_id>", methods=['PUT'])
def update_driver_status(driver_id):
    driver = Driver.query.filter_by(driver_id=driver_id).first()
    if driver:
        if driver.availability:
            driver.availability = False
        elif driver.availability == False:
            driver.availability = True

        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": driver.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "driver_id": driver_id
            },
            "message": "Driver not found."
        }
    ), 404
    
# add new driver 
@app.route("/new_driver", methods=['POST'])
def create_driver():
    data = request.get_json()

    driver_id = data.get('driver_id')
    driver_name = data.get('driver_name')
    phone_number = data.get('phone_number')
    region = data.get('region')
    availability = data.get('availability')

    new_driver = Driver(driver_id=driver_id, driver_name=driver_name, phone_number=phone_number, region=region, availability=availability)

    try:
        db.session.add(new_driver)
        db.session.commit()
        print('masuk ke data')
    except Exception as e:
        print(e)
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while adding new driver" + str(e)
            }
        ), 500
    
    print(json.dumps(new_driver.json(), default=str)) # convert a JSON object to a string and print
    print()

    return jsonify(
        {
            "code": 201,
            "data": new_driver.json()
        }
    ), 201

#change driver region
@app.route("/update_driver_region/<int:driver_id>", methods=['PUT'])
def update_driver_region(driver_id):
    driver = Driver.query.filter_by(driver_id=driver_id).first()
    
    data = request.get_json()
    new_region = data.get('region')

    driver.region = new_region
    db.session.commit()
        
    return jsonify(
        {
            "code": 200,
            "data": driver.json()
        }
    )
       

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("This is flask for " + os.path.basename(__file__) + ": driver")
    app.run(host='0.0.0.0', port=5003, debug=True)