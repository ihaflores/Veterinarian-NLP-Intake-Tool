import streamlit as st
import time

# --- STUB/MOCK INFERENCE FUNCTION ---
# In Phase 3, will replace this with TF-IDF Baseline model.
# In Phase 6, will replace this with DeBERTa Transformer.
def mock_inference(text):
    time.sleep(1) # Simulate model processing time

    # Simple rule-based mock just for the UI skeleton
    text_lower = text.lower()
    if "lily" in text_lower or "collapse" in text_lower:
        label = "EMERGENCY"
        conf = 0.88
    elif "chocolate" in text_lower or "vomit" in text_lower:
        label = "URGENT"
        conf = 0.75
    elif "vaccine" in text_lower or "trim" in text_lower:
        label = "ROUTINE"
        conf = 0.95
    else:
        label = "SOON"
        conf = 0.60 # Simulating lower confidence

    # Mock output matching your Phase 6 deliverables
    return {
        "triage_class": label,
        "confidence": conf,
        "abstain": conf < 0.65, # Simulating the Phase 5 abstention policy
        "entities": {
            "Symptoms": ["vomiting"] if "vomit" in text_lower else [],
            "Exposures": ["lily"] if "lily" in text_lower else [],
            "Duration": ["this morning"] if "morning" in text_lower else [],
            "Medications": []
        },
        "summary": "Patient presenting with owner-reported concerns.",
        "evidence": ["vomiting", "lily"] # Words to highlight
    }

# STREAMLIT UI 
st.set_page_config(page_title="Veterinary NLP Triage", layout="wide")

st.title("🐾 Vet Triage NLP Decision Support")
st.markdown("*Note: This is a decision-support tool. It does not provide medical diagnoses.*")

# Text Input
intake_note = st.text_area("Paste Intake Note Here:", height=150,
                           placeholder="e.g., My cat chewed on a lily petal about an hour ago and has vomited twice...")

if st.button("Analyze Note"):
    if intake_note.strip() == "":
        st.warning("Please enter an intake note.")
    else:
        with st.spinner("Analyzing text..."):
            results = mock_inference(intake_note)

        st.divider()

        # Top Row: Triage Label and Confidence
        col1, col2, col3 = st.columns(3)

        with col1:
            if results["abstain"]:
                st.error("⚠️ STATUS: NEEDS HUMAN REVIEW")
            else:
                st.success(f"🏥 TRIAGE CLASS: {results['triage_class']}")

        with col2:
            st.metric(label="Confidence Score", value=f"{results['confidence']:.0%}")

        with col3:
            st.info(f"📝 Summary: {results['summary']}")

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