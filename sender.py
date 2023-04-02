import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)

channel = connection.channel()
channel.exchange_declare(exchange='experiment', exchange_type='direct')
channel.queue_declare(queue='my_queue')
channel.queue_bind(queue='my_queue', exchange='experiment', routing_key='new_route')
message = 'experiment success!'
channel.basic_publish( exchange='experiment',
                      routing_key='new_route',
                      body=message)

print("Sent message:", message)

connection.close()
