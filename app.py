from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import pika
import eventlet
from eventlet import wsgi
import json

# Pythonの標準ライブラリを非同期I/Oに対応するように書き換えます。
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Create a function to handle incoming RabbitMQ messages
def on_rabbitmq_message_item(body):
    # When a message is received, broadcast it to all connected WebSocket clients
    data = json.loads(body)
    socketio.emit('item_added', {'item_id': '1', 'itemName': data[0], 'itemPrice': data[1]})
    with open('log.txt', 'a') as f:
        print(data, file=f)

# Create a function to handle incoming RabbitMQ messages
def on_rabbitmq_message_user(body):
    # When a message is received, broadcast it to all connected WebSocket clients
    data = json.loads(body)
    socketio.emit('user_info', {'user_id': '1', 'card_id': data[0], 'imbalanced': data[2]})
    with open('log.txt', 'a') as f:
        print(data, file=f)


# Define a function to set up RabbitMQ connection and channel
def setup_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='barcode_queue')
    channel.queue_declare(queue='nfc_queue')
    
    # Set up consumers
    channel.basic_consume(queue='barcode_queue', on_message_callback=lambda ch, method, properties, body: on_rabbitmq_message_item(body), auto_ack=True)
    channel.basic_consume(queue='nfc_queue', on_message_callback=lambda ch, method, properties, body: on_rabbitmq_message_user(body), auto_ack=True)
    return channel

# Create a separate thread for the RabbitMQ consumer
def rabbitmq_consumer_thread():
    channel = setup_rabbitmq()
    channel.start_consuming()

@socketio.on('confirmation')
def handle_my_event(data):
    print('Received data:', data)
    with open('log.txt', 'a') as f:
        print(data, file=f)

# 購入処理が終わったらブラウザ側に購入処理が終わったことを通知する
@socketio.on('confirm_purchase')
def handle_my_event(data):
    print('Received data:', data)
    socketio.emit('purchase_confirmed', {'flag': 'ok'})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    eventlet.spawn(rabbitmq_consumer_thread)
    # socketio.run(app, debug=True)
    wsgi.server(eventlet.listen(("127.0.0.1", 8000)), app) 