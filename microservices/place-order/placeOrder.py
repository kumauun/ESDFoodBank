from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests

# import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)

# all URL 
restaurant_URL="http://localhost:5001/"
foodbank_URL= "http://localhost:5002/"
driver_URL = "http://localhost:5003/"
order_URL = "http://localhost:5004/"

def get_foodbank_by_id(foodbank_id):
    result = requests.get(f"{foodbank_URL}/get_foodbank/{foodbank_id}")
    if result.status_code == 200:
        return result.json()['data']
    else:
        return None
    
    
    
def publish_message_to_restaurant(region, foodbank_name, foodbank_phone_number, order_id):
    message = f"Your post of id {order_id} has been ordered by {foodbank_name} (contact number: '+{foodbank_phone_number}+')" 
    try:
        # publish message to RabbitMQ exchange
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # declare the exchange
        channel.exchange_declare(exchange='restaurant_foodbankorder', exchange_type='direct')
        channel.queue_declare(queue='foodbankorder', durable=True)
        channel.queue_bind(queue='foodbankorder', exchange='restaurant_foodbankorder', routing_key='foodbankorder')
        # publish message to RabbitMQ exchange
        channel.basic_publish(
            exchange='restaurant_foodbankorder',
            routing_key='foodbankorder',
            body=message
        )
        # close the connection
        connection.close()
    except Exception as e:
        print("An error occurred while publishing the message: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to notify restaurant: " + str(e)
            }
        ), 500
        
def publish_message_to_driver(region, foodbank_name, foodbank_phone_number, driver_phone_number):
    message = "New order from foodbank"+foodbank_name+'(contact number: '+foodbank_phone_number+')' + " in region " + region
    try:
        # publish message to RabbitMQ exchange
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # declare the exchange
        channel.exchange_declare(exchange='notify_driver', exchange_type='direct')
        channel.queue_declare(queue='new_order', durable=True)
        channel.queue_bind(queue='new_order', exchange='notify_driver', routing_key='new_order')
        # publish message to RabbitMQ exchange
        channel.basic_publish(
            exchange='notify_driver',
            routing_key='new_order',
            body=message
        )
        # close the connection
        connection.close()
    except Exception as e:
        print("An error occurred while publishing the message: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to notify driver: " + str(e)
            }
        ), 500

@app.route("/place_order", methods=['PUT'])
def place_order():
    print('place_order invoked')
    # 1. retrieve foodbank details from the foodbank table
    print(request.json)
    order_id= request.json['order_id']
    foodbank_id = request.json['foodbank_id']
    print('bukan foodbank_id ini yang salah')
    print(f'received order_id: {order_id}, foodbank_id: {foodbank_id}')
    foodbank= get_foodbank_by_id(foodbank_id)
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
    publish_message_to_restaurant(region, foodbank_name, foodbank_phone_number, order_id)
    
    try:
        # invoke foodbank microservice to get the phone number of foodbanks in the region
        result = requests.get(driver_URL + f"/get_driver/{region}")
        drivers = result.json()['data']
        driver_phone_numbers = [driver['phone_number']
                                  for driver in drivers]

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
    for driver_phone_number in driver_phone_numbers:
        publish_message_to_driver(
            region, foodbank_name, foodbank_phone_number, driver_phone_number)
        print("Sent message to:"+driver_phone_number)


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
