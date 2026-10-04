import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Map the  triage classes to integer IDs matching the training script
LABEL_MAP = {"EMERGENCY": 0, "URGENT": 1, "SOON": 2, "ROUTINE": 3}
ID_TO_LABEL = {v: k for k, v in LABEL_MAP.items()}

def calculate_ece(confidences, predictions, labels, num_bins=10):
    """Calculates Expected Calibration Error (ECE) to see if confidence matches accuracy."""
    bin_boundaries = np.linspace(0, 1, num_bins + 1)
    ece = 0.0
    total_samples = len(predictions)

    for i in range(num_bins):
        bin_lower, bin_upper = bin_boundaries[i], bin_boundaries[i+1]

        # Find predictions that fall into this confidence bin
        in_bin = np.where((confidences > bin_lower) & (confidences <= bin_upper))[0]
        if len(in_bin) == 0:
            continue

        bin_acc = np.mean(predictions[in_bin] == labels[in_bin])
        bin_conf = np.mean(confidences[in_bin])
        bin_weight = len(in_bin) / total_samples

        # ECE is weighted average of the gap between confidence and accuracy
        ece += bin_weight * np.abs(bin_acc - bin_conf)

    return ece

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

    # Use GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    all_confidences = []
    all_predictions = []

    print("Extracting probabilities...")
    with torch.no_grad(): # Disables gradient calculation to save memory during evaluation
        for text in texts:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256).to(device)
            outputs = model(**inputs)

            # Convert raw logits to a probability distribution
            probs = torch.softmax(outputs.logits, dim=-1).squeeze().cpu().numpy()

            # Get the top prediction and its exact confidence score
            pred_class = np.argmax(probs)
            confidence = probs[pred_class]

            all_predictions.append(pred_class)
            all_confidences.append(confidence)

    all_predictions = np.array(all_predictions)
    all_confidences = np.array(all_confidences)
    true_labels = np.array(true_labels)

    # Calculate Metrics
    acc = np.mean(all_predictions == true_labels)
    ece = calculate_ece(all_confidences, all_predictions, true_labels)

    # Calculate Phase 5 Safety Metric: Emergency False Negatives
    emergency_id = LABEL_MAP["EMERGENCY"]
    actual_emergencies = np.where(true_labels == emergency_id)[0]
    missed_emergencies = np.sum(all_predictions[actual_emergencies] != emergency_id)
    emergency_fn_rate = missed_emergencies / len(actual_emergencies) if len(actual_emergencies) > 0 else 0.0

    print("\n" + "="*50)
    print("PHASE 5: SAFETY & CALIBRATION METRICS")
    print("="*50)
    print(f"Accuracy:                      {acc:.4f}")
    print(f"Expected Calibration Error:    {ece:.4f}")
    print(f"Emergency False-Negative Rate: {emergency_fn_rate:.4f} ({missed_emergencies} missed)")
    print("="*50)

if __name__ == "__main__":
    main()