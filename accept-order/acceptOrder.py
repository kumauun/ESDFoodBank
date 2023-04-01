from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests

import amqp_setup
import pika
import json

from invoke import invoke_http


app = Flask(__name__)
CORS(app)


#accept order dapet dari driver UI
@app.route("/accept_order", methods=['PUT'])
def accept_order():
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
    # 1. update status ordernya jadi 'picked up'
    # 2. retrieve phone number foodbank and restoran from order table
    # 3. notification ke foodbank using the foodbank phone number yang didapet dr previous request
    # 4. notification ke restaurant using the restaurant phone number yang didapet dr previous request
    # 5. update order buat include the driver_id and driver phone number
    # 6. update status driver jadi 'unavailable' ato False ( kayanya ini Boolean si coba cek di database )
    # 7. send back response to driver UI
def processAcceptOrder():
    accept_order_result = invoke_http("http://localhost:5004/update_order_accepted", method='PUT', json=accept_order)
    code = accept_order_result["code"]
    message = json.dumps(accept_order_result)

    order_result = invoke_http("http://localhost:5004/update_order_accepted", method='PUT', json=accept_order)

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

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": foodbank")
    app.run(host='0.0.0.0', port=5009, debug=True)
