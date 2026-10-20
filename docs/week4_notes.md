Week 4 Notes — FASTA QC, Filtering and Git Discipline
Project: Viral Vaccine Pipeline
Author: Adeolu-Shittu Akinloluwa
Branch: `feature/week4-qc`
Status: Days 1–2 complete
---
Week 4 objective
Turn the Week 3 vertical slice (FASTA → BLAST → Python parse) into something that
refuses bad input loudly, reports what it was given, and is developed with proper
version-control discipline.
Target deliverable: FASTA → QC → BLAST → Python filtering → structured output.
Day	Focus	Status
1	Git discipline: branches, commits, `.gitignore`, CHANGELOG, issues	Done
2	Python FASTA validator + QC statistics script	Done
3	Wire validation/QC into Nextflow with proper failure behaviour	Pending
4	Filtering rules + structured JSON/TSV outputs	Pending
5	pytest tests, merge branch, tag `v0.1.0`	Pending
---
Day 1 — Git discipline
What was done
Created `.gitignore` covering `work/`, `.nextflow/`, `__pycache__/`, `results/`
and OS noise, so the repository stays small and contains only inputs and code.
Created branch `feature/week4-qc` with `git switch -c`, leaving `main` frozen at
the last working Week 3 commit.
Created `CHANGELOG.md` using the Keep a Changelog format, with an `[Unreleased]`
section and a pending `[0.1.0]` entry.
Made a commit with a subject line and an explanatory body, using the
Conventional Commits `chore:` prefix.
Pushed the branch with `git push -u origin feature/week4-qc`.
Opened four GitHub issues covering input validation, QC statistics, structured
outputs and automated tests.
Key commands
```bash
git status
git log --oneline --graph --decorate -n 15
git switch -c feature/week4-qc
git branch
git add .gitignore CHANGELOG.md
git commit -m "chore: add .gitignore and CHANGELOG for Week 4" -m "<why>"
git push -u origin feature/week4-qc
git ls-files | grep -E "^(work|\.nextflow)/"   # check for already-tracked junk
```
Concepts
A branch is a movable label pointing at one commit — not a copy of the files.
A commit is a snapshot of the whole project plus a pointer to its parent. This is
why branching is instantaneous: Git writes a 40-character commit ID into a small
file.
Commit message anatomy: subject under ~50 characters in the imperative mood,
blank line, then a body explaining why. The diff already shows what changed; it
cannot show reasoning.
Semantic versioning (`MAJOR.MINOR.PATCH`): MAJOR increments on
backwards-incompatible changes, MINOR on backwards-compatible new features, PATCH
on backwards-compatible bug fixes.
---
Day 1 quiz
Q1. In your own words, what is a Git branch — and why is creating one
essentially instantaneous?
> A git branch is another sort of version or extension of the code which can be
> used to store a certain version of code while allowing different commits from
> other branches.
Correct. The piece worth adding: a branch does not store a copy of the code.
It is a pointer to a commit, and the commit stores the snapshot. That is the
reason creation is instant.
Q2. Why does `.gitignore` have no effect on a file that was already committed
in a previous week?
> Because `.gitignore` works on files which have just been added to it. To remove
> previous versions one would have to write a git command to remove specific parts.
Correct. The precise rule: `.gitignore` only applies to untracked files.
Once a file is tracked, Git keeps tracking it regardless. The command to stop
tracking while keeping the file on disk is `git rm --cached <path>`.
Q3. What is the difference in purpose between a commit message and a CHANGELOG
entry?
> A commit message is a short title head of what was done in the code within that
> session; a changelog is a list of everything worked on or and changed.
Correct in substance. The sharper framing is audience: commit messages are
written for developers reading the history of the code; a CHANGELOG is written
for users of the software, grouped by released version, in plain language. One is
granular and chronological; the other is summarised and version-scoped.
Q4. Under semantic versioning, what does the leading `0` in `0.1.0` communicate?
> Semantic versioning X.Y.Z. X in this case 0 represents major changes which the
> codebase has undergone which could have a great effect when used.
Partly correct — needs a correction. X is indeed the MAJOR number, and MAJOR
increments signal breaking changes. But `0` specifically is a reserved special
case: major version zero means the software is in initial development and the
public API should not be considered stable. It does not mean "zero major
changes have happened"; it means "I reserve the right to break anything without
warning." A pipeline at `0.1.0` is announcing it is not yet safe to depend on.
Q5. Should `results/` be gitignored in a research project that cares about
reproducibility?
> I believe it isn't the right call because the results could help other
> researchers with reproducibility or verification; why I feel it is okay is
> because with proper versioning the results would always remain the same hence
> my results directory may be ignored by git.
Good reasoning on both sides. The position this project adopts: ignore
`results/` in Git, but make results reproducible and archivable by other means.
Git is optimised for text diffs, not large binary or regenerable outputs. A
repository that accumulates every run's output becomes slow to clone and
impossible to review.
Reproducibility is served by pinning the inputs and the environment — tool
versions, Conda environment file, parameters, tagged commit — not by storing
the outputs.
The caveat on your second point: results are only guaranteed identical if the
environment is also pinned. BLAST 2.16.0 against database version X with
recorded parameters gives the same answer; "the code is versioned" alone does
not.
When results genuinely need to be published (a benchmark set, a figure's
underlying data), the right home is a data archive with its own DOI, referenced
from the repository — not the Git history.
---
Day 2 — FASTA validation and QC
What was done
Wrote a Python script that parses FASTA, validates it, and emits QC statistics.
Validation rules: file non-empty, headers well formed, no empty sequence
records, residues restricted to the standard amino-acid alphabet, minimum
length enforced via a `--min-length` parameter.
Added a heuristic nucleotide-sequence check to catch DNA accidentally submitted
to a protein pipeline.
Distinguished exit codes: 2 for invalid input, 1 for an internal crash,
0 for success.
Used a generator (`yield`) in `parse_fasta` rather than building a list.
Concepts
Two alphabets. The nucleotide alphabet is A, C, G, T (U in RNA) plus ambiguity
codes including N. The protein alphabet is the 20 standard amino acids —
ACDEFGHIKLMNPQRSTVWY — plus U (selenocysteine), O (pyrrolysine), B, Z, J, X and
the terminator `*`.
Exit codes. `0` = success, non-zero = failure. Which non-zero value is a
design decision the script author makes, and downstream tools can branch on it.
Generators. A function containing `yield` returns an iterator that produces
items one at a time, holding only the current item in memory.
---
Day 2 quiz
Q1. Why can't a simple alphabet check catch a DNA sequence submitted to
`blastp`? Answer in terms of the two alphabets.
> Because ATCGUN are also proteins.
Right instinct, imprecise wording. The exact statement: the nucleotide
alphabet is a subset of the protein alphabet. Every one of A, C, G, T, U and N
is itself a valid single-letter amino-acid code —
Letter	As nucleotide	As amino acid
A	Adenine	Alanine
C	Cytosine	Cysteine
G	Guanine	Glycine
T	Thymine	Threonine
U	Uracil	Selenocysteine
N	Any base	Asparagine
So `ATGCGTACGT` is a syntactically perfect protein sequence. No alphabet check can
reject it, because nothing is out of alphabet. This is why the nucleotide check
has to be a compositional heuristic — "what fraction of residues fall inside
the nucleotide subset?" — rather than a membership test.
Q2. The script exits 2 for bad input and 1 for an internal crash. Why is
collapsing both into a generic 1 a bad idea for a scientific pipeline?
> Because specification on what type of error occurs can help with debugging and
> easy error readability.
Correct, and worth extending to the pipeline level. The two failures demand
different responses, and the response can be automated only if the codes
differ:
Exit 2 (bad input) is the user's problem. Nextflow should fail that sample,
report it clearly, and carry on with the remaining samples. Retrying is
pointless — the file will still be invalid.
Exit 1 (internal crash) is your problem. It may be transient (memory, disk,
a race) and is a legitimate candidate for `errorStrategy 'retry'`, and it means
there is a bug to fix.
Collapse them and Nextflow cannot tell "this FASTA is malformed" from "my code is
broken", so it either retries invalid input forever or never retries recoverable
faults.
Q3. `parse_fasta` uses `yield` instead of returning a list. What concrete
problem does that choice prevent, and when would it start to matter?
> It prevents the script from reading thousands of sequences which would help when
> larger files are being analyzed.
Correct idea, but the wording inverts it — fix this in your head. The generator
does not prevent the script from reading thousands of sequences; it reads all
of them just fine. What it prevents is holding all of them in memory
simultaneously. A list of 50,000 records exists in RAM all at once; a generator
holds one record at a time and discards it before reading the next.
When it starts to mattering for this project: the toy test files are irrelevant.
It becomes real at whole-proteome scale — a bacterial proteome is roughly
4,000–6,000 proteins and is still fine either way, but a multi-strain
pan-proteome, or a host proteome such as human (~20,000 proteins, many of them
long), is where a list-based parser starts consuming gigabytes. It also matters
the moment this runs inside Django, where several jobs may share one machine.
Q4. The nucleotide check is a heuristic with a known false-positive mode.
Describe a real protein that might trip it, and argue whether failing loudly on
such a protein is acceptable.
> A protein that might fail it is one which contains larger portions of ATCGUN in
> it, and failing it loudly would be acceptable to tell the researcher that their
> sequence might be a nucleotide.
Correct in structure; it needs a concrete example to be a complete answer.
Real candidates are proteins with strongly biased composition in Ala, Cys, Gly,
Thr and Asn:
Glycine-rich and Ala/Gly-rich structural proteins — silk fibroin and
related repeat proteins are dominated by Gly and Ala runs.
Cysteine-rich peptides — defensins, some toxins and metallothioneins carry
unusually high Cys content.
Short peptides generally, where a handful of residues can push the
composition past any threshold by chance.
On acceptability: yes, failing loudly is the right trade-off provided three
conditions hold — (i) the message says it is a heuristic and states the observed
composition, (ii) the threshold is a configurable parameter rather than a
hard-coded constant, and (iii) an explicit override flag exists. A scientific
tool may refuse to guess, but it must never refuse without telling the researcher
exactly why and how to proceed. Silent rejection would be unacceptable; loud,
explained, overridable rejection is good design.
Q5. Why is `--min-length` a parameter instead of a fixed value of 10? Give a
biological scenario.
> This is to ensure that files may be read regardless of length and to avoid
> unnecessary flagging.
Too general — here is the biological answer the question was after. The right
minimum length depends entirely on what the sequences biologically are, and
this pipeline will process several different kinds:
MHC class I epitopes are typically 8–11 residues, and class II around
13–25. A fixed minimum of 10 would silently reject a large share of valid
class I epitopes — exactly the entities this vaccine pipeline exists to work
with.
Whole-protein antigen screening is the opposite case: there, a sequence of
20 residues is almost certainly a fragment or an annotation error, and a much
higher floor than 10 is appropriate.
Signal peptides (~15–30 aa), linker-joined constructs and the OROV-style
multi-epitope vaccine constructs all sit at different scales again.
The general principle, which is the one the roadmap keeps returning to:
thresholds carrying biological meaning must be configurable and recorded with
the run, never hard-coded. A hard-coded 10 is an undocumented scientific
assumption baked into the software.
---
Carry-forward to Day 3
Wrap the validator as a Nextflow process ahead of BLAST.
Make Nextflow treat exit 2 and exit 1 differently via `errorStrategy`.
Record the `--min-length` and nucleotide-threshold values used into the run
output, so a result can be traced back to the assumptions that produced it.
