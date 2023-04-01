import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from datetime import datetime
import json
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or "mysql+mysqlconnector://admin:rootroot@db-savood.c0hav88yk9mq.us-east-1.rds.amazonaws.com:3306/orders_database"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)

class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region = db.Column(db.Enum('Central', 'North', 'West', 'East', 'North-East'), nullable=False)
    foodbank_id = db.Column(db.Integer)
    foodbank_phone_number = db.Column(db.String(15))
    foodbank_address= db.Column(db.String(100))
    foodbank_name= db.Column(db.String(100))
    restaurant_id = db.Column(db.Integer)
    restaurant_name = db.Column(db.String(200))
    restaurant_phone_number = db.Column(db.String(15))
    restaurant_address = db.Column(db.String(100))
    restaurant_name = db.Column(db.String(100))
    dish_name = db.Column(db.String(100))
    status = db.Column(db.Enum('pending', 'ordered', 'accepted', 'picked up', 'delivered', 'cancelled', 'done'), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    def json(self):
        return {
        'order_id': self.order_id,
        'region': self.region,
        'foodbank_id': self.foodbank_id,
        'foodbank_phone_number': self.foodbank_phone_number,
        'foodbank_address': self.foodbank_address,
        'foodbank_name': self.foodbank_name,
        'restaurant_id': self.restaurant_id,
        'restaurant_name': self.restaurant_name,
        'restaurant_phone_number': self.restaurant_phone_number,
        'restaurant_address': self.restaurant_address,
        'restaurant_name': self.restaurant_name,
        'dish_name': self.dish_name,
        'status': self.status,
        'created_at': self.created_at
        } 

@app.route("/get_order/<order_id>", methods=['GET'])
def get_order(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({"message": "Order not found."}), 404

        return jsonify({
            "message": "Order retrieved successfully.",
            "order": order.json()
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/new_order", methods=['POST'])
def create_order():
    data = request.get_json()

    region = data.get('region')
    foodbank_id = data.get('foodbank_id')
    foodbank_phone_number = data.get('foodbank_phone_number')
    foodbank_address= data.get('foodbank_address')
    foodbank_name= data.get('foodbank_name')
    restaurant_id = data.get('restaurant_id')
    restaurant_phone_number = data.get('restaurant_phone_number')
    restaurant_address= data.get('restaurant_address')
    restaurant_name= data.get('restaurant_name')
    dish_name = data.get('dish_name')
    
    new_order = Order(
        region=region,
        foodbank_id=foodbank_id,
        foodbank_phone_number=foodbank_phone_number,
        foodbank_address=foodbank_address,
        foodbank_name=foodbank_name,
        restaurant_id=restaurant_id,
        restaurant_phone_number=restaurant_phone_number,
        restaurant_address=restaurant_address,
        restaurant_name=restaurant_name,
        dish_name=dish_name,
        status='pending'
    )

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

@app.route("/get_order/<region>", methods=['GET'])
def get_order_by_region(region):
    data = request.get_json()
    user_type = data.get('user_type')

    #filter is based on who the user_type is
    if user_type == 'foodbank':
        status = 'pending'
    elif user_type == 'driver':
        status = 'ordered'

    orderlist = Order.query.filter_by(region=region).filter_by(status=status).all()

    if orderlist:
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


@app.route("/get_self_postings/<int:restaurant_id>", methods=['GET'])
def get_self_postings(restaurant_id):
    orderlist = Order.query.filter_by(restaurant_id=restaurant_id).all()

    if orderlist:
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


@app.route("/update_order_ordered", methods=['PUT'])
def update_order_details():
    try:
        order_data = request.get_json()
        order_id = order_data.get('order_id')
        new_status = order_data.get('status')
        foodbank_id = order_data.get('foodbank_id')
        foodbank_phone_number = order_data.get('foodbank_phone_number')
        
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({"message": "Order not found."}), 404

        order.status = new_status

        if new_status == 'ordered':
            order.foodbank_id = foodbank_id
            order.foodbank_phone_number = foodbank_phone_number

        db.session.commit()

        return jsonify({
            "message": "Order status and foodbank details updated successfully.",
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

        if new_status == 'accepted' and driver_id:
            order.driver_id = driver_id

        db.session.commit()

        return jsonify({
            "message": "Order status updated successfully.",
            "order": order.json()
        }), 200
        
    except Exception as e:
        return jsonify({"message": str(e)}), 500 

@app.route("/update_order_status", methods=['PUT'])
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

@app.route("/get_previous_orders/<int:foodbank_id>")
def get_previous_orders(foodbank_id):
    
    orderlist = Order.query.filter_by(foodbank_id=foodbank_id, status='completed').all()

    if orderlist:
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
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("This is flask for " + os.path.basename(__file__) + ": foodbank")
    app.run(host='0.0.0.0', port=5005, debug=True)




