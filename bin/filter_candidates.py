#!/usr/bin/env python3
"""Convert parsed BLAST hits plus QC results into structured candidate records.

Emits one record per input query — including queries that failed QC or
produced no hits — so that absence is always explicit.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_VERSION = "0.1.0"

EXIT_OK = 0
EXIT_INTERNAL = 1
EXIT_BAD_INPUT = 2


def read_tsv(path):
    """Read a TSV with a header row into a list of dicts."""
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def read_query_ids(fasta_path):
    """Collect every sequence ID from the query FASTA, in file order."""
    ids = []
    with open(fasta_path) as fh:
        for line in fh:
            if line.startswith(">"):
                ids.append(line[1:].strip().split()[0])
    return ids


def passes_thresholds(hit, min_identity, max_evalue, min_align_length):
    """Return (bool, list_of_failure_reasons) for a single BLAST hit."""
    reasons = []
    try:
        if float(hit["pident"]) < min_identity:
            reasons.append(f"identity {hit['pident']} < {min_identity}")
        if float(hit["evalue"]) > max_evalue:
            reasons.append(f"evalue {hit['evalue']} > {max_evalue}")
        if int(hit["length"]) < min_align_length:
            reasons.append(f"alignment length {hit['length']} < {min_align_length}")
    except (KeyError, ValueError) as exc:
        raise ValueError(f"malformed hit row: {exc}") from exc
    return (len(reasons) == 0, reasons)


def build_records(query_ids, hits, thresholds, blast_version):
    """Build one candidate record per query ID."""
    by_query = defaultdict(list)
    for hit in hits:
        by_query[hit["qseqid"]].append(hit)

    records = []
    for qid in query_ids:
        record = {
            "query_id": qid,
            "status": None,
            "reasons": [],
            "n_hits_total": len(by_query.get(qid, [])),
            "n_hits_passing": 0,
            "best_hit": None,
            "thresholds": thresholds,
            "tool_versions": {
                "filter_candidates.py": SCRIPT_VERSION,
                "blast": blast_version,
            },
        }

        candidate_hits = by_query.get(qid, [])
        if not candidate_hits:
            record["status"] = "NO_HIT"
            record["reasons"].append("no BLAST hits returned for this query")
            records.append(record)
            continue

        passing = []
        rejection_reasons = []
        for hit in candidate_hits:
            ok, why = passes_thresholds(
                hit,
                thresholds["min_identity"],
                thresholds["max_evalue"],
                thresholds["min_align_length"],
            )
            if ok:
                passing.append(hit)
            else:
                rejection_reasons.extend(why)

        record["n_hits_passing"] = len(passing)

        if passing:
            best = max(passing, key=lambda h: float(h["bitscore"]))
            record["best_hit"] = {
                "subject_id": best["sseqid"],
                "identity": float(best["pident"]),
                "evalue": float(best["evalue"]),
                "bitscore": float(best["bitscore"]),
                "alignment_length": int(best["length"]),
            }
            record["status"] = "PASS"
        else:
            record["status"] = "FAIL_FILTER"
            record["reasons"] = sorted(set(rejection_reasons))

        records.append(record)

    return records


def write_tsv(records, path):
    """Flat TSV view — one row per query, for quick human inspection."""
    columns = [
        "query_id", "status", "n_hits_total", "n_hits_passing",
        "best_subject", "best_identity", "best_evalue", "best_bitscore",
        "reasons",
    ]
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(columns)
        for r in records:
            bh = r["best_hit"] or {}
            writer.writerow([
                r["query_id"],
                r["status"],
                r["n_hits_total"],
                r["n_hits_passing"],
                bh.get("subject_id", "NA"),
                bh.get("identity", "NA"),
                bh.get("evalue", "NA"),
                bh.get("bitscore", "NA"),
                "; ".join(r["reasons"]) if r["reasons"] else "NA",
            ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hits", required=True, help="parsed BLAST hits TSV")
    parser.add_argument("--query", required=True, help="query FASTA")
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-tsv", required=True)
    parser.add_argument("--min-identity", type=float, default=30.0)
    parser.add_argument("--max-evalue", type=float, default=1e-5)
    parser.add_argument("--min-align-length", type=int, default=30)
    parser.add_argument("--blast-version", default="unknown")
    args = parser.parse_args()

    for path in (args.hits, args.query):
        if not Path(path).is_file():
            print(f"ERROR: input file not found: {path}", file=sys.stderr)
            return EXIT_BAD_INPUT

    thresholds = {
        "min_identity": args.min_identity,
        "max_evalue": args.max_evalue,
        "min_align_length": args.min_align_length,
    }

    try:
        hits = read_tsv(args.hits)
        query_ids = read_query_ids(args.query)
    except (OSError, csv.Error) as exc:
        print(f"ERROR: could not read inputs: {exc}", file=sys.stderr)
        return EXIT_BAD_INPUT

    if not query_ids:
        print(f"ERROR: no sequence IDs found in {args.query}", file=sys.stderr)
        return EXIT_BAD_INPUT

    records = build_records(query_ids, hits, thresholds, args.blast_version)

    summary = {
        "n_queries": len(records),
        "n_pass": sum(1 for r in records if r["status"] == "PASS"),
        "n_fail_filter": sum(1 for r in records if r["status"] == "FAIL_FILTER"),
        "n_no_hit": sum(1 for r in records if r["status"] == "NO_HIT"),
    }

    with open(args.out_json, "w") as fh:
        json.dump({"summary": summary, "candidates": records}, fh, indent=2)
    write_tsv(records, args.out_tsv)

    print(
        f"{summary['n_queries']} queries: "
        f"{summary['n_pass']} pass, "
        f"{summary['n_fail_filter']} filtered out, "
        f"{summary['n_no_hit']} without hits",
        file=sys.stderr,
    )
    return EXIT_OK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — deliberate top-level guard
        print(f"INTERNAL ERROR: {exc}", file=sys.stderr)
        sys.exit(EXIT_INTERNAL)
