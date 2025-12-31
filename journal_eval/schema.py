# journal_eval/schema.py

# Constrained enums (allowed sets):
VALID_DOMAINS = {"symptom", "food", "emotion", "mind"}
VALID_POLARITY = {"present", "absent", "uncertain"}
VALID_TIME_BUCKETS = {"today", "last_night", "past_week", "unknown"}
VALID_INTENSITY_LEVELS = {"low", "medium", "high", "unknown"}
VALID_CONFIDENCE = {"high", "medium", "low"}  # Optional field

# Free text fields: `text` and `evidence_text` must be verbatim substrings of journal text.


def normalize_keys(obj):
    """
    Normalize legacy keys to the new schema without mutating the original dict.
    - evidence_span -> evidence_text
    - intensity_bucket -> intensity_level
    - confidence: if numeric, do not validate; if string, must be one of VALID_CONFIDENCE.
    """
    norm = dict(obj)

    if "evidence_text" not in norm and "evidence_span" in norm:
        norm["evidence_text"] = norm.get("evidence_span", "")

    if "intensity_level" not in norm and "intensity_bucket" in norm:
        norm["intensity_level"] = norm.get("intensity_bucket")

    return norm


def validate_object(obj):
    """
    Validate a semantic object according to the updated schema.

    Required fields:
      - domain (enum)
      - evidence_text (free text, non-empty; must be substring of journal text at runtime)
      - polarity (enum)
      - time_bucket (enum)

    Optional fields:
      - intensity_level (enum)
      - confidence (enum: "high" | "medium" | "low")
      - text (free text, not validated here)

    Comments:
      - Constrained enums: domain, polarity, time_bucket, intensity_level, confidence
      - Free text: evidence_text, text
    """
    obj = normalize_keys(obj)

    required_fields = ["domain", "evidence_text", "polarity", "time_bucket"]
    for field in required_fields:
        if field not in obj:
            return False

    if obj["domain"] not in VALID_DOMAINS:
        return False

    if obj["polarity"] not in VALID_POLARITY:
        return False

    if obj["time_bucket"] not in VALID_TIME_BUCKETS:
        return False

    # intensity_level is optional but, if present, must be valid
    if "intensity_level" in obj and obj["intensity_level"] not in VALID_INTENSITY_LEVELS:
        return False

    # confidence is optional; if present and is a string, it must be in VALID_CONFIDENCE
    if "confidence" in obj and isinstance(obj["confidence"], str):
        if obj["confidence"] not in VALID_CONFIDENCE:
            return False

    # evidence_text must be a non-empty string; substring check happens during processing
    if not isinstance(obj["evidence_text"], str) or not obj["evidence_text"].strip():
        return False

    return True
