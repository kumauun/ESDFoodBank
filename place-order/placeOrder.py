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
    # 1. update order status to 'ordered'
    # 2. retrieve restaurant id dari order table
    # 3. retrieve phone number restorannya 
    # 4. notify restoran yang bersangkutan
    # 5. retrieve phone number driver yang ada di regionnya
    # 6. notify driver yang ada di regionnya
    # 6. Send back response to foodbank UI 