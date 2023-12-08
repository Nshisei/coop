# 購買システム
下西研究室の購買システム

# 構築ステップ


## Apache
Apacheのインストール
https://gb-j.com/column/ubuntu-flask/
```
sudo apt-get install apache2
```
サービスの再起動
```
sudo systemctl restart apache2
```
wsgi
```
sudo apt-get install libapache2-mod-wsgi-py3
```
sudo ln -sT ~/coop  /var/www/html/coop

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