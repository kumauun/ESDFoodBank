
import json
import pika

from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import sys
from os import environ

import requests
file_directory = './'
sys.path.append(file_directory)
import amqp_setup
app = Flask(__name__)
CORS(app)

restaurant_URL = "http://localhost:5001/"
foodbank_URL = "http://localhost:5002/"
orderManagement_URL = "http://localhost:5004/"


def get_restaurant_by_id(restaurant_id):
    result = requests.get(f"{restaurant_URL}/get_restaurant/{restaurant_id}")
    if result.status_code == 200:
        return result.json()['data']
    else:
        return None


#    def publish_message_to_foodbank(region, restaurant_phone_number, foodbank_phone_number):
 #       message = {
 #           "restaurant_phone_number": restaurant_phone_number, "foodbank_phone_number": foodbank_phone_number,
 #           "region": region
 #       }
 #       try:
  #          # publish message to RabbitMQ exchange
   #         
   #         
   #         amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="foodbank.new_posting",
   #                                         body=message, properties=pika.BasicProperties(delivery_mode=2))
   #         print("Sent message to RabbitMQ Exchange")
   #     except Exception as e:
   #         print("An error occurred while publishing the message: " + str(e))
   #         return jsonify(
   #             {
   #                 "code": 500,
   #                 "message": "Failed to notify foodbank: " + str(e)
   #             }
   #         ), 500

def publish_message_to_foodbank(region, restaurant_name, restaurant_phone_number, foodbank_phone_number):
    message = "New posting from restaurant " + restaurant_name+'(contact number: '+restaurant_phone_number+')' + " in region " + region
    amqp_setup.check_setup()
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="newpost.foodbank", 
            body=message)
 

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
    for foodbank_phone_number in foodbank_phone_numbers:
        publish_message_to_foodbank(
            region, restaurant_name, restaurant_phone_number, foodbank_phone_number)
        print("Sent message to:"+foodbank_phone_number)

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
