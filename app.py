import eventlet
# Pythonの標準ライブラリを非同期I/Oに対応するように書き換えます。
eventlet.monkey_patch()
from eventlet import wsgi

from flask import Flask, render_template, request
from flask_socketio import SocketIO
import pika
import json
import os
from utils.connect_db import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*",async_mode='threading')

# --------------------Connect to BARCODE and NFCREAD through RabbitMQ-----------------------------------
# Create a function to handle incoming RabbitMQ messages
def on_rabbitmq_message_item(body):
    # When a message is received, broadcast it to all connected WebSocket clients
    data = json.loads(body)
    print("item", data)
    socketio.emit('item_added', {'item_id': data[0], 'itemName': data[1], 'itemPrice': data[2]
                                 , 'stockNum': data[3], 'itemClass': data[4], 'Barcode': data[5]})

# Create a function to handle incoming RabbitMQ messages
def on_rabbitmq_message_user(body):
    # When a message is received, broadcast it to all connected WebSocket clients
    data = json.loads(body)
    print("user", data)
    socketio.emit('user_info', {'user_id': data[0], 'userName': data[1], 'nfc_id': data[2], 'grade': data[3], 'balance': data[4]})

def on_rabbitmq_message_user_registration(body):
    # When a message is received, broadcast it to all connected WebSocket clients
    data = json.loads(body)
    socketio.emit('user_nfc', {'nfc_id': body})
def on_rabbitmq_message_item_registration(body):
    # When a message is received, broadcast it to all connected WebSocket clients
    data = body.decode()
    print(data, type(data))
    socketio.emit('item_barcode', {'barcode': data})

# Define a function to set up RabbitMQ connection and channel
def setup_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='barcode_queue')
    channel.queue_declare(queue='nfc_queue')
    channel.queue_declare(queue='barcode_registration')
    channel.queue_declare(queue='nfc_registration')
    
    # Set up consumers
    channel.basic_consume(queue='barcode_queue', on_message_callback=lambda ch, method, properties, body: on_rabbitmq_message_item(body), auto_ack=True)
    channel.basic_consume(queue='nfc_queue', on_message_callback=lambda ch, method, properties, body: on_rabbitmq_message_user(body), auto_ack=True)
    channel.basic_consume(queue='barcode_registration', on_message_callback=lambda ch, method, properties, body: on_rabbitmq_message_item_registration(body), auto_ack=True)
    channel.basic_consume(queue='nfc_registration', on_message_callback=lambda ch, method, properties, body: on_rabbitmq_message_user_registration(body), auto_ack=True)
    return channel

# Create a separate thread for the RabbitMQ consumer
def rabbitmq_consumer_thread():
    channel = setup_rabbitmq()
    channel.start_consuming()

# --------------------DB -----------------------------------------------------------------------------------

# 購入処理が終わったらブラウザ側に購入処理が終わったことを通知する
PAGE_ID = "" 
@socketio.on('confirm_purchase')
def confirm_purchase(data):
    global PAGE_ID
    print('Received data:', data)
    data = dict(data)
    if data["page_id"] == PAGE_ID:
        return
    else:
        PAGE_ID = data["page_id"]
        insert_order(data)
        update_balance(data)
        socketio.emit('purchase_confirmed', {'flag': 'ok'})

# --------------------Page--------------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html', title='Coop Shopping')

@app.route('/item_list')
def item_list():
    sql_path = os.path.join(sql_dir, 'get_all_items.sql')
    rows = exec_sql_cmd(sql_path)
    return render_template('item_list.html', title='商品一覧', data=rows)


@app.route('/product_registration', methods=["GET", "POST"])
def product_registration():
    if request.method == "GET":
        return render_template('product_registration.html', title='新規商品登録', message='')
    else:
        data = dict(request.form)
        result = new_items_or_update_items(data)
        if isinstance(result, list):
            return render_template('product_registration.html', title='新規商品登録', message='商品登録ができました')
        else:
            # エラー
            return render_template('product_registration.html', title='新規商品登録', message=result)

@app.route('/user_registration', methods=["GET", "POST"])
def user_registration():
    print(request.method)
    if request.method == "GET":
        return render_template('user_registration.html', title='新規ユーザー登録', message='')
    else:
        data = dict(request.form)
        if data['nfcId'] == '' or data['userName'] == '':
            return render_template('user_registration.html', title='新規ユーザー登録', message='正しく入力してください')
        result = new_user_or_update_user(data)
        if isinstance(result, list):
            return render_template('user_registration.html', title='新規ユーザー登録', message='ユーザ登録ができました')
        else:
            # エラー
            return render_template('user_registration.html', title='新規ユーザー登録', message=result)

def create_app():
    eventlet.spawn(rabbitmq_consumer_thread)
    # socketio.run(app, debug=True)
    return app

if __name__ == '__main__':
    create_app()
    wsgi.server(eventlet.listen(("192.168.2.198", 8080)), app)
