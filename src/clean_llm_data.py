import json

def clean_llm_data(input_file, output_file):
    cleaned_cases = []
    cat_count = 1
    dog_count = 1
    scenario_count = 1

    with open(input_file, 'r') as f:
        for line in f:
            case = json.loads(line)

            # Assign IDs
            if case.get("species") == "cat":
                case["id"] = f"CAT_{cat_count:04d}"
                cat_count += 1
            else:
                case["id"] = f"DOG_{dog_count:04d}"
                dog_count += 1

            case["scenario_id"] = f"SCENARIO_{scenario_count:04d}"
            scenario_count += 1

            # Fix Triage Key
            if "triage" in case:
                case["triage_label"] = case.pop("triage")

            # Fix Entity Keys and Build Evidence Array
            evidence_list = []
            if "entities" in case:
                for ent in case["entities"]:
                    if "label" in ent:
                        ent["type"] = ent.pop("label")
                    # Add to evidence
                    if "text" in ent:
                        evidence_list.append(ent["text"])

            case["evidence"] = evidence_list

            # Ensure noise_tags and source exist
            case["noise_tags"] = case.get("noise_tags", [])
            case["source"] = case.get("source", "synthetic")

            # Reorder dict for cleanliness
            ordered_case = {
                "id": case["id"],
                "scenario_id": case["scenario_id"],
                "species": case["species"],
                "text": case["text"],
                "triage_label": case["triage_label"],
                "entities": case["entities"],
                "evidence": case["evidence"],
                "noise_tags": case["noise_tags"],
                "source": case["source"]
            }
            cleaned_cases.append(ordered_case)

    with open(output_file, 'w') as f:
        for c in cleaned_cases:
            f.write(json.dumps(c) + "\n")

clean_llm_data("gen_data_v1.jsonl", "seed_cases_v2.jsonl")