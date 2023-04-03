import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql.expression import not_, or_

from datetime import datetime, timedelta
import json
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or "mysql+mysqlconnector://admin:rootroot@db-savood.c0hav88yk9mq.us-east-1.rds.amazonaws.com:3306/orders_database"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def utcnow_with_timezone():
    return datetime.utcnow() + timedelta(hours=8)

db = SQLAlchemy(app)

CORS(app, resources={r'*': {'origins': '*'}})

def utcnow_with_timezone():
    return datetime.utcnow() + timedelta(hours=8)

class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region = db.Column(db.Enum('Central', 'North', 'West', 'East', 'North-East'))
    foodbank_id = db.Column(db.Integer) 
    foodbank_phone_number = db.Column(db.String(15))
    foodbank_address= db.Column(db.String(100))
    foodbank_name= db.Column(db.String(100))
    restaurant_id = db.Column(db.Integer)
    restaurant_phone_number = db.Column(db.String(15))
    restaurant_address = db.Column(db.String(100))
    restaurant_name = db.Column(db.String(100))
    driver_id = db.Column(db.Integer)
    driver_phone_number = db.Column(db.String(15))
    driver_name = db.Column(db.String(100))
    dish_name = db.Column(db.String(100))
    status = db.Column(db.Enum('pending', 'ordered', 'accepted', 'picked up', 'delivered', 'done'), nullable=False, default='pending')
    img_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow_with_timezone)


    def json(self):
        return {
        'order_id': self.order_id,
        'region': self.region,
        'foodbank_id': self.foodbank_id,
        'foodbank_phone_number': self.foodbank_phone_number,
        'foodbank_address': self.foodbank_address,
        'foodbank_name': self.foodbank_name,
        'restaurant_id': self.restaurant_id,
        'restaurant_phone_number': self.restaurant_phone_number,
        'restaurant_address': self.restaurant_address,
        'restaurant_name': self.restaurant_name,
        'driver_id': self.driver_id,
        'driver_phone_number': self.driver_phone_number,
        'driver_name': self.driver_name,
        'dish_name': self.dish_name,
        'status': self.status,
        'img_url': self.img_url,
        'created_at': self.created_at
        } 

@app.route("/get_order/<order_id>", methods=['GET'])
def get_order(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({
                "code": 404,
                "message": "Order not found."}), 404

        return jsonify({
            "code": 200,
            "data": order.json()
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/new_order", methods=['POST'])
def create_order():
    data = request.get_json()

    region = data.get('region')
    foodbank_id = data.get('foodbank_id')
    foodbank_phone_number = data.get('foodbank_phone_number')
    foodbank_address = data.get('foodbank_address')
    foodbank_name = data.get('foodbank_name')
    restaurant_id = data.get('restaurant_id')
    restaurant_phone_number = data.get('restaurant_phone_number')
    restaurant_address = data.get('restaurant_address')
    restaurant_name = data.get('restaurant_name')
    driver_id = data.get('driver_id')
    driver_phone_number = data.get('driver_phone_number')
    driver_name = data.get('driver_name')
    dish_name = data.get('dish_name')
    img_url = data.get('img_url')

    new_order = Order(
        region=region,
        foodbank_id=foodbank_id,
        foodbank_phone_number=foodbank_phone_number,
        foodbank_address = foodbank_address,
        foodbank_name=foodbank_name,
        restaurant_id=restaurant_id,
        restaurant_phone_number=restaurant_phone_number,
        restaurant_address = restaurant_address,
        restaurant_name =   restaurant_name,
        driver_id = driver_id,
        driver_phone_number =   driver_phone_number,
        driver_name = driver_name,
        dish_name=dish_name,
        img_url = img_url,
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

@app.route("/get_order_by_region/<region>", methods=['GET'])
def get_order_by_region(region):
    print('Hello')
    status = request.args.get('status')

    #filter is based on who the user_type is
    # if user_type == 'foodbank':
    #     status = 'pending'
    # elif user_type == 'driver':
    #     status = 'ordered'
    print(status)
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
@app.route("/place_order/<int:order_id>", methods=['PUT'])
def place_order(order_id):
    data = request.get_json()
    foodbank_id = data.get('foodbank_id')
    foodbank_phone_number = data.get('foodbank_phone_number')
    foodbank_address = data.get('foodbank_address')
    foodbank_name = data.get('foodbank_name')
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({"message": "Order not found."}), 404

        order.status = 'ordered'
        order.foodbank_id = foodbank_id
        order.foodbank_phone_number = foodbank_phone_number
        order.foodbank_address = foodbank_address
        order.foodbank_name = foodbank_name
        
        db.session.commit()

        return jsonify({
            "message": "Order placed successfully.",
            "order": order.json()
        }), 200
        
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/accept_order/<int:order_id>", methods=['PUT'])
def accept_order(order_id):
    data = request.get_json()
    driver_id = data.get('driver_id')
    driver_phone_number = data.get('driver_phone_number')
    driver_name = data.get('driver_name')
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({"message": "Order not found."}), 404

        order.status = 'accepted'
        order.driver_id = driver_id
        order.driver_phone_number = driver_phone_number
        order.driver_name = driver_name
        
        db.session.commit()

        return jsonify({
            "message": "Order accepted successfully.",
            "order": order.json()
        }), 200
        
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/delivered_order/<int:order_id>", methods=['PUT'])
def delivered_order(order_id):
    data = request.get_json()
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({"message": "Order not found."}), 404

        order.status = 'delivered'
     
        db.session.commit()

        return jsonify({
            "message": "Order delivered successfully.",
            "order": order.json()
        }), 200
        
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
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
    
    orderlist = Order.query.filter_by(foodbank_id=foodbank_id, status='done').all()
    print(orderlist)

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

@app.route("/get_previous_postings/<int:restaurant_id>")
def get_previous_postings(restaurant_id):
    
    orderlist = Order.query.filter_by(restaurant_id=restaurant_id, status='done').all()
    print(orderlist)

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
    
@app.route("/get_non_done_postings/<int:restaurant_id>", methods=['GET'])
def get_non_done_postings(restaurant_id):
    orderlist = Order.query.filter(Order.restaurant_id == restaurant_id, Order.status != 'done').all()
    print(orderlist)

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

@app.route("/get_non_pending_or_done_orders/<int:foodbank_id>", methods=['GET'])
def get_non_pending_or_done_orders(foodbank_id):
    print('cihui')
    try:
        orders = Order.query.filter_by(foodbank_id=foodbank_id).filter(Order.status.notin_(['pending', 'done'])).all()

        if not orders:
            return jsonify({"code": 404, "message": "No orders found."}), 404

        return jsonify({
            "code": 200,
            "orders": [order.json() for order in orders]
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
@app.route("/get_current_deliveries/<int:driver_id>", methods=['GET'])
def get_current_deliveries(driver_id):
    valid_statuses = ['accepted', 'picked up', 'delivered']
    orderlist = Order.query.filter(Order.driver_id == driver_id, Order.status.in_(valid_statuses)).all()
    print(orderlist)

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
    

@app.route("/get_driver_past_deliveries/<int:driver_id>", methods=['GET'])
def get_driver_past_deliveries(driver_id):
    orderlist = Order.query.filter_by(driver_id=driver_id, status='done').all()
    print(orderlist)

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
    app.run(host='0.0.0.0', port=5004, debug=True)




