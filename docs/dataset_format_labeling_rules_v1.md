# Dataset Format and Labeling Rules V1

## 1. Master Dataset Format Example

```
{
  "id": "CAT_0001",
  "scenario_id": "SCENARIO_0001",
  "species": "cat",
  "text": "My cat has been throwing up since last night and is barely eating.",
  "triage_label": "URGENT",
  "entities": [
    {
      "type": "SYMPTOM",
      "text": "throwing up",
      "start": 16,
      "end": 27,
      "normalized": "vomiting",
      "negated": false
    },
    {
      "type": "DURATION",
      "text": "since last night",
      "start": 28,
      "end": 44
    },
    {
      "type": "SYMPTOM",
      "text": "barely eating",
      "start": 52,
      "end": 65,
      "normalized": "decreased appetite",
      "negated": false
    }
  ],
  "evidence": [
    "throwing up since last night",
    "barely eating"
  ],
  "noise_tags": [
    "informal_language"
  ],
  "source": "synthetic"
}
```

## 2. Required Fields
| Field          | Purpose                             |
| -------------- | ----------------------------------- |
| `id`           | Unique note identifier              |
| `species`      | `cat` or `dog`                      |
| `text`         | Original intake note                |
| `triage_label` | Emergency, Urgent, Soon, or Routine |
| `entities`     | Annotated extraction targets        |
| `evidence`     | Text supporting triage decision     |
| `noise_tags`   | Synthetic language/noise conditions |
| `source`       | Initially always `synthetic`        |

## 3. ID Convention
Use simple IDs for each entry, for example:

```
CAT_0001
CAT_0002
DOG_0001
DOG_0002
```

## 4. Triage Label Rules
ALWAYS use the four classes

```
EMERGENCY
URGENT
SOON
ROUTINE
```

to ensure consistency. Each note received exactly one grouth-truth triage label

### Labeling Rule
If multiple signs correspond to different urgency levels:

> Assign the highest urgency level supported by the note.

Example:

> “Mild diarrhea today but now struggling to breathe.”

Label:

```
"triage_label": "EMERGENCY"
```

## 5. Entity Annotation Rules
Each entity should represent a span that appears in the original text.

For example:

> “My cat has been throwing up for two days.”

would annotate to:

```
{
  "type": "SYMPTOM",
  "text": "throwing up",
  "normalized": "vomiting"
}
```

as opposed to only:

```
{
  "type": "SYMPTOM",
  "text": "vomiting"
}
```

because "vomiting" didn't appear in the note.

The idea is to keep both:

<ul>
    <li>original wording</li>
    <li>normalized wording</li>
</ul>

## 6. Character Offsets
The extraction model will need to know where in text an entity occurs. So we will include:

```
{
  "type": "SYMPTOM",
  "text": "vomiting",
  "start": 20,
  "end": 28,
  "normalized": "vomiting"
}
```

Where:
<ul>
    <li>start = first character position</li>
    <li>end = character position immediately after the entity</li>
</ul>

This will make it much easier later to convert data into token-level NER labels.

## 7. Negation Rule
For symptoms explicitly stated as absent:

> “No vomiting, but she has diarrhea.”

We would then store:

```
{
  "type": "SYMPTOM",
  "text": "vomiting",
  "negated": true
}
```

and

```
{
  "type": "SYMPTOM",
  "text": "diarrhea",
  "negated": false
}
```

This lets the dataset preserve information that a bag-of-words baseline may struggle with.

### Rule

Do not treat negated symptoms as positive clinical evidence for triage unless their absence itself matters in context.

## 8. Exposure certainty

Use a simple field for certainty:

```
confirmed
possible
```

Example:

> “He ate chocolate.”

```
"certainty": "confirmed"
```

versus:

> “He may have gotten into chocolate.”

```
"certainty": "possible"
```

## 9. Missing entities

Not every note needs all four entity types.

Example:

> “Annual vaccine appointment.”

Could have:

```
"entities": []
```

Do not have to insert information just to fill all categories.

## 10. Evidence annotations

The evidence field should contain the phrase or phrases most responsible for the triage label.

Example:

> “Male cat keeps straining in the litter box but no urine is coming out.”

Possible evidence:

```
"evidence": [
  "straining in the litter box",
  "no urine is coming out"
]
```

This is different from the full entity list. The evidence field gives you a ground-truth reference for that.

## 11. Noise tags

<ul>
    <li>typo</li>
    <li>abbreviation</li>
    <li>paraphrase</li>
    <li>missing_information</li>
    <li>vague_timing</li>
    <li>informal_language</li>
    <li>negation</li>
    <li>none</li>
</ul>

Example:

```
"noise_tags": [
  "typo",
  "informal_language"
]
```

For a clean note:

```
"noise_tags": []
```

No need for "none" if we're using an empty list.

## 12. Clean vs noisy variants

Example clean note:

> “The cat has been vomiting for two days and has decreased appetite.”

Noisy version:

> “cat been throwin up 2 days, barely eating”

Both may represent the same underlying case.

This will let us test:

> Does the model make the same triage decision when the clinical meaning stays the same but the language changes?

## 13. Avoid label leakage

Do not generate notes like:

> “This is an emergency. The cat cannot breathe.”

If the label is EMERGENCY, the model could learn the word emergency instead of the clinical evidence.

Similarly avoid:

<ul>
    <li>“needs urgent care”</li>
    <li>“routine visit”</li>
    <li>“can wait a few days”</li>
</ul>

unless those phrases are intentionally part of a special test set.

The model should infer urgency from clinical content.

## 14. Train / validation / test split

Dataset starting point:
<ul>
    <li>70% training</li>
    <li>15% validation</li>
    <li>15% test</li>
</ul>

The important rule:

> Related variants of the same underlying synthetic case should stay in the same split.

For example, if these are paraphrases of one underlying case:

> “Cat vomited three times today.”

and

> “Kitty has thrown up 3x since this morning.”

Do not put one in training and one in test.

This data leakage would artificially inflate performance because they're almost the same example.

## 5. Introduce a scenario ID

Because of that leakage issue outline in previous section, we can add:

```
"scenario_id": "SCENARIO_0042"
```

Then several language variants can share the same scenario:

```
SCENARIO_0042
    CAT_0091
    CAT_0092
    CAT_0093
```

When splitting the data, we can split by scenario_id, and not by individual note.

## Labeling Rules V1 Summary
<ul>
    <li>Label only information present in the note.</li>
    <li>Do not infer a diagnosis.</li>
    <li>Assign exactly one triage class.</li>
    <li>If multiple urgency levels are present, use the highest supported urgency.</li>
    <li>Preserve the original wording of extracted entities.</li>
    <li>Store normalized concepts separately.</li>
    <li>Annotate negated symptoms and mark them as negated.</li>
    <li>Mark exposures as possible or confirmed where appropriate.</li>
    <li>Do not invent entities that are absent.</li>
    <li>Related paraphrases/noisy versions must share a scenario_id.</li>
    <li>All versions of one scenario must remain in the same train/validation/test split.</li>
    <li>Avoid explicit urgency words that leak the ground-truth label.</li>
</ul>