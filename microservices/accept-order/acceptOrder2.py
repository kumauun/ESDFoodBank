from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests

file_directory = '../'
sys.path.append(file_directory)

#import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)

# all URL 
restaurant_URL="http://localhost:5001/"
foodbank_URL= "http://localhost:5002/"
driver_URL = "http://localhost:5003/"
order_URL = "http://localhost:5004/"

def get_driver_by_id(driver_id):
    result = requests.get(f"{driver_URL}/get_driver/{driver_id}")
    if result.status_code == 200:
        return result.json()['data']
    else:
        return None
    
    
    
def publish_message_to_foodbank(region, driver_name, driver_phone_number, order_id, order_status):
    message = "Your order of id"+ str(order_id)+" has been"+order_status +"by " + driver_name+'(contact number: '+driver_phone_number+')' 
    try:
        # publish message to RabbitMQ exchange
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # declare the exchange
        channel.exchange_declare(exchange='driver_order', exchange_type='direct')
        channel.queue_declare(queue='driver', durable=True)
        channel.queue_bind(queue='driver', exchange='driver_order', routing_key='driver')
        # publish message to RabbitMQ exchange
        channel.basic_publish(
            exchange='driver_order',
            routing_key='driver',
            body=message
        )
        # close the connection
        connection.close()
    except Exception as e:
        print("An error occurred while publishing the message: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to notify foodbank: " + str(e)
            }
        ), 500
        
def publish_message(order_id, status):
    message = "Your order of id"+ str(order_id)+" has been"+ status
    try:
        # publish message to RabbitMQ exchange
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # declare the exchange
        channel.exchange_declare(exchange='driver_deliver', exchange_type='direct')
        channel.queue_declare(queue='driver', durable=True)
        channel.queue_bind(queue='driver', exchange='driver_deliver', routing_key='driver')
        # publish message to RabbitMQ exchange
        channel.basic_publish(
            exchange='driver_deliver',
            routing_key='driver',
            body=message
        )
        # close the connection
        connection.close()
    except Exception as e:
        print("An error occurred while publishing the message: " + str(e))
        return jsonify(
            {
                "code": 500,
                "message": "Failed to notify foodbank: " + str(e)
            }
        ), 500        
        
@app.route("/accept_order", methods=['PUT'])
def accept_order():
    # 1. retrieve driver details from the driver table
    order_id= request.json['order_id']
    driver_id = request.json['driver_id']
    driver= get_driver_by_id(driver_id)
    if driver is None:
        return jsonify(
            {
                "code": 404,
                "message": "driver not found."
            }
        ), 404
    region = driver['region']
    driver_name = driver['driver_name']
    driver_phone_number = driver['phone_number']
    
    accept_order = {
        "driver_id": driver_id,
        "driver_phone_number": driver_phone_number,
        "driver_name": driver_name,
        "status": "accepted"
    }
    try:
        result = requests.put(
            f"{order_URL}/accept_order/{order_id}", json=accept_order)
        response = result.json()
        print(response)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)
        print("Order management microservice is unavailable: " + str(e))
        return jsonify({"code": 500, "message": "Failed to accept order: " + ex_str}), 500
    
    #amqp notify
    
    publish_message_to_foodbank(region, driver_name, driver_phone_number, order_id, "accepted")
    print("message sent from:"+ driver_phone_number)
    return jsonify(
            {
                "code": 200,
                "data": "success accepted order"
            }
    ), 200
    
'''@app.route("/delivered_order", methods=['PUT'])
def delivered_order():
    
        order_id= request.json['order_id']
      
        updated_order = {
                "order_id": order_id,
                "status": "delivered"
            }
        try:
            result = requests.put(
                f"{order_URL}/delivered_order/{order_id}", json=updated_order)
            response = result.json()
            print(response)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)
            print("Order management microservice is unavailable: " + str(e))
            return jsonify({"code": 500, "message": "Failed to update order status: " + ex_str}), 500
        publish_message_to_restaurant(order_id)
        print("order is completed")
        return jsonify(
            {
                "code": 200,
                "data": "success delivered order"
            }
        ), 200
'''      
@app.route("/update_order", methods=['PUT'])
def update_order():
    
        order_id= request.json['order_id']
    
        status = request.json['status']
        updated_order = {
                "order_id": order_id,
                "status": status
            }
        try:
            result = requests.put(
                f"{order_URL}/update_order_status", json=updated_order)
            response = result.json()
            print(response)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)
            print("Order management microservice is unavailable: " + str(e))
            return jsonify({"code": 500, "message": "Failed to update order status: " + ex_str}), 500
        
        publish_message(order_id, status)
        
        return jsonify(
            {
                "code": 200,
                "data": "success delivered order"
            }
        ), 200


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": driver")
    app.run(host='0.0.0.0', port=5009, debug=True)