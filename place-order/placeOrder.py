from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests
from invokes import invoke_http

import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)

# all URL 
restaurant_URL="http://localhost:5001/restaurant"
foodbank_URL= "http://localhost:5002/foodbank"
driver_URL = "http://localhost:5002/driver"
order_URL = "http://localhost:5005/orderManagement"

@app.route("/place_order", methods=['POST'])
def place_order():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            order = request.get_json()
            print("\nReceived an order in JSON:", order)

            # do the actual work
            # 1. Send order info {cart items}
            result = processPlaceOrder(order)
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "place_order.py internal error: " + ex_str
            }), 500
        
    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


#dapet dari foodbank UI, kirim request ke order management for update order, receive reponse 
#dari order management, fire back to foodbank UI

# Function to update the order in the order management microservice
def processPlaceOrder(order):

    # order = dict

    #2. change the order status from pending to ordered + update food details 
    foodbank_order_URL = order_URL + "/update_order_ordered"
    print('\n-----Invoking order microservice-----')
    order_result = invoke_http(updateOrder_URL, method='PUT', json=order)
    print('order_result:', order_result)

    #3. notify the restaurant about the new order
    print('\n\n-----Publishing the (order info) message with routing_key=order.info-----')
    

    template_msg = f'Your order is accepted by a foodbank, please proceed to prepare your food'
    
    message = { "code": 200, "message": { "phone_number": foodbank_phone_number, "template_msg": template_msg} }

    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="restaurant.foodbank_order",
        body=message, properties=pika.BasicProperties(delivery_mode = 2))

    print("\nOrder published to RabbitMQ Exchange.\n")

    #4. find the driver that is in same region as the foodbank
    region = order.get('region')
    driver_region_URL = driver_URL + "/get_available_driver_region/{region}"
    print('\n-----Invoking driver microservice-----')

    response = invoke_http(driver_region_URL, method='GET')
    
    
    drivers_result = response.json() # all the driver json that is in that region 
    
    #5. notify the driver that is in the same region as foodbank

    restaurant_name = order.get('restaurant_name')

    for driver in drivers_result.get('data', {}).get('drivers', []):
        driver_name = driver.get('driver_name')
        driver_phone_number = driver.get('phone_number')

        template_msg = f'There is a new order for restaurant {restaurant_name}, see if you want to deliver this'

        message = {
            "code": 200,
            "message": {
                "phone_number": driver_phone_number,
                "template_msg": template_msg
            }
        }

        amqp_setup.channel.basic_publish(
            exchange=amqp_setup.exchangename,
            routing_key="restaurant.foodbank_order",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode = 2)
        )
    
    print("\nOrder published to RabbitMQ Exchange for all available drivers in the region.\n")

    #6. Send back response to foodbank UI
    return jsonify({'message': 'Order placed successfully.'})

# Place order API endpoint
# @app.route("/place_order", methods=['PUT'])
# def place_order():
#     # 1. retrieve phone number of foodbank that places the order from the foodbank table
#     foodbank_id = request.json['foodbank_id']
#     response = requests.get(foodbank_URL + "/get_foodbank/" + foodbank_id)
#     foodbank_phone = response.json()['phone_number']

#     # 2. update order status to 'ordered' and order foodbank number with the #1 output
#     order_id = request.json['order_id']
#     update_order(order_id, foodbank_phone) # add foodbank_id buat payload update status

#     # 3. retrieve restaurant phone number from order table
#     response = requests.get(orderManagement_URL + "/get_order/" + order_id)
#     #ini variabel 'response' mau consider ganti ga biar g ke overwrite in case butuh?
#     restaurant_id = response.json()['restaurant_id'] #both resto id and resto phone bs didapet dr request di atas
#     response = requests.get(restaurant_URL + "/get_phone_number/" + restaurant_id)
#     restaurant_phone = response.json()['phone_number']

#     # 4. notify involved restaurant
#     notify_restaurant(restaurant_phone, order_id)

#     # 5. retrieve phone number driver yang ada di regionnya
#     foodbank_region = request.json['foodbank_region']
#     drivers = get_drivers(foodbank_region)

#     # 6. notify driver yang ada di regionnya
#     notify_drivers(drivers, order_id)

#     # 7. Send back response to foodbank UI
#     return jsonify({'message': 'Order placed successfully.'})

@app.route("/load_orders/<foodbank_id>", methods=['GET'])
def load_orders(foodbank_id):

    # 1. retrieve foodbank details from the foodbank table 
    load_order_URL = foodbank_URL + f"/get_foodbank/{foodbank_id}"
    print('\n-----Invoking foodbank microservice-----')
    
    response = requests.get(load_order_URL)
    foodbank_response = response.json()['data']

    print('foodbank details:', foodbank_details)
        
    foodbank_region = foodbank_details['region']
    foodbank_name = foodbank_details['foodbank_name']
    foodbank_phone_number = foodbank_details['phone_number']
    foodbank_address = foodbank_details['foodbank_address']

    # foodbank_id = request.json['foodbank_id']
    # response = requests.get(foodbank_URL + "/get_foodbank/" + foodbank_id)
    # region = response.json()['region']

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
    app.run(host='0.0.0.0', port=5008, debug=True)
