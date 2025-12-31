# journal_eval/scorer.py

from journal_eval.matcher import is_match


def score_journal(predicted_items, gold_items, journal_text):
    matched_pred = set()
    matched_gold = set()
    matches = []

    for i, pred in enumerate(predicted_items):
        for j, gold in enumerate(gold_items):
            if j in matched_gold:
                continue
            if is_match(pred, gold):
                matched_pred.add(i)
                matched_gold.add(j)
                matches.append((pred, gold))
                break

    TP = len(matches)
    FP = len(predicted_items) - len(matched_pred)
    FN = len(gold_items) - len(matched_gold)

    # Polarity accuracy is only evaluated on matched objects because
    # polarity pertains to the same semantic object; unmatched items
    # are not comparable for polarity correctness.
    polarity_correct = sum(
        1 for pred, gold in matches
        if pred.get("polarity") == gold.get("polarity")
    )
    polarity_accuracy = polarity_correct / TP if TP > 0 else 0.0

    # Evidence coverage: proportion of predictions whose evidence_text
    # appears verbatim in the journal text. This discourages hallucinations.
    def _evi(p):
        return p.get("evidence_text") or p.get("evidence_span", "")

    evidence_coverage = (
        sum(1 for pred in predicted_items if _evi(pred) and _evi(pred) in journal_text)
        / len(predicted_items)
        if predicted_items
        else 1.0
    )

    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    # Bucket accuracy (like intensity_level) should be conditional on correct object matching,
    # since bucket labels are tied to the specific matched semantic object.

    return {
        "TP": TP,
        "FP": FP,
        "FN": FN,
        "semantic_object_precision": round(precision, 3),
        "semantic_object_recall": round(recall, 3),
        "semantic_object_f1": round(f1, 3),
        "polarity_accuracy": round(polarity_accuracy, 3),
        "evidence_coverage": round(evidence_coverage, 3),
    }
