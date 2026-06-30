---
name: Bug report
description: Something isn't working during deploy or runtime
title: "[Bug]: "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for reporting an issue. **Do not include passwords or `config.yaml` contents.**
        See [troubleshooting.md](https://github.com/adamsimms/echoberry/blob/master/docs/troubleshooting.md) first.

  - type: dropdown
    id: location
    attributes:
      label: Site
      options:
        - YUL (Montreal)
        - YDF (Newfoundland)
        - Icecast server
        - Development / CI
        - Other
    validations:
      required: true

  - type: input
    id: hardware
    attributes:
      label: Hardware / OS
      description: Pi model, OS version, or server distro
      placeholder: e.g. Raspberry Pi 3, Raspberry Pi OS Bookworm
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
      description: Commands run, switch actions, etc.
      placeholder: |
        1. cp config.example.yaml config.yaml
        2. bash scripts/install.sh yul
        3. ...
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Actual behavior
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Logs
      description: journalctl output, errors (redact secrets)
      render: shell
      placeholder: sudo journalctl -u echoberry --no-pager -n 50

  - type: checkboxes
    id: checks
    attributes:
      label: Pre-report checks
      options:
        - label: I read docs/troubleshooting.md
          required: true
        - label: I confirmed config.yaml is not pasted in this issue
          required: true
