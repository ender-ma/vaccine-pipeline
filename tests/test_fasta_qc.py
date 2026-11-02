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
        assert any(len(seq) == 0 for _, _, seq, _ in records)

    def test_nucleotide_sequence_flagged(self, tmp_path):
        """A DNA string is valid protein syntax — only composition betrays it."""
        f = write_fasta(tmp_path, ">dna\n" + "ATGC" * 15 + "\n")
        _, errors = fasta_qc.validate_and_describe(f, min_length=10, max_length=None)
        assert any("nucleotide" in e for e in errors)
