# journal_eval/matcher.py

# Matching based on evidence substring overlap ratio and domain equality.
# This avoids accidental partial matches and negation-related false positives
# by requiring substantial overlap of the actual evidence text.


def longest_common_substring_length(a: str, b: str) -> int:
    """Deterministic LCS (contiguous) length over lowercase strings."""
    a = a.lower()
    b = b.lower()
    la = len(a)
    lb = len(b)
    if la == 0 or lb == 0:
        return 0

    # DP table for longest common substring
    # dp[i][j] = length of longest common substring ending at a[i-1], b[j-1]
    dp = [0] * (lb + 1)
    best = 0
    for i in range(1, la + 1):
        prev = 0
        for j in range(1, lb + 1):
            tmp = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev + 1
                if dp[j] > best:
                    best = dp[j]
            else:
                dp[j] = 0
            prev = tmp
    return best


def is_match(pred, gold, threshold: float = 0.5) -> bool:
    # Domain must match exactly to be considered.
    if pred.get("domain") != gold.get("domain"):
        return False

    pred_evi = pred.get("evidence_text") or pred.get("evidence_span", "")
    gold_evi = gold.get("evidence_text") or gold.get("evidence_span", "")

    overlap_len = longest_common_substring_length(pred_evi, gold_evi)
    denom = min(len(pred_evi), len(gold_evi)) or 1
    overlap_ratio = overlap_len / denom

    return overlap_ratio >= threshold
