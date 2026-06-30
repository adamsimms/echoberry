#!/usr/bin/env bash
# Render icecast.xml from config.yaml for server deployment.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ ! -f "$REPO_ROOT/config.yaml" ]]; then
    echo "Copy config.example.yaml to config.yaml and edit it before rendering."
    exit 1
fi

python3 "$REPO_ROOT/scripts/render_configs.py" yul
echo "Rendered $REPO_ROOT/conf/icecast.xml"
echo "Copy to your Icecast server: sudo cp conf/icecast.xml /usr/local/etc/icecast.xml"
