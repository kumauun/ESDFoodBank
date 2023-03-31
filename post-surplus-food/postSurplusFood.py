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

# Define constants for the AMQP exchange and queue
EXCHANGE_NAME = 'foodbank_exchange'
QUEUE_NAME = 'foodbank_queue'

# Set up the AMQP connection and channel
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declare the exchange and queue
channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='direct', durable=True)
channel.queue_declare(queue=QUEUE_NAME, durable=True)
channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key='foodbank')

def close_connection():
    connection.close()
    
    
    
    
    
foodbank_URL= "http://localhost:5002/get_foodbank/<foodbank_id>"

order_URL = "http://localhost:5005/new_order"



#/post_food
#dapet dari restoran UI, add new order, tunggu reponse dari order management microservice
# notify foodbank di region thaqt there is new post (message-based),
# fire response back to retoran UI
@app.route("/post_food", methods=['POST'])
def post_food():
    
    # 1. retrieve phone number of restaurant that is posting the surplus food
    restaurant_phone_number = request.json['phone_number']
    
    
    # 2. create new order di tabel order, order status is pending, order restaurant phone number from reponse #1
    order_data = {'status': 'pending', 'restaurant_phone_number': restaurant_phone_number}
    order_response = requests.post('http://order-management-microservice/new_order', json=order_data)
    order_id = order_response.json()['order_id']
    
    
    
    # 3. get phone number of foodbank in the region
    region = request.json['region']
    foodbank_response = requests.get(f'http://foodbank-microservice/foodbank/{region}')
    foodbank_phone_number = foodbank_response.json()['phone_number']
    
    
    
    # 4. notify foodbank with the phone number retrieved from the request above
    message = {'order_id': order_id, 'restaurant_phone_number': restaurant_phone_number}
    amqp_setup.channel.basic_publish(exchange=amqp_setup.EXCHANGE_NAME, routing_key=foodbank_phone_number, body=json.dumps(message))
    
    
    
    # 5. send back response to restaurant UI



#port and __name__ = __main__ stuff