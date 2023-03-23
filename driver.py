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

class driver(db.Model):
    __tablename__ = 'drivers2'

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
@app.route("/get_driver/<driver_id>")
def get_driver_by_id(driver_id):
    pass  #edit ini dong hehe

#get driver by region and availability=true
@app.route("get_driver_region/<region>")
def get_driver_region_availaibility(region):
    availability = True
    pass #edit ini

#update driver availability
@app.route("/update_driver/<to_be_status>")
def update_driver_status(to_be_status):
    pass #edit ini

@app.route("/new_driver", methods=['POST'])
def create_driver():
    print('hallo')
    data = request.get_json()

    print('ini datanya', data)
    driver_id = data.get('driver_id')
    driver_name = data.get('driver_name')
    phone_number = data.get('phone_number')
    region = data.get('region')
    availability = data.get('availability')

    new_driver = driver(driver_id = driver_id, driver_name=driver_name, phone_number=phone_number, region=region, availability=availability)

    print(driver_id)
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("This is flask for " + os.path.basename(__file__) + ": driver")
    app.run(host='0.0.0.0', port=5003, debug=True)