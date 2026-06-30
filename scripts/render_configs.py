#!/usr/bin/env python3
"""Render deployment configs from config.yaml and templates."""

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "conf"


def load_config():
    config_path = REPO_ROOT / "config.yaml"
    if not config_path.exists():
        print("Copy config.example.yaml to config.yaml and edit it before rendering configs.", file=sys.stderr)
        sys.exit(1)

    with open(config_path, encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


def render_template(template_name, output_name, substitutions):
    template_path = TEMPLATE_DIR / template_name
    output_path = TEMPLATE_DIR / output_name
    content = template_path.read_text(encoding="utf-8")
    for key, value in substitutions.items():
        content = content.replace("__{}__".format(key), str(value))
    output_path.write_text(content, encoding="utf-8")
    print("Wrote {}".format(output_path))


def main():
    parser = argparse.ArgumentParser(description="Render EchoBerry config files from config.yaml")
    parser.add_argument("location", choices=["yul", "ydf"], help="Deployment location")
    args = parser.parse_args()

    config = load_config()
    location_config = config["locations"][args.location]
    server = config["server"]

    substitutions = {
        "SERVER_HOST": server["host"],
        "SERVER_PORT": server["port"],
        "SOURCE_PASSWORD": server["source_password"],
        "ADMIN_USER": server["admin_user"],
        "ADMIN_PASSWORD": server["admin_password"],
        "MOUNT_POINT": location_config["stream_mount"],
        "DARKICE_NAME": location_config["darkice_name"],
        "DARKICE_DESCRIPTION": location_config["darkice_description"],
        "ALSA_DEVICE": config["audio"]["alsa_device"],
    }

    render_template("darkice.cfg.template", "darkice.cfg", substitutions)
    render_template("icecast.xml.template", "icecast.xml", substitutions)


if __name__ == "__main__":
    main()
