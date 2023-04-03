import pika
from os import environ ###


hostname = environ.get('rabbit_host') or 'localhost' 
port = environ.get('rabbit_port') or 5672 
# connect to the broker and set up a communication channel in the connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=hostname, port=port,
        heartbeat=3600, blocked_connection_timeout=3600, # these parameters to prolong the expiration time (in seconds) of the connection
))
channel = connection.channel()

exchangename= "notify_foodbank" 
exchangetype= "direct" 
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)
    

#new posting from postSurplus
queue_name = 'new_food' #?##
channel.queue_declare(queue=queue_name, durable=True) 
routing_key = 'new_posting'
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key=routing_key) 


exchangename= "notify_driver" 
exchangetype= "direct" 
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)

queue_name = 'new_order' 
channel.queue_declare(queue=queue_name, durable=True)
routing_key = 'new_order'
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key=routing_key) 

# Set up the queue to receive notifications about new posting to foodbank
# notify driver there is new order
exchangename= "restaurant_foodbankorder" #?##
exchangetype= "direct" #?##
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)

#Notify resto that their post is ordered
queue_name = 'foodbankorder' #?##
channel.queue_declare(queue=queue_name, durable=True)
routing_key = 'foodbankorder'
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key=routing_key) 


# Set up the queue to receive notifications about new posting to foodbank
# notify driver there is new order
exchangename= "driver_order" #?##
exchangetype= "direct" #?##
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)

queue_name = 'driver' #?##
channel.queue_declare(queue=queue_name, durable=True)
routing_key = 'driver'
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key=routing_key) 

# Set up the queue to receive notifications about new posting to foodbank
# notify driver there is new order
exchangename= "driver_deliver" #?##
exchangetype= "direct" #?##
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)

queue_name = 'driver' #?##
channel.queue_declare(queue=queue_name, durable=True)
routing_key = 'driver'
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key=routing_key) 


"""
This function in this module sets up a connection and a channel to a local AMQP broker,
and declares a 'topic' exchange to be used by the microservices in the solution.
"""
def check_setup():
    # The shared connection and channel created when the module is imported may be expired, 
    # timed out, disconnected by the broker or a client;
    # - re-establish the connection/channel is they have been closed
    global connection, channel, hostname, port, exchangename, exchangetype

    if not is_connection_open(connection):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port, heartbeat=3600, blocked_connection_timeout=3600))
    if channel.is_closed:
        channel = connection.channel()
        channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True) ###


def is_connection_open(connection):
    # For a BlockingConnection in AMQP clients,
    # when an exception happens when an action is performed,
    # it likely indicates a broken connection.
    # So, the code below actively calls a method in the 'connection' to check if an exception happens
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False
