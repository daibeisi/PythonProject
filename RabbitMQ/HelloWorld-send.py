#!/usr/bin/env python
import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='', port=7,
                              credentials=pika.PlainCredentials('', '')))
channel1 = connection.channel()

channel1.queue_declare(queue='task_queue', durable=True, exclusive=True)
channel2 = connection.channel()

channel2.queue_declare(queue='task_queue', durable=True, exclusive=True)

message = ' '.join(sys.argv[1:]) or "Hello World!5"
channel1.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message.encode(),
    properties=pika.BasicProperties(
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
    ))
print(" [1] Sent %r" % message)
channel2.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message.encode(),
    properties=pika.BasicProperties(
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
    ))
print(" [2] Sent %r" % message)
connection.close()

