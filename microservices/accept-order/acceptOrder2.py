from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests



import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)

# all URL 
restaurant_URL="http://restaurant:5001/"
foodbank_URL= "http://foodbank:5002/"
driver_URL = "http://driver:5003/"
order_URL = "http://order-management:5004/"

def get_driver_by_id(driver_id):
    result = requests.get(f"{driver_URL}/get_driver/{driver_id}")
    if result.status_code == 200:
        return result.json()['data']
    else:
        return None

def get_order_by_id(order_id):
    result = requests.get(f"{order_URL}/get_order/{order_id}")
    if result.status_code == 200:
        print(result.json())
        return result.json()['data']
    else:
        return None
    
    
def publish_message_to_foodbank(message):
    amqp_setup.check_setup()
    try:
        amqp_setup.channel.basic_publish(exchange='driver_order', routing_key="driver", 
            body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2)) 
    
    except Exception as e:
        print("An error occurred while publishing the message: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to notify foodbank: " + str(e)
            }
        ), 500
        
def publish_message(message):
    amqp_setup.check_setup()
    try:
        amqp_setup.channel.basic_publish(exchange='driver_deliver', routing_key="driver", 
            body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2)) 
    
    except Exception as e:
        print("An error occurred while publishing the message: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to notify restaurant and foodbanks: " + str(e)
            }
        ), 500        
        
@app.route("/accept_order", methods=['PUT'])
def accept_order():
    # 1. retrieve driver details from the driver table
    order_id= request.json['order_id']
    driver_id = request.json['driver_id']
    driver= get_driver_by_id(driver_id)
    if driver is None:
        return jsonify(
            {
                "code": 404,
                "message": "driver not found."
            }
        ), 404
    region = driver['region']
    driver_name = driver['driver_name']
    driver_phone_number = driver['phone_number']

    order = get_order_by_id(order_id)
    if order is None:
        return jsonify(
            {
                "code": 404,
                "message": "Target order not found."
            }
        ), 404
    
    foodbank_phone_number = order['foodbank_phone_number']
    
    accept_order = {
        "driver_id": driver_id,
        "driver_phone_number": driver_phone_number,
        "driver_name": driver_name,
        "status": "accepted"
    }
    try:
        result = requests.put(
            f"{order_URL}/accept_order/{order_id}", json=accept_order)
        response = result.json()
        print(response)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)
        print("Order management microservice is unavailable: " + str(e))
        return jsonify({"code": 500, "message": "Failed to accept order: " + ex_str}), 500

    try:
        result = requests.put(
            f"{driver_URL}/update_driver_status/{driver_id}", json=accept_order)
        response = result.json()
        print(response)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)
        print("Driver microservice is unavailable: " + str(e))
        return jsonify({"code": 500, "message": "Failed to update driver status: " + ex_str}), 500
    
    #amqp notify
    template_message = f"Your order of id {order_id} has been accepted by {driver_name} '(contact number: {driver_phone_number}')" 
    message = {"code": 200, "template_message": template_message, "target_phone_numbers": [foodbank_phone_number]}
    publish_message_to_foodbank(message)
    print(template_message)
    print(f"message sent to foodbank {foodbank_phone_number}")
    return jsonify(
            {
                "code": 200,
                "data": "success accepted order"
            }
    ), 200
    
'''@app.route("/delivered_order", methods=['PUT'])
def delivered_order():
    
        order_id= request.json['order_id']
      
        updated_order = {
                "order_id": order_id,
                "status": "delivered"
            }
        try:
            result = requests.put(
                f"{order_URL}/delivered_order/{order_id}", json=updated_order)
            response = result.json()
            print(response)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)
            print("Order management microservice is unavailable: " + str(e))
            return jsonify({"code": 500, "message": "Failed to update order status: " + ex_str}), 500
        publish_message_to_restaurant(order_id)
        print("order is completed")
        return jsonify(
            {
                "code": 200,
                "data": "success delivered order"
            }
        ), 200
'''      
@app.route("/update_order", methods=['PUT'])
def update_order():
    
        order_id= request.json['order_id']
        status = request.json['status']
        driver_id = request.json['driver_id']
        order = get_order_by_id(order_id)

        updated_order = {
                "order_id": order_id,
                "status": status
            }
        
        foodbank_phone_number = order['foodbank_phone_number']
        restaurant_phone_number = order['restaurant_phone_number']
        try:
            result = requests.put(
                f"{order_URL}/update_order_status", json=updated_order)
            response = result.json()
            print(response)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)
            print("Order management microservice is unavailable: " + str(e))
            return jsonify({"code": 500, "message": "Failed to update order status: " + ex_str}), 500
        
        template_message = f"Your order of id {order_id} has been {status}"
        message = {"code": 200, "template_message": template_message, "target_phone_numbers": [foodbank_phone_number, restaurant_phone_number]}
        publish_message(message)
        print(template_message)
        print(f"Published message to foodbank: {foodbank_phone_number} and restaurant: {restaurant_phone_number}")


        if status == 'delivered':
            try:
                result = requests.put(
                    f"{driver_URL}/update_driver_status/{driver_id}", json=updated_order)
                response = result.json()
                print(response)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
                print(ex_str)
                print("Driver microservice is unavailable: " + str(e))
                return jsonify({"code": 500, "message": "Failed to update driver status: " + ex_str}), 500

        
        return jsonify(
            {
                "code": 200,
                "data": "success delivered order"
            }
        ), 200


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": driver")
    app.run(host='0.0.0.0', port=5009, debug=True)