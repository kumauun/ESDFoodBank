from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests
from invokes import invoke_http

#import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)

restaurant_URL="http://localhost:5001/restaurant"
foodbank_URL= "http://localhost:5002/foodbank"
orderManagement_URL="http://localhost:5005/orderManagement"



#/post_food
#dapet dari restoran UI, add new order, tunggu reponse dari order management microservice
# notify foodbank di region thaqt there is new post (message-based),
# fire response back to retoran UI
@app.route("/post_food", methods=['POST'])
def post_food():
    
    # 1. retrieve phone number of restaurant that is posting the surplus food
    restaurant_id = request.form.get('restaurant_id')
    restaurant = get_restaurant_by_id(restaurant_id).json['data']
    phone_number = restaurant['phone_number']
    # 2. create new order di tabel order, order status is pending, order restaurant phone number from reponse #1
    # 3. get phone number of foodbank in the region
    # 4. notify foodbank with the phone number retrieved from the request above
    # 5. send back response to restaurant UI
    


#port and __name__ = __main__ stuff