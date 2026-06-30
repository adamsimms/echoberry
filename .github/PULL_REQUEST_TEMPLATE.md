## Summary

<!-- What does this PR change and why? -->

## Type of change

- [ ] Bug fix
- [ ] Documentation
- [ ] Install / deploy
- [ ] Refactor
- [ ] Other (describe below)

## Checklist

- [ ] `python3 -m py_compile src/*.py scripts/*.py` passes
- [ ] `python3 scripts/validate_config.py` passes
- [ ] `shellcheck scripts/*.sh` passes (or CI will verify)
- [ ] No secrets, `config.yaml`, or rendered `conf/darkice.cfg` / `conf/icecast.xml` committed
- [ ] Docs updated (README, architecture, troubleshooting) if behavior changed

## Testing

<!-- What did you test? -->

- [ ] Tested on Raspberry Pi (YUL / YDF / both)
- [ ] Tested without Pi (compile / validate / shellcheck only)

**Hardware tested on:** <!-- e.g. Pi 3, Pi OS Bookworm, or N/A -->

**Steps:**

```
1.
2.
```

## Intentional behaviors

<!-- If your change touches streaming, confirm these are preserved unless intentionally changed: -->

- [ ] YUL dual streaming (darkice + ffmpeg on same mount) preserved or change documented
- [ ] darkice `recording.m4a` local archive preserved or change documented
