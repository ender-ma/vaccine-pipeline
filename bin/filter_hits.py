#!/usr/bin/env python3
"""Normalise BLAST tabular output into the project's internal hit schema.

Reads BLAST outfmt 6 and emits JSON and TSV with filter annotations.
Does not discard hits; it annotates them with pass/fail and reasons.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

SCHEMA_VERSION = "0.1.0"

# BLAST outfmt 6 default column order
BLAST_COLUMNS = [
    "query_id", "subject_id", "percent_identity", "alignment_length",
    "mismatches", "gap_opens", "q_start", "q_end",
    "s_start", "s_end", "evalue", "bitscore",
]

NUMERIC_FIELDS = {
    "percent_identity": float, "alignment_length": int,
    "mismatches": int, "gap_opens": int,
    "q_start": int, "q_end": int, "s_start": int, "s_end": int,
    "evalue": float, "bitscore": float,
}


def parse_blast_tabular(path):
    """Yield one dict per BLAST hit, with numeric fields converted."""
    ...


def compute_query_coverage(hit, query_lengths):
    """Return aligned fraction of the query sequence, 0.0-1.0."""
    ...


def apply_filters(hit, thresholds):
    """Annotate a hit with passed_filters and filter_reasons.

    Returns the hit dict with two keys added. Never drops a hit.
    """
    reasons = []
    if hit["evalue"] > thresholds["max_evalue"]:
        reasons.append("evalue_above_threshold")
    ...
    hit["passed_filters"] = len(reasons) == 0
    hit["filter_reasons"] = reasons
    return hit


def load_query_lengths(fasta_path):
    """Map query_id -> sequence length, needed for coverage."""
    ...


def write_json(records, path, thresholds, source_file):
    """Write records plus a provenance block."""
    ...


def write_tsv(records, path):
    """Write a flat tabular view of the same records."""
    ...


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True,
                        help="BLAST tabular output (outfmt 6)")
    parser.add_argument("--query-fasta", required=True,
                        help="Query FASTA, used to compute coverage")
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--tsv-out", required=True)
    parser.add_argument("--max-evalue", type=float, default=1e-5)
    parser.add_argument("--min-identity", type=float, default=30.0)
    parser.add_argument("--min-coverage", type=float, default=0.50)
    args = parser.parse_args()
    ...


if __name__ == "__main__":
    main()
