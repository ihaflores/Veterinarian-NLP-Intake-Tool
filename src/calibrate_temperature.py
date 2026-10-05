import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.optimize import minimize

LABEL_MAP = {"EMERGENCY": 0, "URGENT": 1, "SOON": 2, "ROUTINE": 3}

def load_validation_data():
    texts, true_labels = [], []
    with open('../data/processed/v2/val_data.jsonl', 'r') as f:
        for line in f:
            case = json.loads(line)
            texts.append(case['text'])
            true_labels.append(LABEL_MAP[case['triage_label']])
    return texts, np.array(true_labels)

def main():
    texts, true_labels = load_validation_data()

    model_path = "./models/triage_model_final"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    logits_list = []
    print("Extracting validation logits...")
    with torch.no_grad():
        for text in texts:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256).to(device)
            outputs = model(**inputs)
            logits_list.append(outputs.logits.cpu().numpy())

    logits = np.vstack(logits_list)
    labels_tensor = torch.tensor(true_labels, dtype=torch.long)
    logits_tensor = torch.tensor(logits, dtype=torch.float)

    # Define Negative Log Likelihood loss function for temperature optimization
    def eval_nll(temp):
        scaled_logits = logits_tensor / temp[0]
        loss_fn = torch.nn.CrossEntropyLoss()
        return loss_fn(scaled_logits, labels_tensor).item()

    # Optimize temperature T using Nelder-Mead
    print("Optimizing temperature scaling parameter...")
    res = minimize(eval_nll, x0=[1.0], method='Nelder-Mead')
    optimal_temperature = res.x[0]

    print(f"\nOptimal Temperature (T): {optimal_temperature:.4f}")

    # Save the optimal temperature parameter for inference use
    with open("./models/optimal_temperature.json", "w") as f:
        json.dump({"temperature": optimal_temperature}, f)
    print("Saved optimal temperature to ./models/optimal_temperature.json")

if __name__ == "__main__":
    main()