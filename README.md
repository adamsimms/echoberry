# RPi Echo

https://www.figma.com/file/Qq94FUIBFmaFRzEGjnB09grI/Echo?node-id=1%3A2


## Components

- Raspberry Pi 3

- USB Mini Microphone
    
    https://www.amazon.co.uk/Richera-Microphone-Notebook-Recognition-Software/dp/B01FJWO5K4/ref=pd_cp_107_3?_encoding=UTF8&psc=1&refRID=0F4J0PPSJHKGHPY9M527

- Magnetic Switch
    
    https://www.adafruit.com/product/375
    
    Note: Connect this switch to `GPIO4` & `GND`

## Setup Audio Streaming Server.

1. Install **Icecast2**

       sudo apt-get install build-essential libxslt-dev libogg-dev libvorbis-dev
       git clone https://github.com/karlheyes/icecast-kh
       cd icecast-kh
       ./configure
       make
       sudo make install

2. Configure **Icecast2**
   
       sudo cp conf/icecast.xml /usr/local/etc/icecast.xml

3. Start **Icecast2**

       icecast -c /usr/local/etc/icecast.xml

**NOTE:** 

- URL: http://54.89.215.33:8000/admin.html
    * Username: admin
    * Password: MyAdminPassword


## Setup Raspberry Pi.

- Install Raspbian **Jessie Lite** from [here](http://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2017-07-05/2017-07-05-raspbian-jessie-lite.zip)

- Clone this repo
    
        cd ~
        https://github.com/adamsimms/echoberry
        cd echoberry

### EchoBerry-YUL @Montreal - Location #1
    
    cd ~/echoberry
    bash install_yul.sh

### EchoBerry-YDF @NewFoundLand - Location #2
        
    cd ~/echoberry
    bash install_ydf.sh

## Stream audio to the server.

- YUL
        
        cd /home/pi/echoberry
        ffmpeg -ac 1 -re -f alsa -i hw:1,0 -re -i sounds/forest_reduced15db.mp3 -filter_complex amerge=inputs=2 -f mp3 icecast://source:MyAdminPassword@54.89.215.33:8000/echoberry-yul

- YDF
        
        sudo darkice


## Listen to Stream

- YUL
    
        mplayer http://54.89.215.33:8000/echoberry-yul
    
    *NOTE* If you want to hear with USB headset, use this:
        
        mplayer -ao alsa:device=hw=1.0 http://54.89.215.33:8000/echoberry-yul

- YDF
    
        mplayer http://54.89.215.33:8000/echoberry-ydf

Now, reboot!
