import json
import numpy as np
from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification
)
import evaluate

# MODEL_NAME = "microsoft/deberta-v3-base"
MODEL_NAME = "distilbert-base-uncased"

# Define the IOB (Inside, Outside, Beginning) schema for the 4 entities
LABEL_LIST = [
    "O",
    "B-SYMPTOM", "I-SYMPTOM",
    "B-EXPOSURE", "I-EXPOSURE",
    "B-MEDICATION", "I-MEDICATION",
    "B-DURATION", "I-DURATION"
]
LABEL_TO_ID = {label: i for i, label in enumerate(LABEL_LIST)}
ID_TO_LABEL = {i: label for i, label in enumerate(LABEL_LIST)}

def load_jsonl_to_hf_dataset(filepath):
    texts, all_entities = [], []
    with open(filepath, 'r') as f:
        for line in f:
            case = json.loads(line)
            texts.append(case['text'])
            all_entities.append(case.get('entities', []))
    return Dataset.from_dict({"text": texts, "entities": all_entities})

def main():
    print("Loading data splits...")
    dataset = DatasetDict({
        "train": load_jsonl_to_hf_dataset('../data/split/v2/train_data.jsonl'),
        "validation": load_jsonl_to_hf_dataset('../data/split/v2/val_data.jsonl'),
        "test": load_jsonl_to_hf_dataset('../data/split/v2/test_data.jsonl')
    })

    print(f"Initializing {MODEL_NAME} tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize_and_align_labels(example):
        # Removed padding="max_length" to allow dynamic padding via the DataCollator
        tokenized_inputs = tokenizer(
            example["text"],
            truncation=True,
            max_length=256,
            return_offsets_mapping=True
        )

        labels = []
        for i, offsets in enumerate(tokenized_inputs["offset_mapping"]):
            # Ignore special tokens like [CLS] and [SEP]
            if offsets == (0, 0):
                labels.append(-100)
                continue

            start_char, end_char = offsets
            assigned_label = "O"

            # Check if this token falls inside any ground-truth entity using overlap logic
            for ent in example["entities"]:
                ent_start = ent["start"]
                ent_end = ent["end"]
                ent_type = ent["type"].upper()

                if start_char < ent_end and end_char > ent_start:
                    prev_start, prev_end = tokenized_inputs["offset_mapping"][i-1] if i > 0 else (0, 0)
                    # If previous token was also part of this entity, it's an "Inside" tag
                    if prev_start < ent_end and prev_end > ent_start:
                        assigned_label = f"I-{ent_type}"
                    else: # Otherwise, it's the "Beginning" of the entity
                        assigned_label = f"B-{ent_type}"
                    break

            labels.append(LABEL_TO_ID[assigned_label])

        tokenized_inputs["labels"] = labels
        del tokenized_inputs["offset_mapping"]
        return tokenized_inputs

    print("Aligning tokens and tags...")
    tokenized_datasets = dataset.map(tokenize_and_align_labels, remove_columns=["text", "entities"])

    # # Explicitly remove token_type_ids to prevent NaN crashes in DeBERTa
    # if "token_type_ids" in tokenized_datasets["train"].column_names:
    #     tokenized_datasets = tokenized_datasets.remove_columns("token_type_ids")

    # Convert arrays to PyTorch tensors so the DataCollator pads labels correctly
    tokenized_datasets.set_format("torch")

    # Initialize the NER model
    print(f"Loading {MODEL_NAME} for token classification...")
    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABEL_LIST),
        id2label=ID_TO_LABEL,
        label2id=LABEL_TO_ID
    )

    # Seqeval is the standard metric library for evaluating NER tasks
    seqeval = evaluate.load("seqeval")

    def compute_metrics(p):
        predictions, labels = p
        predictions = np.argmax(predictions, axis=2)

        # Remove ignored index (-100) and convert IDs back to string labels
        true_predictions = [
            [LABEL_LIST[p] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [LABEL_LIST[l] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]

        results = seqeval.compute(predictions=true_predictions, references=true_labels)
        return {
            "precision": results["overall_precision"],
            "recall": results["overall_recall"],
            "f1": results["overall_f1"],
            "accuracy": results["overall_accuracy"],
        }

    training_args = TrainingArguments(
        output_dir="./models/extraction_model_checkpoints",
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        warmup_steps=100,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=15,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="f1"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        processing_class=tokenizer,
        data_collator=DataCollatorForTokenClassification(tokenizer=tokenizer),
        compute_metrics=compute_metrics
    )

    print("Starting NER training...")
    trainer.train()

    print("Training complete. Evaluating on the test set...")
    test_results = trainer.evaluate(tokenized_datasets["test"])
    print(test_results)

    print("Saving final extraction model to ./models/extraction_model_final")
    trainer.save_model("./models/extraction_model_final")

if __name__ == "__main__":
    main()