#!/usr/bin/env nextflow

/*
 * Week 3 Day 4: FASTA -> BLAST database -> blastp -> table of hits
 */

process MAKEBLASTDB {
    input:
    path db_fasta

    output:
    path "blastdb", emit: db

    script:
    """
    mkdir blastdb
    makeblastdb -in ${db_fasta} -dbtype prot -out blastdb/db
    """
}

process BLASTP {
    publishDir params.outdir, mode: 'copy'

    input:
    path query
    path db

    output:
    path "${query.baseName}.blast.tsv", emit: hits
    path "blast_version.txt",           emit: version

    script:
    """
    run_blast.sh ${query} ${db}/db ${query.baseName}.blast.tsv
    blastp -version > blast_version.txt
    """
}

workflow {
    db_fasta_ch = channel.fromPath(params.db_fasta, checkIfExists: true)
    query_ch    = channel.fromPath(params.query,    checkIfExists: true)

    MAKEBLASTDB(db_fasta_ch)
    BLASTP(query_ch, MAKEBLASTDB.out.db.first())
}
