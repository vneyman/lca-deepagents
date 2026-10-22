#!/usr/bin/env python3
"""Calculate crime rates per 100,000 residents by country and year.

Rows without a valid positive population are skipped. Crime metrics are handled
independently: a missing count is displayed as NA, while an available count is
converted to a rate. The source CSV is read only; population is in millions.
"""

import argparse
import csv
from pathlib import Path


def number(value):
    """Return a number, or None for a missing/invalid value."""
    if value is None or not value.strip() or value.strip().upper() in {"NA", "N/A", "NULL"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv_file",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("g10-crime-stats.csv"),
        help="source CSV (defaults to g10-crime-stats.csv beside this script)",
    )
    args = parser.parse_args()

    rows = []
    with args.csv_file.open(newline="", encoding="utf-8-sig") as source:
        for record in csv.DictReader(source):
            population = number(record.get("population_millions_approx"))
            if population is None or population <= 0:
                continue

            antisemitic = number(record.get("antisemitic_crimes"))
            total = number(record.get("total_crimes"))
            # Counts divided by population in millions and then by 10 yield
            # rates per 100,000 people.
            antisemitic_rate = antisemitic / population / 10 if antisemitic is not None else None
            total_rate = total / population / 10 if total is not None else None
            rows.append((record["country"], record["year"], antisemitic_rate, total_rate))

    # Descending antisemitic rate; rows without that metric are placed last.
    rows.sort(key=lambda row: (row[2] is None, -(row[2] or 0), row[0], row[1]))

    headers = ("Country", "Year", "Antisemitic crimes / 100k", "Total crimes / 100k")
    rendered = [
        (country, year, "NA" if antisemitic is None else f"{antisemitic:,.2f}",
         "NA" if total is None else f"{total:,.2f}")
        for country, year, antisemitic, total in rows
    ]
    widths = [max(len(headers[i]), *(len(row[i]) for row in rendered)) for i in range(len(headers))]
    print(" | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))))
    print("-+-".join("-" * width for width in widths))
    for row in rendered:
        print(" | ".join(row[i].ljust(widths[i]) for i in range(len(headers))))


if __name__ == "__main__":
    main()
