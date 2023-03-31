from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests
from invokes import invoke_http

import pika
import json

app = Flask(__name__)
CORS(app)

restaurant_URL="http://localhost:5001/restaurant"
foodbank_URL= "http://localhost:5002/foodbank"
orderManagement_URL="http://localhost:5005/orderManagement"

def get_restaurant_by_id(restaurant_id):
    result = invoke_http(restaurant_URL + f"/get_restaurant/{restaurant_id}", method='GET')
    if result['code'] == 200:
        return result['data']
    else:
        return None

def publish_message_to_foodbank(region, phone_number):
    message = {
        "region": region,
        "phone_number": phone_number
    }
    message = json.dumps(message)
    
    # establish a connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # create the foodbank exchange if it doesn't exist
    channel.exchange_declare(exchange='foodbank', exchange_type='topic')

    # publish the message to the foodbank exchange with the region as the routing key
    channel.basic_publish(exchange='foodbank', routing_key=region, body=message)

    # close the connection
    connection.close()

@app.route("/post_food", methods=['POST'])
def post_food():
    
    # 1. retrieve phone number of restaurant that is posting the surplus food
    restaurant_id = request.form.get('restaurant_id')
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        return jsonify(
            {
                "code": 404,
                "message": "Restaurant not found."
            }
        ), 404
    phone_number = restaurant['phone_number']
    
    # 2. create new order di tabel order, order status is pending, order restaurant phone number from reponse #1
    new_order = {
        "restaurant_phone_number": phone_number,
        "status": "pending"
    }
    try:
        # invoke order management microservice to add new order
        result = invoke_http(orderManagement_URL + "/add_order", method='POST', json=new_order)
        order = result['data']
        print(f"Added new order to order management microservice: {order}")
    except Exception as e:
        print("Order management microservice is unavailable: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to create new order: " + str(e)
            }
    ), 500
    # 3. get phone number of foodbank in the region
    region = restaurant['region']
    try:
        # invoke foodbank microservice to get the phone number of foodbank in the region
        result = invoke_http(foodbank_URL + f"/get_foodbank_by_region/{region}", method='GET')
        foodbank = result['data']
        foodbank_phone_number = foodbank['phone_number']
        print(f"Retrieved foodbank phone number in region {region}: {foodbank_phone_number}")
    except Exception as e:
        print("Foodbank microservice is unavailable: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to retrieve foodbank phone number: " + str(e)
            }
        ), 500
    
    # 4. notify foodbank with the phone number retrieved from the request above
    '''message = {
        "restaurant_phone_number": phone_number,
        "foodbank_phone_number": foodbank_phone_number,
        "region": region
    }
    try:
        # publish message to RabbitMQ exchange
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="foodbank", 
                                         body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2))
        print("Sent message to RabbitMQ Exchange")
    except Exception as e:
        print("An error occurred while publishing the message: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to notify foodbank: " + str(e)
            }
        ), 500
    '''
    #5 send back response to restaurant UI    
    response_message = {
    "code": 200,
    "message": "Surplus food posted successfully."
    }
    status_code = 200

    return jsonify(response_message), status_code