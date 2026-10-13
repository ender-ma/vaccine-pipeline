# Week 3 Notes: Conda + BLAST + first scientific process

**Deliverable (done):** Nextflow runs BLAST and Python consumes the result.

Pipeline: `MAKEBLASTDB -> BLASTP -> PARSE_BLAST`

Files built this week:
- `envs/blast.yml`: conda env `vp-blast` (Python 3.11, BLAST+ 2.16.0, pandas)
- `test_data/blast/toy_db.fasta`, `toy_query.fasta`: invented test proteins
- `bin/run_blast.sh`: BLAST wrapper that fails loudly
- `bin/parse_blast.py`: filters hits (e-value < 1e-5), writes filtered table + JSON summary
- `main.nf`, `nextflow.config`: the pipeline and its settings
- `docs/versions.md`: tool and database versions

Run it:
    conda activate vp-blast
    nextflow run main.nf

---

## Day 1: Conda environment

**Q: Why not install BLAST into `base`?**
A: Isolation. Installing other tools into base can change libraries BLAST depends on and break it. A dedicated env stays untouched and can be rebuilt from `envs/blast.yml`.

**Q: Difference between `>` and `>>`?**
A: `>` creates or overwrites a file. `>>` appends to the end of it.

**Q: What does `which blastn` tell you?**
A: Which copy of a program the shell will actually run. A path containing `envs/vp-blast/bin/` proves it's the env's copy.

## Day 2: First BLAST search by hand

Results: query1 -> toy_prot_A (95.7%, e-value 2e-35) = real hit; query1 -> toy_prot_B (e-value 0.049) = noise; query2 -> no rows = negative control passed.

**Q: Why run `makeblastdb` before searching?**
A: It converts the database FASTA into an indexed format so BLAST can search it fast, like a dictionary's index. It does not create the results file.

**Q: Which column proves the toy_prot_B hit is noise?**
A: Columns 11 (e-value) and 12 (bitscore). E-value 0.049 = likely chance; bitscore 15.8 = weak. Columns 9-10 only show WHERE the match is. Rule: keep hits with e-value < 1e-5.

**Q: query2 has no rows. Is that a failure?**
A: No. It was the negative control, expected to find nothing, so it PASSED. No hits = missing rows = normal result.

**Q: Why not commit `db/` to git?**
A: It's generated: it can be rebuilt from the FASTA with one command, it's binary, and real databases are huge. Rule: commit inputs and code; ignore anything a command can recreate.

## Day 3: stdout, stderr, exit codes, paths

- stdout (1) = data; stderr (2) = messages/errors; exit code 0 = success, non-zero = failure
- `> file` saves stdout, `2> file` saves stderr, `echo $?` shows the last exit code
- Expected exit codes: A normal run = 0, B missing query = 1, C wrong database = 2, D bad -evalue = 1
- A crashed run can still leave an EMPTY output file, so only the exit code tells crash from "no hits"

**Q: Which channel for data, which for messages? Why keep them apart?**
A: Data -> stdout, messages -> stderr. Output files then contain only clean data a parser can read, while errors stay visible or go to a log.

**Q: An output file is empty. How do you tell a crash from "no hits"?**
A: Check the exit code right after (`echo $?`). 0 = ran fine, no hits. Non-zero = crashed.

**Q: Why did the command fail from `~`?**
A: Relative paths are looked up from the current folder. From `~`, `test_data/...` doesn't exist. Absolute paths work from anywhere.

**Q: What does `set -euo pipefail` protect against?**
A: The script stops at the first error instead of continuing with broken data, catches misspelled variables, and catches failures inside pipes, then exits non-zero so the failure can't be missed.

**Q: First file to read when a Nextflow task fails?**
A: `.command.err` (stderr), then `.exitcode`.

## Day 4: BLAST inside Nextflow

Work folder files: `.command.sh` = script run, `.command.out` = stdout, `.command.err` = stderr, `.exitcode` = exit code.

**Q: Why does `main.nf` sit at the top of the repo?**
A: Nextflow only adds `bin/` to the PATH when `bin/` sits next to `main.nf`. (`nextflow.config` is the settings file, like Django's settings.py.)

**Q: Why build the database inside a `blastdb` folder?**
A: A BLAST database is several files (.pin, .phr, .psq...). A folder bundles them into ONE item that can travel through a channel.

**Q: What goes wrong with 10 queries if `.first()` is removed?**
A: The database would be used up by the first query, and the other 9 would be silently skipped. `.first()` makes it a reusable value channel.

**Q: How were failures A and B caught differently?**
A: A (missing input) was caught by Nextflow BEFORE any task ran (`checkIfExists`), a pre-flight check. B (wrong db name) happened WHILE the task ran: BLAST exited with 2 and Nextflow saw the non-zero exit code. Catch problems as early as possible.

**Q: What does `publishDir` do, and why?**
A: It copies outputs from the random, temporary `work/` folders to a permanent, predictable place (`results/blast/`).

## Day 5: Python parser

**Q: Why does the parser need the query FASTA too?**
A: A query with no hits leaves no row in the BLAST table. The FASTA is the full list of what was searched, so the parser can report queries without hits.

**Q: Why does BLASTP output a tuple?**
A: To keep each hits file paired with the query it came from. Parallel tasks finish in any order, so separate channels could mismatch them.

**Q: Why exit with code 1 on a broken row instead of skipping it?**
A: Skipping gives a summary that looks fine but is wrong. Failing forces you to notice, and Nextflow stops the pipeline.

**Q: Why did only PARSE_BLAST rerun after changing `--evalue`?**
A: Nextflow fingerprints (hashes) each task's inputs and command. Only PARSE_BLAST's command changed, so the other two were cached.

**Q: Why test the parser by hand before adding it to Nextflow?**
A: Isolation. If it breaks inside Nextflow later, you know the script isn't the cause. Edge cases (empty, broken) are also faster to test by hand.

---

## Week 3 rules to remember
1. One environment per stage; never install into `base`.
2. Always include a positive and a negative control in tests.
3. Data -> stdout, messages -> stderr.
4. Exit codes, not file existence, decide success.
5. Commit inputs and code; ignore what a command can recreate.
6. Test each script alone before adding it to the pipeline.
