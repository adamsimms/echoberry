# Installation reference photos

Wiring and hardware photos for redeploying the EchoBerry installation. See [architecture.md](../architecture.md) for how components connect logically.

| File | Description |
|------|-------------|
| `setup-wiring-01.jpg` | Magnetic switch wired to GPIO4 and GND |
| `setup-wiring-02.jpg` | USB microphone and audio connections |
| `setup-installation-01.jpg` | Raspberry Pi in installation context |
| `setup-installation-02.jpg` | Completed hardware assembly |

## GPIO reminder

- Magnetic switch: **GPIO4** (BCM) and **GND**
- Config key: `gpio.switch_pin` in `config.yaml` (default `4`)

## Audio device reminder

USB mic and headset device indices vary. List ALSA devices on your Pi:

```bash
arecord -l   # capture (mic)
aplay -l     # playback (speaker/headset)
```

Update `audio.alsa_device` and `audio.playback_device` in `config.yaml` accordingly.
