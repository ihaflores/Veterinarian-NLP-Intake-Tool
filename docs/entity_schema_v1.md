# Entity Schema V1

## Entity Schema Summary
| Entity       | Meaning                           | Example         |
| ------------ | --------------------------------- | --------------- |
| `SYMPTOM`    | Clinical sign/complaint           | vomiting        |
| `DURATION`   | Timing/onset/duration             | since yesterday |
| `EXPOSURE`   | Potential external cause/exposure | ate chocolate   |
| `MEDICATION` | Medication/treatment mention      | prednisone      |

### Optional Metadata
| Field        | Purpose                              |
| ------------ | ------------------------------------ |
| `normalized` | Standardized wording                 |
| `negated`    | Whether symptom is explicitly absent |
| `certainty`  | Possible vs confirmed                |
| `species`    | Cat or dog                           |
| `noise_tags` | Tracks synthetic perturbations       |

## 1. SYMPTOM

### Definition
Any phrase describing an observed clinical sign, complaint, behavioral change, or physical abnormality reported in the intake note.

### Examples
<ul>
    <li>vomiting</li>
    <li>diarrhea</li>
    <li>lethargic</li>
    <li>not eating</li>
    <li>coughing</li>
    <li>limping</li>
    <li>difficulty breathing</li>
    <li>straining to urinate</li>
    <li>blood in urine</li>
    <li>shaking</li>
    <li>collapsed</li>
</ul>

### Annotation Rule
Annotate the smallest meaningful phrase that captures the symptom.
Example:

> “My cat has been vomiting repeatedly since last night.”

Annotate:

> vomiting repeatedly

rather than the entire sentence.

### Normalization
Where useful, map informal wording to a standardized concept.
| Raw phrase        | Normalized value     |
| ----------------- | -------------------- |
| throwing up       | vomiting             |
| puking            | vomiting             |
| not eating        | decreased appetite   |
| very tired        | lethargy             |
| peeing blood      | hematuria            |
| trouble breathing | respiratory distress |


## 2. DURATION

### Definition
Any phrase describing when a symptom or event began, how long it has lasted, or when it occurred.

### Examples
<ul>
    <li>since yesterday</li>
    <li>for three days</li>
    <li>this morning</li>
    <li>started an hour ago</li>
    <li>about a week</li>
    <li>for months</li>
    <li>20 minutes ago</li>
</ul>

### Annotation Rule
Preserve the original wording.
Example:

> “She has been coughing for about three days.”

Extract:
```
{
  "type": "DURATION",
  "text": "for about three days"
}
```

### Optional Normalization
```
{
  "text": "for three days",
  "normalized_value": 3,
  "normalized_unit": "days"
}
```

## 3. EXPOSURE

### Definition
A phrase describing possible or confirmed contact with a toxin, foreign object, harmful substance, trauma source, or other potentially relevant external event. A reported contact, ingestion, or external event that could contribute to the animal's current condition.

### Examples
<ul>
    <li>ate chocolate</li>
    <li>chewed on a lily</li>
    <li>got into rat poison</li>
    <li>swallowed string</li>
    <li>drank antifreeze</li>
    <li>may have eaten medication</li>
    <li>got into the trash</li>
    <li>hit by a car</li>
</ul>

## 4. MEDICATION

### Definition
Any medication, drug, supplement, or treatment explicitly mentioned in the intake note.

### Examples
<ul>
    <li>Benadryl</li>
    <li>insulin</li>
    <li>prednisone</li>
    <li>antibiotics</li>
    <li>flea medication</li>
    <li>pain medication</li>
    <li>gabapentin</li>
</ul>

### Annotation Rule
Extract the medication mention itself.
Example:

> “I gave her Benadryl about two hours ago.”

Might annotate to:
```
{
  "type": "MEDICATION",
  "text": "Benadryl",
  "normalized": "diphenhydramine"
}
```
The timing:

> two hours ago

would separately be labeled DURATION.

## Important Functionalities

### Allow multiple entities
A single note can contain several symptoms.
Example:

> “My cat has been vomiting and having diarrhea since yesterday and seems lethargic.”

That should produce:
```
{
  "symptoms": [
    "vomiting",
    "diarrhea",
    "lethargic"
  ],
  "duration": [
    "since yesterday"
  ]
}
```

### Negation
Consider:

> “He is not vomiting but has diarrhea.”

You should not treat vomiting as a positive symptom. So we will annotate it with negation metadata:
```
{
  "type": "SYMPTOM",
  "text": "vomiting",
  "negated": true
}
```

Example:

> “No vomiting, but she has diarrhea.”

could become:
```
[
  {
    "type": "SYMPTOM",
    "text": "vomiting",
    "normalized": "vomiting",
    "negated": true
  },
  {
    "type": "SYMPTOM",
    "text": "diarrhea",
    "normalized": "diarrhea",
    "negated": false
  }
]
```

### Uncertainty
Same idea for phrases like:

> “I think he may have eaten chocolate.”

That's not the same as:

> “I watched him eat chocolate.”

Can add an optional field:
```
"certainty": "possible"
```

## Potential JSON Structure for V1
```
{
  "id": "CAT_0001",
  "species": "cat",
  "text": "My cat has been vomiting since last night and may have eaten part of a lily.",
  "triage_label": "URGENT",
  "entities": [
    {
      "type": "SYMPTOM",
      "text": "vomiting",
      "normalized": "vomiting",
      "negated": false
    },
    {
      "type": "DURATION",
      "text": "since last night"
    },
    {
      "type": "EXPOSURE",
      "text": "may have eaten part of a lily",
      "normalized": "lily ingestion",
      "certainty": "possible"
    }
  ],
  "evidence": [
    "vomiting",
    "may have eaten part of a lily"
  ],
  "source": "synthetic"
}
```