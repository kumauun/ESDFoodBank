
import json
import pika

from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import sys
import amqp_setup
from os import environ

import requests

app = Flask(__name__)
CORS(app)

restaurant_URL = "http://restaurant:5001/"
foodbank_URL = "http://foodbank:5002/"
orderManagement_URL = "http://order-management:5004/"


def get_restaurant_by_id(restaurant_id):
    result = requests.get(f"{restaurant_URL}/get_restaurant/{restaurant_id}")
    if result.status_code == 200:
        return result.json()['data']
    else:
        return None


def publish_message_to_foodbank(message):
    amqp_setup.check_setup()
    try:
        amqp_setup.channel.basic_publish(exchange='notify_foodbank', routing_key="new_posting", 
            body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2)) 
    
    except Exception as e:
        print("An error occurred while publishing the message: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to notify foodbank: " + str(e)
            }
        ), 500

@app.route("/post_food", methods=['POST'])
def post_food():

    if not request.is_json:
        return jsonify(
            {
                "code": 400,
                "message": "Request does not contain JSON data."
            }
        ), 400

    # 1. retrieve phone number of restaurant that is posting the surplus food
    restaurant_id = request.json['restaurant_id']
    dish_name = request.json['dish_name']
    img_url = request.json['img_url']
    restaurant = get_restaurant_by_id(restaurant_id)
    if restaurant is None:
        return jsonify(
            {
                "code": 404,
                "message": "Restaurant not found."
            }
        ), 404
    restaurant_name = restaurant['restaurant_name']
    restaurant_address = restaurant['restaurant_address']
    restaurant_phone_number = restaurant['phone_number']
    region = restaurant['region']

    # 2. create new order di tabel order, order status is pending, order restaurant phone number from reponse #1
    new_order = {
        "restaurant_id": restaurant_id,
        "restaurant_phone_number": restaurant_phone_number,
        "restaurant_name": restaurant_name,
        "restaurant_address": restaurant_address,
        "region": region,
        "dish_name": dish_name,
        "img_url": img_url,
        "status": "pending"
    }
    try:
        result = requests.post(
            f"{orderManagement_URL}/new_order", json=new_order)
        response = result.json()
        print(response)
        order = response['data']
        print(f"Added new order to order management microservice: {order}")

    except Exception as e:
        print("Order management microservice is unavailable: " + str(e))
        return jsonify({"code": 500, "message": "Failed to create new order: " + str(e)})

    # 3. get phone number of foodbank in the region
    region = restaurant['region']
    try:
        # invoke foodbank microservice to get the phone number of foodbanks in the region
        result = requests.get(foodbank_URL + f"/get_foodbank/{region}")
        foodbanks = result.json()['data']
        foodbank_phone_numbers = [foodbank['phone_number']
                                  for foodbank in foodbanks]

        if not foodbank_phone_numbers:
            return jsonify(
                {
                    "code": 404,
                    "message": "No foodbanks found in this region."
                }
            ), 404

    except Exception as e:
        print("Foodbank microservice is unavailable: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to retrieve foodbank phone number: " + str(e)
            }
        ), 500

    # return jsonify(
    #    {
    #        "code": 200,
    #        "data": [foodbank["phone_number"] for foodbank #in foodbanks]
    #    }
    # ), 200

    # 4. notify foodbank with the phone number retrieved from the request above
    template_message = f"New posting from restaurant {restaurant_name} (contact number: '{restaurant_phone_number}') in you region. Place your order now!"
    message = { "code": 200, "template_message": template_message, "target_phone_numbers": foodbank_phone_numbers}
    publish_message_to_foodbank(message)
    print(template_message)
    print(f"Sent message to: {foodbank_phone_numbers}")

    return jsonify(
        {
            "code": 200,
            "data": "success notify foodbank"
        }
    ), 200


if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for posting surplus food")
    app.run(host="0.0.0.0", port=5007, debug=True)
