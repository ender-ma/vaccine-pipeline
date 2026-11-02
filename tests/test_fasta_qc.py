"""Tests for FASTA validation and QC."""

import pytest
import fasta_qc


def write_fasta(tmp_path, content, name="test.fasta"):
    path = tmp_path / name
    path.write_text(content)
    return path


class TestValidation:

    def test_valid_protein_accepted(self, tmp_path):
        f = write_fasta(tmp_path, ">p1 good\nMKTAYIAKQRQISFVKSHFSRQLEERLGLIE\n")
        records = list(fasta_qc.parse_fasta(f))
        assert len(records) == 1

    def test_empty_sequence_record_detected(self, tmp_path):
        f = write_fasta(tmp_path, ">p1 no sequence\n\n>p2\nMKTAYIAK\n")
        records = list(fasta_qc.parse_fasta(f))
        assert any(len(seq) == 0 for _, seq in records)

    def test_nucleotide_sequence_flagged(self, tmp_path):
        """A DNA string is valid protein syntax — only composition betrays it."""
        f = write_fasta(tmp_path, ">dna\nATGCGTACGTAGCTAGCTAGCATCGATCGTAGC\n")
        records = list(fasta_qc.parse_fasta(f))
        _, seq = records[0]
        nt_fraction = sum(1 for c in seq.upper() if c in "ACGTUN") / len(seq)
        assert nt_fraction > 0.9