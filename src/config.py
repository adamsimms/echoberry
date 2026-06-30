import os
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config.yaml"
EXAMPLE_CONFIG_PATH = REPO_ROOT / "config.example.yaml"

REQUIRED_TOP_LEVEL = ("location", "server", "gpio", "audio", "install", "locations")
REQUIRED_SERVER = ("host", "port", "source_password", "admin_user", "admin_password")
REQUIRED_AUDIO = ("alsa_device", "playback_device", "ring_file", "forest_file", "forest_stream_loop")
REQUIRED_INSTALL = ("repo_root", "amixer_analog_cmd")
REQUIRED_LOCATION = ("stream_mount", "listen_mount", "darkice_name", "darkice_description")


class ConfigError(Exception):
    pass


def _require_mapping(data, key, path):
    if key not in data or not isinstance(data[key], dict):
        raise ConfigError("Missing or invalid '{}' in {}".format(key, path))
    return data[key]


def _require_keys(mapping, keys, path):
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise ConfigError("Missing keys in {}: {}".format(path, ", ".join(missing)))


def validate_config_structure(config):
    _require_keys(config, REQUIRED_TOP_LEVEL, "config.yaml")

    location = config["location"]
    if location not in config["locations"]:
        raise ConfigError(
            "Unknown location '{}'. Expected one of: {}".format(location, list(config["locations"]))
        )

    server = _require_mapping(config, "server", "config.yaml")
    _require_keys(server, REQUIRED_SERVER, "server")

    audio = _require_mapping(config, "audio", "config.yaml")
    _require_keys(audio, REQUIRED_AUDIO, "audio")

    install = _require_mapping(config, "install", "config.yaml")
    _require_keys(install, REQUIRED_INSTALL, "install")

    for name, location_config in config["locations"].items():
        if not isinstance(location_config, dict):
            raise ConfigError("Invalid locations.{}".format(name))
        _require_keys(location_config, REQUIRED_LOCATION, "locations.{}".format(name))


def validate_config_deployed(config):
    validate_config_structure(config)
    server = config["server"]
    if server["source_password"] == "CHANGE_ME":
        raise ConfigError("Set server.source_password in config.yaml before deploying")

    if server["host"] in ("icecast.example.com", "localhost", ""):
        raise ConfigError("Set server.host in config.yaml before deploying")


def _validate_config(config):
    validate_config_deployed(config)


def load_raw_config(path=None, allow_example=False):
    if path is None:
        path = CONFIG_PATH

    path = Path(path)
    if not path.exists():
        if allow_example and EXAMPLE_CONFIG_PATH.exists():
            path = EXAMPLE_CONFIG_PATH
        else:
            raise FileNotFoundError(
                "No config found at {}. Copy {} to config.yaml and edit it.".format(
                    CONFIG_PATH, EXAMPLE_CONFIG_PATH.name
                )
            )

    with open(path, encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    if config is None:
        raise ConfigError("config.yaml is empty")

    return config


def load_config(require_deployed=True):
    if require_deployed and not CONFIG_PATH.exists():
        raise FileNotFoundError(
            "config.yaml is required on deployed systems. Copy {} to config.yaml and edit it.".format(
                EXAMPLE_CONFIG_PATH.name
            )
        )

    path = CONFIG_PATH if CONFIG_PATH.exists() else EXAMPLE_CONFIG_PATH
    config = load_raw_config(path)
    if require_deployed:
        _validate_config(config)

    location = config["location"]
    location_config = config["locations"][location]
    return {
        "repo_root": str(REPO_ROOT),
        "location": location,
        "server": config["server"],
        "gpio": config["gpio"],
        "audio": config["audio"],
        "install": config["install"],
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


def sync_location(location, config_path=None):
    config_path = Path(config_path or CONFIG_PATH)
    config = load_raw_config(config_path)
    if location not in config["locations"]:
        raise ConfigError("Unknown location '{}'".format(location))
    config["location"] = location
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
