#!/usr/bin/env bash
# run_blast.sh - run blastp safely and fail loudly
# Usage: run_blast.sh <query.fasta> <database_name> <output.tsv>

set -euo pipefail

if [[ $# -ne 3 ]]; then
    echo "Usage: run_blast.sh <query.fasta> <database_name> <output.tsv>" >&2
    exit 2
fi

query="$1"
db="$2"
out="$3"

if [[ ! -s "$query" ]]; then
    echo "ERROR: query file missing or empty: $query" >&2
    exit 3
fi

echo "INFO: running blastp on $query against $db" >&2

blastp -query "$query" \
       -db "$db" \
       -outfmt "6 qseqid sseqid pident length evalue bitscore" \
       -out "$out"

echo "INFO: done, $(wc -l < "$out") hit rows written to $out" >&2
