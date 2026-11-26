# Week 4 — FASTA QC, Filtering, and Git Discipline

**Project:** vaccine-pipeline
**Branch worked on:** `feature/week4-qc`
**Version at start of week:** `0.1.0`

---

## Goal of the week

Stop treating the pipeline as a chain of commands that happen to work, and start treating it as software:

1. Input data is **validated before** it reaches an expensive step (BLAST).
2. Failures are **loud, typed, and distinguishable** from each other (exit codes).
3. Every change is **traceable** to a reason (branch → commit → issue → CHANGELOG).

---

## Day 1 — Git discipline

### What was built

- `.gitignore` covering generated and environment artefacts (`work/`, `.nextflow*`, `results/`, `__pycache__/`, `*.log`).
- Feature branch `feature/week4-qc` created off `main`.
- `CHANGELOG.md` started, using Keep-a-Changelog style under an `[Unreleased]` heading.
- First structured commit pushed to the remote.
- Four GitHub issues opened to scope the week's work.

### Commands that mattered

```bash
git checkout -b feature/week4-qc        # create label at current commit, switch to it
git add .gitignore CHANGELOG.md
git commit -m "chore: add gitignore and changelog scaffolding"
git push -u origin feature/week4-qc     # -u links local branch to remote for future bare `git push`
```

### Concepts — corrected answers

**A branch is a movable pointer to a commit.** It is not a copy of the working tree. Creating one is instant because only a label is written. Each commit moves the label forward. Deleting a branch deletes the label, not the commits it pointed at.

**`.gitignore` only applies to untracked files.** Once a file is tracked, Git keeps tracking it regardless of ignore rules. To stop tracking something already committed:

```bash
git rm --cached <path>   # removes from the index, keeps the file on disk
git commit -m "chore: stop tracking generated output"
```

**Commit message vs CHANGELOG — different audiences.**

| | Commit message | CHANGELOG |
|---|---|---|
| Audience | Developer reading history | User of the pipeline |
| Scope | One change | One release |
| Content | *Why* this change was made | *What* visibly changed |
| Editable | No (history is immutable) | Yes (curated by hand) |

Fifty commits may collapse into four CHANGELOG lines.

**Semantic versioning `MAJOR.MINOR.PATCH`.** MAJOR = breaking changes, MINOR = backward-compatible features, PATCH = backward-compatible fixes. A **leading `0`** is special: `0.y.z` declares *initial development — the public interface is unstable and may change at any time*. Tagging `1.0.0` is a promise that breaking changes will only arrive with a MAJOR bump. This pipeline stays below `1.0.0` until the CLI flags and output schema settle.

**Should `results/` be gitignored? Yes.** Git versions *inputs* — code, config, parameters — so that outputs can be regenerated. Committing outputs stores the answer instead of the method, and because Git keeps a full object for every version of a changed file, repeated pipeline runs permanently bloat the repository. Reproducibility is achieved by pinning the code commit, the parameters, **and the reference database version**; results themselves are shared as release artefacts or deposited (Zenodo/figshare) with a DOI that cites the producing commit.

---

## Day 2 — FASTA validator and QC script

### What was built

- A Python FASTA validator / QC script.
- `--min-length` parameter for length-based filtering.
- A nucleotide-vs-protein heuristic (character composition of the sequence alphabet).
- A typed exit-code contract.

### Exit-code contract

| Code | Meaning | Pipeline response |
|---|---|---|
| `0` | All sequences valid | Continue to BLAST |
| `1` | Malformed / unusable input | Fail the run |
| `2` | Valid file, but some sequences filtered out | Continue, with a warning |

This is the core idea of the day: an exit code is the **machine-readable** half of the output. `stdout` is for data, `stderr` is for humans, and the exit status is what Nextflow actually branches on.

### Debugging notes

- An `--input` vs `--in` argparse mismatch between the script's parser and the Nextflow process call caused a silent-looking failure; the lesson is that the process script block and the Python CLI are a contract that must match exactly.

---

## Day 3 — Wiring QC into the pipeline as a gate

### What was built

- `FASTA_QC` process added to `main.nf`, placed **before** `BLASTP`.
- `BLASTP` now consumes `FASTA_QC.out.validated` — so BLAST is structurally incapable of running on unvalidated input.
- `errorStrategy` branching on exit status, so code `2` is tolerated while code `1` halts the run.
- `min_length` exposed as a pipeline-level `param` rather than hard-coded in the script.

### Why the channel dependency matters

Nextflow has no concept of "step order" written by hand. Order is **inferred from data dependencies**. By making `BLASTP` take `FASTA_QC.out.validated` as its input channel, the gate is enforced by the dataflow graph itself, not by a convention a future contributor could forget.

### Debugging notes

- A missing `toy_db.fasta` surfaced as a cryptic failure inside the work directory. The habit to keep: when a process fails, go to the hashed `work/` directory printed in the error, and read `.command.err`, `.command.sh`, and `.exitcode` before changing any code.

---

## Day 4 — Filtering rules and structured outputs

> Fill in the specifics from your own run before committing this file.

### What was built

- Filtering rules applied to QC'd sequences (length, ambiguous-character fraction, duplicate IDs).
- Structured machine-readable output written alongside the FASTA: JSON for the run summary, TSV for the per-sequence table.

### Why structured output instead of printed text

A printed summary is for a human reading a terminal once. A JSON/TSV artefact is what the **next process**, a test, or a report consumes. The rule: anything a downstream step needs must be a file in a channel, never something scraped from log text.

Record here: number of sequences in, number passing, number filtered and why, and the exact `min_length` used.

---

## Day 5 — Merging Week 4 into `main`

### Steps

1. Final commit on `feature/week4-qc`, CHANGELOG updated under `[Unreleased]`.
2. Push the branch; open a pull request `feature/week4-qc → main` on GitHub.
3. Link the PR to the four issues opened on Day 1 using closing keywords (`Closes #1`) so they close automatically on merge.
4. Review your own diff file by file before merging — this is the step that catches accidentally committed `work/` files and leftover debug prints.
5. Merge, then delete the remote branch.

### Verifying the merge actually happened

```bash
git checkout main
git pull                                   # bring the merge commit down locally
git log --oneline --graph --decorate -10   # expect the Week 4 commits on main
git branch --merged main                   # feature/week4-qc should be listed
```

If `feature/week4-qc` appears in `git branch --merged main`, every commit on it is reachable from `main`. That is the definitive local proof.

---

## Week 4 summary

| Area | State at end of week |
|---|---|
| Input validation | Enforced as a pipeline gate before BLAST |
| Failure handling | Typed exit codes with `errorStrategy` branching |
| Parameterisation | `min_length` configurable at the pipeline level |
| Git hygiene | `.gitignore`, feature branch, structured commits, CHANGELOG, issues |
| Version | `0.1.0` — still pre-stable, interface may change |

### Carried into Week 5

- Automated tests for the QC script (the exit-code contract is now testable).
- Keeping the CHANGELOG updated *in the same commit* as the change, not retroactively.
