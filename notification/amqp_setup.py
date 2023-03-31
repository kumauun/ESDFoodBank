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
        'restaurant_driver_pickup'
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
