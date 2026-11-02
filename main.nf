#!/usr/bin/env nextflow

/*
 * Week 3: FASTA -> BLAST database -> blastp -> Python parser
 */

process FASTA_QC {

    tag "${fasta.simpleName}"

    publishDir "${params.outdir}/qc", mode: 'copy'

    errorStrategy { task.exitStatus == 2 ? 'ignore' : 'retry' }
    maxRetries 2

    input:
    path fasta

    output:
    path fasta,                           emit: validated
    path "${fasta.simpleName}_qc.tsv",    emit: report

    script:
    """
    fasta_qc.py \\
	--input ${fasta} \\
        --min-length ${params.min_length} \\
        > ${fasta.simpleName}_qc.tsv
    """
}

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
    publishDir params.outdir, mode: 'copy', pattern: "*.{tsv,txt}"

    input:
    path query
    path db

    output:
    tuple path(query), path("${query.baseName}.blast.tsv"), emit: hits
    path "blast_version.txt",                                emit: version

    script:
    """
    run_blast.sh ${query} ${db}/db ${query.baseName}.blast.tsv
    blastp -version > blast_version.txt
    """
}

process PARSE_BLAST {
    publishDir "${params.outdir}/parsed", mode: 'copy'

    input:
    tuple path(query), path(blast_out)

    output:
    tuple path(query), path("${query.baseName}.filtered.tsv"), emit: hits
    path "${query.baseName}.summary.json",                     emit: summary

    script:
    """
    parse_blast.py ${blast_out} ${query} \\
        --evalue ${params.evalue} \\
        --prefix ${query.baseName}
    """
}

process FILTER_CANDIDATES {

    tag "${query.simpleName}"

    publishDir "${params.outdir}/candidates", mode: 'copy'

    errorStrategy { task.exitStatus == 2 ? 'ignore' : 'retry' }
    maxRetries 2

    input:
    tuple path(query), path(hits)

    output:
    path "${query.baseName}.candidates.json", emit: json
    path "${query.baseName}.candidates.tsv",  emit: tsv

    script:
    """
    BLAST_VERSION=\$(blastp -version | head -n 1)

    filter_candidates.py \\
        --hits ${hits} \\
        --query ${query} \\
        --out-json ${query.baseName}.candidates.json \\
        --out-tsv ${query.baseName}.candidates.tsv \\
        --min-identity ${params.min_identity} \\
        --max-evalue ${params.max_evalue} \\
        --min-align-length ${params.min_align_length} \\
        --blast-version "\$BLAST_VERSION"
    """
}

process FILTER_HITS {

    tag "${hits.simpleName}"

    publishDir "${params.outdir}/candidates", mode: 'copy'

    errorStrategy { task.exitStatus == 2 ? 'ignore' : 'retry' }
    maxRetries 2

    input:
    path hits
    path query_fasta

    output:
    path "${hits.simpleName}_filtered.json", emit: json
    path "${hits.simpleName}_filtered.tsv",  emit: tsv

    script:
    """
    filter_hits.py \\
        --input ${hits} \\
        --query-fasta ${query_fasta} \\
        --json-out ${hits.simpleName}_filtered.json \\
        --tsv-out ${hits.simpleName}_filtered.tsv \\
        --max-evalue ${params.max_evalue} \\
        --min-identity ${params.min_identity} \\
        --min-coverage ${params.min_coverage}
    """
}

workflow {
    db_fasta_ch = channel.fromPath(params.db_fasta, checkIfExists: true)
    query_ch    = channel.fromPath(params.query,    checkIfExists: true)

    FASTA_QC(query_ch)

    MAKEBLASTDB(db_fasta_ch)
    BLASTP(FASTA_QC.out.validated, MAKEBLASTDB.out.db.first())
    PARSE_BLAST(BLASTP.out.hits)

    FILTER_CANDIDATES(PARSE_BLAST.out.hits)
}
