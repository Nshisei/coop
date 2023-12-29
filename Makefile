sudo apt-get install -y libusb-dev
sudo apt install libpcsclite-dev
git clone https://github.com/rfujita/libpafe.git
cd libpafe
./configure
make
sudo make install

sudo touch /etc/udev/pasori.rules
sudo chmod 777 /etc/udev/pasori.rules

test='ACTION!="add", GOTO="pasori_rules_end"
SUBSYSTEM=="usb_device", GOTO="pasori_rules_start"
SUBSYSTEM!="usb", GOTO="pasori_rules_end"
LABEL="pasori_rules_start"

ATTRS{idVendor}=="054c", ATTRS{idProduct}=="01bb", MODE="0664", GROUP="plugdev"
ATTRS{idVendor}=="054c", ATTRS{idProduct}=="02e1", MODE="0664", GROUP="plugdev"

LABEL="pasori_rules_end"'


sudo cat "$text" > /etc/udev/pasori.rules

cd /etc/udev/rules.d
sudo ln -s ../pasori.rules 010_pasori.rules

test='blacklist pn533
blacklist nfc'
sudo echo "$text" >> /etc/modprobe.d/pasori.conf

# sudo reboot

# RabbitMQの処理
sudo apt-get install rabbitmq-server
sudo service rabbitmq-server start

