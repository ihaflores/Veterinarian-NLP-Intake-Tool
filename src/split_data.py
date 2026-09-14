import json
import random
from collections import defaultdict

def create_dataset_splits(input_file, train_ratio=0.7, val_ratio=0.15):
    # Group all cases by their scenario_id to prevent data leakage
    scenarios = defaultdict(list)
    with open(input_file, 'r') as f:
        for line in f:
            case = json.loads(line)
            scenarios[case["scenario_id"]].append(case)

    # Shuffle the unique scenario IDs
    unique_scenarios = list(scenarios.keys())
    random.seed(42) # Set seed for reproducibility
    random.shuffle(unique_scenarios)

    # Calculate split indices
    total_scenarios = len(unique_scenarios)
    train_idx = int(total_scenarios * train_ratio)
    val_idx = train_idx + int(total_scenarios * val_ratio)

    # Assign scenarios to splits
    train_ids = set(unique_scenarios[:train_idx])
    val_ids = set(unique_scenarios[train_idx:val_idx])
    test_ids = set(unique_scenarios[val_idx:])

    splits = {"train": [], "val": [], "test": []}

    for sid, cases in scenarios.items():
        if sid in train_ids:
            splits["train"].extend(cases)
        elif sid in val_ids:
            splits["val"].extend(cases)
        else:
            splits["test"].extend(cases)

    # Save the split files
    for split_name, cases in splits.items():
        with open(f"{split_name}_data.jsonl", 'w') as f:
            for case in cases:
                f.write(json.dumps(case) + "\n")

    # Generate Dataset Statistics
    print(f"Total Scenarios: {total_scenarios} | Total Cases: {sum(len(c) for c in splits.values())}")
    for split_name, cases in splits.items():
        triage_counts = defaultdict(int)
        for case in cases:
            triage_counts[case["triage_label"]] += 1
        print(f"\n{split_name.upper()} SPLIT ({len(cases)} cases):")
        for label, count in triage_counts.items():
            print(f"  - {label}: {count}")

# Run the splitter
create_dataset_splits("train_cases_v2.jsonl")