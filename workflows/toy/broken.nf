nextflow.enable.dsl=2

process COUNT_SEQS {
    input:
    path fasta

    output:
    stdout

    script:
    """
    grepp -c '^>' $fasta
    """
}
process EXTRACT_HEADERS {
    input:
    path fasta

    output:
    path "headers.txt"

    script:
    """
    grep '^>' $fasta > headers.txt
    """
}
process UNIQUE_HEADERS {
    input:
    path headers

    output:
    stdout

    script:
    """
    sort $headers | uniq | wc -l
    """
}

workflow {
    fasta_ch = Channel.fromPath(params.fasta)

    COUNT_SEQS(fasta_ch)
    headers_ch = EXTRACT_HEADERS(fasta_ch)
    UNIQUE_HEADERS(headers_ch)

    COUNT_SEQS.out.view()
    UNIQUE_HEADERS.out.view()
}
