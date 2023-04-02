from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests

file_directory = '../'
sys.path.append(file_directory)

import amqp_setup
import pika
import json

from invoke import invoke_http


app = Flask(__name__)
CORS(app)


#accept order dapet dari driver UI
@app.route("/accept_order", methods=['PUT'])
def accept_order():
    print("Hallo")
    print(request)
    if request.is_json:
        try:
            # ada driver id, driver phone number, status jadi accepted
            driver = request.get_json()
            result = processAcceptOrder(driver)
            return jsonify(result), result["code"]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            return jsonify({
                "code": 500,
                "message": "acceptOrder.py internal error: " + ex_str
            }), 500
    pass    
    
def processAcceptOrder(driver):
    # 1. update status ordernya jadi 'picked up'
    print("hello")
    result1 = invoke_http("http://localhost:5004/update_order_accepted", method='PUT', json=driver["data"])
    code = result1["code"]
    message = json.dumps(result1)

    # 2. retrieve phone number foodbank, restoran from order table
    result2 = invoke_http("http://localhost:5004/get_order_by_id", method='GET') #change jadi whatever the get by id url is in the oprder management
    code2 = result2["code"]
    foodbank_phone_number = result2["data"]["foodbank_phone_number"]
    restaurant_phone_number = result2["data"]["restaurant_phone_number"]
    message2 = json.dumps(result2)
    
    # 3. notification ke foodbank using the foodbank phone number yang didapet dr previous request
    template_msg3 = f'Your order is accepted by a driver, please wait for your food to come'
    message3 = { "code": 200, "message": { "phone_number": foodbank_phone_number, "template_msg": template_msg3} } # please add phone number ama template message
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="foodbank.driver_pickup", 
            body=json.dumps(message3), properties=pika.BasicProperties(delivery_mode = 2)) 


    # 4. notification ke restaurant using the restaurant phone number yang didapet dr previous request
    template_msg4 = f'Your order is accepted by a driver, please wait for your food to be picked up'
    message4 = { "code": 200, "message": { "phone_number": restaurant_phone_number, "template_msg": template_msg4}}
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="foodbank.driver_pickup", 
            body=json.dumps(message4), properties=pika.BasicProperties(delivery_mode = 2))

    # 5. update order buat include the driver_id and driver phone number
    # result5 = invoke_http("http://localhost:5004/update_order_accepted", method='PUT', json=accept_order)
    # code = result5["code"]
    # message = json.dumps(result5)

    # 6. update status driver jadi 'unavailable' ato False ( kayanya ini Boolean si coba cek di database )
    result6 = invoke_http(f"http://localhost:5004/update_driver_status/{driver.get('driver_id')}", method='PUT', json=accept_order)
    code = result6["code"]
    message6 = json.dumps(result6)

    # 7. send back response to driver UI
    return jsonify({'message': 'Order accepted successfully.'})

#order_delivered
@app.route("/order_delivered", methods=['PUT'])
def order_delivered():
    if request.is_json:
        try:
            # ada driver id, driver phone number, status jadi accepted
            order = request.get_json()
            result = processAcceptOrder(order)
            return jsonify(result), result["code"]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            return jsonify({
                "code": 500,
                "message": "acceptOrder.py internal error: " + ex_str
            }), 500

def processOrderDelivered(order):
    #order is a dictionary
    # 1. update status ordernya jadi 'delivered'
    result1 = invoke_http(f"http://localhost:5005/update_order_status", method='PUT', json=order["data"])

    pass


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

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": foodbank")
    app.run(host='0.0.0.0', port=5009, debug=True)
