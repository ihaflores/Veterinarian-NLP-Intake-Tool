# System Specification V1

## System Purpose

Given a free-text small-animal veterinary intake note, the system will identify clinically relevant information and assign an intake urgency category of Emergency, Urgent, Soon, or Routine. The system is intended only as workflow decision support and does not provide diagnoses or treatment recommendations.

## Input

- One free-text veterinary intake note
- Cats first dataset
- Not vitals, images, lab tests, or structured EHR fields requried

## Output

- Triage Class
  - Emergency
  - Urgent
  - Soon
  - Routine

- Extracted Information
  - Symptoms
  - Duration/onset
  - Exposures
  - Medications

- Short Summary
  - Confidence Score
  - Abstain / Needs Review option
  - Evidence phrases

## Intended Use

- Intake/triage decision support
- Not diagnosis
- Not treament advice
- Not a replacement for a veterinarian

## Constraints

- Synthetic database
- Input is text only
- Primary emphasis is cats, with dogs included secondarily
- No vital signs, laboratory results, images, or physical-exam findings unless explicitly described in the intake text
- The model must classify based only on information available in the note
- When information is insufficient or confidence is low, the final system may return Needs Review / Abstain
