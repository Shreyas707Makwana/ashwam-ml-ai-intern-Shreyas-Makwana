# journal_eval/run.py

import json
from pathlib import Path

from journal_eval.scorer import score_journal
from journal_eval.schema import validate_object, normalize_keys


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def _normalize_and_filter(items, journal_text):
    """
    Normalize schema keys and enforce evidence-grounding constraints.
    - Skip objects with missing/empty evidence_text
    - Skip objects whose evidence_text is not a substring of the journal text
    - If polarity is "uncertain" and no concrete evidence_text exists, abstain safely
    This restraint avoids hallucinations and keeps outputs reviewer-friendly.
    """
    out = []
    for obj in items:
        norm = normalize_keys(obj)

        evi = norm.get("evidence_text", "")
        pol = norm.get("polarity")

        if not isinstance(evi, str) or not evi.strip():
            # Missing or empty evidence: skip
            continue
        if evi not in journal_text:
            # Evidence must be a verbatim substring of journal text
            continue
        if pol == "uncertain" and not evi.strip():
            # Uncertain polarity without concrete evidence: abstain
            continue

        # Only include objects that pass validation (with enums vs free text)
        if validate_object(norm):
            out.append(norm)
    return out


def run(data_dir, out_dir):
    data_dir = Path(data_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    journals = load_jsonl(data_dir / "journals.jsonl")
    gold = load_jsonl(data_dir / "gold.jsonl")
    preds = load_jsonl(data_dir / "sample_predictions.jsonl")

    gold_by_id = {g["journal_id"]: g.get("items", []) for g in gold}
    preds_by_id = {p["journal_id"]: p.get("items", []) for p in preds}

    per_journal_results = []

    for journal in journals:
        jid = journal["journal_id"]
        text = journal["text"]

        gold_items_raw = gold_by_id.get(jid, [])
        pred_items_raw = preds_by_id.get(jid, [])

        # Gold is assumed clean; normalize but do not filter out-of-text (shouldn't occur)
        gold_items = [normalize_keys(g) for g in gold_items_raw]
        pred_items = _normalize_and_filter(pred_items_raw, text)

        scores = score_journal(pred_items, gold_items, text)
        scores["journal_id"] = jid
        per_journal_results.append(scores)

    with open(out_dir / "per_journal_scores.jsonl", "w", encoding="utf-8") as f:
        for row in per_journal_results:
            f.write(json.dumps(row) + "\n")

    summary = {}
    for key in [
        "semantic_object_precision",
        "semantic_object_recall",
        "semantic_object_f1",
        "polarity_accuracy",
        "evidence_coverage",
    ]:
        summary[key] = round(
            sum(r[key] for r in per_journal_results) / len(per_journal_results), 3
        )

    with open(out_dir / "score_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
