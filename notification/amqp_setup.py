import pika
from os import environ

hostname = environ.get('rabbit_host') or 'localhost'
port = environ.get('rabbit_port') or 5672

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=hostname, port=port,
        heartbeat=3600, blocked_connection_timeout=3600,
    )
)

channel = connection.channel()

exchangename = "notification_topic"
exchangetype = "topic"
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)

queue_names = {
    'restaurant': [
        'restaurant_foodbank_order',
        'restaurant_driver_pickup',
        'restaurant_new_surplus_food'
    ],
    'foodbank': [
        'foodbank_new_posting',
        'foodbank_driver_pickup',
        'foodbank_driver_arrival'
    ],
    'driver': [
        'driver_foodbank_order_region'
    ]
}

routing_keys = {
    'restaurant_foodbank_order': 'restaurant.foodbank_order',
    'restaurant_driver_pickup': 'restaurant.driver_pickup',
    'restaurant_new_surplus_food': 'restaurant.new_surplus_food',
    'foodbank_new_posting': 'foodbank.new_posting',
    'foodbank_driver_pickup': 'foodbank.driver_pickup',
    'foodbank_driver_arrival': 'foodbank.driver_arrival',
    'driver_foodbank_order_region': 'driver.foodbank_order_region'
}

for key, queues in queue_names.items():
    for queue_name in queues:
        channel.queue_declare(queue=queue_name, durable=True)
        routing_key = routing_keys[queue_name]
        channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key=routing_key)

print("Queues and exchange set up successfully.")


def check_setup():
    global connection, channel, hostname, port, exchangename, exchangetype

    if not is_connection_open(connection):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port, heartbeat=3600, blocked_connection_timeout=3600))
    if channel.is_closed:
        channel = connection.channel()
        channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)


def is_connection_open(connection):
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False
