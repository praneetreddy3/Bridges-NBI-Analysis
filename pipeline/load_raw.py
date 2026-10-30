"""Load the raw FHWA NBI extracts into DuckDB as raw.nbi_bridges.

This is the "EL" of ELT: copy the source files as-is (every column as text) into the
warehouse. All cleaning happens later in dbt, so the raw table is always a faithful
copy of what FHWA delivered and can be re-checked at any time.

Idempotent: the table is rebuilt from the files on every run (CREATE OR REPLACE),
so running it twice gives the same result.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILES = ["2024_part1.txt", "datasetfinal_2025.txt"]


def sql_path(p: Path) -> str:
    """Quote a file path for use inside a SQL string literal."""
    return str(p).replace("'", "''")


def load(raw_dir: Path, db_path: Path, files: list[str]) -> int:
    missing = [f for f in files if not (raw_dir / f).exists()]
    if missing:
        raise FileNotFoundError(f"Raw files not found in {raw_dir}: {missing}")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    # FHWA InfoBridge exports wrap text in single quotes. Read every column as text
    # so nothing (like 15-digit structure numbers) gets reinterpreted on the way in.
    sq = "'"  # SQL literal for a single-quote character is: ' + '' + '
    selects = [
        f"""SELECT *, '{f}' AS _source_file
            FROM read_csv('{sql_path(raw_dir / f)}', header = true,
                          quote = '{sq}{sq}', all_varchar = true)"""
        for f in files
    ]
    # UNION ALL BY NAME lines columns up by name, because the yearly files list
    # them in a different order.
    con.execute(
        "CREATE OR REPLACE TABLE raw.nbi_bridges AS "
        + " UNION ALL BY NAME ".join(selects)
    )
    con.execute(
        "ALTER TABLE raw.nbi_bridges ADD COLUMN _loaded_at TIMESTAMP DEFAULT current_timestamp"
    )
    n = con.execute("SELECT count(*) FROM raw.nbi_bridges").fetchone()[0]
    con.close()
    return n


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw-dir", type=Path,
                    default=Path(os.getenv("NBI_RAW_DIR", ROOT / "data" / "raw")))
    ap.add_argument("--db", type=Path,
                    default=Path(os.getenv("NBI_DUCKDB_PATH", ROOT / "warehouse" / "nbi.duckdb")))
    ap.add_argument("--files", nargs="+", default=DEFAULT_FILES)
    args = ap.parse_args()

    n = load(args.raw_dir, args.db, args.files)
    print(f"Loaded {n:,} rows into raw.nbi_bridges ({args.db})")


if __name__ == "__main__":
    main()
