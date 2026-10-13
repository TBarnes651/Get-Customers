"""Export discovered companies (research candidates) with their observed signals.

`harvey export` only exports PROSPECTS (people), which only the Scout agent creates, so it
cannot see what `harvey discover` / `harvey profile` collected. This reads the same SQLite
database, read-only, and writes a review sheet.

Financial eligibility is NEVER computed. Those columns start as `unknown` for a human to fill
in from an identified filing and its date.

Run:  .venv/bin/python scripts/export_candidates.py [--out exports/candidates.csv]
"""
import argparse
import csv
import sqlite3
from collections import defaultdict
from pathlib import Path

from harvey.state import DB_PATH

REVIEW_COLUMNS = [
    "financial_eligibility",   # unknown | eligible | ineligible
    "filing_source_and_date",  # e.g. Companies House accounts, year end 31 March 2025
    "sector_fit_checked",      # construction / telecoms / neither
    "operational_complexity_evidence",
    "observed_facts_with_urls",
    "hypotheses_unverified",
    "review_status",           # research | approved_for_draft | rejected
]
SIGNAL_COLUMNS = {
    "CONTACT_FOUND": "named_contacts",
    "DECISION_MAKER_TITLE": "decision_maker_titles",
    "HIRING_ROLE": "advertised_roles",
    "CONTACT_FORM_URL": "contact_form",
    "FOUND_IN_SERP": "found_via",
}


def safe(value) -> str:
    """Scraped text must not become a spreadsheet formula."""
    s = "" if value is None else str(value)
    return "'" + s if s[:1] in ("=", "+", "-", "@") else s


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="exports/candidates.csv")
    ap.add_argument("--limit", type=int, default=0, help="Max companies (0 = all)")
    args = ap.parse_args()

    if not Path(DB_PATH).exists():
        raise SystemExit(f"No database at {DB_PATH}. Run `harvey discover` first.")
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row

    obs = defaultdict(lambda: defaultdict(list))
    for r in db.execute("SELECT company_id, signal_code, value_num, value_text, evidence_url "
                        "FROM observations ORDER BY observed_at"):
        text = r["value_text"] or ("" if r["value_num"] is None else str(r["value_num"]))
        item = f"{text} <{r['evidence_url']}>" if r["evidence_url"] else text
        obs[r["company_id"]][r["signal_code"]].append(item)

    sql = "SELECT * FROM companies ORDER BY created_at"
    if args.limit:
        sql += f" LIMIT {int(args.limit)}"
    companies = db.execute(sql).fetchall()

    cols = (["company", "domain", "website", "location", "source_category", "source", "source_url"]
            + list(SIGNAL_COLUMNS.values()) + REVIEW_COLUMNS)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for c in companies:
            row = {"company": c["name"], "domain": c["domain"], "website": c["website"],
                   "location": c["location"], "source_category": c["industry"],
                   "source": c["source"], "source_url": c["source_url"],
                   "financial_eligibility": "unknown", "review_status": "research"}
            for code, col in SIGNAL_COLUMNS.items():
                row[col] = " | ".join(obs[c["id"]].get(code, []))
            w.writerow({k: safe(v) for k, v in row.items()})
    print(f"Exported {len(companies)} candidate(s) to {out}")


if __name__ == "__main__":
    main()
