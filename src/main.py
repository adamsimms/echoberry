import datetime
import os
import subprocess
import sys
import threading
import time

from mutagen.mp3 import MP3

import RPi.GPIO as GPIO

from config import icecast_source_url, load_config, stream_url
from utils import kill_process_by_name


class RPiEcho(threading.Thread):

    state = "idle"

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.repo_root = config["repo_root"]
        self.ring_path = os.path.join(self.repo_root, config["audio"]["ring_file"])
        self.forest_path = os.path.join(self.repo_root, config["audio"]["forest_file"])
        self.playback_device = config["audio"]["playback_device"]
        self.stream_mount = config["stream_mount"]
        self.listen_mount = config["listen_mount"]

    def run(self):
        while True:
            time.sleep(1)

    def on_switch_event(self, *args):
        if GPIO.input(self.config["gpio"]["switch_pin"]):
            self.on_switch_opened()
        else:
            self.on_switch_closed()

    def on_switch_opened(self):
        print(">>> {}:: Switch is opened!".format(datetime.datetime.now()))
        if self.state == "idle":
            self.state = "active"
            self._play_ring()
            self._start_stream()
            self._start_listener()

    def on_switch_closed(self):
        print(">>> {}:: Switch is closed.".format(datetime.datetime.now()))
        self.state = "idle"
        kill_process_by_name("ffmpeg")
        kill_process_by_name("mplayer")
        kill_process_by_name("mpv")

    def _play_ring(self):
        subprocess.Popen(
            [
                "mplayer",
                "-ao",
                "alsa:device={}".format(self.playback_device),
                self.ring_path,
            ]
        )
        audio = MP3(self.ring_path)
        time.sleep(audio.info.length)
        kill_process_by_name("mplayer")

    def _start_stream(self):
        output_url = icecast_source_url(self.config, self.stream_mount)
        cmd = [
            "ffmpeg",
            "-ac",
            "1",
            "-re",
            "-f",
            "alsa",
            "-i",
            self.config["audio"]["alsa_device"],
            "-re",
            "-i",
            self.forest_path,
            "-filter_complex",
            "amerge=inputs=2",
            "-f",
            "mp3",
            output_url,
        ]
        print(">>> {}:: Audio Stream - {}".format(datetime.datetime.now(), " ".join(cmd)))
        subprocess.Popen(cmd)

    def _start_listener(self):
        listen_url = stream_url(self.config, self.listen_mount)
        subprocess.Popen(
            [
                "mplayer",
                "-ao",
                "alsa:device={}".format(self.playback_device),
                listen_url,
            ]
        )


def main():
    if not sys.version_info >= (3, 0):
        sys.stdout.write("Sorry, requires Python 3.x. Please execute with `python3 src/main.py`\n")
        sys.exit(1)

    if os.getuid() != 0:
        sys.stdout.write("You need root privileges to run this service. Please try with `sudo`.\n")
        sys.exit(1)

    config = load_config()

    if config["location"] != "yul":
        sys.stdout.write("main.py is only used at the YUL location. YDF uses darkice and echoberry-listener.\n")
        sys.exit(1)

    os.system("amixer cset numid=3 1")

    echo = RPiEcho(config)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config["gpio"]["switch_pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(
        config["gpio"]["switch_pin"],
        GPIO.BOTH,
        callback=echo.on_switch_event,
        bouncetime=200,
    )

    echo.start()
    echo.join()


if __name__ == "__main__":
    main()
