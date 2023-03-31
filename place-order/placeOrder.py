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
    url = orderManagement_URL + "/update_order" #bnrin url
    headers = {'Content-Type': 'application/json'}
    data = {'order_id': order_id, 'status': 'ordered', 'foodbank_phone': foodbank_phone} #tambahin foodbank_id
    response = requests.put(url, headers=headers, json=data)
    return response.json()


# Function to notify the restaurant about the new order
def notify_restaurant(restaurant_phone, order_id):
    url = restaurant_URL + "/notify" #ganti pake line bawah ama bikin message
    # amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="restaurant.foodbank_order", 
    #         body=message, properties=pika.BasicProperties(delivery_mode = 2))
    headers = {'Content-Type': 'application/json'}
    data = {'order_id': order_id}
    response = requests.post(url, headers=headers, json=data)
    return response.json()


# Function to retrieve driver phone numbers in the same region as the foodbank
def get_drivers(region):
    url = orderManagement_URL + "/get_available_driver_region/" + region
    headers = {'Content-Type': 'application/json'}
    data = {'region': region} # no need for this??
    response = requests.post(url, headers=headers, json=data) #ganti jadi get
    return response.json()


# Function to notify drivers about the new order
def notify_drivers(drivers, order_id): #idt perlu order_id si, kasitaua aja ada new order di the area
    url = orderManagement_URL + "/notify_drivers" # change to line below, add body message with template msg and phone number
    # amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="driver.foodbank_order_region", 
    #         body=message, properties=pika.BasicProperties(delivery_mode = 2))
    headers = {'Content-Type': 'application/json'}
    data = {'order_id': order_id, 'drivers': drivers}
    response = requests.post(url, headers=headers, json=data)
    return response.json()


# Place order API endpoint
@app.route("/place_order", methods=['PUT'])
def place_order():
    # 1. retrieve phone number of foodbank that places the order from the foodbank table
    foodbank_id = request.json['foodbank_id']
    response = requests.get(foodbank_URL + "/get_foodbank/" + foodbank_id)
    foodbank_phone = response.json()['phone_number']

    # 2. update order status to 'ordered' and order foodbank number with the #1 output
    order_id = request.json['order_id']
    update_order(order_id, foodbank_phone) # add foodbank_id buat payload update status

    # 3. retrieve restaurant phone number from order table
    response = requests.get(orderManagement_URL + "/get_order/" + order_id)
    #ini variabel 'response' mau consider ganti ga biar g ke overwrite in case butuh?
    restaurant_id = response.json()['restaurant_id'] #both resto id and resto phone bs didapet dr request di atas
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
    pass
    # 1. ambil region dari foodbank table
    foodbank_id = request.json['foodbank_id']
    response = requests.get(foodbank_URL + "/get_foodbank/" + foodbank_id)
    region = response.json()['region']
    # 2. ambil food listings dari order table pake filter region 
    listings = requests.get(orderManagement_URL + "/get_order/" + region)
    
    return {
        "code": 201,
        "data": {
           listings
        }
    } #help reformat and test gw buat ini jam 3 subuh g yakin bener

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": foodbank")
    app.run(host='0.0.0.0', port=5008, debug=True)
