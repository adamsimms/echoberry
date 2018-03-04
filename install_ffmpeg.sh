#!/usr/bin/env bash

echo "Installing FFMPEG now..."

cd /tmp
git clone git://git.videolan.org/x264
cd x264
./configure --host=arm-unknown-linux-gnueabi --enable-static --disable-opencl
make
sudo make install

sudo apt-get install libmp3lame-dev

cd /tmp
git clone https://github.com/FFmpeg/FFmpeg.git
cd FFmpeg
./configure --arch=armel --target-os=linux --enable-gpl --enable-libx264 --enable-nonfree --enable-libmp3lame
make -j4
sudo make install
