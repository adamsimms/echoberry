#!/usr/bin/env python3
"""Render deployment configs from config.yaml and templates."""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from config import ConfigError, load_raw_config, sync_location
TEMPLATE_DIR = REPO_ROOT / "conf"
OUTPUT_DIR = REPO_ROOT / "conf"


def render_template(template_name, output_name, substitutions):
    template_path = TEMPLATE_DIR / template_name
    output_path = OUTPUT_DIR / output_name
    content = template_path.read_text(encoding="utf-8")
    for key, value in substitutions.items():
        content = content.replace("__{}__".format(key), str(value))
    output_path.write_text(content, encoding="utf-8")
    print("Wrote {}".format(output_path))


def write_env_file(path, values):
    lines = ["{}={}".format(key, value) for key, value in values.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Wrote {}".format(path))


def build_substitutions(config, location):
    location_config = config["locations"][location]
    server = config["server"]
    install = config["install"]
    return {
        "SERVER_HOST": server["host"],
        "SERVER_PORT": server["port"],
        "SOURCE_PASSWORD": server["source_password"],
        "ADMIN_USER": server["admin_user"],
        "ADMIN_PASSWORD": server["admin_password"],
        "MOUNT_POINT": location_config["stream_mount"],
        "DARKICE_NAME": location_config["darkice_name"],
        "DARKICE_DESCRIPTION": location_config["darkice_description"],
        "ALSA_DEVICE": config["audio"]["alsa_device"],
        "ECHOBERY_ROOT": install["repo_root"],
        "ECHOBERY_VENV_PYTHON": "{}/.venv/bin/python".format(install["repo_root"]),
        "LISTEN_MOUNT": location_config["listen_mount"],
        "PLAYBACK_DEVICE": config["audio"]["playback_device"],
        "LISTEN_URL": "http://{}:{}/{}".format(
            server["host"], server["port"], location_config["listen_mount"]
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="Render EchoBerry config files from config.yaml")
    parser.add_argument("location", choices=["yul", "ydf"], help="Deployment location")
    parser.add_argument(
        "--sync-location",
        action="store_true",
        help="Update config.yaml location to match the requested deployment location",
    )
    args = parser.parse_args()

    config_path = REPO_ROOT / "config.yaml"
    if not config_path.exists():
        print("Copy config.example.yaml to config.yaml and edit it before rendering configs.", file=sys.stderr)
        sys.exit(1)

    if args.sync_location:
        sync_location(args.location, config_path)
        print("Updated config.yaml location to {}".format(args.location))

    config = load_raw_config(config_path)
    substitutions = build_substitutions(config, args.location)

    render_template("darkice.cfg.template", "darkice.cfg", substitutions)
    render_template("icecast.xml.template", "icecast.xml", substitutions)
    write_env_file(OUTPUT_DIR / "listener.env", {
        "ECHOBERY_PLAYBACK_DEVICE": substitutions["PLAYBACK_DEVICE"],
        "ECHOBERY_LISTEN_URL": substitutions["LISTEN_URL"],
    })
    write_env_file(OUTPUT_DIR / "install.env", {
        "ECHOBERY_ROOT": substitutions["ECHOBERY_ROOT"],
        "ECHOBERY_VENV_PYTHON": substitutions["ECHOBERY_VENV_PYTHON"],
    })


if __name__ == "__main__":
    try:
        main()
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
