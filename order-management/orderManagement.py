#bikin db modelnya 


#1. add new order (order_id, foodbank_id, resto_id, status, )


# #2. update order status (
# #pas di posting statusnya 'pending', 
#  pas foodbank accept statusnya 'ordered'
#pas dpt driver status 'accepted'
#pas lagi di jalan statusnya 'picked up'
# pas udh nyampe statusnya 'delivered'
# #)
#tentatif kalo mau implement cancel, ganti balik jadi 'ordered' 
#trs notify semua user yg bersangkutan, delete the driver id


#jangan lupa set postnya ama the __main__ stuff

import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from datetime import datetime
import json
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or "mysql+mysqlconnector://admin:rootroot@db-savood.c0hav88yk9mq.us-east-1.rds.amazonaws.com:3306/foodbank"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)

class Order(db.Model):
    __tablename__ = 'orders2'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    foodbank_id = db.Column(db.Integer, nullable=False)
    foodbank_address = db.Column(db.String(30))
    foodbank_postalcode = db.Column(db.Integer)
    restaurant_id = db.Column(db.Integer, nullable=False)
    restaurant_address = db.Column(db.String(30))
    restaurant_postalcode = db.Column(db.Integer)
    dish_id = db.Column(db.Integer, nullable=False)
    quantity_check = db.Column(db.Boolean, nullable=False, default=True)
    status = db.Column(db.Enum('pending', 'ordered', 'accepted', 'picked up', 'delivered', 'cancelled', 'done'), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    def json(self):
        return {
            'order_id': self.order_id,
            'foodbank_id': self.foodbank_id
            'foodbank_address': self.foodbank_address,
            'foodbank_postalcode': self.foodbank_postalcode,
            'restaurant_id': self.restaurant_id,
            'restaurant_address': self.restaurant_address,
            'restaurant_postalcode': self.restaurant_postalcode,
            'dish_id': self.dish_id,
            'quantity_check': self.quantity_check
            'status': self.status
            'created_at': self.created_at
    }


@app.route("/new_order", methods=['POST'])
def create_order():
    data = request.get_json()
    
    foodbank_id=data.get('foodbank_id'),
    foodbank_address=data.get('foodbank_address'),
    foodbank_postalcode=data.get('foodbank_postalcode'),
    restaurant_id=data.get('restaurant_id'),
    restaurant_address=data.get('restaurant_address'),
    restaurant_postalcode=data.get('restaurant_postalcode'),
    dish_id=data.get('dish_id'),
    quantity_check=data.get('quantity_check')
    status=data.get('status')
    created_at=data.get('created_at')
    new_order = Order(foodbank_id=foodbank_id,foodbank_address=foodbank_address,foodbank_postalcode=foodbank_postalcode,restaurant_id=restaurant_id,restaurant_address=restaurant_address,restaurant_postalcode=restaurant_postalcode,dish_id,status=status,created_at=created_at)


    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the order. " + str(e)
            }
        ), 500

    return jsonify(
        { 
            "code": 201,
            "data": order.json()
        }
    ), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("This is flask for " + os.path.basename(__file__) + ": foodbank")
    app.run(host='0.0.0.0', port=5005, debug=True)




