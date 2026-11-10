# Agent notes

EchoBerry (2021) is a two-site audio installation linking Montreal and Newfoundland through live sound: opening the Montreal enclosure streams voice and forest ambience between the sites, with a ringing bell. Prefer one issue per chat when the work is mechanical.

Canonical files: [README.md](README.md), [docs/architecture.md](docs/architecture.md), `src/`, `scripts/`.

## Private material

Private notes live in the private studio repo (adamsimms/studio). Nothing from studio comes into this repo unless Adam approves it. Never put a phone number or home address here; a global pre-commit guard blocks them.

## Bibliography / Zotero

Zotero is the source library (public library; no project collection yet, ask Adam). Writing to Zotero is publishing: only approved batches. Do not query `~/Zotero/zotero.sqlite`. Do not invent citations.

## Hard rules

- Do not invent hardware or streaming setup that is not in the README, `docs/` or code.
- Config comes from `config.example.yaml` copied to a local config; never commit live stream credentials.
- Secrets only via `.env`; see `.env.example`.

Docs policy and the decisions rule (work decision vs proposal choice vs option): [`.cursor/rules/docs.mdc`](.cursor/rules/docs.mdc).

## GitHub

Issues here are about the work. Applications, calls and their deadlines are tracked in the private studio repo, not here. Issue titles have no kind prefix; kind lives on labels.

## Project media

Photos, renders, sound and video never stay in this repo's ignored folders: they are not backed up. They go to the project's synced Drive folder, `$MEDIA_DIR` (`30 STUDIO/32 PROJECTS/ECHOBERRY/`): `01-REFERENCES`, `02-STUDIES`, `03-TESTS`, `04-ARTWORK`, `05-DOCUMENTATION`. Inside 02 and 03, one dated folder per piece of work: `<YYYY-MM>-<NAME>`. Older folders there predate this layout and are not reorganized yet.

## Support

Funder acknowledgements are not recorded here yet. Ask Adam before adding any.
