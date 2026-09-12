import json
import random
import copy
import re

VET_ABBREVIATIONS = {
    "vomiting and diarrhea": "v/d",
    "vomiting": "v+",
    "diarrhea": "d+",
    "history": "hx",
    "symptoms": "sx",
    "treatment": "tx",
    "prescription": "rx",
    "medication": "rx",
    "physical exam": "pe",
    "urinalysis": "ua",
    "domestic shorthair": "dsh",
    "domestic longhair": "dlh",
    "male neutered": "mn",
    "female spayed": "fs",
    "heart rate": "hr",
    "respiratory rate": "rr"
}

INFORMAL_DICT = {
    "lethargic": ["acting super lazy", "wiped out", "super tired"],
    "decreased appetite": ["barely eating", "picking at her food"],
    "vomiting": ["puking", "throwing up"],
    "diarrhea": ["the runs"],
    "respiratory distress": ["breathing really hard", "panting heavy"]
}

VAGUE_TIMING_DICT = {
    "since yesterday": ["for a while now", "recently"],
    "for three days": ["for a few days", "for a while"],
    "last night": ["recently", "a while ago"],
    "this morning": ["earlier", "recently"],
    "about an hour ago": ["a bit ago", "earlier"],
    "about 30 minutes ago": ["a little while ago", "just recently"],
    "for two days": ["for a couple days", "for a while"],
    "last week": ["a while ago", "recently"]
}

def apply_abbreviation(text, entities):
    """
    Finds a standard veterinary phrase in the text, replaces it with
    vet tech shorthand, and shifts the entity offsets.
    """
    possible_replacements = []

    # Scan the text for any phrases that exist in our dictionary
    for phrase, abbr in VET_ABBREVIATIONS.items():
        # Use regex to find whole words only (case-insensitive)
        pattern = r'\b' + re.escape(phrase) + r'\b'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            possible_replacements.append({
                "start": match.start(),
                "end": match.end(),
                "phrase": match.group(),
                "abbr": abbr
            })

    # If no matching phrases are found, return the original data
    if not possible_replacements:
        return text, entities, None

    # Pick a random replacement to apply (to keep variants diverse)
    choice = random.choice(possible_replacements)

    # Use helper function to safely swap the text and shift offsets
    new_text, new_entities = replace_text_and_shift_offsets(
        text=text,
        entities=entities,
        match_start=choice["start"],
        match_end=choice["end"],
        new_string=choice["abbr"]
    )

    return new_text, new_entities, "abbreviation"

def apply_typo(text, entities):
    """
    Introduces a random, realistic typo into a word longer than 4 characters
    and shifts the entity offsets accordingly.
    """
    # Find all words longer than 4 characters (avoids messing up short words like "cat")
    words = [(m.start(), m.end(), m.group()) for m in re.finditer(r'\b[a-zA-Z]{5,}\b', text)]

    # If no suitable words are found, return the original data
    if not words:
        return text, entities, None

    # Pick a random word to mess up
    match_start, match_end, word = random.choice(words)

    # Choose a random typo strategy
    typo_type = random.choice(["swap", "drop", "double"])

    if typo_type == "swap" and len(word) > 3:
        # Swap two adjacent internal letters (e.g., "vomiting" -> "vomtiing")
        idx = random.randint(1, len(word) - 3)
        new_word = word[:idx] + word[idx+1] + word[idx] + word[idx+2:]

    elif typo_type == "drop":
        # Drop a random internal letter (e.g., "lethargic" -> "lethrgic")
        idx = random.randint(1, len(word) - 2)
        new_word = word[:idx] + word[idx+1:]

    else:
        # Double a random internal letter (e.g., "breathing" -> "breathhing")
        idx = random.randint(1, len(word) - 2)
        new_word = word[:idx] + word[idx] + word[idx:]

    # Apply the change and shift offsets
    new_text, new_entities = replace_text_and_shift_offsets(
        text=text,
        entities=entities,
        match_start=match_start,
        match_end=match_end,
        new_string=new_word
    )

    return new_text, new_entities, "typo"

def apply_informal_language(text, entities):
    """Swaps clinical terms for informal owner phrasing."""
    possible_replacements = []

    for formal, informal_list in INFORMAL_DICT.items():
        pattern = r'\b' + re.escape(formal) + r'\b'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            possible_replacements.append({
                "start": match.start(),
                "end": match.end(),
                "phrase": match.group(),
                "informal": random.choice(informal_list) # Pick a random slang term
            })

    if not possible_replacements:
        return text, entities, None

    choice = random.choice(possible_replacements)

    new_text, new_entities = replace_text_and_shift_offsets(
        text=text, entities=entities,
        match_start=choice["start"], match_end=choice["end"],
        new_string=choice["informal"]
    )

    return new_text, new_entities, "informal_language"

def apply_vague_timing(text, entities):
    """Swaps specific duration/onset phrases for vague equivalents."""
    possible_replacements = []

    for specific, vague_list in VAGUE_TIMING_DICT.items():
        pattern = r'\b' + re.escape(specific) + r'\b'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            possible_replacements.append({
                "start": match.start(),
                "end": match.end(),
                "phrase": match.group(),
                "vague": random.choice(vague_list) # Pick a random vague term
            })

    if not possible_replacements:
        return text, entities, None

    choice = random.choice(possible_replacements)

    new_text, new_entities = replace_text_and_shift_offsets(
        text=text, entities=entities,
        match_start=choice["start"], match_end=choice["end"],
        new_string=choice["vague"]
    )

    return new_text, new_entities, "vague_timing"

def generate_variants(base_case, num_variants=2):
    """
    Creates noisy variants from a clean base case
    """
    variants = [base_case] # keep the clean base case

    for i in range(num_variants):
        variant = copy.deepcopy(base_case)

        # Modify ID so it's unique, but keep scenario_id the same
        variant["id"] = f"{base_case['id']}_var{i+1}"

        # Randomly choose a noise function (simplified)
        new_text, new_entities, applied_tag = apply_abbreviation(
            variant["text"],
            variant["entities"]
        )

        variant["text"] = new_text
        variant["entities"] = new_entities
        variant["noise_tags"].append(applied_tag)

        return variants

def replace_text_and_shift_offsets(text, entities, match_start, match_end, new_string):
    """
    Replaces a specific slice of text with a new string and updates all entity offsets.
    """
    # Calculate how much the total string length will change
    length_diff = len(new_string) - (match_end - match_start)

    # Splice the new string into the text
    new_text = text[:match_start] + new_string + text[match_end:]

    # Create a fresh copy of the entities so we don't overwrite the base case
    new_entities = copy.deepcopy(entities)

    for ent in new_entities:
        # Case A: Entity is strictly BEFORE the replaced text -> No change
        if ent["end"] <= match_start:
            continue

        # Case B: Entity is strictly AFTER the replaced text -> Shift both start & end
        elif ent["start"] >= match_end:
            ent["start"] += length_diff
            ent["end"] += length_diff

        # Case C: The replacement happens INSIDE the entity itself (e.g., adding a typo)
        elif ent["start"] <= match_start and ent["end"] >= match_end:
            ent["end"] += length_diff
            # We also must update the literal "text" field of the entity to match the new text
            local_start = match_start - ent["start"]
            local_end = match_end - ent["start"]
            ent["text"] = ent["text"][:local_start] + new_string + ent["text"][local_end:]

        else:
            print(f"Warning: Partial boundary overlap detected for entity '{ent['text']}'.")

    return new_text, new_entities

def generate_variants(base_case, num_variants=2):
    """Creates noisy variants from a clean base case."""
    variants = [base_case]
    noise_functions = [apply_abbreviation, apply_typo, apply_informal_language, apply_vague_timing]

    for i in range(num_variants):
        variant = copy.deepcopy(base_case)
        variant["id"] = f"{base_case['id']}_var{i+1}"

        # Pick a random noise function to apply
        func = random.choice(noise_functions)
        new_text, new_entities, applied_tag = func(variant["text"], variant["entities"])

        # Only add the variant if a change was actually made
        if applied_tag:
            variant["text"] = new_text
            variant["entities"] = new_entities
            if applied_tag not in variant["noise_tags"]:
                variant["noise_tags"].append(applied_tag)
            variants.append(variant)

    return variants

if __name__ == "__main__":
    input_file = "../data/seed/seed_cases_v2.jsonl"
    output_file = "../data/train_cases_v2.jsonl"

    expanded_dataset = []

    # Read the base cases
    with open(input_file, "r") as f:
        for line in f:
            base_case = json.loads(line)
            # Generate 2 noisy variants per base case
            expanded_dataset.extend(generate_variants(base_case, num_variants=2))

    # Save the new dataset
    with open(output_file, "w") as f:
        for case in expanded_dataset:
            f.write(json.dumps(case) + "\n")

    print(f"Success! Generated {len(expanded_dataset)} total cases.")