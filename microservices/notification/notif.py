import pika
import json

RABBITMQ_HOST = 'rabbitmq'

with pika.BlockingConnection(pika.ConnectionParameters('rabbitmq')) as connection:
    channel = connection.channel()

    #sms function nannti edit twilio 
    def callback(ch, method, properties, body):
        print(f"Received message: {body}")

    #notif ke foodbank ada new posting
    channel.exchange_declare(exchange='notify_foodbank', exchange_type='direct')
    channel.queue_declare(queue='new_food', durable=True)
    channel.queue_bind(queue='new_food', exchange='notify_foodbank', routing_key='new_posting')
    channel.basic_consume(queue='new_food', on_message_callback=callback, auto_ack=True)


    #notif ke driver ada new order
    channel.exchange_declare(exchange='notify_driver', exchange_type='direct')
    channel.queue_declare(queue='new_order', durable=True)
    channel.queue_bind(queue='new_order', exchange='notify_driver', routing_key='new_order')
    channel.basic_consume(queue='new_order', on_message_callback=callback, auto_ack=True)

    #notif ke restoran pas ada foodbank new posting
    channel.exchange_declare(exchange='restaurant_foodbankorder', exchange_type='direct')
    channel.queue_declare(queue='foodbankorder', durable=True)
    channel.queue_bind(queue='foodbankorder', exchange='restaurant_foodbankorder', routing_key='foodbankorder')
    channel.basic_consume(queue='foodbankorder', on_message_callback=callback, auto_ack=True)

    #notif driver ngeaccept order 

    channel.exchange_declare(exchange='driver_order', exchange_type='direct')
    channel.queue_declare(queue='driver', durable=True)
    channel.queue_bind(queue='driver', exchange='driver_order', routing_key='driver')
    channel.basic_consume(queue='driver', on_message_callback=callback, auto_ack=True)

    #notif driver delivered order
    channel.exchange_declare(exchange='driver_deliver', exchange_type='direct')
    channel.queue_declare(queue='driver', durable=True)
    channel.queue_bind(queue='driver', exchange='driver_deliver', routing_key='driver')
    channel.basic_consume(queue='driver', on_message_callback=callback, auto_ack=True)
    
    
'''




Traceback (most recent call last):
  File "/usr/src/app/./notif.py", line 6, in <module>
    with pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST)) as connection:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/pika/adapters/blocking_connection.py", line 360, in __init__
    self._impl = self._create_connection(parameters, _impl_class)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/pika/adapters/blocking_connection.py", line 451, in _create_connection
    raise self._reap_last_connection_workflow_error(error)
pika.exceptions.AMQPConnectionError





'''