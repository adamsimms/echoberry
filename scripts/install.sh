#!/usr/bin/env bash
set -euo pipefail

LOCATION="${1:-}"
if [[ "$LOCATION" != "yul" && "$LOCATION" != "ydf" ]]; then
    echo "Usage: $0 <yul|ydf>"
    exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f "$REPO_ROOT/config.yaml" ]]; then
    echo "Copy config.example.yaml to config.yaml and edit it before installing."
    exit 1
fi

echo "==> Installing system packages"
sudo apt-get update
sudo apt-get -y install \
    alsa-utils \
    avahi-daemon \
    darkice \
    ffmpeg \
    mpv \
    mplayer \
    python3 \
    python3-pip \
    python3-dev \
    python3-yaml

echo "==> Installing Python dependencies"
sudo pip3 install -r "$REPO_ROOT/requirements.txt"

echo "==> Rendering configs for location: $LOCATION"
python3 "$REPO_ROOT/scripts/render_configs.py" "$LOCATION"
sudo cp "$REPO_ROOT/conf/darkice.cfg" /etc/darkice.cfg

echo "==> Installing systemd units"
sudo mkdir -p /etc/echoberry
sudo cp "$REPO_ROOT/systemd/darkice.service" /etc/systemd/system/darkice.service
sudo systemctl daemon-reload
sudo systemctl enable darkice.service
sudo systemctl restart darkice.service

PLAYBACK_DEVICE="$(python3 -c "import yaml; c=yaml.safe_load(open('$REPO_ROOT/config.yaml')); print(c['audio']['playback_device'])")"
LISTEN_MOUNT="$(python3 -c "import yaml; c=yaml.safe_load(open('$REPO_ROOT/config.yaml')); print(c['locations']['$LOCATION']['listen_mount'])")"
SERVER_HOST="$(python3 -c "import yaml; c=yaml.safe_load(open('$REPO_ROOT/config.yaml')); print(c['server']['host'])")"
SERVER_PORT="$(python3 -c "import yaml; c=yaml.safe_load(open('$REPO_ROOT/config.yaml')); print(c['server']['port'])")"

sudo tee /etc/echoberry/listener.env > /dev/null <<EOF
ECHOBERY_PLAYBACK_DEVICE=$PLAYBACK_DEVICE
ECHOBERY_LISTEN_URL=http://${SERVER_HOST}:${SERVER_PORT}/${LISTEN_MOUNT}
EOF

if [[ "$LOCATION" == "yul" ]]; then
    sudo cp "$REPO_ROOT/systemd/echoberry.service" /etc/systemd/system/echoberry.service
    sudo systemctl enable echoberry.service
    sudo systemctl restart echoberry.service
    echo "YUL install complete. echoberry.service and darkice.service are enabled."
else
    sudo cp "$REPO_ROOT/systemd/echoberry-listener.service" /etc/systemd/system/echoberry-listener.service
    sudo systemctl enable echoberry-listener.service
    sudo systemctl restart echoberry-listener.service
    echo "YDF install complete. echoberry-listener.service and darkice.service are enabled."
fi

echo "==> Setting analogue audio output"
amixer cset numid=3 1 || true

echo "Done."
