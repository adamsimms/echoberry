#!/usr/bin/env python3
"""Validate config.example.yaml structure for CI and local checks."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from config import ConfigError, load_raw_config, validate_config_structure  # noqa: E402


def main():
    example_path = REPO_ROOT / "config.example.yaml"
    config = load_raw_config(example_path, allow_example=True)
    try:
        validate_config_structure(config)
    except ConfigError as exc:
        print("Invalid config.example.yaml: {}".format(exc), file=sys.stderr)
        sys.exit(1)
    print("config.example.yaml structure is valid")


if __name__ == "__main__":
    main()
