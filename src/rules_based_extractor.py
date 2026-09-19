import json
import re

# 1. Define the regex patterns for the 4-part entity schema
# These prioritize common cats-first and general veterinary terms
ENTITY_PATTERNS = {
    "SYMPTOM": [
        r"\bvomiting\b", r"\bv/d\b", r"\bdiarrhea\b", r"\bd\+\b", r"\bv\+\b",
        r"\blethargic\b", r"\bacting weird\b", r"\bpain\b", r"\bstraining\b",
        r"\blimping\b", r"\bcrying\b", r"\bpanting\b", r"\bsneezing\b", r"\bseizure\b"
    ],
    "EXPOSURE": [
        r"\blily\b", r"\bchocolate\b", r"\btoxin\b", r"\bforeign body\b", r"\bhit by car\b"
    ],
    "MEDICATION": [
        r"\bgabapentin\b", r"\binsulin\b", r"\bvaccines?\b"
    ],
    "DURATION": [
        r"\bsince yesterday\b", r"\bfor \w+ days\b", r"\btoday\b",
        r"\babout an hour ago\b", r"\bthis morning\b", r"\ba while ago\b", r"\brecently\b"
    ]
}

def extract_entities(text):
    """Scans textand returns extracted entities with exact character offsets."""
    extracted = []
    for entity_type, patterns in ENTITY_PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                extracted.append({
                    "type": entity_type,
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
    return extracted

def evaluate_extraction(true_entities, pred_entities):
    """Calculates exact-match precision, recall, and F1."""
    # Convert lists of dicts to sets of tuples for easy intersection logic
    # Exact match requires the type, start index, and end index to be identical
    true_set = set((e['type'], e['start'], e['end']) for e in true_entities)
    pred_set = set((e['type'], e['start'], e['end']) for e in pred_entities)

    tp = len(true_set.intersection(pred_set))
    fp = len(pred_set - true_set)
    fn = len(true_set - pred_set)

    return tp, fp, fn

def main():
    print("Loading validation data...")
    val_cases = []
    with open('../data/val_data.jsonl', 'r') as f:
        for line in f:
            val_cases.append(json.loads(line))

    total_tp, total_fp, total_fn = 0, 0, 0

    print("Running rule-based entity extraction...")
    for case in val_cases:
        true_ents = case.get('entities', [])
        pred_ents = extract_entities(case['text'])

        tp, fp, fn = evaluate_extraction(true_ents, pred_ents)
        total_tp += tp
        total_fp += fp
        total_fn += fn

    # Calculate final entity-level metrics
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    print("\n" + "="*50)
    print("BASELINE EXTRACTION RESULTS (Exact Match)")
    print("="*50)
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"\nTotal True Positives: {total_tp}")
    print(f"Total False Positives: {total_fp}")
    print(f"Total False Negatives: {total_fn}")

if __name__ == "__main__":
    main()