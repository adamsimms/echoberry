# Security Policy

## Reporting

If you discover a security issue with EchoBerry, open a private disclosure via [GitHub Security Advisories](https://github.com/adamsimms/echoberry/security/advisories/new) on this repository, or contact the repository owner directly.

Please do not open public issues for undisclosed vulnerabilities.

## Secrets

- Never commit `config.yaml`, private keys (`.pem`, `.key`), or credentials.
- Copy `config.example.yaml` to `config.yaml` locally and keep it out of version control.
- Rotate Icecast passwords if they were ever committed to git or shared in documentation.

## Known historical exposure

`Echo-Server.pem` was previously committed to this repository.

**Remediation status:**

- Removed from the repository tree
- Purged from `master` git history via `git filter-repo`

**If you cloned before the purge**, fetch the latest `master` and reset your local copy. Anyone who may have accessed the old key should:

1. Assume the key is compromised
2. Revoke and replace it on the server
3. Rotate Icecast and related credentials

## Deployment

- `src/main.py` refuses to start without a valid `config.yaml` on deployed systems.
- `scripts/install.sh` syncs `config.yaml` `location` to the install target (`yul` or `ydf`).
- Run services as root only where required (GPIO access on Raspberry Pi).
- Rendered configs (`conf/darkice.cfg`, `conf/icecast.xml`) contain secrets and are gitignored — do not commit them.

## Dependencies

Install scripts create a project virtualenv at `.venv/` rather than installing Python packages system-wide.
