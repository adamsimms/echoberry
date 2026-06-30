# RPi Echo (EchoBerry)

An interactive audio installation: a magnetic switch on a Raspberry Pi triggers a ring tone, then streams live microphone audio mixed with forest ambience to an Icecast server. Two locations (YUL and YDF) can listen to each other's streams.

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
│   └── utils.py
├── scripts/
│   ├── install.sh        # unified installer (yul | ydf)
│   ├── render_configs.py
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

Never commit `config.yaml` — it contains secrets.

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

### 4. Manual streaming (debug)

Stream mic + forest ambience to YUL mount:

```bash
ffmpeg -ac 1 -re -f alsa -i hw:1,0 -re -i sounds/forest_1h.mp3 \
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

## Audio assets

- `sounds/ring.mp3` — played locally when the switch opens
- `sounds/forest_1h.mp3` — mixed under the live mic stream (~83 MB, tracked via Git LFS)

If Git LFS is not installed: `git lfs install && git lfs pull`

## Security notes

- **Do not commit** private keys, PEM files, or `config.yaml`.
- Rotate any credentials that were previously committed to this repository.
- The old `Echo-Server.pem` has been removed and purged from git history; rotate the key on the server if it was ever exposed.

## Legacy install

`scripts/install_ffmpeg.sh` builds FFmpeg from source for very old ARM systems. Modern installs use `apt-get install ffmpeg` via `scripts/install.sh`.

## Documentation photos

See `docs/documentation/` for wiring and installation reference images.
