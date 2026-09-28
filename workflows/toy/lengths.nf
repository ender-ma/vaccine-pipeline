nextflow.enable.dsl=2

params.fasta  = "test_data/test.fasta"
params.outdir = "results"

process SEQ_LENGTHS {
    publishDir params.outdir, mode: 'copy'

    input:
    path fasta

    output:
    path "lengths.tsv"

    script:
    """
    awk '/^>/ {if (name) print name"\\t"len; name=substr(\$0,2); len=0; next} {len+=length(\$0)} END {if (name) print name"\\t"len}' $fasta > lengths.tsv
    """
}

workflow {
    fasta_ch = Channel.fromPath(params.fasta)
    SEQ_LENGTHS(fasta_ch)
}
