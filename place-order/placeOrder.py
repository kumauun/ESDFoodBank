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
    # 6. Send back response to foodbank UI 

@app.route("/load_listings", methods=['GET'])
def load_listings():
    pass
    # 1. ambil region dari foodbank table
    # 2. ambil food listings dari order table pake filter region 

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": foodbank")
    app.run(host='0.0.0.0', port=5008, debug=True)
