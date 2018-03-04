#!/usr/bin/env bash

cur_dir="$( cd "$(dirname "$0")" ; pwd -P )"
sudo cp ${cur_dir}/conf/darkice-ydf.cfg /etc/darkice.cfg

sudo apt-get update
sudo apt-get -y install unzip autoconf libtool libtool-bin checkinstall libssl-dev libasound2-dev \
                libmp3lame-dev libpulse-dev alsa-utils avahi-daemon mplayer
sudo apt-get install -y ffmpeg

cd /tmp
wget http://tipok.org.ua/downloads/media/aacplus/libaacplus/libaacplus-2.0.2.tar.gz
tar -xzf libaacplus-2.0.2.tar.gz
cd libaacplus-2.0.2
./autogen.sh --with-parameter-expansion-string-replace-capable-shell=/bin/bash --host=arm-unknown-linux-gnueabi \
             --enable-static
make
sudo make install
sudo ldconfig

echo "deb-src http://archive.raspbian.org/raspbian jessie main contrib non-free rpi" | sudo tee --append /etc/apt/sources.list
sudo apt-get update

cd /tmp
apt-get source darkice
cd darkice-1.2
./configure --with-aacplus --with-aacplus-prefix=/usr/local \
            --with-pulseaudio --with-pulseaudio-prefix=/usr/lib/arm-linux-gnueabihf \
            --with-lame --with-lame-prefix=/usr/lib/arm-linux-gnueabihf \
            --with-alsa --with-alsa-prefix=/usr/lib/arm-linux-gnueabihf \
            --with-jack --with-jack-prefix=/usr/lib/arm-linux-gnueabihf
make
sudo make install
cd ..
sudo rm -r darkice-1.2

sudo service darkice start

sudo sed -i -- "s/^exit 0/amixer cset numid=3 1\\nexit 0/g" /etc/rc.local
sudo sed -i -- "s/^exit 0/darkice \&\\nexit 0/g" /etc/rc.local
sudo sed -i -- "s/^exit 0/(mplayer http:\/\/54.89.215.33:8000\/echoberry-yul)\&\\nexit 0/g" /etc/rc.local
