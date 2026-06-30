# RPi Echo (EchoBerry)

*A two-site audio installation linking Montreal and Newfoundland through live sound.*

EchoBerry (2021) connects distant places with voice, forest ambience, and a ringing bell. When someone opens the enclosure at Montreal, audio flows outward — mixed with the sound of the forest — while Newfoundland listens in and sends its own stream back. The result is a quiet, long-distance conversation between two Raspberry Pi installations bridged over Icecast.

> **Note:** This project documents a completed art installation. It is maintained for archival and redeployment reference, not active product development.

Design reference: [Figma — Echo](https://www.figma.com/file/Qq94FUIBFmaFRzEGjnB09grI/Echo?node-id=1%3A2)

**Sites:** YUL — Montreal · YDF — Newfoundland

## Documentation

| Doc | Audience |
|-----|----------|
| [README.md](README.md) | Deploy the installation |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Change code or docs |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |
| [SECURITY.md](SECURITY.md) | Report vulnerabilities, handle secrets |
| [docs/architecture.md](docs/architecture.md) | How YUL/YDF, services, and streams fit together |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Common deploy and runtime issues |
| [docs/documentation/README.md](docs/documentation/README.md) | Hardware photo captions |

## Components

- Raspberry Pi 3 (or newer)
- USB mini microphone — [example on Amazon](https://www.amazon.co.uk/Richera-Microphone-Notebook-Recognition-Software/dp/B01FJWO5K4)
- Magnetic switch — [Adafruit #375](https://www.adafruit.com/product/375) (connect to GPIO4 and GND)

## Project layout

```
echoberry/
├── config.example.yaml   # copy to config.yaml (gitignored)
├── requirements.txt
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── src/
│   ├── main.py           # YUL switch controller
│   ├── config.py
│   ├── audio_player.py
│   └── utils.py
├── scripts/
│   ├── install.sh        # unified installer (yul | ydf)
│   ├── install_ffmpeg.sh # legacy FFmpeg build
│   ├── render_configs.py
│   ├── validate_config.py
│   └── render_icecast.sh
├── conf/                 # templates + rendered configs (gitignored outputs)
├── systemd/
├── sounds/
│   ├── ring.mp3
│   └── forest_1h.mp3
├── docs/
│   ├── architecture.md
│   ├── troubleshooting.md
│   └── documentation/    # wiring/install photos
└── .github/
    └── workflows/ci.yml
```

## Quick start

### 1. Configure

```bash
cp config.example.yaml config.yaml
# Edit config.yaml: set server host, passwords, and location (yul or ydf)
```

Never commit `config.yaml` — it contains secrets. The application refuses to start without a deployed `config.yaml`.

### 2. Set up the Icecast server

On your streaming server, clone this repo and create a local config (same secrets the Pis will use):

```bash
git clone https://github.com/adamsimms/echoberry
cd echoberry
cp config.example.yaml config.yaml
# edit config.yaml: server.host, passwords, etc.
```

Build and run Icecast-KH (or install Icecast2 from your distro):

```bash
sudo apt-get install build-essential libxslt-dev libogg-dev libvorbis-dev
git clone https://github.com/karlheyes/icecast-kh
cd icecast-kh && ./configure && make && sudo make install
```

Render and install the server config from the echoberry repo:

```bash
cd ~/echoberry
bash scripts/render_icecast.sh
sudo cp conf/icecast.xml /usr/local/etc/icecast.xml
icecast -c /usr/local/etc/icecast.xml
```

Admin UI: `http://<server-host>:<port>/admin.html`

### 3. Set up a Raspberry Pi

Use [Raspberry Pi OS](https://www.raspberrypi.com/software/) (Lite is fine).

```bash
cd ~
git clone https://github.com/adamsimms/echoberry
cd echoberry
git lfs install && git lfs pull
cp config.example.yaml config.yaml
# edit config.yaml
```

**Montreal (YUL):**

```bash
bash scripts/install.sh yul
```

**Newfoundland (YDF):**

```bash
bash scripts/install.sh ydf
```

`install.sh` syncs `config.yaml` `location` to match the install target and writes `/etc/echoberry/*.env` for systemd.

### 4. Manual streaming (debug)

Stream mic + looping forest ambience to YUL mount:

```bash
ffmpeg -ac 1 -re -f alsa -i hw:1,0 -stream_loop -1 -re -i sounds/forest_1h.mp3 \
  -filter_complex amerge=inputs=2 -f mp3 \
  icecast://source:<password>@<host>:<port>/echoberry-yul
```

Listen:

```bash
mpv http://<host>:<port>/echoberry-yul
# USB headset:
mpv --audio-device=alsa/hw=1.0 http://<host>:<port>/echoberry-yul
```

YDF uses `darkice` (configured by `install.sh ydf`) and auto-listens to the YUL stream via `echoberry-listener.service`.

## Services

| Service | Location | Purpose |
|---------|----------|---------|
| `darkice.service` | YUL, YDF | Continuous mic stream to Icecast |
| `echoberry.service` | YUL | GPIO switch → ring + ffmpeg stream + remote listen |
| `echoberry-listener.service` | YDF | Plays remote YUL stream on boot |

```bash
sudo systemctl status darkice echoberry          # YUL
sudo systemctl status darkice echoberry-listener # YDF
```

See [docs/architecture.md](docs/architecture.md) for a full system diagram.

### YUL dual streaming (intentional)

At YUL, **both** `darkice` and the switch-triggered `ffmpeg` stream target the same mount. This is deliberate for the installation: darkice provides a continuous baseline mic feed, while opening the switch layers ring + forest ambience via ffmpeg.

### Darkice local recording (intentional)

`darkice` writes `recording.m4a` locally as an archive of the live stream. This is intentional for the art installation.

## Audio assets

- `sounds/ring.mp3` — played locally when the switch opens
- `sounds/forest_1h.mp3` — mixed under the live mic stream, looped indefinitely (~83 MB, Git LFS)

Forest looping is controlled by `audio.forest_stream_loop` in `config.yaml` (default `-1` = infinite).

If Git LFS is not installed: `git lfs install && git lfs pull`

## Configuration

Key `config.yaml` fields:

| Key | Purpose |
|-----|---------|
| `location` | Active site (`yul` or `ydf`); synced by `install.sh` |
| `server.host` | Icecast server hostname or IP |
| `server.port` | Icecast port (default `8000`) |
| `server.source_password` | Password for stream sources (`darkice`, `ffmpeg`) |
| `server.admin_user` / `server.admin_password` | Icecast admin UI credentials |
| `gpio.switch_pin` | BCM pin for magnetic switch (default `4`) |
| `audio.alsa_device` | ALSA capture device (e.g. `hw:1,0`) |
| `audio.playback_device` | Local playback device (e.g. `hw=1.0`) |
| `audio.ring_file` | Ring tone path (default `sounds/ring.mp3`) |
| `audio.forest_file` | Forest ambience path (default `sounds/forest_1h.mp3`) |
| `audio.forest_stream_loop` | ffmpeg loop count (`-1` = infinite) |
| `install.repo_root` | Install path (auto-set by `install.sh`) |
| `install.amixer_analog_cmd` | Pi analogue audio routing command |

Copy from `config.example.yaml` and see inline comments for location-specific mount names.

## Security

See [SECURITY.md](SECURITY.md). Summary:

- Do not commit private keys, PEM files, or `config.yaml`.
- Rotate credentials that were previously in git (especially the old `Echo-Server.pem` key).
- `Echo-Server.pem` has been removed from the tree and purged from `master` git history.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow. Quick checks:

```bash
pip install PyYAML
python3 -m py_compile src/*.py scripts/*.py
python3 scripts/validate_config.py
shellcheck scripts/*.sh   # optional, matches CI
```

CI runs compile, config validation, and shellcheck on push/PR. GPIO and audio streaming require a Raspberry Pi to test fully.

## Legacy install

`scripts/install_ffmpeg.sh` builds FFmpeg from source for very old ARM systems. Modern installs use `apt-get install ffmpeg` via `scripts/install.sh`.

## License

[MIT](LICENSE)
