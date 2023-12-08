# 購買システム
下西研究室の購買システム

# 構築ステップ


## Apacheインストール
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



# 旧バージョン

```
sudo apt-get install php
sudo apt-get install php-mysqli
sudo service apache2 restart

ls /usr/lib/php/20190902/
sudo vim /etc/php/7.4/apache2/php.ini 
extension=mysqli
extention=
sudo chmod 777 /usr/lib/php/20190902/mysqli.so 
sudo apt-get install ruby-dev
gem install mysql2

```