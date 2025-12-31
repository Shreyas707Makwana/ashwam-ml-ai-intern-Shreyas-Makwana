# Evidence-Grounded Extraction & Evaluation (Journals)

## What This Solves

Real journals are messy: people write symptoms, food, emotions, and thoughts in free text. There’s no neat label set to lean on. This repo evaluates extractions by anchoring everything to verbatim evidence copied from the journal itself. If the evidence isn’t in the text, we don’t emit it.

The focus of this assignment is evaluation design rather than extraction quality; extraction is intentionally minimal to highlight objective, evidence-based scoring.

## Why Evidence-Grounded?

- Prevents hallucination: every object includes an `evidence_text` that appears exactly in the journal.
- Keeps results auditable: reviewers can trace predictions to the source line.
- Stays deterministic: no ML models or randomness; same input → same output.

## How Matching Works (no fixed vocabularies)

We match a predicted object to a gold object only when:
- Domains are identical (e.g., `symptom` to `symptom`), and
- The evidence strings have strong overlap: we compute the longest common substring and require an overlap ratio ≥ 0.5 relative to the shorter span. This blocks accidental partial matches and typical negation traps.

## Uncertainty & Abstention

Restraint is built in:
- If `evidence_text` is missing, empty, or not a substring of the journal, we skip the object.
- If polarity is `uncertain` and the evidence isn’t concrete, we abstain rather than guess.

These rules keep outputs clean and reviewer-friendly.

## Schema 

- `domain` (enum): symptom | food | emotion | mind
- `evidence_text` (free text): verbatim substring from the journal
- `polarity` (enum): present | absent | uncertain
- `time_bucket` (enum): today | last_night | past_week | unknown
- `intensity_level` (enum, optional): low | medium | high | unknown
- `confidence` (enum, optional): high | medium | low

Notes:
- Constrained enums: `domain`, `polarity`, `time_bucket`, `intensity_level`, `confidence`
- Free text: `evidence_text` (must be a verbatim substring), optional `text`
- Legacy keys like `evidence_span` and `intensity_bucket` are still accepted and normalized.

## Metrics

Calculated only from matched objects:
- `semantic_object_precision`, `semantic_object_recall`, `semantic_object_f1`
- `polarity_accuracy` (on matched pairs only)
- `evidence_coverage` (fraction of predictions with in-text evidence)

Why these choices?
- Polarity accuracy is measured on matched items because polarity is only meaningful for the same semantic object.
- Bucket accuracy (e.g., intensity) is conditional on a correct object match to avoid scoring unrelated labels.

## CLI

Run the evaluator end-to-end:

```bash
python -m journal_eval run --data ./data --out ./out
```

## Outputs

- `out/per_journal_scores.jsonl` — per-journal metrics
- `out/score_summary.json` — macro-averaged summary

## Project Notes

- No ML models, embeddings, or randomness.
- Deterministic, simple, and readable.
- Designed to prevent hallucination and make review easy.
