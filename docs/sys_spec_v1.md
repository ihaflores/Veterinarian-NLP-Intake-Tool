# System Specification V1

## System Purpose
Given a free-text small-animal veterinary intake note, the system will identify clinically relevant information and assign an intake urgency category of Emergency, Urgent, Soon, or Routine. The system is intended only as workflow decision support and does not provide diagnoses or treatment recommendations.

## Input
<ul>
    <li>One free-text veterinary intake note</li>
    <li>Cats first dataset</li>
    <li>Not vitals, images, lab tests, or structured EHR fields requried</li>
</ul>

## Output
<ul>
    <li>Triage Class</li>
      <ul>
        <li>Emergency</li>
        <li>Urgent</li>
        <li>Soon</li>
        <li>Routine</li>
      </ul>
    <li>Extracted Information</li>
      <ul>
        <li>Symptoms</li>
        <li>Duration/onset</li>
        <li>Exposures</li>
        <li>Medications</li>
      </ul>
    <li>Short Summary</li>
    <li>Confidence Score</li>
    <li>Abstain / Needs Review option</li>
    <li>Evidence phrases</li>
</ul>

## Intended Use
<ul>
    <li>Intake/triage decision support</li>
    <li>Not diagnosis</li>
    <li>Not treament advice</li>
    <li>Not a replacement for a veterinarian</li>
</ul>

## Constraints
<ul>
    <li>Synthetic database
    <li>Input is text only</li>
    <li>Primary emphasis is cats, with dogs included secondarily</li>
    <li>No vital signs, laboratory results, images, or physical-exam findings unless explicitly described in the intake text</li>
    <li>The model must classify based only on information available in the note</li>
    <li>When information is insufficient or confidence is low, the final system may return Needs Review / Abstain</li>
</ul>