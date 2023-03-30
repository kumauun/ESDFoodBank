import pika
from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client

app = Flask(__name__)
CORS(app)

# Set your Twilio account SID and auth token
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

# Initialize the Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Set up the connection to RabbitMQ
RABBITMQ_HOST = 'localhost'
RABBITMQ_QUEUE = 'notification_queue'

connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE)

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
channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=send_sms, auto_ack=True)

if __name__ == '__main__':
    try:
        print("Starting RabbitMQ consumer")
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping RabbitMQ consumer")
        channel.stop_consuming()
        connection.close()
