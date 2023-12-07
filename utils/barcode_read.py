import evdev
from evdev import InputDevice, categorize, ecodes
import pika
import mysql.connector
from connect_db import get_items
from dotenv import load_dotenv
import os
import json

load_dotenv()
# データベースの設定
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PW'),
    'database': os.getenv('DB_NAME')
}

# RabbitMQに接続
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# キューを宣言
channel.queue_declare(queue='barcode_queue')

def send_barcode_data(data):
    # NFCデータが文字列であることを確認し、バイト型に変換
    if isinstance(data, str):
        data_bytes = data.encode()
    else:
        # NFCデータがすでにバイト型であるか、またはJSON形式に変換可能なオブジェクトである場合
        data_bytes = json.dumps(data).encode()
    
    channel.basic_publish(exchange='', routing_key='barcode_queue', body=data_bytes)
    print(f" [x] Sent Barcode data: {data}")


# def get_item(barcode_data):
#     # データベースへの接続
#     db = mysql.connector.connect(**db_config)
#     cursor = db.cursor()
#     cursor.execute("USE coop")
#     db.commit()
#     cursor.execute(f"""
#                     SELECT 
#                         name
#                         , price
#                     FROM 
#                         items 
#                     WHERE 
#                         code = '{barcode_data}'
#                 """)
#     rows = cursor.fetchall()
#     if (len(rows) == 1):
#             print(rows[0])
#             return rows[0]
#     else:
#         print("err!")

# # 利用可能なデバイスをリストアップ
# devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
# for device in devices:
#     print(device.path, device.name, device.phys)

# # バーコードリーダーのデバイスパスを設定 (例: /dev/input/event0)
# barcode_scanner_path = "/dev/input/event1"

# # バーコードリーダーデバイスを開く
# barcode_scanner = InputDevice(barcode_scanner_path)

# print("バーコードリーダーを監視中...")

# # バーコードデータを収集するための変数
# barcode_data = ''

while True:
    # for event in barcode_scanner.read_loop():
    #     if event.type == ecodes.EV_KEY:
    #         data = categorize(event)
    #         if data.keystate == 1:  # Down events only
    #             if data.keycode == 'KEY_ENTER':
    #                 # Enterキーが押されたらバーコードデータを表示してリセット
    a = input()
    barcode_data = '4904872100195'
    item_info = get_items(barcode_data)
    send_barcode_data(item_info)
    print("読み取ったバーコード:", barcode_data)
    barcode_data = ''