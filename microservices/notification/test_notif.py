import pika

def callback(ch, method, properties, body):
    print("Received message: %r" % body)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='notify_foodbank', exchange_type='direct')
channel.queue_declare(queue='new_food', durable=True)
channel.queue_bind(queue='new_food', exchange='notify_foodbank', routing_key='new_posting')

channel.basic_consume(queue='new_food', on_message_callback=callback, auto_ack=True)

print('Waiting for messages...')
channel.start_consuming()
