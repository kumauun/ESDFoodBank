import pika
import json
from twilio.rest import Client


# Set your Twilio account SID and auth token
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

# Initialize the Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Set up the connection to RabbitMQ
RABBITMQ_HOST = 'localhost'

connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
# Declare the queues
channel.queue_declare(queue='driver_foodbank_order_region')
channel.queue_declare(queue='foodbank_driver_arrival')
channel.queue_declare(queue='foodbank_driver_pickup')
channel.queue_declare(queue='foodbank_new_posting')
channel.queue_declare(queue='restaurant_driver_pickup')
channel.queue_declare(queue='restaurant_foodbank_order')
channel.queue_declare(queue='restaurant_new_surplus_food')

def send_sms(ch, method, properties, body):
    data = json.loads(body)
    phone_number = data.get('phone_number')
    message = data.get('message')

    if not phone_number or not message:
        print("Error: Missing phone_number or message")
        return

    # Send the SMS using the Twilio client
    try:
        sms = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print("SMS notification sent successfully")
    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")

# Set up the callback function for processing messages from RabbitMQ
channel.basic_consume(queue='driver_foodbank_order_region', on_message_callback=send_sms, auto_ack=True)
channel.basic_consume(queue='foodbank_driver_arrival', on_message_callback=send_sms, auto_ack=True)
channel.basic_consume(queue='foodbank_driver_pickup', on_message_callback=send_sms, auto_ack=True)
channel.basic_consume(queue='foodbank_new_posting', on_message_callback=send_sms, auto_ack=True)
channel.basic_consume(queue='restaurant_driver_pickup', on_message_callback=send_sms, auto_ack=True)
channel.basic_consume(queue='restaurant_foodbank_order', on_message_callback=send_sms, auto_ack=True)
channel.basic_consume(queue='restaurant_new_surplus_food', on_message_callback=send_sms, auto_ack=True)

if __name__ == '__main__':
    try:
        print("Starting RabbitMQ consumer")
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping RabbitMQ consumer")
        channel.stop_consuming()
        connection.close()
