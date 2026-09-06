# Triage Rurbic V1

## Class Summary Chart
| Class       | Meaning                                 | Target Response Time                                      | Typical Examples                                |
| ----------- | ----------------------------------------| --------------------------------------------------------- | ----------------------------------------------- |
| Emergency   | Immediate threat to life/organ function | Immediate                                                 | respiratory distress, collapse, active seizures |
| Urgent      | Serious but currently stable | Same day | toxin exposure while stable, repeated vomiting + lethargy | could worsen if delayed                         |
| Soon        | Stable, noncritical medical issue       | 1-3 days | mild GI upset, mild lameness, ear/skin issues  | care needed but short delay acceptable          |
| Routine     | Non-urgent                              | Next available | vaccine, wellness, stable follow-up      | no meaningful acute deterioration               |

## Emergency

### Definition
A case should be labeled Emergency when the intake text suggests an immediate or potentially imminent threat to life, breathing, circulation, neurologic function, or critical organ function that warrants immediate veterinary assessment.

### Intended Response
Immediate evaluation.

### Typical Indicators
<ul>
    <li>severe difficulty breathing</li>
    <li>open-mouth breathing in a cat</li>
    <li>blue/pale gums when paired with severe clinical signs</li>
    <li>collapse or unresponsiveness</li>
    <li>inability to stand associated with acute severe illness</li>
    <li>active seizure or repeated seizures</li>
    <li>uncontrolled bleeding</li>
    <li>major trauma</li>
    <li>suspected urinary obstruction, ie a cat repeatedly straining without producing urine</li>
    <li>severe toxin exposure accompanied by significant symptoms</li>
    <li>rapidly worsening neurologic signs</li>
    <li>severe abdominal distention with signs of distress</li>
    <li>profound weakness accompanied by other critical signs</li>
</ul>

### Important Rule
A single symptom should not automatically make a case Emergency unless that symptom itself represents a critical condition.
For example:

> “Vomited once this morning but is acting normal.” 

would not be Emergency. But:

> “Has been vomiting repeatedly and just collapsed.”

would be Emergency because of the combination and severity.


## Urgent

### Definition
A case should be labeled Urgent when the patient appears stable enough that immediate resuscitation is not indicated from the note, but the signs suggest a potentially serious condition requiring veterinary assessment the same day.

### Intended Response
Same-day evaluation.

### Typical Indicators
<ul>
    <li>repeated vomiting or diarrhea with lethargy</li>
    <li>significant decrease in appetite accompanied by other illness signs</li>
    <li>suspected toxin ingestion while currently stable</li>
    <li>painful injury or suspected fracture while the animal remains stable</li>
    <li>worsening respiratory symptoms without obvious severe respiratory distress</li>
    <li>fever or suspected infection with systemic illness</li>
    <li>blood in vomit, urine, or stool without signs of immediate instability</li>
    <li>significant pain</li>
    <li>acute neurologic abnormalities without collapse or active seizure</li>
    <li>repeated unsuccessful urination attempts when obstruction is not clearly established</li>
    <li>foreign-body ingestion without current collapse or severe distress</li>
</ul>

### Important Rule
Urgent cases are potentially serious, but the text does not indicate immediate life-threatening instability.
A useful distinction is:

> Emergency: “This animal may deteriorate or die without immediate intervention.”

versus

> Urgent: “This animal needs to be evaluated today because waiting could significantly worsen the outcome.”


## Soon

### Definition
A case should be labeled Soon when there is a medical problem that warrants veterinary evaluation but the patient appears stable and a short delay is unlikely to create immediate danger.

### Intended Response
Approximately within 1–3 days.

### Typical Indicators
<ul>
    <li>mild vomiting or diarrhea without systemic illness</li>
    <li>mild decrease in appetite while otherwise behaving normally</li>
    <li>mild lameness while still walking and bearing weight</li>
    <li>ear irritation</li>
    <li>skin irritation, itching, or minor lesions</li>
    <li>mild coughing without breathing difficulty</li>
    <li>chronic condition with a mild change</li>
    <li>minor eye irritation without severe pain or trauma</li>
    <li>minor wound without active bleeding</li>
    <li>behavioral change without significant systemic symptoms</li>
    <li>mild urinary frequency without evidence of obstruction</li>
</ul>

### Important Rule
Soon generally means:

> “This should be examined, but there is no indication in the note that waiting briefly creates substantial immediate risk.”


## Routine

### Definition
A case should be labeled Routine when the note describes preventive care, stable follow-up, administrative/non-acute concerns, or a longstanding issue without evidence of meaningful acute deterioration.

### Intended Response
Next routinely available appointment.

### Typical Indicators
<ul>
    <li>wellness examination</li>
    <li>vaccinations</li>
    <li>nail trim</li>
    <li>routine medication follow-up</li>
    <li>stable chronic condition</li>
    <li>longstanding minor issue with no recent change</li>
    <li>preventive-care questions</li>
    <li>diet or weight-management discussion without acute symptoms</li>
    <li>routine recheck after successful treatment</li>
    <li>nonurgent owner questions</li>
</ul>

### Important Rule
Routine does not mean “nothing is wrong.” It means there is no evidence in the note that expedited evaluation is necessary.

## Class Precedence Rule
When multiple findings suggest different urgency levels, assign the highest urgency level supported by the note. Example:

> “Cat has mild diarrhea but is now having difficulty breathing.”

Diarrhea might suggest Soon, but breathing difficulty could justify Emergency. Therefore:

> Emergency wins.

## Handling Missing/Ambiguous Information
Distinguish between:

### Ground-truth triage labels

> Emergency / Urgent / Soon / Routine

and

### Model abstention

> Needs Review

## Example Cases
| Intake note                                                                    | Proposed class | Reasoning                                              |
| ------------------------------------------------------------------------------ | -------------- | ------------------------------------------------------ |
| “Cat vomited once this morning but is eating and playing normally.”            | Soon           | Mild acute symptom, stable                             |
| “Cat has vomited six times since last night and is very lethargic.”            | Urgent         | Persistent symptoms + systemic illness                 |
| “Cat has been vomiting and just collapsed.”                                    | Emergency      | Collapse makes the situation critical                  |
| “Cat has been scratching one ear for two days.”                                | Soon           | Stable localized complaint                             |
| “Cat is breathing with mouth open and sides are heaving.”                      | Emergency      | Severe respiratory distress                            |
| “Dog has been coughing occasionally but otherwise normal.”                     | Soon           | Needs evaluation, no acute distress                    |
| “Cat may have chewed a lily leaf but currently seems normal.”                  | Urgent         | Potentially serious exposure despite current stability |
| “Cat chewed a lily and is now vomiting and extremely weak.”                    | Emergency      | Exposure + severe systemic signs                       |
| “Male cat keeps going to litter box and produces no urine.”                    | Emergency      | Strong obstruction signal                              |
| “Cat urinating more frequently but producing urine normally.”                  | Soon           | Urinary issue without obstruction signal               |
| “Dog limping after playing but still walking and comfortable.”                 | Soon           | Stable musculoskeletal issue                           |
| “Dog was hit by a car and cannot stand.”                                       | Emergency      | Major trauma + severe impairment                       |
| “Owner wants annual vaccinations.”                                             | Routine        | Preventive care                                        |
| “Stable arthritis follow-up; no new symptoms.”                                 | Routine        | Stable chronic follow-up                               |
| "“My cat chewed part of a lily about 20 minutes ago and currently seems fine.” | Urgent         | Credible toxin exposure without symptoms               |