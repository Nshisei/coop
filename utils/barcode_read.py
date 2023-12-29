import evdev
from evdev import InputDevice, categorize, ecodes
import pika
import mysql.connector
from connect_db import get_items
from dotenv import load_dotenv
import os
import json

def send_barcode_data(data):
    # RabbitMQに接続
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # NFCデータが文字列であることを確認し、バイト型に変換
    if isinstance(data, str):
        data_bytes = data.encode()
        channel.queue_declare(queue='barcode_registration')
        data_bytes = data.encode()
        channel.basic_publish(exchange='', routing_key='barcode_registration', body=data_bytes)
    else:
        # キューを宣言
        channel.queue_declare(queue='barcode_queue')
        data_bytes = json.dumps(data).encode()
        channel.basic_publish(exchange='', routing_key='barcode_queue', body=data_bytes)
    print(f" [x] Sent Barcode data: {data}")

# 利用可能なデバイスをリストアップ
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(device.path, device.name, device.phys)
    if 'Barcode' in device.name:
        # バーコードリーダーのデバイスパスを設定 (例: /dev/input/event0)
        barcode_scanner_path = device.path

# バーコードリーダーデバイスを開く
barcode_scanner = InputDevice(barcode_scanner_path)

print("バーコードリーダーを監視中...")

# バーコードデータを収集するための変数
barcode_data = ''

while True:
    for event in barcode_scanner.read_loop():
        if event.type == ecodes.EV_KEY:
            data = categorize(event)
            if data.keystate == 1:  # Down events only
                if data.keycode == 'KEY_ENTER':
                    # Enterキーが押されたらバーコードデータを表示してリセット
                    item_info = get_items(barcode_data)
                    send_barcode_data(item_info)
                    print("読み取ったバーコード:", barcode_data)
                    barcode_data = ''
                else:
                    # バーコードデータに文字を追加
                    barcode_data += data.keycode.lstrip('KEY_')
