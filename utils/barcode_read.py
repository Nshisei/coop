import evdev
from evdev import InputDevice, categorize, ecodes
import mysql.connector
from utils.connect_db import get_items
from dotenv import load_dotenv
import os
import asyncio


async def barcode_reader(barcode_queue):
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        print(device.path, device.name, device.phys)
        if 'Barcode' in device.name:
            # バーコードリーダーのデバイスパスを設定 (例: /dev/input/event0)
            barcode_scanner_path = device.path
    if not barcode_scanner_path:
        raise Exception("Barcode scanner not found")


    # バーコードリーダーデバイスを開く
    barcode_scanner = InputDevice(barcode_scanner_path)
    print("バーコードリーダーを監視中...")
    # バーコードデータを収集するための変数
    barcode_data = ''
    loop = asyncio.get_event_loop()
    while True:
        # 非同期でイベントを待機
        events = await loop.run_in_executor(None, barcode_scanner.read)  # 非同期にデバイス読み取り
        for event in events:
            if event.type == ecodes.EV_KEY:
                data = categorize(event)
                if data.keystate == 1:  # Down events only
                    if data.keycode == 'KEY_ENTER':
                        # Enterキーが押されたらバーコードデータを表示してリセット
                        item_info = get_items(barcode_data)
                        await barcode_queue.put(item_info) # キューに非同期でデータを送信
                        print("読み取ったバーコード:", barcode_data)
                        barcode_data = ''
                    else:
                        # バーコードデータに文字を追加
                        barcode_data += data.keycode.lstrip('KEY_')
