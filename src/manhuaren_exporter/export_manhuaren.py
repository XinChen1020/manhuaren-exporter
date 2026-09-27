#!/usr/bin/env python3
"""
Export saved manga data from a Manhuaren SQLite database.

Examples:
    python3 export_manhuaren.py ~/path/to/database.sqlite
    python3 export_manhuaren.py ~/path/to/database.sqlite --format json
    python3 export_manhuaren.py ~/path/to/database.sqlite --list-tables
    python3 export_manhuaren.py ~/path/to/database.sqlite --describe yq__collect
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Iterable


DEFAULT_TABLE = "yq__collect"


def open_read_only(db_path: Path) -> sqlite3.Connection:
    """Open SQLite database in read-only mode."""
    if not db_path.is_file():
        raise FileNotFoundError(f"Database not found: {db_path}")

    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def quote_identifier(name: str) -> str:
    """Safely quote a SQLite identifier such as a table name."""
    return '"' + name.replace('"', '""') + '"'


def get_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    return [row["name"] for row in rows]


def ensure_table_exists(conn: sqlite3.Connection, table: str) -> None:
    if table not in get_tables(conn):
        raise ValueError(
            f"Table {table!r} does not exist. "
            "Use --list-tables to see available tables."
        )


def describe_table(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    ensure_table_exists(conn, table)
    return conn.execute(
        f"PRAGMA table_info({quote_identifier(table)})"
    ).fetchall()


def fetch_rows(conn: sqlite3.Connection, table: str) -> tuple[list[str], list[sqlite3.Row]]:
    ensure_table_exists(conn, table)
    cursor = conn.execute(f"SELECT * FROM {quote_identifier(table)}")
    columns = [description[0] for description in cursor.description]
    return columns, cursor.fetchall()


def normalize_value(value: Any) -> Any:
    """
    Convert values that JSON/CSV cannot represent directly.

    SQLite BLOB values are encoded as base64 with a clear prefix.
    """
    if isinstance(value, bytes):
        return "base64:" + base64.b64encode(value).decode("ascii")
    return value


def export_csv(
    output_path: Path,
    columns: list[str],
    rows: Iterable[sqlite3.Row],
) -> None:
    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([normalize_value(row[col]) for col in columns])


def export_json(
    output_path: Path,
    columns: list[str],
    rows: Iterable[sqlite3.Row],
) -> None:
    data = [
        {col: normalize_value(row[col]) for col in columns}
        for row in rows
    ]
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export a Manhuaren SQLite table to CSV or JSON."
    )
    parser.add_argument(
        "database",
        type=Path,
        help="Path to the Manhuaren .sqlite database",
    )
    parser.add_argument(
        "--table",
        default=DEFAULT_TABLE,
        help=f"Table to export (default: {DEFAULT_TABLE})",
    )
    parser.add_argument(
        "--format",
        choices=("csv", "json"),
        default="csv",
        help="Output format (default: csv)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path. Defaults to <table>.csv/json in the current directory.",
    )
    parser.add_argument(
        "--list-tables",
        action="store_true",
        help="List available SQLite tables and exit.",
    )
    parser.add_argument(
        "--describe",
        metavar="TABLE",
        help="Show column information for a table and exit.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        with open_read_only(args.database) as conn:
            if args.list_tables:
                for table in get_tables(conn):
                    print(table)
                return 0

            if args.describe:
                rows = describe_table(conn, args.describe)
                print(f"{'cid':>3}  {'name':<30} {'type':<15} {'notnull':<7} {'pk':<2}")
                print("-" * 65)
                for row in rows:
                    print(
                        f"{row['cid']:>3}  "
                        f"{row['name']:<30} "
                        f"{(row['type'] or ''):<15} "
                        f"{row['notnull']:<7} "
                        f"{row['pk']:<2}"
                    )
                return 0

            columns, rows = fetch_rows(conn, args.table)

            output = args.output or Path(f"{args.table}.{args.format}")
            output = output.expanduser()

            if args.format == "csv":
                export_csv(output, columns, rows)
            else:
                export_json(output, columns, rows)

            print(f"Exported {len(rows)} rows from {args.table}")
            print(f"Saved to: {output.resolve()}")
            return 0

    except (FileNotFoundError, sqlite3.Error, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
