import datetime
import threading
import os
import sys
import subprocess
from mutagen.mp3 import MP3
import time
from utils import kill_process_by_name
import RPi.GPIO as GPIO
from constant import *


cur_dir = os.path.dirname(os.path.realpath(__file__))
ring_path = os.path.join(cur_dir, RING_FILE)

CMD = 'ffmpeg -ac 1 -re -f alsa -i hw:1,0 -re -i {} -filter_complex amerge=inputs=2 -f mp3 ' \
      'icecast://source:{}@54.89.215.33:8000/echoberry-yul'.format(FOREST_SOUND_FILE, ICECAST_PASSWORD)


class RPiEcho(threading.Thread):

    state = 'idle'

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            time.sleep(1)

    def on_switch_event(self, *args):
        if GPIO.input(SWITCH_PIN):
            self.on_switch_opened()
        else:
            self.on_switch_closed()

    def on_switch_opened(self):
        print('>>> {}:: Switch is opened!'.format(datetime.datetime.now()))
        if self.state == 'idle':
            self.state = 'active'
            # Play the ring audio
            subprocess.Popen('mplayer -ao alsa:device=hw=1.0 {}'.format(ring_path), shell=True)
            audio = MP3(ring_path)
            time.sleep(audio.info.length)
            kill_process_by_name('mplayer')
            # Start streaming
            print(">>> {}:: Audio Stream - {}".format(datetime.datetime.now(), CMD))
            subprocess.Popen(CMD, shell=True)
            subprocess.Popen('mplayer -ao alsa:device=hw=1.0 http://54.89.215.33:8000/echoberry-ydf', shell=True)

    def on_switch_closed(self):
        print('>>> {}:: Switch is closed.'.format(datetime.datetime.now()))
        self.state = 'idle'
        kill_process_by_name('omxplayer')
        kill_process_by_name('ffmpeg')
        kill_process_by_name('mplayer')


if __name__ == '__main__':

    if not sys.version_info >= (3, 0):
        sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x. Please execute with `python3 main.py`\n")
        sys.exit(1)

    if os.getuid() != 0:
        sys.stdout.write("You need to have root privileges to run this service.\n Please try with `sudo`")
        sys.exit(1)

    # Switch the audio output to analogue
    os.system('amixer cset numid=3 1')

    echo = RPiEcho()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(SWITCH_PIN, GPIO.BOTH, callback=echo.on_switch_event, bouncetime=200)

    echo.start()
