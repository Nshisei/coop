from ctypes import *
import multiprocessing
from dotenv import load_dotenv
import os
from utils.connect_db import get_user
load_dotenv()
# データベースの設定
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PW'),
    'database': os.getenv('DB_NAME')
}

FELICA_POLLING_ANY = 0xffff

def nfc_process(queue):
    """ NFC リーダーを監視し、Queue に送信 """
    
    libpafe = cdll.LoadLibrary("/usr/local/lib/libpafe.so")
    libpafe.pasori_open.restype = c_void_p
    pasori = libpafe.pasori_open()
    before = 0

    while True:
        try:
            libpafe.pasori_init(pasori)
            libpafe.felica_polling.restype = c_void_p
            felica = libpafe.felica_polling(pasori, FELICA_POLLING_ANY, 0, 0)
            idm = c_ulonglong()
            libpafe.felica_get_idm.restype = c_void_p
            libpafe.felica_get_idm(felica, byref(idm))

            if idm.value != 0 and idm.value != before:
                # IDmを16進表記
                user_info = get_user("%016X" % idm.value)
                queue.put(user_info)  # Queue に送信
                before = idm.value  # 直前の IDm を保存して重複送信を防ぐ

        except KeyboardInterrupt:
            print("NFC 監視プロセスを終了します")
            break



if __name__ == '__main__':
    nfc_queue = multiprocessing.Queue()
    nfc_reader(nfc_queue)
