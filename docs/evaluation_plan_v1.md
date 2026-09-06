# Evaluation Plan V1

## 1. Triage classification evaluation

Macro-F1

You should also report for each class:

<ul>
    <li>Precision</li>
    <li>Recall</li>
    <li>F1-score</li>
</ul>

And include a:

<ul>
    <li>Confusion matrix</li>

</ul>

For example:

<ul>
    <li>Emergency → Urgent</li>
    <li>Urgent → Soon</li>
    <li>Soon → Routine</li>
</ul>

Those errors are not equally serious.

## 2. Safety-focused evaluation


### Emergency Recall

$$ Recall_{Emergency} = \frac{Correctly\ Predicted\ Emergency} {All\ Actual\ Emergency} $$

This answers:

> Of all real Emergency cases in the test set, how many did the model successfully identify?


### Emergency False-Negative Rate
$$ Emergency\ FNR = 1 - Emergency\ Recall $$

This directly measures under-triage of Emergency cases.

For example:

If there are 100 true Emergency cases and the model misses 8:

<ul>
    <li>Emergency recall = 92%</li>
    <li>Emergency FNR = 8%</li>
</ul>

## 3. Under-triage severity

Assign each class an ordinal urgency level:

<ul>
    <li>ROUTINE = 0</li>
    <li>SOON = 1</li>
    <li>URGENT = 2</li>
    <li>EMERGENCY = 3</li>
</ul>

Then measure how far a prediction falls below the correct urgency.

Example:

| Actual    | Predicted | Under-triage distance |
| --------- | --------- | --------------------: |
| Emergency | Urgent    |                     1 |
| Emergency | Soon      |                     2 |
| Emergency | Routine   |                     3 |
| Urgent    | Soon      |                     1 |
| Soon      | Routine   |                     1 |

This is useful because:

> Emergency → Urgent

is bad, but

> Emergency → Routine

is substantially worse.

## 4. Entity extraction evaluation

For your four extracted entity types:

SYMPTOM
DURATION
EXPOSURE
MEDICATION

use:

Precision
Recall
F1

Ideally report:

overall entity F1
F1 by entity type

For example:
| Entity     | Precision | Recall | F1 |
| ---------- | --------: | -----: | -: |
| Symptom    |         — |      — |  — |
| Duration   |         — |      — |  — |
| Exposure   |         — |      — |  — |
| Medication |         — |      — |  — |

## 5. Decide what counts as a correct extraction

Example ground truth:

> "throwing up"

Model predicts:

> "throwing up"

This is correct.

But if the model predicts:

> "has been throwing up"

that is not an exact span match. Exact matching is strict, which is useful for reproducibility.

## 6. Normalization evaluation

We're storing things such as:

> throwing up → vomiting

so we have two possible tasks:

<ol>
    <li>Find the correct text span</li>
    <li>Assign the correct normalized concept</li>
</ol>

Normalization can initially use deterministic lookup rules and be evaluated separately with:

> percentage of extracted entities mapped to the correct normalized concept.

That prevents the NER task from becoming unnecessarily complicated.

## 7. Confidence and calibration

The classifier will output probabilities such as:

```
Emergency: 0.72
Urgent:    0.19
Soon:      0.07
Routine:   0.02
```

A model can be accurate while still having bad confidence estimates.

### Expected Calibration Error (ECE)

If the model says it is about 80% confident on many examples, roughly 80% of those predictions should be correct.

### Brier Score

This measures how close predicted probabilities are to the actual outcome.

## 8. Abstention evaluation

The system may return:

> Needs Review

when confidence is below a chosen threshold.

Example:

```
maximum confidence < 0.60 → Needs Review
```

The threshold will be selected using the validation set.

### Coverage

Percentage of cases where the model actually makes a prediction.

Example:

> 90% coverage

means it abstained on 10%.

### Accuracy / safety among accepted predictions

As abstention increases, you'd ideally expect the remaining predictions to become safer.

> Abstention Rate vs Emergency False-Negative Rate graph

## 9. Robustness evaluation

Use noise tages to evaluate performance separately on:

### Clean notes

Normal grammatical intake text.

### Typographical noise

> "vommiting"

### Abbreviations

> "v/d"

### Informal language

> "kitty keeps puking"

### Paraphrases

> "throwing up" instead of "vomiting"

### Vague timing

> "for a while"

### Missing information

Important details intentionally omitted.

### Negation

> "not vomiting"

For each subset, compare macro-F1 against the clean set.

Example eventual result:
| Condition           | Macro-F1 |
| ------------------- | -------: |
| Clean               |      .XX |
| Typos               |      .XX |
| Paraphrases         |      .XX |
| Missing information |      .XX |
| Negation            |      .XX |

## 10. Baseline vs transformer comparison

Compare:

### Baseline

TF-IDF + logistic regression

against:

### Transformer

DeBERTa (Or other models chosen to use)

For classification:
| Model                        | Macro-F1 | Emergency Recall | Emergency FNR |
| ---------------------------- | -------: | ---------------: | ------------: |
| TF-IDF + Logistic Regression |        — |                — |             — |
| Transformer                  |        — |                — |             — |

## 12. Primary Success Criteria
Primary classification success criterion: The transformer-based triage classifier should outperform the TF-IDF + logistic regression baseline in macro-F1 while maintaining strong Emergency-class recall.

### For extraction:

> Primary extraction success criterion: The transformer-based extraction system should improve entity-level F1 compared with the rule/dictionary baseline, particularly on paraphrased and noisy notes.

### For safety:

> Safety success criterion: Calibration and abstention should reduce high-confidence under-triage errors compared with the uncalibrated classifier.

## Evaluation Table V1
| Component             | Primary measure         | Supporting measures                  |
| --------------------- | ----------------------- | ------------------------------------ |
| Triage classification | Macro-F1                | Per-class precision, recall, F1      |
| Emergency safety      | Emergency Recall        | Emergency FNR, under-triage severity |
| Classification errors | Confusion matrix        | Error-case analysis                  |
| Entity extraction     | Entity-level F1         | Precision/recall by entity type      |
| Calibration           | ECE                     | Brier score                          |
| Abstention            | Coverage vs safety      | Abstention rate                      |
| Robustness            | Macro-F1 under noise    | Performance drop from clean set      |
| Species analysis      | Cat vs dog Macro-F1     | Per-class metrics                    |
| Model comparison      | Transformer vs baseline | Error-type comparison                |
