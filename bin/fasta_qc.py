#!/usr/bin/env python3
"""
fasta_qc.py — validate a protein FASTA file and report QC statistics.

Exits with:
    0  input is valid
    2  input failed validation
    1  unexpected internal error
"""

import argparse
import sys
from pathlib import Path

STANDARD_AA = set("ACDEFGHIKLMNPQRSTVWY")
AMBIGUOUS_AA = set("XBZ")
ALLOWED_AA = STANDARD_AA | AMBIGUOUS_AA

NUCLEOTIDE_LETTERS = set("ACGTUN")
NUCLEOTIDE_FRACTION_THRESHOLD = 0.90
NUCLEOTIDE_MIN_LENGTH = 50


def parse_fasta(path):
    """Yield (identifier, description, sequence, header_line_number) tuples."""
    identifier = None
    description = ""
    header_line_no = 0
    chunks = []

    with open(path, "r", encoding="utf-8") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if identifier is not None:
                    yield identifier, description, "".join(chunks), header_line_no
                header = line[1:].strip()
                parts = header.split(None, 1)
                identifier = parts[0] if parts else ""
                description = parts[1] if len(parts) > 1 else ""
                header_line_no = line_no
                chunks = []
            else:
                if identifier is None:
                    raise ValueError(
                        f"line {line_no}: sequence data found before any '>' header"
                    )
                chunks.append(line.upper())

    if identifier is not None:
        yield identifier, description, "".join(chunks), header_line_no


def looks_like_nucleotide(sequence):
    """Heuristic: is this really DNA/RNA wearing a protein costume?"""
    if len(sequence) < NUCLEOTIDE_MIN_LENGTH:
        return False
    nucleotide_count = sum(1 for residue in sequence if residue in NUCLEOTIDE_LETTERS)
    return (nucleotide_count / len(sequence)) >= NUCLEOTIDE_FRACTION_THRESHOLD


def validate_and_describe(path, min_length, max_length):
    """Return (records, errors). Each record is a dict of per-sequence stats."""
    records = []
    errors = []
    seen_identifiers = {}

    for identifier, description, sequence, line_no in parse_fasta(path):
        if not identifier:
            errors.append(f"line {line_no}: header '>' has no identifier")
            continue

        if identifier in seen_identifiers:
            errors.append(
                f"line {line_no}: duplicate identifier '{identifier}' "
                f"(first seen at line {seen_identifiers[identifier]})"
            )
        else:
            seen_identifiers[identifier] = line_no

        if not sequence:
            errors.append(f"line {line_no}: record '{identifier}' has no sequence")
            continue

        illegal = sorted(set(sequence) - ALLOWED_AA)
        if illegal:
            errors.append(
                f"line {line_no}: record '{identifier}' contains illegal "
                f"character(s): {' '.join(illegal)}"
            )

        length = len(sequence)
        if length < min_length:
            errors.append(
                f"line {line_no}: record '{identifier}' length {length} "
                f"is below minimum {min_length}"
            )
        if max_length is not None and length > max_length:
            errors.append(
                f"line {line_no}: record '{identifier}' length {length} "
                f"exceeds maximum {max_length}"
            )

        if looks_like_nucleotide(sequence):
            errors.append(
                f"line {line_no}: record '{identifier}' appears to be a "
                f"nucleotide sequence, not a protein"
            )

        records.append(
            {
                "id": identifier,
                "description": description,
                "length": length,
                "ambiguous_residues": sum(1 for r in sequence if r in AMBIGUOUS_AA),
                "illegal_characters": illegal,
            }
        )

    if not records and not errors:
        errors.append("file contains no FASTA records")

    return records, errors


def print_report(path, records):
    """Write a human-readable QC summary to stdout."""
    print(f"# FASTA QC report for: {path}")
    print(f"# records: {len(records)}")

    if records:
        lengths = sorted(r["length"] for r in records)
        total = sum(lengths)
        middle = len(lengths) // 2
        median = (
            lengths[middle]
            if len(lengths) % 2
            else (lengths[middle - 1] + lengths[middle]) / 2
        )
        ambiguous_total = sum(r["ambiguous_residues"] for r in records)

        print(f"# total residues: {total}")
        print(f"# length min/median/max: {lengths[0]}/{median}/{lengths[-1]}")
        print(f"# ambiguous residues (X/B/Z): {ambiguous_total}")

    print()
    print("id\tlength\tambiguous\tdescription")
    for record in records:
        print(
            f"{record['id']}\t{record['length']}\t"
            f"{record['ambiguous_residues']}\t{record['description']}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Validate a protein FASTA file and report QC statistics."
    )
    parser.add_argument("--input", required=True, help="path to the FASTA file")
    parser.add_argument(
        "--min-length",
        type=int,
        default=10,
        help="minimum acceptable sequence length (default: 10)",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=None,
        help="maximum acceptable sequence length (default: no limit)",
    )
    args = parser.parse_args()

    path = Path(args.input)

    if not path.exists():
        print(f"ERROR: input file does not exist: {path}", file=sys.stderr)
        return 2
    if path.stat().st_size == 0:
        print(f"ERROR: input file is empty: {path}", file=sys.stderr)
        return 2

    try:
        records, errors = validate_and_describe(path, args.min_length, args.max_length)
    except ValueError as exc:
        print(f"ERROR: {path}: {exc}", file=sys.stderr)
        return 2

    if errors:
        print(f"ERROR: {len(errors)} validation problem(s) in {path}:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 2

    print_report(path, records)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"INTERNAL ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
