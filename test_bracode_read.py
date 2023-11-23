import evdev
from evdev import InputDevice, categorize, ecodes

# 利用可能なデバイスをリストアップ
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(device.path, device.name, device.phys)

# バーコードリーダーのデバイスパスを設定 (例: /dev/input/event0)
barcode_scanner_path = "/dev/input/event1"

# バーコードリーダーデバイスを開く
barcode_scanner = InputDevice(barcode_scanner_path)

print("バーコードリーダーを監視中...")

# バーコードデータを収集するための変数
barcode_data = ''

try:
    for event in barcode_scanner.read_loop():
        if event.type == ecodes.EV_KEY:
            data = categorize(event)
            if data.keystate == 1:  # Down events only
                if data.keycode == 'KEY_ENTER':
                    # Enterキーが押されたらバーコードデータを表示してリセット
                    print("読み取ったバーコード:", barcode_data)
                    barcode_data = ''
except KeyboardInterrupt:
    print("プログラムを終了します。")
