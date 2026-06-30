# RPi Echo (EchoBerry)

An interactive audio installation (2021): a magnetic switch on a Raspberry Pi triggers a ring tone, then streams live microphone audio mixed with forest ambience to an Icecast server. Two locations (YUL and YDF) can listen to each other's streams.

> **Note:** This project documents a completed art installation. It is maintained for archival and redeployment reference, not active product development.

Design reference: [Figma — Echo](https://www.figma.com/file/Qq94FUIBFmaFRzEGjnB09grI/Echo?node-id=1%3A2)

## Components

- Raspberry Pi 3 (or newer)
- USB mini microphone — [example on Amazon](https://www.amazon.co.uk/Richera-Microphone-Notebook-Recognition-Software/dp/B01FJWO5K4)
- Magnetic switch — [Adafruit #375](https://www.adafruit.com/product/375) (connect to GPIO4 and GND)

## Project layout

```
echoberry/
├── config.example.yaml   # copy to config.yaml (gitignored)
├── requirements.txt
├── src/
│   ├── main.py           # YUL switch controller
│   ├── config.py
│   ├── audio_player.py
│   └── utils.py
├── scripts/
│   ├── install.sh        # unified installer (yul | ydf)
│   ├── render_configs.py
│   ├── validate_config.py
│   └── render_icecast.sh
├── conf/                 # templates + rendered configs (gitignored outputs)
├── systemd/
├── sounds/
│   ├── ring.mp3
│   └── forest_1h.mp3
└── docs/documentation/
```

## Quick start

### 1. Configure

```bash
cp config.example.yaml config.yaml
# Edit config.yaml: set server host, passwords, and location (yul or ydf)
```

Never commit `config.yaml` — it contains secrets. The application refuses to start without a deployed `config.yaml`.

### 2. Set up the Icecast server

On your streaming server:

```bash
# Build Icecast-KH (or install Icecast2 from your distro)
sudo apt-get install build-essential libxslt-dev libogg-dev libvorbis-dev
git clone https://github.com/karlheyes/icecast-kh
cd icecast-kh && ./configure && make && sudo make install

# Render and install config from this repo
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

### YUL dual streaming (intentional)

At YUL, **both** `darkice` and the switch-triggered `ffmpeg` stream target the same mount. This is deliberate for the installation: darkice provides a continuous baseline mic feed, while opening the switch layers ring + forest ambience via ffmpeg.

### Darkice local recording (intentional)

`darkice` writes `recording.m4a` locally as an archive of the live stream. This is intentional for the art installation.

## Audio assets

- `sounds/ring.mp3` — played locally when the switch opens
- `sounds/forest_1h.mp3` — mixed under the live mic stream, looped indefinitely (~83 MB, Git LFS)

Forest looping is controlled by `audio.forest_stream_loop` in `config.yaml` (default `-1` = infinite).

## Configuration

Key `config.yaml` fields:

| Key | Purpose |
|-----|---------|
| `location` | Active site (`yul` or `ydf`); synced by `install.sh` |
| `server.*` | Icecast host, port, passwords |
| `audio.alsa_device` | Capture device for mic/forest mix |
| `audio.playback_device` | Local playback device (`hw=1.0`) |
| `install.repo_root` | Install path (auto-set by `install.sh`) |
| `install.amixer_analog_cmd` | Pi analogue audio routing command |

## Security

See [SECURITY.md](SECURITY.md). Summary:

- Do not commit private keys, PEM files, or `config.yaml`.
- Rotate credentials that were previously in git.
- Purge `Echo-Server.pem` from `master` history if the repo was ever public.

## Development

```bash
pip install PyYAML mutagen
python3 -m py_compile src/*.py scripts/*.py
python3 scripts/validate_config.py
```

CI runs the same checks on push/PR.

## Legacy install

`scripts/install_ffmpeg.sh` builds FFmpeg from source for very old ARM systems. Modern installs use `apt-get install ffmpeg` via `scripts/install.sh`.

## Documentation photos

See [docs/documentation/README.md](docs/documentation/README.md) for captions.

## License

[MIT](LICENSE)
