import logging
import os
import signal
import subprocess
import sys

import RPi.GPIO as GPIO

from audio_player import build_play_command, find_player, play_and_wait
from config import icecast_source_url, load_config, stream_url
from utils import kill_process_by_name, stop_processes

logger = logging.getLogger("echoberry")


class RPiEcho:

    state = "idle"

    def __init__(self, config):
        self.config = config
        self.repo_root = config["repo_root"]
        self.ring_path = os.path.join(self.repo_root, config["audio"]["ring_file"])
        self.forest_path = os.path.join(self.repo_root, config["audio"]["forest_file"])
        self.playback_device = config["audio"]["playback_device"]
        self.stream_mount = config["stream_mount"]
        self.listen_mount = config["listen_mount"]
        self.player = find_player()
        self._processes = []

    def on_switch_event(self, *args):
        if GPIO.input(self.config["gpio"]["switch_pin"]):
            self.on_switch_opened()
        else:
            self.on_switch_closed()

    def on_switch_opened(self):
        logger.info("Switch opened")
        if self.state == "idle":
            self.state = "active"
            self._play_ring()
            self._start_stream()
            self._start_listener()

    def on_switch_closed(self):
        logger.info("Switch closed")
        self.state = "idle"
        stop_processes(self._processes)
        self._processes.clear()
        kill_process_by_name("ffmpeg")
        kill_process_by_name("mplayer")
        kill_process_by_name("mpv")

    def _spawn(self, cmd):
        logger.info("Starting: %s", " ".join(cmd))
        proc = subprocess.Popen(cmd)
        self._processes.append(proc)
        return proc

    def _play_ring(self):
        play_and_wait(self.ring_path, self.playback_device)
        kill_process_by_name(self.player)

    def _start_stream(self):
        output_url = icecast_source_url(self.config, self.stream_mount)
        loop_count = str(self.config["audio"]["forest_stream_loop"])
        cmd = [
            "ffmpeg",
            "-ac",
            "1",
            "-re",
            "-f",
            "alsa",
            "-i",
            self.config["audio"]["alsa_device"],
            "-stream_loop",
            loop_count,
            "-re",
            "-i",
            self.forest_path,
            "-filter_complex",
            "amerge=inputs=2",
            "-f",
            "mp3",
            output_url,
        ]
        self._spawn(cmd)

    def _start_listener(self):
        listen_url = stream_url(self.config, self.listen_mount)
        cmd = build_play_command(listen_url, self.playback_device, self.player)
        self._spawn(cmd)

    def run(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.config["gpio"]["switch_pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.config["gpio"]["switch_pin"],
            GPIO.BOTH,
            callback=self.on_switch_event,
            bouncetime=200,
        )
        logger.info("Waiting for switch events on GPIO %s", self.config["gpio"]["switch_pin"])
        try:
            signal.pause()
        except KeyboardInterrupt:
            logger.info("Shutting down")
        finally:
            self.on_switch_closed()
            GPIO.cleanup()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    if not sys.version_info >= (3, 0):
        sys.stderr.write("Requires Python 3.x. Run with `python3 src/main.py`\n")
        sys.exit(1)

    if os.getuid() != 0:
        sys.stderr.write("Root privileges required. Run with `sudo`.\n")
        sys.exit(1)

    config = load_config(require_deployed=True)

    if config["location"] != "yul":
        sys.stderr.write("main.py is only used at the YUL location.\n")
        sys.exit(1)

    amixer_cmd = config["install"]["amixer_analog_cmd"]
    if amixer_cmd:
        logger.info("Running audio setup: %s", amixer_cmd)
        os.system(amixer_cmd)

    RPiEcho(config).run()


if __name__ == "__main__":
    main()
