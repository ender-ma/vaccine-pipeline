## 2026-09-23
- Learned: pwd, ls, ls -la, cd, mkdir, cp, mv, rm, grep, less, head/tail, find, chmod, ps/top
- Ran into: [any error you hit and how you fixed it]
- Decision: repo structure follows roadmap section 8; LICENSE = MIT (placeholder)
- Next: create GitHub repo, first commit 
# Changelog

All notable changes to this project are documented in this file.
Format based on Keep a Changelog; versioning follows Semantic Versioning.

## [Unreleased]

### Added
- `.gitignore` covering Nextflow work directories, Python caches and results output.
- This changelog.

## [0.1.0] - Pending

### Added
- Nextflow workflow (`main.nf`) running MAKEBLASTDB and BLASTP processes.
- `bin/run_blast.sh` wrapper script for manual BLAST execution.
- `bin/parse_blast.py` parsing BLAST tabular output into filtered hits and a summary.
- Conda environment `vp-blast` with BLAST+ 2.16.0.
- Toy workflows and test data under `workflows/toy/` and `test_data/`.
- Week 2 and Week 3 notes in `docs/`.
