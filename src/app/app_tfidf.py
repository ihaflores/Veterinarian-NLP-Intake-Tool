import streamlit as st
import time
import joblib
from rules_based_extractor import extract_entities

# Load the trained TF-IDF pipeline once at startup
try:
    pipeline = joblib.load('tfidf_baseline.joblib')
except FileNotFoundError:
    st.error("Model file not found. Please run train_tfidf_baseline.py first.")

def baseline_inference(text):
    # 1. TF-IDF Triage Classification
    triage_class = pipeline.predict([text])[0]

    # Extract confidence using prediction probabilities
    probs = pipeline.predict_proba([text])[0]
    confidence = max(probs)

    # 2. Rule-Based Entity Extraction
    extracted_entities = extract_entities(text)

    # 3. Format outputs for the Streamlit UI
    formatted_entities = {
        "Symptoms": [], "Exposures": [], "Duration": [], "Medications": []
    }
    evidence_list = []

    for ent in extracted_entities:
        # Map the uppercase schema keys to the UI dictionary
        key = ent['type'].capitalize()
        if key == "Symptom" or key == "Exposure" or key == "Medication":
            key += "s"

        formatted_entities[key].append(ent['text'])
        evidence_list.append(ent['text'])

    return {
        "triage_class": triage_class,
        "confidence": confidence,
        "abstain": confidence < 0.65,
        "entities": formatted_entities,
        "summary": "Baseline extraction and classification complete.",
        "evidence": evidence_list
    }

# STREAMLIT UI
st.set_page_config(page_title="Veterinary NLP Triage", layout="wide")

st.title("Vet Triage NLP Decision Support")
st.markdown("*Note: This is a decision-support tool. It does not provide medical diagnoses.*")

# Text Input
intake_note = st.text_area("Paste Intake Note Here:", height=150,
                           placeholder="e.g., My cat chewed on a lily petal about an hour ago and has vomited twice...")

if st.button("Analyze Note"):
    if intake_note.strip() == "":
        st.warning("Please enter an intake note.")
    else:
        with st.spinner("Analyzing text..."):
            results = baseline_inference(intake_note)

        st.divider()

        # Top Row: Triage Label and Confidence
        col1, col2, col3 = st.columns(3)

        with col1:
            if results["abstain"]:
                st.error("STATUS: NEEDS HUMAN REVIEW")
            else:
                st.success(f"TRIAGE CLASS: {results['triage_class']}")

        with col2:
            st.metric(label="Confidence Score", value=f"{results['confidence']:.0%}")

        with col3:
            st.info(f"Summary: {results['summary']}")

        st.divider()

        # Bottom Row: Entities and Evidence
        col_ent, col_ev = st.columns(2)

        with col_ent:
            st.subheader("Extracted Entities")
            st.json(results["entities"])

        with col_ev:
            st.subheader("Evidence Highlights")
            # Simple highlighter for the demo skeleton
            highlighted_text = intake_note
            for ev in results["evidence"]:
                if ev in intake_note.lower():
                    # Highlighting in yellow
                    highlighted_text = highlighted_text.replace(
                        ev, f"<mark style='background-color: yellow; padding: 2px; border-radius: 4px;'>{ev}</mark>"
                    )
                    highlighted_text = highlighted_text.replace(
                        ev.title(), f"<mark style='background-color: yellow; padding: 2px; border-radius: 4px;'>{ev.title()}</mark>"
                    )
            st.markdown(highlighted_text, unsafe_allow_html=True)