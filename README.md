# 購買システム
研究室の購買システム

# 実行の様子
![Gif](https://github.com/Nshisei/coop/blob/2e7d617b1e1d4e0eeea11a975ac652fee0e537f2/images/%E5%88%A9%E7%94%A8%E5%8B%95%E7%94%BB.gif)


## 購入処理
1. NFCカードをかざして、購入者情報を読み取る
2. 商品のバーコードをかざし、商品情報を読み取る(1,2は順不同)
3. キャンセルする場合は赤いボタンをクリック/そうでなければ購入ボタンをクリック
4. 購入確定ポップアップが出たら完了

* 商品 or ユーザー情報を入力する前に購入ボタンを押してもエラーポップアップが表示されるだけで購入処理は走らない

## 新規ユーザー登録
1. 新規ユーザー登録画面に移動
2. 新規のNFCカードをかざして、NFC　IDを読み取る
3. 名前と学年を入力
4. 完了しました。という文字列が表示されたら終了

## 新規商品登録
1. 新規商品登録画面を表示
2. 新規商品のバーコードを読み取る
3. 新規商品の名前、金額、在庫数、商品種別を入力
4. 完了しました。という文字列が表示されたら終了

## 画面一覧
<details>
  <summary>HOME画面</summary>
<img src="https://github.com/Nshisei/coop/blob/d16ccee809ffb65f908b9ee60fe8e67d466af98d/images/HOME%E7%94%BB%E9%9D%A2.png">
</details>
<details>
  <summary>商品一覧</summary>
<img src="https://github.com/Nshisei/coop/blob/d16ccee809ffb65f908b9ee60fe8e67d466af98d/images/%E5%95%86%E5%93%81%E4%B8%80%E8%A6%A7%E7%94%BB%E9%9D%A2.png">
</details>
<details>
  <summary>新規ユーザー登録</summary>
<img src="https://github.com/Nshisei/coop/blob/d16ccee809ffb65f908b9ee60fe8e67d466af98d/images/%E6%96%B0%E8%A6%8F%E7%99%BB%E9%8C%B2%E7%94%BB%E9%9D%A2.png">
</details>
<details>
  <summary>新規商品登録</summary>
<img src="https://github.com/Nshisei/coop/blob/d16ccee809ffb65f908b9ee60fe8e67d466af98d/images/%E5%95%86%E5%93%81%E7%99%BB%E9%8C%B2%E7%94%BB%E9%9D%A2.png">
</details>

# 実行環境

* [Raspberry Pi 3 model B+](https://raspida.com/rpi3b-plus)
* [Sony FeliCa RC-S330](https://www.sony.jp/cat/products/RC-S330/)
* [ZEBEX Barcode Scanner](https://www.zebex.com/jp/product/index/75/Z-3010)

ラズパイOS: Raspbian GNU/Linux 11 (bullseye)
[イメージダウンロードリンク](https://downloads.raspberrypi.org/raspios_armhf/images/raspios_armhf-2022-01-28/)
`2022-01-28-raspios-bullseye-armhf.zip`を選択
Python 3.9.2


# 概要図&使用技術
<img src="https://github.com/Nshisei/coop/blob/d16ccee809ffb65f908b9ee60fe8e67d466af98d/images/%E6%A6%82%E8%A6%81%E5%9B%B3.png">

## RabittMQ
[RabbitMQ徹底解説: Qiita](https://qiita.com/haystacker/items/52e2fb7c5903c3f3bbf9)
情報読み取り側(バーコード読み取りプログラム, NFC読み取りプログラム)とサーバープログラムをそれぞれの間で非同期通信を行うために用いる。
[MQ（メッセージキューイング）](https://note.com/fz5050/n/na46f3fbe88f9)という仕組みを用いることで情報を読み取ったタイミングでデータを送信し、受信側は適当なタイミングで受信するということを実現している。これは今回のようなマイクロサービスアーキテクチャに適している。

## websocket
[WebSocketについて調べてみた。: Qiita](https://qiita.com/south37/items/6f92d4268fe676347160)
Webにおいての双方向通信を行う仕組み。サーバー側からの商品やユーザ情報をブラウザ側に表示、ブラウザ側からの購入情報のPostを高速で実行するために用いる。
特に、情報の読み取りが発生し、サーバー側からブラウザ側に情報のアップデートが必要になった時にHTTPポーリングせずにブラウザ側が情報を受け取る & 更新なしでJavascriptでこれらの操作を実行できるようにするために採用している。

## flask
Pythonを用いてWebアプリケーションを実現するための軽量なフレームワーク.
[Flask](https://msiz07-flask-docs-ja.readthedocs.io/ja/latest/)
Djangoに比べて軽量であるためラズパイ上で実現するのに適している。

# ER図
<img src="https://github.com/Nshisei/coop/blob/d16ccee809ffb65f908b9ee60fe8e67d466af98d/images/ER%E5%9B%B3.png">

# 実行環境構築ステップ

## 1. libpafeのインストール
FeliCaを実行できるようにするためのライブラリをインストールする。基本的にはlibpafeの[README](https://github.com/rfujita/libpafe)を参考に実行する。

### 1.a USBデバイスを扱うプログラムをOSを意識せずに扱えるライブラリをインストール
```
$ sudo apt-get install -y libusb-dev
$ sudo apt install libpcsclite-dev
```
### 1.b libpafeインストール
```
$ git clone https://github.com/rfujita/libpafe.git
$ cd libpafe
$ ./configure
$ make
$ sudo make install
```
### 1.c udev の設定
```
$ sudo touch /etc/udev/pasori.rules
$ sudo chmod 777 /etc/udev/pasori.rules
$ sudo vim /etc/udev/pasori.rules
```
下記内容を記述
```
ACTION!="add", GOTO="pasori_rules_end"
SUBSYSTEM=="usb_device", GOTO="pasori_rules_start"
SUBSYSTEM!="usb", GOTO="pasori_rules_end"
LABEL="pasori_rules_start"

ATTRS{idVendor}=="054c", ATTRS{idProduct}=="01bb", MODE="0664", GROUP="plugdev"
ATTRS{idVendor}=="054c", ATTRS{idProduct}=="02e1", MODE="0664", GROUP="plugdev"

LABEL="pasori_rules_end"
```

```
$ cd /etc/udev/rules.d
$ sudo ln -s ../pasori.rules 010_pasori.rules
$ sudo vim /etc/modprobe.d/pasori.conf
```
下記内容を記述
```
blacklist pn533
blacklist nfc
```
ここまで行ったあと、再起動
```
sudo reboot
```

## 2. pythonライブラリのインストール
```
$ pip3 install -r requirments.txt
```

## 3. RabbitMQのインストール
```
sudo apt-get install rabbitmq-server
sudo service rabbitmq-server start
```

## 4. Apacheインストール
[参考サイト1](https://sqr.hateblo.jp/entry/2023/05/03/135438)
[参考サイト2](https://qiita.com/nabion/items/88528ad5eaf6fdad992e)
Apacheのインストール
```
sudo apt-get install apache2
```
WSGIのインストール (requirement.txtをインストールしていれば不要)
```
sudu pip3 install mod-wsgi
```
実行環境のリンクを張る
```
sudo ln -sT ~/coop  /var/www/html/coop
```

Apacheディレクティブの修正
```
$ sudo vim /etc/apache2/sites-enabled/000-default.conf
<VirtualHost *:80>
        ServerName 192.168.2.198
        WSGIDaemonProcess coop threads=5
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html/coop
        WSGIScriptAlias / /var/www/html/coop/app.wsgi
        LoadModule wsgi_module /home/srv-admin/.local/lib/python3.9/site-packages/mod_wsgi/server/mod_wsgi-py39.cpython-39-arm-linux-gnueabihf.so
        <Directory "/var/www/html/coop">
             WSGIProcessGroup %{GLOBAL}
             WSGIApplicationGroup %{RESOURCE}
             WSGIScriptReloading On
             Require all granted
        </Directory>
</VirtualHost>
```
モジュールの実行権限の付与
```
sudo chmod 777 /home/srv-admin/.local/lib/python3.9/site-packages/mod_wsgi/server/mod_wsgi-py39.cpython-39-arm-linux-gnueabihf.so
```
```
$ sudo vim /etc/apache2/apache2.conf
<Directory /var/www/html/coop>
        Options FollowSymLinks
        AllowOverride None
        Require all granted
</Directory>
```
再起動
```
sudo systemctl restart apache2
```
補足
何か問題が起こったときは以下のコマンドでエラーメッセージを読む
```
# Apacheが起動しない場合
systemctl status apache2
# ApacheとFlaskの連携がうまくいかない場合
tail -n 20 /var/log/apache2/error.log
```
