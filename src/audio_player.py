import shutil
import subprocess


def find_player():
    if shutil.which("mpv"):
        return "mpv"
    if shutil.which("mplayer"):
        return "mplayer"
    raise RuntimeError("No supported audio player found. Install mpv or mplayer.")


def _mpv_device(playback_device):
    # config uses hw=1.0; mpv expects alsa/hw:1.0
    return "alsa/{}".format(playback_device.replace("=", ":"))


def build_play_command(source, playback_device, player=None):
    player = player or find_player()

    if player == "mpv":
        return [
            "mpv",
            "--no-video",
            "--audio-device={}".format(_mpv_device(playback_device)),
            source,
        ]

    return [
        "mplayer",
        "-ao",
        "alsa:device={}".format(playback_device),
        source,
    ]


def play_and_wait(source, playback_device):
    cmd = build_play_command(source, playback_device)
    subprocess.run(cmd, check=False)
