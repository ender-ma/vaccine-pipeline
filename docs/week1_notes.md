# Viral Vaccine Pipeline — Pipeline Specification v1

Status: Week 5 complete. Scientific data model + pipeline specification v1 (the roadmap's Week 5 deliverable) done below.

## Upstream (already built, Weeks 1–4)

FASTA_QC → BLASTP → PARSE_BLAST → validated/filtered proteins (JSON/TSV)

## Antigen-selection stage (7 parallel checks)

| Concept | Process name | Input | Output | Candidate tool/method |
|---|---|---|---|---|
| Subcellular localization | LOCALIZATION | Protein sequence | Localization label + confidence | DeepLoc, or signal-peptide + TM-topology heuristics |
| Adhesin probability | ADHESIN_PREDICT | Protein sequence | Adhesin probability score | SPAAN-style sequence classifier |
| TM helix count | TM_TOPOLOGY | Protein sequence | Number + position of TM helices | TMHMM / DeepTMHMM |
| Antigenicity / immunogenicity | ANTIGENICITY | Protein sequence | Antigenicity score | VaxiJen-equivalent (same tool used manually on OROV) |
| Host-proteome homology | HOST_HOMOLOGY | Protein sequence | % identity to closest human hit | BLASTP vs. human reference proteome |
| Cross-strain conservation | CONSERVATION | Protein sequence + isolate set | Conservation score across isolates | MSA (MAFFT/MUSCLE) — same idea as the MEGA11 step used for OROV |
| Allergenicity & toxicity | SAFETY_SCREEN | Protein sequence | Allergen/toxin flag + score | AllerTOP / ToxinPred |

Note: epitope-level predictors from the OROV methodology (NetMHCpan, NetCTL, IEDB B-cell prediction) are NOT part of this checklist — they belong to the epitope-prediction stage, downstream of antigen selection (roadmap Weeks 10–11).

## Pipeline flow (overview)

Validated proteins (Weeks 1–4 output) → Antigen selection (7 parallel checks) → Evidence aggregation → Candidate record (ranked, traceable)

## Candidate data model (9 entities)

- **Pathogen** — id, species, taxonomy_id
- **Genome** — id, pathogen_id (FK), accession, checksum
- **Protein** — id, genome_id (FK), protein_id, sequence_hash
- **Tool** — id, name, version
- **Database** — id, name, version
- **Run** — id, pipeline_version, status
- **Prediction** — id, protein_id (FK), tool_id (FK), database_id (FK, nullable), run_id (FK), raw_score, normalized_score
- **Evidence** — id, prediction_id (FK), candidate_id (FK), interpretation, conflict_flag
- **Candidate** — id, protein_id (FK), status, rationale

Relationships: Pathogen → Genome → Protein (1:many each). Each Protein is screened by many Predictions, each Prediction produced by one Tool, optionally referencing one Database, during one Run. Each Prediction normalizes into exactly one Evidence record. A Protein may be promoted to one Candidate; a Candidate is supported by many Evidence records.

## What makes a protein a "Candidate"

A protein is promoted from screened to Candidate status only once it has a Prediction + Evidence record for all 7 antigen-selection checks — not just the ones that happened to score well. No single predictor (e.g. a strong antigenicity score alone) is sufficient to call something a candidate; `candidate.rationale` must state, in plain language, why it's being carried forward, including how any failed or borderline check was weighed. `candidate.status` distinguishes passed / rejected / promoted_with_caveats so a failed check is never silently dropped.

## Required evidence per candidate

One Evidence record per antigen-selection check (7 total), each traceable to: which Tool (name + version) produced it, which Database (name + version) it referenced if any, which Run it was produced in, its raw and normalized score, and whether it passed, failed, or triggered a conflict flag against another check's result. This is what "every prediction traceable to a specific input and tool version" (roadmap pointer) means in practice, and it's what prevents presenting a single composite score as if it were validated (the Week 14 trap).

## Implementation calendar (per roadmap)

- Week 6: annotation / normalization adapter layer
- Week 7: localization stage + Docker introduced
- Week 8: conservation stage
- Week 9: antigenicity stage + evidence records
- Weeks 10–11: epitope/MHC prediction (separate downstream stage)
