from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import pika
import eventlet
from eventlet import wsgi
import json
from utils.connect_db import insert_order, update_balance

# Pythonの標準ライブラリを非同期I/Oに対応するように書き換えます。
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# --------------------Connect to BARCODE and NFCREAD through RabbitMQ-----------------------------------
# Create a function to handle incoming RabbitMQ messages
def on_rabbitmq_message_item(body):
    # When a message is received, broadcast it to all connected WebSocket clients
    data = json.loads(body)
    print(data)
    socketio.emit('item_added', {'item_id': data[0], 'itemName': data[1], 'itemPrice': data[2]})

# Create a function to handle incoming RabbitMQ messages
def on_rabbitmq_message_user(body):
    # When a message is received, broadcast it to all connected WebSocket clients
    data = json.loads(body)
    print(data)
    socketio.emit('user_info', {'user_id': data[0], 'userName': data[1], 'nfc_id': data[2], 'grade': data[3], 'balance': data[4]})


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

# --------------------DB -----------------------------------------------------------------------------------

# 購入処理が終わったらブラウザ側に購入処理が終わったことを通知する
@socketio.on('confirm_purchase')
def confirm_purchase(data):
    print('Received data:', data)
    data = dict(data)
    insert_order(data)
    update_balance(data)
    socketio.emit('purchase_confirmed', {'flag': 'ok'})

# --------------------Page--------------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    eventlet.spawn(rabbitmq_consumer_thread)
    # socketio.run(app, debug=True)
    wsgi.server(eventlet.listen(("127.0.0.1", 8000)), app)