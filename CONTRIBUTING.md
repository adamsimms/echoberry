# Contributing to EchoBerry

Thank you for helping preserve and improve this archival art-installation project.

EchoBerry is a **2021 two-site audio work** connecting Montreal and Newfoundland through live streams of voice, forest ambience, and bell tones. Changes should respect the original experience unless you are explicitly modernizing or fixing a bug.

## Before you start

1. Read [README.md](README.md) for deployment context
2. Read [docs/architecture.md](docs/architecture.md) to understand YUL vs YDF
3. Check [open issues](https://github.com/adamsimms/echoberry/issues) or open one to discuss larger changes

## What you can do without hardware

These run on any machine (Linux/macOS/WSL):

```bash
git clone https://github.com/adamsimms/echoberry
cd echoberry
git lfs install && git lfs pull

pip install PyYAML
python3 -m py_compile src/*.py scripts/*.py
python3 scripts/validate_config.py
```

Optional (matches CI):

```bash
shellcheck scripts/*.sh
```

To test config rendering locally:

```bash
cp config.example.yaml config.yaml
# edit with non-production values
PYTHONPATH=src python3 scripts/render_configs.py yul
# inspect conf/darkice.cfg, conf/icecast.xml, conf/*.env
```

Do **not** commit `config.yaml` or rendered files under `conf/`.

## What requires a Raspberry Pi

| Area | Why |
|------|-----|
| `src/main.py` | Needs `RPi.GPIO`, ALSA devices, root for GPIO |
| `scripts/install.sh` | Installs systemd units, darkice, configures ALSA |
| Audio streaming | USB mic, `hw:1,0` device paths are hardware-specific |
| Switch behavior | Magnetic switch on GPIO4 |

If you cannot test on a Pi, say so in your PR and describe what you validated instead.

## Development setup on a Pi

```bash
cd ~/echoberry
git lfs install && git lfs pull
cp config.example.yaml config.yaml
# edit secrets and server.host

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# dry-run config render
PYTHONPATH=src .venv/bin/python scripts/render_configs.py yul --sync-location

# full install (writes /etc, enables systemd)
bash scripts/install.sh yul   # or ydf
```

Run the switch controller manually:

```bash
sudo .venv/bin/python src/main.py
```

## Branch and commit conventions

- Branch from `master`: `your-name/short-description` or `cursor/...` for agents
- Keep commits focused; use complete sentences in commit messages
- One logical change per PR when possible

## Pull request checklist

Before opening a PR, confirm:

- [ ] `python3 -m py_compile src/*.py scripts/*.py` passes
- [ ] `python3 scripts/validate_config.py` passes
- [ ] `shellcheck scripts/*.sh` passes (if available)
- [ ] No secrets, `config.yaml`, or rendered `conf/*.cfg` / `conf/*.xml` committed
- [ ] README / architecture / troubleshooting updated if behavior changed
- [ ] Tested on a Pi, **or** PR notes explain what could not be tested and why

Use the PR template when opening a pull request.

## Project areas

| Path | Change when… |
|------|----------------|
| `src/` | Python application logic |
| `scripts/` | Install, config rendering, validation |
| `conf/*.template` | Icecast or darkice template structure |
| `systemd/` | Service definitions |
| `config.example.yaml` | New config keys (update validation in `src/config.py`) |
| `docs/` | Architecture, troubleshooting, hardware photos |

## Intentional behaviors — do not "fix" without discussion

- **YUL dual streaming:** `darkice` and switch-triggered `ffmpeg` both feed the same mount
- **`recording.m4a`:** darkice archives the live stream locally
- **Cross-location listen:** YUL listens to YDF on switch open; YDF listens to YUL on boot

## Code style

- Match existing style in the file you edit
- Prefer small, focused diffs over large refactors
- No unnecessary comments; explain non-obvious installation behavior in `docs/`

## Questions

- **Bugs / redeploy issues:** open a [bug report issue](https://github.com/adamsimms/echoberry/issues/new?template=bug_report.md)
- **Security:** see [SECURITY.md](SECURITY.md) — do not file public issues for vulnerabilities
- **Large design changes:** open an issue first; this is an archival project

Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
