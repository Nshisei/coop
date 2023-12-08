# -*- coding: utf-8 -*-

from __future__ import print_function
import pika
from ctypes import *
from dotenv import load_dotenv
import os
import json
from connect_db import get_user
load_dotenv()
# データベースの設定
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PW'),
    'database': os.getenv('DB_NAME')
}

def send_nfc_data(nfc):
    # RabbitMQに接続
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    if isinstance(nfc, str):
        # NFCデータが文字列であることを確認し、バイト型に変換
        channel.queue_declare(queue='nfc_registration')
        nfc_bytes = nfc.encode()
        channel.basic_publish(exchange='', routing_key='nfc_registration', body=nfc_bytes)
    else:
        # NFCデータがすでにバイト型であるか、またはJSON形式に変換可能なオブジェクトである場合
        channel.queue_declare(queue='nfc_queue')
        nfc_bytes = json.dumps(nfc).encode()
        channel.basic_publish(exchange='', routing_key='nfc_queue', body=nfc_bytes)

    print(f" [x] Sent NFC data: {nfc_bytes}")
    connection.close()


# libpafe.hの77行目で定義
FELICA_POLLING_ANY = 0xffff

if __name__ == '__main__':

    libpafe = cdll.LoadLibrary("/usr/local/lib/libpafe.so")

    libpafe.pasori_open.restype = c_void_p
    pasori = libpafe.pasori_open()
    before = 0

    while True:
        # 入力の受付
        libpafe.pasori_init(pasori)
        libpafe.felica_polling.restype = c_void_p
        felica = libpafe.felica_polling(pasori, FELICA_POLLING_ANY, 0, 0)
        idm = c_ulonglong()
        libpafe.felica_get_idm.restype = c_void_p
        libpafe.felica_get_idm(felica, byref(idm))
        if idm.value != 0 and idm.value != before:
            # IDmは16進表記
            user_info = get_user("%016X" % idm.value)
            send_nfc_data(user_info)
    # # READMEより、felica_polling()使用後はfree()を使う
    # # なお、freeは自動的にライブラリに入っているもよう
    # libpafe.free(felica)

    # libpafe.pasori_close(pasori)
    