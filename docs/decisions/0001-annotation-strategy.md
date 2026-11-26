# 0001 — Annotation strategy

- **Status:** Proposed
- **Date:** 2026-11-22
- **Author:** Adeolu-Shittu Akinloluwa
- **Affects:** Week 6 annotation stage; Week 7 localization stage; Week 25 licence audit

## Context

The pipeline needs functional information attached to each protein before any of the seven
antigen-selection checks defined in `pipeline_specification_v1` can run. Those checks consume a
protein sequence plus, in most cases, some notion of what the protein is and where it sits — so
annotation has to be resolved first.

The target pathogen for the first implementation is Oropouche virus (OROV), a segmented RNA virus
with a small proteome. This matters for the choice: most off-the-shelf annotation pipelines assume
a bacterial genome and begin with gene prediction, which is unnecessary work for a virus whose
proteins are already described in public reference records.

Three constraints apply to any option:

1. **Licence** — the tool and every database it draws on must be usable for the intended purpose.
   Open source does not imply unrestricted use.
2. **Reproducibility** — both the software version and the database version must be pinnable, so a
   run can be repeated exactly at a later date.
3. **Organism fit** — the tool must be appropriate for viral proteomes, not only bacterial ones.

## Decision

Use a **two-layer annotation strategy**:

- **Layer 1 — NCBI RefSeq existing annotation** as the primary source of per-protein identity for
  OROV. Retrieve the annotated reference records rather than predicting genes locally.
- **Layer 2 — InterProScan** as the domain and family signature layer, run on the protein
  sequences from layer 1 to add domain-level evidence that RefSeq records do not consistently
  carry.

These are complementary rather than competing: layer 1 answers "which proteins exist and what are
they called", layer 2 answers "what domains and families do they contain". Both outputs are
normalized into the internal schema by the adapter layer (Week 6, Day 2) rather than consumed raw.

## Options considered

### NCBI RefSeq existing annotation — ACCEPTED (layer 1)

| Property | Value |
|---|---|
| Licence | US government work, public domain; no licence restriction on reuse |
| Input format | None — records are retrieved, not computed (Entrez / FTP) |
| Output format | GenBank flat file, GFF3, protein FASTA |
| Version pinnable | Yes — `accession.version` per record, plus the RefSeq release number |

Chosen because the proteome of a well-described virus is already annotated by NCBI, and
re-deriving it locally would add failure modes without adding information.

### InterProScan — ACCEPTED (layer 2)

| Property | Value |
|---|---|
| Licence | Apache 2.0 for the software and bundled scanning tools, **except SignalP and TMHMM**, which require separately obtained licences and are excluded from the default distribution |
| Input format | Protein FASTA (nucleotide also accepted) |
| Output format | TSV, XML, GFF3, JSON |
| Version pinnable | Yes. Two numbers must be recorded: the InterProScan software version and the InterPro release, which are paired in release notes (e.g. "InterPro 84.0 / InterProScan 5.50-84.0"). Previous releases remain archived on the EBI FTP site |

Chosen because it is permissively licensed for the parts we intend to use, produces machine-readable
output suited to the adapter layer, and is explicitly versionable on both software and data axes.

### Bakta — REJECTED

Licensed GPL-3.0, with a versioned database published on Zenodo that lists its external database
versions (Pfam, RefSeq, UniProt and others) per release — so it would satisfy the licence and
reproducibility constraints. Rejected on **organism fit**: Bakta annotates bacterial genomes, MAGs
and plasmids. It is the wrong tool class for a viral proteome.

Worth revisiting only if the pipeline is later extended to bacterial pathogens, which is in the
post-MVP backlog rather than the six-month scope.

### Pfam-only lookup — REJECTED

Rejected as redundant rather than unsuitable. Pfam is one of the member databases InterProScan
already queries, so a standalone Pfam lookup would deliver a subset of layer 2 while adding a
second tool to version, audit and maintain. Narrower scope for the same provenance overhead.

## Defaults accepted

Recorded explicitly because accepting a default silently is indistinguishable, six months later,
from having chosen it deliberately.

### NCBI RefSeq

- Protein names, gene boundaries and functional assignments are taken as given from NCBI's
  annotation pipeline and curators. This project does not re-derive or second-guess them at the
  annotation stage.
- Record whether each retrieved record is curated (`NC_` / `NP_` prefixes) or computationally
  derived (`NZ_` / `WP_`), since the two carry different evidential weight.
- Record the retrieval date. Records are revised in place and only the `.version` suffix changes,
  so date plus `accession.version` together identify what was actually fetched.

### InterProScan

- All available member-database analyses run unless restricted with `-appl`. The set of "available"
  analyses depends on what the local installation includes — notably excluding SignalP and TMHMM by
  default, per the licence note above.
- E-value and score thresholds are set per member database and are inherited as-is; this project
  does not override them.
- GO term mapping (`-goterms`) and pathway annotation (`-pa`) remain off unless explicitly enabled.
- The default output format set applies unless `-f` is specified.
- The InterPro data release moves independently of the software version, so both are recorded per
  run.

## Consequences

1. **Two of the seven antigen-selection checks are affected by the SignalP/TMHMM licence terms.**
   `LOCALIZATION` and `TM_TOPOLOGY` in `pipeline_specification_v1` currently name signal-peptide
   and TM-topology tools that are not covered by InterProScan's Apache licence. Substitutes
   (DeepTMHMM, DeepLoc) must have their own terms checked before the Week 7 localization stage is
   implemented. This is a blocker for Week 7, not Week 6.

2. **The `Tool` and `Database` entities now have concrete first instances.** RefSeq and InterPro
   become `Database` rows (name + version); InterProScan becomes a `Tool` row (name + version).
   Every `Prediction` produced downstream references them, which is what makes the provenance
   requirement from Week 5 operational rather than aspirational.

3. **Raw outputs are retained.** Both layers' unmodified outputs are kept alongside the normalized
   records, per the Week 6 note not to discard raw evidence after parsing.

4. **The Week 25 licence audit inherits this record.** The `THIRD_PARTY_NOTICES` file should cite
   InterProScan, InterPro and RefSeq with the versions actually used.

## Open items

- [ ] Record the exact InterProScan software version and InterPro release once installed
- [ ] Record the OROV RefSeq accessions (all segments) with their `.version` suffixes and retrieval
      date
- [ ] Confirm DeepTMHMM / DeepLoc licence terms before Week 7
- [ ] Change status to Accepted once the Week 6 annotation stage runs end to end