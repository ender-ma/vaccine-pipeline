"""Tests for the candidate filtering logic."""

import pytest
from filter_candidates import passes_thresholds, build_records, read_query_ids


THRESHOLDS = {"min_identity": 30.0, "max_evalue": 1e-5, "min_align_length": 30}


def make_hit(qseqid="q1", pident="80.0", evalue="1e-20", length="100", bitscore="200.0", sseqid="s1"):
    """Build a BLAST hit row with sensible defaults, overridable per test."""
    return {
        "qseqid": qseqid, "sseqid": sseqid, "pident": pident,
        "evalue": evalue, "length": length, "bitscore": bitscore,
    }


class TestPassesThresholds:

    def test_good_hit_passes(self):
        ok, reasons = passes_thresholds(make_hit(), 30.0, 1e-5, 30)
        assert ok is True
        assert reasons == []

    def test_low_identity_fails(self):
        ok, reasons = passes_thresholds(make_hit(pident="22.0"), 30.0, 1e-5, 30)
        assert ok is False
        assert len(reasons) == 1
        assert "identity" in reasons[0]

    def test_high_evalue_fails(self):
        ok, _ = passes_thresholds(make_hit(evalue="0.5"), 30.0, 1e-5, 30)
        assert ok is False

    def test_short_alignment_fails(self):
        ok, _ = passes_thresholds(make_hit(length="12"), 30.0, 1e-5, 30)
        assert ok is False

    def test_multiple_failures_all_reported(self):
        ok, reasons = passes_thresholds(
            make_hit(pident="10.0", evalue="1.0", length="5"), 30.0, 1e-5, 30
        )
        assert ok is False
        assert len(reasons) == 3

    def test_exactly_at_threshold_passes(self):
        """Boundary: >= should pass, so 30.0 identity is acceptable."""
        ok, _ = passes_thresholds(make_hit(pident="30.0"), 30.0, 1e-5, 30)
        assert ok is True

    def test_malformed_row_raises(self):
        bad = make_hit()
        del bad["pident"]
        with pytest.raises(ValueError):
            passes_thresholds(bad, 30.0, 1e-5, 30)


class TestBuildRecords:

    def test_query_with_no_hits_is_still_recorded(self):
        """The core guarantee: absence must be visible."""
        records = build_records(["q1", "q2"], [make_hit(qseqid="q1")], THRESHOLDS, "test")
        assert len(records) == 2
        q2 = [r for r in records if r["query_id"] == "q2"][0]
        assert q2["status"] == "NO_HIT"
        assert q2["best_hit"] is None

    def test_best_hit_is_highest_bitscore(self):
        hits = [
            make_hit(bitscore="150.0", sseqid="weaker"),
            make_hit(bitscore="300.0", sseqid="stronger"),
        ]
        records = build_records(["q1"], hits, THRESHOLDS, "test")
        assert records[0]["best_hit"]["subject_id"] == "stronger"

    def test_all_hits_rejected_gives_fail_filter(self):
        records = build_records(["q1"], [make_hit(pident="5.0")], THRESHOLDS, "test")
        assert records[0]["status"] == "FAIL_FILTER"
        assert records[0]["reasons"]

    def test_thresholds_are_recorded_in_record(self):
        records = build_records(["q1"], [make_hit()], THRESHOLDS, "test")
        assert records[0]["thresholds"]["min_identity"] == 30.0

    def test_record_order_follows_query_order(self):
        records = build_records(["z", "a", "m"], [], THRESHOLDS, "test")
        assert [r["query_id"] for r in records] == ["z", "a", "m"]


class TestReadQueryIds:

    def test_ids_truncated_at_first_space(self, tmp_path):
        fasta = tmp_path / "q.fasta"
        fasta.write_text(">query1 some description here\nMKTAYIAK\n")
        assert read_query_ids(fasta) == ["query1"]

    def test_empty_file_gives_empty_list(self, tmp_path):
        fasta = tmp_path / "empty.fasta"
        fasta.write_text("")
        assert read_query_ids(fasta) == []