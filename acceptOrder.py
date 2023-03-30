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


#accept order dapet dari driver UI
@app.route("/accept_order", methods=['PUT'])
def accept_order():
    pass
    # 1. update status ordernya jadi 'picked up'
    # 2. retrieve phone number foodbank and restoran from order table
    # 3. notification ke foodbank using the foodbank phone number yang didapet dr previous request
    # 4. notification ke restaurant using the restaurant phone number yang didapet dr previous request
    # 5. update order buat include the driver_id and driver phone number
    # 6. update status driver jadi 'unavailable' ato False ( kayanya ini Boolean si coba cek di database )
    # 7. send back response to driver UI


#order_delivered
@app.route("/order_delivered", methods=['PUT'])
def order_delivered():
    pass
    # 1. update status ordernya jadi 'delivered'
    # 2. retrieve phone number foodbank and restoran
    # 3. notification ke foodbank using the foodbank phone number yang didapet dr previous request
    # 4. notification ke restaurant using the restaurant phone number yang didapet dr previous request
    # 5. update status driver jadi 'available' ato True ( kayanya ini Boolean si coba cek di database )
    # 6. Send back response to driver UI 

#cancel_order_dari driver
@app.route("/order_cancelled", methods=['PUT'])
def order_cancelled():
    pass
    # 1. update status ordernya balik jadi 'ordered'
    # 2. retrieve phone number foodbank and restoran
    # 3. notification ke foodbank using the foodbank phone number yang didapet dr previous request
    # 4. notification ke restaurant using the restaurant phone number yang didapet dr previous request
    # 5. update order to remove the driver_id 
    # 6. update status driver jadi 'available' ato True ( kayanya ini Boolean si coba cek di database )
    # 7. Send back response to driver UI 