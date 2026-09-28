
# Nextflow Cheat Sheet

## Process anatomy
process NAME { input: ... output: ... script: """...""" }

## Input/output types
val = plain value | path = file | stdout = printed text

## Channels
Channel.of(...)  Channel.fromPath(...)

## Running
nextflow run file.nf --param value
nextflow run file.nf -resume      (single dash!)
nextflow log

## Debugging
work/<hash>/.command.sh  .command.out  .command.err  .exitcode

## Traps I hit
- $ inside script blocks needs \ for awk/shell variables
