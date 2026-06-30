# Troubleshooting

Common issues when redeploying EchoBerry. See also [architecture.md](architecture.md).

## Config and install

### `config.yaml is required on deployed systems`

Copy and edit the example file:

```bash
cp config.example.yaml config.yaml
```

Set `server.host`, `server.source_password`, and other secrets before running `install.sh` or `src/main.py`.

### `install.sh` fails validating passwords

`src/config.py` rejects placeholder values when deployed. Ensure:

- `server.source_password` is not `CHANGE_ME`
- `server.host` is not `icecast.example.com`

### Location mismatch after install

`install.sh` syncs `config.yaml` `location` to the install argument (`yul` or `ydf`). If you re-run for a different site, re-run with the correct argument:

```bash
bash scripts/install.sh ydf
```

## Git LFS / audio files

### `forest_1h.mp3` is tiny or won't play

The file is tracked with Git LFS (~83 MB). After cloning:

```bash
git lfs install
git lfs pull
```

Verify size:

```bash
ls -lh sounds/forest_1h.mp3   # should be ~83M, not ~130 bytes
```

## Icecast server

### `render_icecast.sh` fails — no config.yaml

Create config on the server before rendering:

```bash
cp config.example.yaml config.yaml
# edit server.* values
bash scripts/render_icecast.sh
```

### Cannot connect to admin UI

- Confirm Icecast is running: `icecast -c /usr/local/etc/icecast.xml`
- Check firewall allows port `8000` (or your configured port)
- Use credentials from `config.yaml` → `server.admin_user` / `server.admin_password`

### Stream mount not found

Ensure mount names in `config.yaml` match what clients use:

- YUL: `echoberry-yul`
- YDF: `echoberry-ydf`

## Raspberry Pi audio

### Wrong or missing microphone (`hw:1,0`)

List devices:

```bash
arecord -l
```

Update `audio.alsa_device` in `config.yaml` (e.g. `hw:2,0`), re-render and reinstall:

```bash
PYTHONPATH=src .venv/bin/python scripts/render_configs.py yul --sync-location
sudo cp conf/darkice.cfg /etc/darkice.cfg
sudo systemctl restart darkice
```

### No sound on local speaker

- Check `audio.playback_device` (often `hw=1.0` for USB headset)
- Run the amixer command from config manually:

```bash
amixer cset numid=3 1
```

Card control numbers differ by Pi model — update `install.amixer_analog_cmd` if needed.

### `main.py` requires root

GPIO access needs root on Raspberry Pi OS:

```bash
sudo .venv/bin/python src/main.py
```

## Services

### Check service status

YUL:

```bash
sudo systemctl status darkice echoberry
sudo journalctl -u echoberry -f
```

YDF:

```bash
sudo systemctl status darkice echoberry-listener
sudo journalctl -u echoberry-listener -f
```

### darkice fails to start

- Verify `/etc/darkice.cfg` exists and passwords match Icecast
- Test connectivity: `curl -I http://<server-host>:8000/`
- Check darkice logs via `journalctl -u darkice`

### echoberry.service exits immediately

- Confirm `config.yaml` exists and passes validation
- Confirm `location: yul` in config (main.py is YUL-only)
- Check `journalctl -u echoberry` for `ConfigError` messages

## Streaming behavior

### Forest ambience stops after ~1 hour

Ensure `audio.forest_stream_loop: -1` in `config.yaml`. ffmpeg uses `-stream_loop -1` to loop `forest_1h.mp3` indefinitely.

### YUL dual streams sound wrong

This may be expected: darkice provides a continuous baseline; ffmpeg adds forest + ring on switch open. See [architecture.md](architecture.md).

### `recording.m4a` growing on disk

darkice intentionally writes a local archive. Monitor disk space or rotate the file as part of your install maintenance.

## Development / CI

### `import RPi.GPIO` fails on laptop

Expected — GPIO code only runs on a Raspberry Pi. CI compiles Python without executing GPIO logic.

### shellcheck not installed

```bash
sudo apt-get install shellcheck
```

Or rely on GitHub Actions CI on your PR.

## Still stuck?

1. Gather logs: `journalctl -u darkice -u echoberry -u echoberry-listener --no-pager`
2. Note Pi model, OS version, and `arecord -l` output
3. Open a [bug report](https://github.com/adamsimms/echoberry/issues/new?template=bug_report.md) with reproduction steps (redact secrets)
