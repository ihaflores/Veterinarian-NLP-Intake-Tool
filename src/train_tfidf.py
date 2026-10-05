import json
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix

def load_data(filepath):
    """Loads text and triage labels from the JSONL splits."""
    texts = []
    labels = []
    with open(filepath, 'r') as f:
        for line in f:
            case = json.loads(line)
            texts.append(case['text'])
            labels.append(case['triage_label'])
    return texts, labels

def main():
    # Load the dataset splits generated in Phase 2
    print("Loading data...")
    X_train, y_train = load_data('../data/processed/v2/train_data.jsonl')
    X_val, y_val = load_data('../data/processed/v2/val_data.jsonl')

    # Build the scikit-learn pipeline
    # Using TfidfVectorizer and LogisticRegression to establish the reference point
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2), # Captures single words and bi-grams like "v/d" or "acting weird"
            max_features=5000
        )),
        ('clf', LogisticRegression(
            class_weight='balanced', # Penalizes errors equally across the four classes
            max_iter=1000
        ))
    ])

    # Train the TF-IDF triage classifier
    print("Training TF-IDF + Logistic Regression model...")
    pipeline.fit(X_train, y_train)

    # Predict on the validation set
    print("Generating predictions on validation set...")
    y_pred = pipeline.predict(X_val)

    # Evaluate and output the required baseline metrics
    print("\n" + "="*50)
    print("BASELINE EVALUATION RESULTS")
    print("="*50)

    # Defines the exact four-class urgency scheme
    target_names = ['EMERGENCY', 'URGENT', 'SOON', 'ROUTINE']

    # Outputs macro-F1 and per-class precision/recall
    print("\nClassification Report:")
    print(classification_report(y_val, y_pred, labels=target_names))

    # Outputs the confusion matrix for baseline error analysis
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_val, y_pred, labels=target_names)
    cm_df = pd.DataFrame(cm, index=target_names, columns=target_names)
    print(cm_df)

    # Store the pipeline as a file to be used by web app
    joblib.dump(pipeline, 'models/tfidf_baseline.joblib')

if __name__ == "__main__":
    main()