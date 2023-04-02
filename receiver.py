
import pika

def callback(ch, method, properties, body):
    print(f"Received message: {body}")

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='experiment', exchange_type='direct')
channel.queue_declare(queue='my_queue')
channel.queue_bind(queue='my_queue', exchange='experiment', routing_key='new_route')

channel.basic_consume(queue='my_queue', on_message_callback=callback, auto_ack=True)

print('Waiting for messages...')
channel.start_consuming()
