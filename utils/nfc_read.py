from ctypes import *
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
import asyncio

async def nfc_reader(nfc_queue):
    FELICA_POLLING_ANY = 0xffff
    libpafe = cdll.LoadLibrary("/usr/local/lib/libpafe.so")

    libpafe.pasori_open.restype = c_void_p
    pasori = libpafe.pasori_open()
    before = 0
    loop = asyncio.get_event_loop()

    while True:
        await loop.run_in_executor(None, libpafe.pasori_init, pasori)
        libpafe.felica_polling.restype = c_void_p
        felica = await libpafe.felica_polling(pasori, FELICA_POLLING_ANY, 0, 0)
        idm = c_ulonglong()
        libpafe.felica_get_idm.restype = c_void_p
        await loop.run_in_executor(None, libpafe.felica_get_idm, felica, byref(idm))
        if idm.value != 0 and idm.value != before:
            user_info = get_user("%016X" % idm.value)
            print(user_info)
            await fc_queue.put(user_info)
    # libpafe.pasori_close(pasori)
    

if __name__ == '__main__':
    nfc_queue = multiprocessing.Queue()
    nfc_reader(nfc_queue)
