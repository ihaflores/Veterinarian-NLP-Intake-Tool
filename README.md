# Veterinary Intake NLP Triage Tool

A Master's project prototype for applying natural language processing (NLP) to small-animal veterinary intake notes.

The system is designed to take a free-text intake note and produce:

- a four-level triage classification: **Emergency, Urgent, Soon, or Routine**
- structured clinical information, including:
  - symptoms
  - duration/onset
  - exposures
  - medications
- a short summary
- confidence / abstention information
- evidence highlights supporting the triage result

The project is intended as **workflow decision support**, not as a diagnostic or treatment system.

## Project Status

Currently in **Phase 1: System Design and Planning**.

Current work includes:

- defining the four-class triage rubric
- defining the entity extraction schema
- defining dataset and labeling rules
- defining the evaluation plan
- creating a small synthetic seed dataset for sanity checking

## Initial Project Scope

- Small-animal veterinary intake notes
- Cats-first, with dog support
- Text-only input
- Synthetic data for initial development
- Four triage classes:
  - `EMERGENCY`
  - `URGENT`
  - `SOON`
  - `ROUTINE`

## Planned NLP Tasks

### Triage Classification

Classify each intake note into one of the four urgency levels.

### Entity Extraction

Extract clinically relevant information from the note:

- `SYMPTOM`
- `DURATION`
- `EXPOSURE`
- `MEDICATION`

### Decision-Support Output

The final prototype is planned to return:

- triage class
- confidence score
- Needs Review / abstention status
- extracted entities
- short summary
- evidence highlights

## Planned Technology

- Python 3.11
- PyTorch
- Hugging Face Transformers
- scikit-learn
- pandas / NumPy
- FastAPI or Streamlit
- Git / GitHub

Planned baseline models include:

- rule / dictionary-based extraction
- TF-IDF + logistic regression for triage classification

A transformer-based model will later be fine-tuned for triage classification and entity extraction.

## Evaluation

Planned evaluation includes:

- macro-F1
- per-class precision, recall, and F1
- confusion matrix
- Emergency recall
- Emergency false-negative rate
- entity-level precision, recall, and F1
- calibration metrics
- abstention behavior
- robustness testing under typos, paraphrases, missing information, vague timing, and other noisy input

## Repository Structure

```text
vet-triage-nlp/
├── data/
│   ├── seed/
│   ├── synthetic/
│   └── processed/
├── docs/
├── src/
├── tests/
├── README.md
└── requirements.txt
```

The structure may change as development progresses.

## Data

Initial development uses synthetic veterinary intake notes only.

The seed dataset is intended for design validation and is not yet a formal train/validation/test dataset.

## Disclaimer

This project is an academic prototype for veterinary intake triage decision support.

It is **not** intended to diagnose disease, recommend treatment, or replace professional veterinary judgment.
