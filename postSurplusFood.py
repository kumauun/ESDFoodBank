from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests

#import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)


#/post_food
#dapet dari restoran UI, add new order, tunggu reponse dari order management microservice
# notify foodbank di region thaqt there is new post (message-based),
# fire response back to retoran UI
@app.route("/post_food", methods=['POST'])
def post_food():
    pass
    # 1. create new order di tabel order, order status is pending
    # 2. get phone number of foodbank in the region
    # 3. notify foodbank with the phone number retrieved from the request above
    # 4. send back response to restaurant UI



#port and __name__ = __main__ stuff