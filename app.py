import eventlet
# Pythonの標準ライブラリを非同期I/Oに対応するように書き換えます。
eventlet.monkey_patch()
from eventlet import wsgi
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import json
import os
from utils.connect_db import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*",async_mode='threading')

# NFC & Barcode 用のキューとプロセス
nfc_queue = multiprocessing.Queue()
barcode_queue = multiprocessing.Queue()

nfc_proc = multiprocessing.Process(target=nfc_process, args=(nfc_queue,))
barcode_proc = multiprocessing.Process(target=barcode_process, args=(barcode_queue,))

def nfc_listener():
    """ NFC データを監視し、WebSocket で送信 """
    while True:
        result = nfc_queue.get()  # Queue からデータ取得 (ブロッキング)
        if isinstance(result, str):
            socketio.emit('user_nfc', {'nfc_id': result})
        else:
            user_info = result
            socketio.emit('user_info', {'user_id': user_info["id"], 'userName': user_info["name"],
                                        'nfc_id': user_info["nfc_id"], 'grade': user_info["grade"], 'balance': user_info["balance"]})

def barcode_listener():
    """ バーコードデータを監視し、WebSocket で送信 """
    while True:
        result = barcode_queue.get()  # Queue からデータ取得 (ブロッキング)
        if isinstance(result, str):
            socketio.emit('item_barcode', {'barcode': data})
        else:
            item = result
            socketio.emit('item_added', {'item_id': item["id"], 'itemName': item["name"], 'itemPrice': item["price"]
                             , 'stockNum': item["stock_num"], 'itemClass': item["class"], 'Barcode': item["code"]})

def start_monitoring():
    """ NFC & バーコードの監視プロセスを開始し、監視ループを別スレッドで実行 """
    nfc_proc.start()
    barcode_proc.start()
    eventlet.spawn(nfc_listener)
    eventlet.spawn(barcode_listener)


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
    result  = exec_sql_cmd(sql_path)
    if result["result"] == "success":
        return render_template('item_list.html', title='商品一覧', data=result["output"])
    else:
        print(result["output"])


@app.route('/product_registration', methods=["GET", "POST"])
def product_registration():
    if request.method == "GET":
        return render_template('product_registration.html', title='新規商品登録', message='')
    else:
        data = dict(request.form)
        result = new_items_or_update_items(data)
        if result["result"] == "success":
            return render_template('product_registration.html', title='新規商品登録', message='商品登録ができました')
        else:
            # エラー
            return render_template('product_registration.html', title='新規商品登録', message=result["output"])

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
        if result["result"] == "success":
            return render_template('user_registration.html', title='新規ユーザー登録', message='ユーザ登録ができました')
        else:
            # エラー
            return render_template('user_registration.html', title='新規ユーザー登録', message=result["output"])

if __name__ == '__main__':
    start_monitoring()  # NFC & バーコード監視を開始
    try:
        wsgi.server(eventlet.listen(("192.168.2.198", 8080)), app)
    finally:
        nfc_proc.terminate()  # Flask 終了時にプロセスを安全に停止
        barcode_proc.terminate()  # Flask 終了時にプロセスを安全に停止
        print("アプリ終了: NFC & バーコード監視プロセスを停止")
