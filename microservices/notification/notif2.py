#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import json
import os
import amqp_setup

def sendNotificationFoodbank():
    amqp_setup.check_setup()
        
    queue_name = 'new_food'
    
    # set up a consumer and start to wait for coming messages
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

# def callback(channel, method, properties, body): # required signature for the callback; no return
#     print("\nReceived a new posting notification:")
#     sendSMS(body)
#     print() # print a new line feed

# def sendSMS(body):
#     # Add your Twilio credentials and phone number here
#     account_sid = '<YOUR_ACCOUNT_SID>'
#     auth_token = '<YOUR_AUTH_TOKEN>'
#     client = Client(account_sid, auth_token)

#     message = client.messages \
#                     .create(
#                         body=f"New food item posted: {body}",
#                         from_='<YOUR_TWILIO_PHONE_NUMBER>',
#                         to='<YOUR_DESTINATION_PHONE_NUMBER>'
#                     )

#     print(f"SMS sent with message ID: {message.sid}")


if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("\nThis is " + os.path.basename(__file__), end='')
    # print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    # receiveNotification()
