import json
import torch
import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Veterinary NLP Triage Decision Support",
    layout="centered"
)

# --- LOAD REAL MODELS & RESOURCES ---
@st.cache_resource
def load_all_resources():
    # Load Triage Model & Tokenizer
    triage_path = "./models/triage_model_final"
    triage_tokenizer = AutoTokenizer.from_pretrained(triage_path)
    triage_model = AutoModelForSequenceClassification.from_pretrained(triage_path)
    triage_model.eval()

    # Load Temperature
    with open("./models/optimal_temperature.json", "r") as f:
        temp_data = json.load(f)
    temperature = temp_data["temperature"]

    # Load Token-Classification Extraction Pipeline
    extraction_path = "./models/extraction_model_final"
    extraction_pipe = pipeline(
        "token-classification",
        model=extraction_path,
        tokenizer=extraction_path,
        aggregation_strategy="simple"
    )

    return triage_model, triage_tokenizer, temperature, extraction_pipe

model, tokenizer, temperature, extraction_pipe = load_all_resources()
LABEL_MAP_INV = {0: "EMERGENCY", 1: "URGENT", 2: "SOON", 3: "ROUTINE"}

# --- DISCLAIMER BANNER ---
st.warning(
    "**Clinical Decision Support Disclaimer:** This tool is intended for "
    "pre-triage prioritization support only and does not replace professional "
    "veterinary diagnosis or treatment. All classifications must be verified by clinical staff."
)

st.title("Veterinary Intake Triage Assistant")
st.markdown("Paste an owner intake note below to evaluate urgency via your fine-tuned DistilBERT model, extract clinical entities with your NER model, and review evidence highlights.")

# --- INPUT TEXT AREA ---
note_input = st.text_area(
    "Owner Intake Note",
    placeholder="e.g., My cat Coco got into some Easter lilies yesterday and has been vomiting repeatedly since this morning...",
    height=120
)

# --- REAL MODEL INFERENCE FUNCTION ---
def run_real_inference(text):
    # Triage Classification Inference
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)

    with torch.no_grad():
        outputs = model(**inputs)
        scaled_logits = outputs.logits / temperature
        probs = torch.softmax(scaled_logits, dim=-1).squeeze().cpu().numpy()

    pred_class_id = int(torch.argmax(outputs.logits, dim=-1).item())
    triage_label = LABEL_MAP_INV[pred_class_id]
    confidence = float(probs[pred_class_id])

    # Phase 5 Abstention Policy (Optimized Threshold = 0.82)
    abstain = confidence < 0.82

    # Entity Extraction Inference (Token Classification)
    raw_entities = extraction_pipe(text)

    extracted_entities = {
        "Symptoms": [],
        "Exposures": [],
        "Duration": [],
        "Medications": []
    }
    evidence_words = []

    for ent in raw_entities:
        ent_group = ent["entity_group"].upper().replace("B-", "").replace("I-", "")
        ent_text = ent["word"].strip()
        evidence_words.append(ent_text)

        if "SYMPTOM" in ent_group:
            if ent_text not in extracted_entities["Symptoms"]:
                extracted_entities["Symptoms"].append(ent_text)
        elif "EXPOSURE" in ent_group:
            if ent_text not in extracted_entities["Exposures"]:
                extracted_entities["Exposures"].append(ent_text)
        elif "DURATION" in ent_group:
            if ent_text not in extracted_entities["Duration"]:
                extracted_entities["Duration"].append(ent_text)
        elif "MEDICATION" in ent_group:
            if ent_text not in extracted_entities["Medications"]:
                extracted_entities["Medications"].append(ent_text)

    summary = f"Patient presents with owner-reported symptoms categorized under tier: {triage_label}."

    return {
        "triage_class": triage_label,
        "confidence": confidence,
        "abstain": abstain,
        "entities": extracted_entities,
        "summary": summary,
        "evidence": list(set(evidence_words))
    }

# --- EXECUTION BUTTON ---
if st.button("Evaluate Triage Note"):
    if not note_input.strip():
        st.error("Please enter a valid intake note before running evaluation.")
    else:
        with st.spinner("Analyzing intake note with DistilBERT and NER extraction models..."):
            result = run_real_inference(note_input)

        st.divider()
        st.subheader("Triage Evaluation Results")

        # Top Row: Status / Class & Confidence
        col1, col2, col3 = st.columns(3)

        with col1:
            if result["abstain"]:
                st.error("STATUS: NEEDS HUMAN REVIEW")
            else:
                st.success(f"CLASS: {result['triage_class']}")

        with col2:
            st.metric(label="Confidence Score", value=f"{result['confidence']:.2%}")

        with col3:
            st.info(f"Summary: {result['summary']}")

        st.divider()

        # Bottom Row: Entities and Evidence Highlighting
        col_ent, col_ev = st.columns(2)

        with col_ent:
            st.subheader("Extracted Entities")
            st.json(result["entities"])

        with col_ev:
            st.subheader("Evidence Highlights")
            highlighted_text = note_input
            for ev in result["evidence"]:
                if ev and ev in note_input.lower():
                    # Basic case-insensitive replacement for highlighting
                    highlighted_text = highlighted_text.replace(
                        ev, f"<mark style='background-color: yellow; padding: 2px; border-radius: 4px;'>{ev}</mark>"
                    )
            st.markdown(highlighted_text, unsafe_allow_html=True)