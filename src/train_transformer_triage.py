import numpy as np
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
import torch
print(f"GPU Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Device: {torch.cuda.get_device_name(0)}")

# Define the primary model specified in the Phase 4 checkpoint
# MODEL_NAME = "microsoft/deberta-v3-base"
MODEL_NAME = "distilbert-base-uncased"

# Map the four triage classes to integer IDs for PyTorch
LABEL_MAP = {
    "EMERGENCY": 0,
    "URGENT": 1,
    "SOON": 2,
    "ROUTINE": 3
}

def compute_metrics(eval_pred):
    """Calculates macro-F1 and other metrics to compare against the Phase 3 baseline."""
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    # Calculate precision, recall, and F1 with macro averaging
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='macro')
    acc = accuracy_score(labels, predictions)

    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def main():
    print("Loading and preparing data splits...")
    dataset = load_dataset('json', data_files={
        'train': '../data/split/v2/train_data.jsonl',
        'validation': '../data/split/v2/val_data.jsonl',
        'test': '../data/split/v2/test_data.jsonl'
    })

    def encode_labels(example):
        # Rename 'label' to 'labels' and cast to a list for tensor stacking
        example['labels'] = [LABEL_MAP[example['triage_label']]]
        return example

    dataset = dataset.map(encode_labels)

    print(f"Initializing {MODEL_NAME} tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=256
        )

    tokenized_datasets = dataset.map(tokenize_function, batched=True)

    # Drop 'token_type_ids' and keep the newly named 'labels'
    cols_to_keep = ["input_ids", "attention_mask", "labels"]
    cols_to_remove = [c for c in tokenized_datasets["train"].column_names if c not in cols_to_keep]
    tokenized_datasets = tokenized_datasets.remove_columns(cols_to_remove)
    tokenized_datasets.set_format("torch")

    print(f"Loading {MODEL_NAME} for sequence classification...")
    # Initialize the model with a 4-class classification head
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=4,
        problem_type="single_label_classification"
    )

    # Define training hyperparameters
    training_args = TrainingArguments(
        output_dir="./models/triage_model_checkpoints",
        eval_strategy="epoch",            # Evaluate at the end of each epoch
        save_strategy="epoch",            # Save a checkpoint at the end of each epoch
        learning_rate=2e-5,
        warmup_steps=100,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=15,
        weight_decay=0.01,
        load_best_model_at_end=True,      # Automatically reload the best checkpoint based on validation
        metric_for_best_model="f1",        # Optimize for macro-F1
    )

    print("Initializing Hugging Face Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        compute_metrics=compute_metrics,
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer)
    )

    print("Starting training...")
    trainer.train()

    print("Training complete. Evaluating on the test set...")
    test_results = trainer.evaluate(tokenized_datasets["test"])
    print(test_results)

    # Save the final tuned model and tokenizer
    print("Saving final model to ./models/triage_model_final")
    trainer.save_model("./models/triage_model_final")
    tokenizer.save_pretrained("./models/triage_model_final")

if __name__ == "__main__":
    main()