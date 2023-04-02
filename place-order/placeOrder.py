from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests

import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)

# all URL 
restaurant_URL="http://localhost:5001/"
foodbank_URL= "http://localhost:5002/"
driver_URL = "http://localhost:5003/"
order_URL = "http://localhost:5005/"

def get_foodbank_by_id(foodbank_id):
    result = requests.get(f"{foodbank_URL}/get_foodbank/{foodbank_id}")
    if result.status_code == 200:
        return result.json()['data']
    else:
        return None

@app.route("/place_order", methods=['PUT'])
def place_order():
    # 1. retrieve foodbank details from the foodbank table
    order_id= request.json['order_id']
    foodbank_id = request.json['foodbank_id']
    foodbank= get_foodbank_by_id(foodbank_id)
    if foodbank is None:
        return jsonify(
            {
                "code": 404,
                "message": "Foodbank not found."
            }
        ), 404
    region = foodbank['region']
    foodbank_name = foodbank['foodbank_name']
    foodbank_phone_number = foodbank['phone_number']
    foodbank_address = foodbank['foodbank_address']
    place_order = {
        "foodbank_id": foodbank_id,
        "foodbank_phone_number": foodbank_phone_number,
        "foodbank_name": foodbank_name,
        "foodbank_address": foodbank_address,
        "status": "ordered"
    }
    try:
        result = requests.put(
            f"{order_URL}/place_order/{order_id}", json=place_order)
        response = result.json()
        print(response)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)
        print("Order management microservice is unavailable: " + str(e))
        return jsonify({"code": 500, "message": "Failed to place order: " + ex_str}), 500
    
    
    
    return jsonify(
        {
            "code": 200,
            "data": "success place order"
        }
    ), 200


@app.route("/load_orders/<foodbank_id>", methods=['GET'])
def load_orders(foodbank_id):

    # 1. retrieve foodbank details from the foodbank table 
    load_order_URL = foodbank_URL + f"/get_foodbank/{foodbank_id}"
    print('\n-----Invoking foodbank microservice-----')
    
    response = requests.get(load_order_URL)
    foodbank_response = response.json()['data']

    print('foodbank details:', foodbank_response)
        
    foodbank_region = foodbank_response['region']
    foodbank_name = foodbank_response['foodbank_name']
    foodbank_phone_number = foodbank_response['phone_number']
    foodbank_address = foodbank_response['foodbank_address']

    # 2. Retrieve order listing from the order table using the region filter and status pending
    get_order_URL = order_URL + f"/get_order/{foodbank_region}?status=pending"
    listings = requests.get(get_order_URL)
    
    if listings:
        return jsonify(
            {
                "code": 200,
                "data": [list.json() for list in listings]
            }
        )
    else:
        return jsonify(
            {
                "code" : 404,
                "message": "Orders not found"
            }
        ), 404


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": foodbank")
    app.run(host='0.0.0.0', port=5101, debug=True)
