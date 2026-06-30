#!/usr/bin/env bash
# Legacy script for building ffmpeg from source on older Raspberry Pi OS releases.
# Prefer `apt-get install ffmpeg` (used by scripts/install.sh) on modern systems.

set -euo pipefail

echo "Installing FFmpeg from source (legacy)..."

cd /tmp
git clone https://github.com/FFmpeg/FFmpeg.git
cd FFmpeg
git clone https://github.com/FFmpeg/x264.git

cd x264
./configure --host=arm-unknown-linux-gnueabi --enable-static --disable-opencl
make
sudo make install

sudo apt-get install -y libmp3lame-dev

cd /tmp/FFmpeg
./configure --arch=armel --target-os=linux --enable-gpl --enable-libx264 --enable-nonfree --enable-libmp3lame
make -j"$(nproc)"
sudo make install

echo "FFmpeg installed from source."
