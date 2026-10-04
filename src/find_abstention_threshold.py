import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

LABEL_MAP = {"EMERGENCY": 0, "URGENT": 1, "SOON": 2, "ROUTINE": 3}

def main():
    print("Loading validation data...")
    texts, true_labels = [], []
    with open('../data/split/v2/val_data.jsonl', 'r') as f:
        for line in f:
            case = json.loads(line)
            texts.append(case['text'])
            true_labels.append(LABEL_MAP[case['triage_label']])

    print("Loading tuned triage model and tokenizer...")
    model_path = "./models/triage_model_final"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)

    # Load optimal temperature
    with open("./models/optimal_temperature.json", "r") as f:
        temp_data = json.load(f)
    temperature = temp_data["temperature"]
    print(f"Loaded optimal temperature: {temperature:.4f}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    all_confidences = []
    all_predictions = []

    print("Extracting temperature-scaled probabilities for threshold sweep...")
    with torch.no_grad():
        for text in texts:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256).to(device)
            outputs = model(**inputs)

            # Scale logits by temperature before softmax
            scaled_logits = outputs.logits / temperature
            probs = torch.softmax(scaled_logits, dim=-1).squeeze().cpu().numpy()

            pred_class = np.argmax(probs)
            confidence = probs[pred_class]

            all_predictions.append(pred_class)
            all_confidences.append(confidence)

    all_predictions = np.array(all_predictions)
    all_confidences = np.array(all_confidences)
    true_labels = np.array(true_labels)

    emergency_id = LABEL_MAP["EMERGENCY"]
    actual_emergencies = np.where(true_labels == emergency_id)[0]
    total_emergencies = len(actual_emergencies)

    print("\n" + "="*60)
    print("PHASE 5: TEMPERATURE-SCALED ABSTENTION SWEEP")
    print("="*60)
    print(f"{'Threshold':<10} | {'Emergency FNR':<15} | {'Abstention Rate':<15}")
    print("-" * 46)

    optimal_threshold = None
    optimal_abstention_rate = None
    target_fnr = 0.05

    for threshold in np.arange(0.50, 0.98, 0.02):
        missed_emergencies = 0
        for idx in actual_emergencies:
            is_wrong = all_predictions[idx] != emergency_id
            is_confident = all_confidences[idx] >= threshold
            if is_wrong and is_confident:
                missed_emergencies += 1

        fnr = missed_emergencies / total_emergencies if total_emergencies > 0 else 0.0
        abstention_rate = np.sum(all_confidences < threshold) / len(true_labels)

        print(f"{threshold:<10.2f} | {fnr:<15.4f} | {abstention_rate:<15.4f}")

        if fnr <= target_fnr and optimal_threshold is None:
            optimal_threshold = threshold
            optimal_abstention_rate = abstention_rate

    print("-" * 46)
    if optimal_threshold is not None:
        print(f"Target Met! Optimal Threshold: {optimal_threshold:.2f} | Abstention Rate: {optimal_abstention_rate:.2%}")
    else:
        print("Could not satisfy the 5% FNR constraint in this range.")

if __name__ == "__main__":
    main()