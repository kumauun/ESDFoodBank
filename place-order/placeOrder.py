from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests
from invokes import invoke_http
##import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)
restaurant_URL="http://localhost:5001/restaurant"
foodbank_URL= "http://localhost:5002/foodbank"
orderManagement_URL="http://localhost:5005/orderManagement"

#dapet dari foodbank UI, kirim request ke order management for update order, receive reponse 
#dari order management, fire back to foodbank UI
# Function to update the order in the order management microservice
def update_order(order_id, foodbank_phone):
    url = orderManagement_URL + "/update_order"
    headers = {'Content-Type': 'application/json'}
    data = {'order_id': order_id, 'status': 'ordered', 'foodbank_phone': foodbank_phone}
    response = requests.put(url, headers=headers, json=data)
    return response.json()


# Function to notify the restaurant about the new order
def notify_restaurant(restaurant_phone, order_id):
    url = restaurant_URL + "/notify"
    headers = {'Content-Type': 'application/json'}
    data = {'order_id': order_id}
    response = requests.post(url, headers=headers, json=data)
    return response.json()


# Function to retrieve driver phone numbers in the same region as the foodbank
def get_drivers(region):
    url = orderManagement_URL + "/get_drivers"
    headers = {'Content-Type': 'application/json'}
    data = {'region': region}
    response = requests.post(url, headers=headers, json=data)
    return response.json()


# Function to notify drivers about the new order
def notify_drivers(drivers, order_id):
    url = orderManagement_URL + "/notify_drivers"
    headers = {'Content-Type': 'application/json'}
    data = {'order_id': order_id, 'drivers': drivers}
    response = requests.post(url, headers=headers, json=data)
    return response.json()


# Place order API endpoint
@app.route("/place_order", methods=['PUT'])
def place_order():
    # 1. retrieve phone number of foodbank that places the order from the foodbank table
    foodbank_id = request.json['foodbank_id']
    response = requests.get(foodbank_URL + "/get_phone_number/" + foodbank_id)
    foodbank_phone = response.json()['phone_number']

    # 2. update order status to 'ordered' and order foodbank number with the #1 output
    order_id = request.json['order_id']
    update_order(order_id, foodbank_phone)

    # 3. retrieve restaurant phone number from order table
    response = requests.get(orderManagement_URL + "/get_order/" + order_id)
    restaurant_id = response.json()['restaurant_id']
    response = requests.get(restaurant_URL + "/get_phone_number/" + restaurant_id)
    restaurant_phone = response.json()['phone_number']

    # 4. notify involved restaurant
    notify_restaurant(restaurant_phone, order_id)

    # 5. retrieve phone number driver yang ada di regionnya
    foodbank_region = request.json['foodbank_region']
    drivers = get_drivers(foodbank_region)

    # 6. notify driver yang ada di regionnya
    notify_drivers(drivers, order_id)

    # 7. Send back response to foodbank UI
    return jsonify({'message': 'Order placed successfully.'})
@app.route("/load_listings", methods=['GET'])
def load_listings():
    # 1. ambil region dari foodbank table
   
    order_id = request.json['order_id']
    response = requests.get(orderManagement_URL + "/get_order/" + order_id)
    close_region = response.json()['region']
    # 2. take all the listings from the listings table where region = #1 output
    listings= requests.get(orderManagement_URL + "/get_order/" + close_region)
    return listings
    
if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": foodbank")
    app.run(host='0.0.0.0', port=5008, debug=True)
