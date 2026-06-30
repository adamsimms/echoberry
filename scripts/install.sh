#!/usr/bin/env bash
set -euo pipefail

LOCATION="${1:-}"
if [[ "$LOCATION" != "yul" && "$LOCATION" != "ydf" ]]; then
    echo "Usage: $0 <yul|ydf>"
    exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
VENV="$REPO_ROOT/.venv"

if [[ ! -f "$REPO_ROOT/config.yaml" ]]; then
    echo "Copy config.example.yaml to config.yaml and edit it before installing."
    exit 1
fi

# Record install path in config so systemd units can reference it.
python3 - <<PY
import yaml
from pathlib import Path

config_path = Path("$REPO_ROOT/config.yaml")
config = yaml.safe_load(config_path.read_text())
config.setdefault("install", {})["repo_root"] = "$REPO_ROOT"
config_path.write_text(yaml.safe_dump(config, sort_keys=False))
PY

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
    python3-venv \
    python3-yaml

echo "==> Creating Python virtualenv"
python3 -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip
"$VENV/bin/pip" install -r "$REPO_ROOT/requirements.txt"

echo "==> Rendering configs for location: $LOCATION"
PYTHONPATH="$REPO_ROOT/src" "$VENV/bin/python" "$REPO_ROOT/scripts/render_configs.py" "$LOCATION" --sync-location
sudo cp "$REPO_ROOT/conf/darkice.cfg" /etc/darkice.cfg

echo "==> Installing systemd units and environment files"
sudo mkdir -p /etc/echoberry
sudo cp "$REPO_ROOT/conf/install.env" /etc/echoberry/install.env
sudo cp "$REPO_ROOT/conf/listener.env" /etc/echoberry/listener.env
sudo cp "$REPO_ROOT/systemd/darkice.service" /etc/systemd/system/darkice.service
sudo systemctl daemon-reload
sudo systemctl enable darkice.service
sudo systemctl restart darkice.service

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

AMIXER_CMD="$(python3 -c "import yaml; print(yaml.safe_load(open('$REPO_ROOT/config.yaml'))['install']['amixer_analog_cmd'])")"
if [[ -n "$AMIXER_CMD" ]]; then
    echo "==> Setting analogue audio output"
    eval "$AMIXER_CMD" || true
fi

echo "Done."
