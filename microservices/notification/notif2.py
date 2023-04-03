#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import json
import os
import amqp_setup
from twilio.rest import Client

ACCOUNT_SID = 'AC3787c29d6d589298c79c868ae48c9078'
AUTH_TOKEN = '0526be0ea35265adf4f128a455ccd3e5'
TWILIO_PHONE_NUMBER = '+14346026523'

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# def sendNotificationFoodbank():
#     amqp_setup.check_setup()
        
#     queue_name = 'new_food'
    
#     # set up a consumer and start to wait for coming messages
#     amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
#     amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
#     #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def setup_consumers():
    amqp_setup.check_setup()

    queues = [
        'new_food',
        'new_order',
        'foodbankorder',
        'driver'
    ]

    for queue_name in queues:
        amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    amqp_setup.channel.start_consuming()


def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived a new message")
    sendSMS(body)
    print() # print a new line feed

def sendSMS(body):
    # Add your Twilio credentials and phone number here
    data = json.loads(body)
    target_phone_numbers = data.get('target_phone_numbers')
    template_message = data.get('template_message')
    
    for phone_number in target_phone_numbers:
        try:
            sms = twilio_client.messages.create(
                body=template_message,
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            print("SMS notification sent successfully")
        except Exception as e:
            print(f"Failed to send SMS: {str(e)}")



if __name__ == "__main__":
    print("\nThis is " + os.path.basename(__file__), end='')
    setup_consumers()
