# Nextflow Cheat Sheet: Week 2

## The big idea
Nextflow is DATAFLOW. I declare processes (units of work) and connect them
with channels (streams of data). Nextflow works out the order and the
parallelism from the connections.
- process = a worker at a station
- channel = the conveyor belt feeding that worker

## Process anatomy
    process NAME {
        publishDir "results", mode: 'copy'   // optional: copy outputs somewhere tidy

        input:
        path fasta          // a file (staged into the work dir)

        output:
        path "result.txt"   // a file the script creates

        script:
        """
        my_command $fasta > result.txt
        """
    }

Mapping to science: input file -> script (the command I would type) -> output file.

## Input / output types
- val    = plain value (text, number)
- path   = a file (Nextflow copies/symlinks it into an isolated work dir)
- stdout = whatever the script prints (cannot be handed on as a file)
Rule: to pass a result to the NEXT process, save it as a file (output: path).

## Channels
    Channel.of('a', 'b', 'c')                                    // list of values
    Channel.fromPath(params.fasta, checkIfExists: true)          // a file, fail early if missing

## The workflow block (wiring)
    workflow {
        fasta_ch   = Channel.fromPath(params.fasta, checkIfExists: true)
        COUNT_SEQS(fasta_ch)                    // call like a function
        headers_ch = EXTRACT_HEADERS(fasta_ch)  // keep the output channel
        UNIQUE_HEADERS(headers_ch)              // chain: output feeds next input
        COUNT_SEQS.out.view()                   // print a process result
    }
- One channel can feed several processes (branching).
- Pipe style also works:  Channel.of(...) | PROCESS | view

## Parameters
    params.fasta  = "test_data/test.fasta"    // default value inside the script
    nextflow run file.nf --fasta other.fasta  // double dash overrides it
Nextflow options use ONE dash (-resume). Pipeline parameters use TWO (--fasta).

## Running
    nextflow run workflows/toy/main.nf --fasta test_data/test.fasta
    nextflow run workflows/toy/main.nf --fasta test_data/test.fasta -resume
    nextflow log                     # history of runs

## How -resume works
Each process run gets a fingerprint (hash) made from:
  1. the contents of its input files
  2. its script/command
  3. its parameters
Same fingerprint as a previous successful run -> skipped, shown as "cached".
Anything changed -> that process reruns, plus everything downstream.

## The work directory (my debugging tool)
Every process runs in its own folder: work/<xx>/<hash>/
    ls -a inside it shows:
    .command.sh    the exact command that ran
    .command.out   what it printed
    .command.err   error messages
    .exitcode      0 = success, anything else = failure
Exit code 127 = command not found. Exit code 2 (awk) = could not open file.

## Traps I hit
- Path errors: a path only means something relative to the folder I run
  the command from. Check with ls. Use checkIfExists: true so it fails early.
- "Pulling ..." / "Remote resource not found" = Nextflow did not find my
  LOCAL file and tried GitHub instead. The path is wrong (folder is
  workflows/, with an s).
- Inside a script block, $ means "Nextflow variable". For awk/shell use
  \$0 and \\t so Nextflow leaves them alone.
- "It ran" is not "it is right". Spot-check one result by hand.
- rm -rf deletes permanently with no confirmation. Read it twice.
- -resume with no earlier run just prints a warning and is ignored (harmless).

## Linux commands used this week
    cat > file << 'EOF' ... EOF    create a file (overwrites!)
    cat >> file                    append to a file
    mkdir -p a/b                   make folders, no complaint if they exist
    mv src dest                    move or rename
    ls -a / ls -l                  show hidden files / show symlinks
    find ~ -name "x" 2>/dev/null   search for a file
    grep -c '^>' file              count FASTA sequences
    sort f | uniq | wc -l          count unique lines
    echo -n "TEXT" | wc -c         count characters
    pwd                            where am I?

## Git basics used
    git status
    git init
    git add .
    git commit -m "message"
.gitignore should contain: work/  .nextflow*  results/

## Self-test answers (corrected)
1. First run failed because the path written in the script did not point to
   where the file really was (relative to where I launched). Nextflow made a
   broken symlink in work/, so awk could not open it.
2. -resume compares a fingerprint of input contents + script + parameters.
   Match = cached. Change = rerun that process and everything after it.
3. output: path saves a file that the next process can take as input.
   stdout only prints text, so it cannot feed a chain.
