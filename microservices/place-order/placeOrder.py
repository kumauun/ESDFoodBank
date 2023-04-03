from flask import Flask, request, jsonify
from flask_cors import CORS

import os
from os import environ

import requests

import sys
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

def get_foodbank_by_id(foodbank_id):
    result = requests.get(f"{foodbank_URL}/get_foodbank/{foodbank_id}")
    if result.status_code == 200:
        return result.json()['data']
    else:
        return None

def get_order_by_id(order_id):
    result = requests.get(f"{order_URL}/get_order/{order_id}")
    if result.status_code == 200:
        return result.json()['data']
    else:
        return None
    
    
    
def publish_message_to_restaurant(message):
    amqp_setup.check_setup()
    try:
        amqp_setup.channel.basic_publish(exchange='restaurant_foodbankorder', routing_key="foodbankorder", 
            body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2)) 
    
    except Exception as e:
        print("An error occurred while publishing the message: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to notify restaurants: " + str(e)
            }
        ), 500
        
def publish_message_to_driver(message):
    amqp_setup.check_setup()
    try:
        amqp_setup.channel.basic_publish(exchange='notify_driver', routing_key="new_order", 
            body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2)) 
    
    except Exception as e:
        print("An error occurred while publishing the message: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to notify drivers: " + str(e)
            }
        ), 500

@app.route("/place_order", methods=['PUT'])
def place_order():
    print('place_order invoked')
    # 1. retrieve foodbank details from the foodbank table
    print(request.json)
    order_id= request.json['order_id']
    foodbank_id = request.json['foodbank_id']
    
    print(f'received order_id: {order_id}, foodbank_id: {foodbank_id}')
    foodbank= get_foodbank_by_id(foodbank_id)
    order = get_order_by_id(order_id)
    if foodbank is None:
        return jsonify(
            {
                "code": 404,
                "message": "Foodbank not found."
            }
        ), 404
    region = foodbank['region']
    foodbank_name = foodbank['foodbank_name']
    foodbank_phone_number = foodbank['phone_number']
    foodbank_address = foodbank['foodbank_address']

    if order is None:
        return jsonify(
            {
                "code": 404,
                "message": "Target order not found."
            }
        ), 404
    restaurant_phone_number = order['restaurant_phone_number']
    
    place_order = {
        "foodbank_id": foodbank_id,
        "foodbank_phone_number": foodbank_phone_number,
        "foodbank_name": foodbank_name,
        "foodbank_address": foodbank_address,
        "status": "ordered"
    }
    try:
        result = requests.put(
            f"{order_URL}/place_order/{order_id}", json=place_order)
        response = result.json()
        print(response)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)
        print("Order management microservice is unavailable: " + str(e))
        return jsonify({"code": 500, "message": "Failed to place order: " + ex_str}), 500
    
    #amqp notify
    template_message = f"Your post of id {order_id} has been ordered by {foodbank_name} (contact number: '{foodbank_phone_number}')" 
    message = { "code": 200, "template_message": template_message, "target_phone_numbers": [restaurant_phone_number]}
    publish_message_to_restaurant(message)
    print(template_message)
    print(f"Message sent to restaurant: {restaurant_phone_number}")
    
    try:
        # invoke foodbank microservice to get the phone number of foodbanks in the region
        result = requests.get(driver_URL + f"/get_available_driver_region/{region}")
        drivers = result.json()['data']
        print(drivers)
        print('test')
        driver_phone_numbers = [driver['phone_number'] for driver in drivers]

        if not driver_phone_numbers:
            return jsonify(
                {
                    "code": 404,
                    "message": "No drivers found in this region."
                }
            ), 404

    except Exception as e:
        print("driver microservice is unavailable: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to retrieve driver phone number: " + str(e)
            }
        ), 500
        
    # 4. notify driver with the phone number retrieved from the request above
    template_message = f"New order from foodbank {foodbank_name} '(contact number: '{foodbank_phone_number}')' in {region} region."
    message = { "code": 200, "template_message": template_message, "target_phone_numbers": driver_phone_numbers}
    publish_message_to_driver(message)
    print(template_message)
    print(f"Sent message to: {driver_phone_numbers}")


    return jsonify(
        {
            "code": 200,
            "data": "success place order"
        }
    ), 200


@app.route("/load_orders/<foodbank_id>", methods=['GET'])
def load_orders(foodbank_id):

    # 1. retrieve foodbank details from the foodbank table 
    load_order_URL = foodbank_URL + f"/get_foodbank/{foodbank_id}"
    print('\n-----Invoking foodbank microservice-----')
    
    response = requests.get(load_order_URL)
    foodbank_response = response.json()['data']

    print('foodbank details:', foodbank_response)
        
    foodbank_region = foodbank_response['region']
    foodbank_name = foodbank_response['foodbank_name']
    foodbank_phone_number = foodbank_response['phone_number']
    foodbank_address = foodbank_response['foodbank_address']

    # 2. Retrieve order listing from the order table using the region filter and status pending
    get_order_URL = order_URL + f"/get_order_by_region/{foodbank_region}?status=pending"
    listings = requests.get(get_order_URL)
    print(listings)
    
    print('pretetet')
    if listings:
        listings_data = listings.json()
        orders_list = listings_data['data']['orders']
        print(orders_list)
        return jsonify(
            {
                "code": 200,
                "data": orders_list
            }
        )
    else:
        return jsonify(
            {
                "code" : 404,
                "message": "Orders not found"
            }
        ), 404


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": foodbank")
    app.run(host='0.0.0.0', port=5008, debug=True)
