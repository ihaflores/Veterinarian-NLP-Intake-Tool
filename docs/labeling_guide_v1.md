# Veterinary NLP Triage Tool: Quick-Reference Labeling Guide

## 1. General Principles

- Label Only What is There: Do not infer diagnoses (e.g., if a dog is vomiting, label vomiting, do not label gastroenteritis).
- Exact Character Matching: Entity spans must perfectly match the original text. Do not include surrounding punctuation or articles (e.g., extract lily, not a lily.).

## 2. Triage Classification (The "Precedence Rule")

Always assign the single highest urgency level supported by the text.

- EMERGENCY: Immediate threat to life. (e.g., collapse, actively seizing, major trauma, open-mouth breathing in cats, unable to urinate).
- URGENT: Serious but currently stable. Warrants same-day care to prevent deterioration. (e.g., toxin exposure while acting normal, repeated vomiting with lethargy, painful fractures).
- SOON: Stable, non-critical medical issue. Can wait 1-3 days. (e.g., mild limping, ear infection, occasional vomiting without lethargy).
- ROUTINE: Non-urgent, preventative, or stable chronic care. (e.g., vaccines, nail trims, wellness exams, stable medication refills).
- **Ambiguity Rule:** If a note is vague (e.g., "acting weird"), assume the worst reasonable case, but lean on the system's "Needs Review" abstention for safety.

## 3. Entity Extraction Categories

- SYMPTOM: Clinical signs or complaints (e.g., vomiting, lethargic, limping).
- DURATION: Timing or onset of the symptoms (e.g., for 3 days, since this morning, about an hour ago).
- EXPOSURE: Toxins, traumas, or foreign bodies (e.g., ate chocolate, hit by car, chewed a lily).
- MEDICATION: Any drug or supplement explicitly named (e.g., gabapentin, insulin).

## 4. Evidence Highlighting

The evidence array must contain the exact string matches of the extracted entities that most strongly justify the chosen triage_label.
