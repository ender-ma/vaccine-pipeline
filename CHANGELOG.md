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
