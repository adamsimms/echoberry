# Security Policy

## Reporting

If you discover a security issue with EchoBerry, open a private disclosure via GitHub Security Advisories on this repository, or contact the repository owner directly.

## Secrets

- Never commit `config.yaml`, private keys (`.pem`, `.key`), or credentials.
- Copy `config.example.yaml` to `config.yaml` locally and keep it out of version control.
- Rotate Icecast passwords if they were ever committed to git or shared in documentation.

## Known historical exposure

`Echo-Server.pem` was previously committed to this repository. It has been removed from the tree. If the repository was ever public:

1. Assume the key is compromised.
2. Revoke and replace the key on the server.
3. Purge the blob from `master` git history (`git filter-repo --path Echo-Server.pem --invert-paths`) and force-push.

## Deployment

- `src/main.py` refuses to start without a valid `config.yaml` on deployed systems.
- `scripts/install.sh` syncs `config.yaml` `location` to the install target (`yul` or `ydf`).
- Run services as root only where required (GPIO access on Raspberry Pi).

## Dependencies

Install scripts create a project virtualenv at `.venv/` rather than installing Python packages system-wide.
