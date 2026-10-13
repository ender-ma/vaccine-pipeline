#!/usr/bin/env python3
"""
parse_blast.py - read a BLAST tabular file, keep significant hits, write a summary.

Expected input columns (from run_blast.sh):
    qseqid sseqid pident length evalue bitscore
"""

import argparse
import csv
import json
import sys

COLUMNS = ["qseqid", "sseqid", "pident", "length", "evalue", "bitscore"]


def read_query_ids(fasta_path):
    """Return the ID (first word after '>') of every sequence in a FASTA file."""
    ids = []
    with open(fasta_path) as handle:
        for line in handle:
            if line.startswith(">"):
                ids.append(line[1:].split()[0])
    return ids


def read_hits(tsv_path):
    """Read BLAST rows into a list of dictionaries, checking each row's shape."""
    hits = []
    with open(tsv_path) as handle:
        for line_number, row in enumerate(csv.reader(handle, delimiter="\t"), start=1):
            if not row:
                continue  # skip blank lines
            if len(row) != len(COLUMNS):
                sys.exit(
                    f"ERROR: line {line_number} has {len(row)} columns, "
                    f"expected {len(COLUMNS)}: {row}"
                )
            hit = dict(zip(COLUMNS, row))
            try:
                hit["pident"] = float(hit["pident"])
                hit["length"] = int(hit["length"])
                hit["evalue"] = float(hit["evalue"])
                hit["bitscore"] = float(hit["bitscore"])
            except ValueError as err:
                sys.exit(f"ERROR: line {line_number} has a non-numeric value: {err}")
            hits.append(hit)
    return hits


def main():
    parser = argparse.ArgumentParser(description="Filter BLAST tabular output.")
    parser.add_argument("hits", help="BLAST tabular file (6 columns)")
    parser.add_argument("queries", help="the query FASTA that was searched")
    parser.add_argument("--evalue", type=float, default=1e-5,
                        help="keep hits with e-value below this (default: 1e-5)")
    parser.add_argument("--prefix", default="blast",
                        help="prefix for output file names (default: blast)")
    args = parser.parse_args()

    query_ids = read_query_ids(args.queries)
    all_hits = read_hits(args.hits)
    kept = [h for h in all_hits if h["evalue"] < args.evalue]

    # Best hit per query = the kept hit with the highest bitscore
    best = {}
    for hit in kept:
        q = hit["qseqid"]
        if q not in best or hit["bitscore"] > best[q]["bitscore"]:
            best[q] = hit

    no_hit_queries = [q for q in query_ids if q not in best]

    # 1) filtered table, with a header row this time
    with open(f"{args.prefix}.filtered.tsv", "w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerows(kept)

    # 2) machine-readable summary
    summary = {
        "evalue_cutoff": args.evalue,
        "queries_total": len(query_ids),
        "hits_total": len(all_hits),
        "hits_kept": len(kept),
        "hits_removed": len(all_hits) - len(kept),
        "best_hit_per_query": {q: best[q]["sseqid"] for q in best},
        "queries_without_significant_hits": no_hit_queries,
    }
    with open(f"{args.prefix}.summary.json", "w") as out:
        json.dump(summary, out, indent=2)

    print(f"INFO: kept {len(kept)} of {len(all_hits)} hits "
          f"(e-value < {args.evalue})", file=sys.stderr)


if __name__ == "__main__":
    main()
