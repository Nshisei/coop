import evdev
from evdev import InputDevice, categorize, ecodes
from utils.connect_db import get_items
import os
import multiprocessing
import time

def barcode_process(queue):
    """ バーコードリーダーの入力を監視し、Queue に送信 """
    
    # 利用可能なデバイスをリストアップ
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    barcode_scanner = None

    for device in devices:
        print(device.path, device.name, device.phys)
        if 'Barcode' in device.name:
            barcode_scanner = InputDevice(device.path)
            print(f"バーコードリーダーを監視中: {device.path}")
            break

    if barcode_scanner is None:
        print("バーコードリーダーが見つかりません")
        return

    barcode_data = ''
    while True:
        for event in barcode_scanner.read_loop():
            if event.type == ecodes.EV_KEY:
                data = categorize(event)
                if data.keystate == 1:  # Down events only
                    if data.keycode == 'KEY_ENTER':
                        # Enterキーが押されたらバーコードデータを表示してリセット
                        item_info = get_items(barcode_data)
                        queue.put(item_info)  # Queue に送信
                        print("読み取ったバーコード:", barcode_data)
                        barcode_data = ''
                    else:
                        # バーコードデータに文字を追加
                        barcode_data += data.keycode.lstrip('KEY_')
