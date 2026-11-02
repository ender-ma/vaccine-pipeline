## 2026-09-23
- Learned: pwd, ls, ls -la, cd, mkdir, cp, mv, rm, grep, less, head/tail, find, chmod, ps/top
- Ran into: [any error you hit and how you fixed it]
- Decision: repo structure follows roadmap section 8; LICENSE = MIT (placeholder)
- Next: create GitHub repo, first commit

# Negative time will be updated
 
### 2026-10-20
- `bin/fasta_qc.py`: FASTA input validation (structure, alphabet, duplicate IDs,
  length bounds) and per-sequence QC statistics, with configurable thresholds.
- Heuristic detection of nucleotide sequences submitted as protein input.
- Test fixtures in `test_data/qc/` covering valid, empty, malformed and
  disguised-nucleotide inputs.

## [Unreleased]

## [0.1.0] - 2026-11-02

### Added
- Nextflow workflow running MAKEBLASTDB, BLASTP, FASTA_QC, PARSE_BLAST and
  FILTER_CANDIDATES end to end.
- `bin/fasta_qc.py`: FASTA validation and QC statistics with a configurable
  minimum length and a compositional nucleotide heuristic.
- `bin/filter_candidates.py`: structured candidate records in JSON and TSV.
  Every input query is recorded, including NO_HIT and FAIL_FILTER cases.
- `bin/parse_blast.py`: BLAST tabular output parsing.
- Validation gate: BLASTP consumes only FASTA_QC-validated input.
- Distinct exit codes (0 success, 1 internal error, 2 invalid input) with a
  Nextflow `errorStrategy` that ignores invalid input and retries internal
  failures.
- Configurable thresholds: `min_length`, `min_identity`, `max_evalue`,
  `min_align_length`. Threshold values and the BLAST version are recorded
  inside every candidate record.
- Unit tests under `tests/`, run with pytest.
- `.gitignore` and this changelog.

### Known limitations
- Sequence similarity to a small toy database is the only evidence type.
  This is not yet a reverse-vaccinology pipeline.
- Default thresholds are conventional, not validated against any benchmark.
- The nucleotide heuristic has a known false-positive mode for Gly/Ala/Cys-rich
  proteins.