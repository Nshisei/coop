from flask import Flask, render_template
from flask_socketio import SocketIO
import pika
import eventlet
import json

# Pythonの標準ライブラリを非同期I/Oに対応するように書き換えます。
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Create a function to handle incoming RabbitMQ messages
def on_rabbitmq_message(body):
    # When a message is received, broadcast it to all connected WebSocket clients
    data = json.loads(body)
    print(data)

# Define a function to set up RabbitMQ connection and channel
def setup_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='barcode_queue')
    channel.queue_declare(queue='nfc_queue')
    
    # Set up consumers
    for queue_name in ['barcode_queue', 'nfc_queue']:
        channel.basic_consume(queue=queue_name, on_message_callback=lambda ch, method, properties, body: on_rabbitmq_message(body), auto_ack=True)
    return channel

# Create a separate thread for the RabbitMQ consumer
def rabbitmq_consumer_thread():
    channel = setup_rabbitmq()
    channel.start_consuming()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    eventlet.spawn(rabbitmq_consumer_thread)
