from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests

##import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)

#dapet dari foodbank UI, kirim request ke order management for update order, receive reponse 
#dari order management, fire back to foodbank UI
@app.route("/place_order", methods=['PUT'])
def accept_order():
    pass
    # 1. retrieve phone number of foodbank that places the order from the foodbank table
    # 2. update order status to 'ordered' and order foodbank number with the #1 output
    # 3. retrieve resto phone number from order table  
    # 4. notify restoran yang bersangkutan
    # 5. retrieve phone number driver yang ada di regionnya
    # 6. notify driver yang ada di regionnya
    # 7. Send back response to foodbank UI 