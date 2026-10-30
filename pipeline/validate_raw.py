"""Data-quality gate on raw.nbi_bridges, run before any transformation.

Each check is a SQL query that counts problems. If any check fails the script exits
with code 1, which makes the Airflow task fail and stops everything downstream.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_COLUMNS = [
    "Year", "1 - State Code", "8 - Structure Number", "22 - Owner Agency",
    "27 - Year Built", "43A - Main Span Material", "43B - Main Span Design",
    "48 - Length of Maximum Span (ft.)", "29 - Average Daily Traffic",
    "109 - Average Daily Truck Traffic (Percent ADT)", "31 - Design Load Descriptor",
    "30 - Year of Average Daily Traffic", "70 - Bridge Posting Code",
]


def run_checks(con, min_rows: int) -> list[dict]:
    cols = {r[0] for r in con.execute("DESCRIBE raw.nbi_bridges").fetchall()}
    missing = [c for c in REQUIRED_COLUMNS if c not in cols]
    checks = [{"check": "required_columns_present", "value": missing, "passed": not missing}]
    if missing:
        return checks

    def scalar(sql: str):
        return con.execute(sql).fetchone()[0]

    total = scalar("SELECT count(*) FROM raw.nbi_bridges")
    years = sorted(r[0] for r in con.execute(
        'SELECT DISTINCT "Year" FROM raw.nbi_bridges').fetchall())
    null_ids = scalar("""SELECT count(*) FROM raw.nbi_bridges
                         WHERE nullif(trim("8 - Structure Number"), '') IS NULL""")
    # Excel turns long IDs into things like 1.00001E+14; that must never reach the warehouse.
    sci_ids = scalar("""SELECT count(*) FROM raw.nbi_bridges
                        WHERE "8 - Structure Number" ILIKE '%E+%'""")
    bad_posting = scalar("""SELECT count(*) FROM raw.nbi_bridges
                            WHERE "70 - Bridge Posting Code" IS NOT NULL
                              AND trim("70 - Bridge Posting Code") NOT IN ('0','1','2','3','4','5')""")
    null_posting = scalar("""SELECT count(*) FROM raw.nbi_bridges
                             WHERE "70 - Bridge Posting Code" IS NULL""")
    bad_year_built = scalar("""SELECT count(*) FROM raw.nbi_bridges
                               WHERE try_cast("27 - Year Built" AS INTEGER) IS NULL""")

    checks += [
        {"check": "row_count_at_least", "value": total, "threshold": min_rows,
         "passed": total >= min_rows},
        {"check": "both_years_present", "value": years, "passed": years == ["2024", "2025"]},
        {"check": "no_missing_structure_numbers", "value": null_ids, "passed": null_ids == 0},
        {"check": "no_scientific_notation_ids", "value": sci_ids, "passed": sci_ids == 0},
        {"check": "posting_codes_valid", "value": bad_posting, "passed": bad_posting == 0},
        # A handful of missing posting codes is tolerated (dbt quarantines them);
        # more than 0.1% means the extract itself is broken.
        {"check": "missing_posting_codes_below_0.1pct", "value": null_posting,
         "passed": null_posting <= 0.001 * total},
        {"check": "year_built_parses", "value": bad_year_built, "passed": bad_year_built == 0},
    ]
    return checks


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path,
                    default=Path(os.getenv("NBI_DUCKDB_PATH", ROOT / "warehouse" / "nbi.duckdb")))
    ap.add_argument("--min-rows", type=int, default=1_000_000)
    args = ap.parse_args()

    con = duckdb.connect(str(args.db), read_only=True)
    checks = run_checks(con, args.min_rows)
    con.close()

    print(json.dumps(checks, indent=2, default=str))
    failed = [c["check"] for c in checks if not c["passed"]]
    if failed:
        print(f"VALIDATION FAILED: {failed}", file=sys.stderr)
        sys.exit(1)
    print("All raw-data checks passed.")


if __name__ == "__main__":
    main()
