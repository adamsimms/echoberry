import threading
import os
import sys
import subprocess
from mutagen.mp3 import MP3
import time
from utils import kill_process_by_name
import RPi.GPIO as GPIO
from constant import *


class RPiEcho(threading.Thread):

    state = 'idle'

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            time.sleep(1)

    def on_switch_opened(self, *args):
        if self.state == 'idle':
            self.state = 'active'
            # Play the ring audio
            subprocess.Popen('omxplayer -o local {}'.format(RING_FILE), shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            audio = MP3(RING_FILE)
            time.sleep(audio.info.length)

            # Start streaming
            subprocess.Popen('darkice', shell=True)
            subprocess.Popen('mplayer http://54.89.215.33:8000/echoberry-ydf', shell=True)

    def on_switch_closed(self, *args):
        self.state = 'idle'
        kill_process_by_name('omxplayer')
        kill_process_by_name('darkice')
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
    GPIO.add_event_detect(SWITCH_PIN, GPIO.RISING, callback=echo.on_switch_opened, bouncetime=200)
    GPIO.add_event_detect(SWITCH_PIN, GPIO.FALLING, callback=echo.on_switch_closed, bouncetime=200)

    echo.start()
