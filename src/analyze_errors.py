import json
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

def load_data(filepath):
    texts, labels = [], []
    with open(filepath, 'r') as f:
        for line in f:
            case = json.loads(line)
            texts.append(case['text'])
            labels.append(case['triage_label'])
    return texts, labels

def main():
    # Load the data
    X_train, y_train = load_data('../data/processed/v2/train_data.jsonl')
    X_val, y_val = load_data('../data/processed/v2/val_data.jsonl')

    # Rebuild and fit the exact baseline pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)),
        ('clf', LogisticRegression(class_weight='balanced', max_iter=1000))
    ])
    pipeline.fit(X_train, y_train)

    # Generate predictions
    y_pred = pipeline.predict(X_val)

    # Load the raw JSON objects so we can inspect noise tags and IDs
    with open('../data/val_data.jsonl', 'r') as f:
        val_cases = [json.loads(line) for line in f]

    print("🔍 FULL ERROR ANALYSIS: All Misclassified Cases")
    print("="*60 + "\n")

    # Group errors by their (True Label -> Predicted Label) pairing
    errors_by_type = defaultdict(list)

    for i in range(len(y_val)):
        true_label = y_val[i]
        pred_label = y_pred[i]

        # Catch ANY mismatch between the ground truth and the prediction
        if true_label != pred_label:
            case = val_cases[i]
            error_info = {
                'id': case.get('id', 'Unknown'),
                'species': case.get('species', 'Unknown'),
                'noise_tags': case.get('noise_tags', []),
                'text': X_val[i]
            }
            errors_by_type[(true_label, pred_label)].append(error_info)

    # Print the grouped errors for easy review
    for (true_label, pred_label), cases in errors_by_type.items():
        print(f"🚨 TRUE: {true_label} -> PREDICTED: {pred_label} ({len(cases)} cases)")
        print("-" * 60)
        for count, case in enumerate(cases, 1):
            print(f"  [{count}] ID: {case['id']} | Species: {case['species']}")
            print(f"      Noise Tags: {case['noise_tags']}")
            print(f"      Text: {case['text']}\n")

if __name__ == "__main__":
    main()