import os
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config.yaml"
EXAMPLE_CONFIG_PATH = REPO_ROOT / "config.example.yaml"


def load_config():
    path = CONFIG_PATH if CONFIG_PATH.exists() else EXAMPLE_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"No config found. Copy {EXAMPLE_CONFIG_PATH.name} to {CONFIG_PATH.name} and edit it."
        )

    with open(path, encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    location = config["location"]
    if location not in config["locations"]:
        raise ValueError(f"Unknown location '{location}'. Expected one of: {list(config['locations'])}")

    location_config = config["locations"][location]
    return {
        "repo_root": str(REPO_ROOT),
        "location": location,
        "server": config["server"],
        "gpio": config["gpio"],
        "audio": config["audio"],
        "stream_mount": location_config["stream_mount"],
        "listen_mount": location_config["listen_mount"],
        "darkice_name": location_config["darkice_name"],
        "darkice_description": location_config["darkice_description"],
    }


def stream_url(config, mount):
    server = config["server"]
    return "http://{host}:{port}/{mount}".format(
        host=server["host"],
        port=server["port"],
        mount=mount,
    )


def icecast_source_url(config, mount):
    server = config["server"]
    return "icecast://source:{password}@{host}:{port}/{mount}".format(
        password=server["source_password"],
        host=server["host"],
        port=server["port"],
        mount=mount,
    )
