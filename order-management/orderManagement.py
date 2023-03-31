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

    #halo gw tambahin nomor telpon, region foodbank ama restonya di tabel ini biar gampang integrate ama twilionya
    #tambahin dish name aja ga drpd dish_id??

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region = db.Column(db.Enum('Central', 'North', 'West', 'East', 'North-East'), nullable=False)
    foodbank_id = db.Column(db.Integer, nullable=False)
    foodbank_address = db.Column(db.String(30))
    foodbank_postalcode = db.Column(db.Integer)
    foodbank_phone_number = db.Column(db.String(255))
    restaurant_id = db.Column(db.Integer, nullable=False)
    restaurant_address = db.Column(db.String(30))
    restaurant_postalcode = db.Column(db.Integer)
    restaurant_phone_number = db.Column(db.String(255))
    dish_id = db.Column(db.Integer, nullable=False) #ini perlu kah?
    quantity_check = db.Column(db.Boolean, nullable=False, default=True) #ini jg perlu kah
    status = db.Column(db.Enum('pending', 'ordered', 'accepted', 'picked up', 'delivered', 'cancelled', 'done'), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    def json(self):
        return {
            'order_id': self.order_id,
            'region': self.region,
            'foodbank_id': self.foodbank_id,
            'foodbank_address': self.foodbank_address,
            'foodbank_postalcode': self.foodbank_postalcode,
            'foodbank_phone_number': self.foodbank_phone_number,
            'restaurant_id': self.restaurant_id,
            'restaurant_address': self.restaurant_address,
            'restaurant_postalcode': self.restaurant_postalcode,
            'restaurant_phone_number': self.restaurant_phone_number,
            'dish_id': self.dish_id,
            'quantity_check': self.quantity_check,
            'status': self.status,
            'created_at': self.created_at
    }

@app.route("/get_order/<int:order_id>")
def get_order_by_id(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    if order:
        return jsonify(
            {
                "code": 200,
                "data": order.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Order not found."
        }
    ), 404
    

@app.route("/new_order", methods=['POST'])
def create_order():
    data = request.get_json()
    
    #foodbank_id=data.get('foodbank_id'),
    #foodbank_address=data.get('foodbank_address'),
    #foodbank_postalcode=data.get('foodbank_postalcode'),
    region = data.get('region'),
    restaurant_id=data.get('restaurant_id'),
    restaurant_address=data.get('restaurant_address'),
    restaurant_postalcode=data.get('restaurant_postalcode'),
    dish_id=data.get('dish_id'),
    quantity_check=data.get('quantity_check') #ini masih kepake ga? 
    created_at=data.get('created_at')
    new_order = Order(region=region, restaurant_id=restaurant_id, restaurant_address=restaurant_address, restaurant_postalcode=restaurant_postalcode, dish_id=dish_id, status='pending') 
    #ini tolong line atas consider add dish name or no

    try:
        db.session.add(new_order)
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
            "data": new_order.json()
        }
    ), 201

@app.route("/get_order/<region>")
def get_order_by_region(region):
    data = request.get_json()
    user_type = data.get('user_type')

    #filter is based on who the user_type is
    if user_type == 'foodbank':
        status = 'pending'
    elif user_type == 'driver':
        status = 'ordered'

    orderlist = Order.query.filter_by(region=region).filter_by(status=status)

    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404
    pass

@app.route("/get_self_postings")
def get_self_postings():
    data = request.get_json()
    restaurant_id = data.get('restaurant_id')
    orderlist = Order.query.filter_by(restaurant_id=restaurant_id)

    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no postings."
        }
    ), 404

    pass

@app.route("/update_order_ordered", methods=['PUT'])
def update_order_details():
    try:
        
        order_data = request.get_json()
        order_id = order_data['order_id']
        new_status = order_data['status']
        foodbank_id = order_data.get('foodbank_id', None)

        valid_statuses = ['pending', 'ordered', 'accepted', 'picked up', 'delivered', 'cancelled', 'done']
        if new_status not in valid_statuses:
            return jsonify(
                {
                    "message": "Invalid status."
                }), 400

        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({"message": "Order not found."}), 404

        order.status = new_status

        # Add foodbank_id to the order when the status is 'ordered'
        if new_status == 'ordered' and foodbank_id:
            order.foodbank_id = foodbank_id

        db.session.commit()

        return jsonify({
            "message": "Order status updated successfully.",
            "order": order.json()
        }), 200
        
    except Exception as e:
        return jsonify({"message": str(e)}), 500 

@app.route("/update_order_accepted",methods=['PUT'])
def update_order_accepted():
    try:
        
        order_data = request.get_json()
        order_id = order_data['order_id']
        new_status = order_data['status']
        driver_id = order_data.get('driver_id', None)

        valid_statuses = ['pending', 'ordered', 'accepted', 'picked up', 'delivered', 'cancelled', 'done']
        if new_status not in valid_statuses:
            return jsonify(
                {
                    "message": "Invalid status."
                }), 400

        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({"message": "Order not found."}), 404

        order.status = new_status

        # Add foodbank_id to the order when the status is 'ordered'
        if new_status == 'accepted' and driver_id:
            order.driver_id = driver_id

        db.session.commit()

        return jsonify({
            "message": "Order status updated successfully.",
            "order": order.json()
        }), 200
        
    except Exception as e:
        return jsonify({"message": str(e)}), 500 

@app.route("/update_order_status")
def update_order_status():
    try:
        order_data = request.get_json()
        order_id = order_data['order_id']
        new_status = order_data['status']

        # Check if the input status is valid
        valid_statuses = ['pending', 'ordered', 'accepted', 'picked up', 'delivered', 'cancelled', 'done']
        if new_status not in valid_statuses:
            return jsonify({"message": "Invalid status."}), 400

        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({"message": "Order not found."}), 404

        order.status = new_status
        db.session.commit()

        return jsonify({
            "message": "Order status updated successfully.",
            "order": order.json()
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("This is flask for " + os.path.basename(__file__) + ": foodbank")
    app.run(host='0.0.0.0', port=5005, debug=True)




