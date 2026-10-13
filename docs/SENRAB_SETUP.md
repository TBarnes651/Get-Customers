# SENRAB phase one: setup record

Phase one is **research and drafts only**. Nothing is sent, posted, submitted, booked or connected.

## Provenance

| Item | Value |
|---|---|
| Upstream project | `ethanplusai/harvey`, package version 0.2.0 |
| Upstream commit used | `822e84e7c7ec665b781a92cd290a679e9166992d` (read from the zip archive comment of `harvey-main.zip`) |
| Archive checksum (SHA-256) | `7ee9645cadadcf5cb9f957bc1568605da746cf393aa2ffe89c1349f102accf73` |
| This repo's import commit | `2703a80` ("Add files via upload", the zip only) |
| Environment | Linux cloud container, Python 3.12.x in `.venv` (3.11, 3.12, 3.13 present), 242 upstream tests pass |

The archive has no `.git`, so the upstream commit comes only from the zip comment.

## Documentation versus executable code (code followed)

1. **`harvey train` output file.** CLAUDE.md says it generates `harvey.yaml`. `harvey/trainer.py` writes
   **`harvey.local.yaml`**, and `harvey/config.py::_find_config_file()` ranks that above `harvey.yaml`. A later
   `harvey train` therefore silently overrides every phase-one setting. It also writes
   `skills/product_knowledge.md` (overwriting the hand-written one) and `skills/competitive_intel.md`.
2. **What the trainer generates.** Email `enabled: true`, provider `instantly`, LinkedIn `enabled: true`, timezone
   `America/New_York`, budget 80, persona `harvey@<domain>` and an invented LinkedIn slug, competitors the model is
   told to infer when the site names none. Not run here, and not safe to run without review.
3. **Which file `harvey run` checks.** `harvey/main.py::_needs_setup()` reads only `harvey.yaml` and starts the
   interactive wizard if the company is still "Your Company". Using `harvey.yaml` (as here) avoids that; a
   `harvey.local.yaml`-only setup would not. `harvey setup` rewrites `harvey.yaml` and `.env`: do not run it.
4. **`email.enabled: false` is not a master switch for everything.** Only `Sender` and `Handler` check it. `Scout` and
   `Writer` ignore it, and Scout does web searches and site scraping. This is why `harvey run` stays off.
5. **`harvey export` cannot export discovery results.** Only the Scout agent creates prospects. `harvey discover` and
   `harvey profile` create companies and observations. `scripts/export_candidates.py` was added for this.
6. **Export default is `verified`/`risky` emails only**, so on a fresh install `harvey export` writes nothing
   (CLAUDE.md's "valuable purely as a list-builder" assumes a verifier key).
7. **Writer only drafts for prospects with a verified/risky email.** With no verifier key and no mailbox it drafts
   nothing, so the stock pipeline cannot produce the three drafts (see next step).
8. **Dashboard "Start Harvey" button** spawns `python -m harvey` with no arguments, which is the CLI help. Do not
   rely on it, and do not click it.
9. **Smaller mismatches.** The signal catalogue has 23 signals (docs say about 19). `harvey signals --confirm free`
   matches on the cost note starting "free" or "included". `harvey status` prints the prospect dict, not a count.
   `docker-compose.yml` mounts only `harvey.yaml`. `prompts/writer.md` bans the word "free", which conflicts with a
   free operational review; it now allows "free operational review" from email 2 only.
10. **Playwright.** `harvey install` downloads Chromium for LinkedIn. Skipped: LinkedIn is off.

## Effective configuration

Loader order (`config.py`): `harvey.local.yaml` (cwd), `harvey.local.yaml` (project root), `harvey.yaml` (cwd),
parent-dir `harvey.yaml`, `harvey.yaml` (project root). No `harvey.local.yaml` exists, so **`harvey.yaml`** is used.

| Setting | Value |
|---|---|
| `channels.email.enabled` | `false` (provider `gmail`, inert; `max_daily_sends: 0`) |
| `channels.email.require_approval` | `true` (preserved) |
| `channels.email.send_to_risky` | `false` (preserved) |
| `channels.linkedin.enabled` | `false` (limits 0) |
| Sending kill switch | paused (`harvey sending pause`; stored in `data/harvey.db`) |
| Timezone / Claude budget | `Europe/London` / `20` percent |
| Dashboard bind | `127.0.0.1:5555` (CLI default) |
| `.env` | created from `.env.example`, every credential blank, mode 600 |
| Persona name/role/email/LinkedIn | blank. Drafts sign off `{sender_name}`, which the pre-send gate rejects |

Re-check any time: `.venv/bin/python scripts/check_phase_one.py`

## Signals

Confirmed (5, all free, all implemented): `FOUND_IN_SERP` (provenance), `CONTACT_FOUND`, `DECISION_MAKER_TITLE`,
`HIRING_ROLE` (weak: its role regex favours trades roles), `CONTACT_FORM_URL` (reachability only).

Deliberately not confirmed: `NO_SCHEMA_MARKUP`, `NO_ONLINE_BOOKING`, `BLOG_STALE`, `SITE_PAGE_COUNT`,
`BLOCKS_AI_CRAWLERS`, `RUNNING_*_ADS`, `INCUMBENT_AGENCY`, `TECH_STACK` (website-marketing facts, not evidence a
contractor needs operational software); `SERP_RANK`, `NO_WEBSITE`, `UNCLAIMED_LISTING`, `REVIEW_*` (need a paid
listings or SERP provider); `REGISTRY_VERIFIED`, `LIKELY_OWNER` (no collector exists); `EMAIL_PATTERN`,
`EMAIL_STATUS` (need verifier accounts; deferred).

## Financial screen (revenue at least GBP 2m; else net assets above GBP 750k and cash above GBP 250k)

Harvey has **no native support**: no field, filter, Companies House integration or accounts parser. It is a manual
review criterion. `exports/candidates.csv` carries `financial_eligibility` (default `unknown`) and
`filing_source_and_date`. `company_size` is not used as a filter. Unknown never excludes a research candidate.

## Commands

Linux/macOS (from the repo root):

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest -q
cp -n .env.example .env && chmod 600 .env
.venv/bin/harvey sending pause
.venv/bin/harvey signals --confirm FOUND_IN_SERP,CONTACT_FOUND,DECISION_MAKER_TITLE,HIRING_ROLE,CONTACT_FORM_URL
.venv/bin/python scripts/check_phase_one.py

.venv/bin/harvey dashboard                      # http://127.0.0.1:5555 (do not click Start Harvey)
.venv/bin/harvey discover --estimate --city "Greater Manchester" --limit 25
.venv/bin/harvey discover --city "Greater Manchester" --limit 25 --max-spend 0   # free source, reads OSM then profiles sites
.venv/bin/harvey status ; .venv/bin/harvey signals ; .venv/bin/harvey sending status
.venv/bin/python scripts/export_candidates.py   # -> exports/candidates.csv (gitignored)
```

Windows PowerShell (no activation needed, so execution-policy settings cannot block it):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\harvey.exe sending pause
.\.venv\Scripts\python.exe scripts\check_phase_one.py
.\.venv\Scripts\harvey.exe dashboard
.\.venv\Scripts\harvey.exe discover --city "Greater Manchester" --limit 25 --max-spend 0
.\.venv\Scripts\python.exe scripts\export_candidates.py
```

Never run in phase one: `harvey run`, `harvey setup`, `harvey train`, `harvey gmail ...`, `harvey outbox --approve*`,
`harvey sending resume`, the dashboard's Start / Approve buttons.

## Persistence

`.venv/`, `.env`, `data/` (database, kill-switch state, signal decisions) and `exports/` are gitignored by design and
do **not** survive a fresh clone or a reclaimed cloud container. After cloning locally, repeat the install commands,
then `harvey sending pause` and the `harvey signals --confirm ...` line, then run `scripts/check_phase_one.py`.

## Costs and accounts still outstanding

| Item | Status |
|---|---|
| Claude | Uses the existing Claude CLI login (a subscription). The setup made **0** headless Claude calls. |
| Discovery (OpenStreetMap) | Free, no account. Covers builders/construction only; **no telecoms tag exists**. |
| Mailbox / sending identity | Not set up. Needs a real sender name, address and domain (Google Workspace roughly $7/month is the upstream suggestion). Phase two. |
| Email verifier (Reoon / ZeroBounce / Hunter) | Free tiers need an account and API key. Not created. Without one, Writer drafts nothing. |
| Serper / DataForSEO | Not used. Serper has 2,500 free searches (account needed); DataForSEO needs a deposit. Not used. |
| Companies House | Free public search for the financial screen; not integrated. |

Outstanding spend today: **GBP 0 / USD 0**.

## Not verified

SENRAB's live website could not be read from the setup environment (the network policy blocked DNS for
`senrab.co.uk`). `skills/product_knowledge.md` therefore contains only what the owner stated (section A) and, clearly
marked unverified, a search-engine summary (section B). Re-read the site and reconcile before any draft is used.
